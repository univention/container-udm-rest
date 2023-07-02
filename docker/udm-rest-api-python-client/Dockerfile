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


ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-ucs-base/ucs-base-dev-504
ARG UCS_BASE_IMAGE_TAG=latest

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

RUN ucs-dev-add-branch.sh jbornhold-udm-rest-client \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-univention-directory-manager-rest-client=10.* \
      python3-yaml=3.* \
      # TODO: Tweak upstream debian package, missing dependencies
      python3-requests=2.* \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*
