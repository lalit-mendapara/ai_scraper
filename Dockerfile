FROM python:3.12-slim
WORKDIR /app

# 1. Install system utilities needed for Playwright's helper script
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install Playwright browsers AND their system dependencies
# The --with-deps flag installs all the missing .so libraries from your error log
RUN playwright install chromium --with-deps

COPY . . 
CMD ["python","main.py"]