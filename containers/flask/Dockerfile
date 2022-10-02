FROM python:3.9-slim-buster 
RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y libsqlite3-dev
RUN pip install gunicorn
RUN pip install poetry
COPY poetry.lock pyproject.toml /app/
WORKDIR /app
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi
COPY . /app
WORKDIR /app
ENTRYPOINT [ "/app/entrypoint.sh" ]