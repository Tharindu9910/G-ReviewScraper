# ✅ UPDATED Dockerfile
FROM python:3.11-slim

# ✅ Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# ✅ Set working directory
WORKDIR /app

# ✅ Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    libxkbcommon0 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxdamage1 \
    libxrandr2 \
    libxcomposite1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libxrender1 \
    libxss1 \
    libnss3 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy requirements
COPY requirements.txt .

# ✅ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install Playwright browser (system dependencies already installed)
RUN playwright install --with-deps chromium

# ✅ Copy application code
COPY main.py .

# ✅ Expose port
EXPOSE 8080

# ✅ Start Functions Framework
CMD ["functions-framework", "--target=handler", "--port=8080", "--host=0.0.0.0"]