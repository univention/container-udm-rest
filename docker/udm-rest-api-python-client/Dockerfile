###############################################################################
# Dockerfile for UDM REST API Python Client
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2025 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-521
ARG UCS_BASE_IMAGE_TAG=0.18.1-build-2025-05-29

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as base

RUN \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-univention-directory-manager-rest-client

FROM base as cli

ENTRYPOINT [ "python3", "-m", "univention.admin.rest.client" ]

FROM base as final

ENTRYPOINT []
