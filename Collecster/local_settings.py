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
    #"advg",
    "supervisor",
    "videogame",
    "ndmusic",
)

# The secret key is now to be found in $DJANGO_SECRET_KEY env var. This file is no longer private !
import os
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']


##
## From here: copied from https://devcenter.heroku.com/articles/getting-started-with-django#django-settings
##

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {} # Added, because the symbol is not defined otherwise
DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
            os.path.join(BASE_DIR, 'static'),
)
