#!/bin/bash
set -euxo pipefail

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

