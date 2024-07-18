#!/bin/sh

# Applying database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start uWSGI
echo "Starting uWSGI..."
exec uwsgi --socket :9000 --workers 4 --master --enable-threads --module storefront.wsgi
