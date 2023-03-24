###############################################################################
# Dockerfile for UDM REST API
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
ARG DOCKERHUB_CACHE

FROM ${DOCKERHUB_CACHE}debian:${DEBIAN_BASE_IMAGE_TAG} AS build

ARG APT_KEY_URL=https://updates.software-univention.de/univention-archive-key-ucs-5x.gpg

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

WORKDIR /apt

###############################################################################
# Install Univention APT-Key

RUN \
  apt-get update && \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
    ca-certificates=20* \
    curl=7.64.* \
    gpg=2.2.* \
    gpg-agent=2.2.* \
    patch=2.7.* && \
  curl -fsSL "${APT_KEY_URL}" | apt-key add - && \
  rm -rf /var/lib/apt/lists/*

###############################################################################
# Install UDM REST API

COPY sources.list /etc/apt/sources.list.d/15_ucs-online-version.list

# The following scripts get called during dpkg-install but are not required
# in a container environment
COPY fake.sh /usr/local/bin/call_joinscript
COPY fake.sh /usr/local/bin/create_logfile
COPY fake.sh /usr/local/bin/ucr
COPY fake.sh /usr/local/bin/systemctl
COPY fake.sh /usr/local/bin/univention-config-registry
COPY fake.sh /usr/local/bin/stop_udm_cli_server
COPY fake.sh /usr/local/bin/a2dissite
COPY fake.sh /usr/local/bin/umc_frontend_new_hash
COPY fake.sh /usr/local/bin/invoke-rc.d
COPY fake.sh /usr/sbin/univention-management-console-acls

RUN \
  mkdir /usr/share/univention-lib/ && \
  mkdir --parents /var/www/univention-directory-reports && \
  # The original file would source many bash-helper-functions not required here.
  touch /usr/share/univention-lib/all.sh && \
  touch /usr/share/univention-lib/join.sh && \
  touch /usr/share/univention-lib/umc.sh && \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends --assume-yes \
      python3=3.7.* \
      python3-univention-directory-manager-rest=10.* \
      libunivention-debug1=12.* \
      python3-ldap=3.* \
      python3-univention-config-registry=15.* \
      python3-univention-debhelper=2.* \
      python3-six=1.* \
      # dependencies of univention-management-console-module-udm
      python-notifier=0.* \
      univention-directory-manager-tools=15.* \
      univention-directory-reports=12.* \
      univention-management-console-server=12.* \
      univention-config=15.* \
      univention-join=12.* \
      # dependencies of python3-univention-directory-manager-rest
      python3-genshi=0.* \
      python3-mimeparse=0.* \
      python3-pycurl=7.* \
      python3-tornado=5.* \
      python3-univention-directory-manager=15.* \
      python3-univention-directory-reports=12.* \
      python3-univention-management-console=12.* \
      python3-uritemplate=0.* \
      univention-management-console-module-udm=10.* \
      univention-saml-schema=7.*  && \
  # static www content, stylesheet, js, etc. without all dependencies
  apt-get download univention-directory-manager-rest && \
  dpkg --force-depends --install univention-directory-manager-rest_10.*.deb && \
  rm univention-directory-manager-rest_10.*.deb \
  rm -rf /apt /var/lib/apt/lists/* && \
  awk \
    '/^Package: python3-univention-directory-manager-rest$/{ while(!/^Version: /){getline} print $2 }' \
    /var/lib/dpkg/status > /version

###############################################################################
# Apply patches for containerization

WORKDIR /
COPY patch-openapi.patch /udm/patch-openapi.patch
RUN \
  patch -p1 < /udm/patch-openapi.patch

###############################################################################
# Second stage image to get rid of unneeded files

FROM ${DOCKERHUB_CACHE}debian:${DEBIAN_BASE_IMAGE_TAG} AS final

ARG APT_KEY_URL=https://updates.software-univention.de/univention-archive-key-ucs-5x.gpg
ARG LABEL_CREATED=undefined
ARG LABEL_REVISION=undefined
ARG LABEL_SOURCE=undefined
ARG LABEL_VERSION=undefined

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

WORKDIR /apt

RUN \
  apt-get update && \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
    ca-certificates=20* \
    curl=7.64.* \
    gpg=2.2.* \
    gpg-agent=2.2.* && \
  curl -fsSL "${APT_KEY_URL}" | apt-key add - && \
  rm -rf /var/lib/apt/lists/*

COPY sources.list /etc/apt/sources.list.d/15_ucs-online-version.list
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive \
    apt-get install --assume-yes --verbose-versions --no-install-recommends \
      libc-bin=2.* \
      libcurl3-gnutls=7.* \
      locales=2.* \
      python3=3.7.* \
      python3-ldap=3.* \
      python3-six=1.* \
      python3-pil=5.* \
      python3-magic=2:0.* \
      python3-samba=2:4.* \
      python3-cracklib=2.* \
      python3-univention-heimdal=10.* \
      && \
  apt-get download \
   libunivention-config0=15.* \
   libunivention-debug1=12.* \
   libunivention-license0=11.* \
   libunivention-policy0=11.* \
   && \
  dpkg --install --force-depends /apt/* && \
  rm -rf /apt /var/lib/apt/lists/*

WORKDIR /

# Copy python3 dependencies
COPY --from=build \
  /usr/lib/python3/dist-packages/ \
  /usr/lib/python3/dist-packages/

# Copy favicons
COPY --from=build \
  /usr/share/univention-management-console-frontend/js/dijit/themes/umc/icons/ \
  /usr/share/univention-management-console-frontend/js/dijit/themes/umc/icons/
# available reports
COPY --from=build \
  /etc/univention/directory/reports/ \
  /etc/univention/directory/reports/
# static web, e.g. stylesheets and js
COPY --from=build \
  /var/www/univention/udm/ \
  /var/www/univention/udm/

# dummmy UCR
COPY --from=build \
  /etc/univention/*.conf \
  /etc/univention/

COPY --from=build \
  /version \
  /version

RUN \
  echo > /usr/lib/python3/dist-packages/univention/lib/package_manager.py && \
  #
  # build all locales
  echo -en 'en_US.UTF-8 UTF-8\nde_DE.UTF-8 UTF-8\n' >> /etc/locale.gen && \
    localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8 && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 && \
  #
  # for base.conf:
  mkdir --parents /etc/univention/ && \
  #
  # for CAcert.pem
  mkdir --parents /etc/univention/ssl/ucsCA/ && \
  #
  mkdir /udm/ && \
  #
  # create stub for AppCenter attributes mapping
  # See: https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/-/issues/1
  mkdir --parents /var/lib/univention-appcenter/attributes/ && \
  echo '{}' > /var/lib/univention-appcenter/attributes/mapping.json

COPY entrypoint.sh /udm/
COPY env_to_ucr.py /udm/
WORKDIR /udm/

ENTRYPOINT ["/udm/entrypoint.sh"]

# Parameters for UDM
CMD [ \
  "-d", "4", \
  "-p", "9979", \
  "-i", "0.0.0.0", \
  "-c", "0" \
]

EXPOSE 9979
LABEL org.opencontainers.image.created="${LABEL_CREATED}"
LABEL org.opencontainers.image.description="REST service for UCS Directory Manager"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.revision=$LABEL_REVISION
LABEL org.opencontainers.image.source="${LABEL_SOURCE}"
LABEL org.opencontainers.image.title="udm-rest"
LABEL org.opencontainers.image.url="https://docs.software-univention.de/developer-reference/5.0/en/udm/rest-api.html"
LABEL org.opencontainers.image.vendor="Univention GmbH"
LABEL org.opencontainers.image.version="${LABEL_VERSION}"


############################################################
# Third stage to create a debug image

FROM final as debug

SHELL ["/bin/bash", "-c"]

# make this container debugable:
RUN apt-get update -qq && \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --no-install-recommends -y install \
  vim=2:8.* \
  curl=7.* \
  netcat=1.* \
  iproute2=4.* \
  && \
  rm -rf /var/lib/apt/lists/*

# [EOF]
