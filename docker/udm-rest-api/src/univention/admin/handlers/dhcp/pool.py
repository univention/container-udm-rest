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

"""|UDM| module for the |DHCP| pool"""

import copy
import ipaddress

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.uexceptions
from univention.admin.layout import Group, Tab

from .__common import DHCPBase, add_dhcp_options, rangeMap, rangeUnmap


translation = univention.admin.localization.translation('univention.admin.handlers.dhcp')
_ = translation.translate

module = 'dhcp/pool'
operations = ['add', 'edit', 'remove', 'search']
superordinate = ['dhcp/subnet', 'dhcp/sharedsubnet']
childs = False
short_description = _('DHCP: Pool')
object_name = _('DHCP pool')
object_name_plural = _('DHCP pools')
long_description = _('A pool of dynamic addresses assignable to hosts.')
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionDhcpPool'],
    ),
}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description=_('A unique name for this DHCP pool object.'),
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'range': univention.admin.property(
        short_description=_('IP range for dynamic assignment'),
        long_description=_('Define a pool of addresses available for dynamic address assignment.'),
        syntax=univention.admin.syntax.IPv4_AddressRange,
        multivalue=True,
        required=True,
    ),
    'failover_peer': univention.admin.property(
        short_description=_('Failover peer configuration'),
        long_description=_('The name of the "failover peer" configuration to use.'),
        syntax=univention.admin.syntax.string,
    ),
    'known_clients': univention.admin.property(
        short_description=_('Allow known clients'),
        long_description=_('Addresses from this pool are given to clients which have a DHCP host entry matching their MAC address, but with no IP address assigned.'),
        syntax=univention.admin.syntax.AllowDeny,
    ),
    'unknown_clients': univention.admin.property(
        short_description=_('Allow unknown clients'),
        long_description=_('Addresses from this pool are given to clients, which do not have a DHCP host entry matching their MAC address.'),
        syntax=univention.admin.syntax.AllowDeny,
    ),
    'dynamic_bootp_clients': univention.admin.property(
        short_description=_('Allow dynamic BOOTP clients'),
        long_description=_('Addresses from this pool are given to clients using the old BOOTP protocol, which has no mechanism to free addresses again.'),
        syntax=univention.admin.syntax.AllowDeny,
    ),
    'all_clients': univention.admin.property(
        short_description=_('All clients'),
        long_description=_('Globally enable or disable this pool.'),
        syntax=univention.admin.syntax.AllowDeny,
    ),
}

layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('General DHCP pool settings'), layout=[
            'name',
            'range',
        ]),
    ]),
    Tab(_('Advanced'), _('Advanced DHCP pool options'), advanced=True, layout=[
        'failover_peer',
        ['known_clients', 'unknown_clients'],
        ['dynamic_bootp_clients', 'all_clients'],
    ]),
]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('range', 'dhcpRange', rangeMap, rangeUnmap)
mapping.register('failover_peer', 'univentionDhcpFailoverPeer', None, univention.admin.mapping.ListToString, encoding='ASCII')

add_dhcp_options(__name__)


class object(DHCPBase):
    module = module

    permits_udm2dhcp = {
        'known_clients': 'known clients',
        'unknown_clients': 'unknown clients',
        'dynamic_bootp_clients': 'dynamic bootp clients',
        'all_clients': 'all clients',
    }
    permits_dhcp2udm = {value: key for (key, value) in permits_udm2dhcp.items()}

    def open(self):
        univention.admin.handlers.simpleLdap.open(self)

        for i in [x.decode('UTF-8') for x in self.oldattr.get('dhcpPermitList', [])]:
            permit, name = i.split(u' ', 1)
            if name in self.permits_dhcp2udm:
                prop = self.permits_dhcp2udm[name]
                self[prop] = permit

        self.save()

    def ready(self):
        super(object, self).ready()
        # Use ipaddress.IPv4Interface().network to be liberal with subnet notation
        subnet = ipaddress.IPv4Interface(u'%(subnet)s/%(subnetmask)s' % self.superordinate.info).network
        for addresses in self.info['range']:
            for addr in addresses:
                if ipaddress.IPv4Address(u'%s' % (addr,)) not in subnet:
                    raise univention.admin.uexceptions.rangeNotInNetwork(addr)

    def _ldap_modlist(self):
        ml = univention.admin.handlers.simpleLdap._ldap_modlist(self)
        if self.hasChanged(self.permits_udm2dhcp.keys()):
            old = self.oldattr.get('dhcpPermitList', [])
            new = copy.deepcopy(old)

            for prop, value in self.permits_udm2dhcp.items():
                try:
                    permit = self.oldinfo[prop]
                    new.remove(u' '.join((permit, value)).encode('UTF-8'))
                except LookupError:
                    pass
                try:
                    permit = self.info[prop]
                    new.append(u' '.join((permit, value)).encode('UTF-8'))
                except LookupError:
                    pass

            ml.append(('dhcpPermitList', old, new))
        if self.info.get('failover_peer', None) and not self.info.get('dynamic_bootp_clients', None) == 'deny':
            raise univention.admin.uexceptions.bootpXORFailover
        return ml

    @classmethod
    def rewrite_filter(cls, filter, mapping):
        if filter.variable in cls.permits_udm2dhcp:
            filter.value = '%s %s' % (filter.value.strip('*'), cls.permits_udm2dhcp[filter.variable])
            filter.variable = 'dhcpPermitList'
        else:
            super(object, cls).rewrite_filter(filter, mapping)


lookup_filter = object.lookup_filter
lookup = object.lookup
identify = object.identify
