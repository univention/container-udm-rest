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

"""|UDM| module for the Managed Node packages policies"""

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


class memberPackagesFixedAttributes(univention.admin.syntax.select):
    name = 'memberPackagesFixedAttributes'
    choices = [
        ('univentionMemberPackages', _('Package installation list')),
        ('univentionMemberPackagesRemove', _('Package removal list')),
    ]


module = 'policies/memberpackages'
operations = ['add', 'edit', 'remove', 'search']

policy_oc = 'univentionPolicyPackagesMember'
policy_apply_to = ["computers/memberserver"]
policy_position_dn_prefix = "cn=packages,cn=update"

childs = False
short_description = _('Policy: Packages for Managed Nodes')
object_name = _('Managed Node packages policy')
object_name_plural = _('Managed Node packages policies')
policy_short_description = _('Packages for Managed Nodes')
long_description = ''
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionPolicy', 'univentionPolicyPackagesMember'],
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
    'memberPackages': univention.admin.property(
        short_description=_('Package installation list'),
        long_description='',
        syntax=univention.admin.syntax.Packages,
        multivalue=True,
    ),
    'memberPackagesRemove': univention.admin.property(
        short_description=_('Package removal list'),
        long_description='',
        syntax=univention.admin.syntax.PackagesRemove,
        multivalue=True,
    ),

}, **dict([
    requiredObjectClassesProperty(),
    prohibitedObjectClassesProperty(),
    fixedAttributesProperty(syntax=memberPackagesFixedAttributes),
    emptyAttributesProperty(syntax=memberPackagesFixedAttributes),
    ldapFilterProperty(),
]))

layout = [
    Tab(_('General'), policy_short_description, layout=[
        Group(_('General Managed Node packages settings'), layout=[
            'name',
            'memberPackages',
            'memberPackagesRemove',
        ]),
    ]),
    policy_object_tab(),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('memberPackages', 'univentionMemberPackages')
mapping.register('memberPackagesRemove', 'univentionMemberPackagesRemove')
register_policy_mapping(mapping)


class object(univention.admin.handlers.simplePolicy):
    module = module


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
