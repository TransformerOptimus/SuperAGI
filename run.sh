#!/bin/bash

# Check if config.yaml file exists
if [ ! -f "config.yaml" ]; then
    echo "ERROR: config.yaml file not found. Please create the config.yaml file."
    exit 1
fi

# Check if requirements are already installed
echo "Checking requirements..."
if ! pip show -r requirements.txt >/dev/null 2>&1; then
    echo "Installing requirements..."
    pip install -r requirements.txt >/dev/null 2>&1
else
    echo "All packages are already installed."
fi

# Run test.py using python
echo "Running test.py with python..."
python test.py

# If the above command fails, run test.py using python3
if [ $? -ne 0 ]; then
    echo "Running test.py with python3..."
    python3 test.py
fi
