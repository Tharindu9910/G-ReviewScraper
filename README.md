# 🕵️ Google Maps Reviews Scraper API  
### Serverless • Playwright • Anti-Bot • Flask • Cloud Run

This is a **serverless API** that scrapes Google Maps reviews using **Playwright + Python** and exposes them through a scalable HTTP endpoint (Google Cloud Functions).


---

# 🚀 Overview

This API extracts **latest Google Maps reviews** for any place URL and returns structured JSON data.

Designed to behave like a **real human browser** and run safely inside a **serverless cloud environment**.

### What this project demonstrates

- Advanced Playwright automation  
- Anti-bot evasion techniques  
- Human-like browser behaviour simulation  
- Async Python architecture  
- Serverless deployment usning docker container on Google Cloud Run 
- Production API design + CORS support  
- Error handling & resource cleanup  

---

# 📌 Features

## 🔎 Data Extracted

For each review:

- Author name
- Star rating ⭐
- Review date
- Full review text

Returned as structured JSON.

---

## 🤖 Human-Like Scraping Engine

Google Maps aggressively blocks bots.  
This scraper simulates real user behaviour:

| Technique | Purpose |
|---|---|
| Random mouse movement | Mimics real cursor behaviour |
| Random scrolling | Prevents bot detection |
| Human reading delays | Avoids robotic timing patterns |
| Random click positions | Natural interaction |
| Random viewport & headers | Real browser fingerprint |
| Navigator spoofing | Hides automation traces |

This makes the scraper far more resilient than typical scripts.

---

## 🧠 Anti-Detection Techniques

Browser context is hardened with:

- Disabled automation flags  
- Overridden `navigator.webdriver`  
- Fake plugins & languages  
- Chrome runtime spoofing  
- Realistic HTTP headers  
- Headless cloud-safe Chromium flags  

This replicates a **real Chrome user**.

---

# 🧪 Local Development

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

Run locally

```bash
functions-framework --target=handler --debug
```

Note: This project is built for educational & research purposes.
