# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.3-build.20251128@sha256:2febf0d2be06f0cca264085db0270c2c61170ea93d14c7ff840c61ecd5328c70

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
