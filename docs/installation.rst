============
Installation
============

************
Requirements
************

Collecster was written as a Python3 Django application, developped with Django 1.9
(and the intention to keep it compatible with future releases of Django).

The required Python modules are all available from pip, and listed in *requirements.txt*

.. note::
   Do not install those manually by reading the file. Virtualenv can do that for you.

On my development environment (`ubuntu/bionic64 <https://app.vagrantup.com/ubuntu/boxes/bionic64>` Vagrant box),
the following additional binary packages required installation:::

    $ sudo apt-get install \
                        build-essential \
                        libjpeg-dev \
                        libpq-dev \
                        python3-dev \
                        python3-venv

Make sure to have access to a dedicated database (ideally through a dedicated user).
Note that you can alternatively use the sqlite backend of Django, notably to setup a development environment.

*********
Procedure
*********

#. Clone the project:::

   $ git clone https://github.com/Adnn/Collecster.git
   $ cd Collecster


#. Prepare a virtualenv, activate it and install the pip modules:::

       $ python3 -m venv venv
       $ source venv/bin/activate
       (venv)$ pip3 install wheel # Otherwise, following command fails with "error: invalid command 'bdist_wheel'"
       (venv)$ pip3 install -r requirements.txt


#. Configure the installed applications in *Collecsters/local_settings.py*.
   By default, :ref:`supervisor <supervisor_user>`, :ref:`advideogame_user` and django_archive are installed.


#. Configure the environment via environment variable. Examples:::

       (venv)$ export DJANGO_SU_NAME=admin
       (venv)$ export DJANGO_SU_PASSWORD=admin
       (venv)$ export DJANGO_SU_EMAIL=admin@server.org

       (venv)$ export DATABASE_URL='sqlite:///sqlite.db' # See details below
       (venv)$ export DJANGO_SECRET_KEY='change_to_a_django_secret_key'

   For ``DATABASE_URL`` values, see `dj-database URL schema documentation <https://github.com/kennethreitz/dj-database-url#url-schema>`_.

   If desired, environment variable can be defined in a *.env* file then exported in the current environment with::

       #export the environnement variable from .env
       (venv)$ export $(cat .env | xargs)

#. Run initial database creation steps. This will notably create the super user based on variables values above.::

       (venv)$ scripts/initialize_db.sh

#. Create a user for Collecster application, and assign it to a deployed configuration
   (in this case, the user *myuser* is created and assigned configuration *advideogame* as its config with index *1*):::

       (venv)$ python3 manage.py adduserext myuser
       (venv)$ python3 manage.py addusercollection myuser advideogame 1

#. It should now be possible to start the application server:::

       (venv)$ scripts/activate_and_run.sh gunicorn -c gunicorn_conf.py Collecster.wsgi

   And to access the application by pointing a web browser to http://localhost:80/admin/
   (logging in with the user created during previous step).

   Note: ``activate_and_run.sh`` script is a simple wrapper to load the virtual env before executing a command.
   It can be usefull to start the application from a supervisor. E.g.::

       scripts/activate_and_run.sh gunicorn -c gunicorn_conf_readenv.py Collecster.wsgi

