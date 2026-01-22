###############################################################################
# Dockerfile for blocklist clean expired script
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.4-build.20260122@sha256:6d56ece83f5b501d9f079a87946ace02b86e490f67fae8d431e49bab72e0d1d7

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS base

RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest-client \
  && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY blocklist_clean_expired.py /bin/

ENTRYPOINT ["/bin/blocklist_clean_expired.py"]
