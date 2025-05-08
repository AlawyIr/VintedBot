# Use the official Playwright Python image
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Set the working directory
WORKDIR /app

# Copy your code into the image
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install --with-deps

# Run your bot
CMD ["python", "BotVinted.py"]
