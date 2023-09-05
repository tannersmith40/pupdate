ARG PYTHON_VERSION=3.11-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  gcc libpq-dev libc-dev\
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./compose/local/fastapi/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


# Add an entrypoint script to run Alembic migrations before starting the app
COPY ./compose/${BUILD_ENVIRONMENT}/fastapi/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

#CMD ["uvicorn", "back.lancaster.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]