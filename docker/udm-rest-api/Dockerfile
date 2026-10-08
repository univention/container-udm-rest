###############################################################################
# Dockerfile for UDM REST API
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2026 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.7-build.20260924@sha256:f856cd5bcb3588fd14a7d17a5da44ea58b72703b29c95720629753c66e7fde1c

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
  # used by the final stage to apply patches/
  patch \
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
  univention-heimdal-common \
  univention-ldap-config-master \
  univention-management-console-module-udm \
  univention-saml-schema \
  # telemetry sender and its dependencies
  univention-telemetry \
  python3-prometheus-client \
  python3-requests \
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

# Record all installed Debian packages owning at least one non-directory entry
# below /usr/lib/python3/dist-packages as "<package>=<version>", one per line.
# The final stage installs exactly these versions via dpkg, so that SBOM
# scanners attribute the Python modules to their Debian packages.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# hadolint ignore=SC2016
RUN \
  for list in /var/lib/dpkg/info/*.list; do \
    pkg="$(basename "${list}" .list)"; \
    # "|| true": grep fails without matches or on SIGPIPE after "break"
    { grep '^/usr/lib/python3/dist-packages/.' "${list}" || true; } | \
    while IFS= read -r path; do \
      if [ -L "${path}" ] || [ ! -d "${path}" ]; then echo "${pkg}"; break; fi; \
    done; \
  done | \
  xargs --no-run-if-empty \
  dpkg-query --show --showformat='${db:Status-Abbrev} ${Package}=${Version}\n' | \
  awk '$1 == "ii" { print $2 }' | \
  LC_ALL=C sort --unique > /python-packages.list && \
  test -s /python-packages.list && \
  cat /python-packages.list


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
  python3-certifi \
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

# Install the Debian packages providing /usr/lib/python3/dist-packages in the
# exact versions recorded in the build stage, instead of copying the files.
# The build stage's /usr/local/bin provides the fake commands called by the
# maintainer scripts, its /usr/share/univention-lib the Univention shell
# library (with all.sh, join.sh and umc.sh replaced by fake-uv-lib.sh).
# Afterwards patches/ is applied on top of the pristine files from the Debian
# packages, using the patch tool from the build stage.
WORKDIR /apt/python

# hadolint ignore=SC2016
RUN \
  --mount=type=bind,from=build,source=/usr/local/bin,target=/usr/local/bin \
  --mount=type=bind,from=build,source=/usr/share/univention-lib,target=/usr/share/univention-lib \
  --mount=type=bind,from=build,source=/python-packages.list,target=/python-packages.list \
  --mount=type=bind,from=build,source=/usr/bin/patch,target=/usr/bin/patch \
  --mount=type=bind,source=patches,target=/patches \
  chown _apt . && \
  # skip packages which are already installed in exactly this version
  while IFS='=' read -r pkg version; do \
    installed="$(dpkg-query --show --showformat='${db:Status-Abbrev}${Version}' "${pkg}" 2>/dev/null)"; \
    if [ "${installed}" != "ii ${version}" ]; then \
      echo "${pkg}=${version}"; \
    fi; \
  done < /python-packages.list > python-packages.download && \
  # /usr/local/bin/systemctl is a copy of fake.sh
  cp /usr/local/bin/systemctl /usr/sbin/univention-management-console-acls && \
  mkdir --parents /var/www/univention-directory-reports && \
  xargs --no-run-if-empty apt-get download < python-packages.download && \
  dpkg --force-depends --install ./*.deb && \
  # remove the fake again unless a package took over the file
  { dpkg-query --search /usr/sbin/univention-management-console-acls > /dev/null 2>&1 || \
    rm /usr/sbin/univention-management-console-acls; } && \
  # "|| exit 1": a for loop only returns the status of its last iteration
  for p in /patches/*.patch; do \
    patch --no-backup-if-mismatch -p 4 \
      -d /usr/lib/python3/dist-packages/ -i "${p}" || exit 1; \
  done && \
  rm ./*

WORKDIR /

# UDM tool scripts used by k8s CronJobs or scripts
COPY --from=build \
  /usr/share/univention-directory-manager-tools/univention-update-license-cache \
  /usr/share/univention-directory-manager-tools/univention-blocklist-clean-expired-entries \
  /usr/share/univention-directory-manager-tools/remove_krb5key_keytypes \
  /usr/share/univention-directory-manager-tools/remove_sambantpassword \
  /usr/share/univention-directory-manager-tools/

COPY --from=build \
  /usr/share/univention-ldap/univention-update-univention-object-identifier \
  /usr/share/univention-ldap/

RUN sed -i 's/getRootDnConnection/getAdminConnection/g' /usr/share/univention-ldap/univention-update-univention-object-identifier

COPY --from=build \
  /usr/share/univention-telemetry/univention-telemetry-sender \
  /usr/share/univention-telemetry/

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
  mkdir --parents /etc/krb5/ && \
  #
  mkdir /udm/ && \
  #
  # create stub for AppCenter attributes mapping
  # See: https://git.knut.univention.de/univention/dev/nubus-for-k8s/ldap/-/issues/1
  mkdir --parents /var/lib/univention-appcenter/attributes/ && \
  echo '{}' > /var/lib/univention-appcenter/attributes/mapping.json

COPY entrypoint.d /entrypoint.d/
COPY --chmod=755 univention-probe-udm.py /usr/local/bin/univention-probe-udm.py
WORKDIR /udm/

RUN adduser app && \
  chown app:app /etc/krb5
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
