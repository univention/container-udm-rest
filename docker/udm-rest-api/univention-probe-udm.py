#!/usr/bin/python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH


import argparse
import base64
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description="Kubernetes probe for the UDM REST API")
    parser.add_argument(
        "check",
        choices=["alive", "ready"],
        help="'alive' succeeds on any HTTP response, 'ready' also fails on HTTP 503 (LDAP unreachable)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9979,
        help="port the UDM REST API listens on (default: %(default)s)",
    )
    args = parser.parse_args()
    with open(os.environ["UDM_API_PASSWORD_FILE"]) as fd:
        password = fd.read().strip()
    credentials = f'{os.environ["UDM_API_USER"]}:{password}'
    auth = base64.b64encode(credentials.encode("ISO8859-1")).decode()
    root_path = os.environ.get("UDM_REST_API_ROOT_PATH", "").rstrip("/")
    request = urllib.request.Request(
        f"http://127.0.0.1:{args.port}{root_path}/udm/",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/json"},
    )
    try:
        urllib.request.urlopen(request, timeout=3)
    except urllib.error.HTTPError as exc:
        if args.check == "ready" and exc.code == 503:
            return 1
        return 0
    except OSError as exc:
        print(f"probe failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
