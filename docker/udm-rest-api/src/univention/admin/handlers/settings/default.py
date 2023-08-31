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

"""|UDM| module for default paths"""

import univention.admin.handlers
import univention.admin.localization
import univention.admin.password
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.settings')
_ = translation.translate

module = 'settings/default'
superordinate = 'settings/cn'
childs = False
operations = ['search', 'edit']
short_description = _('Preferences: Default')
object_name = _('Default preference')
object_name_plural = _('Default preferences')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionDefault'],
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
        default=('univention', []),
    ),
    'defaultGroup': univention.admin.property(
        short_description=_('Default Primary Group'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        dontsearch=True,
        required=True,
    ),
    'defaultComputerGroup': univention.admin.property(
        short_description=_('Default Group for Computers'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        dontsearch=True,
        required=True,
    ),
    'defaultDomainControllerGroup': univention.admin.property(
        short_description=_('Default Group for Replica Directory Nodes'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        dontsearch=True,
        required=True,
    ),
    'defaultDomainControllerMBGroup': univention.admin.property(
        short_description=_('Default Group for Primary and Backup Directory Nodes'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        dontsearch=True,
        required=True,
    ),
    'defaultMemberServerGroup': univention.admin.property(
        short_description=_('Default Group for Managed Nodes'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        dontsearch=True,
        required=True,
    ),
    'defaultClientGroup': univention.admin.property(
        short_description=_('Default Group for Client Computers'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        dontsearch=True,
        required=True,
    ),
    'defaultKdeProfiles': univention.admin.property(
        short_description=_('Default KDE Profiles'),
        long_description='',
        syntax=univention.admin.syntax.string,
        multivalue=True,
    ),
}

layout = [
    Tab(_('General'), _('Basic values'), layout=[
        Group(_('Default settings description'), layout=[
            "name",
        ]),
    ]),
    Tab(_('Primary Groups'), _('Primary Groups'), layout=[
        Group(_('Primary Groups'), layout=[
            "defaultGroup",
            "defaultComputerGroup",
            "defaultDomainControllerMBGroup",
            "defaultDomainControllerGroup",
            "defaultMemberServerGroup",
            "defaultClientGroup",
        ]),
    ]),
    Tab(_('KDE Profiles'), _('KDE Profiles'), layout=[
        Group(_('KDE Profiles'), layout=[
            "defaultKdeProfiles",
        ]),
    ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('defaultGroup', 'univentionDefaultGroup', None, univention.admin.mapping.ListToString)
mapping.register('defaultComputerGroup', 'univentionDefaultComputerGroup', None, univention.admin.mapping.ListToString)
mapping.register('defaultDomainControllerMBGroup', 'univentionDefaultDomainControllerMasterGroup', None, univention.admin.mapping.ListToString)
mapping.register('defaultDomainControllerGroup', 'univentionDefaultDomainControllerGroup', None, univention.admin.mapping.ListToString)
mapping.register('defaultMemberServerGroup', 'univentionDefaultMemberserverGroup', None, univention.admin.mapping.ListToString)
mapping.register('defaultClientGroup', 'univentionDefaultClientGroup', None, univention.admin.mapping.ListToString)
mapping.register('defaultKdeProfiles', 'univentionDefaultKdeProfiles', encoding='ASCII')


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_dn(self):
        return 'cn=default containers,cn=univention,%s' % (self.position.getDomain())


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
