###############################################################################
# Dockerfile for blocklist clean expired script
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520
ARG UCS_BASE_IMAGE_TAG=0.16.1-build-2025-02-20

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as base

RUN \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-univention-directory-manager-rest-client

COPY blocklist_clean_expired.py /bin/

ENTRYPOINT ["/bin/blocklist_clean_expired.py"]
