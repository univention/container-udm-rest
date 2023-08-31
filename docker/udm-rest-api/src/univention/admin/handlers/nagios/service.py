#!/usr/bin/python3
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

"""|UDM| module for nagios services"""

import re
from typing import List  # noqa: F401

import ldap
from ldap.filter import filter_format

import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.syntax
import univention.admin.uexceptions
import univention.debug as ud
from univention.admin import configRegistry
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.nagios')
_ = translation.translate

module = 'nagios/service'
default_containers = ['cn=nagios']

childs = False
short_description = _('Nagios service')
object_name = _('Nagios service')
object_name_plural = _('Nagios services')
long_description = ''
operations = ['search', 'edit', 'add', 'remove']


class NagiosTimePeriod(univention.admin.syntax.UDM_Attribute):
    udm_module = 'nagios/timeperiod'
    attribute = 'name'


options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionNagiosServiceClass'],
    ),
}

property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description=_('Service name'),
        syntax=univention.admin.syntax.string_numbers_letters_dots,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'description': univention.admin.property(
        short_description=_('Description'),
        long_description=_('Service description'),
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
    ),
    'checkCommand': univention.admin.property(
        short_description=_('Plugin command'),
        long_description=_('Command name of Nagios plugin'),
        syntax=univention.admin.syntax.string,
        required=True,
    ),
    'checkArgs': univention.admin.property(
        short_description=_('Plugin command arguments'),
        long_description=_('Arguments of used Nagios plugin'),
        syntax=univention.admin.syntax.string,
    ),
    'useNRPE': univention.admin.property(
        short_description=_('Use NRPE'),
        long_description=_('Use NRPE to check remote services'),
        syntax=univention.admin.syntax.boolean,
    ),
    'checkPeriod': univention.admin.property(
        short_description=_('Check period'),
        long_description=_('Check services within check period'),
        syntax=getattr(univention.admin.syntax, 'NagiosTimePeriod', NagiosTimePeriod),
        required=True,
    ),
    'maxCheckAttempts': univention.admin.property(
        short_description=_('Maximum number of check attempts'),
        long_description=_('Maximum number of check attempts with non-OK-result until contact will be notified'),
        syntax=univention.admin.syntax.integer,
        required=True,
        default='10',
        size='One',
    ),
    'normalCheckInterval': univention.admin.property(
        short_description=_('Check interval'),
        long_description=_('Interval between checks'),
        syntax=univention.admin.syntax.integer,
        required=True,
        default='10',
        size='One',
    ),
    'retryCheckInterval': univention.admin.property(
        short_description=_('Retry check interval'),
        long_description=_('Interval between re-checks if service is in non-OK-state'),
        syntax=univention.admin.syntax.integer,
        required=True,
        default='1',
        size='One',
    ),
    'notificationInterval': univention.admin.property(
        short_description=_('Notification interval'),
        long_description=_('Interval between notifications'),
        syntax=univention.admin.syntax.integer,
        required=True,
        default='180',
        size='One',
    ),
    'notificationPeriod': univention.admin.property(
        short_description=_('Notification period'),
        long_description=_('Send notifications during this period'),
        syntax=getattr(univention.admin.syntax, 'NagiosTimePeriod', NagiosTimePeriod),
        required=True,
    ),
    'notificationOptionWarning': univention.admin.property(
        short_description=_('Notify if service state changes to WARNING'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
        default='1',
    ),
    'notificationOptionCritical': univention.admin.property(
        short_description=_('Notify if service state changes to CRITICAL'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
        default='1',
    ),
    'notificationOptionUnreachable': univention.admin.property(
        short_description=_('Notify if service state changes to UNREACHABLE'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
        default='1',
    ),
    'notificationOptionRecovered': univention.admin.property(
        short_description=_('Notify if service state changes to RECOVERED'),
        long_description='',
        syntax=univention.admin.syntax.boolean,
        default='1',
    ),
    'assignedHosts': univention.admin.property(
        short_description=_('Assigned hosts'),
        long_description=_('Check services on these hosts'),
        syntax=univention.admin.syntax.nagiosHostsEnabledDn,
        multivalue=True,
    ),
}


layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('General Nagios service settings'), layout=[
            ["name", "description"],
            ["checkCommand", "checkArgs"],
            "useNRPE",
        ]),
    ]),
    Tab(_('Interval'), _('Check settings'), advanced=True, layout=[
        ["normalCheckInterval", "retryCheckInterval"],
        ["maxCheckAttempts", "checkPeriod"],
    ]),
    Tab(_('Notification'), _('Notification settings'), advanced=True, layout=[
        ["notificationInterval", "notificationPeriod"],
        "notificationOptionWarning",
        "notificationOptionCritical",
        "notificationOptionUnreachable",
        "notificationOptionRecovered",
    ]),
    Tab(_('Hosts'), _('Assigned hosts'), layout=[
        Group(_('Assigned hosts'), layout=[
            "assignedHosts",
        ]),
    ]),
]


mapping = univention.admin.mapping.mapping()

mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
mapping.register('checkCommand', 'univentionNagiosCheckCommand', None, univention.admin.mapping.ListToString)
mapping.register('checkArgs', 'univentionNagiosCheckArgs', None, univention.admin.mapping.ListToString)
mapping.register('useNRPE', 'univentionNagiosUseNRPE', None, univention.admin.mapping.ListToString)

mapping.register('normalCheckInterval', 'univentionNagiosNormalCheckInterval', None, univention.admin.mapping.ListToString)
mapping.register('retryCheckInterval', 'univentionNagiosRetryCheckInterval', None, univention.admin.mapping.ListToString)
mapping.register('maxCheckAttempts', 'univentionNagiosMaxCheckAttempts', None, univention.admin.mapping.ListToString)
mapping.register('checkPeriod', 'univentionNagiosCheckPeriod', None, univention.admin.mapping.ListToString)

mapping.register('notificationInterval', 'univentionNagiosNotificationInterval', None, univention.admin.mapping.ListToString)
mapping.register('notificationPeriod', 'univentionNagiosNotificationPeriod', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
    module = module

    OPTION_BITS = {
        'notificationOptionWarning': b'w',
        'notificationOptionCritical': b'c',
        'notificationOptionUnreachable': b'u',
        'notificationOptionRecovered': b'r',
    }

    def _post_unmap(self, info, values):
        value = values.get('univentionNagiosNotificationOptions', [b''])[0]
        if value:
            options = value.split(b',')  # type: List[bytes]
            for key, value in self.OPTION_BITS.items():
                info[key] = '1' if value in options else '0'

        return info

    def open(self):
        super(object, self).open()
        _re = re.compile(r'^([^.]+)\.(.+?)$')
        # convert host FQDN to host DN
        hostlist = []
        hosts = self.oldattr.get('univentionNagiosHostname', [])
        for host in [x.decode('UTF-8') for x in hosts]:
            # split into relDomainName and zoneName
            if host and _re.match(host) is not None:
                (relDomainName, zoneName) = _re.match(host).groups()
                # find correct dNSZone entry
                res = self.lo.search(filter=filter_format('(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=%s)(aRecord=*))', (zoneName, relDomainName)))
                if not res:
                    ud.debug(ud.ADMIN, ud.INFO, 'service.py: open: could not find dNSZone of %s' % (host,))
                else:
                    # found dNSZone
                    filter = '(&(objectClass=univentionHost)'
                    for aRecord in [x.decode('ASCII') for x in res[0][1]['aRecord']]:
                        filter += filter_format('(aRecord=%s)', [aRecord])
                    filter += filter_format('(cn=%s))', [relDomainName])

                    # find dn of host that is related to given aRecords
                    res = self.lo.search(filter=filter)
                    if res:
                        hostlist.append(res[0][0])  # type: List[str]

        self['assignedHosts'] = hostlist

        self.save()

    def _ldap_modlist(self):
        ml = univention.admin.handlers.simpleLdap._ldap_modlist(self)

        options = []
        for key, value in self.OPTION_BITS.items():
            if self[key] == '1':
                options.append(value)  # type: List[bytes]

        # univentionNagiosNotificationOptions is required in LDAP schema
        if not options:
            options.append(b'n')

        newoptions = b','.join(options)
        ml.append(('univentionNagiosNotificationOptions', self.oldattr.get('univentionNagiosNotificationOptions', []), newoptions))

        # save assigned hosts
        if self.hasChanged('assignedHosts'):
            hostlist = []
            for hostdn in self.info.get('assignedHosts', []):
                try:
                    host = self.lo.get(hostdn, ['associatedDomain', 'cn'], required=True)
                    cn = host['cn'][0]  # type: bytes
                except (univention.admin.uexceptions.noObject, ldap.NO_SUCH_OBJECT):
                    raise univention.admin.uexceptions.valueError(_('The host "%s" does not exists.') % (hostdn,), property='assignedHosts')
                except KeyError:
                    raise univention.admin.uexceptions.valueError(_('The host "%s" is invalid, it has no "cn" attribute.') % (hostdn,), property='assignedHosts')

                domain = host.get('associatedDomain', [configRegistry.get("domainname").encode('ASCII')])[0]  # type: bytes
                hostlist.append(b"%s.%s" % (cn, domain))

            ml.insert(0, ('univentionNagiosHostname', self.oldattr.get('univentionNagiosHostname', []), hostlist))

        return ml


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
