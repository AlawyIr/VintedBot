# Use official Python image
FROM python:3.11

# Create working directory
WORKDIR /app

# Copy requirements file first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run your bot
CMD ["python", "BotVinted.py"]
