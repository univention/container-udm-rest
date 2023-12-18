# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

"""
Module providing command-line argument parser
and common fixtures for use in integration tests.
"""
import pytest
import requests


def pytest_addoption(parser: pytest.Parser):
    """
    Allow customizing global options of the tests,
    e.g. where to find the UDM REST container and how to connect.
    """
    parser.addoption(
        "--udm-rest-url",
        action="store",
        default="http://localhost:9979/udm/",
        help="UDM REST API base url to run tests against.",
    )
    parser.addoption(
        "--ldap-base-dn",
        action="store",
        default="dc=univention-organization,dc=intranet",
        help="Base DN of the LDAP directory.",
    )
    parser.addoption(
        "--username",
        action="store",
        default="cn=admin",
        help="Username to authenticate with the UDM REST API.",
    )
    parser.addoption(
        "--password",
        action="store",
        default="univention",
        help="Password to authenticate with the UDM REST API.",
    )


@pytest.fixture(scope="session")
def base_dn(pytestconfig):
    """Base DN of the LDAP server."""
    return pytestconfig.getoption("--ldap-base-dn")


@pytest.fixture(scope="session")
def udm_url(pytestconfig):
    """Base URL of the UDM REST API."""
    return pytestconfig.getoption("--udm-rest-url")


@pytest.fixture(scope="session")
def session(pytestconfig):
    """Prepare requests to UDM REST API."""
    session = requests.Session()
    session.auth = (
        pytestconfig.getoption("--username"),
        pytestconfig.getoption("--password"),
    )
    session.headers["accept"] = "application/json"
    yield session
