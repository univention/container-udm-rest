###############################################################################
# Dockerfile for UDM REST API
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.3-build.20251016@sha256:779104f80174bea204d5e48de723302320bf73e6ef58a0e200ff77cc87ded4c2


FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build

###############################################################################
# Install UDM REST API

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
COPY fake-uv-lib.sh /usr/local/bin/fake-uv-lib.sh

WORKDIR /apt

# hadolint ignore=SC2016
RUN chown _apt . && \
  # install Univention bash helper functions dependency
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  shell-univention-lib \
  && \
  # we do not need the many bash helper-functions here
  cp /usr/local/bin/fake-uv-lib.sh /usr/share/univention-lib/all.sh && \
  cp /usr/local/bin/fake-uv-lib.sh /usr/share/univention-lib/join.sh && \
  cp /usr/local/bin/fake-uv-lib.sh /usr/share/univention-lib/umc.sh && \
  mkdir --parents /var/www/univention-directory-reports && \
  # install unlisted dependencies
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-distutils \
  && \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  python3-univention-directory-manager-rest \
  libsasl2-modules-oauthbearer \
  libunivention-debug1 \
  python3-ldap \
  python3-univention-authorization \
  python3-univention-config-registry \
  python3-univention-debhelper \
  # dependencies of univention-management-console-module-udm
  univention-directory-manager-tools \
  univention-directory-reports \
  univention-management-console-server \
  univention-config \
  univention-join \
  # dependencies of python3-univention-directory-manager-rest
  python3-genshi \
  python3-mimeparse \
  python3-pycurl \
  python3-tornado \
  python3-univention-directory-manager \
  python3-univention-directory-reports \
  python3-univention-management-console \
  python3-uritemplate \
  univention-management-console-module-udm \
  univention-saml-schema \
  && \
  # univention-portal module:
  # /usr/lib/python3/dist-packages/univention/udm/modules/portal.py
  apt-get download univention-portal && \
  dpkg --force-depends --install univention-portal_6.*.deb && \
  # static www content, stylesheet, js, etc. without all dependencies
  apt-get download univention-directory-manager-rest && \
  dpkg --force-depends --install univention-directory-manager-rest_12.*.deb && \
  rm univention-directory-manager-rest_12.*.deb && \
  dpkg-query -f '${Version}' -W python3-univention-directory-manager-rest > /version


###############################################################################
# Second stage image to get rid of unneeded files


FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
LABEL org.opencontainers.image.created="${LABEL_CREATED}"
LABEL org.opencontainers.image.description="REST service for UCS Directory Manager"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.revision=$LABEL_REVISION
LABEL org.opencontainers.image.source="${LABEL_SOURCE}"
LABEL org.opencontainers.image.title="udm-rest"
LABEL org.opencontainers.image.url="https://docs.software-univention.de/developer-reference/5.0/en/udm/rest-api.html"
LABEL org.opencontainers.image.vendor="Univention GmbH"
LABEL org.opencontainers.image.version="${LABEL_VERSION}"
ARG LABEL_CREATED=undefined
ARG LABEL_REVISION=undefined
ARG LABEL_SOURCE=undefined
ARG LABEL_VERSION=undefined

WORKDIR /apt

RUN chown _apt . && \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  libc-bin \
  libcurl3-gnutls \
  libjansson4 \
  librhonabwy1.1 \
  locales \
  python3 \
  python3-ldap \
  python3-pil \
  python3-magic \
  python3-samba \
  python3-cracklib \
  python3-univention-heimdal \
  && \
  apt-get download \
  libunivention-config0 \
  libunivention-debug1 \
  libunivention-license0 \
  libunivention-policy0 \
  && \
  dpkg --install --force-depends /apt/*

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

# UCR

COPY --from=build \
  /etc/univention/*.conf \
  /etc/univention/
COPY --from=build \
  /usr/sbin/univention-config-registry \
  /usr/sbin/ucr \
  /usr/sbin/
COPY --from=build \
  /etc/univention/templates \
  /etc/univention/templates

COPY --from=build \
  /version \
  /version

# OAUTHBEARER
COPY --from=build \
  /usr/lib/x86_64-linux-gnu/sasl2/liboauthbearer.so.0.2.0 \
  /usr/lib/x86_64-linux-gnu/sasl2/

RUN \
  ln -s /usr/lib/x86_64-linux-gnu/sasl2/liboauthbearer.so.0.2.0 \
  /usr/lib/x86_64-linux-gnu/sasl2/liboauthbearer.so.0 \
  \
  && ln -s /usr/lib/x86_64-linux-gnu/sasl2/liboauthbearer.so.0.2.0 \
  /usr/lib/x86_64-linux-gnu/sasl2/liboauthbearer.so

RUN \
  echo > /usr/lib/python3/dist-packages/univention/lib/package_manager.py && \
  #
  # build all locales
  printf 'en_US.UTF-8 UTF-8\nde_DE.UTF-8 UTF-8\n' >> /etc/locale.gen && \
  localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8 && \
  localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 && \
  #
  # for base.conf:
  mkdir --parents /etc/univention/ && \
  #
  # for UCR:
  mkdir --parents \
  /var/cache/univention-config/ \
  /var/log/univention/ && \
  #
  # for CAcert.pem
  mkdir --parents /etc/univention/ssl/ucsCA/ && \
  #
  mkdir /udm/ && \
  #
  # create stub for AppCenter attributes mapping
  # See: https://git.knut.univention.de/univention/dev/nubus-for-k8s/ldap/-/issues/1
  mkdir --parents /var/lib/univention-appcenter/attributes/ && \
  echo '{}' > /var/lib/univention-appcenter/attributes/mapping.json

COPY entrypoint.d /entrypoint.d/
WORKDIR /udm/

RUN adduser app
USER app

# Parameters for UDM
# --processes 0 means one process per cpu core
# When deployed using Helm, CMD will be overwritten with values from
# container-udm-rest/helm/udm-rest-api/templates/deployment.yaml.
CMD [ \
  "python3", \
  "-m", "univention.admin.rest.server", \
  "--debug", "2", \
  "--port", "9979", \
  "--interface", "0.0.0.0", \
  "--processes", "1" \
  ]

EXPOSE 9979

############################################################
# Third stage to create a debug image

FROM final AS debug

# hadolint ignore=DL3002
USER root
SHELL ["/bin/bash", "-c"]

# make this container debugable:
RUN \
  DEBIAN_FRONTEND=noninteractive \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  vim \
  curl \
  netcat-traditional \
  iproute2=6.*


############################################################
# Fourth stage to create an image for running tests

FROM final AS test

# hadolint ignore=DL3002
USER root
SHELL ["/bin/bash", "-c"]

# load a UCR config for testing
COPY test-base.conf /etc/univention/base.conf

# [EOF]
