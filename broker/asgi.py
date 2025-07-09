"""
WSGI config for broker project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "broker.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Production")

from configurations.asgi import get_asgi_application  # noqa

application = get_asgi_application()
