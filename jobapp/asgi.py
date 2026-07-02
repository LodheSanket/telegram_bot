"""ASGI config for the jobapp project. Not required for this project
since everything runs fine on WSGI/gunicorn, included for completeness
in case you later want to run under an async server."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobapp.settings")

application = get_asgi_application()
