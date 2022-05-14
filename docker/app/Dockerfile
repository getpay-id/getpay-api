FROM python:3.9-buster
LABEL maintainer="Aprila Hijriyan <me@aprila.dev>"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_IGNORE_INSTALLED 1
COPY ./app /space/app
COPY ./Pipfile /space/Pipfile
COPY ./Pipfile.lock /space/Pipfile.lock
COPY ./.env /space/.env
COPY ./install.py /space/install.py
WORKDIR /space
RUN pip install -U pip pipenv
RUN pipenv install --system --deploy --ignore-pipfile
COPY ./docker/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
