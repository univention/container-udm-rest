# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging
import os
from pprint import pformat
from typing import NamedTuple

import ldap

logger = logging.getLogger(__name__)


class Config(NamedTuple):
    ldap_uri: str
    ldap_base_dn: str
    ldap_admin_user: str
    ldap_admin_password: str
    log_level: str


def get_config() -> Config:
    ldap_uri = os.environ.get("LDAP_URI")
    if not ldap_uri:
        raise ValueError("Missing environment variable: LDAP_URI")
    ldap_admin_user = os.environ.get("LDAP_ADMIN_USER")
    if not ldap_admin_user:
        raise ValueError("Missing environment variable: LDAP_ADMIN_USER")
    ldap_admin_password = os.environ.get("LDAP_ADMIN_PASSWORD")
    if not ldap_admin_password:
        raise ValueError("Missing environment variable: LDAP_ADMIN_PASSWORD")
    ldap_base_dn = os.environ.get("LDAP_BASE_DN")
    if not ldap_base_dn:
        raise ValueError("Missing environment variable: LDAP_BASE_DN")
    log_level = os.environ.get("PYTHON_LOG_LEVEL")
    if not log_level:
        raise ValueError("Missing environment variable: PYTHON_LOG_LEVEL")

    return Config(
        log_level=log_level,
        ldap_base_dn=ldap_base_dn,
        ldap_uri=ldap_uri,
        ldap_admin_user=ldap_admin_user,
        ldap_admin_password=ldap_admin_password,
    )


def setup_logging(level: str | int):
    log_format = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=log_format, level=level)
    global logger
    logger = logging.getLogger(__name__)


def ldap_connect(ldap_uri: str, ldap_admin_user: str, ldap_admin_password: str, ldap_base_dn: str):
    logger.debug("Try connect to %s (%s) with %s", ldap_uri, ldap_base_dn, ldap_admin_user)

    ldap_connection = ldap.initialize(ldap_uri)
    ldap_connection.simple_bind_s(ldap_admin_user, ldap_admin_password)

    logger.debug("Connected to %s (%s) with %s", ldap_uri, ldap_base_dn, ldap_admin_user)

    return ldap_connection


def update_univention_object_identifier(ldap_connection: ldap.ldapobject, ldap_base_dn: str):
    result = ldap_connection.search_s(
        f"{ldap_base_dn}",
        ldap.SCOPE_SUBTREE,
        "(&(objectClass=univentionObject)(!(univentionObjectIdentifier=*)))",
        ["univentionObjectIdentifier", "entryUUID"],
    )

    updated_count = 0
    failed_count = 0
    for entry in result:
        logger.debug("Processing %s", entry[0])
        logger.debug("Values:\n%s", pformat(entry[1], indent=4))

        if entry[1].get("univentionObjectIdentifier") or not entry[1].get("entryUUID"):
            logger.warning(
                "Wrong ldap search condition! univentionObjectIdentifier: %s entryUUID: %s",
                entry[1].get("univentionObjectIdentifier"),
                entry[1].get("entryUUID"),
            )
            continue

        try:
            ldap_connection.modify_s(
                entry[0],
                [
                    (
                        ldap.MOD_REPLACE,
                        "univentionObjectIdentifier",
                        entry[1].get("entryUUID"),
                    )
                ],
            )
        except Exception as e:
            logger.error(e)
            failed_count += 1
            continue

        updated_count += 1

    logger.info("Updated %s records. Failed to update %s records.", updated_count, failed_count)


def main(config: Config):
    setup_logging(config.log_level)

    logger.info("Updating univentionObjectIdentifier with entryUUID values.")
    logger.debug("Loaded config:\n%s", pformat(dict(config._asdict()), indent=4))

    try:
        ldap_connection = ldap_connect(
            ldap_uri=config.ldap_uri,
            ldap_admin_user=config.ldap_admin_user,
            ldap_admin_password=config.ldap_admin_password,
            ldap_base_dn=config.ldap_base_dn,
        )
    except ldap.SERVER_DOWN:
        logger.error("LDAP server down")
        exit(1)
    except ldap.INVALID_CREDENTIALS:
        logger.error("Invalid LDAP credentials")
        exit(1)

    update_univention_object_identifier(ldap_connection=ldap_connection, ldap_base_dn=config.ldap_base_dn)


# ###########################################################################
# # Main
# ###########################################################################

if __name__ == "__main__":
    main(get_config())
