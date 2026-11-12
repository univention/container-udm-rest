# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
Every workload's pods carry their own `app.kubernetes.io/name`,
so that a NetworkPolicy can select each of them alone.
"""

import pytest
from pytest_helm.utils import load_yaml


@pytest.mark.parametrize(
    "kind,name,path_pod_labels,expected",
    [
        (
            "Deployment",
            "release-name-udm-rest-api",
            "spec.template.metadata.labels",
            "udm-rest-api",
        ),
        (
            "CronJob",
            "release-name-udm-rest-api-blocklist-cleanup",
            "spec.jobTemplate.spec.template.metadata.labels",
            "release-name-udm-rest-api-blocklist-cleanup",
        ),
        (
            "CronJob",
            "release-name-udm-rest-api-license-cache",
            "spec.jobTemplate.spec.template.metadata.labels",
            "release-name-udm-rest-api-license-cache",
        ),
        (
            "CronJob",
            "release-name-udm-rest-api-telemetry-sender",
            "spec.jobTemplate.spec.template.metadata.labels",
            "release-name-udm-rest-api-telemetry-sender",
        ),
        (
            "Job",
            "release-name-udm-rest-api-1-update-univention-object-identifier",
            "spec.template.metadata.labels",
            "release-name-udm-rest-api-update-univention-object-identifier",
        ),
    ],
)
def test_pod_name_label_is_unique_and_stable(chart, kind, name, path_pod_labels, expected):
    values = load_yaml(
        """
        telemetrySender:
          enabled: true
        """)
    result = chart.helm_template(values)
    labels = result.get_resource(kind=kind, name=name).findone(path_pod_labels)
    assert labels["app.kubernetes.io/name"] == expected
