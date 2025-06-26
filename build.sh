#!/usr/bin/env bash
set -e

# Install dependencies
apt-get update
apt-get install -y wget unzip curl gnupg

# Install Google Chrome
wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome.deb

# Get Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

# Download ChromeDriver that matches Chrome
wget -q -O chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip"

# Unpack and move
unzip chromedriver.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
