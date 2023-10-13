#!/usr/bin/python3
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2021-2023 Univention GmbH
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

import json
from multiprocessing import managers

from setproctitle import getproctitle, setproctitle


proctitle = getproctitle()


class _SharedMemory(managers.SyncManager):

    children = {}
    queue = {}
    search_sessions = {}
    authenticated = {}

    def start(self, *args, **kwargs):
        setproctitle(proctitle + '   # multiprocessing manager')
        try:
            super().start(*args, **kwargs)
        finally:
            setproctitle(proctitle)

        # we must create the parent dictionary instance before forking but after Python importing
        self.children = self.dict()
        self.queue = self.dict()
        self.search_sessions = self.dict()
        self.authenticated = self.dict()


shared_memory = _SharedMemory()


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, managers.DictProxy):
            return dict(o)
        if isinstance(o, managers.ListProxy):
            return list(o)
        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')
