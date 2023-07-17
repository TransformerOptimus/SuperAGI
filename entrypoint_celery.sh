#!/usr/bin/env bash
celery -A superagi.worker worker --beat -l info --concurrency 20 -E
