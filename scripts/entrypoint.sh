#!/bin/bash

# Start Redis server
redis-server &

# Start Celery worker
celery -A backend worker -l info &

# Activate the Poetry environment and run Gunicorn with Uvicorn workers for ASGI
gunicorn backend.asgi:application --bind 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker
