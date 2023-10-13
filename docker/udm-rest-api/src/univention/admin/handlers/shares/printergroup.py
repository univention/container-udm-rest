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

"""|UDM| module for printer groups"""

from ldap.filter import escape_filter_chars, filter_format

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.syntax
import univention.admin.uldap
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.shares')
_ = translation.translate

module = 'shares/printergroup'
operations = ['add', 'edit', 'remove', 'search', 'move']
childs = False
short_description = _('Printer share: Printer group')
object_name = _('Printer share group')
object_name_plural = _('Printer share groups')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionPrinterGroup'],
    ),
}
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
    'groupMember': univention.admin.property(
        short_description=_('Group members'),
        long_description='',
        syntax=univention.admin.syntax.PrinterNames,
        multivalue=True,
        required=True,
    ),
    'sambaName': univention.admin.property(
        short_description=_('Windows name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        unique=True,
    ),
}

layout = [
    Tab(_('General'), _('General settings'), layout=[
        Group(_('General printer group share settings'), layout=[
            ['name', 'spoolHost'],
            ['sambaName', 'groupMember'],
        ]),
    ]),
]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('spoolHost', 'univentionPrinterSpoolHost', encoding='ASCII')
mapping.register('sambaName', 'univentionPrinterSambaName', None, univention.admin.mapping.ListToString)
mapping.register('groupMember', 'univentionPrinterGroupMember')


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_pre_create(self):
        super(object, self)._ldap_pre_create()
        self.is_valid_printer_object()  # check all members

    def _ldap_modlist(self):  # check for membership in a quota-printerclass
        if self.hasChanged('groupMember'):
            self.is_valid_printer_object()  # check all members
        return univention.admin.handlers.simpleLdap._ldap_modlist(self)

    def _ldap_pre_remove(self):  # check for last member in printerclass on same spoolhost
        super(object, self)._ldap_pre_remove()
        printergroups_filter = '(&(objectClass=univentionPrinterGroup)(|%s))' % (''.join(filter_format('(univentionPrinterSpoolHost=%s)', [x]) for x in self.info['spoolHost']))
        rm_attrib = []
        for pg_dn, member_list in self.lo.search(filter=printergroups_filter, attr=['univentionPrinterGroupMember', 'cn']):
            for member_cn in [x.decode('UTF-8') for x in member_list['univentionPrinterGroupMember']]:
                if member_cn == self.info['name']:
                    rm_attrib.append(pg_dn)
                    if len(member_list['univentionPrinterGroupMember']) < 2:
                        raise univention.admin.uexceptions.emptyPrinterGroup(_('%(name)s is the last member of the printer group %(group)s. ') % {'name': self.info['name'], 'group': member_list['cn'][0].decode('UTF-8')})

        printergroup_module = univention.admin.modules.get('shares/printergroup')
        for rm_dn in rm_attrib:
            printergroup_object = univention.admin.objects.get(printergroup_module, None, self.lo, position='', dn=rm_dn)
            printergroup_object.open()
            printergroup_object['groupMember'].remove(self.info['name'])
            printergroup_object.modify()

    def is_valid_printer_object(self):  # check printer on current spoolhost
        spoolhosts = '(|%s)' % ''.join(filter_format('(univentionPrinterSpoolHost=%s)', [host]) for host in self.info['spoolHost'])
        for member in self.info['groupMember']:
            if not self.lo.searchDn(filter='(&(objectClass=univentionPrinter)(cn=%s)%s)' % (escape_filter_chars(member), spoolhosts)):
                raise univention.admin.uexceptions.notValidPrinter(_('%(name)s is not a valid printer on Spoolhost %(host)s.') % {'name': member, 'host': self.info['spoolHost']})


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
