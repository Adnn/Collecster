============
Installation
============

************
Requirements
************

Collecster was written as a Python 3 Django application, developped with Django 1.9 (and the intention to keep it 
compatible with future releases of Django).

The required Python modules are all available from pip, and listed in *requirements.txt*

.. note::
   Do not install those manually by reading the file. Virtualenv can do that for you.

On my development environment (Linux like, with postgres database),
the following additional binary packages required installation:

* python-dev
* libpq-dev
* libjpeg62-dev

Make sure to have access to a dedicated database (ideally through a dedicated user). Note that you can alternatively
use the sqlite backend of Django.

*********
Procedure
*********

#. Clone the project from https://github.com/Adnn/Collecster.git


#. Start a virtualenv, activate it and install the pip modules:::

       $ virtualenv venv -p python3
       $ source venv/bin/activate
       (venv)$ pip install -r requirements.txt


#. Configure the installed applications in *Collecsters/local_settings.py*. 
   By default, :ref:`supervisor <supervisor_user>` and :ref:`advideogame_user` are installed.


#. Configure the environment. The Django secret key and database config are read from a *.env* file at the root of the project.
   It should contain something of the form:::

       DATABASE_URL='see below' 
       DJANGO_SECRET_KEY='change_to_a_django_secret_key'

   For ``DATABASE_URL`` values, see `dj-database URL schema documentation <https://github.com/kennethreitz/dj-database-url#url-schema>`_.

#. Run initial database creation steps. This will notably ask you to create the superuser for Django::

       (venv)$ export $(cat .env | xargs) #export the environnement variable from .env
       (venv)$ scripts/initialize_db.sh

#. Create a user for Collecster application, and assign it to a deployed configuration 
   (in this case, the user *myuser* is created and assigned configuration *advideogame* as its config with index *1*):::

       (venv)$ python manage.py adduserext myuser
       (venv)$ python manage.py addusercollection myuser advideogame 1

#. It should now be possible to start the application server:::

       (venv)$ scripts/activate_and_run.sh gunicorn -c gunicorn_conf.py Collecster.wsgi  

   And to access the application by pointing a web browser to http://localhost:9090/admin/ (loging with the user created
   during previous step).
