# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Verify the LDAP client configuration for the UDM Rest API.

The UDM Rest API is currently using most of the information out of the UCR. The
related tests are decorated with `pytest.skip`.

The container also as the file `/etc/ldap/ldap.conf` to configure the regular
ldap clients.
"""

import re

import pytest

from univention.testing.helm.client.ldap import (
    Auth,
    ConnectionUri,
    ConnectionUriViaConfigMap,
)


class TestAuth(Auth):
    config_map_name = "release-name-udm-rest-api"
    secret_name = "release-name-udm-rest-api-ldap"

    path_ldap_bind_dn = "data.LDAP_ADMIN_USER"

    @pytest.mark.skip(reason="The UDM Rest API discovers the bind dn via UCR")
    def test_auth_bind_dn_is_required():
        pass

    @pytest.mark.skip(reason="The UDM Rest API discovers the bind dn via UCR")
    def test_auth_bind_dn_has_default():
        pass

    @pytest.mark.skip(reason="The UDM Rest API discovers the bind dn via UCR")
    def test_auth_plain_values_bind_dn_is_templated():
        pass

    @pytest.mark.skip(reason="The UDM Rest API discovers the bind dn via UCR")
    def test_auth_plain_values_provide_bind_dn():
        pass


class TestLdapConnectionLdapConf(ConnectionUriViaConfigMap, ConnectionUri):
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
