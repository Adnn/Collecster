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

    "django_archive",
)

# The secret key is found in $DJANGO_SECRET_KEY env var.
import os
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']


# django-archive settings
ARCHIVE_DIRECTORY = "/Collecster/backups"
ARCHIVE_FORMAT    = "bz2"
ARCHIVE_MEDIA_POLICY = "all_files"
ARCHIVE_DB_INDENT    = 2


##
## From here: copied from https://devcenter.heroku.com/articles/django-app-configuration#database-configuration
##
# Parse database configuration from $DATABASE_URL env var.
import dj_database_url
if not 'DATABASES' in locals():
    DATABASES = {}
DATABASES['default'] = dj_database_url.config()
