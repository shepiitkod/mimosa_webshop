"""
WSGI config for mimosa_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mimosa_backend.settings')

application = get_wsgi_application()


def ensure_default_superuser():
	username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
	email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
	password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin12345')

	try:
		user_model = get_user_model()
		if not user_model.objects.filter(username=username).exists():
			user_model.objects.create_superuser(username=username, email=email, password=password)
	except (OperationalError, ProgrammingError):
		pass


ensure_default_superuser()
