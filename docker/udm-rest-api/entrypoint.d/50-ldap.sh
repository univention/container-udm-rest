#!/bin/bash
set -euxo pipefail
#
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2021-2025 Univention GmbH

############################################################
# Prepare LDAP TLS certificates and settings
UDM_STARTTLS="$(ucr get uldap/start-tls)"
if [[ -z "${UDM_STARTTLS}" ]]; then
  UDM_STARTTLS=2
fi

case "${UDM_STARTTLS}" in
  "2")
    TLS_MODE="secure"
    TLS_REQCERT="demand"
    ;;
  "1")
    TLS_MODE="unvalidated"
    TLS_REQCERT="allow"
    ;;
  "0")
    TLS_MODE="off"
    TLS_REQCERT="never"
    ;;
  *)
    echo "UCR variable 'uldap/start-tls' must be one of: 0, 1, 2"
    exit 1
esac

# TODO: Install the certificates of the LDAP server from Kubernetes secrets.
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
LDAP_HOST="$(ucr get ldap/server/name)"
LDAP_PORT="$(ucr get ldap/server/port)"
LDAP_BASE_DN="$(ucr get ldap/base)"
mkdir -pv /etc/ldap
[[ -w /etc/ldap/ldap.conf ]] && cat <<EOF > /etc/ldap/ldap.conf
# This file should be world readable but not world writable.

${CA_DIR:+TLS_CACERT /etc/univention/ssl/ucsCA/CAcert.pem}
TLS_REQCERT ${TLS_REQCERT:-demand}

URI ldap://${LDAP_HOST}:${LDAP_PORT}

BASE ${LDAP_BASE_DN}
EOF
[[ -w /etc/ldap/ldap.conf ]] && chmod 0644 /etc/ldap/ldap.conf

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
