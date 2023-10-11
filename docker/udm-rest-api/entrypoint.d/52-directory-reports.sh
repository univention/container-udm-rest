#!/bin/bash
set -euxo pipefail

############################################################
# Configure Univention Directory Reports
# (In UCS this is done by `ucr commit`.)

# TODO: At this point, UCR contains these values.
#       Can we generate the file with ucr commit??
#       Yeah, sort of, but the bottom half of the file is missing atm...!?!?

cat <<EOF > /etc/univention/directory/reports/config.ini
[DEFAULT]
# default report name
report=PDF Document

[reports]
csv/computer1=computers/computer "CSV Report" /etc/univention/directory/reports/default computers.csv
csv/group1=groups/group "CSV Report" /etc/univention/directory/reports/default groups.csv
csv/user1=users/user "CSV Report" /etc/univention/directory/reports/default users.csv
pdf/computer1=computers/computer "PDF Document" /etc/univention/directory/reports/default computers.rml
pdf/group1=groups/group "PDF Document" /etc/univention/directory/reports/default groups.rml
pdf/user1=users/user "PDF Document" /etc/univention/directory/reports/default users.rml
EOF
