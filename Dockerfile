FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1 \
    POETRY_VERSION=1.4.2

WORKDIR /app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/django-entrypoint.sh .
RUN chmod +x django-entrypoint.sh

COPY src .