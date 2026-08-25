# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025-2026 Univention GmbH

"""
Unit tests for the Job which updates the `univentionObjectIdentifier`.

The Job runs the UCS migration script
`univention-update-univention-object-identifier` out of the UDM Rest API image.
It is configured like the license cache CronJob: the LDAP connection is taken
from the UCR configuration and the credentials are provided as
`/etc/ldap.secret`.
"""

import pytest
from pytest_helm.utils import load_yaml


class TestJobUpdateUniventionObjectIdentifier:

    template_file = "templates/job-update-univention-object-identifier.yaml"

    job_name = "release-name-udm-rest-api-1-update-univention-object-identifier"

    config_map_name = "release-name-udm-rest-api"

    ucr_volume_name = "config-map-ucr"

    migration_script = "/usr/share/univention-ldap/univention-update-univention-object-identifier"

    path_main_container = "spec.template.spec.containers[?@.name=='main']"

    def render_job(self, chart, values=None):
        result = chart.helm_template(values, self.template_file)
        return result.get_resource(kind="Job", name=self.job_name)

    def get_main_container(self, chart, values=None):
        job = self.render_job(chart, values)
        return job.findone(self.path_main_container)

    def test_job_is_created_by_default(self, chart):
        job = self.render_job(chart)
        assert job

    def test_job_can_be_disabled(self, chart):
        values = load_yaml(
            """
            ldapUpdateUniventionObjectIdentifier:
              enabled: false
            """)
        result = chart.helm_template(values)
        assert result.get_resources(kind="Job") == []

    def test_job_is_suspended_by_default(self, chart):
        job = self.render_job(chart)
        assert job.findone("spec.suspend") is True

    def test_job_suspend_can_be_configured(self, chart):
        values = load_yaml(
            """
            ldapUpdateUniventionObjectIdentifier:
              suspend: false
            """)
        job = self.render_job(chart, values)
        assert job.findone("spec.suspend") is False

    def test_main_container_runs_the_ucs_migration_script(self, chart):
        main_container = self.get_main_container(chart)
        assert main_container.findone("command") == [self.migration_script]

    def test_main_container_uses_the_udm_rest_api_image(self, chart):
        values = load_yaml(
            """
            udmRestApi:
              image:
                registry: "stub-registry"
                repository: "stub-repository"
                tag: "stub-tag"
                pullPolicy: "Never"
            """)
        main_container = self.get_main_container(chart, values)
        assert main_container.findone("image") == "stub-registry/stub-repository:stub-tag"
        assert main_container.findone("imagePullPolicy") == "Never"

    def test_main_container_does_not_use_a_dedicated_image(self, chart):
        """
        The dedicated image has been replaced by the script from the UDM Rest
        API image, the old image configuration must not have an effect anymore.
        """
        values = load_yaml(
            """
            ldapUpdateUniventionObjectIdentifier:
              image:
                registry: "stub-unused-registry"
                repository: "stub-unused-repository"
                tag: "stub-unused-tag"
            """)
        main_container = self.get_main_container(chart, values)
        assert "stub-unused" not in main_container.findone("image")

    def test_main_container_reads_the_configuration_from_the_config_map(self, chart):
        main_container = self.get_main_container(chart)
        config_map_ref = main_container.findone("envFrom[?@.configMapRef]")
        assert config_map_ref.findone("configMapRef.name") == self.config_map_name

    def test_main_container_mounts_the_ldap_secret(self, chart):
        main_container = self.get_main_container(chart)
        volume_mount = main_container.findone("volumeMounts[?@.name=='secret-ldap']")
        assert volume_mount.findone("mountPath") == "/etc/ldap.secret"

    @pytest.mark.parametrize("file_name", ["base.conf", "base-defaults.conf"])
    def test_main_container_mounts_the_ucr_configuration(self, chart, file_name):
        main_container = self.get_main_container(chart)
        volume_mount = main_container.findone(f"volumeMounts[?@.subPath=='{file_name}']")
        assert volume_mount.findone("name") == self.ucr_volume_name
        assert volume_mount.findone("mountPath") == f"/etc/univention/{file_name}"

    def test_ucr_config_map_supports_global_default(self, chart):
        values = load_yaml(
            """
            global:
              configMapUcr: "stub-global-ucr"
            configMapUcr: null
            """)
        job = self.render_job(chart, values)
        volume = job.findone(f"spec.template.spec.volumes[?@.name=='{self.ucr_volume_name}']")
        assert volume.findone("configMap.name") == "stub-global-ucr"

    def test_ucr_config_map_is_templated(self, chart):
        values = load_yaml(
            """
            global:
              test: "stub-value"
            configMapUcr: "{{ .Values.global.test }}"
            """)
        job = self.render_job(chart, values)
        volume = job.findone(f"spec.template.spec.volumes[?@.name=='{self.ucr_volume_name}']")
        assert volume.findone("configMap.name") == "stub-value"

    def test_extra_env_vars_can_be_configured(self, chart):
        values = load_yaml(
            """
            ldapUpdateUniventionObjectIdentifier:
              extraEnvVars:
                - name: "STUB_NAME"
                  value: "stub-value"
            """)
        main_container = self.get_main_container(chart, values)
        env_var = main_container.findone("env[?@.name=='STUB_NAME']")
        assert env_var.findone("value") == "stub-value"

    def test_env_is_omitted_without_extra_env_vars(self, chart):
        main_container = self.get_main_container(chart)
        assert "env" not in main_container
