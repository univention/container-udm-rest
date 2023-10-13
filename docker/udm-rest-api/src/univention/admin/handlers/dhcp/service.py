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

"""|UDM| module for |DHCP| services"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
from univention.admin.layout import Group, Tab

from .__common import DHCPBase, add_dhcp_options


translation = univention.admin.localization.translation('univention.admin.handlers.dhcp')
_ = translation.translate

module = 'dhcp/service'
operations = ['add', 'edit', 'remove', 'search']
childs = True
childmodules = ('dhcp/host', 'dhcp/server', 'dhcp/shared', 'dhcp/subnet')
short_description = _('DHCP: Service')
object_name = _('DHCP service')
object_name_plural = _('DHCP services')
long_description = _('The top-level container for a DHCP configuration.')
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionDhcpService'],
    ),
}
property_descriptions = {
    'service': univention.admin.property(
        short_description=_('Service name'),
        long_description=_('A unique name for this DHCP service.'),
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
}

layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('DHCP service description'), layout=[
            'service',
        ]),
    ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('service', 'cn', None, univention.admin.mapping.ListToString)

add_dhcp_options(__name__)


class object(DHCPBase):
    module = module

    def __init__(self, co, lo, position, dn='', superordinate=None, attributes=[]):
        univention.admin.handlers.simpleLdap.__init__(self, co, lo, position, dn, superordinate, attributes=attributes)
        if not self.dn and not self.position:
            raise univention.admin.uexceptions.insufficientInformation(_('Neither DN nor position given.'))

    @staticmethod
    def unmapped_lookup_filter():
        return univention.admin.filter.conjunction('&', [
            univention.admin.filter.conjunction('|', [
                univention.admin.filter.expression('objectClass', 'dhcpService'),
                univention.admin.filter.expression('objectClass', 'univentionDhcpService'),
            ]),
        ])


def identify(dn, attr):
    return b'dhcpService' in attr.get('objectClass', []) \
        or b'univentionDhcpService' in attr.get('objectClass', [])


lookup_filter = object.lookup_filter
lookup = object.lookup
