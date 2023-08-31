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

"""|UDM| module for the IP clients"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.handlers.dns.forward_zone
import univention.admin.handlers.dns.reverse_zone
import univention.admin.handlers.networks.network
import univention.admin.localization
import univention.admin.mapping
import univention.admin.syntax
import univention.admin.uldap
from univention.admin import nagios
from univention.admin.certificate import PKIIntegration, pki_option, pki_properties, pki_tab, register_pki_mapping
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.computers')
_ = translation.translate

module = 'computers/ipmanagedclient'
operations = ['add', 'edit', 'remove', 'search', 'move']
docleanup = True
childs = False
short_description = _('Computer: IP client')
object_name = _('IP client')
object_name_plural = _('IP clients')
long_description = ''
options = {
    'pki': pki_option(),
}
property_descriptions = dict({
    'name': univention.admin.property(
        short_description=_('IP client name'),
        long_description='',
        syntax=univention.admin.syntax.hostName,
        include_in_default_search=True,
        required=True,
        identifies=True,
    ),
    'description': univention.admin.property(
        short_description=_('Description'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
    ),
    'mac': univention.admin.property(
        short_description=_('MAC address'),
        long_description='',
        syntax=univention.admin.syntax.MAC_Address,
        multivalue=True,
        include_in_default_search=True,
    ),
    'network': univention.admin.property(
        short_description=_('Network'),
        long_description='',
        syntax=univention.admin.syntax.network,
    ),
    'ip': univention.admin.property(
        short_description=_('IP address'),
        long_description='',
        syntax=univention.admin.syntax.ipAddress,
        multivalue=True,
        include_in_default_search=True,
    ),
    'dnsEntryZoneForward': univention.admin.property(
        short_description=_('Forward zone for DNS entry'),
        long_description='',
        syntax=univention.admin.syntax.dnsEntry,
        multivalue=True,
        dontsearch=True,
    ),
    'dnsEntryZoneReverse': univention.admin.property(
        short_description=_('Reverse zone for DNS entry'),
        long_description='',
        syntax=univention.admin.syntax.dnsEntryReverse,
        multivalue=True,
        dontsearch=True,
    ),
    'dnsEntryZoneAlias': univention.admin.property(
        short_description=_('Zone for DNS alias'),
        long_description='',
        syntax=univention.admin.syntax.dnsEntryAlias,
        multivalue=True,
        dontsearch=True,
    ),
    'dnsAlias': univention.admin.property(
        short_description=_('DNS alias'),
        long_description='',
        syntax=univention.admin.syntax.string,
        multivalue=True,
    ),
    'dhcpEntryZone': univention.admin.property(
        short_description=_('DHCP service'),
        long_description='',
        syntax=univention.admin.syntax.dhcpEntry,
        multivalue=True,
        dontsearch=True,
    ),
    'inventoryNumber': univention.admin.property(
        short_description=_('Inventory number'),
        long_description='',
        syntax=univention.admin.syntax.string,
        multivalue=True,
        include_in_default_search=True,
    ),
    'groups': univention.admin.property(
        short_description=_('Groups'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        multivalue=True,
        dontsearch=True,
    ),
    'domain': univention.admin.property(
        short_description=_('Domain'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
    ),
}, **pki_properties())

layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('Computer account'), layout=[
            ['name', 'description'],
            'inventoryNumber',
        ]),
        Group(_('Network settings '), layout=[
            'network',
            'mac',
            'ip',
        ]),
        Group(_('DNS Forward and Reverse Lookup Zone'), layout=[
            'dnsEntryZoneForward',
            'dnsEntryZoneReverse',
        ]),
        Group(_('DHCP'), layout=[
            'dhcpEntryZone',
        ]),
    ]),
    Tab(_('Groups'), _('Group memberships'), advanced=True, layout=[
        "groups",
    ]),
    Tab(_('DNS alias'), _('Alias DNS entry'), advanced=True, layout=[
        'dnsEntryZoneAlias',
    ]),
    pki_tab(),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
mapping.register('inventoryNumber', 'univentionInventoryNumber')
mapping.register('mac', 'macAddress', encoding='ASCII')
mapping.register('network', 'univentionNetworkLink', None, univention.admin.mapping.ListToString)
mapping.register('domain', 'associatedDomain', None, univention.admin.mapping.ListToString, encoding='ASCII')
register_pki_mapping(mapping)

# add Nagios extension
nagios.addPropertiesMappingOptionsAndLayout(property_descriptions, mapping, options, layout)


class object(univention.admin.handlers.simpleComputer, nagios.Support, PKIIntegration):
    module = module

    def __init__(self, co, lo, position, dn='', superordinate=None, attributes=[]):
        univention.admin.handlers.simpleComputer.__init__(self, co, lo, position, dn, superordinate, attributes)
        nagios.Support.__init__(self)

    def open(self):
        self.pki_open()
        univention.admin.handlers.simpleComputer.open(self)
        self.nagios_open()

        if not self.exists():
            return

        self.save()

    def _ldap_pre_create(self):
        super(object, self)._ldap_pre_create()
        self.nagios_ldap_pre_create()

    def _ldap_addlist(self):
        al = super(object, self)._ldap_addlist()
        return al + [('objectClass', [b'top', b'univentionHost', b'univentionClient', b'person'])]

    def _ldap_post_create(self):
        univention.admin.handlers.simpleComputer._ldap_post_create(self)
        self.nagios_ldap_post_create()

    def _ldap_post_remove(self):
        self.nagios_ldap_post_remove()
        univention.admin.handlers.simpleComputer._ldap_post_remove(self)

    def _ldap_post_modify(self):
        univention.admin.handlers.simpleComputer._ldap_post_modify(self)
        self.nagios_ldap_post_modify()

    def _ldap_pre_modify(self):
        univention.admin.handlers.simpleComputer._ldap_pre_modify(self)
        self.nagios_ldap_pre_modify()

    def _ldap_modlist(self):
        ml = univention.admin.handlers.simpleComputer._ldap_modlist(self)
        self.nagios_ldap_modlist(ml)
        return ml

    def cleanup(self):
        self.open()
        self.nagios_cleanup()
        univention.admin.handlers.simpleComputer.cleanup(self)


def rewrite(filter, mapping):
    if filter.variable == 'ip':
        filter.variable = 'aRecord'
    else:
        univention.admin.mapping.mapRewrite(filter, mapping)


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=False, required=False, timeout=-1, sizelimit=0, serverctrls=None, response=None):
    res = []
    filter_s = univention.admin.filter.replace_fqdn_filter(filter_s)
    filter_s = univention.admin.handlers.dns.alias.lookup_alias_filter(lo, filter_s)
    filter = univention.admin.filter.conjunction('&', [
        univention.admin.filter.expression('objectClass', 'univentionHost'),
        univention.admin.filter.expression('objectClass', 'univentionClient'),
        univention.admin.filter.conjunction('!', [univention.admin.filter.expression('objectClass', 'posixAccount')]),
    ])

    if filter_s:
        filter_p = univention.admin.filter.parse(filter_s)
        univention.admin.filter.walk(filter_p, rewrite, arg=mapping)
        filter.expressions.append(filter_p)

    for dn, attrs in lo.search(str(filter), base, scope, [], unique, required, timeout, sizelimit, serverctrls, response):
        res.append(object(co, lo, None, dn, attributes=attrs))
    return res


def identify(dn, attr, canonical=False):
    return b'univentionHost' in attr.get('objectClass', []) and b'univentionClient' in attr.get('objectClass', []) and b'posixAccount' not in attr.get('objectClass', [])
