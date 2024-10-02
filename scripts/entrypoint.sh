#!/bin/bash

# Activate the Poetry environment and run Gunicorn with Uvicorn workers for ASGI
poetry run gunicorn backend.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
