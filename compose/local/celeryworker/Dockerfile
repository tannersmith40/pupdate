ARG PYTHON_VERSION=3.11-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as builder1

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  wget gcc gnupg libpq-dev libc-dev\
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update && apt-get install --no-install-recommends -y google-chrome-stable

FROM builder1 as builder2
RUN mkdir -p /app/log
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install selenium webdriver-manager
COPY ./compose/local/fastapi/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
COPY ./compose/local/celeryworker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/celerybeat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN mkdir -p log
RUN mkdir -p scraper/log
RUN mkdir -p scraper/debug
RUN mkdir -p /root/.wdm/drivers


#COPY ./compose/local/django/celery/flower/start /start-flower
#RUN sed -i 's/\r$//g' /start-flower
#RUN chmod +x /start-flower

# Add an entrypoint script to run Alembic migrations before starting the app
COPY ./compose/local/celeryworker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

#CMD ["uvicorn", "lancaster.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]