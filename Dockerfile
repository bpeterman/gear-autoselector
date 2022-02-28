FROM python:3.10-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

WORKDIR /gear_app

RUN pip install poetry

COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /gear_app

RUN chmod +x /gear_app/etc/start-server.sh
