#!/bin/bash

# To exit immediately in case there is any command in the script that returns a non-zero exit status
#set -e

# Run tool_manager.py if needed
 python tool_manager.py

# Set executable permissions for install_tool_dependencies.sh
chmod +x install_tool_dependencies.sh

# Install dependencies
./install_tool_dependencies.sh

# Run Alembic migrations
alembic upgrade head

# Start the app
exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload
