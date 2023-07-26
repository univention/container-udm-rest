from unittest import mock
import importlib.util
import os
import os.path

import pytest


@pytest.fixture
def process_join_data():
    """Provide "process-join-data.py" as a module."""
    module_name = "process_join_data"
    module_path = "./bin/process-join-data.py"
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(module_path),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def app(process_join_data):
    mock_udm = mock.Mock()
    return process_join_data.App(mock_udm)


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("my-join-data.yaml", False),
        ("my-join-data.yaml.j2", True),
    ],
)
def test_is_template(filename, expected, process_join_data):
    result = process_join_data.is_template(filename)
    assert result == expected


def test_ensure_list_contains_adds_property(app):
    mock_obj = app.udm.obj_by_dn()
    mock_obj.properties = {
        "users": [],
    }

    properties = {
        "users": [
            "uid=Administrator,cn=users,dc=base",
        ],
    }
    policies = {}

    app.ensure_list_contains(
        "groups/group",
        "cn=Domain Users,dc=base",
        properties,
        policies,
    )
    assert "uid=Administrator,cn=users,dc=base" in mock_obj.properties["users"]
    mock_obj.save.assert_called()


def test_ensure_list_contains_skips_existing_property(app):
    mock_obj = app.udm.obj_by_dn()
    mock_obj.properties = {
        "users": [
            "uid=Administrator,cn=users,dc=base",
        ],
    }

    properties = {
        "users": [
            "uid=Administrator,cn=users,dc=base",
        ],
    }
    policies = {}

    app.ensure_list_contains(
        "groups/group",
        "cn=Domain Users,dc=base",
        properties,
        policies,
    )
    assert len(mock_obj.properties["users"]) == 1
    mock_obj.save.assert_not_called()


def test_ensure_list_contains_adds_policy(app):
    mock_obj = app.udm.obj_by_dn()
    mock_obj.policies = {
        "policies/umc": [],
    }

    properties = {}
    policies = {
        "policies/umc": [
            "cn=default-umc-users,cn=UMC,cn=policies,dc=base",
        ],
    }

    app.ensure_list_contains(
        "groups/group",
        "cn=Domain Users,dc=base",
        properties,
        policies,
    )
    assert (
        "cn=default-umc-users,cn=UMC,cn=policies,dc=base"
        in mock_obj.policies["policies/umc"]
    )
    mock_obj.save.assert_called()


def test_ensure_list_contains_skips_existing_policy(app):
    mock_obj = app.udm.obj_by_dn()
    mock_obj.policies = {
        "policies/umc": [
            "cn=default-umc-users,cn=UMC,cn=policies,dc=base",
        ],
    }

    properties = {}
    policies = {
        "policies/umc": [
            "cn=default-umc-users,cn=UMC,cn=policies,dc=base",
        ],
    }

    app.ensure_list_contains(
        "groups/group",
        "cn=Domain Users,dc=base",
        properties,
        policies,
    )
    assert len(mock_obj.policies["policies/umc"]) == 1
    mock_obj.save.assert_not_called()
