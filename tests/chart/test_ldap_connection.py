# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import re

from univention.testing.helm.client.ldap import (ConnectionUri,
                                                 ConnectionUriViaConfigMap)


class TestUdmRestApiUsesLdapConnectionLdap(ConnectionUriViaConfigMap, ConnectionUri):
    """
    Verify the regular ldap client configuration in `/etc/ldap/ldap.conf`
    """
    config_map_name = "release-name-udm-rest-api-ldap-conf"

    path_ldap_conf = "data['ldap.conf']"

    def get_ldap_uri(self, result):
        """
        Special discovery required because the value is inside a generated
        configuration file.
        """
        config_map = result.get_resource(kind="ConfigMap", name=self.config_map_name)
        ldap_conf = config_map.findone(self.path_ldap_conf)
        re_match = re.search(r'^URI\s+(?P<ldap_uri>.*?)$', ldap_conf, flags=re.MULTILINE)
        return re_match.group('ldap_uri')


class TestJobUpdateUniventionObjectIdentifierWaitsForLdapConnection(ConnectionUri):
    """
    Verify the LDAP connection of the init container `wait-for-ldap`.

    This is the only place in this Job where the LDAP URI is configured
    explicitly. The main container runs the UCS migration script, which
    discovers the LDAP server through the mounted UCR configuration. See
    `tests/chart/test_job_update_univention_object_identifier.py`.

    Note that the init container waits for the *primary* LDAP server, because
    the migration script has to write. Outside of a Nubus deployment there is
    only one configurable URI, so both are identical here.
    """

    workload_kind = "Job"
    workload_name = "release-name-udm-rest-api-1-update-univention-object-identifier"
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-ldap']"
