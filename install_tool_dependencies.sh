#!/bin/bash

# Run the project's main requirements.txt
pip install -r /app/requirements.txt

# Loop through the tools directories and install their requirements.txt if they exist
<<<<<<< HEAD
for tool in /app/superagi/tools/* ; do
=======
for tool in /app/superagi/.input_tools/* ; do
>>>>>>> tool-input-arch
  if [ -d "$tool" ] && [ -f "$tool/requirements.txt" ]; then
    echo "Installing requirements for tool: $(basename "$tool")"
    pip install -r "$tool/requirements.txt"
  fi
<<<<<<< HEAD
done
=======
done
>>>>>>> tool-input-arch
