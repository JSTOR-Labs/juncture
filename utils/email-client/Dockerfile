FROM python:3.8

ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

RUN set -e; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini; \
    apt-get clean; \
    rm -rf /var/tmp/* /tmp/* /var/lib/apt/lists/*

RUN set -e; \
    pip install flask flask_cors sendgrid requests PyYAML uwsgi 

WORKDIR /usr/src/app

ADD app.py .
add config.yaml .

ENV PORT 8080

ENTRYPOINT ["tini", "--"]
CMD uwsgi --http :${PORT} --manage-script-name --mount /app=app:app --enable-threads --processes 4