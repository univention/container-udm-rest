# -*- coding: utf-8 -*-
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2011-2023 Univention GmbH
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

"""|UDM| module for |DNS| text records (TXT)"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.handlers.dns.forward_zone
import univention.admin.localization
from univention.admin.handlers.dns import ARPA_IP4
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.dns')
_ = translation.translate

module = 'dns/txt_record'
operations = ['add', 'edit', 'remove', 'search']
columns = ['txt']
superordinate = 'dns/forward_zone'
childs = False
short_description = _('DNS: TXT Record')
object_name = _('TXT record')
object_name_plural = _('TXT record')
long_description = _('Resolve the symbolic name to some textual data.')
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'dNSZone'],
    ),
}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description=_('The name of the host relative to the domain.'),
        syntax=univention.admin.syntax.dnsName,
        include_in_default_search=True,
        required=True,
        identifies=True,
    ),
    'zonettl': univention.admin.property(
        short_description=_('Time to live'),
        long_description=_('The time this entry may be cached.'),
        syntax=univention.admin.syntax.UNIX_TimeInterval,
        default=(('22', 'hours'), []),
        dontsearch=True,
    ),
    'txt': univention.admin.property(
        short_description=_('Text Record'),
        long_description=_('One or more arbitrary text strings.'),
        syntax=univention.admin.syntax.string,
        multivalue=True,
        required=True,
        size='Two',
    ),
}

layout = [
    Tab(_('General'), _('Basic values'), layout=[
        Group(_('General TXT record settings'), layout=[
            'name',
            'txt',
            'zonettl',
        ]),
    ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'relativeDomainName', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('txt', 'tXTRecord', encoding='ASCII')
mapping.register('zonettl', 'dNSTTL', univention.admin.mapping.mapUNIX_TimeInterval, univention.admin.mapping.unmapUNIX_TimeInterval)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _updateZone(self):
        if self.update_zone:
            self.superordinate.open()
            self.superordinate.modify()

    def __init__(self, co, lo, position, dn='', superordinate=None, attributes=[], update_zone=True):
        self.update_zone = update_zone
        univention.admin.handlers.simpleLdap.__init__(self, co, lo, position, dn, superordinate, attributes=attributes)

    def _ldap_addlist(self):
        return super(object, self)._ldap_addlist() + [
            (self.superordinate.mapping.mapName('zone'), self.superordinate.mapping.mapValue('zone', self.superordinate['zone'])),
        ]

    def _ldap_post_create(self):
        super(object, self)._ldap_post_create()
        self._updateZone()

    def _ldap_post_modify(self):
        super(object, self)._ldap_post_modify()
        if self.hasChanged(self.descriptions.keys()):
            self._updateZone()

    def _ldap_post_remove(self):
        super(object, self)._ldap_post_remove()
        self._updateZone()

    @classmethod
    def unmapped_lookup_filter(cls):
        return univention.admin.filter.conjunction('&', [
            univention.admin.filter.expression('objectClass', 'dNSZone'),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('relativeDomainName', '@')]),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('zoneName', '*.in-addr.arpa', escape=False)]),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('cNAMERecord', '*', escape=False)]),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('sRVRecord', '*', escape=False)]),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('aRecord', '*', escape=False)]),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('aAAARecord', '*', escape=False)]),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('mXRecord', '*', escape=False)]),
            univention.admin.filter.expression('tXTRecord', '*', escape=False),
        ])

    @classmethod
    def lookup_filter_superordinate(cls, filter, superordinate):
        filter.expressions.append(univention.admin.filter.expression('zoneName', superordinate.mapping.mapValueDecoded('zone', superordinate['zone']), escape=True))
        return filter


lookup = object.lookup
lookup_filter = object.lookup_filter


def identify(dn, attr, canonical=False):
    mod = module.encode('ASCII')
    return all([
        b'dNSZone' in attr.get('objectClass', []),
        b'@' not in attr.get('relativeDomainName', []),
        not attr.get('zoneName', [b'.in-addr.arpa'])[0].decode('ASCII').endswith(ARPA_IP4),
        attr.get('tXTRecord', []),
        not any(attr.get(a) for a in ('aRecord', 'aAAARecord', 'mXRecord', 'sRVRecord')),
        mod in attr.get('univentionObjectType', [mod]),
    ])
