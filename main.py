import asyncio
import random
from playwright.async_api import async_playwright
import functions_framework
from flask import request, jsonify, abort
from datetime import timedelta, timezone
from concurrent.futures import TimeoutError
import functools

# Metadata URL (used in some cases to get instance zone)
metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/zone"

# URL = "https://www.google.com/maps/place/Ministry+of+Crab/@6.933608,79.8433473,17z/data=!4m8!3m7!1s0x3ae25925b5da82cd:0x8b9e5cd682e5283f!8m2!3d6.933608!4d79.8433473!9m1!1b1!16s%2Fg%2F1tdw6gvs?entry=ttu&g_ep=EgoyMDI1MTEyMy4xIKXMDSoASAFQAw%3D%3D"

async def human_delay(min_s=0.3, max_s=2.5):
    await asyncio.sleep(random.uniform(min_s, max_s))


# Mouse movement before click
async def human_move_and_click(page, locator):
    try:
        # Ensure element is attached & visible
        await locator.wait_for(state="visible", timeout=3000)

        box = await locator.bounding_box()

        # Fallback if Google re-rendered
        if box is None:
            await locator.click(force=True)
            return

        x = box["x"] + random.uniform(0.2, 0.8) * box["width"]
        y = box["y"] + random.uniform(0.2, 0.8) * box["height"]

        await page.mouse.move(
            x, y,
            steps=random.randint(8, 25)
        )
        await asyncio.sleep(random.uniform(0.1, 0.4))
        await page.mouse.click(x, y)

    except Exception:
        # LAST RESORT (never crash scraper)
        try:
            await locator.click(force=True)
        except:
            pass

# Human scroll (imperfect)
async def human_scroll(page, total_scrolls=None):
    scrolls = total_scrolls or random.randint(2, 6)
    for _ in range(scrolls):
        await page.evaluate(f"""
            () => window.scrollBy(0, {random.randint(200, 600)})
        """)
        await human_delay(0.3, 1.2)

    # occasional upward correction
    if random.random() < 0.3:
        await page.evaluate("""
            () => window.scrollBy(0, -200)
        """)


# Idle like a human reading
async def human_idle(min_s=3, max_s=9):
    await asyncio.sleep(random.uniform(min_s, max_s))

async def human_scroll_container(page, container_selector, steps=5):
    for _ in range(steps):
        # Hover the container (important!)
        await page.hover(container_selector)

        # Human-like wheel scroll
        await page.mouse.wheel(
            0,
            random.randint(300, 700)
        )

        # Random pause
        await asyncio.sleep(random.uniform(0.8, 1.8))


# Random viewport size (call ONCE)
def random_viewport():
    return {
        "width": random.choice([1280, 1366, 1440, 1536, 1600, 1920]),
        "height": random.choice([720, 768, 900, 960, 1080])
    }
    
# @timeout_decorator(300)  # 5 minutes timeout
async def scrape_reviews(URL,review_count):
    # browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    
                    # Anti-detection flags
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    
                    # Performance flags for headless
                    "--no-first-run",
                    "--no-service-autorun",
                    "--password-store=basic",
                    "--use-mock-keychain",
                    
                    # Window size
                    "--window-size=1920,1080",
                ],
                
                # Ignore automation flags
                ignore_default_args=[
                    "--enable-automation",
                    "--disable-component-extensions-with-background-pages"
                ]
                # slow_mo=120
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                
                # Extra HTTP headers
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            await context.add_init_script("""
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Mock Chrome runtime
                window.chrome = {
                    runtime: {},
                };
                
                // Remove automation痕迹
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'denied' }),
                    }),
                });
            """)
            page =  await context.new_page()
            page.set_default_timeout(30000) 
            print("1.Opening place")
            await page.goto(URL, wait_until="domcontentloaded")

            print("2.Clicking Reviews")
            # reviews_btn = await page.locator('button:has-text("Reviews")').first.click()
            # # await page.wait_for_timeout(3000)
            # # humanize
            # await human_move_and_click(page, reviews_btn)
            # await human_delay(1, 2)
    
            print("3.Sorting → Newest")
            sort_btn = await page.locator('button[aria-label*="Sort"]').click(force=True)
            # await page.wait_for_timeout(1000)
            #humanize
            await human_move_and_click(page, sort_btn)
            await human_delay(0.5, 1.5)
            newest = await page.locator('text=Newest').click(force=True)
            # await page.wait_for_timeout(3000)
            #humanize
            await human_move_and_click(page, newest)
            await human_idle(2, 4)
    
            # CRITICAL: wait for reviews AFTER sorting
            print("4.Waiting for reviews to render")
            await page.wait_for_selector(".jftiEf")
            
            # await human_scroll_container(page, ".m6QErb[aria-label*='review']")
            # await human_scroll_container(page,".m6QErb[aria-label*='review']",steps=6)
            collected = []
    
            while len(collected) < review_count:
                if len(collected) % 3 == 0:
                    await human_idle(5, 8)
                reviews = page.locator(".jftiEf")
                total = await reviews.count()
    
                for i in range(total):
                    if len(collected) >= review_count:
                        break
    
                    review = reviews.nth(i)
    
                    # Expand "More" safely
                    more = review.locator("button[jsaction*='more']")
                    if await more.count() > 0:
                        try:
                            # await more.click(force=True)
                            # await page.wait_for_timeout(300)
                            #humanize
                            await human_move_and_click(page, more)
                            await human_delay(0.3, 0.8)
                        except:
                            pass
    
                    # Extract review text (CORRECT)
                    text_locator = review.locator(".wiI7pd")
                    if await text_locator.count() == 0:
                        continue
    
                    text = (await text_locator.inner_text()).strip()
                    if not text:
                        continue
                    
                    # AUTHOR
                    author_locator = review.locator(".d4r55")
                    author = (await author_locator.inner_text()).strip() if await author_locator.count() > 0 else "Unknown"
    
                    # RATING (from aria-label like: "5.0 star rating")
                    rating = 0
                    rating_locator = review.locator(".kvMYJc")
    
                    if await rating_locator.count() > 0:
                        aria = await rating_locator.get_attribute("aria-label")
                        if aria:
                            for ch in aria:
                                if ch.isdigit():
                                    rating = int(ch)
                                    break
    
                    # REVIEW TEXT
                    # content_locator = review.locator(".wiI7pd")
                    # content = (await content_locator.inner_text()).strip() if await content_locator.count() > 0 else ""
    
                    # DATE
                    date_locator = review.locator(".rsqaWe")
                    date = (await date_locator.inner_text()).strip() if await date_locator.count() > 0 else ""
    
                    collected.append({
                        "author": author,
                        "rating": rating,
                        "date": date,
                        "content": text,
                    })
    
                    print(f"Collected review {len(collected),}")
                    #humanize
                    await human_delay(0.4, 1.2)
    
                # Scroll review panel to load more
                await page.evaluate("""
                    () => {
                        const panel = document.querySelector('.m6QErb[aria-label*="review"]');
                        if (panel) panel.scrollTop = panel.scrollHeight;
                    }
                """)
                await page.wait_for_timeout(2000)
    
            # ALWAYS write JSON (even if empty)
            # with open("reviews.json", "w", encoding="utf-8") as f:
            #     json.dump(collected, f, indent=2, ensure_ascii=False)
    
            print("reviews.json saved with", len(collected), "reviews")
            # await browser.close()
            return collected
    except Exception as e:
        await browser.close()
        print(f"Error during scraping: {e}")
        raise
    finally:
        if browser:
            await browser.close()
                
# asyncio.run(scrape_reviews())
@functions_framework.http
def handler(req):
    # Handle CORS preflight requests
    if req.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Authorization,Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return "", 204, headers

    # Set CORS headers for the main request
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Authorization, Content-Type"
    }  
    # token = create_jwt("94711342232",SECRET_KEY)
    # print("token:",token)
    if req.method != 'POST':
        return jsonify({
            "error": "Invalid request method"
        }), 500

    try:
        json_data = req.get_json(silent=True)
        review_count = json_data.get('review_count',5)
        url = json_data.get('url')
        reviews = asyncio.run(scrape_reviews(URL=url, review_count=review_count))
        return jsonify({
            "reviews":reviews
        }),200,headers
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500,headers