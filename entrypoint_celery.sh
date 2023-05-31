#!/usr/bin/env bash
celery -A superagi.worker worker -l info --concurrency 3 -E