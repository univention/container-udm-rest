# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.16.2-build-2025-03-18
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-521

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN mkdir -p /opt/univention/ldap-tools

COPY ldap-update-univention-object-identifier.py /opt/univention/ldap-tools
COPY requirements.txt /opt/univention/ldap-tools

RUN apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip \
      libldap2-dev \
      build-essential \
      python3-dev \
      libldap2-dev \
      libsasl2-dev \
      slapd \
      ldap-utils tox \
      lcov valgrind \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && pip3 install --no-cache-dir --break-system-packages -r /opt/univention/ldap-tools/requirements.txt

CMD ["python3", "/opt/univention/ldap-tools/ldap-update-univention-object-identifier.py"]
