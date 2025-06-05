#!/bin/bash

echo "Loading environment variables..."
source .env

echo "Waiting for PostgreSQL..."
until pg_isready -h db -U $DB_USER; do
  echo "Waiting for database..."
  sleep 2
done

echo "Running database migrations..."
python manage.py migrate

echo "Collectstatic"
python manage.py collectstatic --no-input

echo "Start project"
exec gunicorn --workers 2 --bind 0.0.0.0:8000 settings.wsgi:application
