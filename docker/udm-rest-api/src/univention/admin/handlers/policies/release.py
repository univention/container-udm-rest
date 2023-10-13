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

"""|UDM| module for the release settings policies"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.syntax
from univention.admin.layout import Group, Tab
from univention.admin.policy import (
    emptyAttributesProperty, fixedAttributesProperty, ldapFilterProperty, policy_object_tab,
    prohibitedObjectClassesProperty, register_policy_mapping, requiredObjectClassesProperty,
)


translation = univention.admin.localization.translation('univention.admin.handlers.policies')
_ = translation.translate


class releaseFixedAttributes(univention.admin.syntax.select):
    name = 'releaseFixedAttributes'
    choices = [
        ('univentionUpdateVersion', _('Release Version')),
    ]


module = 'policies/release'
operations = ['add', 'edit', 'remove', 'search']

policy_oc = 'univentionPolicyUpdate'
policy_apply_to = ["computers/domaincontroller_master", "computers/domaincontroller_backup", "computers/domaincontroller_slave", "computers/memberserver"]
policy_position_dn_prefix = "cn=update"

childs = False
short_description = _('Policy: Automatic updates')
object_name = _('Automatic updates policy')
object_name_plural = _('Automatic updates policies')
policy_short_description = _('Automatic updates')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionPolicy', 'univentionPolicyUpdate'],
    ),
}
property_descriptions = dict({
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description='',
        syntax=univention.admin.syntax.policyName,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'activate': univention.admin.property(
        short_description=_('Activate release updates (Errata updates are activated by default).'),
        long_description='',
        syntax=univention.admin.syntax.TrueFalseUp,
    ),
    'releaseVersion': univention.admin.property(
        short_description=_('Update to this UCS version'),
        long_description=_('Without specifying the most recent version will be used'),
        syntax=univention.admin.syntax.string,
    ),

}, **dict([
    requiredObjectClassesProperty(),
    prohibitedObjectClassesProperty(),
    fixedAttributesProperty(syntax=releaseFixedAttributes),
    emptyAttributesProperty(syntax=releaseFixedAttributes),
    ldapFilterProperty(),
]))

layout = [
    Tab(_('General'), _('Automatic updates'), layout=[
        Group(_('General automatic updates settings'), layout=[
            'name',
            'activate',
            'releaseVersion',
        ]),
    ]),
    policy_object_tab(),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('releaseVersion', 'univentionUpdateVersion', None, univention.admin.mapping.ListToString)
mapping.register('activate', 'univentionUpdateActivate', None, univention.admin.mapping.ListToString)
register_policy_mapping(mapping)


class object(univention.admin.handlers.simplePolicy):
    module = module


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
