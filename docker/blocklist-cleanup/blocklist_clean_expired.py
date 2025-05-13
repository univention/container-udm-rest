#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging
import os
from datetime import UTC, datetime

from univention.admin.rest.client import UDM, HTTPError, ConnectionError

log = logging.getLogger("app")


def search_and_delete_expired_blocklist_entries(udm: UDM):
    mod = udm.get("blocklists/entry")
    if mod is None:
        log.error("UDM module 'blocklists/entry' not found")
        exit(1)

    now = datetime.now(UTC)
    for entry in mod.search():
        obj = entry.open()
        blocked_until: str | None = obj.properties.get("blockedUntil")
        if blocked_until is None:
            log.error('blocklist entry %s does not have "blockedUntil" property', obj.dn)
            continue

        log.debug('processing blocklist entry %s blocked until %s', obj.dn,
                  blocked_until)

        if is_expired(blocked_until, now):
            log.info("deleting expired entry: %s", obj.dn)
            obj.delete()


def is_expired(blocked_until: str, current_time: datetime):
    expired_time = datetime.strptime(blocked_until, "%Y%m%d%H%M%S%z")
    log.debug('Entry expires at %s, current time %s', expired_time,
              current_time)
    return current_time > expired_time


_sentinel = object()


def _get_env_var(key: str, default=_sentinel) -> str:
    value = os.environ.get(key, default)
    if value is _sentinel:
        log.error("missing %s environment variable", key)
        exit(1)

    return value


def _connect_to_udm():
    udm_api_url = _get_env_var("UDM_API_URL")
    log.info("Connecting to UDM API at URL %s", udm_api_url)
    udm_api_user = _get_env_var("UDM_API_USER")
    udm_api_password_file = _get_env_var("UDM_API_PASSWORD_FILE")

    with open(udm_api_password_file, "r") as password_file:
        udm_api_password = password_file.read()

    try:
        udm = UDM.http(udm_api_url, udm_api_user, udm_api_password)
        _ = udm.get_ldap_base()
        return udm
    except (HTTPError, ConnectionError) as e:
        log.error("Failed to create a UDM REST-API with URL %s Client: %s",
                  udm_api_url, e)
        exit(1)


def main():
    log_level = _get_env_var("LOG_LEVEL", "WARNING").upper()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=log_level)
    udm = _connect_to_udm()
    search_and_delete_expired_blocklist_entries(udm)


if __name__ == "__main__":
    main()
