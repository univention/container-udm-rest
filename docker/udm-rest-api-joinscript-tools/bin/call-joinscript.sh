#!/bin/bash

set -x

export ldap_base="dc=univention-organization,dc=intranet"

die()
{
    true
}
export -f die

ucs_registerLDAPExtension() {
    true
}
export -f ucs_registerLDAPExtension

exec "$@"
