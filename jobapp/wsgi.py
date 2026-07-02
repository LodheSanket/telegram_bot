"""WSGI config for the jobapp project. This is what gunicorn points at
in production, for example: gunicorn jobapp.wsgi --log-file -"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobapp.settings")

application = get_wsgi_application()
