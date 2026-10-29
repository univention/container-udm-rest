###############################################################################
# Dockerfile for blocklist clean expired script
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025-2026 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.7-build.20261029@sha256:ea7a4e49b0e9380901af1a3a6ffb49e50a1f952eb483f3628f75c84a98c09ee6

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS base

RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest-client \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY blocklist_clean_expired.py /bin/

ENTRYPOINT ["/bin/blocklist_clean_expired.py"]
