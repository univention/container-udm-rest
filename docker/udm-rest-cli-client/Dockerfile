###############################################################################
# Dockerfile for UDM REST CLI Client
#
# Copyright 2021 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.

ARG DEBIAN_BASE_IMAGE_TAG=buster-slim
ARG DOCKER_PROXY

FROM ${DOCKER_PROXY}debian:${DEBIAN_BASE_IMAGE_TAG} AS ucs-base

ARG APT_KEY_URL=https://updates.software-univention.de/univention-archive-key-ucs-5x.gpg
ARG APT_KEY_URL_DEV=http://omar.knut.univention.de/build2/git/key.pub

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

WORKDIR /

RUN \
  apt-get --quiet update && \
  DEBIAN_FRONTEND=noninteractive \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
      ca-certificates=20* \
      curl=7.64.* \
      gpg=2.2.* \
      gpg-agent=2.2.* \
      patch=2.7.* && \
  curl -fsSL "${APT_KEY_URL}" | apt-key add - && \
  curl -fsSL "${APT_KEY_URL_DEV}" | apt-key add - && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY sources.list /etc/apt/sources.list.d/15_ucs-online-version.list
COPY dev-sources.list /etc/apt/sources.list.d/15_souvap-dev.list


FROM ucs-base as build

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-univention-directory-manager-rest-client=10.* \
      python3-univention-config-registry=15.* \
      netcat=1.* \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*
