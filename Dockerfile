FROM python:3.12-slim

WORKDIR /code

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root

COPY app ./app
COPY certs ./certs
COPY migrations ./migrations
COPY alembic.ini ./
COPY prestart.sh ./

CMD ["sh", "prestart.sh"]