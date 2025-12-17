###############################################################################
# Dockerfile for UDM REST API Python Client
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2025 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.4-build.20251216@sha256:9788102246405bc83d736b9a77d0cc32ed41c2b5b04bad4fce99c928ab909f4a

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS base

RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest-client \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

FROM base AS cli

ENTRYPOINT [ "python3", "-m", "univention.admin.rest.client" ]

FROM base AS final

ENTRYPOINT []
