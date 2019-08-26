FROM ubuntu:18.04 as copy-image

# advideogame and supervisor are applications explicitly listed in local_settings.py
# advideogame imports from config_template and data_manager
COPY advideogame /Collecster/advideogame
COPY Collecster /Collecster/Collecster
COPY config_template /Collecster/config_template 
COPY data_manager /Collecster/data_manager
COPY scripts /Collecster/scripts
COPY supervisor /Collecster/supervisor
COPY manage.py gunicorn_conf.py requirements.txt /Collecster/

###

FROM ubuntu:18.04

COPY --from=copy-image /Collecster /Collecster/

WORKDIR /Collecster

RUN apt-get update \
    # Install the application requirements
    && apt-get install -y python3 python3-pip libpq-dev git \
    && pip3 install -r requirements.txt \
    # Installs docker-entrypoint.sh script
    && git clone -c advice.detachedHead=false --depth 1 --branch 1.0.0 https://github.com/Adnn/docker-entrypoint.git \
    && mv docker-entrypoint/docker-entrypoint.sh / \
    && rm -r docker-entrypoint/ \
    # Create the entrypoints
    && mkdir /docker-entrypoint.d \
    && ln -s /Collecster/scripts/initialize_db.sh /docker-entrypoint.d/020-initialize_db \
    # Clean up the image
    && apt-get remove -y --purge git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["gunicorn", "-c", "gunicorn_conf.py", "Collecster.wsgi"]

EXPOSE 80

