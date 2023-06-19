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
# Link certificates in place
CA_CERT_FILE=${CA_CERT_FILE:-/run/secrets/ca_cert}

if [[ ! -f "${CA_CERT_FILE}" ]]; then
  echo "SSL CA Certificate is missing at ${CA_CERT_FILE}"
  exit 1
fi

CA_DIR="/etc/univention/ssl/ucsCA"

mkdir --parents "${CA_DIR}"
ln --symbolic --force "${CA_CERT_FILE}" "${CA_DIR}/CAcert.pem"


############################################################
# Store LDAP configuration
cat <<EOF > /etc/ldap/ldap.conf
# This file should be world readable but not world writable.

TLS_CACERT /etc/univention/ssl/ucsCA/CAcert.pem
TLS_REQCERT ${TLS_REQCERT:-demand}

URI ldap://${LDAP_HOST}:${LDAP_PORT}

BASE ${LDAP_BASE_DN}
EOF
chmod 0644 /etc/ldap/ldap.conf

LDAP_SECRET_FILE=${LDAP_SECRET_FILE:-/run/secrets/ldap_secret}
MACHINE_SECRET_FILE=${MACHINE_SECRET_FILE:-/run/secrets/machine_secret}
ln --symbolic --force "${LDAP_SECRET_FILE}" /etc/ldap.secret
ln --symbolic --force "${MACHINE_SECRET_FILE}" /etc/machine.secret

############################################################
# Fill UCR
AUTHORIZED_DC_BACKUP=${AUTHORIZED_DC_BACKUP:-cn=DC Backup Hosts,cn=groups,dc=example,dc=org}
AUTHORIZED_DC_SLAVES=${AUTHORIZED_DC_SLAVES:-cn=DC Slave Hosts,cn=groups,dc=example,dc=org}
AUTHORIZED_DOMAIN_ADMINS=${AUTHORIZED_DOMAIN_ADMINS:-cn=Domain Admins,cn=groups,dc=example,dc=org}

# FIXME: makeshift UCR replacement until DCD comes along
ucr-set() {
  # parameters: 1 - key, 2 - value
  key="$1"
  value="$2"
  base_conf=/etc/univention/base.conf

  # delete existing value
  sed --in-place --expression="\#^${key}:#d" ${base_conf}
  # add newline if necessary
  [[ -n "$(tail --bytes=1 ${base_conf})" ]] && \
    echo "" >> ${base_conf}
  # set new value
  echo -n "${key}: ${value}" >> ${base_conf}
}

ucr-set "ldap/master" "${LDAP_HOST}"
ucr-set "ldap/master/port" "${LDAP_PORT}"
ucr-set "ldap/server/name" "${LDAP_HOST}"
ucr-set "ldap/server/port" "${LDAP_PORT}"
ucr-set "ldap/hostdn" "${LDAP_HOST_DN}"
ucr-set "ldap/base" "${LDAP_BASE_DN}"
ucr-set "domainname" "${DOMAINNAME}"
ucr-set "hostname" "${HOSTNAME}"
ucr-set "directory/manager/rest/authorized-groups/dc-backup" "${AUTHORIZED_DC_BACKUP}"
ucr-set "directory/manager/rest/authorized-groups/dc-slaves" "${AUTHORIZED_DC_SLAVES}"
ucr-set "directory/manager/rest/authorized-groups/domain-admins" "${AUTHORIZED_DOMAIN_ADMINS}"
ucr-set "directory/manager/rest/debug_level" "${DEBUG_LEVEL}"
ucr-set "directory/manager/templates/alphanum/whitelist" ""
ucr-set "directory/manager/user/activate_ldap_attribute_mailForwardCopyToSelf" "yes"
ucr-set "directory/manager/user_group/uniqueness" "true"
ucr-set "directory/manager/web/language" "de_DE.UTF-8"
ucr-set "directory/manager/web/modules/autosearch" "1"
ucr-set "directory/manager/web/modules/computers/computer/add/default" "computers/windows"
ucr-set "directory/manager/web/modules/groups/group/caching/uniqueMember/timeout" "300"
ucr-set "directory/manager/web/modules/groups/group/checks/circular_dependency" "yes"
ucr-set "directory/manager/web/modules/search/advanced_on_open" "false"
ucr-set "directory/manager/web/modules/users/user/properties/homePostalAddress/syntax" "postalAddress"
ucr-set "directory/manager/web/modules/wizards/disabled" "no"
ucr-set "directory/manager/web/sizelimit" "2000"
ucr-set "directory/reports/cleanup/age" "43200"
ucr-set "directory/reports/cleanup/cron" "0 0 * * *"
ucr-set "directory/reports/logo" "/usr/share/univention-directory-reports/univention_logo.png"
ucr-set "directory/reports/templates/csv/computer1" "computers/computer \"CSV Report\" /etc/univention/directory/reports/default computers.csv"
ucr-set "directory/reports/templates/csv/group1" "groups/group \"CSV Report\" /etc/univention/directory/reports/default groups.csv"
ucr-set "directory/reports/templates/csv/user1" "users/user \"CSV Report\" /etc/univention/directory/reports/default users.csv"
ucr-set "directory/reports/templates/pdf/computer1" "computers/computer \"PDF Document\" /etc/univention/directory/reports/default computers.rml"
ucr-set "directory/reports/templates/pdf/group1" "groups/group \"PDF Document\" /etc/univention/directory/reports/default groups.rml"
ucr-set "directory/reports/templates/pdf/user1" "users/user \"PDF Document\" /etc/univention/directory/reports/default users.rml"
ucr-set "groups/default/domainadmins" "Domain Admins"
ucr-set "groups/default/printoperators" "Printer-Admins"
ucr-set "license/base" "dc=example,dc=org"
ucr-set "locale/default" "de_DE.UTF-8:UTF-8"
ucr-set "locale" "de_DE.UTF-8:UTF-8 en_US.UTF-8:UTF-8"
ucr-set "password/hashing/method" "SHA-512"
ucr-set "update/available" "false"
ucr-set "update/reboot/required" "false"
ucr-set "uuid/license" "00000000-0000-0000-0000-000000000000"
ucr-set "uuid/system" "00000000-0000-0000-0000-000000000000"
ucr-set "version/erratalevel" "0"
ucr-set "version/patchlevel" "3"
ucr-set "version/version" "5.0"

exec python3 -m univention.admin.rest.server "$@"

# [EOF]
