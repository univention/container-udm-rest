# -*- coding: utf-8 -*-
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2004-2023 Univention GmbH
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

"""|UDM| module for printer shares"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.handlers.shares.printer
import univention.admin.handlers.shares.printergroup
import univention.admin.localization


translation = univention.admin.localization.translation('univention.admin.handlers.shares')
_ = translation.translate

module = 'shares/print'
childmodules = ['shares/printer', 'shares/printergroup']
childs = False
short_description = _('Printer share')
object_name = _('Printer share')
object_name_plural = _('Printer shares')
long_description = ''
operations = ['search']
virtual = True
options = {}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description='',
        syntax=univention.admin.syntax.printerName,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'spoolHost': univention.admin.property(
        short_description=_('Print server'),
        long_description='',
        syntax=univention.admin.syntax.ServicePrint_FQDN,
        multivalue=True,
        required=True,
    ),
    'sambaName': univention.admin.property(
        short_description=_('Windows name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        unique=True,
    ),
}

mapping = univention.admin.mapping.mapping()


class object(univention.admin.handlers.simpleLdap):
    module = module


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=False, required=False, timeout=-1, sizelimit=0):
    res = []
    for module in (univention.admin.handlers.shares.printer, univention.admin.handlers.shares.printergroup):
        res.extend(module.lookup(co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit))
    return res


def identify(dn, attr, canonical=False):
    pass
