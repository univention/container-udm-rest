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

"""|UDM| module for network objects"""

import ipaddress
import traceback

import ldap
from ldap.filter import filter_format

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.modules
import univention.admin.uexceptions
import univention.debug as ud
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.networks')
_ = translation.translate

module = 'networks/network'
operations = ['add', 'edit', 'remove', 'search']
childs = False
short_description = _('Networks: Network')
object_name = _('Network')
object_name_plural = _('Networks')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionNetworkClass'],
    ),
}

property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'network': univention.admin.property(
        short_description=_('Networks'),
        long_description='',
        syntax=univention.admin.syntax.ipAddress,
        include_in_default_search=True,
        required=True,
        may_change=False,
    ),
    'netmask': univention.admin.property(
        short_description=_('Netmask'),
        long_description='',
        syntax=univention.admin.syntax.netmask,
        include_in_default_search=True,
        required=True,
        may_change=False,
    ),
    'nextIp': univention.admin.property(
        short_description=_('Next IP address'),
        long_description='',
        syntax=univention.admin.syntax.string,
        dontsearch=True,
    ),
    'ipRange': univention.admin.property(
        short_description=_('IP address range'),
        long_description='',
        syntax=univention.admin.syntax.IP_AddressRange,
        multivalue=True,
        dontsearch=True,
    ),
    'dnsEntryZoneForward': univention.admin.property(
        short_description=_('DNS forward lookup zone'),
        long_description='',
        syntax=univention.admin.syntax.DNS_ForwardZone,
        dontsearch=True,
    ),
    'dnsEntryZoneReverse': univention.admin.property(
        short_description=_('DNS reverse lookup zone'),
        long_description='',
        syntax=univention.admin.syntax.DNS_ReverseZone,
        dontsearch=True,
    ),
    'dhcpEntryZone': univention.admin.property(
        short_description=_('DHCP service'),
        long_description='',
        syntax=univention.admin.syntax.dhcpService,
        dontsearch=True,
    ),
}

layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('General network settings'), layout=[
            'name',
            ['network', 'netmask'],
            'ipRange',
        ]),
        Group(_('DNS preferences'), layout=[
            'dnsEntryZoneForward',
            'dnsEntryZoneReverse',
        ]),
        Group(_('DHCP preferences'), layout=[
            'dhcpEntryZone',
        ]),
    ]),
]


def rangeMap(value, encoding=()):
    return [u' '.join(x).encode(*encoding) for x in value]


def rangeUnmap(value, encoding=()):
    return [x.decode(*encoding).split(u' ') for x in value]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('network', 'univentionNetwork', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('netmask', 'univentionNetmask', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('nextIp', 'univentionNextIp', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('dnsEntryZoneForward', 'univentionDnsForwardZone', univention.admin.mapping.IgnoreNone, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('dnsEntryZoneReverse', 'univentionDnsReverseZone', univention.admin.mapping.IgnoreNone, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('dhcpEntryZone', 'univentionDhcpEntry', univention.admin.mapping.IgnoreNone, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('ipRange', 'univentionIpRange', rangeMap, rangeUnmap, encoding='ASCII')


class object(univention.admin.handlers.simpleLdap):
    module = module

    def stepIp(self):
        try:
            network = ipaddress.ip_network(u'%s/%s' % (self['network'], self['netmask']), strict=False)
        except ValueError as exc:
            raise univention.admin.uexceptions.valueError(str(exc), property='nextIp')

        if self['nextIp']:
            # nextIP is already set:
            # - check range for actual ip
            # - inc ip
            # - check for range
            currentIp = ipaddress.ip_address(u'%s' % self['nextIp'])
            newIp = ipaddress.ip_address(u'%s' % self['nextIp']) + 1
            for ipRange in self['ipRange']:
                if not ipRange:  # ignore bad default value self['ipRange'] = ['']
                    continue
                firstIP = ipaddress.ip_address(u'%s' % ipRange[0])
                lastIP = ipaddress.ip_address(u'%s' % ipRange[1])
                if firstIP <= currentIp <= lastIP:
                    if firstIP <= newIp <= lastIP:
                        self['nextIp'] = str(newIp)
                    else:
                        position = (self['ipRange'].index(ipRange) + 1) % len(self['ipRange'])  # find "next" ipRange
                        self['nextIp'] = self['ipRange'][position][0]  # select first IP of that range
                        if ipaddress.ip_address(u'%s' % self['nextIp']) == network.network_address:  # do not give out all hostbits zero
                            self['nextIp'] = str(ipaddress.ip_address(u'%s' % self['nextIp']) + 1)
                    break
            else:  # currentIp is not in any ipRange
                if self['ipRange'] and self['ipRange'][0]:  # ignore bad default value self['ipRange'] = ['']
                    self['nextIp'] = self['ipRange'][0][0]
                    if ipaddress.ip_address(u'%s' % self['nextIp']) == network.network_address:  # do not give out all hostbits zero
                        self['nextIp'] = str(ipaddress.ip_address(u'%s' % self['nextIp']) + 1)
                else:  # did not find nextIp in ipRanges because ipRanges are empty
                    if newIp in network:
                        self['nextIp'] = str(newIp)
                    else:
                        self['nextIp'] = str(network.network_address + 1)  # first usable host address in network
        elif self['ipRange']:
            # nextIP is not set
            # - use first ip range entry
            self['nextIp'] = self['ipRange'][0][0]
            if ipaddress.ip_address(u'%s' % self['nextIp']) == network.network_address:  # do not give out all hostbits zero
                self['nextIp'] = str(ipaddress.ip_address(u'%s' % self['nextIp']) + 1)
        elif self['network']:
            # nextIP is not set, no IPrange, then we use the first ip of the network
            self['nextIp'] = str(network.network_address + 1)  # first usable host address in network

    def refreshNextIp(self):
        start_ip = self['nextIp']
        while self.lo.search(scope='domain', attr=['aRecord'], filter=filter_format('(&(aRecord=%s))', [self['nextIp']])) or self['nextIp'].split('.')[-1] in ['0', '1', '254']:
            self.stepIp()
            if self['nextIp'] == start_ip:
                raise univention.admin.uexceptions.nextFreeIp()
        self.modify(ignore_license=True)

    def _ldap_post_remove(self):
        super(object, self)._ldap_post_remove()
        filter_ = univention.admin.filter.expression('univentionNetworkLink', self.dn, escape=True)
        for computer in univention.admin.modules.get('computers/computer').lookup(None, self.lo, filter_s=filter_):
            try:
                self.lo.modify(computer.dn, [('univentionNetworkLink', self.dn.encode('UTF-8'), b'')])
            except (univention.admin.uexceptions.base, ldap.LDAPError):
                ud.debug(ud.ADMIN, ud.ERROR, 'Failed to remove network %s from %s: %s' % (self.dn, computer.dn, traceback.format_exc()))

    def _ldap_addlist(self):
        if not self['nextIp']:
            self.stepIp()

        return super(object, self)._ldap_addlist()

    def _ldap_modlist(self):
        ml = univention.admin.handlers.simpleLdap._ldap_modlist(self)

        next_ip_changed = False

        if self.hasChanged('ipRange'):
            try:
                network = ipaddress.ip_network(u'%s/%s' % (self['network'], self['netmask']), strict=False)
                ipaddress.ip_address(u'%s' % self['nextIp'])
            except ValueError as exc:
                raise univention.admin.uexceptions.valueError(str(exc), property='nextIp')

            if self['ipRange']:
                try:
                    self.sort_ipranges()
                except TypeError as exc:
                    raise univention.admin.uexceptions.valueError(str(exc))
                self['nextIp'] = self['ipRange'][0][0]
            else:
                self['nextIp'] = str(network.network_address + 1)
            if self['nextIp'] != self.oldattr.get('univentionNextIp', [b''])[0].decode('UTF-8'):
                next_ip_changed = True

            ipRange = []
            for i in self['ipRange']:
                firstIP = ipaddress.ip_address(u'%s' % i[0])
                lastIP = ipaddress.ip_address(u'%s' % i[1])
                for j in self['ipRange']:
                    if i != j:
                        otherFirstIP = ipaddress.ip_address(u'%s' % j[0])
                        otherLastIP = ipaddress.ip_address(u'%s' % j[1])
                        if firstIP < otherFirstIP < lastIP or \
                                firstIP < otherLastIP < lastIP or \
                                otherFirstIP < firstIP < otherLastIP or \
                                otherFirstIP < lastIP < otherLastIP:
                            raise univention.admin.uexceptions.rangesOverlapping('%s-%s; %s-%s' % (i[0], i[1], j[0], j[1]))
                if firstIP not in network or lastIP not in network:
                    raise univention.admin.uexceptions.rangeNotInNetwork('%s-%s' % (firstIP, lastIP))
                if firstIP == network.network_address or lastIP == network.network_address:
                    raise univention.admin.uexceptions.rangeInNetworkAddress('%s-%s' % (firstIP, lastIP))
                if firstIP == network.broadcast_address or lastIP == network.broadcast_address:
                    raise univention.admin.uexceptions.rangeInBroadcastAddress('%s-%s' % (firstIP, lastIP))
                ipRange.append(u' '.join(i).encode('ASCII'))

            ud.debug(ud.ADMIN, ud.INFO, 'old Range: %s' % self.oldinfo.get('ipRange'))
            ml = [x for x in ml if x[0] != 'univentionIpRange']
            ml.append(('univentionIpRange', self.oldattr.get('univentionIpRange', [b'']), ipRange))

        if next_ip_changed:
            ml = [x for x in ml if x[0] != 'univentionNextIp']
            ml.append(('univentionNextIp', self.oldattr.get('univentionNextIp', b''), self['nextIp'].encode('ASCII')))

        return ml

    def sort_ipranges(self):
        # make sure that the ipRanges are ordered by their start address (smallest first)
        for i in range(1, len(self['ipRange'])):
            if ipaddress.ip_address(u'%s' % self['ipRange'][i][0]) < ipaddress.ip_address(u'%s' % self['ipRange'][i - 1][0]):
                self['ipRange'].insert(i - 1, self['ipRange'].pop(i))
        for i in range(1, len(self['ipRange'])):
            if ipaddress.ip_address(u'%s' % self['ipRange'][i][0]) < ipaddress.ip_address(u'%s' % self['ipRange'][i - 1][0]):
                self.sort_ipranges()


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
