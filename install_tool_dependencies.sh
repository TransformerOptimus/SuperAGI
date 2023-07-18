#!/bin/bash

# Run the project's main requirements.txt
pip install -r /app/requirements.txt

# Loop through the tools directories and install their requirements.txt if they exist
for tool in /app/superagi/tools/* /app/superagi/tools/external_tools/* /app/superagi/tools/marketplace_tools/* ; do
  if [ -d "$tool" ] && [ -f "$tool/requirements.txt" ]; then
    echo "Installing requirements for tool: $(basename "$tool")"
    pip install -r "$tool/requirements.txt"
  fi
done
