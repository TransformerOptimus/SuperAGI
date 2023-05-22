# #!/bin/bash

# # Check if config.yaml file exists
# if [ ! -f "config.yaml" ]; then
#     echo "ERROR: config.yaml file not found. Please create the config.yaml file using the command 'cp config_template.yaml config.yaml' and edit it'."
#     exit 1
# fi

# # Install requirements
# echo "Installing requirements..."
# pip install -r requirements.txt

# # Run test.py
# echo "Running test.py..."
# python test.py
#!/bin/bash

# Check if config.yaml file exists
if [ ! -f "config.yaml" ]; then
    echo "ERROR: config.yaml file not found. Please create the config.yaml file using the command 'cp config_template.yaml config.yaml' and edit it."
    exit 1
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run test.py using python
echo "Running test.py with python..."
python test.py

# If the above command fails, run test.py using python3
if [ $? -ne 0 ]; then
    echo "Running test.py with python3..."
    python3 test.py
fi
