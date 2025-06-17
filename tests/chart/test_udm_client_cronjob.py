# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

"""
Verify `CronJob` specific UDM Rest API client usage.

The `CronJob` is regularly cleaning up the blocklist entries and needs access
to the UDM Rest API for this purpose.

Currently it does not support a dedicated configuration of the UDM Rest API
client, e.g. username, password etc. cannot be configured separately. The tests
are only verifying the correct usage of the values.
"""

import pytest

from univention.testing.helm.client.ldap import Auth


not_supported = pytest.mark.skip(
    reason="The CronJob does not allow to configure the UDM Rest API user")


class TestUdmAuth(Auth):
    """
    The CronJob configuration for UDM is using the LDAP client.

    The test for the CronJob is special. the CronJob uses currently the values
    from the LDAP configuration and has some values like the user name
    hardcoded.

    The main intention of this test is to check the correct usage of the Secret
    within the CronJob.
    """

    config_map_name = "release-name-udm-rest-api"
    secret_name = "release-name-udm-rest-api-ldap"
    workload_kind = "CronJob"

    path_udm_username = "data.UDM_API_USER"

    @not_supported
    def test_auth_plain_values_provide_bind_dn():
        pass

    @not_supported
    def test_auth_plain_values_bind_dn_is_templated():
        pass

    @not_supported
    def test_auth_bind_dn_has_default():
        pass

    def test_username_is_fixed(self, chart):
        result = chart.helm_template()
        config_map = result.get_resource(kind="ConfigMap", name=self.config_map_name)
        username = config_map.findone(self.path_udm_username)
        assert username == "cn=admin"
