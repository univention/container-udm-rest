#!/bin/bash
set -euxo pipefail

############################################################
# Configure Univention Directory Reports
ucr commit /etc/univention/directory/reports/config.ini
