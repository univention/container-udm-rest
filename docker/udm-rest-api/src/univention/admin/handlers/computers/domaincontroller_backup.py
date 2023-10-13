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

"""|UDM| module for the Backup Directory Node hosts"""

import univention.admin.handlers
import univention.admin.localization
import univention.admin.mapping
import univention.admin.syntax
from univention.admin import nagios
from univention.admin.certificate import pki_option, pki_properties, pki_tab, register_pki_mapping
from univention.admin.handlers.computers.__base import ComputerObject
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.computers')
_ = translation.translate

module = 'computers/domaincontroller_backup'
operations = ['add', 'edit', 'remove', 'search', 'move']
docleanup = True
childs = False
short_description = _('Computer: Backup Directory Node')
object_name = _('Backup Directory Node')
object_name_plural = _('Backup Directory Nodes')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=('top', 'person', 'univentionHost', 'univentionDomainController'),
    ),
    'posix': univention.admin.option(
        short_description=_('Posix account'),
        default=1,
        objectClasses=('posixAccount', 'shadowAccount'),
    ),
    'kerberos': univention.admin.option(
        short_description=_('Kerberos principal'),
        default=1,
        objectClasses=('krb5Principal', 'krb5KDCEntry'),
    ),
    'samba': univention.admin.option(
        short_description=_('Samba account'),
        editable=True,
        default=1,
        objectClasses=('sambaSamAccount',),
    ),
    'pki': pki_option(),
}
property_descriptions = dict({
    'name': univention.admin.property(
        short_description=_('Directory Node name'),
        long_description='',
        syntax=univention.admin.syntax.hostName,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'description': univention.admin.property(
        short_description=_('Description'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
    ),
    'operatingSystem': univention.admin.property(
        short_description=_('Operating system'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
    ),
    'operatingSystemVersion': univention.admin.property(
        short_description=_('Operating system version'),
        long_description='',
        syntax=univention.admin.syntax.string,
    ),
    'domain': univention.admin.property(
        short_description=_('Domain'),
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
    'serverRole': univention.admin.property(
        short_description=_('System role'),
        long_description='',
        syntax=univention.admin.syntax.string,
        multivalue=True,
        include_in_default_search=True,
    ),
    'service': univention.admin.property(
        short_description=_('Service'),
        long_description='',
        syntax=univention.admin.syntax.Service,
        multivalue=True,
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
    'password': univention.admin.property(
        short_description=_('Password'),
        long_description='',
        syntax=univention.admin.syntax.passwd,
        options=['kerberos', 'posix', 'samba'],
        dontsearch=True,
    ),
    'unixhome': univention.admin.property(
        short_description=_('Unix home directory'),
        long_description='',
        syntax=univention.admin.syntax.absolutePath,
        options=['posix'],
        required=True,
        default=('/dev/null', []),
    ),
    'shell': univention.admin.property(
        short_description=_('Login shell'),
        long_description='',
        syntax=univention.admin.syntax.string,
        options=['posix'],
        default=('/bin/bash', []),
    ),
    'primaryGroup': univention.admin.property(
        short_description=_('Primary group'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        options=['posix'],
        required=True,
        dontsearch=True,
    ),
    'reinstall': univention.admin.property(
        short_description=_('(Re-)install on next boot'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
    ),
    'reinstalloption': univention.admin.property(
        short_description=_('additional start options'),
        long_description='',
        syntax=univention.admin.syntax.string,
    ),
    'instprofile': univention.admin.property(
        short_description=_('Name of installation profile'),
        long_description='',
        syntax=univention.admin.syntax.string,
    ),
    'inventoryNumber': univention.admin.property(
        short_description=_('Inventory number'),
        long_description='',
        syntax=univention.admin.syntax.string,
        multivalue=True,
    ),
    'groups': univention.admin.property(
        short_description=_('Groups'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        multivalue=True,
        dontsearch=True,
    ),
    'sambaRID': univention.admin.property(
        short_description=_('Relative ID'),
        long_description='',
        syntax=univention.admin.syntax.integer,
        dontsearch=True,
        options=['samba'],
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
    Tab(_('Account'), _('Account'), advanced=True, layout=[
        'password',
        'primaryGroup',
    ]),
    Tab(_('Unix account'), _('Unix account settings'), advanced=True, layout=[
        ['unixhome', 'shell'],
    ]),
    Tab(_('Services'), _('Services'), advanced=True, layout=[
        'service',
    ]),
    Tab(_('Deployment'), _('Deployment'), advanced=True, layout=[
        ['reinstall'],
        ['instprofile', 'reinstalloption'],
    ]),
    Tab(_('Groups'), _('Group memberships'), advanced=True, layout=[
        'groups',
    ]),
    Tab(_('DNS alias'), _('Alias DNS entry'), advanced=True, layout=[
        'dnsEntryZoneAlias',
    ]),
    pki_tab(),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
mapping.register('domain', 'associatedDomain', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('serverRole', 'univentionServerRole')
mapping.register('mac', 'macAddress', encoding='ASCII')
mapping.register('inventoryNumber', 'univentionInventoryNumber')
mapping.register('reinstall', 'univentionServerReinstall', None, univention.admin.mapping.ListToString)
mapping.register('instprofile', 'univentionServerInstallationProfile', None, univention.admin.mapping.ListToString)
mapping.register('reinstalloption', 'univentionServerInstallationOption', None, univention.admin.mapping.ListToString)
mapping.register('network', 'univentionNetworkLink', None, univention.admin.mapping.ListToString)
mapping.register('unixhome', 'homeDirectory', None, univention.admin.mapping.ListToString)
mapping.register('shell', 'loginShell', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('service', 'univentionService')
mapping.register('operatingSystem', 'univentionOperatingSystem', None, univention.admin.mapping.ListToString)
mapping.register('operatingSystemVersion', 'univentionOperatingSystemVersion', None, univention.admin.mapping.ListToString)
register_pki_mapping(mapping)
# add Nagios extension
nagios.addPropertiesMappingOptionsAndLayout(property_descriptions, mapping, options, layout)


class object(ComputerObject):
    module = module
    CONFIG_NAME = 'univentionDefaultDomainControllerMasterGroup'
    SAMBA_ACCOUNT_FLAG = 'S'
    SERVER_ROLE = 'backup'


rewrite = object.rewrite_filter
lookup_filter = object.lookup_filter
lookup = object.lookup
identify = object.identify
