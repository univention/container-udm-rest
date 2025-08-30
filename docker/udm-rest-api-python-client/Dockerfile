###############################################################################
# Dockerfile for UDM REST API Python Client
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2025 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.2-build.20250828@sha256:40615df599a3ac99e351c04d42895bb2f5104b8f95528ffe62bdc78b73bb6a44

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS base

RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest-client \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

FROM base AS cli

ENTRYPOINT [ "python3", "-m", "univention.admin.rest.client" ]

FROM base AS final

ENTRYPOINT []
