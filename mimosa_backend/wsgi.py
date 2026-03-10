"""
WSGI config for mimosa_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mimosa_backend.settings')

application = get_wsgi_application()

# TEMPORARY: auto-create superuser on every startup. Remove after first login.
try:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin12345',
        )
except Exception:
    pass
