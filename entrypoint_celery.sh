#!/usr/bin/env bash
python superagi/tool_manager.py

# Install dependencies
./install_tool_dependencies.sh
celery -A superagi.worker worker --beat -l info --concurrency 20 -E
