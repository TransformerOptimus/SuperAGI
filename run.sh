#!/bin/bash

# Check if config.yaml file exists
if [ ! -f "config.yaml" ]; then
    echo "ERROR: config.yaml file not found. Please create the config.yaml file using the command 'cp config.yaml.example config.yaml' and edit it'."
    exit 1
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run test.py
echo "Running test.py..."
python test.py
