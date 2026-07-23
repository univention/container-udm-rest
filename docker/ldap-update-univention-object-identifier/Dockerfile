# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20260723@sha256:48b6d1495de17562e23862702ed27cb55b9e478bee6deb6e7218580b5d337bfc

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN mkdir -p /opt/univention/ldap-tools

COPY ldap-update-univention-object-identifier.py /opt/univention/ldap-tools
COPY requirements.txt /opt/univention/ldap-tools

RUN apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
    python3-ldap \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

CMD ["python3", "/opt/univention/ldap-tools/ldap-update-univention-object-identifier.py"]
