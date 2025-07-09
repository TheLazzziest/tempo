#!/bin/bash
set -e

# Run migrations
uv run broker/wait_for_postgres.py && uv run manage.py migrate || exit 1

# Start the Django application
uv run uvicorn --host 0.0.0.0 --port ${PORT:-8000} --access-log broker.asgi:application
