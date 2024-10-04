#!/bin/bash

#Activate the poetry environment
poetry run python manage.py makemigrations --noinput
poetry run python manage.py migrate --noinput
