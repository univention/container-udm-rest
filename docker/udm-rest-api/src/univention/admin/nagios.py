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

"""|UDM| methods and defines for Nagios related attributes."""

import copy
import re

from ldap.filter import filter_format

import univention.admin
import univention.admin.localization
import univention.admin.syntax
import univention.debug as ud
from univention.admin import configRegistry
from univention.admin.layout import Tab


translation = univention.admin.localization.translation('univention.admin')
_ = translation.translate


nagios_properties = {
    'nagiosContactEmail': univention.admin.property(
        short_description=_('Email address of Nagios contacts'),
        long_description='',
        syntax=univention.admin.syntax.emailAddress,
        multivalue=True,
        options=['nagios'],
    ),
    'nagiosParents': univention.admin.property(
        short_description=_('Parent hosts'),
        long_description='',
        syntax=univention.admin.syntax.nagiosHostsEnabledDn,
        multivalue=True,
        options=['nagios'],
    ),
    'nagiosServices': univention.admin.property(
        short_description=_('Assigned Nagios services'),
        long_description='',
        syntax=univention.admin.syntax.nagiosServiceDn,
        multivalue=True,
        options=['nagios'],
    ),
}


nagios_tab_A = Tab(_('Nagios services'), _('Nagios Service Settings'), advanced=True, layout=[
    "nagiosServices",
])

nagios_tab_B = Tab(_('Nagios notification'), _('Nagios Notification Settings'), advanced=True, layout=[
    "nagiosContactEmail",
    "nagiosParents",
])


nagios_mapping = [
    ['nagiosContactEmail', 'univentionNagiosEmail', None, None],
]


nagios_options = {
    'nagios': univention.admin.option(
        short_description=_('Nagios support'),
        default=0,
        editable=True,
        objectClasses=['univentionNagiosHostClass'],
    ),
}


def addPropertiesMappingOptionsAndLayout(new_property, new_mapping, new_options, new_layout):
    """Add Nagios properties."""
    # FIXME: property_descriptions is not changed atomically during module initialization
    for key, value in nagios_properties.items():
        new_property[key] = value

    # append tab with Nagios options
    new_layout.append(nagios_tab_A)
    new_layout.append(nagios_tab_B)

    # append nagios attribute mapping
    for (ucskey, ldapkey, mapto, mapfrom) in nagios_mapping:
        new_mapping.register(ucskey, ldapkey, mapto, mapfrom)

    for key, value in nagios_options.items():
        new_options[key] = value


class Support(object):

    def __init__(self):
        self.nagiosRemoveFromServices = False

    def __getFQDN(self):
        hostname = self.oldattr.get("cn", [b''])[0].decode('UTF-8')
        domain = self.oldattr.get("associatedDomain", [b''])[0].decode('UTF-8')
        if not domain:
            domain = configRegistry.get("domainname", None)
        if domain and hostname:
            return hostname + "." + domain

        return None

    def nagiosGetAssignedServices(self):
        fqdn = self.__getFQDN()

        if fqdn:
            return self.lo.searchDn(filter=filter_format('(&(objectClass=univentionNagiosServiceClass)(univentionNagiosHostname=%s))', [fqdn]), base=self.position.getDomain())
        return []

    def nagiosGetParentHosts(self):
        # univentionNagiosParent
        _re = re.compile(r'^([^.]+)\.(.+?)$')

        parentlist = []
        parents = self.oldattr.get('univentionNagiosParent', [])
        for parent in [x.decode('UTF-8') for x in parents]:
            if parent and _re.match(parent) is not None:
                (relDomainName, zoneName) = _re.match(parent).groups()

                res = self.lo.search(filter_format('(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=%s)(aRecord=*))', (zoneName, relDomainName)))
                if not res:
                    ud.debug(ud.ADMIN, ud.INFO, "nagios.py: NGPH: couldn't find dNSZone of %s" % parent)
                else:
                    # found dNSZone
                    filter = '(&(objectClass=univentionHost)'
                    for aRecord in res[0][1]['aRecord']:
                        filter += filter_format('(aRecord=%s)', [aRecord.decode('ASCII')])
                    filter += filter_format('(cn=%s))', [relDomainName])
                    res = self.lo.searchDn(filter)
                    if res:
                        parentlist.append(res[0])

        return parentlist

    def nagios_open(self):
        if 'nagios' in self.options:
            self['nagiosServices'] = self.nagiosGetAssignedServices()
            self['nagiosParents'] = self.nagiosGetParentHosts()

    def nagiosSaveParentHostList(self, ml):
        if self.hasChanged('nagiosParents'):
            parentlist = []
            for parentdn in self.info.get('nagiosParents', []):
                domain = self.lo.getAttr(parentdn, 'associatedDomain')
                cn = self.lo.getAttr(parentdn, 'cn')
                if not domain:
                    domain = [configRegistry["domainname"].encode('UTF-8')]
                if cn and domain:
                    parentlist.append(b'.'.join((cn[0], domain[0])))
            ml.insert(0, ('univentionNagiosParent', self.oldattr.get('univentionNagiosParent', []), parentlist))

    def nagios_ldap_modlist(self, ml):
        if 'nagios' in self.options:
            if ('ip' not in self.info) or (not self.info['ip']) or (len(self.info['ip']) == 1 and self.info['ip'][0] == ''):
                raise univention.admin.uexceptions.nagiosARecordRequired()
            if not self.info.get('domain', None):
                if ('dnsEntryZoneForward' not in self.info) or (not self.info['dnsEntryZoneForward']) or (len(self.info['dnsEntryZoneForward']) == 1 and self.info['dnsEntryZoneForward'][0] == ''):
                    raise univention.admin.uexceptions.nagiosDNSForwardZoneEntryRequired()

        # add nagios option
        if self.option_toggled('nagios') and 'nagios' in self.options:
            ud.debug(ud.ADMIN, ud.INFO, 'added nagios option')
            if b'univentionNagiosHostClass' not in self.oldattr.get('objectClass', []):
                ml.insert(0, ('univentionNagiosEnabled', b'', b'1'))

        # remove nagios option
        if self.option_toggled('nagios') and 'nagios' not in self.options:
            ud.debug(ud.ADMIN, ud.INFO, 'remove nagios option')
            for key in ['univentionNagiosParent', 'univentionNagiosEmail', 'univentionNagiosEnabled']:
                if self.oldattr.get(key, []):
                    ml.insert(0, (key, self.oldattr.get(key, []), b''))

            # trigger deletion from services
            self.nagiosRemoveFromServices = True

        if 'nagios' in self.options:
            self.nagiosSaveParentHostList(ml)

    def nagios_ldap_pre_modify(self):
        pass

    def nagios_ldap_pre_create(self):
        pass

    def __change_fqdn(self, oldfqdn, newfqdn):
        oldfqdn = oldfqdn.encode('utf-8')
        newfqdn = newfqdn.encode('utf-8')
        for servicedn in self.oldinfo['nagiosServices']:
            oldmembers = self.lo.getAttr(servicedn, 'univentionNagiosHostname')
            if oldfqdn in oldmembers:
                newmembers = copy.deepcopy(oldmembers)
                newmembers.remove(oldfqdn)
                newmembers.append(newfqdn)
                self.lo.modify(servicedn, [('univentionNagiosHostname', oldmembers, newmembers)])  # TODO: why not simply ('univentionNagiosHostname', oldfqdn, newfqdn) ?

    def nagiosModifyServiceList(self):
        fqdn = ''

        if 'nagios' in self.old_options:
            if self.hasChanged('name') and self.hasChanged('domain'):
                oldfqdn = u'%s.%s' % (self.oldinfo['name'], self.oldinfo['domain'])
                newfqdn = u'%s.%s' % (self['name'], self['domain'])
                self.__change_fqdn(oldfqdn, newfqdn)
            elif self.hasChanged('name'):
                oldfqdn = u'%s.%s' % (self.oldinfo['name'], self['domain'])
                newfqdn = u'%s.%s' % (self['name'], self['domain'])
                self.__change_fqdn(oldfqdn, newfqdn)
            elif self.hasChanged('domain'):
                oldfqdn = u'%s.%s' % (self.oldinfo['name'], self.oldinfo['domain'])
                newfqdn = u'%s.%s' % (self['name'], self['domain'])
                self.__change_fqdn(oldfqdn, newfqdn)

        fqdn = '%s.%s' % (self['name'], configRegistry.get("domainname"))
        if self.has_property('domain') and self['domain']:
            fqdn = '%s.%s' % (self['name'], self['domain'])

        # remove host from services
        if 'nagios' in self.old_options:
            for servicedn in self.oldinfo.get('nagiosServices', []):
                if servicedn not in self.info.get('nagiosServices', []):
                    oldmembers = self.lo.getAttr(servicedn, 'univentionNagiosHostname')
                    newmembers = [x for x in oldmembers if x.decode('UTF-8').lower() != fqdn.lower()]
                    self.lo.modify(servicedn, [('univentionNagiosHostname', oldmembers, newmembers)])

        if 'nagios' in self.options:
            # add host to new services
            ud.debug(ud.ADMIN, ud.INFO, 'nagios.py: NMSL: nagios in options')
            for servicedn in self.info.get('nagiosServices', []):
                if not servicedn:
                    continue
                ud.debug(ud.ADMIN, ud.INFO, 'nagios.py: NMSL: servicedn %s' % servicedn)
                if 'nagios' not in self.old_options or servicedn not in self.oldinfo['nagiosServices']:
                    ud.debug(ud.ADMIN, ud.INFO, 'nagios.py: NMSL: add')
                    # option nagios was freshly enabled or service has been enabled just now
                    oldmembers = self.lo.getAttr(servicedn, 'univentionNagiosHostname')
                    newmembers = copy.deepcopy(oldmembers)
                    newmembers.append(fqdn.encode('UTF-8'))
                    ud.debug(ud.ADMIN, ud.WARN, 'nagios.py: NMSL: oldmembers: %s' % oldmembers)
                    ud.debug(ud.ADMIN, ud.WARN, 'nagios.py: NMSL: newmembers: %s' % newmembers)
                    self.lo.modify(servicedn, [('univentionNagiosHostname', oldmembers, newmembers)])

    def nagiosRemoveHostFromServices(self):
        self.nagiosRemoveFromServices = False
        fqdn = self.__getFQDN()

        if fqdn:
            searchResult = self.lo.search(
                filter=filter_format('(&(objectClass=univentionNagiosServiceClass)(univentionNagiosHostname=%s))', [fqdn]),
                base=self.position.getDomain(), attr=['univentionNagiosHostname'])

            for (dn, attrs) in searchResult:
                newattrs = [x for x in attrs['univentionNagiosHostname'] if x.decode('UTF-8').lower() != fqdn.lower()]
                self.lo.modify(dn, [('univentionNagiosHostname', attrs['univentionNagiosHostname'], newattrs)])

    def nagiosRemoveHostFromParent(self):
        self.nagiosRemoveFromParent = False

        fqdn = self.__getFQDN()

        if fqdn:
            searchResult = self.lo.search(
                filter=filter_format('(&(objectClass=univentionNagiosHostClass)(univentionNagiosParent=%s))', [fqdn]),
                base=self.position.getDomain(), attr=['univentionNagiosParent'])

            for (dn, attrs) in searchResult:
                newattrs = [x for x in attrs['univentionNagiosParent'] if x.decode('UTF-8').lower() != fqdn.lower()]
                self.lo.modify(dn, [('univentionNagiosParent', attrs['univentionNagiosParent'], newattrs)])

    def nagios_ldap_post_modify(self):
        if self.nagiosRemoveFromServices:
            # nagios support has been disabled
            self.nagiosRemoveHostFromServices()
            self.nagiosRemoveHostFromParent()
        else:
            # modify service objects if needed
            if 'nagios' in self.options:
                self.nagiosModifyServiceList()

    def nagios_ldap_post_create(self):
        if 'nagios' in self.options:
            self.nagiosModifyServiceList()

    def nagios_ldap_post_remove(self):
        self.nagiosRemoveHostFromServices()
        self.nagiosRemoveHostFromParent()

    def nagios_cleanup(self):
        self.nagiosRemoveHostFromServices()
        self.nagiosRemoveHostFromParent()
