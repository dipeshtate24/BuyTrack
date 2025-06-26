#!/usr/bin/env bash
set -x

# Update and install necessary tools
apt-get update
apt-get install -y wget unzip curl gnupg

# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# Find installed Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

# Download matching ChromeDriver (Chrome for Testing version)
wget -O chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip"
unzip chromedriver.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
