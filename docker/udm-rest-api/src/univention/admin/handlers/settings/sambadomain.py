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

"""|UDM| module for samba domain configuration"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.password
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.settings')
_ = translation.translate

# see also container/dc.py


def logonToChangePWMap(val):
    """
    'User must logon to change PW' behaves like an integer (at least
    to us), but must be stored as either 0 (allow) or 2 (disallow)
    """
    if (val == "1"):
        return b"2"
    else:
        return b"0"

# see also container/dc.py


def logonToChangePWUnmap(val):
    if (val[0] == b"2"):
        return u"1"
    else:
        return u"2"


module = 'settings/sambadomain'
childs = False
operations = ['add', 'edit', 'remove', 'search', 'move']
short_description = _('Settings: Samba Domain')
object_name = _('Samba Domain')
object_name_plural = _('Samba Domains')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['sambaDomain'],
    ),
}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Samba domain name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        identifies=True,
    ),
    'SID': univention.admin.property(
        short_description=_('Samba SID'),
        long_description='',
        syntax=univention.admin.syntax.string,
        required=True,
        may_change=False,
        default='',
    ),
    'NextUserRid': univention.admin.property(
        short_description=_('Next user RID'),
        long_description='',
        syntax=univention.admin.syntax.integer,
        default='1000',
    ),
    'NextGroupRid': univention.admin.property(
        short_description=_('Next group RID'),
        long_description='',
        syntax=univention.admin.syntax.integer,
        default='1000',
    ),
    'NextRid': univention.admin.property(
        short_description=_('Next RID'),
        long_description='',
        syntax=univention.admin.syntax.integer,
        default='1000',
    ),
    'passwordLength': univention.admin.property(
        short_description=_('Password length'),
        long_description='',
        syntax=univention.admin.syntax.integer,
    ),
    'passwordHistory': univention.admin.property(
        short_description=_('Password history'),
        long_description='',
        syntax=univention.admin.syntax.integer,
    ),
    'minPasswordAge': univention.admin.property(
        short_description=_('Minimum password age'),
        long_description='',
        syntax=univention.admin.syntax.SambaMinPwdAge,
    ),
    'badLockoutAttempts': univention.admin.property(
        short_description=_('Bad lockout attempts'),
        long_description='',
        syntax=univention.admin.syntax.integer,
    ),
    'logonToChangePW': univention.admin.property(
        short_description=_('User must logon to change password'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
    ),
    'maxPasswordAge': univention.admin.property(
        short_description=_('Maximum password age'),
        long_description='',
        syntax=univention.admin.syntax.SambaMaxPwdAge,
    ),
    'lockoutDuration': univention.admin.property(
        short_description=_('Lockout duration minutes'),
        long_description='',
        syntax=univention.admin.syntax.UNIX_TimeInterval,
    ),
    'resetCountMinutes': univention.admin.property(
        short_description=_('Reset count minutes'),
        long_description='',
        syntax=univention.admin.syntax.integer,
    ),
    'disconnectTime': univention.admin.property(
        short_description=_('Disconnect time'),
        long_description='',
        syntax=univention.admin.syntax.UNIX_TimeInterval,
    ),
    'refuseMachinePWChange': univention.admin.property(
        short_description=_('Refuse machine password change'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
    ),
    'domainPasswordComplex': univention.admin.property(
        short_description=_('Passwords must meet complexity requirements'),
        long_description=_("Is not based on the user's account name. Contains at least six characters. Contains characters from three of the following four categories: Uppercase alphabet characters (A-Z), Lowercase alphabet characters (a-z), Arabic numerals (0-9), Nonalphanumeric characters (for example, !$#,%)"),
        syntax=univention.admin.syntax.boolean,
    ),
    'domainPasswordStoreCleartext': univention.admin.property(
        short_description=_('Store plaintext passwords'),
        long_description=_('Store plaintext passwords where account have "store passwords with reversible encryption" set.'),
        syntax=univention.admin.syntax.boolean,
    ),
    'domainPwdProperties': univention.admin.property(
        short_description=_('Password properties'),
        long_description=_('A bitfield to indicate complexity and storage restrictions.'),
        syntax=univention.admin.syntax.integer,
    ),
}

layout = [
    Tab(_('General'), _('Basic values'), layout=[
        Group(_('General Samba domain settings'), layout=[
            ["name", "SID"],
            ["NextRid", "NextUserRid", "NextGroupRid"],
        ]),
        Group(_('Password'), layout=[
            ["passwordLength", "passwordHistory"],
            ["minPasswordAge"],
            ["maxPasswordAge"],
            ["logonToChangePW", "refuseMachinePWChange"],
            ["domainPasswordComplex", "domainPasswordStoreCleartext"],
        ]),
        Group(_('Connection'), layout=[
            ["badLockoutAttempts"],
            ["resetCountMinutes"],
            ["lockoutDuration"],
            ["disconnectTime"],
        ]),
    ]),
]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'sambaDomainName', None, univention.admin.mapping.ListToString)
mapping.register('SID', 'sambaSID', None, univention.admin.mapping.ListToString, encoding='ASCII')
mapping.register('NextUserRid', 'sambaNextUserRid', None, univention.admin.mapping.ListToString)
mapping.register('NextGroupRid', 'sambaNextGroupRid', None, univention.admin.mapping.ListToString)
mapping.register('NextRid', 'sambaNextRid', None, univention.admin.mapping.ListToString)
mapping.register('passwordLength', 'sambaMinPwdLength', None, univention.admin.mapping.ListToString)
mapping.register('passwordHistory', 'sambaPwdHistoryLength', None, univention.admin.mapping.ListToString)
mapping.register('minPasswordAge', 'sambaMinPwdAge', univention.admin.mapping.mapUNIX_TimeInterval, univention.admin.mapping.unmapUNIX_TimeInterval)
mapping.register('maxPasswordAge', 'sambaMaxPwdAge', univention.admin.mapping.mapUNIX_TimeInterval, univention.admin.mapping.unmapUNIX_TimeInterval)
mapping.register('badLockoutAttempts', 'sambaLockoutThreshold', None, univention.admin.mapping.ListToString)
mapping.register('logonToChangePW', 'sambaLogonToChgPwd', logonToChangePWMap, logonToChangePWUnmap)
mapping.register('lockoutDuration', 'sambaLockoutDuration', univention.admin.mapping.mapUNIX_TimeInterval, univention.admin.mapping.unmapUNIX_TimeInterval)
mapping.register('resetCountMinutes', 'sambaLockoutObservationWindow', None, univention.admin.mapping.ListToString)
mapping.register('disconnectTime', 'sambaForceLogoff', univention.admin.mapping.mapUNIX_TimeInterval, univention.admin.mapping.unmapUNIX_TimeInterval)
mapping.register('refuseMachinePWChange', 'sambaRefuseMachinePwdChange', None, univention.admin.mapping.ListToString)
mapping.register('domainPwdProperties', 'univentionSamba4pwdProperties', None, univention.admin.mapping.ListToString)

DOMAIN_PASSWORD_COMPLEX = 1
DOMAIN_PASSWORD_NO_ANON_CHANGE = 2
DOMAIN_PASSWORD_NO_CLEAR_CHANGE = 4
DOMAIN_LOCKOUT_ADMINS = 8
DOMAIN_PASSWORD_STORE_CLEARTEXT = 16
DOMAIN_REFUSE_PASSWORD_CHANGE = 32


class object(univention.admin.handlers.simpleLdap):
    module = module

    def open(self):
        univention.admin.handlers.simpleLdap.open(self)
        if self.dn:
            # map domain domainPwdProperties bitfield to individual password attributes
            self['domainPasswordComplex'] = '0'
            self['domainPasswordStoreCleartext'] = '0'
            props = int(self.info.get('domainPwdProperties', 0))
            if (props | DOMAIN_PASSWORD_COMPLEX) == props:
                self['domainPasswordComplex'] = '1'
            if (props | DOMAIN_PASSWORD_STORE_CLEARTEXT) == props:
                self['domainPasswordStoreCleartext'] = '1'

    def _ldap_pre_create(self):
        super(object, self)._ldap_pre_create()
        self.__update_password_properties()

    def _ldap_pre_modify(self):
        super(object, self)._ldap_pre_modify()
        self.__update_password_properties()

    def __update_password_properties(self):
        # DOMAIN_PASSWORD_COMPLEX 1 domainPasswordComplex -> univentionSamba4pwdProperties
        # DOMAIN_PASSWORD_NO_ANON_CHANGE 2 -> logonToChangePW -> sambaLogonToChgPwd
        # DOMAIN_PASSWORD_NO_CLEAR_CHANGE 4
        # DOMAIN_LOCKOUT_ADMINS 8
        # DOMAIN_PASSWORD_STORE_CLEARTEXT 16 -> univentionSamba4pwdProperties
        # DOMAIN_REFUSE_PASSWORD_CHANGE 32 -> refuseMachinePWChange -> sambaRefuseMachinePwdChange

        props = int(self.get('domainPwdProperties', 0))

        if self.hasChanged('domainPwdProperties'):
            # if domainPwdProperties where modified directly (udm cli, s4 connector),
            # this setting has precedence
            return

        # domainPasswordComplex -> domainPwdProperties
        if self.hasChanged('domainPasswordComplex'):
            if self['domainPasswordComplex'] == '1':
                props = props | DOMAIN_PASSWORD_COMPLEX
            else:
                props = props & (~DOMAIN_PASSWORD_COMPLEX)
        # domainPasswordStoreCleartext -> domainPwdProperties
        if self.hasChanged('domainPasswordStoreCleartext'):
            if self['domainPasswordStoreCleartext'] == '1':
                props = props | DOMAIN_PASSWORD_STORE_CLEARTEXT
            else:
                props = props & (~DOMAIN_PASSWORD_STORE_CLEARTEXT)

        if props != int(self.get("domainPwdProperties", 0)):
            self['domainPwdProperties'] = str(props)

    @classmethod
    def unmapped_lookup_filter(cls):
        return univention.admin.filter.conjunction('&', [
            univention.admin.filter.expression('objectClass', 'sambaDomain'),
            univention.admin.filter.conjunction('!', [univention.admin.filter.expression('objectClass', 'univentionDomain')]),
        ])


lookup = object.lookup
lookup_filter = object.lookup_filter


def identify(dn, attr, canonical=False):
    return b'sambaDomain' in attr.get('objectClass', []) and b'univentionDomain' not in attr.get('objectClass', [])
