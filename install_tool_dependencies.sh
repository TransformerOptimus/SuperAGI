#!/bin/bash

# Update and upgrade apt settings and apps
apt update && apt upgrade -y
xargs apt install -y < /app/requirements_apt.txt

# Run the project's main requirements.txt
pip install -r /app/requirements.txt

for tool in /app/superagi/tools/* /app/superagi/tools/external_tools/* /app/superagi/tools/marketplace_tools/* ; do
# Loop through the tools directories and install their apt_requirements.txt if they exist
  if [ -d "$tool" ] && [ -f "$tool/requirements_apt.txt" ]; then
    echo "Installing apt requirements for tool: $(basename "$tool")"
    xargs apt install -y < "$tool/requirements_apt.txt"
  fi
# Loop through the tools directories and install their requirements.txt if they exist
  if [ -d "$tool" ] && [ -f "$tool/requirements.txt" ]; then
    echo "Installing requirements for tool: $(basename "$tool")"
    pip install -r "$tool/requirements.txt"
  fi
done
