#!/bin/bash

# TODO: Apply all files in /join-data in a sorted way
process-join-data.py /join-data/00-umc-init.yaml.j2
process-join-data.py /join-data/10-univention-ldap-server.yaml.j2
process-join-data.py /join-data/univention-portal.yaml.j2
process-join-data.py /join-data/misc-saml.yaml.j2
process-join-data.py /join-data/35-univention-management-console-module-udm.yaml.j2
