#!/bin/bash

# Downloads the tools
python superagi/tool_manager.py

# Set executable permissions for install_tool_dependencies.sh
chmod +x install_tool_dependencies.sh

# Install dependencies
./install_tool_dependencies.sh

# Run Alembic migrations
alembic upgrade head

# Start the app
exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload
