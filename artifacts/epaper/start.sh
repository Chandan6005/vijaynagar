#!/bin/bash
set -e

cd "$(dirname "$0")"

export DJANGO_SETTINGS_MODULE=epaper_project.settings

echo "Running migrations..."
python manage.py migrate --run-syncdb

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@epaper.com', 'admin123')
    print('Created admin user: admin / admin123')
else:
    print('Admin already exists.')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server on port ${PORT:-8000}..."
exec python manage.py runserver 0.0.0.0:${PORT:-8000}
