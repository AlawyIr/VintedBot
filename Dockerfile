# Use a recent Python version compatible with greenlet and playwright
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libxdamage1 \
    libxfixes3 \
    libxext6 \
    libx11-6 \
    libglib2.0-0 \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install browsers for Playwright
RUN playwright install --with-deps chromium

# Copy the rest of the code
COPY . .

# Run your bot
CMD ["python", "BotVinted.py"]
