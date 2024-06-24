# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023-2024 Univention GmbH

ARG DOCKER_PROXY
ARG PYTHON_TAG=3.11

FROM ${DOCKER_PROXY}python:${PYTHON_TAG}

WORKDIR /testrunner

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir pipenv==2023.6.18 \
    && pipenv sync --dev --system \
    && rm -r ~/.cache

WORKDIR /app

CMD [ "pytest", "tests/integration" ]
