#!/bin/bash

# Check if config.yaml file exists
if [ ! -f "config.yaml" ]; then
    echo "ERROR: config.yaml file not found. Please create the config.yaml file."
    exit 1
fi

if [ ! -f "tgwui/text-generation-webui" ]; then
    echo "Downloading tgwui src"
    git clone https://github.com/oobabooga/text-generation-webui
    mv text-generation-webui tgwui
fi

# Function to check if virtual environment is activated
is_venv_activated() {
    [[ -n "$VIRTUAL_ENV" ]]
}

# Check if virtual environment is activated
if ! is_venv_activated; then
    echo "Virtual environment not activated. Creating and activating virtual environment..."

    # Create virtual environment
    python3 -m venv venv

    # Activate virtual environment based on the operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        source venv/bin/activate
    else
        source venv/bin/activate
    fi
else
    echo "Virtual environment is already activated."
fi

# Activate virtual environment
if ! is_venv_activated; then
    echo "Activating virtual environment..."
    source venv/bin/activate
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
#echo "Running test.py with python..."
#python test.py
#
## If the above command fails, run test.py using python3
#if [ $? -ne 0 ]; then
#    echo "Running test.py with python3..."
#    python3 test.py
#fi


if [ "$1" = "ui" ]; then
    echo "Running UI..."
    python ui.py
    if [ $? -ne 0 ]; then
        echo "Running UI with python3..."
        python3 ui.py
    fi
fi
if [ "$1" = "cli" ]; then
    echo "Running superagi cli..."
    python cli2.py

    # If the above command fails, run test.py using python3
    if [ $? -ne 0 ]; then
        echo "Running superagi cli..."
        python3 cli2.py
    fi
fi