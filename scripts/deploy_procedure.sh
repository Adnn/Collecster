#!/bin/bash

##
## Arguments parsing
##
if [ $# -ne 2 ]
then
    echo "This script must receive two arguments: the path were to deploy Collecster, and the path to 'django-archive'."
    exit -1
fi

DEST="$1"
DJANGO_ARCHIVE="$2"

if [[ ! -d $DEST ]]
then
    echo "The first argument must be the path to an existing directory."
    exit -1
fi

if [ "$(basename $DJANGO_ARCHIVE)" != "django_archive" ]
then
    echo "The second argument must end in 'django_archive/'"
    exit -1
fi

##
## Start deployment
##
cd $DEST

if [ -d "$DEST/Collecster" ]
then
    tmpd=$(mktemp -d)       && \
    echo "Previous installation found. Saving settings in "$tmpd
    cp $DEST/Collecster/.env $tmpd 
    cp $DEST/Collecster/Collecster/local_settings.py $tmpd
    rm -rf $DEST/Collecster/* $DEST/Collecster/.*
fi

git clone https://github.com/Adnn/Collecster.git    && \
cd $DEST/Collecster  && \
virtualenv venv -p /usr/local/bin/python3.4 && \
source venv/bin/activate

if [ -d "$tmpd" ]
then
    echo "Restoring settings from '"$tmpd"'"
    cp $tmpd/.env $DEST/Collecster
    cp $tmpd/local_settings.py $DEST/Collecster/Collecster
    rm -r $tmpd
fi

if [ -f ".env" ]
then
    export $(cat .env | xargs)
fi

pip install -r requirements.txt && \
ln -s "$DJANGO_ARCHIVE" venv/lib/python3.4/site-packages/ && \
scripts/initialize_db.sh
