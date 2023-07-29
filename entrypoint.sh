#!/bin/bash

# Downloads the tools from marketplace and external tool repositories
python superagi/tool_manager.py

# Install dependencies
./install_tool_dependencies.sh

# Run Alembic migrations
alembic upgrade head

# Start the app
exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload
