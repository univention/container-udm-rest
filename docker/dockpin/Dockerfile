ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-506
ARG UCS_BASE_IMAGE_TAG=0.11.3

FROM ghcr.io/jille/dockpin:v0.3.0 AS dockpin
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as base

COPY --from=dockpin /bin/dockpin /usr/local/sbin/dockpin

WORKDIR /src
