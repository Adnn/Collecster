# Don't want emails while developing
ADMINS = ()
MANAGERS = ADMINS

# Customize the time zone if necessary
TIME_ZONE = 'Europe/Paris'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom applications
    "supervisor",
    "advideogame.apps.AdvideogameConfig",
    #"ndmusic.apps.NdmusicConfig",
    #'OOModel_attributes',
    #'OOModel_composition',
    #'validate_min',
)

# The secret key is found in $DJANGO_SECRET_KEY env var.
import os
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']


##
## From here: copied from https://devcenter.heroku.com/articles/django-app-configuration#database-configuration
##
# Parse database configuration from $DATABASE_URL env var.
import dj_database_url
if not 'DATABASES' in locals():
    DATABASES = {}
DATABASES['default'] = dj_database_url.config()
