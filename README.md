# Collecster

A Django application to Collect All The Things !

Please refere to `docs/` for user documentation

## Usage

It is recommended to run Collecster from the Docker container,
publicly available from docker hub as `aadnn/collecter`

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
               -e DATABASE_URL="sqlite:////sqlite.db"   \
               -e DJANGO_SECRET_KEY=${SECRET}           \
               -e DJANGO_SU_NAME=admin                  \
               -e DJANGO_SU_PASSWORD=admin              \
               -e DJANGO_SU_EMAIL=none                  \
               adnn/collecster 

### Building the container

**Reminder:** This is optional, since the container publicly available from docker hub 

    docker build -t adnn/collecster .

### Running out of Docker (manual deployment)

Please refer to `docs/installation`
