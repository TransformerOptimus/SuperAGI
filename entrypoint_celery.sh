#!/usr/bin/env bash
celery -A superagi.worker worker --beat -l info --concurrency 3 -E
