#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging
import os
from datetime import datetime

from univention.admin.rest.client import UDM

log = logging.getLogger("app")


def search_and_delete_expired_blocklist_entries():
    with _connect_to_udm as udm:
        mod = udm.get("blocklists/entry")
        for entry in mod.search():
            obj = entry.open()
            if is_expired(obj.properties.get("blockedUntil")):
                now = datetime.now()
                log.info("%s - deleting expired entry: %s", now, obj.dn)
                obj.delete()


def is_expired(blockedUntil: str):
    expired_time = datetime.strptime(blockedUntil, "%Y%m%d%H%M%SZ")
    current_time = datetime.utcnow()
    return current_time > expired_time


def _connect_to_udm():
    udm_api_url = os.environ["UDM_API_URL"]
    log.info("Connecting to UDM API at URL %s", udm_api_url)
    udm_api_user = os.environ["UDM_API_USER"]
    with open(os.environ["UDM_API_PASSWORD_FILE"], "r") as password_file:
        udm_api_password = password_file.read()
    udm = UDM.http(udm_api_url, udm_api_user, udm_api_password)
    return udm


def main():
    search_and_delete_expired_blocklist_entries()
