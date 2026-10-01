FROM python:3.9-slim

WORKDIR /usr/src/app

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN pip install poetry

COPY poetry.lock /usr/src/app/
COPY pyproject.toml /usr/src/app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root

COPY . /usr/src/app/

RUN poetry install --no-interaction --only-root

HEALTHCHECK CMD python -c "" || exit 1


ENTRYPOINT ["poetry", "run", "python"]
