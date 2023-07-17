#!/bin/bash

# Downloads the tools
python superagi/tool_manager.py

# Set executable permissions for install_tool_dependencies.sh
chmod +x install_tool_dependencies.sh

# Install dependencies
./install_tool_dependencies.sh
