ResetApp() {
    # First, update the DB so it thinks no migrations were applied to the app
    python manage.py migrate --fake $1 zero

    # Erase all migrations in the app folder
    rm -r $1/migrations/*

    # Erase the application tables
    python manage.py sqlclear $1 | python manage.py dbshell

    # Restart the app tables
    python manage.py makemigrations $1
    python manage.py migrate $1
}
