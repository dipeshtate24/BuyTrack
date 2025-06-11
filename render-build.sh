#!/usr/bin/env bash

# Install dependencies and Google Chrome on Render
apt-get update && apt-get install -y wget unzip gnupg

# Download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || apt --fix-broken install -y

