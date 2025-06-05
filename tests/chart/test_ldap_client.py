# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.testing.helm.client.ldap import Ldap


class TestLdapClient(Ldap):

    config_map_name = "release-name-udm-rest-api"
    secret_name = "release-name-udm-rest-api-ldap"

    path_main_container = "spec.template.spec.containers[?@.name=='udm-rest-api']"

    path_ldap_bind_dn = "data.LDAP_ADMIN_USER"

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_host_is_required():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_host_is_templated():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_host_supports_global_default():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_host_local_overrides_global():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_port_has_default():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_port_is_templated():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_port_supports_global_default():
        pass

    @pytest.mark.skip(reason="TODO: connection.host vs connection.uri")
    def test_connection_port_local_overrides_global():
        pass
