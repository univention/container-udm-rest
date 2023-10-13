# -*- coding: utf-8 -*-
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2013-2023 Univention GmbH
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

"""|UDM| module for LDAP schema extensions"""

import apt

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.settings')
_ = translation.translate

module = 'settings/ldapschema'
superordinate = 'settings/cn'
childs = False
operations = ['add', 'edit', 'remove', 'search', 'move']
short_description = _('Settings: LDAP Schema Extension')
object_name = _('LDAP Schema Extension')
object_name_plural = _('LDAP Schema Extensions')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionObjectMetadata', 'univentionLDAPExtensionSchema'],
    ),
}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Schema name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        identifies=True,
    ),
    'filename': univention.admin.property(
        short_description=_('Schema file name'),
        long_description='',
        syntax=univention.admin.syntax.BaseFilename,
        required=True,
        default='',
    ),
    'data': univention.admin.property(
        short_description=_('Schema data'),
        long_description='',
        syntax=univention.admin.syntax.Base64Bzip2Text,
        required=True,
    ),
    'active': univention.admin.property(
        short_description=_('Active'),
        long_description='',
        syntax=univention.admin.syntax.TrueFalseUp,
        default='FALSE',
    ),
    'appidentifier': univention.admin.property(
        short_description=_('App identifier'),
        long_description='',
        syntax=univention.admin.syntax.TextArea,
        multivalue=True,
    ),
    'package': univention.admin.property(
        short_description=_('Software package'),
        long_description='',
        syntax=univention.admin.syntax.string,
    ),
    'packageversion': univention.admin.property(
        short_description=_('Software package version'),
        long_description='',
        syntax=univention.admin.syntax.DebianPackageVersion,
    ),
}

layout = [
    Tab(_('General'), _('Basic values'), layout=[
        Group(_('General LDAP schema extension settings'), layout=[
            ["name"],
            ["filename"],
            ["data"],
        ]),
        Group(_('Metadata'), layout=[
            ["package"],
            ["packageversion"],
            ["appidentifier"],
        ]),
        Group(_('Activated'), layout=[
            ["active"],
        ]),
    ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('filename', 'univentionLDAPSchemaFilename', None, univention.admin.mapping.ListToString)
mapping.register('data', 'univentionLDAPSchemaData', univention.admin.mapping.mapBase64, univention.admin.mapping.unmapBase64)
mapping.register('active', 'univentionLDAPSchemaActive', None, univention.admin.mapping.ListToString)
mapping.register('appidentifier', 'univentionAppIdentifier')
mapping.register('package', 'univentionOwnedByPackage', None, univention.admin.mapping.ListToString)
mapping.register('packageversion', 'univentionOwnedByPackageVersion', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_pre_modify(self):
        super(object, self)._ldap_pre_modify()
        diff_keys = [key for key in self.info.keys() if self.info.get(key) != self.oldinfo.get(key) and key not in ('active', 'appidentifier')]
        if not diff_keys:  # check for trivial change
            return
        if not self.hasChanged('package'):
            old_version = self.oldinfo.get('packageversion', '0')
            if not apt.apt_pkg.version_compare(self['packageversion'], old_version) > -1:
                raise univention.admin.uexceptions.valueInvalidSyntax(_('packageversion: Version must not be lower than the current one.'), property='packageversion')


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
