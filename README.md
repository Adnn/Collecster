# Collecster

A Django application to Collect All The Things !

Please refere to `docs/` for user documentation

## Usage

It is recommended to run Collecster from the Docker container,
publicly available from docker hub as `adnn/collecster`

The deployment and runtime rely on the following environment variables:

    # Only read at DB initialization time
    DJANGO_SU_NAME # Super user login
    DJANGO_SU_PASSWORD # Super user password
    DJANGO_SU_EMAIL # Super user email

    # Also read during server initialization (i.e. runtime)
    DJANGO_SECRET_KEY=...
    DATABASE_URL="sqlite:///sqlite.db" # Or any other


Note: [dj-database URL schema documentation](https://github.com/kennethreitz/dj-database-url#url-schema)

Example command:

    touch sqlite.db # File must exist, otherwise docker creates a directory
    docker run -p 8080:80                               \
               -v $(pwd)/sqlite.db:/sqlite.db           \
               -v $(pwd)/backups:/Collecster/backups    \
               -e DATABASE_URL="sqlite:////sqlite.db"   \
               -e DJANGO_SECRET_KEY=${SECRET}           \
               -e DJANGO_SU_NAME=admin                  \
               -e DJANGO_SU_PASSWORD=admin              \
               -e DJANGO_SU_EMAIL=none                  \
               adnn/collecster

### Backups

Collecster relies on django-backup project to provide `backup` and `restore` management commands
Different settings controling the backup process are available in Collecster/local_settings.py,
including the default folder for backups

    # Making a backup
    docker exec ${CONTAINER} python3 manage.py archive

    # Restoring from a backup
    docker exec ${CONTAINER} python3 manage.py restore ${ARCHIVE_BASENAME}


### Running out of Docker (manual deployment)

Please refer to `docs/installation`

## Build

### Building the container

**Reminder:** This is optional, since the container publicly available from docker hub

    docker build -t adnn/collecster .

### Automation

Docker images are automatically built on [dockerhub](https://hub.docker.com/) when commits are pushed to specific git branches:

* **master**: `adnn/collecster:latest`
* **develop**: `adnn/collecster:latest-dev`
* **1.9.3**: `adnn/collecster:1.9.3`

## Thanks

[FranzPoize](https://github.com/FranzPoize) & [paradoxxxzero](https://github.com/paradoxxxzero) for both moral and technical support!
