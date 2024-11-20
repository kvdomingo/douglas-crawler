FROM python:3.12-slim AS base

ENV DEBIAN_FRONTEND=noninteractive

FROM base AS build

ENV POETRY_VERSION=1.8.4
ENV POETRY_HOME=/opt/poetry
ENV PATH=${PATH}:${POETRY_HOME}/bin

WORKDIR /tmp

SHELL [ "/bin/sh", "-eu", "-c" ]

# hadolint ignore=DL4006
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    poetry config virtualenvs.create false && \
    apt-get remove -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN poetry export --format requirements.txt --without dev --without-hashes --output requirements.txt

WORKDIR /app

RUN python -m venv .venv && \
    /app/.venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

FROM base AS prod

LABEL org.opencontainers.image.source="https://github.com/kvdomingo/douglas-crawler"
LABEL org.opencontainers.image.url="https://github.com/kvdomingo/douglas-crawler"
LABEL org.opencontainers.image.authors="Kenneth V. Domingo <hello@kvd.studio>"
LABEL org.opencontainers.image.title="Douglas Crawler"

WORKDIR /app

COPY douglas douglas
COPY migrations migrations
COPY scripts scripts
COPY alembic.ini alembic.ini
COPY --from=build /app/.venv ./.venv

ENTRYPOINT [ "/bin/sh", "-eu", "-c" ]
CMD [ "exec /app/.venv/bin/fastapi run /app/douglas/api.py --port 8000 --proxy-headers" ]
