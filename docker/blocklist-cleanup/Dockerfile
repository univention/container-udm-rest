###############################################################################
# Dockerfile for blocklist clean expired script
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025-2026 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.7-build.20261106@sha256:70d082922c26d565cf5bebbf7562063deb0d7282a25623a25fee71045a5bb341

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS base

RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest-client \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY blocklist_clean_expired.py /bin/

ENTRYPOINT ["/bin/blocklist_clean_expired.py"]
