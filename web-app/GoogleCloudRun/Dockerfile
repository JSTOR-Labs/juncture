FROM python:3.9

RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini; \
    apt-get clean; \
    rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/*

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN set -e; pip install bs4 Flask Flask-Cors html5lib requests uWSGI

ENV PORT 8080

ENTRYPOINT ["tini", "--"]
CMD uwsgi --http :${PORT} --manage-script-name --mount /app=main:app --enable-threads --processes 8 --buffer-size 65535