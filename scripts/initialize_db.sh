#!/bin/bash

python manage.py migrate auth &&        \
printf "\nCreating the SUPERUSER:\n" && \
python manage.py createsuperuser &&     \
python manage.py migrate &&             \
python manage.py loaddata groups
