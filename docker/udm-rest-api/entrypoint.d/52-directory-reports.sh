#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023-2025 Univention GmbH

set -euxo pipefail

############################################################
# Configure Univention Directory Reports
ucr commit /etc/univention/directory/reports/config.ini
