# -*- coding: utf-8 -*-
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2018-2023 Univention GmbH
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

"""|UDM| module for Portal entries"""

import univention.admin.localization
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.settings')
_ = translation.translate

module = 'settings/portal_category'
default_containers = ['cn=categories,cn=portal,cn=univention']
childs = False
operations = ['add', 'edit', 'remove', 'search', 'move']
short_description = _('Deprecated Portal: Category')
object_name = _('Deprecated Portal category')
object_name_plural = _('Deprecated Portal categories')
long_description = _('Object under which settings/portal_entry objects can be displayed')
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionPortalCategory'],
    ),
}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Internal name'),
        long_description='',
        syntax=univention.admin.syntax.string_numbers_letters_dots,
        include_in_default_search=True,
        required=True,
        identifies=True,
    ),
    'displayName': univention.admin.property(
        short_description=_('Display Name'),
        long_description=_('Display name of the category. At least one entry; strongly encouraged to have one for en_US'),
        syntax=univention.admin.syntax.LocalizedDisplayName,
        multivalue=True,
        required=True,
    ),
}

layout = [
    Tab(_('General'), _('Category options'), layout=[
        Group(_('Name'), layout=[
            ["name"],
        ]),
        Group(_('Display name'), layout=[
            ["displayName"],
        ]),
    ]),
]


def mapTranslationValue(vals, encoding=()):
    return [u' '.join(val).encode(*encoding) for val in vals]


def unmapTranslationValue(vals, encoding=()):
    return [val.decode(*encoding).split(u' ', 1) for val in vals]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('displayName', 'univentionPortalCategoryDisplayName', mapTranslationValue, unmapTranslationValue)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_post_modify(self):
        super(object, self)._ldap_post_modify()
        if self.hasChanged('name'):
            self.__update_property__content__of__portal()

    def _ldap_post_move(self, olddn):
        super(object, self)._ldap_post_move(olddn)
        self.__update_property__content__of__portal()

    def __update_property__content__of__portal(self):
        for portal_obj in univention.admin.modules.lookup('settings/portal', None, self.lo, scope='sub'):
            portal_obj.open()
            old_content = portal_obj.info.get('content', [])
            new_content = [[self.dn if self.lo.compare_dn(category, self.old_dn) else category, entries] for category, entries in old_content]
            if new_content != old_content:
                portal_obj['content'] = new_content
                portal_obj.modify()

    def _ldap_post_remove(self):
        super(object, self)._ldap_post_remove()
        for portal_obj in univention.admin.modules.lookup('settings/portal', None, self.lo, scope='sub'):
            self._remove_self_from_portal(portal_obj)

    def _remove_self_from_portal(self, portal_obj):
        portal_obj.open()
        old_content = portal_obj.info.get('content', [])
        new_content = [[category, entries] for category, entries in old_content if not self.lo.compare_dn(category, self.dn)]
        if new_content != old_content:
            portal_obj['content'] = new_content
            portal_obj.modify()


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
