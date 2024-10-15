#!/bin/bash

# Start Redis server
redis-server &

# Start Celery worker
poetry run celery -A backend worker -l info &

# Activate the Poetry environment and run Gunicorn with Uvicorn workers for ASGI
poetry run gunicorn backend.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
