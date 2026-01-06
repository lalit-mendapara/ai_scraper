# Use Python 3.12 to avoid your Mac's 3.14 issues
FROM python:3.12-slim

# Install minimal system utilities
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and ALL required system libraries for X11
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy your project files
COPY . .

# Ensure outputs folder exists
RUN mkdir -p outputs

CMD ["python", "main.py"]