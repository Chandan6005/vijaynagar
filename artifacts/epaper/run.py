#!/usr/bin/env python
import os
import sys
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epaper_project.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

def setup():
    from django.core.management import call_command
    print("Running migrations...")
    call_command('migrate', '--run-syncdb', verbosity=0)

    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@epaper.com', 'admin123')
        print("Created default admin user: admin / admin123")
    else:
        print("Admin user already exists.")

    print("Collecting static files...")
    call_command('collectstatic', '--noinput', verbosity=0)

    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}...")
    from django.core.wsgi import get_wsgi_application
    from wsgiref.simple_server import make_server
    application = get_wsgi_application()
    httpd = make_server('0.0.0.0', port, application)
    print(f"Server running at http://0.0.0.0:{port}/")
    httpd.serve_forever()

if __name__ == '__main__':
    setup()
