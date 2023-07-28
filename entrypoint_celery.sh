#!/bin/bash

# Downloads the tools
python superagi/tool_manager.py

# Install dependencies
./install_tool_dependencies.sh

exec celery -A superagi.worker worker --beat --loglevel=info