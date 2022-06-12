FROM python:3.9
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
RUN pip install -r requirements.txt

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 main:app