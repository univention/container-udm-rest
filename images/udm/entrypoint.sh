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

ln --symbolic --force "CAcert.pem" "/etc/univention/ssl/ucsCA/CAcert.pem"

cat <<EOF > /etc/ldap/ldap.conf
# This file should be world readable but not world writable.

TLS_CACERT /etc/univention/ssl/ucsCA/CAcert.pem

URI ${LDAP_URI}

BASE ${LDAP_BASE}
EOF
chmod 0755 /etc/ldap/ldap.conf

touch /etc/machine.secret /etc/ldap.secret
chmod 0700 /etc/machine.secret /etc/ldap.secret
echo -n "${LDAP_ADMIN_PASSWORD}" > /etc/ldap.secret
echo -n "${LDAP_MACHINE_PASSWORD}" > /etc/machine.secret

python3 ./env_to_ucr.py

exec python3 -m univention.admin.rest "$@"

# [EOF]
