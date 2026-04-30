###############################################################################
# Dockerfile for UDM REST API Python Client
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2025 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.5-build.20260430@sha256:03506bb1c0b315bcecc00cb77e7fe7df6f414e581a1a73a9f66f93e731237ae8

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS base

RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest-client \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

FROM base AS cli

ENTRYPOINT [ "python3", "-m", "univention.admin.rest.client" ]

FROM base AS final

ENTRYPOINT []
