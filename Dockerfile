FROM python:3.12-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV POETRY_VERSION=1.8.4
ENV POETRY_HOME=/opt/poetry
ENV PATH=${PATH}:${POETRY_HOME}/bin

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

# hadolint ignore=DL3009
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

WORKDIR /app

ENTRYPOINT [ "/bin/bash", "-euxo", "pipefail", "-c" ]
