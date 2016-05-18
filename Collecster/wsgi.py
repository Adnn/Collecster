"""
WSGI config for Collecster project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Collecster.settings")

application = get_wsgi_application()


##
## From here: copied from https://devcenter.heroku.com/articles/getting-started-with-django#django-settings
##
## IMPORTANT: a more recent version of the doc (https://devcenter.heroku.com/articles/getting-started-with-django#django-settings)
## replaces dj_static with whitenoise. Yet whitenoise does not serve media files, only static, so we stick with dj_static
## until some time is invested into a better solution (eg. django-storages).
##
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

application = Cling(MediaCling(get_wsgi_application()))
