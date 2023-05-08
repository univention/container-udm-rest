#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2021 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.

"""Transform environment variables into a UCR file."""

import os

BASE_PATH = '/etc/univention/base.conf'


def main(base_path):
    """The main transformer function"""
    base_conf = {}
    with open(base_path, 'r', encoding='utf-8') as file_handler:
        for line in file_handler.readlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            if ':' not in line:
                print(f'base.conf contains line without colon: {line}')
                continue
            key, value = line.split(':', 1)
            base_conf[key] = value

    for key, value in os.environ.items():
        if key.replace('_', '').isupper():
            continue
        ldap_key = key.replace('0', '/').replace('_', '-')
        base_conf[ldap_key] = value

    with open(base_path, 'w', encoding='utf-8') as file_handler:
        for key, value in sorted(base_conf.items()):
            file_handler.write(f'{key}: {value}\n')


if __name__ == '__main__':
    main(BASE_PATH)

# [EOF]
