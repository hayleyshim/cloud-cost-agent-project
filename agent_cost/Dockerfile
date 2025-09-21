# agent_cost/Dockerfile
FROM python:3.9-slim
WORKDIR /app

# 1. Install dependencies for Chrome and wget/curl
RUN apt-get update && apt-get install -y \
    gnupg \
    wget \
    libx11-xcb1 \
    libnss3 \
    libfontconfig1 \
    libgbm1 \
    libgtk-3-0 \
    curl

# 2. Download and add Google Chrome signing key with a secure method
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/google-chrome.gpg

# 3. Add Google Chrome repository to sources list
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# 4. Install Google Chrome
RUN apt-get update
RUN apt-get install -y google-chrome-stable

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]