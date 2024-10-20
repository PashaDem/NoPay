FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip3 install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --only main

COPY src/django-entrypoint.sh .
RUN chmod +x django-entrypoint.sh

COPY src .
