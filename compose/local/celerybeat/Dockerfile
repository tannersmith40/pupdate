FROM python:3.11-slim-bullseye
ARG BUILD_ENVIRONMENT=local
WORKDIR /app

COPY . /app
RUN mkdir -p /app/log
# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  gcc libpq-dev libc-dev\
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "lancaster", "beat", "--loglevel=info"]
