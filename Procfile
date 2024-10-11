web: gunicorn backend.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
worker: celery -A backend worker --loglevel=info
