# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Verify `Job` specific LDAP client configuration.

The `Job` to update the `univentionObjectIdentifier` is receiving all
information via environment variables, including the password.
"""

from univention.testing.helm.client.ldap import (
    LdapAuth,
    LdapAuthUsageViaEnv,
    LdapConnectionUri,
)


class TestLdapAuth(LdapAuthUsageViaEnv, LdapAuth):
    config_map_name = "release-name-udm-rest-api"
    secret_name = "release-name-udm-rest-api-ldap"
    workload_kind = "Job"

    path_ldap_bind_dn = "data.LDAP_ADMIN_USER"


class TestLdapConnectionJob(LdapConnectionUri):

    workload_kind = "Job"
