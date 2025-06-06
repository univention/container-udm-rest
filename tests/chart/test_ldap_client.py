# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.testing.helm.client.ldap import Ldap, LdapUsageViaEnv, LdapConnectionUri


class TestLdapClientUdmRestApiDeployment(Ldap):

    config_map_name = "release-name-udm-rest-api"
    secret_name = "release-name-udm-rest-api-ldap"

    path_main_container = "spec.template.spec.containers[?@.name=='udm-rest-api']"

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


class TestLdapAuthJob(LdapConnectionUri, LdapUsageViaEnv, Ldap):

    config_map_name = "release-name-udm-rest-api"
    secret_name = "release-name-udm-rest-api-ldap"
    workload_resource_kind = "Job"

    path_ldap_bind_dn = "data.LDAP_ADMIN_USER"
