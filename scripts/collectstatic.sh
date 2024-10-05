#!/bin/bash

if poetry run python manage.py collectstatic --noinput; then
    echo "static files collected successfully"
else
    echo "Error collecting static files" >&2
    exit
fi
