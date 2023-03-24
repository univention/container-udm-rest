ARG DOCKER_PROXY

FROM ${DOCKER_PROXY}hadolint/hadolint:v2.7.0 as hadolint

FROM ${DOCKER_PROXY}koalaman/shellcheck:v0.9.0 as shellcheck

# hadolint ignore=DL3007
FROM docker-registry.knut.univention.de/knut/pre-commit@sha256:8e37d7a194557e86cedb618d7d0c4513cc2ce495918a9b09685b79967e3412d3 as base

# Note: Installing hadolint is somewhat cumbersome.
#
# This approach is inspired by the way how the upstream project builds their
# images.
#
# Compare https://github.com/hadolint/hadolint/blob/master/docker/Dockerfile

COPY --from=hadolint /bin/hadolint /bin/hadolint
COPY --from=shellcheck /bin/shellcheck /bin/shellcheck

# hadolint ignore=DL3008
RUN apt-get -qq update \
    && apt-get --assume-yes --no-install-recommends install \
      ca-certificates \
      curl \
    && curl -SL https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose \
    && chmod a+x /usr/local/bin/docker-compose \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*
