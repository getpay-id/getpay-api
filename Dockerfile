FROM python:3.9-buster
LABEL maintainer="Aprila Hijriyan <me@aprila.dev>"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_IGNORE_INSTALLED 1
COPY . /space/
WORKDIR /space
RUN pip install -U pip pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN python manage.py init
