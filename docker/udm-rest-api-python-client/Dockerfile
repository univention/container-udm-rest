###############################################################################
# Dockerfile for UDM REST API Python Client
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


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-506
ARG UCS_BASE_IMAGE_TAG=0.10.0

FROM ghcr.io/jille/dockpin:v0.3.0 AS dockpin
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as base

# TODO: This would become part of our base image if we would use this tool
COPY --from=dockpin /bin/dockpin /usr/local/sbin/dockpin

# TODO: Workaround, it seems that our base image does not have ssl certificates
# installed
RUN mkdir -p /var/cache/apt/archives/partial \
    && apt-get update \
    && apt-get install --no-install-recommends --yes ca-certificates \
    # TODO: Workaround for missing "Pre-Depends" support in "dockpin"
    # See: https://github.com/Jille/dockpin/issues/18
    && apt-get install --no-install-recommends --yes python3

COPY dockpin-apt.lock /tmp
RUN /usr/local/sbin/dockpin apt install -p /tmp/dockpin-apt.lock

FROM base as cli

ENTRYPOINT [ "python3", "-m", "univention.admin.rest.client" ]

FROM base as final

ENTRYPOINT []
