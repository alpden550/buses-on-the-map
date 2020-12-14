FROM python:3.9.0-alpine3.12

ENV POETRY_VIRTUALENVS_CREATE=false

RUN apk update && apk add gcc python3-dev musl-dev build-base curl libffi-dev

WORKDIR /app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH = "${PATH}:/root/.poetry/bin"

COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

RUN poetry install

COPY . /app

EXPOSE 8000
