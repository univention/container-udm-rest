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

from univention.testing.helm.client.ldap import AuthPassword, SecretViaVolume


not_supported = pytest.mark.skip(
    reason="The CronJob does not allow to configure the UDM Rest API user")


class TestUdmAuth(SecretViaVolume, AuthPassword):
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

    path_username = "data.UDM_API_USER"

    def test_username_is_fixed(self, chart):
        result = chart.helm_template()
        config_map = result.get_resource(kind="ConfigMap", name=self.config_map_name)
        username = config_map.findone(self.path_username)
        assert username == "cn=admin"
