#!/bin/sh
set -e

echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL is ready!"

echo "Making migrations for custom apps..."
python manage.py makemigrations users surveys responses templates_app bank --noinput

echo "Running migrations..."
python manage.py migrate --fake-initial

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application -b 0.0.0.0:8000 -w 4 --timeout 120
