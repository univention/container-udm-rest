#!/bin/bash
set -euxo pipefail
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

############################################################
# Prepare LDAP TLS certificates and settings
TLS_MODE="${TLS_MODE:-secure}"

case "${TLS_MODE}" in
  "secure")
    TLS_REQCERT="demand"
    UDM_STARTTLS=2
    ;;
  "unvalidated")
    TLS_REQCERT="allow"
    UDM_STARTTLS=1
    ;;
  "off")
    TLS_REQCERT="never"
    UDM_STARTTLS=0
    ;;
  *)
    echo "TLS_MODE must be one of: secure, unvalidated, off."
    exit 1
esac

if [[ "${TLS_MODE}" != "off" ]]; then
  CA_CERT_FILE=${CA_CERT_FILE:-/run/secrets/ca_cert}
  CA_DIR="/etc/univention/ssl/ucsCA"

  if [[ ! -f "${CA_CERT_FILE}" ]]; then
    echo "\$CA_CERT_FILE is not a file at ${CA_CERT_FILE}"
    exit 1
  fi

  mkdir --parents "${CA_DIR}"
  ln --symbolic --force "${CA_CERT_FILE}" "${CA_DIR}/CAcert.pem"
fi

############################################################
# Store LDAP configuration
cat <<EOF > /etc/ldap/ldap.conf
# This file should be world readable but not world writable.

${CA_DIR:+TLS_CACERT /etc/univention/ssl/ucsCA/CAcert.pem}
TLS_REQCERT ${TLS_REQCERT:-demand}

URI ldap://${LDAP_HOST}:${LDAP_PORT}

BASE ${LDAP_BASE_DN}
EOF
chmod 0644 /etc/ldap/ldap.conf

# TODO: Does this container really need to know this secret?
LDAP_SECRET_FILE=${LDAP_SECRET_FILE:-/run/secrets/ldap_secret}
if [[ -f "${LDAP_SECRET_FILE}" ]]; then
  echo "Using LDAP admin secret"
  ln --symbolic --force "${LDAP_SECRET_FILE}" /etc/ldap.secret
else
  echo "No LDAP admin secret provided!"
fi

# Machine account allows checking which users are authorized to use the API
MACHINE_SECRET_FILE=${MACHINE_SECRET_FILE:-/run/secrets/machine_secret}
if [[ -f "${MACHINE_SECRET_FILE}" ]]; then
  echo "Using LDAP machine secret from file"
  ln --symbolic --force "${MACHINE_SECRET_FILE}" /etc/machine.secret
elif [[ -n "${MACHINE_SECRET:-}" ]]; then
  echo "Using LDAP machine secret from env"
  echo -n "${MACHINE_SECRET}" > /etc/machine.secret
else
  echo "No LDAP machine secret found at ${MACHINE_SECRET_FILE} and \$MACHINE_SECRET not set!"
  echo "Check the \$MACHINE_SECRET_FILE variable and the file that it points to."
  exit 1
fi

############################################################
# Configure Univention Directory Reports
# (In UCS this is done by `ucr commit`.)
cat <<EOF > /etc/univention/directory/reports/config.ini
[DEFAULT]
# default report name
report=PDF Document

[reports]
csv/computer1=computers/computer "CSV Report" /etc/univention/directory/reports/default computers.csv
csv/group1=groups/group "CSV Report" /etc/univention/directory/reports/default groups.csv
csv/user1=users/user "CSV Report" /etc/univention/directory/reports/default users.csv
pdf/computer1=computers/computer "PDF Document" /etc/univention/directory/reports/default computers.rml
pdf/group1=groups/group "PDF Document" /etc/univention/directory/reports/default groups.rml
pdf/user1=users/user "PDF Document" /etc/univention/directory/reports/default users.rml
EOF

############################################################
# Fill UCR
AUTHORIZED_DC_BACKUP=${AUTHORIZED_DC_BACKUP:-cn=DC Backup Hosts,cn=groups,dc=example,dc=org}
AUTHORIZED_DC_SLAVES=${AUTHORIZED_DC_SLAVES:-cn=DC Slave Hosts,cn=groups,dc=example,dc=org}
AUTHORIZED_DOMAIN_ADMINS=${AUTHORIZED_DOMAIN_ADMINS:-cn=Domain Admins,cn=groups,dc=example,dc=org}

ucr set \
  ldap/master="${LDAP_HOST}" \
  ldap/master/port="${LDAP_PORT}" \
  ldap/server/name="${LDAP_HOST}" \
  ldap/server/port="${LDAP_PORT}" \
  ldap/hostdn="${LDAP_HOST_DN}" \
  ldap/base="${LDAP_BASE_DN}" \
  domainname="${DOMAINNAME:-}" \
  hostname="${HOSTNAME:-}" \
  directory/manager/rest/authorized-groups/dc-backup="${AUTHORIZED_DC_BACKUP}" \
  directory/manager/rest/authorized-groups/dc-slaves="${AUTHORIZED_DC_SLAVES}" \
  directory/manager/rest/authorized-groups/domain-admins="${AUTHORIZED_DOMAIN_ADMINS}" \
  directory/manager/rest/debug_level="${DEBUG_LEVEL}" \
  directory/manager/rest/ldap-connection/user-read/start-tls="${UDM_STARTTLS}" \
  directory/manager/templates/alphanum/whitelist="" \
  directory/manager/user/activate_ldap_attribute_mailForwardCopyToSelf="yes" \
  directory/manager/user_group/uniqueness="true" \
  directory/manager/web/language="de_DE.UTF-8" \
  directory/manager/web/modules/autosearch="1" \
  directory/manager/web/modules/computers/computer/add/default="computers/windows" \
  directory/manager/web/modules/groups/group/caching/uniqueMember/timeout="300" \
  directory/manager/web/modules/groups/group/checks/circular_dependency="yes" \
  directory/manager/web/modules/search/advanced_on_open="false" \
  directory/manager/web/modules/users/user/properties/homePostalAddress/syntax="postalAddress" \
  directory/manager/web/modules/wizards/disabled="no" \
  directory/manager/web/sizelimit="2000" \
  directory/reports/cleanup/age="43200" \
  directory/reports/cleanup/cron="0 0 * * *" \
  directory/reports/logo="/usr/share/univention-directory-reports/univention_logo.png" \
  directory/reports/templates/csv/computer1="computers/computer \"CSV Report\" /etc/univention/directory/reports/default computers.csv" \
  directory/reports/templates/csv/group1="groups/group \"CSV Report\" /etc/univention/directory/reports/default groups.csv" \
  directory/reports/templates/csv/user1="users/user \"CSV Report\" /etc/univention/directory/reports/default users.csv" \
  directory/reports/templates/pdf/computer1="computers/computer \"PDF Document\" /etc/univention/directory/reports/default computers.rml" \
  directory/reports/templates/pdf/group1="groups/group \"PDF Document\" /etc/univention/directory/reports/default groups.rml" \
  directory/reports/templates/pdf/user1="users/user \"PDF Document\" /etc/univention/directory/reports/default users.rml" \
  groups/default/domainadmins="Domain Admins" \
  groups/default/printoperators="Printer-Admins" \
  license/base="dc=example,dc=org" \
  locale/default="de_DE.UTF-8:UTF-8" \
  locale="de_DE.UTF-8:UTF-8 en_US.UTF-8:UTF-8" \
  password/hashing/method="SHA-512" \
  uldap/start-tls="${UDM_STARTTLS}" \
  update/available="false" \
  update/reboot/required="false" \
  uuid/license="00000000-0000-0000-0000-000000000000" \
  uuid/system="00000000-0000-0000-0000-000000000000" \
  version/erratalevel="0" \
  version/patchlevel="3" \
  version/version="5.0"

ucr unset ldap/server/ip

exec "$@"

# [EOF]
