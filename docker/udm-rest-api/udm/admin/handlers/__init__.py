#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2004-2024 Univention GmbH
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

"""
This module is the base for all Univention Directory Management handler modules.
A UDM handler represents an abstraction of an LDAP object.

.. seealso:: :mod:`univention.admin.uldap`
.. seealso:: :mod:`univention.admin.modules`
.. seealso:: :mod:`univention.admin.objects`
.. seealso:: :mod:`univention.admin.mapping`
.. seealso:: :mod:`univention.admin.syntax`
.. seealso:: :mod:`univention.admin.uexceptions`
"""


import copy
import inspect
import re
import sys
import time
from collections.abc import Iterable
from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network
from logging import getLogger
from typing import TYPE_CHECKING, Any, Self, overload

import ldap
from ldap.controls.readentry import PostReadControl
from ldap.dn import dn2str, escape_dn_chars, explode_rdn, str2dn
from ldap.filter import filter_format

import univention.admin.allocators
import univention.admin.blocklist
import univention.admin.filter
import univention.admin.localization
import univention.admin.mapping
import univention.admin.modules
import univention.admin.syntax
import univention.admin.uexceptions
import univention.admin.uldap
from univention.admin import configRegistry
from univention.admin.uldap import DN
from univention.admindiary.client import write_event
from univention.admindiary.events import DiaryEvent


if TYPE_CHECKING:
    import univention.admin.handlers.dns.forward_zone
    import univention.admin.handlers.dns.reverse_zone
    import univention.admin.handlers.networks.network

try:
    from typing import Literal
    _HookName = Literal[
        "hook_open",
        "hook_ldap_pre_create",
        "hook_ldap_addlist",
        "hook_ldap_post_create",
        "hook_ldap_pre_modify",
        "hook_ldap_modlist",
        "hook_ldap_post_modify",
        "hook_ldap_pre_remove",
        "hook_ldap_post_remove",
    ]
except ImportError:
    pass


log = getLogger('ADMIN')

try:
    import univention.lib.admember
    _prevent_to_change_ad_properties = univention.lib.admember.is_localhost_in_admember_mode()
except ImportError:
    log.warning("Failed to import univention.lib.admember")
    _prevent_to_change_ad_properties = False

_Attributes = dict[str, list[bytes]]
_Properties = dict[str, str | list[str]]
_Encoding = tuple[str, ...]

translation = univention.admin.localization.translation('univention/admin/handlers')
_ = translation.translate

# global caching variable
if configRegistry.is_true('directory/manager/samba3/legacy', False):
    s4connector_present: bool | None = False
elif configRegistry.is_false('directory/manager/samba3/legacy', False):
    s4connector_present = True
else:
    s4connector_present = None


def disable_ad_restrictions(disable: bool = True) -> None:
    global _prevent_to_change_ad_properties
    _prevent_to_change_ad_properties = disable


class simpleLdap:
    """
    The base class for all UDM handler modules.

    :param co:
    *deprecated* parameter for a config. Please pass `None`.

    :param lo:
    A required LDAP connection object which is used for all LDAP operations (search, create, modify).
    It should be bound to a user which has the LDAP permissions to do the required operations.

    :param position:
    The LDAP container where a new object should be created in, or `None` for existing objects.

    :param dn:
    The DN of an existing LDAP object. If a object should be created the DN must not be passed here!

    :param superordinate:
    The superordinate object of this object. Can be omitted. It is automatically searched by the given DN or position.

    :param attributes:
    The LDAP attributes of the LDAP object as dict. This should by default be omitted. To save performance when an LDAP search is done this can be used, e.g. by the lookup() method.
    If given make sure the dict contains all attributes which are required by :meth:`_ldap_attributes`.

    The following attributes hold information about the state of this object:

    :ivar str dn:
    A LDAP distinguished name (DN) of this object (if exists, otherwise None)
    :ivar str module: the UDM handlers name (e.g. users/user)
    :ivar dict oldattr:
    The LDAP attributes of this object as dict. If the object does not exists the dict is empty.
    :ivar dict info:
    A internal dictionary which holds the values for every property.
    :ivar list options:
    A list of UDM options which are enabled on this object. Enabling options causes specific object classes and attributes to be added to the object.
    :ivar list policies:
    A list of DNs containing references to assigned policies.
    :ivar dict properties: a dict which maps all UDM properties to :class:`univention.admin.property` instances.
    :ivar univention.admin.mapping.mapping mapping:
    A :class:`univention.admin.mapping.mapping` instance containing a mapping of UDM property names to LDAP attribute names.
    :ivar dict oldinfo:
    A private copy of :attr:`info` containing the original properties which were set during object loading. This is only set by :func:`univention.admin.handlers.simpleLdap.save`.
    :ivar list old_options:
    A private copy of :attr:`options` containing the original options which were set during object loading. This is only set by :func:`univention.admin.handlers.simpleLdap.save`.
    :ivar list oldpolicies:
    A private copy of :attr:`policies` containing the original policies which were set during object loading. This is only set by :func:`univention.admin.handlers.simpleLdap.save`.

    .. caution::
    Do not operate on :attr:`info` directly because this would bypass syntax validations. This object should be used like a dict.
    Properties should be assigned in the following way: obj['name'] = 'value'
    """

    module = ''  # the name of the module
    use_performant_ldap_search_filter = False
    ldap_base = configRegistry['ldap/base']
    _lo_machine_primary = None
    default_containers_attribute_name = None

    def __init__(
        self,
        co: None,
        lo: univention.admin.uldap.access,
        position: univention.admin.uldap.position | None,
        dn: str = '',
        superordinate: Self | None = None,
        attributes: _Attributes | None = None,
    ) -> None:
        self._exists = False
        self.co = None
        if isinstance(lo, univention.admin.uldap.access):
            self.lo: univention.admin.uldap.access = lo
        elif isinstance(lo, univention.uldap.access):
            log.error('using univention.uldap.access instance is deprecated. Use univention.admin.uldap.access instead.')
            self.lo = univention.admin.uldap.access(lo=lo)
        else:
            raise TypeError('lo must be instance of univention.admin.uldap.access.')

        self.dn: str | None = dn.decode('utf-8') if isinstance(dn, bytes) else dn
        self.old_dn: str | None = self.dn
        self.superordinate: simpleLdap | None = superordinate

        self.set_defaults = not self.dn  # this object is newly created and so we can use the default values

        self.position: univention.admin.uldap.position = position or univention.admin.uldap.position(self.ldap_base)
        if not position and self.dn:
            self.position.setDn(self.dn)
        self.info: _Properties = {}
        self.oldinfo: _Properties = {}
        self.policies: list[str] = []
        self.oldpolicies: list[str] = []
        self.policyObjects: dict[str, simplePolicy] = {}
        self.__no_default: list[str] = []

        self._open = False
        self.options: list[str] = []
        self.old_options: list[str] = []
        self.alloc: list[tuple[str, str] | tuple[str, str, bool]] = []  # name,value,updateLastUsedValue

        # s4connector_present is a global caching variable than can be
        # None ==> ldap has not been checked for servers with service "S4 Connector"
        # True ==> at least one server with IP address (aRecord) is present
        # False ==> no server is present
        global s4connector_present
        if s4connector_present is None:
            s4connector_present = False
            searchResult = self.lo.searchDn('(&(|(objectClass=univentionDomainController)(objectClass=univentionMemberServer))(univentionService=S4 Connector)(|(aRecord=*)(aAAARecord=*)))')
            s4connector_present = bool(searchResult)
        self.s4connector_present = s4connector_present

        if not univention.admin.modules.modules:
            log.warning('univention.admin.modules.update() was not called')
            univention.admin.modules.update()

        m = univention.admin.modules._get(self.module)
        if not hasattr(self, 'mapping'):
            self.mapping: univention.admin.mapping.mapping | None = getattr(m, 'mapping', None)

        self.oldattr: _Attributes = {}
        if attributes:
            self.oldattr = attributes
        elif self.dn:
            try:
                attr = self._ldap_attributes()
                self.oldattr = self.lo.get(self.dn, attr=attr, required=True)
            except ldap.NO_SUCH_OBJECT:
                raise univention.admin.uexceptions.noObject(self.dn)

        if self.oldattr:
            self._exists = True
            if not univention.admin.modules.virtual(self.module) and not univention.admin.modules.recognize(self.module, self.dn, self.oldattr):
                raise univention.admin.uexceptions.wrongObjectType('%s is not recognized as %s.' % (self.dn, self.module))
            oldinfo = self.mapping.unmapValues(self.oldattr)
            oldinfo = self._post_unmap(oldinfo, self.oldattr)
            oldinfo = self._falsy_boolean_extended_attributes(oldinfo)
            self.info.update(oldinfo)

        self.policies = [x.decode('utf-8') for x in self.oldattr.get('univentionPolicyReference', [])]
        self.__set_options()
        self.save()

        self._validate_superordinate(False)

    def set_lo_machine_primary(self, lo: univention.admin.uldap.access) -> None:
        self._lo_machine_primary = lo

    @property
    def lo_machine_primary(self) -> univention.admin.uldap.access:
        try:  # maybe check if we have long lived connections which are invalidated?!
            if self._lo_machine_primary is not None and not self._lo_machine_primary.whoami():
                raise univention.admin.uexceptions.base('invalid LDAP connection lo_machine_primary')
        except (ldap.LDAPError, univention.admin.uexceptions.base, AttributeError):
            self._lo_machine_primary = None
        if self._lo_machine_primary is None:
            try:
                simpleLdap._lo_machine_primary = univention.admin.uldap.getMachineConnection(ldap_master=True)[0]
            except OSError:
                # This is for joining UCS systems into the domain.
                # During join the joining system calls udm-cli via ssh on the primary
                # as, usally, domain admin. This account does not have read permission for machine.secret
                # so we use the user connection instead.
                # Problems:
                # * the join user (if not domain admins group) has no read permissions for blocklist, so he can bypass the blocklist check
                # * any other user with permissions to create user objects (connector's?) but without permissions to read
                #   blocklists can bypass the blocklist check with udm-cli
                self._lo_machine_primary = self.lo
        return self._lo_machine_primary

    @property
    def descriptions(self) -> dict[str, univention.admin.property]:
        return univention.admin.modules.get(self.module).property_descriptions

    @property
    def entry_uuid(self) -> str | None:
        """The entry UUID of the object (if object exists)"""
        if 'entryUUID' in self.oldattr:
            return self.oldattr['entryUUID'][0].decode('ASCII')

    def save(self) -> None:
        """
        Saves the current internal object state as old state for later comparison when e.g. modifying this object.

        .. seealso:: This method should be called by :func:`univention.admin.handlers.simpleLdap.open` and after further modifications in modify() / create().

        .. note:: self.oldattr is not set and must be set manually
        """
        self.oldinfo = copy.deepcopy(self.info)
        self.old_dn = self.dn
        self.oldpolicies = copy.deepcopy(self.policies)
        self.options = list(set(self.options))
        self.old_options = []
        if self.exists():
            self.old_options = copy.deepcopy(self.options)

    def diff(self) -> list[tuple[str, Any, Any]]:
        """
        Returns the difference between old and current state as a UDM modlist.

        :returns: A list of 3-tuples (udm-property-name, old-property-value, new-property-values).
        """
        changes: list[tuple[str, Any, Any]] = []

        for key, prop in self.descriptions.items():
            null: list | None = [] if prop.multivalue else None
            # remove properties which are disabled by options
            if prop.options and not set(prop.options) & set(self.options):
                if self.oldinfo.get(key, null) not in (null, None):
                    log.debug("simpleLdap.diff: key %s not valid (option not set)", key)
                    changes.append((key, self.oldinfo[key], null))
                continue
            if (self.oldinfo.get(key) or self.info.get(key)) and self.oldinfo.get(key, null) != self.info.get(key, null):
                changes.append((key, self.oldinfo.get(key, null), self.info.get(key, null)))

        return changes

    def hasChanged(self, key: str | Iterable[str]) -> bool:
        """
        Checks if the given attribute(s) was (were) changed.

        :param key: The name of a property.
        :returns: True if the property changed, False otherwise.
        """
        # FIXME: key can even be nested
        if not isinstance(key, str):
            return any(self.hasChanged(i) for i in key)
        if (not self.oldinfo.get(key, '') or self.oldinfo[key] == ['']) and (not self.info.get(key, '') or self.info[key] == ['']):
            return False

        return not univention.admin.mapping.mapCmp(self.mapping, key, self.oldinfo.get(key, ''), self.info.get(key, ''))

    def ready(self) -> None:
        """
        Makes sure all preconditions are met before creating or modifying this object.

        It checks if all properties marked required are set.
        It checks if the superordinate is valid.

        :raises: :class:`univention.admin.uexceptions.insufficientInformation`
        """
        missing = []
        for name, p in self.descriptions.items():
            # skip if this property is not present in the current option set
            if p.options and not set(p.options) & set(self.options):
                continue

            if p.required and (not self[name] or (isinstance(self[name], list) and self[name] == [''])):
                log.debug("property %s is required but not set.", name)
                missing.append(name)
        if missing:
            raise univention.admin.uexceptions.insufficientInformation(_('The following properties are missing:\n%s') % ('\n'.join(missing),), missing_properties=missing)

        # when creating a object make sure that its position is underneath of its superordinate
        if not self.exists() and self.position and self.superordinate and not self._ensure_dn_in_subtree(self.superordinate.dn, self.position.getDn()):
            raise univention.admin.uexceptions.insufficientInformation(_('The position must be in the subtree of the superordinate.'))

        self._validate_superordinate(True)

    def has_property(self, key: str) -> bool:
        """
        Checks if the property exists in this module and if it is enabled in the set UDM options.

        :param str key: The name of a property.
        :returns: True if the property exists and is enabled, False otherwise.
        """
        try:
            p = self.descriptions[key]
        except KeyError:
            return False
        if p.options:
            return bool(set(p.options) & set(self.options))
        return True

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets or unsets the property to the given value.

        :param str key: The name of a property.
        :param value: The value to set.

        :raises KeyError: if the property belongs to an option, which is currently not enabled.
        :raises: :class:`univention.admin.uexceptions.noProperty` or :class:`KeyError` if the property does not exists or is not enabled by the UDM options.
        :raises: :class:`univention.admin.uexceptions.valueRequired` if the value is unset but required.
        :raises: :class:`univention.admin.uexceptions.valueMayNotChange` if the values cannot be modified.
        :raises: :class:`univention.admin.uexceptions.valueInvalidSyntax` if the value is invalid.
        """
        def _changeable():
            yield self.descriptions[key].editable
            if not self.descriptions[key].may_change:
                yield key not in self.oldinfo or self.oldinfo[key] == value
            # if _prevent_to_change_ad_properties:  # FIXME: users.user.object.__init__ modifies firstname and lastname by hand
            #    yield not (self.descriptions[key].readonly_when_synced and self._is_synced_object() and self.exists())

        # property does not exist
        if not self.has_property(key):
            # don't set value if the option is not enabled
            log.warning('__setitem__: Ignoring property %s', key)
            try:
                self.descriptions[key]
            except KeyError:
                # raise univention.admin.uexceptions.noProperty(key)
                raise
            return
        # attribute may not be changed
        elif not all(_changeable()):
            raise univention.admin.uexceptions.valueMayNotChange(_('key=%(key)s old=%(old)s new=%(new)s') % {'key': key, 'old': self[key], 'new': value}, property=key)
        # required attribute may not be removed
        elif self.descriptions[key].required and not value:
            raise univention.admin.uexceptions.valueRequired(_('The property %s is required') % self.descriptions[key].short_description, property=key)
        # do nothing
        if self.info.get(key, None) == value:
            log.debug('values are identical: %s:%s', key, value)
            return

        if self.info.get(key, None) == self.descriptions[key].default(self):
            self.__no_default.append(key)

        if self.descriptions[key].multivalue:
            # make sure value is list
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                raise univention.admin.uexceptions.valueInvalidSyntax(_('The property %s must be a list') % (self.descriptions[key].short_description,), property=key)

            self.info[key] = []
            for v in value:
                if not v:
                    continue
                err = ""
                p = None
                try:
                    s = self.descriptions[key].syntax
                    p = s.parse(v)

                except univention.admin.uexceptions.valueError as emsg:
                    err = str(emsg)
                if not p:
                    if not err:
                        err = ""
                    try:
                        raise univention.admin.uexceptions.valueInvalidSyntax("%s: %s" % (key, err), property=key)
                    except UnicodeEncodeError:  # raise fails if err contains umlauts or other non-ASCII-characters
                        raise univention.admin.uexceptions.valueInvalidSyntax(self.descriptions[key].short_description, property=key)
                self.info[key].append(p)

        elif not value and key in self.info:
            del self.info[key]

        elif value:
            err = ""
            p = None
            try:
                s = self.descriptions[key].syntax
                p = s.parse(value)
            except univention.admin.uexceptions.valueError as e:
                err = str(e)
            if not p:
                if not err:
                    err = ""
                try:
                    raise univention.admin.uexceptions.valueInvalidSyntax("%s: %s" % (self.descriptions[key].short_description, err), property=key)
                except UnicodeEncodeError:  # raise fails if err contains umlauts or other non-ASCII-characters
                    raise univention.admin.uexceptions.valueInvalidSyntax("%s" % self.descriptions[key].short_description, property=key)
            self.info[key] = p

    def __getitem__(self, key: str) -> Any:
        """
        Get the currently set value of the given property.

        :param str key: The name of a property.
        :returns: The currently set value.  If the value is not set the default value is returned.

        .. warning:: this method changes the set value to the default if it is unset. For a side effect free retrieval of the value use :func:`univention.admin.handlers.simpleLdap.get`.
        """
        if not key:
            return None

        if key in self.info:
            if self.descriptions[key].multivalue and not isinstance(self.info[key], list):
                # why isn't this correct in the first place?
                log.warning('The mapping for %s in %s is broken!', key, self.module)
                self.info[key] = [self.info[key]]
            return self.info[key]
        elif key not in self.__no_default and self.descriptions[key].editable:
            self.info[key] = self.descriptions[key].default(self)
            return self.info[key]
        elif self.descriptions[key].multivalue:
            return []
        else:
            return None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the currently set value of the given property.

        :param str key: The name of a property.
        :param default: The default to return if the property is not set.
        :returns: The currently set value.  If the value is not set :attr:`default` is returned.
        """
        return self.info.get(key, default)

    def __contains__(self, key: str) -> bool:
        """
        Checks if the property exists in this module.

        :param key: The name of a property.
        :returns: True if the property exists, False otherwise.

        .. warning:: This does not check if the property is also enabled by the UDM options. Use :func:`univention.admin.handlers.simpleLdap.has_property` instead.
        """
        return key in self.descriptions

    def keys(self) -> Iterable[str]:
        """
        Returns the names of all properties this module has.

        :returns: The list of property names.
        """
        return self.descriptions.keys()

    def items(self) -> Iterable[tuple[str, Any]]:
        """
        Return all items which belong to the current options - even if they are empty.

        :returns: a list of 2-tuples (udm-property-name, property-value).

        .. warning:: In certain circumstances this sets the default value for every property (e.g. when having a new object).
        """
        return [(key, self[key]) for key in self.keys() if self.has_property(key)]

    def create(self, serverctrls: list[ldap.controls.LDAPControl] | None = None, response: dict[str, Any] | None = None, ignore_license: bool = False) -> str:
        """
        Creates the LDAP object if it does not exists by building the list of attributes (addlist) and write it to LDAP.
        If this call raises an exception it is necessary to instantiate a new object before trying to create it again.

        :raises: :class:`univention.admin.uexceptions.invalidOperation` if objects of this type do not support to be created.
        :raises: :class:`univention.admin.uexceptions.objectExists` if the object already exists.
        :raises: :class:`univention.admin.uexceptions.insufficientInformation`

        :param serverctrls: a list of :py:class:`ldap.controls.LDAPControl` instances sent to the server along with the LDAP request.
        :param dict response: An optional dictionary to receive the server controls of the result.
        :param ignore_license: If the license is exceeded the modification may fail. Setting this to True causes license checks to be disabled
        :returns: The DN of the created object.
        """
        if not univention.admin.modules.supports(self.module, 'add'):
            # if the licence is exceeded 'add' is removed from the modules operations. Blocklist objects may need to be added anyway.
            if not ignore_license:
                raise univention.admin.uexceptions.invalidOperation(_('Objects of the "%s" object type can not be created.') % (self.module,))

        if self.exists():
            raise univention.admin.uexceptions.objectExists(self.dn)

        if not isinstance(response, dict):
            response = {}

        try:
            self._ldap_pre_ready()
            self.ready()

            dn = self._create(response=response, serverctrls=serverctrls, ignore_license=ignore_license)
        except Exception:
            self._safe_cancel()
            raise

        for c in response.get('ctrls', []):
            if c.controlType == PostReadControl.controlType:
                self.oldattr.update({k: [v if isinstance(v, bytes) else v.encode('ISO8859-1') for v in val] for k, val in c.entry.items()})
        self._write_admin_diary_create()
        return dn

    def _get_admin_diary_event(self, event_name: str) -> DiaryEvent:
        name = self.module.replace('/', '_').upper()
        return DiaryEvent.get('UDM_%s_%s' % (name, event_name)) or DiaryEvent.get('UDM_GENERIC_%s' % event_name)

    def _get_admin_diary_args_names(self, event: DiaryEvent) -> list[str]:
        return [
            name
            for name in self.descriptions
            if name in event.args
        ]

    def _get_admin_diary_args(self, event: DiaryEvent) -> dict[str, Any]:
        args: dict[str, Any] = {'module': self.module}
        if event.name.startswith('UDM_GENERIC_'):
            value = self.dn
            for k, v in self.descriptions.items():
                if v.identifies:
                    value = self[k]
                    break
            args['id'] = value
        else:
            for name in self._get_admin_diary_args_names(event):
                args[name] = str(self[name])
        return args

    def _get_admin_diary_username(self) -> str:
        username = ldap.dn.explode_rdn(self.lo.binddn)[0]
        if username != 'cn=admin':
            username = username.rsplit('=', 1)[1]
        return username

    def _write_admin_diary_event(self, event: DiaryEvent, additional_args: dict[str, Any] | None = None) -> None:
        try:
            event = self._get_admin_diary_event(event)
            if not event:
                return
            args = self._get_admin_diary_args(event)
            if args:
                if additional_args:
                    args.update(additional_args)
                username = self._get_admin_diary_username()
                write_event(event, args, username=username)
        except Exception as exc:
            log.warning("Failed to write Admin Diary entry: %s", exc)

    def _write_admin_diary_create(self) -> None:
        self._write_admin_diary_event('CREATED')

    def modify(self, modify_childs: bool = True, ignore_license: bool = False, serverctrls: list[ldap.controls.LDAPControl] | None = None, response: dict[str, Any] | None = None) -> str:
        """
        Modifies the LDAP object by building the difference between the current state and the old state of this object and write this modlist to LDAP.

        :param modify_childs: Specifies if child objects should be modified as well.

        :param ignore_license: If the license is exceeded the modification may fail. Setting this to True causes license checks to be disabled

        :raises: :class:`univention.admin.uexceptions.invalidOperation` if objects of this type do not support to be modified.

        :raises: :class:`univention.admin.uexceptions.noObject` if the object does not exists.

        :raises: :class:`univention.admin.uexceptions.insufficientInformation`

        :returns: The DN of the modified object.
        """
        if not univention.admin.modules.supports(self.module, 'edit'):
            # if the licence is exceeded 'edit' is removed from the modules operations. Nevertheless we need a way to make modifications then.
            if not ignore_license:
                raise univention.admin.uexceptions.invalidOperation(_('Objects of the "%s" object type can not be modified.') % (self.module,))

        if not self.exists():
            raise univention.admin.uexceptions.noObject(self.dn)

        if not isinstance(response, dict):
            response = {}

        try:
            self._ldap_pre_ready()
            self.ready()

            dn = self._modify(modify_childs, ignore_license=ignore_license, response=response, serverctrls=serverctrls)
        except Exception:
            self._safe_cancel()
            raise

        for c in response.get('ctrls', []):
            if c.controlType == PostReadControl.controlType:
                self.oldattr.update({k: [v if isinstance(v, bytes) else v.encode('ISO8859-1') for v in val] for k, val in c.entry.items()})
        return dn

    def _write_admin_diary_modify(self) -> None:
        self._write_admin_diary_event('MODIFIED')

    def _create_temporary_ou(self) -> str:
        name = 'temporary_move_container_%s' % time.time()

        module = univention.admin.modules.get('container/ou')
        position = univention.admin.uldap.position('%s' % self.lo.base)

        temporary_object: simpleLdap = module.object(None, self.lo, position)
        temporary_object.open()
        temporary_object['name'] = name
        temporary_object.create()

        return 'ou=%s' % ldap.dn.escape_dn_chars(name)

    def _delete_temporary_ou_if_empty(self, temporary_ou: str | None) -> None:
        """
        Try to delete the organizational unit entry if it is empty.

        :param str temporary_ou: The distinguished name of the container.
        """
        if not temporary_ou:
            return

        dn = '%s,%s' % (temporary_ou, self.lo.base)

        module = univention.admin.modules.get('container/ou')
        temporary_object = univention.admin.modules.lookup(module, None, self.lo, scope='base', base=dn, required=True, unique=True)[0]
        temporary_object.open()
        try:
            temporary_object.remove()
        except (univention.admin.uexceptions.ldapError, ldap.NOT_ALLOWED_ON_NONLEAF):
            pass

    def move(self, newdn: str, ignore_license: bool = False, temporary_ou: str | None = None) -> str:
        """
        Moves the LDAP object to the target position.

        :param str newdn: The DN of the target position.
        :param bool ignore_license: If the license is exceeded the modification may fail. Setting this to True causes license checks to be disabled.
        :param str temporary_ou: The distiguished name of a temporary container which is used to rename the object if only is letter casing changes.

        :raises: :class:`univention.admin.uexceptions.invalidOperation` if objects of this type do not support to be moved.
        :raises: :class:`univention.admin.uexceptions.noObject` if the object does not exists.

        :returns: The new DN of the moved object
        """
        log.debug('move: called for %s to %s', self.dn, newdn)

        if not (univention.admin.modules.supports(self.module, 'move') or univention.admin.modules.supports(self.module, 'subtree_move')):
            raise univention.admin.uexceptions.invalidOperation(_('Objects of the "%s" object type can not be moved.') % (self.module,))

        if self.lo.compare_dn(self.dn, self.lo.whoami()):
            raise univention.admin.uexceptions.invalidOperation(_('The own object cannot be moved.'))

        if not self.exists():
            raise univention.admin.uexceptions.noObject(self.dn)

        if _prevent_to_change_ad_properties and self._is_synced_object():
            raise univention.admin.uexceptions.invalidOperation(_('Objects from Active Directory can not be moved.'))

        def n(x: str) -> str:
            return dn2str(str2dn(x))

        assert self.dn is not None
        newdn = n(newdn)
        self.dn = n(self.dn)

        goaldn = self.lo.parentDn(newdn)
        goalmodule = univention.admin.modules.identifyOne(goaldn, self.lo.get(goaldn))
        goalmodule = univention.admin.modules.get(goalmodule)
        if not goalmodule or not hasattr(goalmodule, 'childs') or goalmodule.childs != 1:
            raise univention.admin.uexceptions.invalidOperation(_("Destination object can't have sub objects."))

        if self.lo.compare_dn(self.dn.lower(), newdn.lower()):
            if self.dn == newdn:
                raise univention.admin.uexceptions.ldapError(_('Moving not possible: old and new DN are identical.'))
            else:
                # We must use a temporary folder because OpenLDAP does not allow a rename of an container with subobjects
                temporary_ou = self._create_temporary_ou()
                temp_dn = dn2str(str2dn(newdn)[:1] + str2dn(temporary_ou) + str2dn(self.lo.base))
                self.dn = n(self.move(temp_dn, ignore_license, temporary_ou))

        if newdn.lower().endswith(self.dn.lower()):
            raise univention.admin.uexceptions.ldapError(_("Moving into one's own sub container not allowed."))

        if univention.admin.modules.supports(self.module, 'subtree_move'):
            # check if is subtree:
            subelements = self.lo.search(base=self.dn, scope='one', attr=[])
            if subelements:
                olddn = self.dn
                log.debug('move: found subelements, do subtree move: newdn: %s', newdn)
                # create copy of myself
                module = univention.admin.modules.get(self.module)
                position = univention.admin.uldap.position(self.lo.base)
                position.setDn(self.lo.parentDn(newdn))
                copyobject = module.object(None, self.lo, position)
                copyobject.options = self.options[:]
                copyobject.open()
                for key in self.keys():
                    copyobject[key] = self[key]
                copyobject.policies = self.policies
                copyobject.create()
                to_be_moved = []
                moved = []
                pattern = re.compile('%s$' % (re.escape(self.dn),), flags=re.I)
                try:
                    for subolddn, suboldattrs in subelements:
                        # Convert the DNs to lowercase before the replacement. The cases might be mixed up if the Python lib is
                        # used by the connector, for example:
                        #   subolddn: uid=user_test_h80,ou=TEST_H81,$LDAP_BASE
                        #   self.dn: ou=test_h81,$LDAP_BASE
                        #   newdn: OU=TEST_H81,ou=test_h82,$LDAP_BASE
                        #   -> subnewdn: uid=user_test_h80,OU=TEST_H81,ou=test_h82,$LDAP_BASE
                        subnew_position = pattern.sub(dn2str(str2dn(self.lo.parentDn(subolddn))), newdn)
                        subnewdn = dn2str(str2dn(subolddn)[:1] + str2dn(subnew_position))
                        log.debug('move: subelement %r to %r', subolddn, subnewdn)

                        submodule = univention.admin.modules.identifyOne(subolddn, suboldattrs)
                        submodule = univention.admin.modules.get(submodule)
                        subobject = univention.admin.objects.get(submodule, None, self.lo, position='', dn=subolddn)
                        if not subobject or not (univention.admin.modules.supports(submodule, 'move') or univention.admin.modules.supports(submodule, 'subtree_move')):
                            subold_rdn = '+'.join(explode_rdn(subolddn, 1))
                            type_ = univention.admin.modules.identifyOne(subolddn, suboldattrs)
                            raise univention.admin.uexceptions.invalidOperation(_('Unable to move object %(name)s (%(type)s) in subtree, trying to revert changes.') % {
                                'name': subold_rdn,
                                'type': type_ and type_.module,
                            })
                        to_be_moved.append((subobject, subolddn, subnewdn))

                    for subobject, subolddn, subnewdn in to_be_moved:
                        subobject.open()
                        subobject.move(subnewdn)
                        moved.append((subolddn, subnewdn))

                    univention.admin.objects.get(univention.admin.modules.get(self.module), None, self.lo, position='', dn=self.dn).remove()
                    self._delete_temporary_ou_if_empty(temporary_ou)
                except BaseException:
                    log.error('move: subtree move failed, trying to move back.')
                    position = univention.admin.uldap.position(self.lo.base)
                    position.setDn(self.lo.parentDn(olddn))
                    for subolddn, subnewdn in moved:
                        submodule = univention.admin.modules.identifyOne(subnewdn, self.lo.get(subnewdn))
                        submodule = univention.admin.modules.get(submodule)
                        subobject = univention.admin.objects.get(submodule, None, self.lo, position='', dn=subnewdn)
                        subobject.open()
                        subobject.move(subolddn)
                    copyobject.remove()
                    self._delete_temporary_ou_if_empty(temporary_ou)
                    raise
                self.dn = newdn
                return newdn
            else:
                # normal move, fails on subtrees
                res = n(self._move(newdn, ignore_license=ignore_license))
                self._delete_temporary_ou_if_empty(temporary_ou)
                return res

        else:
            res = n(self._move(newdn, ignore_license=ignore_license))
            self._delete_temporary_ou_if_empty(temporary_ou)
            return res

    def move_subelements(self, olddn: str, newdn: str, subelements: list[tuple[str, dict]], ignore_license: bool = False) -> list[tuple[str, str]] | None:
        """
        Internal function to move all children of a container.

        :param str olddn: The old distinguished name of the parent container.
        :param str newdn: The new distinguished name of the parent container.
        :param subelements: A list of 2-tuples (old-dn, old-attrs) for each child of the parent container.
        :param bool ignore_license: If the license is exceeded the modification may fail. Setting this to True causes license checks to be disabled.
        :returns: A list of 2-tuples (old-dn, new-dn)
        """
        if subelements:
            log.debug('move: found subelements, do subtree move')
            moved = []
            try:
                for subolddn, suboldattrs in subelements:
                    log.debug('move: subelement %s', subolddn)
                    subnewdn = re.sub('%s$' % (re.escape(olddn),), newdn, subolddn)  # FIXME: looks broken
                    submodule = univention.admin.modules.identifyOne(subolddn, suboldattrs)
                    submodule = univention.admin.modules.get(submodule)
                    subobject = univention.admin.objects.get(submodule, None, self.lo, position='', dn=subolddn)
                    if not subobject or not (univention.admin.modules.supports(submodule, 'move') or univention.admin.modules.supports(submodule, 'subtree_move')):
                        subold_rdn = '+'.join(explode_rdn(subolddn, 1))
                        raise univention.admin.uexceptions.invalidOperation(_('Unable to move object %(name)s (%(type)s) in subtree, trying to revert changes.') % {'name': subold_rdn, 'type': univention.admin.modules.identifyOne(subolddn, suboldattrs)})
                    subobject.open()
                    subobject._move(subnewdn)
                    moved.append((subolddn, subnewdn))
                return moved
            except Exception:
                log.error('move: subtree move failed, try to move back')
                for subolddn, subnewdn in moved:
                    submodule = univention.admin.modules.identifyOne(subnewdn, self.lo.get(subnewdn))
                    submodule = univention.admin.modules.get(submodule)
                    subobject = univention.admin.objects.get(submodule, None, self.lo, position='', dn=subnewdn)
                    subobject.open()
                    subobject.move(subolddn)
                raise

        return None  # FIXME

    def remove(self, remove_childs: bool = False) -> None:
        """
        Removes this LDAP object.

        :param bool remove_childs: Specifies to remove children objects before removing this object.

        :raises: :class:`univention.admin.uexceptions.ldapError` (Operation not allowed on non-leaf: subordinate objects must be deleted first) if the object contains childrens and *remove_childs* is False.
        :raises: :class:`univention.admin.uexceptions.invalidOperation` if objects of this type do not support to be removed.
        :raises: :class:`univention.admin.uexceptions.noObject` if the object does not exists.
        """
        if not univention.admin.modules.supports(self.module, 'remove'):
            raise univention.admin.uexceptions.invalidOperation(_('Objects of the "%s" object type can not be removed.') % (self.module,))

        if not self.dn or not self.lo.get(self.dn):
            raise univention.admin.uexceptions.noObject(self.dn)

        if self.lo.compare_dn(self.dn, self.lo.whoami()):
            raise univention.admin.uexceptions.invalidOperation(_('The own object cannot be removed.'))

        return self._remove(remove_childs)

    def get_gid_for_primary_group(self) -> str:
        """
        Return the numerical group ID of the primary group.

        :returns: The numerical group ID as a string or "99999" if no primary group is declared.
        :raises univention.admin.uexceptions.primaryGroup: if the object has no primary group.
        """
        gidNum = '99999'
        if self['primaryGroup']:
            try:
                gidNum = self.lo.getAttr(self['primaryGroup'], 'gidNumber', required=True)[0].decode('ASCII')
            except ldap.NO_SUCH_OBJECT:
                raise univention.admin.uexceptions.primaryGroup(self['primaryGroup'])
        return gidNum

    def get_sid_for_primary_group(self) -> str:
        """
        Return the Windows security ID for the primary group.

        :returns: The security identifier of the primary group.
        :raises univention.admin.uexceptions.primaryGroup: if the object has no primary group.
        """
        try:
            sidNum = self.lo.getAttr(self['primaryGroup'], 'sambaSID', required=True)[0].decode('ASCII')
        except ldap.NO_SUCH_OBJECT:
            raise univention.admin.uexceptions.primaryGroupWithoutSamba(self['primaryGroup'])
        return sidNum

    def _ldap_pre_ready(self) -> None:
        """Hook which is called before :func:`univention.admin.handlers.simpleLdap.ready`."""

    def _ldap_pre_create(self) -> None:
        """Hook which is called before the object creation."""
        self.dn = self._ldap_dn()
        self.request_lock('cn-uid-position', self.dn)

    def _ldap_dn(self) -> str:
        """
        Builds the LDAP DN of the object before creation by using the identifying properties to build the RDN.

        :returns: the distringuised name.
        """
        identifier = [
            (self.mapping.mapName(name), self.mapping.mapValueDecoded(name, self.info[name]), 2)
            for name, prop in self.descriptions.items()
            if prop.identifies
        ]
        return '%s,%s' % (dn2str([identifier]), dn2str(str2dn(self.dn)[1:]) if self.exists() else self.position.getDn())

    def _ldap_post_create(self) -> None:
        """Hook which is called after the object creation."""
        self._confirm_locks()

    def _ldap_pre_modify(self) -> None:
        """Hook which is called before the object modification."""

    def _ldap_post_modify(self) -> None:
        """Hook which is called after the object modification."""
        self._confirm_locks()

    def _ldap_pre_rename(self, newdn: str) -> None:
        """
        Hook which is called before renaming the object.

        :param str newdn: The new distiguished name the object will be renamed to.
        """
        self.request_lock('cn-uid-position', newdn)

    def _ldap_post_rename(self, olddn: str) -> None:
        """
        Hook which is called after renaming the object.

        :param str olddn: The old distiguished name the object was renamed from.
        """

    def _ldap_pre_move(self, newdn: str) -> None:
        """
        Hook which is called before the object moving.

        :param str newdn: The new distiguished name the object will be moved to.
        """
        self.request_lock('cn-uid-position', newdn)

    def _ldap_post_move(self, olddn: str) -> None:
        """
        Hook which is called after the object moving.

        :param str olddn: The old distiguished name the object was moved from.
        """

    def _ldap_pre_remove(self) -> None:
        """Hook which is called before the object removal."""

    def _ldap_post_remove(self) -> None:
        """Hook which is called after the object removal."""
        self._release_locks()

    def _safe_cancel(self) -> None:
        try:
            self.cancel()
        except (KeyboardInterrupt, SystemExit, SyntaxError):
            raise
        except Exception:
            log.exception("cancel() failed:")

    def _falsy_boolean_extended_attributes(self, info: _Properties) -> _Properties:
        m = univention.admin.modules._get(self.module)
        for prop in getattr(m, 'extended_udm_attributes', []):
            if prop.syntax == 'boolean' and not info.get(prop.name):
                info[prop.name] = '0'
        return info

    def exists(self) -> bool:
        """
        Indicates that this object exists in LDAP.

        :returns: True if the object exists in LDAP, False otherwise.
        """
        return self._exists

    def _validate_superordinate(self, must_exists: bool = True) -> None:
        """
        Checks if the superordinate is set to a valid :class:`univention.admin.handlers.simpleLdap` object if this module requires a superordinate.
        It is ensured that the object type of the superordinate is correct.
        It is ensured that the object lies underneath of the superordinate position.

        :raises: :class:`univention.admin.uexceptions.insufficientInformation`

        :raises: :class:`univention.admin.uexceptions.noSuperordinate`
        """
        superordinate_names = set(univention.admin.modules.superordinate_names(self.module))
        if not superordinate_names:
            return  # module has no superodinates

        if not self.dn and not self.position:
            # this check existed in all modules with superordinates, so still check it here, too
            raise univention.admin.uexceptions.insufficientInformation(_('Neither DN nor position given.'))

        if not self.superordinate:
            self.superordinate = univention.admin.objects.get_superordinate(self.module, None, self.lo, self.dn or self.position.getDn())

        if not self.superordinate:
            if superordinate_names == {'settings/cn'}:
                log.warning('No settings/cn superordinate was given.')
                return   # settings/cn might be misued as superordinate, don't risk currently
            if not must_exists:
                return
            raise univention.admin.uexceptions.noSuperordinate(_('No superordinate object given'))

        # check if the superordinate is of the correct object type
        if not {self.superordinate.module} & superordinate_names:
            raise univention.admin.uexceptions.insufficientInformation(_('The given %r superordinate is expected to be of type %s.') % (self.superordinate.module, ', '.join(superordinate_names)))

        if self.dn and not self._ensure_dn_in_subtree(self.superordinate.dn, self.lo.parentDn(self.dn)):
            raise univention.admin.uexceptions.insufficientInformation(_('The DN must be underneath of the superordinate.'))

    def _ensure_dn_in_subtree(self, parent: str, dn: str | None) -> bool:
        """
        Checks if the given DN is underneath of the subtree of the given parent DN.

        :param str parent: The distiguished name of the parent container.
        :param str dn: The distinguished name to check.
        :returns: True if `dn` is underneath of `parent`, False otherwise.
        """
        while dn:
            if self.lo.compare_dn(dn, parent):
                return True
            dn = self.lo.parentDn(dn)
        return False

    def call_udm_property_hook(
        self,
        hookname: _HookName,
        module: Self,
        changes=None,  # dict[str, tuple] | None
    ) -> dict[str, tuple] | None:
        """
        Internal method to call a hook scripts of extended attributes.

        :param str hookname: The name of the hook function to call.
        :param str module: The name of the UDM module.
        :param dict changes: A list of changes.
        :returns: The (modified) list of changes.
        """
        m = univention.admin.modules._get(module.module)
        attrs = getattr(m, 'extended_udm_attributes', None)
        if attrs:
            for prop in attrs:
                if prop.hook is not None:
                    func = getattr(prop.hook, hookname)
                    if changes is None:
                        func(module)
                    else:
                        changes = func(module, changes)
        return changes

    def open(self) -> None:
        """
        Opens this object.

        During the initialization of this object the current set LDAP attributes are mapped into :py:attr:`info`.
        This method makes it possible to e.g. resolve external references to other objects which are not represented in the raw LDAP attributes
        of this object, for example the group memberships of a user.

        By default only the `open` hook for extended attributes is called.
        This method can be subclassed.

        .. warning::
        If this method changes anything in self.info it *must* call :py:meth:`save` afterwards.

        .. warning::
        If your are going to do any modifications (such as creating, modifying, moving, removing this object)
        this method must be called directly after the constructor and before modifying any property.
        """
        self._open = True
        self.call_udm_property_hook('hook_open', self)
        self.save()

    def _remove_option(self, name: str) -> None:
        """
        Removes the UDM option if it is set.

        :param str name: The name of the option to remove.
        """
        if name in self.options:
            self.options.remove(name)

    def __set_options(self) -> None:
        """Enables the UDM options of this object by evaluating the currently set LDAP object classes. If the object does not exists yet the default options are enabled."""
        options = univention.admin.modules.options(self.module)
        if 'objectClass' in self.oldattr:
            ocs = {x.decode('UTF-8') for x in self.oldattr['objectClass']}
            self.options = [
                opt
                for opt, option in options.items()
                if not option.disabled and option.matches(ocs) and self.__app_option_enabled(opt, option)
            ]
        else:
            log.debug('reset options to default by _define_options')
            self.options = []
            self._define_options(options)

    def _define_options(self, module_options: dict[str, Any]) -> None:
        """
        Enables all UDM options which are enabled by default.

        :param dict module_options: A mapping of option-name to option.
        """
        log.debug('modules/__init__.py _define_options: reset to default options')
        self.options.extend(
            name
            for name, opt in module_options.items()
            if not opt.disabled and opt.default
        )

    def option_toggled(self, option: str) -> bool:
        """
        Checks if an UDM option was changed.

        :param str option: The name of the option to check.
        :returns: True if the option was changed, False otherwise.

        .. warning::
                This does not work for not yet existing objects.
        """
        return option in set(self.options) ^ set(self.old_options)

    def policy_reference(self, *policies):
        for policy in policies:
            if not ldap.dn.is_dn(policy):
                raise univention.admin.uexceptions.valueInvalidSyntax(policy)
            try:
                if b'univentionPolicy' not in self.lo.getAttr(policy, 'objectClass', required=True):
                    raise univention.admin.uexceptions.valueError('Object is not a policy', policy)
            except ldap.NO_SUCH_OBJECT:
                raise univention.admin.uexceptions.noObject('Policy does not exists', policy)
        self.policies.extend(policy for policy in policies if not any(self.lo.compare_dn(pol, policy) for pol in self.policies))

    def policy_dereference(self, *policies):
        for policy in policies:
            if not ldap.dn.is_dn(policy):
                raise univention.admin.uexceptions.valueInvalidSyntax(policy)
        self.policies = [policy for policy in self.policies if not any(self.lo.compare_dn(pol, policy) for pol in policies)]

    def policiesChanged(self) -> bool:
        return set(self.oldpolicies) != set(self.policies)

    def __app_option_enabled(self, name: str, option: univention.admin.option) -> bool:
        if option.is_app_option:
            return all(self[pname] in ('TRUE', '1', 'OK') for pname, prop in self.descriptions.items() if name in prop.options and prop.syntax.name in ('AppActivatedBoolean', 'AppActivatedTrue', 'AppActivatedOK'))
        return True

    def description(self) -> str:
        """
        Return a descriptive string for the object.
        By default the relative distinguished name is returned.

        :returns: A descriptive string or `none` as fallback.
        """
        if self.dn:
            return '+'.join(explode_rdn(self.dn, 1))
        else:
            for name, property in self.descriptions.items():
                if property.identifies:
                    syntax = property.syntax
                    return syntax.tostring(self[name] or '')
        return 'none'

    def _post_unmap(self, info: _Properties, values: _Attributes) -> _Properties:
        """
        This method can be overwritten to define special un-map methods to map
        back from LDAP to UDM that can not be done with the default mapping API.

        :param info: The list of UDM properties.
        :param values: The list of LDAP attributes.
        :returns: The (modified) list of UDM properties.
        """
        return info

    def _post_map(self, modlist: list[tuple[str, Any, Any]], diff: list[tuple[str, Any, Any]]) -> list[tuple[str, Any, Any]]:
        """
        This method can be overwritten to define special map methods to map from
        UDM to LDAP that can not be done with the default mapping API.

        :param modlist: The list of LDAP modifications.
        :param list diff: A list of modified UDM properties.
        :returns: The (modified) list of LDAP modifications.
        """
        return modlist

    def _ldap_addlist(self) -> list[tuple[str, Any]]:
        return []

    def _ldap_modlist(self) -> list[tuple[str, Any, Any]]:
        """
        Builds the list of modifications when creating and modifying this object.

        It compares the old properties (:py:attr:`oldinfo`) with the new properties (:py:attr:`info`) and applies the LDAP mapping.
        Differences are added to the modlist which consists of a tuple with three items:

        ("LDAP attribute-name", [old, values], [new, values])

        ("LDAP attribute-name", old_value, new_value)

        ("LDAP attribute-name", None, added_value)

        .. seealso:: :mod:`univention.uldap` for further information about the format of the modlist.

        This method can be overridden in a subclass to add special behavior, e.g. for properties which have no mapping defined.

        .. caution:: The final modlist used for creation of objects is mixed with the :func:`univention.admin.handlers.simpleLdap._ldap_addlist`.
        Make sure this method don't add attributes which are already set.
        """
        diff_ml = self.diff()
        ml = univention.admin.mapping.mapDiff(self.mapping, diff_ml)
        ml = self._post_map(ml, diff_ml)

        if self.policiesChanged():
            policy_ocs_set = b'univentionPolicyReference' in self.oldattr.get('objectClass', [])
            if self.policies and not policy_ocs_set:
                ml.append(('objectClass', b'', [b'univentionPolicyReference']))
            elif not self.policies and policy_ocs_set:
                ml.append(('objectClass', b'univentionPolicyReference', b''))
            ml.append(('univentionPolicyReference', [x.encode('UTF-8') for x in self.oldpolicies], [x.encode('UTF-8') for x in self.policies]))

        return ml

    def _create(self, response: dict[str, Any] | None = None, serverctrls: list[ldap.controls.LDAPControl] | None = None, ignore_license: bool = False) -> str:
        """Create the object. Should only be called by :func:`univention.admin.handlers.simpleLdap.create`."""
        univention.admin.blocklist.check_blocklistentry(self)
        self._ldap_pre_create()
        self._update_policies()
        self.call_udm_property_hook('hook_ldap_pre_create', self)

        self.set_default_values()

        self._call_checkLdap_on_all_property_syntaxes()

        al = self._ldap_addlist()
        al.extend(self._ldap_modlist())
        al = self._ldap_object_classes_add(al)
        al = self.call_udm_property_hook('hook_ldap_addlist', self, al)

        # ensure univentionObject is set
        al.append(('objectClass', [b'univentionObject']))
        al.append(('univentionObjectType', [self.module.encode('utf-8')]))

        log.debug("create object with dn: %s", self.dn)
        log.log(1, 'Create dn=%r;\naddlist=%r;', self.dn, al)

        # if anything goes wrong we need to remove the already created object, otherwise we run into 'already exists' errors
        try:
            self.lo.add(self.dn, al, serverctrls=serverctrls, response=response, ignore_license=ignore_license)
            self._exists = True
            self._ldap_post_create()
        except Exception:
            # ensure that there is no lock left
            exc = sys.exc_info()
            log.info("Creating %r failed: %r", self.dn, exc[1])
            try:
                self.cancel()
            except Exception:
                log.exception("Post-create: cancel() failed:")
            try:
                if self._exists:  # add succeeded but _ldap_post_create failed!
                    obj = univention.admin.objects.get(univention.admin.modules._get(self.module), None, self.lo, self.position, self.dn)
                    obj.open()
                    obj.remove()
            except Exception:
                log.exception("Post-create: remove() failed: %s")
            raise exc[1].with_traceback(exc[2])

        self.call_udm_property_hook('hook_ldap_post_create', self)

        self.save()
        return self.dn

    def _ldap_object_classes_add(self, al: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
        m = univention.admin.modules._get(self.module)
        # evaluate extended attributes
        ocs: set[str] = set()
        for prop in getattr(m, 'extended_udm_attributes', []):
            log.debug('simpleLdap._create: info[%s]:%r = %r', prop.name, self.has_property(prop.name), self.info.get(prop.name))
            if prop.syntax == 'boolean' and self.info.get(prop.name) == '0':
                continue
            if self.has_property(prop.name) and self.info.get(prop.name):
                ocs.add(prop.objClass)

        module_options = univention.admin.modules.options(self.module)
        # add object classes of (especially extended) options
        for option in ["default", *self.options]:
            try:
                opt = module_options[option]
            except KeyError:
                log.debug('%r does not specify option %r', m.module, option)
                continue
            ocs |= set(opt.objectClasses)

        # remove duplicated object classes
        for i in al:
            key, val = i[0], i[-1]  # might be a triple
            if val and key.lower() == 'objectclass':
                val_list = [val] if not isinstance(val, tuple | list) else val
                val_unicode = [x.decode('UTF-8') if isinstance(x, bytes) else x for x in val_list]
                ocs -= set(val_unicode)  # TODO: check str vs bytes everywhere for ocs calculations
        if ocs:
            al.append(('objectClass', [x.encode('UTF-8') for x in ocs]))

        return al

    def _modify(self, modify_childs=True, ignore_license=False, response=None, serverctrls=None):
        """Modify the object. Should only be called by :func:`univention.admin.handlers.simpleLdap.modify`."""
        self.__prevent_ad_property_change()

        univention.admin.blocklist.check_blocklistentry(self)
        self._ldap_pre_modify()
        self._update_policies()
        self.call_udm_property_hook('hook_ldap_pre_modify', self)

        self.set_default_values()
        self._fix_app_options()

        # iterate over all properties and call checkLdap() of corresponding syntax
        self._call_checkLdap_on_all_property_syntaxes()

        ml = self._ldap_modlist()
        ml = self.call_udm_property_hook('hook_ldap_modlist', self, ml)
        ml = self._ldap_object_classes(ml)

        class wouldRename(Exception):
            @classmethod
            def on_rename(cls, dn, new_dn, ml):
                raise cls(dn, new_dn)

        # FIXME: timeout without exception if objectClass of Object is not exsistant !!
        log.log(1, 'Modify dn=%r;\nmodlist=%r;\noldattr=%r;', self.dn, ml, self.oldattr)

        blocklist_entries = univention.admin.blocklist.create_blocklistentry(self)
        try:
            try:
                self.dn = self.lo.modify(self.dn, ml, ignore_license=ignore_license, serverctrls=serverctrls, response=response, rename_callback=wouldRename.on_rename)
            except wouldRename as exc:
                self._ldap_pre_rename(exc.args[1])
                self.dn = self.lo.modify(self.dn, ml, ignore_license=ignore_license, serverctrls=serverctrls, response=response)
                self._ldap_post_rename(exc.args[0])
        except Exception:
            univention.admin.blocklist.cleanup_blocklistentry(blocklist_entries, self)
            raise
        if ml:
            self._write_admin_diary_modify()

        self._ldap_post_modify()
        self.call_udm_property_hook('hook_ldap_post_modify', self)

        self.save()
        return self.dn

    def set_default_values(self) -> None:
        """Sets all the default values of all properties."""
        # Make sure all default values are set...
        for name, p in self.descriptions.items():
            # ... if property has no option or any required option is currently enabled
            if not self.has_property(name):
                continue
            set_defaults = self.set_defaults
            if not self.set_defaults and p.options and not set(self.old_options) & set(p.options):
                # set default values of properties which depend on an option but weren't activated prior modifying
                self.set_defaults = True
            try:
                if p.default(self):
                    self[name]  # __getitem__ sets default value
            finally:
                self.set_defaults = set_defaults

    def _fix_app_options(self) -> None:
        # for objects with objectClass=appObject and appObjectActivated=0 we must set appObjectActivated=1
        for option, opt in getattr(univention.admin.modules._get(self.module), 'options', {}).items():
            if not opt.is_app_option or not self.option_toggled(option) or option not in self.options:
                continue
            for pname, prop in self.descriptions.items():
                if option in prop.options and prop.syntax.name in ('AppActivatedBoolean', 'AppActivatedTrue', 'AppActivatedOK'):
                    self[pname] = True

    def _ldap_object_classes(self, ml: list[tuple]) -> list[tuple]:
        """Detects the attributes changed in the given modlist, calculates the changes of the object class and appends it to the modlist."""
        m = univention.admin.modules._get(self.module)

        def lowerset(vals: Iterable[str]) -> set[str]:
            return {x.lower() for x in vals}

        ocs = lowerset(x.decode('UTF-8') for x in _MergedAttributes(self, ml).get_attribute('objectClass'))
        unneeded_ocs: set[str] = set()
        required_ocs: set[str] = set()

        # evaluate (extended) options
        module_options = univention.admin.modules.options(self.module)
        available_options = set(module_options)
        options = set(self.options)
        if 'default' in available_options:
            options |= {'default'}
        old_options = set(self.old_options)
        if options != old_options:
            log.debug('options=%r; old_options=%r', options, old_options)
        unavailable_options = (options - available_options) | (old_options - available_options)
        if unavailable_options:
            # Bug #46586: as we simulate legacy options, this is no longer an error
            log.debug('%r does not provide options: %r', self.module, unavailable_options)
        added_options = options - old_options - unavailable_options
        removed_options = old_options - options - unavailable_options

        # evaluate extended attributes
        for prop in getattr(m, 'extended_udm_attributes', []):
            log.debug('simpleLdap._modify: extended attribute=%r  oc=%r', prop.name, prop.objClass)

            if self.has_property(prop.name) and self.info.get(prop.name) and (True if prop.syntax != 'boolean' else self.info.get(prop.name) != '0'):
                required_ocs |= {prop.objClass}
                continue

            if prop.deleteObjClass:
                unneeded_ocs |= {prop.objClass}

            # if the value is unset we need to remove the attribute completely
            if self.oldattr.get(prop.ldapMapping):
                ml = [x for x in ml if x[0].lower() != prop.ldapMapping.lower()]
                ml.append((prop.ldapMapping, self.oldattr.get(prop.ldapMapping), b''))

        unneeded_ocs |= {oc for option in removed_options for oc in module_options[option].objectClasses}
        required_ocs |= {oc for option in added_options for oc in module_options[option].objectClasses}

        ocs -= lowerset(unneeded_ocs)
        ocs |= lowerset(required_ocs)
        if lowerset(x.decode('utf-8') for x in self.oldattr.get('objectClass', [])) == ocs:
            return ml

        log.debug('OCS=%r; required=%r; removed: %r', ocs, required_ocs, unneeded_ocs)

        # case normalize object class names
        schema = self.lo.get_schema()
        ocs = {x.names[0] for x in (schema.get_obj(ldap.schema.models.ObjectClass, x) for x in ocs) if x}

        # make sure we still have a structural object class
        if not schema.get_structural_oc(ocs):
            structural_ocs = schema.get_structural_oc(unneeded_ocs)
            if not structural_ocs:
                log.error('missing structural object class. Modify will fail.')
                return ml
            log.warning('Preventing to remove last structural object class %r', structural_ocs)
            ocs -= set(schema.get_obj(ldap.schema.models.ObjectClass, structural_ocs).names)

        # validate removal of object classes
        must, may = schema.attribute_types(ocs)
        allowed = {name.lower() for attr in may.values() for name in attr.names} | {name.lower() for attr in must.values() for name in attr.names}

        ml = [x for x in ml if x[0].lower() != 'objectclass']
        ml.append(('objectClass', self.oldattr.get('objectClass', []), [x.encode('utf-8') for x in ocs]))
        newattr = ldap.cidict.cidict(_MergedAttributes(self, ml).get_attributes())

        # make sure only attributes known by the object classes are set
        for attr, val in newattr.items():
            if not val:
                continue
            if re.sub(';binary$', '', attr.lower()) not in allowed:
                log.warning('The attribute %r is not allowed by any object class.', attr)
                # ml.append((attr, val, [])) # TODO: Remove the now invalid attribute instead
                return ml

        # require all MUST attributes to be set
        for attr in must.values():
            if not any(newattr.get(name) or newattr.get('%s;binary' % (name,)) for name in attr.names):
                log.warning('The attribute %r is required by the current object classes.', attr.names)
                return ml

        ml = [x for x in ml if x[0].lower() != 'objectclass']
        ml.append(('objectClass', self.oldattr.get('objectClass', []), [x.encode('utf-8') for x in ocs]))

        return ml

    def _move_in_subordinates(self, olddn: str) -> None:
        result = self.lo.searchDn(base=self.lo.base, filter=filter_format('(&(objectclass=person)(secretary=%s))', [olddn]))
        for subordinate in result:
            self.lo.modify(subordinate, [('secretary', olddn.encode('utf-8'), self.dn.encode('utf-8'))])

    def _move_in_groups(self, olddn: str) -> None:
        for group in [*self.oldinfo.get("groups", []), self.oldinfo.get("machineAccountGroup", "")]:
            if group != '':
                try:
                    self.lo.modify(
                        group, [('uniqueMember', [olddn.encode("UTF-8")], None)])
                except univention.admin.uexceptions.ldapError as exc:
                    if not isinstance(exc.original_exception, ldap.NO_SUCH_ATTRIBUTE):
                        raise
                try:
                    self.lo.modify(group, [('uniqueMember', None, [self.dn.encode("UTF-8")])])
                except univention.admin.uexceptions.ldapError as exc:
                    if not isinstance(exc.original_exception, ldap.TYPE_OR_VALUE_EXISTS):
                        raise

    def _move(self, newdn: str, modify_childs: bool = True, ignore_license: bool = False) -> str:
        """Moves this object to the new DN. Should only be called by :func:`univention.admin.handlers.simpleLdap.move`."""
        self._ldap_pre_move(newdn)

        olddn = self.dn
        self.lo.rename(self.dn, newdn)
        self.dn = newdn

        try:
            self._move_in_groups(olddn)  # can be done always, will do nothing if oldinfo has no attribute 'groups'
            self._move_in_subordinates(olddn)
            self._ldap_post_move(olddn)
        except Exception:
            # move back
            log.warning('simpleLdap._move: self._ldap_post_move failed, move object back to %s', olddn)
            self.lo.rename(self.dn, olddn)
            self.dn = olddn
            raise
        self._write_admin_diary_move(newdn)
        return self.dn

    def _write_admin_diary_move(self, position: str) -> None:
        self._write_admin_diary_event('MOVED', {'position': position})

    def _remove(self, remove_childs: bool = False) -> None:
        """Removes this object. Should only be called by :func:`univention.admin.handlers.simpleLdap.remove`."""
        log.debug('handlers/__init__._remove() called for %r with remove_childs=%r', self.dn, remove_childs)

        if _prevent_to_change_ad_properties and self._is_synced_object():
            raise univention.admin.uexceptions.invalidOperation(_('Objects from Active Directory can not be removed.'))

        self._ldap_pre_remove()
        self.call_udm_property_hook('hook_ldap_pre_remove', self)

        if remove_childs:
            subelements: list[tuple[str, dict[str, list[str]]]] = []
            if b'FALSE' not in self.lo.getAttr(self.dn, 'hasSubordinates'):
                log.debug('handlers/__init__._remove() children of base dn %s', self.dn)
                subelements = self.lo.search(base=self.dn, scope='one', attr=[])

            for subolddn, suboldattrs in subelements:
                log.debug('remove: subelement %s', subolddn)
                for submodule in univention.admin.modules.identify(subolddn, suboldattrs):
                    subobject = submodule.object(None, self.lo, None, dn=subolddn, attributes=suboldattrs)
                    subobject.open()
                    try:
                        subobject.remove(remove_childs)
                    except univention.admin.uexceptions.base as exc:
                        log.error('remove: could not remove %r: %s: %s', subolddn, type(exc).__name__, exc)
                    break
                else:
                    log.warning('remove: could not identify UDM module of %r', subolddn)

        self._exists = False
        blocklist_entries = univention.admin.blocklist.create_blocklistentry(self)
        try:
            self.lo.delete(self.dn)
        except Exception:
            univention.admin.blocklist.cleanup_blocklistentry(blocklist_entries, self)
            self._exists = True
            raise

        self._ldap_post_remove()

        self.call_udm_property_hook('hook_ldap_post_remove', self)
        self.oldattr = {}
        self._write_admin_diary_remove()
        self.save()

    def _write_admin_diary_remove(self) -> None:
        self._write_admin_diary_event('REMOVED')

    def loadPolicyObject(self, policy_type: str, reset: int = 0) -> 'simplePolicy':
        pathlist = []

        log.debug("loadPolicyObject: policy_type: %s", policy_type)
        policy_module = univention.admin.modules._get(policy_type)

        # overwrite property descriptions
        univention.admin.ucr_overwrite_properties(policy_module, self.lo)
        # re-build layout if there any overwrites defined
        univention.admin.ucr_overwrite_module_layout(policy_module)

        # retrieve path info from 'cn=directory,cn=univention,<current domain>' object
        pathResult = self.lo.get('cn=directory,cn=univention,' + self.position.getDomain())
        if not pathResult:
            pathResult = self.lo.get('cn=default containers,cn=univention,' + self.position.getDomain())
        for j in pathResult.get('univentionPolicyObject', []):
            i = j.decode('utf-8')
            try:
                self.lo.searchDn(base=i, scope='base')
                pathlist.append(i)
                log.debug("loadPolicyObject: added path %s", i)
            except Exception:
                log.debug("loadPolicyObject: invalid path setting: %s does not exist in LDAP", i)
                continue  # looking for next policy container
            break  # at least one item has been found; so we can stop here since only pathlist[0] is used

        if not pathlist:
            policy_position = self.position
        else:
            policy_position = univention.admin.uldap.position(self.position.getBase())
            policy_path = pathlist[0]
            try:
                prefix = univention.admin.modules.policyPositionDnPrefix(policy_module)
                self.lo.searchDn(base="%s,%s" % (prefix, policy_path), scope='base')
                policy_position.setDn("%s,%s" % (prefix, policy_path))
            except Exception:
                policy_position.setDn(policy_path)

        for dn in self.policies:
            if univention.admin.modules.recognize(policy_module, dn, self.lo.get(dn)) and self.policyObjects.get(policy_type, None) and self.policyObjects[policy_type].cloned == dn and not reset:
                return self.policyObjects[policy_type]

        for dn in self.policies:
            modules = univention.admin.modules.identify(dn, self.lo.get(dn))
            for module in modules:
                if univention.admin.modules.name(module) == policy_type:
                    self.policyObjects[policy_type] = univention.admin.objects.get(module, None, self.lo, policy_position, dn=dn)
                    self.policyObjects[policy_type].clone(self)
                    self._init_ldap_search(self.policyObjects[policy_type])

                    return self.policyObjects[policy_type]
            if not modules:
                self.policies.remove(dn)

        if not self.policyObjects.get(policy_type, None) or reset:
            self.policyObjects[policy_type] = univention.admin.objects.get(policy_module, None, self.lo, policy_position)
            self.policyObjects[policy_type].copyIdentifier(self)
            self._init_ldap_search(self.policyObjects[policy_type])

        return self.policyObjects[policy_type]

    def _init_ldap_search(self, policy: 'simplePolicy') -> None:
        properties: dict[str, univention.admin.property] = {}
        if hasattr(policy, 'property_descriptions'):
            properties = policy.property_descriptions
        elif hasattr(policy, 'descriptions'):
            properties = policy.descriptions
        for pname, prop in properties.items():
            if prop.syntax.name == 'LDAP_Search':
                prop.syntax._load(self.lo)
                if prop.syntax.viewonly:
                    policy.mapping.unregister(pname, False)

    def _update_policies(self) -> None:
        for policy_type, policy_object in self.policyObjects.items():
            log.debug("simpleLdap._update_policies: processing policy of type: %s", policy_type)
            if policy_object.changes:
                log.debug("simpleLdap._update_policies: trying to create policy of type: %s", policy_type)
                log.debug("simpleLdap._update_policies: policy_object.info=%s", policy_object.info)
                policy_object.create()
                univention.admin.objects.replacePolicyReference(self, policy_type, policy_object.dn)

    def closePolicyObjects(self) -> None:
        self.policyObjects = {}

    def savePolicyObjects(self) -> None:
        self._update_policies()
        self.closePolicyObjects()

    def cancel(self) -> None:
        """Cancels the object creation or modification. This method can be subclassed to revert changes for example releasing locks."""
        self._release_locks()

    def _release_locks(self, name: str | None = None) -> None:
        """Release all temporary done locks"""
        for lock in self.alloc[:]:
            key, value = lock[0:2]
            if name and key != name:
                continue
            self.alloc.remove(lock)
            log.debug('release_lock(%s): %r', key, value)
            univention.admin.allocators.release(self.lo, self.position, key, value)

    def _confirm_locks(self) -> None:
        """
        Confirm all temporary done locks. self.alloc should contain a 2-tuple or 3-tuple:
        (name:str, value:str) or (name:str, value:str, updateLastUsedValue:bool)
        """
        while self.alloc:
            item = self.alloc.pop()
            name, value = item[0:2]
            updateLastUsedValue = True
            if len(item) > 2:
                updateLastUsedValue = item[2]
            univention.admin.allocators.confirm(self.lo, self.position, name, value, updateLastUsedValue=updateLastUsedValue)

    @overload
    def request_lock(self, name: univention.admin.allocators._TypesUidGid, value: str | None = None, updateLastUsedValue: bool = True) -> str:
        pass

    @overload
    def request_lock(self, name: univention.admin.allocators._Types, value: str, updateLastUsedValue: bool = True) -> str:
        pass

    def request_lock(self, name: univention.admin.allocators._Types, value: str | None = None, updateLastUsedValue: bool = True) -> str:
        """Request a lock for the given value"""
        try:
            if name == 'sid+user':
                value = univention.admin.allocators.requestUserSid(self.lo, self.position, value)
                name = 'sid'
            else:
                value = univention.admin.allocators.request(self.lo, self.position, name, value)
        except univention.admin.uexceptions.noLock:
            self._release_locks(name)
            raise
        if not updateLastUsedValue:  # backwards compatibility: 2er-tuples required!
            self.alloc.append((name, value, updateLastUsedValue))
        else:
            self.alloc.append((name, value))
        return value

    def _call_checkLdap_on_all_property_syntaxes(self) -> None:
        """
        Calls checkLdap() method on every property if present.
        checkLdap() may raise an exception if the value does not match the constraints of the underlying syntax.

        .. deprecated:: 5.0-2
        Univention internal use only!
        """
        for pname, prop in self.descriptions.items():
            if hasattr(prop.syntax, 'checkLdap') and (not self.exists() or self.hasChanged(pname)):
                if len(inspect.getfullargspec(prop.syntax.checkLdap).args) > 3:
                    prop.syntax.checkLdap(self.lo, self.info.get(pname), pname)
                else:
                    prop.syntax.checkLdap(self.lo, self.info.get(pname))

    def __prevent_ad_property_change(self) -> None:
        if not _prevent_to_change_ad_properties or not self._is_synced_object():
            return

        for key in self.descriptions:
            if self.descriptions[key].readonly_when_synced:
                value = self.info.get(key)
                oldval = self.oldinfo.get(key)
                null = [] if self.descriptions[key].multivalue else ''
                if oldval in (None, null) and value in (None, null):
                    continue
                if oldval != value:
                    raise univention.admin.uexceptions.valueMayNotChange(_('key=%(key)s old=%(old)s new=%(new)s') % {'key': key, 'old': oldval, 'new': value}, property=key)

    def _is_synced_object(self) -> bool:
        """Checks whether this object was synchronized from Active Directory to UCS."""
        flags = self.oldattr.get('univentionObjectFlag', [])
        return b'synced' in flags and b'docker' not in flags

    @classmethod
    def get_default_containers(cls, lo: univention.admin.uldap.access) -> list[str]:
        """
        Returns list of default containers for this module.

        :param univention.admin.uldap.access lo: UDM LDAP access object.
        """
        containers = univention.admin.modules.defaultContainers(univention.admin.modules._get(cls.module))
        settings_directory = univention.admin.modules._get('settings/directory')
        position = univention.admin.uldap.position(lo.base)
        try:
            univention.admin.modules.init(lo, position, settings_directory)
        except univention.admin.uexceptions.noObject:
            pass

        try:
            default_containers = settings_directory.lookup(None, lo, '', required=True)[0]
        except univention.admin.uexceptions.noObject:
            return containers

        if cls.default_containers_attribute_name:
            base = cls.default_containers_attribute_name
        else:
            base = cls.module.split('/', 1)[0]

        containers.extend(default_containers.info.get(base, []))
        return containers

    @classmethod
    def lookup(
        cls,
        co: None,
        lo: univention.admin.uldap.access,
        filter_s: str,
        base: str = '',
        superordinate: Self | None = None,
        scope: str = 'sub',
        unique: bool = False,
        required: bool = False,
        timeout: int = -1,
        sizelimit: int = 0,
        serverctrls: list | None = None,
        response: dict | None = None,
    ) -> list[Self]:
        """
        Perform a LDAP search and return a list of instances.

        :param co: obsolete config
        :param lo: UDM LDAP access object.
        :param filter_s: LDAP filter string.
        :param base: LDAP search base distinguished name.
        :param superordinate: Distinguished name of a superordinate object.
        :param scope: Specify the scope of the search to be one of `base`, `base+one`, `one`, `sub`, or `domain` to specify a base object, base plus one-level, one-level, subtree, or children search.
        :param unique: Raise an exception if more than one object matches.
        :param required: Raise an exception instead of returning an empty dictionary.
        :param timeout: wait at most `timeout` seconds for a search to complete. `-1` for no limit.
        :param sizelimit: retrieve at most `sizelimit` entries for a search. `0` for no limit.
        :param serverctrls: a list of :py:class:`ldap.controls.LDAPControl` instances sent to the server along with the LDAP request.
        :param response: An optional dictionary to receive the server controls of the result.
        :return: A list of UDM objects.
        """
        filter_e = cls.lookup_filter(filter_s, lo)
        if superordinate:
            filter_e = cls.lookup_filter_superordinate(filter_e, superordinate)
        filter_str = str(filter_e or '')
        attr = cls._ldap_attributes()
        result = []
        for dn, attrs in lo.search(filter_str, base or cls.ldap_base, scope, attr, unique, required, timeout, sizelimit, serverctrls=serverctrls, response=response):
            try:
                result.append(cls(co, lo, None, dn=dn, superordinate=superordinate, attributes=attrs))
            except univention.admin.uexceptions.base as exc:
                log.error('lookup() of object %r failed: %s', dn, exc)
        if required and not result:
            raise univention.admin.uexceptions.noObject('lookup(base=%r, filter_s=%r)' % (base, filter_e))
        return result

    @classmethod
    def lookup_filter(cls, filter_s: str | None = None, lo: univention.admin.uldap.access | None = None) -> univention.admin.filter.conjunction:
        """
        Return a LDAP filter as a UDM filter expression.

        :param str filter_s: LDAP filter string.
        :param univention.admin.uldap.access lo: UDM LDAP access object.
        :returns: A LDAP filter expression.

        See :py:meth:`lookup`.
        """
        filter_p = cls.unmapped_lookup_filter()
        # there are instances where the lookup/lookup_filter method of an module handler is called before
        # univention.admin.modules.update() was performed. (e.g. management/univention-directory-manager-modules/univention-dnsedit)
        module = univention.admin.modules._get(cls.module)
        filter_p.append_unmapped_filter_string(filter_s, cls.rewrite_filter, module.mapping)
        return filter_p

    @classmethod
    def lookup_filter_superordinate(cls, filter: univention.admin.filter.conjunction, superordinate: Self) -> univention.admin.filter.conjunction:
        return filter

    @classmethod
    def unmapped_lookup_filter(cls) -> univention.admin.filter.conjunction:
        """
        Return a LDAP filter UDM filter expression.

        :returns: A LDAP filter expression.

        See :py:meth:`lookup_filter`.
        """
        filter_conditions = []
        if cls.use_performant_ldap_search_filter:
            filter_conditions.append(univention.admin.filter.expression('univentionObjectType', cls.module, escape=True))
        else:
            object_classes = univention.admin.modules.options(cls.module).get('default', univention.admin.option()).objectClasses - {'top', 'univentionPolicy', 'univentionObjectMetadata', 'person'}
            filter_conditions.extend(univention.admin.filter.expression('objectClass', ocs) for ocs in object_classes)

        return univention.admin.filter.conjunction('&', filter_conditions)

    @classmethod
    def rewrite_filter(cls, filter: univention.admin.filter.expression, mapping: univention.admin.mapping.mapping) -> None:
        key = filter.variable

        try:
            should_map = mapping.shouldMap(key)
        except KeyError:
            should_map = False

        if should_map:
            filter.variable = mapping.mapName(key)

        if filter.operator == '=*':
            # 1. presence match. We only need to change the variable name. value is not set
            # 2. special case for syntax classes IStates and boolean:
            # properties that are represented as Checkboxes in the
            # frontend should include '(!(propertyName=*))' in the ldap filter
            # if the Checkbox is set to False to also find objects where the property
            # is not set. In that case we don't want to map the '*' to a different value.
            return

        # management/univention-management-console/src/univention/management/console/acl.py does not call univention.admin.modules.update()
        mod = univention.admin.modules._get(cls.module)
        property_ = mod.property_descriptions.get(key)

        # map options to corresponding objectClass
        if not property_ and key == 'options' and filter.value in getattr(mod, 'options', {}):
            ocs = mod.options[filter.value]
            filter.variable = 'objectClass'
            if len(ocs.objectClasses) > 1:
                con = univention.admin.filter.conjunction('&', [univention.admin.filter.expression('objectClass', oc, escape=True) for oc in ocs.objectClasses])
                filter.transform_to_conjunction(con)
            elif ocs.objectClasses:
                filter.value = list(ocs.objectClasses)[0]  # noqa: RUF015
            return

        if not should_map:
            return

        if property_ and not isinstance(filter.value, list | tuple):
            if property_.multivalue:
                # special case: mutlivalue properties need to be a list when map()-ing
                filter.value = [filter.value]
            if issubclass(property_.syntax if inspect.isclass(property_.syntax) else type(property_.syntax), univention.admin.syntax.complex):
                # special case: complex syntax properties need to be a list (of lists, if multivalue)
                filter.value = [filter.value]

        filter.value = mapping.mapValueDecoded(key, filter.value, encoding_errors='ignore')

        if isinstance(filter.value, list | tuple) and filter.value:
            # complex syntax
            filter.value = filter.value[0]

    @classmethod
    def identify(cls, dn: str, attr: _Attributes, canonical: bool = False) -> bool:
        ocs = {x.decode('utf-8') for x in attr.get('objectClass', [])}
        required_object_classes = univention.admin.modules.options(cls.module).get('default', univention.admin.option()).objectClasses - {'top', 'univentionPolicy', 'univentionObjectMetadata', 'person'}
        return (ocs & required_object_classes) == required_object_classes

    _static_ldap_attributes: set[str] = set()

    @classmethod
    def _ldap_attributes(cls) -> list[str]:
        """Get a list of additional (operational) LDAP attributes which needs to be fetched from the LDAP server when creating an instance of this object"""
        return list({'*', 'entryUUID', 'entryCSN', 'modifyTimestamp'} | cls._static_ldap_attributes)


class simpleComputer(simpleLdap):

    def __init__(
        self,
        co: None,
        lo: univention.admin.uldap.access,
        position: univention.admin.uldap.position | None,
        dn: str = '',
        superordinate: simpleLdap | None = None,
        attributes: _Attributes | None = None,
    ) -> None:
        simpleLdap.__init__(self, co, lo, position, dn, superordinate, attributes)

        self.__changes: dict[str, Any] = {}
        self.newPrimaryGroupDn = 0
        self.oldPrimaryGroupDn = 0
        self.ip: list[str] = []
        self.network_object: univention.admin.handlers.networks.network.object | None = None
        self.old_network = 'None'
        self.__saved_dhcp_entry = None
        # read-only attribute containing the FQDN of the host
        self.descriptions['fqdn'] = univention.admin.property(
            short_description='FQDN',
            long_description='',
            syntax=univention.admin.syntax.string,
            may_change=False,
        )
        self['dnsAlias'] = []  # defined here to avoid pseudo non-None value of [''] in modwizard search
        self.oldinfo['ip'] = []
        self.info['ip'] = []
        if self.exists():
            ips = [ip_address(addr.decode('ASCII')).exploded for key in ('aRecord', 'aAAARecord') for addr in self.oldattr.get(key, [])]
            self.oldinfo['ip'] += ips
            self.info['ip'] += ips

    def getMachineSid(self, lo: univention.admin.uldap.access, position: univention.admin.uldap.position, uidNum: str, rid: str | None = None) -> str:
        # if rid is given, use it regardless of s4 connector
        if rid:
            searchResult = self.lo.search(filter='objectClass=sambaDomain', attr=['sambaSID'])
            domainsid = searchResult[0][1]['sambaSID'][0].decode('ASCII')
            sid = domainsid + '-' + rid
            return self.request_lock('sid', sid)
        else:
            # if no rid is given, create a domain sid or local sid if connector is present
            if self.s4connector_present:
                return 'S-1-4-%s' % uidNum
            else:
                num = uidNum
                while True:
                    try:
                        return self.request_lock('sid+user', num)
                    except univention.admin.uexceptions.noLock:
                        num = str(int(num) + 1)

    # HELPER
    @classmethod
    def _ip_from_ptr(cls, zoneName: str, relativeDomainName: str) -> str:
        """
        Extract IP address from reverse DNS record.

        >>> simpleComputer._ip_from_ptr("2.1.in-addr.arpa", "4.3")
        '1.2.3.4'
        >>> simpleComputer._ip_from_ptr("0.0.0.0.0.0.0.0.0.8.b.d.1.0.0.2.ip6.arpa", "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")
        '2001:db80:0000:0000:0000:0000:0000:0001'
        """
        if 'ip6' in zoneName:
            return cls._ipv6_from_ptr(zoneName, relativeDomainName)
        else:
            return cls._ipv4_from_ptr(zoneName, relativeDomainName)

    @staticmethod
    def _ipv4_from_ptr(zoneName: str, relativeDomainName: str) -> str:
        """
        Extract IPv4 address from reverse DNS record.

        >>> simpleComputer._ipv4_from_ptr("2.1.in-addr.arpa", "4.3")
        '1.2.3.4'
        """
        return '%s.%s' % (
            '.'.join(reversed(zoneName.replace('.in-addr.arpa', '').split('.'))),
            '.'.join(reversed(relativeDomainName.split('.'))))

    @staticmethod
    def _ipv6_from_ptr(zoneName: str, relativeDomainName: str) -> str:
        """
        Extract IPv6 address from reverse DNS record.

        >>> simpleComputer._ipv6_from_ptr("0.0.0.0.0.0.0.0.0.8.b.d.1.0.0.2.ip6.arpa", "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")
        '2001:db80:0000:0000:0000:0000:0000:0001'
        """
        fullName = relativeDomainName + '.' + zoneName.replace('.ip6.arpa', '')
        digits = fullName.split('.')
        blocks = [''.join(reversed(digits[i:i + 4])) for i in range(0, len(digits), 4)]
        return ':'.join(reversed(blocks))

    @staticmethod
    def _is_ip(ip: str) -> bool:
        """
        Check if valid IPv4 (0.0.0.0 is allowed) or IPv6 address.

        :param ip: string.
        :returns: `True` if it is a valid IPv4 or IPv6 address., `False` otherwise.

        >>> simpleComputer._is_ip('192.0.2.0')
        True
        >>> simpleComputer._is_ip('::1')
        True
        >>> simpleComputer._is_ip('')
        False
        """
        try:
            ip_address('%s' % (ip,))
            log.debug('IP[%s]? -> Yes', ip)
            return True
        except ValueError:
            log.debug('IP[%s]? -> No', ip)
            return False

    def open(self) -> None:
        """Load the computer object from LDAP."""
        simpleLdap.open(self)

        self.newPrimaryGroupDn = 0
        self.oldPrimaryGroupDn = 0
        self.ip_already_requested = 0
        self.ip_freshly_set = False

        self.__multiip = len(self['mac']) > 1 or len(self['ip']) > 1

        self['dnsEntryZoneForward'] = []
        self['dnsEntryZoneReverse'] = []
        self['dhcpEntryZone'] = []
        self['groups'] = []
        self['dnsEntryZoneAlias'] = []

        # search forward zone and insert into the object
        if self['name']:
            tmppos = univention.admin.uldap.position(self.position.getDomain())
            zones = []

            searchFilter = filter_format('(&(objectClass=dNSZone)(relativeDomainName=%s)(!(cNAMERecord=*)))', [self['name']])
            try:
                result = self.lo.search(base=tmppos.getBase(), scope='domain', filter=searchFilter, attr=['zoneName', 'aRecord', 'aAAARecord'], unique=False)
                for dn, attr in result:
                    zoneName = attr['zoneName'][0].decode('UTF-8')
                    for key in ('aRecord', 'aAAARecord'):
                        if key in attr:
                            zones.append((zoneName, [ip_address(x.decode('ASCII')).exploded for x in attr[key]]))

                log.debug('zoneNames: %s', zones)
                for zoneName, ips in zones:
                    searchFilter = filter_format('(&(objectClass=dNSZone)(zoneName=%s)(sOARecord=*))', [zoneName])
                    for dn in self.lo.searchDn(base=tmppos.getBase(), scope='domain', filter=searchFilter, unique=False):
                        for ip in ips:
                            self['dnsEntryZoneForward'].append([dn, ip])
                log.debug('dnsEntryZoneForward: %s', self['dnsEntryZoneForward'])
            except univention.admin.uexceptions.insufficientInformation:
                self['dnsEntryZoneForward'] = []
                raise

            for zoneName, ips in zones:
                searchFilter = filter_format('(&(objectClass=dNSZone)(|(PTRRecord=%s)(PTRRecord=%s.%s.)))', (self['name'], self['name'], zoneName))
                try:
                    for dn, attr in self.lo.search(base=tmppos.getBase(), scope='domain', attr=['relativeDomainName', 'zoneName'], filter=searchFilter, unique=False):
                        ip = self._ip_from_ptr(attr['zoneName'][0].decode('UTF-8'), attr['relativeDomainName'][0].decode('UTF-8'))
                        if not self._is_ip(ip):
                            log.warning('simpleComputer: dnsEntryZoneReverse: invalid IP address generated: %r', ip)
                            continue
                        entry = [self.lo.parentDn(dn), ip]
                        if entry not in self['dnsEntryZoneReverse']:
                            self['dnsEntryZoneReverse'].append(entry)
                except univention.admin.uexceptions.insufficientInformation:
                    self['dnsEntryZoneReverse'] = []
                    raise
            log.debug('simpleComputer: dnsEntryZoneReverse: %s', self['dnsEntryZoneReverse'])

            for zoneName, ips in zones:
                searchFilter = filter_format('(&(objectClass=dNSZone)(|(cNAMERecord=%s)(cNAMERecord=%s.%s.)))', (self['name'], self['name'], zoneName))
                try:
                    for dn, attr in self.lo.search(base=tmppos.getBase(), scope='domain', attr=['relativeDomainName', 'cNAMERecord', 'zoneName'], filter=searchFilter, unique=False):
                        dnsAlias = attr['relativeDomainName'][0].decode('UTF-8')
                        self['dnsAlias'].append(dnsAlias)
                        dnsAliasZoneContainer = self.lo.parentDn(dn)
                        if attr['cNAMERecord'][0].decode('UTF-8') == self['name']:
                            dnsForwardZone = attr['zoneName'][0].decode('UTF-8')
                        else:
                            dnsForwardZone = zoneName

                        entry = [dnsForwardZone, dnsAliasZoneContainer, dnsAlias]
                        if entry not in self['dnsEntryZoneAlias']:
                            self['dnsEntryZoneAlias'].append(entry)
                except univention.admin.uexceptions.insufficientInformation:
                    self['dnsEntryZoneAlias'] = []
                    raise
            log.debug('simpleComputer: dnsEntryZoneAlias: %s', self['dnsEntryZoneAlias'])

            for macAddress in self['mac']:
                # mac address may be an empty string (Bug #21958)
                if not macAddress:
                    continue

                log.debug('open: DHCP; we have a mac address: %s', macAddress)
                ethernet = 'ethernet ' + macAddress
                searchFilter = filter_format('(&(dhcpHWAddress=%s)(objectClass=univentionDhcpHost))', (ethernet,))
                log.debug('open: DHCP; we search for "%s"', searchFilter)
                try:
                    for dn, attr in self.lo.search(base=tmppos.getBase(), scope='domain', attr=['univentionDhcpFixedAddress'], filter=searchFilter, unique=False):
                        service = self.lo.parentDn(dn)
                        if 'univentionDhcpFixedAddress' in attr:
                            for ip in attr['univentionDhcpFixedAddress']:
                                entry = (service, ip.decode('ASCII'), macAddress)
                                if entry not in self['dhcpEntryZone']:
                                    self['dhcpEntryZone'].append(entry)
                        else:
                            entry = (service, '', macAddress)
                            if entry not in self['dhcpEntryZone']:
                                self['dhcpEntryZone'].append(entry)
                    log.debug('open: DHCP; self[ dhcpEntryZone ] = "%s"', self['dhcpEntryZone'])

                except univention.admin.uexceptions.insufficientInformation:
                    raise

        if self.exists():
            if self.has_property('network'):
                self.old_network = self['network']

            # get groupmembership
            self['groups'] = self.lo.searchDn(base=self.lo.base, filter=filter_format('(&(objectclass=univentionGroup)(uniqueMember=%s))', [self.dn]))

        if 'name' in self.info and 'domain' in self.info:
            self.info['fqdn'] = '%s.%s' % (self['name'], self['domain'])

    def __modify_dhcp_object(self, position: str, mac: str, ip: str | None = None) -> None:
        # identify the dhcp object with the mac address

        name = self['name']
        log.debug('__modify_dhcp_object: position: "%s"; name: "%s"; mac: "%s"; ip: "%s"', position, name, mac, ip)
        if not all((name, mac)):
            return

        ethernet = 'ethernet %s' % mac
        bip = ip.encode('ASCII') if ip else b''

        tmppos = univention.admin.uldap.position(self.position.getDomain())
        if not position:
            log.warning('could not access network object and given position is "None", using LDAP root as position for DHCP entry')
            position = tmppos.getBase()
        results = self.lo.search(base=position, scope='domain', attr=['univentionDhcpFixedAddress'], filter=filter_format('dhcpHWAddress=%s', [ethernet]), unique=False)

        if not results:
            # if the dhcp object doesn't exists, then we create it
            # but it is possible, that the hostname for the dhcp object is already used, so we use the _uv$NUM extension

            log.debug('the dhcp object with the mac address "%s" does not exists, we create one', ethernet)

            results = self.lo.searchDn(base=position, scope='domain', filter=filter_format('(&(objectClass=univentionDhcpHost)(|(cn=%s)(cn=%s_uv*)))', (name, name)), unique=False)
            if results:
                log.debug('the host "%s" already has a dhcp object, so we search for the next free uv name', name)
                RE = re.compile(r'cn=[^,]+_uv(\d+),')
                taken = {int(m.group(1)) for m in (RE.match(dn) for dn in results) if m}
                n = min(set(range(max(taken) + 2)) - taken) if taken else 0
                name = '%s_uv%d' % (name, n)

            dn = 'cn=%s,%s' % (escape_dn_chars(name), position)
            ml = [
                ('objectClass', [b'top', b'univentionObject', b'univentionDhcpHost']),
                ('univentionObjectType', [b'dhcp/host']),
                ('cn', [name.encode('UTF-8')]),
                ('dhcpHWAddress', [ethernet.encode('ASCII')]),
            ]
            if ip:
                ml.append(('univentionDhcpFixedAddress', [bip]))
            self.lo.add(dn, ml)
            log.debug('we just added the object "%s"', dn)
        elif ip:
            # if the object already exists, we append or remove the ip address
            log.debug('the dhcp object with the mac address "%s" exists, we change the ip', ethernet)
            for dn, attr in results:
                if bip in attr.get('univentionDhcpFixedAddress', []):
                    continue
                self.lo.modify(dn, [('univentionDhcpFixedAddress', b'', bip)])
                log.debug('we added the ip "%s"', ip)

    def __rename_dns_object(self, position: univention.admin.uldap.position | None = None, old_name: str | None = None, new_name: str | None = None) -> None:
        for dns_line in self['dnsEntryZoneForward']:
            # dns_line may be the empty string
            if not dns_line:
                continue
            dn, ip = self.__split_dns_line(dns_line)
            if ':' in ip:  # IPv6
                results = self.lo.searchDn(base=dn, scope='domain', filter=filter_format('(&(relativeDomainName=%s)(aAAARecord=%s))', (old_name, ip)), unique=False)
            else:
                results = self.lo.searchDn(base=dn, scope='domain', filter=filter_format('(&(relativeDomainName=%s)(aRecord=%s))', (old_name, ip)), unique=False)
            for result in results:
                host = univention.admin.objects.get(univention.admin.modules.get('dns/host_record'), self.co, self.lo, position=self.position, dn=result)
                assert host is not None
                host.open()
                host['name'] = new_name
                host.modify()
        for dns_line in self['dnsEntryZoneReverse']:
            # dns_line may be the empty string
            if not dns_line:
                continue
            dn, ip = self.__split_dns_line(dns_line)
            results = self.lo.searchDn(base=dn, scope='domain', filter=filter_format('(|(pTRRecord=%s)(pTRRecord=%s.*))', (old_name, old_name)), unique=False)
            for result in results:
                ptr = univention.admin.objects.get(univention.admin.modules.get('dns/ptr_record'), self.co, self.lo, position=self.position, dn=result)
                assert ptr is not None
                ptr.open()
                ptr['ptr_record'] = [ptr_record.replace(old_name, new_name) for ptr_record in ptr.get('ptr_record', [])]
                ptr.modify()
        for entry in self['dnsEntryZoneAlias']:
            # entry may be the empty string
            if not entry:
                continue
            dnsforwardzone, dnsaliaszonecontainer, alias = entry
            results = self.lo.searchDn(base=dnsaliaszonecontainer, scope='domain', filter=filter_format('relativedomainname=%s', [alias]), unique=False)
            for result in results:
                alias = univention.admin.objects.get(univention.admin.modules.get('dns/alias'), self.co, self.lo, position=self.position, dn=result)
                alias.open()
                alias['cname'] = '%s.%s.' % (new_name, dnsforwardzone)
                alias.modify()

    def __rename_dhcp_object(self, old_name: str, new_name: str) -> None:
        module = univention.admin.modules.get('dhcp/host')
        tmppos = univention.admin.uldap.position(self.position.getDomain())
        for mac in self['mac']:
            # mac may be the empty string
            if not mac:
                continue
            ethernet = 'ethernet %s' % mac

            results = self.lo.searchDn(base=tmppos.getBase(), scope='domain', filter=filter_format('dhcpHWAddress=%s', [ethernet]), unique=False)
            if not results:
                continue
            log.debug('simpleComputer: filter [ dhcpHWAddress = %s ]; results: %s', ethernet, results)

            for result in results:
                dhcp = univention.admin.objects.get(module, self.co, self.lo, position=self.position, dn=result)
                assert dhcp is not None
                dhcp.open()
                dhcp['host'] = dhcp['host'].replace(old_name, new_name)
                dhcp.modify()

    def __remove_from_dhcp_object(self, mac: str | None = None, ip: str | None = None) -> str | None:
        # if we got the mac address, then we remove the object
        # if we only got the ip address, we remove the ip address

        log.debug('we should remove a dhcp object: mac="%s", ip="%s"', mac, ip)

        dn = None

        tmppos = univention.admin.uldap.position(self.position.getDomain())
        if ip and mac:
            ethernet = 'ethernet %s' % mac
            log.debug('we only remove the ip "%s" from the dhcp object', ip)
            results = self.lo.search(base=tmppos.getBase(), scope='domain', attr=['univentionDhcpFixedAddress'], filter=filter_format('(&(dhcpHWAddress=%s)(univentionDhcpFixedAddress=%s))', (ethernet, ip)), unique=False)
            for dn, _attr in results:
                host = univention.admin.objects.get(univention.admin.modules.get('dhcp/host'), self.co, self.lo, position=self.position, dn=dn)
                assert host is not None
                host.open()
                if ip in host['fixedaddress']:
                    log.debug('fixedaddress: "%s"', host['fixedaddress'])
                    host['fixedaddress'].remove(ip)
                    if not host['fixedaddress']:
                        host.remove()
                    else:
                        host.modify()
                    dn = host.dn

        elif mac:
            ethernet = 'ethernet %s' % mac
            log.debug('Remove the following mac: ethernet: "%s"', ethernet)
            results = self.lo.search(base=tmppos.getBase(), scope='domain', attr=['univentionDhcpFixedAddress'], filter=filter_format('dhcpHWAddress=%s', [ethernet]), unique=False)
            for dn, _attr in results:
                log.debug('... done')
                host = univention.admin.objects.get(univention.admin.modules.get('dhcp/host'), self.co, self.lo, position=self.position, dn=dn)
                assert host is not None
                host.remove()
                dn = host.dn

        elif ip:
            log.debug('Remove the following ip: "%s"', ip)
            results = self.lo.search(base=tmppos.getBase(), scope='domain', attr=['univentionDhcpFixedAddress'], filter=filter_format('univentionDhcpFixedAddress=%s', [ip]), unique=False)
            for dn, _attr in results:
                log.debug('... done')
                host = univention.admin.objects.get(univention.admin.modules.get('dhcp/host'), self.co, self.lo, position=self.position, dn=dn)
                assert host is not None
                host.remove()
                dn = host.dn

        return dn

    @classmethod
    def __split_dhcp_line(cls, entry: list[str]) -> tuple[str, str, str]:
        """
        >>> simpleComputer._simpleComputer__split_dhcp_line(["service", "0011.2233.4455"])
        ('service', '', '00:11:22:33:44:55')
        >>> simpleComputer._simpleComputer__split_dhcp_line(["service", "1.2.3.4", "00:11:22:33:44:55"])
        ('service', '1.2.3.4', '00:11:22:33:44:55')
        """
        service = entry[0]
        ip = ''
        try:
            # sanitize mac address
            #   0011.2233.4455 -> 00:11:22:33:44:55 -> is guaranteed to work together with our DHCP server
            #   __split_dhcp_line may be used outside of UDM which means that MAC_Address.parse may not be called.
            mac = univention.admin.syntax.MAC_Address.parse(entry[-1])
            if cls._is_ip(entry[-2]):
                ip = entry[-2]
        except univention.admin.uexceptions.valueError:
            mac = ''
        return (service, ip, mac)

    @classmethod
    def __split_dns_line(cls, entry: list[str]) -> tuple[str, str | None]:
        """
        >>> simpleComputer._simpleComputer__split_dns_line(["zoneName"])
        ('zoneName', None)
        >>> simpleComputer._simpleComputer__split_dns_line(["zoneName", "1.2.3.4"])
        ('zoneName', '1.2.3.4')
        """
        zone = entry[0]
        ip = entry[1] if len(entry) > 1 and cls._is_ip(entry[1]) else None

        log.debug('Split entry %s into zone %s and ip %s', entry, zone, ip)
        return (zone, ip)

    def __remove_dns_reverse_object(self, name: str, dnsEntryZoneReverse: str | None, ip: str) -> None:
        def modify(rdn: str, zoneDN: str) -> None:
            zone_name = explode_rdn(zoneDN, True)[0]
            for dn, attributes in self.lo.search(scope='domain', attr=['pTRRecord'], filter=filter_format('(&(relativeDomainName=%s)(zoneName=%s))', (rdn, zone_name))):
                ptr_records = attributes.get('pTRRecord', [])
                removals = []
                if len(ptr_records) > 1:
                    removals = [b'%s.%s.' % (name.encode('UTF-8'), attributes2['zoneName'][0]) for dn2, attributes2 in self.lo.search(scope='domain', attr=['zoneName'], filter=filter_format('(&(relativeDomainName=%s)(objectClass=dNSZone))', [name]), unique=False)]

                if len(ptr_records) <= 1 or set(ptr_records) == set(removals):
                    self.lo.delete('relativeDomainName=%s,%s' % (escape_dn_chars(rdn), zoneDN))
                else:
                    self.lo.modify(dn, [('pTRRecord', removals, b'')])

                zone = univention.admin.handlers.dns.reverse_zone.object(self.co, self.lo, self.position, zoneDN)
                zone.open()
                zone.modify()

        log.debug('we should remove a dns reverse object: dnsEntryZoneReverse="%s", name="%s", ip="%s"', dnsEntryZoneReverse, name, ip)
        if dnsEntryZoneReverse:
            try:
                rdn = self.calc_dns_reverse_entry_name(ip, dnsEntryZoneReverse)
            except ValueError:
                pass
            else:
                modify(rdn, dnsEntryZoneReverse)

        elif ip:
            tmppos = univention.admin.uldap.position(self.position.getDomain())
            results = self.lo.search(base=tmppos.getBase(), scope='domain', attr=['zoneDn'], filter=filter_format('(&(objectClass=dNSZone)(|(pTRRecord=%s)(pTRRecord=%s.*)))', (name, name)), unique=False)
            for dn, _attr in results:
                log.debug('DEBUG: dn: "%s"', dn)
                zone = self.lo.parentDn(dn)
                log.debug('DEBUG: zone: "%s"', zone)
                try:
                    rdn = self.calc_dns_reverse_entry_name(ip, zone)
                    log.debug('DEBUG: rdn: "%s"', rdn)
                    modify(rdn, zone)
                except ValueError as ex:
                    log.debug('DEBUG: rdn: "%s"', ex)
                except univention.admin.uexceptions.noObject:
                    pass

    def __add_dns_reverse_object(self, name: str, zoneDn: str, ip: str) -> None:
        log.debug('we should create a dns reverse object: zoneDn="%s", name="%s", ip="%s"', zoneDn, name, ip)
        if not all((name, zoneDn, ip)):
            return

        addr, attr = self._ip2dns(ip)
        try:
            ipPart = self.calc_dns_reverse_entry_name(ip, zoneDn)
        except ValueError:
            raise univention.admin.uexceptions.missingInformation(_('Reverse zone and IP address are incompatible.'))

        tmppos = univention.admin.uldap.position(self.position.getDomain())
        results = self.lo.search(base=tmppos.getBase(), scope='domain', attr=['zoneName'], filter=filter_format('(&(relativeDomainName=%s)(zoneName=*)(%s=%s))', (name, attr, addr.exploded)), unique=False)
        hostname_list = {
            '%s.%s.' % (name, attr['zoneName'][0].decode('UTF-8'))
            for dn, attr in results
        }
        if not hostname_list:
            log.error('Could not determine host record for name=%r, ip=%r. Not creating pointer record.', name, ip)
            return

        results = self.lo.searchDn(base=tmppos.getBase(), scope='domain', filter=filter_format('(&(relativeDomainName=%s)(%s=%s))', [ipPart, *list(str2dn(zoneDn)[0][0][:2])]), unique=False)
        if not results:
            self.lo.add('relativeDomainName=%s,%s' % (escape_dn_chars(ipPart), zoneDn), [
                ('objectClass', [b'top', b'dNSZone', b'univentionObject']),
                ('univentionObjectType', [b'dns/ptr_record']),
                ('zoneName', [explode_rdn(zoneDn, True)[0].encode('UTF-8')]),
                ('relativeDomainName', [ipPart.encode('ASCII')]),
                ('PTRRecord', [x.encode('UTF-8') for x in hostname_list]),
            ])

            # update Serial
            zone = univention.admin.handlers.dns.reverse_zone.object(self.co, self.lo, self.position, zoneDn)
            zone.open()
            zone.modify()

    def __remove_dns_forward_object(self, name: str, zoneDn: str | None, ip: str | None = None) -> None:
        log.debug('we should remove a dns forward object: zoneDn="%s", name="%s", ip="%s"', zoneDn, name, ip)
        if name:
            # check if dns forward object has more than one ip address
            if not ip:
                if zoneDn:
                    self.lo.delete('relativeDomainName=%s,%s' % (escape_dn_chars(name), zoneDn))
                    fzo = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zoneDn)
                    fzo.open()
                    fzo.modify()
            else:
                if zoneDn:
                    base = zoneDn
                else:
                    tmppos = univention.admin.uldap.position(self.position.getDomain())
                    base = tmppos.getBase()
                log.debug('search base="%s"', base)
                if ':' in ip:
                    ip = IPv6Address('%s' % (ip,)).exploded
                    (attrEdit, attrOther) = ('aAAARecord', 'aRecord')
                else:
                    (attrEdit, attrOther) = ('aRecord', 'aAAARecord')
                results = self.lo.search(base=base, scope='domain', attr=['aRecord', 'aAAARecord'], filter=filter_format('(&(relativeDomainName=%s)(%s=%s))', (name, attrEdit, ip)), unique=False, required=False)
                for dn, attr in results:
                    if [x.decode('ASCII') for x in attr[attrEdit]] == [ip] and not attr.get(attrOther):  # the <ip> to be removed is the last on the object
                        # remove the object
                        self.lo.delete(dn)
                    else:
                        # remove only the ip address attribute
                        new_ip_list = copy.deepcopy(attr[attrEdit])
                        new_ip_list.remove(ip.encode('ASCII'))

                        self.lo.modify(dn, [(attrEdit, attr[attrEdit], new_ip_list)])

                    zone = zoneDn or self.lo.parentDn(dn)
                    fzo = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zone)
                    fzo.open()
                    fzo.modify()

    def __add_related_ptrrecords(self, zoneDN: str, ip: str) -> None:
        if not all((zoneDN, ip)):
            return
        ptrrecord = '%s.%s.' % (self.info['name'], explode_rdn(zoneDN, True)[0])
        ip_split = ip.split('.')
        ip_split.reverse()
        search_filter = filter_format('(|(relativeDomainName=%s)(relativeDomainName=%s)(relativeDomainName=%s))', (ip_split[0], '.'.join(ip_split[:1]), '.'.join(ip_split[:2])))

        for dn, _attributes in self.lo.search(base=zoneDN, scope='domain', attr=['pTRRecord'], filter=search_filter):
            self.lo.modify(dn, [('pTRRecord', '', ptrrecord)])

    def __remove_related_ptrrecords(self, zoneDN: str, ip: str) -> None:
        ptrrecord = '%s.%s.' % (self.info['name'], explode_rdn(zoneDN, True)[0])
        ip_split = ip.split('.')
        ip_split.reverse()
        search_filter = filter_format('(|(relativeDomainName=%s)(relativeDomainName=%s)(relativeDomainName=%s))', (ip_split[0], '.'.join(ip_split[:1]), '.'.join(ip_split[:2])))

        for dn, attributes in self.lo.search(base=zoneDN, scope='domain', attr=['pTRRecord'], filter=search_filter):
            if ptrrecord in attributes['pTRRecord']:
                self.lo.modify(dn, [('pTRRecord', ptrrecord, '')])

    def check_common_name_length(self) -> None:
        log.debug('check_common_name_length with self["ip"] = %r and self["dnsEntryZoneForward"] = %r', self['ip'], self['dnsEntryZoneForward'])
        if self['ip'] and self['dnsEntryZoneForward']:
            for zone in self['dnsEntryZoneForward']:
                if zone == '':
                    continue
                zoneName = explode_rdn(zone[0], True)[0]
                if len(zoneName) + len(self['name']) >= 63:
                    log.debug('simpleComputer: length of Common Name is too long: %d', len(zoneName) + len(self['name']) + 1)
                    raise univention.admin.uexceptions.commonNameTooLong()

    @staticmethod
    def _ip2dns(addr: str) -> tuple[IPv4Address | IPv6Address, str]:
        """
        Convert IP address string to 2-tuple (IPAddress, LdapAttributeName).

        :param addr: an IPv4 or IPv6 address.
        :returns: 2-tuple (IPAddress, LdapAttributeName)

        >>> simpleComputer._ip2dns('127.0.0.1')
        (IPv4Address(u'127.0.0.1'), 'aRecord')
        >>> simpleComputer._ip2dns('::1')
        (IPv6Address(u'::1'), 'aAAARecord')
        """
        ip = ip_address('%s' % (addr, ))
        return (ip, 'aAAARecord' if isinstance(ip, IPv6Address) else 'aRecord')

    def __modify_dns_forward_object(self, name: str, zoneDn: str | None, new_ip: str, old_ip: str) -> None:
        log.debug('we should modify a dns forward object: zoneDn="%s", name="%s", new_ip="%s", old_ip="%s"', zoneDn, name, new_ip, old_ip)
        zone: str | None = None
        if old_ip and new_ip:
            if not zoneDn:
                tmppos = univention.admin.uldap.position(self.position.getDomain())
                base = tmppos.getBase()
            else:
                base = zoneDn

            naddr, _nattr = self._ip2dns(new_ip)
            oaddr, oattr = self._ip2dns(old_ip)
            results = self.lo.search(base=base, scope='domain', attr=['aRecord', 'aAAARecord'], filter=filter_format('(&(relativeDomainName=%s)(%s=%s))', (name, oattr, old_ip)), unique=False)

            for dn, attr in results:
                old_aRecord = attr.get('aRecord', [])
                new_aRecord = copy.deepcopy(old_aRecord)
                old_aAAARecord = attr.get('aAAARecord', [])
                new_aAAARecord = copy.deepcopy(old_aAAARecord)

                if isinstance(oaddr, IPv6Address):
                    new_aAAARecord.remove(old_ip.encode('ASCII'))
                else:
                    new_aRecord.remove(old_ip.encode('ASCII'))

                ip = naddr.exploded.encode('ASCII')
                if isinstance(naddr, IPv6Address):
                    if ip not in new_aAAARecord:
                        new_aAAARecord.append(ip)
                else:
                    if ip not in new_aRecord:
                        new_aRecord.append(ip)

                modlist = []
                if old_aAAARecord != new_aAAARecord:
                    modlist.append(('aAAARecord', old_aAAARecord, new_aAAARecord))
                if old_aRecord != new_aRecord:
                    modlist.append(('aRecord', old_aRecord, new_aRecord))
                self.lo.modify(dn, modlist)
                if not zoneDn:
                    zone = self.lo.parentDn(dn)

            if zoneDn:
                zone = zoneDn

            if zone:
                log.debug('update the zone sOARecord for the zone: %s', zone)

                fzo = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zone)
                fzo.open()
                fzo.modify()

    def __add_dns_forward_object(self, name: str, zoneDn: str, ip: str) -> None:
        log.debug('we should add a dns forward object: zoneDn="%s", name="%s", ip="%s"', zoneDn, name, ip)
        if not all((name, ip, zoneDn)):
            return
        addr = ip_address('%s' % (ip,))
        if isinstance(addr, IPv6Address):
            self.__add_dns_forward_object_ipv6(name, zoneDn, addr)
        elif isinstance(addr, IPv4Address):
            self.__add_dns_forward_object_ipv4(name, zoneDn, addr)

    def __add_dns_forward_object_ipv6(self, name: str, zoneDn: str, addr: IPv6Address) -> None:
        ip = addr.exploded.encode('ASCII')
        results = self.lo.search(base=zoneDn, scope='domain', attr=['aAAARecord'], filter=filter_format('(&(relativeDomainName=%s)(!(cNAMERecord=*)))', (name,)), unique=False)
        if not results:
            try:
                self.lo.add('relativeDomainName=%s,%s' % (escape_dn_chars(name), zoneDn), [
                    ('objectClass', [b'top', b'dNSZone', b'univentionObject']),
                    ('univentionObjectType', [b'dns/host_record']),
                    ('zoneName', explode_rdn(zoneDn, True)[0].encode('UTF-8')),
                    ('aAAARecord', [ip]),
                    ('relativeDomainName', [name.encode('UTF-8')]),
                ])
            except univention.admin.uexceptions.objectExists as ex:
                raise univention.admin.uexceptions.dnsAliasRecordExists(ex.dn)
            # TODO: check if zoneDn really a forwardZone, maybe it is a container under a zone
            zone = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zoneDn)
            zone.open()
            zone.modify()
        else:
            for dn, attr in results:
                if 'aAAARecord' in attr:
                    new_ip_list = copy.deepcopy(attr['aAAARecord'])
                    if ip not in new_ip_list:
                        new_ip_list.append(ip)
                        self.lo.modify(dn, [('aAAARecord', attr['aAAARecord'], new_ip_list)])
                else:
                    self.lo.modify(dn, [('aAAARecord', b'', ip)])

    def __add_dns_forward_object_ipv4(self, name: str, zoneDn: str, addr: IPv4Address) -> None:
        ip = addr.exploded.encode('ASCII')
        results = self.lo.search(base=zoneDn, scope='domain', attr=['aRecord'], filter=filter_format('(&(relativeDomainName=%s)(!(cNAMERecord=*)))', (name,)), unique=False)
        if not results:
            try:
                self.lo.add('relativeDomainName=%s,%s' % (escape_dn_chars(name), zoneDn), [
                    ('objectClass', [b'top', b'dNSZone', b'univentionObject']),
                    ('univentionObjectType', [b'dns/host_record']),
                    ('zoneName', explode_rdn(zoneDn, True)[0].encode('UTF-8')),
                    ('ARecord', [ip]),
                    ('relativeDomainName', [name.encode('UTF-8')]),
                ])
            except univention.admin.uexceptions.objectExists as ex:
                raise univention.admin.uexceptions.dnsAliasRecordExists(ex.dn)
            # TODO: check if zoneDn really a forwardZone, maybe it is a container under a zone
            zone = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zoneDn)
            zone.open()
            zone.modify()
        else:
            for dn, attr in results:
                if 'aRecord' in attr:
                    new_ip_list = copy.deepcopy(attr['aRecord'])
                    if ip not in new_ip_list:
                        new_ip_list.append(ip)
                        self.lo.modify(dn, [('aRecord', attr['aRecord'], new_ip_list)])
                else:
                    self.lo.modify(dn, [('aRecord', b'', ip)])

    def __add_dns_alias_object(self, name: str, dnsForwardZone: str, dnsAliasZoneContainer: str, alias: str) -> None:
        log.debug('add a dns alias object: name="%s", dnsForwardZone="%s", dnsAliasZoneContainer="%s", alias="%s"', name, dnsForwardZone, dnsAliasZoneContainer, alias)
        alias = alias.rstrip('.')
        if name and dnsForwardZone and dnsAliasZoneContainer and alias:
            results = self.lo.search(base=dnsAliasZoneContainer, scope='domain', attr=['cNAMERecord'], filter=filter_format('relativeDomainName=%s', (alias,)), unique=False)
            if not results:
                self.lo.add('relativeDomainName=%s,%s' % (escape_dn_chars(alias), dnsAliasZoneContainer), [
                    ('objectClass', [b'top', b'dNSZone', b'univentionObject']),
                    ('univentionObjectType', [b'dns/alias']),
                    ('zoneName', explode_rdn(dnsAliasZoneContainer, True)[0].encode('UTF-8')),
                    ('cNAMERecord', [b"%s.%s." % (name.encode('UTF-8'), dnsForwardZone.encode('UTF-8'))]),
                    ('relativeDomainName', [alias.encode('UTF-8')]),
                ])

                # TODO: check if dnsAliasZoneContainer really is a forwardZone, maybe it is a container under a zone
                zone = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, dnsAliasZoneContainer)
                zone.open()
                zone.modify()
            else:
                # throw exception, cNAMERecord is single value
                raise univention.admin.uexceptions.dnsAliasAlreadyUsed(_('DNS alias is already in use.'))

    def __remove_dns_alias_object(self, name: str, dnsForwardZone: str, dnsAliasZoneContainer: str, alias: str | None = None) -> None:
        log.debug('remove a dns alias object: name="%s", dnsForwardZone="%s", dnsAliasZoneContainer="%s", alias="%s"', name, dnsForwardZone, dnsAliasZoneContainer, alias)
        if name:
            if alias:
                if dnsAliasZoneContainer:
                    self.lo.delete('relativeDomainName=%s,%s' % (escape_dn_chars(alias), dnsAliasZoneContainer))
                    zone = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, dnsAliasZoneContainer)
                    zone.open()
                    zone.modify()
                elif dnsForwardZone:
                    tmppos = univention.admin.uldap.position(self.position.getDomain())
                    base = tmppos.getBase()
                    log.debug('search base="%s"', base)
                    results = self.lo.search(base=base, scope='domain', attr=['zoneName'], filter=filter_format('(&(objectClass=dNSZone)(relativeDomainName=%s)(cNAMERecord=%s.%s.))', (alias, name, dnsForwardZone)), unique=False, required=False)
                    for dn, attr in results:
                        # remove the object
                        self.lo.delete(dn)
                        # and update the SOA version number for the zone
                        results = self.lo.searchDn(base=tmppos.getBase(), scope='domain', filter=filter_format('(&(objectClass=dNSZone)(zoneName=%s)(sOARecord=*))', (attr['zoneName'][0].decode('UTF-8'),)), unique=False)
                        for zoneDn in results:
                            zone = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zoneDn)
                            zone.open()
                            zone.modify()
            else:
                if dnsForwardZone:
                    tmppos = univention.admin.uldap.position(self.position.getDomain())
                    base = tmppos.getBase()
                    log.debug('search base="%s"', base)
                    results = self.lo.search(base=base, scope='domain', attr=['zoneName'], filter=filter_format('(&(objectClass=dNSZone)(&(cNAMERecord=%s)(cNAMERecord=%s.%s.))', (name, name, dnsForwardZone)), unique=False, required=False)
                    for dn, attr in results:
                        # remove the object
                        self.lo.delete(dn)
                        # and update the SOA version number for the zone
                        results = self.lo.searchDn(base=tmppos.getBase(), scope='domain', filter=filter_format('(&(objectClass=dNSZone)(zoneName=%s)(sOARecord=*))', (attr['zoneName'][0].decode('UTF-8'),)), unique=False)
                        for zoneDn in results:
                            zone = univention.admin.handlers.dns.forward_zone.object(self.co, self.lo, self.position, zoneDn)
                            zone.open()
                            zone.modify()
                else:  # not enough info to remove alias entries
                    pass

    def _ldap_post_modify(self) -> None:
        super()._ldap_post_modify()

        self.__multiip |= len(self['mac']) > 1 or len(self['ip']) > 1

        for entry in self.__changes['dhcpEntryZone']['remove']:
            log.debug('simpleComputer: dhcp check: removed: %s', entry)
            dn, ip, mac = self.__split_dhcp_line(entry)
            if not ip and not mac and not self.__multiip:
                mac = ''
                if self['mac']:
                    mac = self['mac'][0]
                self.__remove_from_dhcp_object(mac=mac)
            else:
                self.__remove_from_dhcp_object(ip=ip, mac=mac)

        for entry in self.__changes['dhcpEntryZone']['add']:
            log.debug('simpleComputer: dhcp check: added: %s', entry)
            dn, ip, mac = self.__split_dhcp_line(entry)
            if not ip and not mac and not self.__multiip:
                ip, mac = ('', '')
                if self['ip']:
                    ip = self['ip'][0]
                if self['mac']:
                    mac = self['mac'][0]
            self.__modify_dhcp_object(dn, mac, ip=ip)

        for entry in self.__changes['dnsEntryZoneForward']['remove']:
            dn, ip = self.__split_dns_line(entry)
            if not ip and not self.__multiip:
                ip = ''
                if self['ip']:
                    ip = self['ip'][0]
                self.__remove_dns_forward_object(self['name'], dn, ip)
                self.__remove_related_ptrrecords(dn, ip)
            else:
                self.__remove_dns_forward_object(self['name'], dn, ip)
                self.__remove_related_ptrrecords(dn, ip)

        for entry in self.__changes['dnsEntryZoneForward']['add']:
            log.debug('we should add a dns forward object "%s"', entry)
            dn, ip = self.__split_dns_line(entry)
            log.debug('changed the object to dn="%s" and ip="%s"', dn, ip)
            if not ip and not self.__multiip:
                log.debug('no multiip environment')
                ip = ''
                if self['ip']:
                    ip = self['ip'][0]
                self.__add_dns_forward_object(self['name'], dn, ip)
                self.__add_related_ptrrecords(dn, ip)
            else:
                self.__add_dns_forward_object(self['name'], dn, ip)
                self.__add_related_ptrrecords(dn, ip)

        for entry in self.__changes['dnsEntryZoneReverse']['remove']:
            dn, ip = self.__split_dns_line(entry)
            if not ip and not self.__multiip:
                ip = ''
                if self['ip']:
                    ip = self['ip'][0]
                self.__remove_dns_reverse_object(self['name'], dn, ip)
            else:
                self.__remove_dns_reverse_object(self['name'], dn, ip)

        for entry in self.__changes['dnsEntryZoneReverse']['add']:
            dn, ip = self.__split_dns_line(entry)
            if not ip and not self.__multiip:
                ip = ''
                if self['ip']:
                    ip = self['ip'][0]
                self.__add_dns_reverse_object(self['name'], dn, ip)
            else:
                self.__add_dns_reverse_object(self['name'], dn, ip)

        for entry in self.__changes['dnsEntryZoneAlias']['remove']:
            dnsForwardZone, dnsAliasZoneContainer, alias = entry
            if not alias:
                # nonfunctional code since self[ 'alias' ] should be self[ 'dnsAlias' ], but this case does not seem to occur
                self.__remove_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, self['alias'][0])
            else:
                self.__remove_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, alias)

        for entry in self.__changes['dnsEntryZoneAlias']['add']:
            log.debug('we should add a dns alias object "%s"', entry)
            dnsForwardZone, dnsAliasZoneContainer, alias = entry
            log.debug('changed the object to dnsForwardZone [%s], dnsAliasZoneContainer [%s] and alias [%s]', dnsForwardZone, dnsAliasZoneContainer, alias)
            if not alias:
                self.__add_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, self['alias'][0])
            else:
                self.__add_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, alias)

        for entry in self.__changes['mac']['remove']:
            self.__remove_from_dhcp_object(mac=entry)

        changed_ip = False
        for entry in self.__changes['ip']['remove']:
            # self.__remove_from_dhcp_object(ip=entry)
            if not self.__multiip:
                if self.__changes['ip']['add']:
                    # we change
                    single_ip = self.__changes['ip']['add'][0]
                    self.__modify_dns_forward_object(self['name'], None, single_ip, entry)
                    changed_ip = True
                    for mac in self['mac']:
                        dn = self.__remove_from_dhcp_object(ip=entry, mac=mac)
                        try:
                            dn = self.lo.parentDn(dn)
                            self.__modify_dhcp_object(dn, mac, ip=single_ip)
                        except Exception:
                            pass
                else:
                    # remove the dns objects
                    self.__remove_dns_forward_object(self['name'], None, entry)
            else:
                self.__remove_dns_forward_object(self['name'], None, entry)
                self.__remove_from_dhcp_object(ip=entry)

            self.__remove_dns_reverse_object(self['name'], None, entry)

        for entry in self.__changes['ip']['add']:
            if not self.__multiip:
                if self.get('dnsEntryZoneForward', []) and not changed_ip:
                    self.__add_dns_forward_object(self['name'], self['dnsEntryZoneForward'][0][0], entry)
                for dnsEntryZoneReverse in self.get('dnsEntryZoneReverse', []):
                    x, ip = self.__split_dns_line(dnsEntryZoneReverse)
                    zoneIsV6 = explode_rdn(x, True)[0].endswith('.ip6.arpa')
                    entryIsV6 = ':' in entry
                    if zoneIsV6 == entryIsV6:
                        self.__add_dns_reverse_object(self['name'], x, entry)

        if self.__changes['name']:
            log.debug('simpleComputer: name has changed')
            self.__update_groups_after_namechange()
            self.__rename_dhcp_object(old_name=self.__changes['name'][0], new_name=self.__changes['name'][1])
            self.__rename_dns_object(position=None, old_name=self.__changes['name'][0], new_name=self.__changes['name'][1])

        self.update_groups()

    def __remove_associated_domain(self, entry: list[str]) -> None:
        dn, _ip = self.__split_dns_line(entry)
        domain = explode_rdn(dn, 1)[0]
        if self.info.get('domain', None) == domain:
            self.info['domain'] = None

    def __set_associated_domain(self, entry: list[str]) -> None:
        dn, _ip = self.__split_dns_line(entry)
        domain = explode_rdn(dn, 1)[0]
        if not self.info.get('domain', None):
            self.info['domain'] = domain

    def _ldap_modlist(self) -> list[tuple[str, Any, Any]]:
        self.__changes = {
            'mac': {'remove': [], 'add': []},
            'ip': {'remove': [], 'add': []},
            'name': None,
            'dnsEntryZoneForward': {'remove': [], 'add': []},
            'dnsEntryZoneReverse': {'remove': [], 'add': []},
            'dnsEntryZoneAlias': {'remove': [], 'add': []},
            'dhcpEntryZone': {'remove': [], 'add': []},
        }
        ml: list[tuple[str, Any, Any]] = []
        if self.hasChanged('mac'):
            for macAddress in self.info.get('mac', []):
                if macAddress in self.oldinfo.get('mac', []):
                    continue
                try:
                    self.__changes['mac']['add'].append(self.request_lock('mac', macAddress))
                except univention.admin.uexceptions.noLock:
                    raise univention.admin.uexceptions.macAlreadyUsed(macAddress)
            for macAddress in self.oldinfo.get('mac', []):
                if macAddress in self.info.get('mac', []):
                    continue
                self.__changes['mac']['remove'].append(macAddress)

        oldAddresses = self.oldinfo.get('ip') or ()
        newAddresses = self.info.get('ip') or ()
        if oldAddresses != newAddresses:
            old_addr = [ip_address('%s' % addr) for addr in oldAddresses]
            old_ipv4 = [addr.exploded.encode('ASCII') for addr in old_addr if isinstance(addr, IPv4Address)]
            old_ipv6 = [addr.exploded.encode('ASCII') for addr in old_addr if isinstance(addr, IPv6Address)]
            new_addr = [ip_address('%s' % addr) for addr in newAddresses]
            new_ipv4 = [addr.exploded.encode('ASCII') for addr in new_addr if isinstance(addr, IPv4Address)]
            new_ipv6 = [addr.exploded.encode('ASCII') for addr in new_addr if isinstance(addr, IPv6Address)]
            ml.append(('aRecord', old_ipv4, new_ipv4))
            ml.append(('aAAARecord', old_ipv6, new_ipv6))

        if self.hasChanged('ip'):
            for ipAddress in self['ip']:
                if not ipAddress:
                    continue
                if ipAddress in self.oldinfo.get('ip'):
                    continue
                if not self.ip_already_requested:
                    try:
                        ipAddress = self.request_lock('aRecord', ipAddress)
                    except univention.admin.uexceptions.noLock:
                        self.ip_already_requested = 0
                        raise univention.admin.uexceptions.ipAlreadyUsed(ipAddress)

                self.__changes['ip']['add'].append(ipAddress)

            for ipAddress in self.oldinfo.get('ip', []):
                if ipAddress in self.info['ip']:
                    continue
                self.__changes['ip']['remove'].append(ipAddress)

        if self.hasChanged('name'):
            ml.append(('sn', self.oldattr.get('sn', [None])[0], self['name'].encode('UTF-8')))
            self.__changes['name'] = (self.oldattr.get('sn', [b''])[0].decode("UTF-8") or None, self['name'])

        if self.hasChanged('ip') or self.hasChanged('mac'):
            dhcp = [self.__split_dhcp_line(entry) for entry in self.info.get('dhcpEntryZone', [])]
            if len(newAddresses) <= 1 and len(self.info.get('mac', [])) == 1 and dhcp:
                # In this special case, we assume the mapping between ip/mac address to be
                # unique. The dhcp entry needs to contain the mac address (as specified by
                # the ldap search for dhcp entries), the ip address may not correspond to
                # the ip address associated with the computer ldap object, but this would
                # be erroneous anyway. We therefore update the dhcp entry to correspond to
                # the current ip and mac address. (Bug #20315)
                self.info['dhcpEntryZone'] = [
                    (dn, newAddresses[0] if newAddresses else '', self.info['mac'][0])
                    for (dn, ip, _mac) in dhcp
                ]
            else:
                # in all other cases, we remove old dhcp entries that do not match ip or
                # mac addresses (Bug #18966)
                removedIPs = set(self.oldinfo.get('ip', [])) - set(self['ip'])
                removedMACs = set(self.oldinfo.get('mac', [])) - set(self['mac'])
                self.info['dhcpEntryZone'] = [
                    (dn, ip, _mac)
                    for (dn, ip, _mac) in dhcp
                    if not (ip in removedIPs or _mac in removedMACs)
                ]

        if self.hasChanged('dhcpEntryZone'):
            if 'dhcpEntryZone' in self.oldinfo:
                if 'dhcpEntryZone' in self.info:
                    for entry in self.oldinfo['dhcpEntryZone']:
                        if entry not in self.info['dhcpEntryZone']:
                            self.__changes['dhcpEntryZone']['remove'].append(entry)
                else:
                    for entry in self.oldinfo['dhcpEntryZone']:
                        self.__changes['dhcpEntryZone']['remove'].append(entry)
            if 'dhcpEntryZone' in self.info:
                for entry in self.info['dhcpEntryZone']:
                    # check if line is valid
                    dn, _ip, mac = self.__split_dhcp_line(entry)
                    if dn and mac:
                        if entry not in self.oldinfo.get('dhcpEntryZone', []):
                            self.__changes['dhcpEntryZone']['add'].append(entry)
                    else:
                        raise univention.admin.uexceptions.invalidDhcpEntry(_('The DHCP entry for this host should contain the zone LDAP-DN, the IP address and the MAC address.'))

        if self.hasChanged('dnsEntryZoneForward'):
            for entry in self.oldinfo.get('dnsEntryZoneForward', []):
                if entry not in self.info.get('dnsEntryZoneForward', []):
                    self.__changes['dnsEntryZoneForward']['remove'].append(entry)
                    self.__remove_associated_domain(entry)
            for entry in self.info.get('dnsEntryZoneForward', []):
                if entry == '':
                    continue
                if entry not in self.oldinfo.get('dnsEntryZoneForward', []):
                    self.__changes['dnsEntryZoneForward']['add'].append(entry)
                self.__set_associated_domain(entry)

        if self.hasChanged('dnsEntryZoneReverse'):
            for entry in self.oldinfo.get('dnsEntryZoneReverse', []):
                if entry not in self.info.get('dnsEntryZoneReverse', []):
                    self.__changes['dnsEntryZoneReverse']['remove'].append(entry)
            for entry in self.info.get('dnsEntryZoneReverse', []):
                if entry not in self.oldinfo.get('dnsEntryZoneReverse', []):
                    self.__changes['dnsEntryZoneReverse']['add'].append(entry)

        if self.hasChanged('dnsEntryZoneAlias'):
            for entry in self.oldinfo.get('dnsEntryZoneAlias', []):
                if entry not in self.info.get('dnsEntryZoneAlias', []):
                    self.__changes['dnsEntryZoneAlias']['remove'].append(entry)
            for entry in self.info.get('dnsEntryZoneAlias', []):
                # check if line is valid
                dnsForwardZone, dnsAliasZoneContainer, alias = entry
                if dnsForwardZone and dnsAliasZoneContainer and alias:
                    if entry not in self.oldinfo.get('dnsEntryZoneAlias', []):
                        self.__changes['dnsEntryZoneAlias']['add'].append(entry)
                else:
                    raise univention.admin.uexceptions.invalidDNSAliasEntry(_('The DNS alias entry for this host should contain the zone name, the alias zone container LDAP-DN and the alias.'))

        self.__multiip = len(self['mac']) > 1 or len(self['ip']) > 1

        ml += super()._ldap_modlist()

        return ml

    @classmethod
    def calc_dns_reverse_entry_name(cls, sip: str, reverseDN: str) -> str:
        """
        >>> simpleComputer.calc_dns_reverse_entry_name('10.200.2.5', 'subnet=2.200.10.in-addr.arpa')
        u'5'
        >>> simpleComputer.calc_dns_reverse_entry_name('10.200.2.5', 'subnet=200.10.in-addr.arpa')
        u'5.2'
        >>> simpleComputer.calc_dns_reverse_entry_name('2001:db8::3', 'subnet=0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa')
        u'3.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0'
        >>> simpleComputer.calc_dns_reverse_entry_name('1.2.3.4', 'subnet=2.in-addr.arpa')
        Traceback (most recent call last):
                ...
        ValueError: 4.3.2.1.in-addr.arpa not in .2.in-addr.arpa
        """
        addr = ip_address('%s' % (sip,))
        rev = addr.reverse_pointer
        subnet = ".%s" % (explode_rdn(reverseDN, True)[0],)
        if not rev.endswith(subnet):
            raise ValueError("%s not in %s" % (rev, subnet))
        return rev[:-len(subnet)]

    def _ldap_pre_create(self) -> None:
        super()._ldap_pre_create()
        self.check_common_name_length()

    def _ldap_pre_modify(self) -> None:
        super()._ldap_pre_modify()
        self.check_common_name_length()

    def _ldap_post_create(self) -> None:
        super()._ldap_post_create()
        for entry in self.__changes['dhcpEntryZone']['remove']:
            log.debug('simpleComputer: dhcp check: removed: %s', entry)
            dn, ip, mac = self.__split_dhcp_line(entry)
            if not ip and not mac and not self.__multiip:
                mac = self['mac'][0] if self['mac'] else ''
                self.__remove_from_dhcp_object(mac=mac)
            else:
                self.__remove_from_dhcp_object(ip=ip, mac=mac)

        for entry in self.__changes['dhcpEntryZone']['add']:
            log.debug('simpleComputer: dhcp check: added: %s', entry)
            dn, ip, mac = self.__split_dhcp_line(entry)
            if not ip and not mac and not self.__multiip:
                if self['ip'] and self['mac']:
                    self.__modify_dhcp_object(dn, self['mac'][0], ip=self['ip'][0])
            else:
                self.__modify_dhcp_object(dn, mac, ip=ip)

        for entry in self.__changes['dnsEntryZoneForward']['remove']:
            dn, ip = self.__split_dns_line(entry)
            if not ip and not self.__multiip:
                ip = self['ip'][0] if self['ip'] else ''
                self.__remove_dns_forward_object(self['name'], dn, ip)
            else:
                self.__remove_dns_forward_object(self['name'], dn, ip)

        for entry in self.__changes['dnsEntryZoneForward']['add']:
            log.debug('we should add a dns forward object "%s"', entry)
            dn, ip = self.__split_dns_line(entry)
            log.debug('changed the object to dn="%s" and ip="%s"', dn, ip)
            if not ip and not self.__multiip:
                log.debug('no multiip environment')
                ip = self['ip'][0] if self['ip'] else ''
                self.__add_dns_forward_object(self['name'], dn, ip)
            else:
                self.__add_dns_forward_object(self['name'], dn, ip)

        for entry in self.__changes['dnsEntryZoneReverse']['remove']:
            dn, ip = self.__split_dns_line(entry)
            if not ip and not self.__multiip:
                ip = self['ip'][0] if self['ip'] else ''
                self.__remove_dns_reverse_object(self['name'], dn, ip)
            else:
                self.__remove_dns_reverse_object(self['name'], dn, ip)

        for entry in self.__changes['dnsEntryZoneReverse']['add']:
            dn, ip = self.__split_dns_line(entry)
            if not ip and not self.__multiip:
                ip = self['ip'][0] if self['ip'] else ''
                self.__add_dns_reverse_object(self['name'], dn, ip)
            else:
                self.__add_dns_reverse_object(self['name'], dn, ip)

        if not self.__multiip and self.get('dhcpEntryZone', []):
            dn, ip, mac = self['dhcpEntryZone'][0]
            for entry in self.__changes['mac']['add']:
                if self['ip']:
                    self.__modify_dhcp_object(dn, entry, ip=self['ip'][0])
                else:
                    self.__modify_dhcp_object(dn, entry)
            if self['mac']:
                for entry in self.__changes['ip']['add']:
                    self.__modify_dhcp_object(dn, self['mac'][0], ip=entry)

        for entry in self.__changes['dnsEntryZoneAlias']['remove']:
            dnsForwardZone, dnsAliasZoneContainer, alias = entry
            # nonfunctional code since self['alias'] should be self['dnsAlias'], but this case does not seem to occur
            self.__remove_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, alias or self['alias'][0])

        for entry in self.__changes['dnsEntryZoneAlias']['add']:
            log.debug('we should add a dns alias object "%s"', entry)
            dnsForwardZone, dnsAliasZoneContainer, alias = entry
            log.debug('changed the object to dnsForwardZone [%s], dnsAliasZoneContainer [%s] and alias [%s]', dnsForwardZone, dnsAliasZoneContainer, alias)
            self.__add_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, alias or self['alias'][0])

        self.update_groups()

    def _ldap_post_remove(self) -> None:
        if self['mac']:
            for macAddress in self['mac']:
                if macAddress:
                    self.alloc.append(('mac', macAddress))
        if self['ip']:
            for ipAddress in self['ip']:
                if ipAddress:
                    self.alloc.append(('aRecord', ipAddress))
        super()._ldap_post_remove()

        # remove computer from groups
        groups = copy.deepcopy(self['groups'])
        if self.oldinfo.get('primaryGroup'):
            groups.append(self.oldinfo.get('primaryGroup'))
        for group in groups:
            groupObject = univention.admin.objects.get(univention.admin.modules.get('groups/group'), self.co, self.lo, self.position, group)
            groupObject.fast_member_remove([self.dn], [x.decode('UTF-8') for x in self.oldattr.get('uid', [])], ignore_license=True)

    def __update_groups_after_namechange(self) -> None:
        oldname = self.oldinfo.get('name')
        newname = self.info.get('name')
        if not oldname:
            log.error('__update_groups_after_namechange: oldname is empty')
            return

        olddn = self.old_dn.encode('UTF-8')
        newdn = self.dn.encode('UTF-8')

        oldUid = b'%s$' % oldname.encode('UTF-8')
        newUid = b'%s$' % newname.encode('UTF-8')
        log.debug('__update_groups_after_namechange: olddn=%s', olddn)
        log.debug('__update_groups_after_namechange: newdn=%s', newdn)

        new_groups = set(self.info.get('groups', []))
        old_groups = set(self.oldinfo.get('groups', []))
        for group in new_groups | old_groups:

            # Using the UDM groups/group object does not work at this point. The computer object has already been renamed.
            # During open() of groups/group each member is checked if it exists. Because the computer object with "olddn" is missing,
            # it won't show up in groupobj['hosts']. That's why the uniqueMember/memberUid updates is done directly via
            # self.lo.modify()

            oldMemberUids = self.lo.getAttr(group, 'memberUid')
            newMemberUids = copy.deepcopy(oldMemberUids)
            if group in new_groups:
                log.debug('__update_groups_after_namechange: changing memberUid in grp=%s', group)
                if oldUid in newMemberUids:
                    newMemberUids.remove(oldUid)
                if newUid not in newMemberUids:
                    newMemberUids.append(newUid)
                self.lo.modify(group, [('memberUid', oldMemberUids, newMemberUids)])
            else:
                log.debug('__update_groups_after_namechange: removing memberUid from grp=%s', group)
                if oldUid in oldMemberUids:
                    oldMemberUids = oldUid
                    newMemberUids = b''
                    self.lo.modify(group, [('memberUid', oldMemberUids, newMemberUids)])

            # we are doing the uniqueMember seperately because of a potential refint overlay that already changed the dn for us
            oldUniqueMembers = self.lo.getAttr(group, 'uniqueMember')
            newUniqueMembers = copy.deepcopy(oldUniqueMembers)
            if group in new_groups:
                log.debug('__update_groups_after_namechange: changing uniqueMember in grp=%s', group)
                if olddn in newUniqueMembers:
                    newUniqueMembers.remove(olddn)
                if newdn not in newUniqueMembers:
                    newUniqueMembers.append(newdn)
                self.lo.modify(group, [('uniqueMember', oldUniqueMembers, newUniqueMembers)])
            else:
                if olddn in oldUniqueMembers:
                    log.debug('__update_groups_after_namechange: removing uniqueMember from grp=%s', group)
                    oldUniqueMembers = olddn
                    newUniqueMembers = b''
                    self.lo.modify(group, [('uniqueMember', oldUniqueMembers, newUniqueMembers)])
                if newdn in oldUniqueMembers:
                    log.debug('__update_groups_after_namechange: removing uniqueMember from grp=%s', group)
                    oldUniqueMembers = newdn
                    newUniqueMembers = b''
                    self.lo.modify(group, [('uniqueMember', oldUniqueMembers, newUniqueMembers)])

    def update_groups(self) -> None:
        if not self.hasChanged('groups') and not self.oldPrimaryGroupDn and not self.newPrimaryGroupDn:
            return
        log.debug('updating groups')

        old_groups = DN.set(self.oldinfo.get('groups', []))
        new_groups = DN.set(self.info.get('groups', []))

        if self.oldPrimaryGroupDn:
            old_groups += DN.set([self.oldPrimaryGroupDn])

        if self.newPrimaryGroupDn:
            new_groups.add(DN(self.newPrimaryGroupDn))

        # prevent machineAccountGroup from being removed
        if self.has_property('machineAccountGroup'):
            machine_account_group = DN.set([self['machineAccountGroup']])
            new_groups += machine_account_group
            old_groups -= machine_account_group

        for group in old_groups ^ new_groups:
            groupdn = str(group)
            groupObject = univention.admin.objects.get(univention.admin.modules.get('groups/group'), self.co, self.lo, self.position, groupdn)
            assert groupObject is not None
            groupObject.open()
            # add this computer to the group
            hosts = DN.set(groupObject['hosts'])
            if group not in new_groups:
                # remove this computer from the group
                hosts.discard(DN(self.old_dn))
            else:
                hosts.add(DN(self.dn))
            groupObject['hosts'] = list(DN.values(hosts))
            groupObject.modify(ignore_license=True)

    def primary_group(self) -> None:
        if not self.hasChanged('primaryGroup'):
            return
        log.debug('updating primary groups')

        primaryGroupNumber = self.lo.getAttr(self['primaryGroup'], 'gidNumber', required=True)
        self.newPrimaryGroupDn = self['primaryGroup']
        self.lo.modify(self.dn, [('gidNumber', b'None', primaryGroupNumber[0])])

        if 'samba' in self.options:
            primaryGroupSambaNumber = self.lo.getAttr(self['primaryGroup'], 'sambaSID', required=True)
            self.lo.modify(self.dn, [('sambaPrimaryGroupSID', b'None', primaryGroupSambaNumber[0])])

    def cleanup(self) -> None:
        self.open()
        if self['dnsEntryZoneForward']:
            for dnsEntryZoneForward in self['dnsEntryZoneForward']:
                dn, ip = self.__split_dns_line(dnsEntryZoneForward)
                try:
                    self.__remove_dns_forward_object(self['name'], dn, None)
                except Exception as e:
                    log.warning('dnsEntryZoneForward.delete(%s): %s', dnsEntryZoneForward, e)

        if self['dnsEntryZoneReverse']:
            for dnsEntryZoneReverse in self['dnsEntryZoneReverse']:
                dn, ip = self.__split_dns_line(dnsEntryZoneReverse)
                try:
                    self.__remove_dns_reverse_object(self['name'], dn, ip)
                except Exception as e:
                    log.warning('dnsEntryZoneReverse.delete(%s): %s', dnsEntryZoneReverse, e)

        if self['dhcpEntryZone']:
            for dhcpEntryZone in self['dhcpEntryZone']:
                dn, ip, mac = self.__split_dhcp_line(dhcpEntryZone)
                try:
                    self.__remove_from_dhcp_object(mac=mac)
                except Exception as e:
                    log.warning('dhcpEntryZone.delete(%s): %s', dhcpEntryZone, e)

        if self['dnsEntryZoneAlias']:
            for entry in self['dnsEntryZoneAlias']:
                dnsForwardZone, dnsAliasZoneContainer, alias = entry
                try:
                    self.__remove_dns_alias_object(self['name'], dnsForwardZone, dnsAliasZoneContainer, alias)
                except Exception as e:
                    log.warning('dnsEntryZoneAlias.delete(%s): %s', entry, e)

        # remove service record entries (see Bug #26400)
        log.debug('_ldap_post_remove: clean up service records, host records, and IP address saved at the forward zone')
        ips = set(self['ip'] or [])
        fqdn = self['fqdn']
        fqdnDot = '%s.' % fqdn  # we might have entries w/ or w/out trailing '.'

        # iterate over all reverse zones
        for zone in self['dnsEntryZoneReverse'] or []:
            # load zone object
            log.debug('clean up entries for zone: %s', zone)
            if not zone:
                continue
            zoneObj = univention.admin.objects.get(
                univention.admin.modules.get('dns/reverse_zone'), self.co, self.lo, self.position, dn=zone[0])
            assert zoneObj is not None
            zoneObj.open()

            # clean up nameserver records
            if 'nameserver' in zoneObj and fqdnDot in zoneObj['nameserver']:
                log.debug('removing %s from dns zone %s', fqdnDot, zone[0])
                # nameserver is required in reverse zone
                if len(zoneObj['nameserver']) > 1:
                    zoneObj['nameserver'].remove(fqdnDot)
                    zoneObj.modify()

        # iterate over all forward zones
        for zone in self['dnsEntryZoneForward'] or []:
            # load zone object
            log.debug('clean up entries for zone: %s', zone)
            if not zone:
                continue
            zoneObj = univention.admin.objects.get(
                univention.admin.modules.get('dns/forward_zone'), self.co, self.lo, self.position, dn=zone[0])
            assert zoneObj is not None
            zoneObj.open()
            log.debug('zone aRecords: %s', zoneObj['a'])

            zone_obj_modified = False
            # clean up nameserver records
            if 'nameserver' in zoneObj and fqdnDot in zoneObj['nameserver']:
                log.debug('removing %s from dns zone %s', fqdnDot, zone)
                # nameserver is required in forward zone
                if len(zoneObj['nameserver']) > 1:
                    zoneObj['nameserver'].remove(fqdnDot)
                    zone_obj_modified = True

            # clean up aRecords of zone itself
            new_entries = list(set(zoneObj['a']) - ips)
            if len(new_entries) != len(zoneObj['a']):
                log.debug('Clean up zone records:\n%s ==> %s', zoneObj['a'], new_entries)
                zoneObj['a'] = new_entries
                zone_obj_modified = True

            if zone_obj_modified:
                zoneObj.modify()

            # clean up service records
            for irecord in univention.admin.modules.lookup('dns/srv_record', self.co, self.lo, base=self.lo.base, scope='sub', superordinate=zoneObj):
                irecord.open()
                new_entries = [j for j in irecord['location'] if fqdn not in j and fqdnDot not in j]
                if len(new_entries) != len(irecord['location']):
                    log.debug('Entry found in "%s":\n%s ==> %s', irecord.dn, irecord['location'], new_entries)
                    irecord['location'] = new_entries
                    irecord.modify()

            # clean up host records (that should probably be done correctly by Samba4)
            for irecord in univention.admin.modules.lookup('dns/host_record', self.co, self.lo, base=self.lo.base, scope='sub', superordinate=zoneObj):
                irecord.open()
                new_entries = list(set(irecord['a']) - ips)
                if len(new_entries) != len(irecord['a']):
                    log.debug('Entry found in "%s":\n%s ==> %s', irecord.dn, irecord['a'], new_entries)
                    irecord['a'] = new_entries
                    irecord.modify()

    def __setitem__(self, key: str, value: object) -> None:
        raise_after = None

        ips = [ip for ip in self['ip'] if ip] if self.has_property('ip') and self['ip'] else []
        ip1 = self['ip'][0] if len(ips) == 1 else ''
        macs = [mac for mac in self['mac'] if mac] if self.has_property('mac') and self['mac'] else []
        mac1 = self['mac'][0] if len(macs) == 1 else ''

        if key == 'network':
            if self.old_network != value and value and value != 'None':
                assert isinstance(value, str)
                network_object = univention.admin.handlers.networks.network.object(self.co, self.lo, self.position, value)
                network_object.open()
                subnet = ip_network("%(network)s/%(netmask)s" % network_object, strict=False)

                if not ips or ip_address('%s' % (ip1,)) not in subnet:
                    if self.ip_freshly_set:
                        raise_after = univention.admin.uexceptions.ipOverridesNetwork
                    else:
                        # get next IP
                        network_object.refreshNextIp()
                        self['ip'] = network_object['nextIp']
                        ips = [ip for ip in self['ip'] if ip] if self.has_property('ip') and self['ip'] else []
                        ip1 = self['ip'][0] if len(ips) == 1 else ''
                        try:
                            self.ip = self.request_lock('aRecord', self['ip'][0])
                            self.ip_already_requested = True
                        except univention.admin.uexceptions.noLock:
                            pass

                    self.network_object = network_object
                if network_object['dnsEntryZoneForward'] and ip1:
                    self['dnsEntryZoneForward'] = [[network_object['dnsEntryZoneForward'], ip1]]
                if network_object['dnsEntryZoneReverse'] and ip1:
                    self['dnsEntryZoneReverse'] = [[network_object['dnsEntryZoneReverse'], ip1]]
                if network_object['dhcpEntryZone']:
                    if ip1 and mac1:
                        self['dhcpEntryZone'] = [(network_object['dhcpEntryZone'], ip1, mac1)]
                    else:
                        self.__saved_dhcp_entry = network_object['dhcpEntryZone']

                self.old_network = value

        elif key == 'ip':

            ips = [ip for ip in value if ip] if self.has_property('ip') else []
            ip1 = ips[0] if len(ips) >= 1 else ''

            self.ip_freshly_set = True
            if not self.ip or self.ip != value:
                if self.ip_already_requested:
                    univention.admin.allocators.release(self.lo, self.position, 'aRecord', self.ip)
                    self.ip_already_requested = 0
                if value and self.network_object:
                    if self.network_object['dnsEntryZoneForward'] and ip1:
                        self['dnsEntryZoneForward'] = [[self.network_object['dnsEntryZoneForward'], ip1]]
                    if self.network_object['dnsEntryZoneReverse'] and ip1:
                        self['dnsEntryZoneReverse'] = [[self.network_object['dnsEntryZoneReverse'], ip1]]
                    if self.network_object['dhcpEntryZone']:
                        if ip1 and macs:
                            self['dhcpEntryZone'] = [(self.network_object['dhcpEntryZone'], ip1, mac1)]
                        else:
                            self.__saved_dhcp_entry = self.network_object['dhcpEntryZone']
            if not self.ip:
                self.ip_freshly_set = False

        elif key == 'mac' and self.__saved_dhcp_entry and ip1 and macs:
            if isinstance(value, list):
                self['dhcpEntryZone'] = [(self.__saved_dhcp_entry, ip1, value[0])]
            else:
                self['dhcpEntryZone'] = [(self.__saved_dhcp_entry, ip1, value)]

        super().__setitem__(key, value)
        if raise_after:
            raise raise_after


class simplePolicy(simpleLdap):

    def __init__(
        self,
        co,  # None
        lo,  # univention.admin.uldap.access
        position,  # univention.admin.uldap.position
        dn: str = '',
        superordinate: simpleLdap | None = None,
        attributes: _Attributes | None = None,
    ) -> None:
        self.resultmode = 0

        if not hasattr(self, 'cloned'):
            self.cloned: str | None = None

        if not hasattr(self, 'changes'):
            self.changes = 0

        if not hasattr(self, 'policy_attrs'):
            self.policy_attrs: dict[str, dict[str, Any]] = {}

        if not hasattr(self, 'referring_object_dn'):
            self.referring_object_dn: str | None = None

        simpleLdap.__init__(self, co, lo, position, dn, superordinate, attributes)

    def _ldap_post_remove(self) -> None:
        super()._ldap_post_remove()
        for object_dn in self.lo.searchDn(filter_format('univentionPolicyReference=%s', [self.dn])):
            try:
                self.lo.modify(object_dn, [('univentionPolicyReference', self.dn.encode('UTF-8'), None)])
            except (univention.admin.uexceptions.base, ldap.LDAPError) as exc:
                log.error('Could not remove policy reference %r from %r: %s', self.dn, object_dn, exc)

    def copyIdentifier(self, from_object: simpleLdap) -> None:
        """Activate the result mode and set the referring object"""
        self.resultmode = 1
        for key, property in from_object.descriptions.items():
            if property.identifies:
                for key2, property2 in self.descriptions.items():
                    if property2.identifies:
                        self.info[key2] = from_object.info[key]
        self.referring_object_dn = from_object.dn
        if not self.referring_object_dn:
            self.referring_object_dn = from_object.position.getDn()
        self.referring_object_position_dn = from_object.position.getDn()

    def clone(self, referring_object: simpleLdap) -> None:
        """
        Marks the object as a not existing one containing values
        retrieved by evaluating the policies for the given object
        """
        self.cloned = self.dn
        self.dn = ''
        self.copyIdentifier(referring_object)

    def getIdentifier(self) -> str:
        for key, property in self.descriptions.items():
            if property.identifies and key in self.info and self.info[key]:
                return key
        raise ValueError()

    def __makeUnique(self) -> None:
        identifier = self.getIdentifier()
        components = self.info[identifier].split("_uv")
        if len(components) > 1:
            try:
                n = int(components[1])
                n += 1
            except ValueError:
                n = 1
        else:
            n = 0
        self.info[identifier] = "%s_uv%d" % (components[0], n)
        log.debug('simplePolicy.__makeUnique: result: %s', self.info[identifier])

    def create(self, serverctrls: list[ldap.controls.LDAPControl] | None = None, response: dict[str, Any] | None = None) -> str:
        if not self.resultmode:
            return super().create(serverctrls=serverctrls, response=response)

        self._exists = False
        try:
            self.oldinfo = {}
            dn = super().create(serverctrls=serverctrls, response=response)
            log.debug('simplePolicy.create: created object: info=%s', self.info)
        except univention.admin.uexceptions.objectExists:
            self.__makeUnique()
            dn = self.create()
        return dn

    def policy_result(self, faked_policy_reference: str | list[str] | None = None) -> None:
        """
        This method retrieves the policy values currently effective
        for this object. If the 'resultmode' is not active the evaluation
        is cancelled.

        If faked_policy_reference is given at the top object
        (referring_object_dn) this policy object temporarily referenced.

        faked_policy_reference can be a string or a list of strings.
        """
        if not self.resultmode:
            return

        self.polinfo_more = {}
        if not self.policy_attrs:
            policies = []
            if isinstance(faked_policy_reference, list | tuple):
                policies.extend(faked_policy_reference)
            elif faked_policy_reference:
                policies.append(faked_policy_reference)

            self.__load_policies(policies)

        if hasattr(self, '_custom_policy_result_map'):
            self._custom_policy_result_map()
        else:
            values = {}
            for attr_name, value_dict in self.policy_attrs.items():
                value_dict = copy.deepcopy(value_dict)
                values[attr_name] = copy.copy(value_dict['value'])
                value_dict['value'] = [x.decode('UTF-8') for x in value_dict['value']]
                self.polinfo_more[self.mapping.unmapName(attr_name)] = value_dict

            self.polinfo = univention.admin.mapping.mapDict(self.mapping, values)
            self.polinfo = self._post_unmap(self.polinfo, values)

    def __load_policies(self, policies: list[str] | None = None) -> None:
        if not self.policy_attrs:
            # the referring object does not exist yet
            if self.referring_object_dn != self.referring_object_position_dn:
                result = self.lo.getPolicies(self.lo.parentDn(self.referring_object_dn), policies=policies)
            else:
                result = self.lo.getPolicies(self.referring_object_position_dn, policies=policies)
            for policy_oc, attrs in result.items():
                if univention.admin.objects.ocToType(policy_oc) == self.module:
                    self.policy_attrs = attrs

    def __getitem__(self, key: str) -> object:
        if not self.resultmode:
            if self.has_property('emptyAttributes') and self.mapping.mapName(key) and self.mapping.mapName(key) in simpleLdap.__getitem__(self, 'emptyAttributes'):
                log.debug('simplePolicy.__getitem__: empty Attribute %s', key)
                if self.descriptions[key].multivalue:
                    return []
                else:
                    return ''
            return simpleLdap.__getitem__(self, key)

        self.policy_result()

        if (key in self.polinfo and not (key in self.info or key in self.oldinfo)) or (key in self.polinfo_more and 'fixed' in self.polinfo_more[key] and self.polinfo_more[key]['fixed']):
            if self.descriptions[key].multivalue and not isinstance(self.polinfo[key], list):
                # why isn't this correct in the first place?
                self.polinfo[key] = [self.polinfo[key]]
            log.debug('simplePolicy.__getitem__: presult: %s=%s', key, self.polinfo[key])
            return self.polinfo[key]

        result = simpleLdap.__getitem__(self, key)
        log.debug('simplePolicy.__getitem__: result: %s=%s', key, result)
        return result

    def fixedAttributes(self) -> dict[str, bool]:
        """Return effectively fixed attributes."""
        if not self.resultmode:
            return {}

        self.__load_policies(None)
        return {
            self.mapping.unmapName(attr_name): value_dict.get('fixed', False)
            for attr_name, value_dict in self.policy_attrs.items()
        }

    def emptyAttributes(self) -> dict[str, bool]:
        """return effectively empty attributes."""
        if not self.has_property('emptyAttributes'):
            return {}

        return {
            self.mapping.unmapName(attrib): True
            for attrib in simpleLdap.__getitem__(self, 'emptyAttributes') or ()
        }

    def __setitem__(self, key: str, newvalue: object) -> None:
        if not self.resultmode:
            simpleLdap.__setitem__(self, key, newvalue)
            return

        self.policy_result()

        if key in self.polinfo:
            if self.polinfo[key] != newvalue or self.polinfo_more[key]['policy'] == self.cloned or (key in self.info and self.info[key] != newvalue):
                if self.polinfo_more[key]['fixed'] and self.polinfo_more[key]['policy'] != self.cloned:
                    raise univention.admin.uexceptions.policyFixedAttribute(key)
                simpleLdap.__setitem__(self, key, newvalue)
                log.debug('polinfo: set key %s to newvalue %s', key, newvalue)
                if self.hasChanged(key):
                    log.debug('polinfo: key:%s hasChanged', key)
                    self.changes = 1
            return

        # this object did not exist before
        if not self.oldinfo:
            # if this attribute is of type boolean and the new value is equal to the default, than ignore this "change"
            if isinstance(self.descriptions[key].syntax, univention.admin.syntax.boolean):
                default = self.descriptions[key].base_default
                if isinstance(self.descriptions[key].base_default, tuple | list):
                    default = self.descriptions[key].base_default[0]
                if (not default and newvalue == '0') or default == newvalue:
                    return

        simpleLdap.__setitem__(self, key, newvalue)
        if self.hasChanged(key):
            self.changes = 1


class _MergedAttributes:
    """Evaluates old attributes and the modlist to get a new representation of the object."""

    def __init__(self, obj: simpleLdap, modlist: Iterable[tuple[Any, ...]]) -> None:
        self.obj = obj
        self.modlist = [x if len(x) == 3 else (x[0], None, x[-1]) for x in modlist]
        self.case_insensitive_attributes = ['objectClass']

    def get_attributes(self) -> dict[str, list[bytes]]:
        attributes = set(self.obj.oldattr.keys()) | {x[0] for x in self.modlist}
        return {attr: self.get_attribute(attr) for attr in attributes}

    def get_attribute(self, attr: str) -> list[bytes]:
        values = set(self.obj.oldattr.get(attr, []))
        # evaluate the modlist and apply all changes to the current values
        for (att, old, new) in self.modlist:
            if att.lower() != attr.lower():
                continue
            new = [] if not new else [new] if isinstance(new, bytes) else new
            old = [] if not old else [old] if isinstance(old, bytes) else old
            if not old and new:  # MOD_ADD
                values |= set(new)
            elif not new and old:  # MOD_DELETE
                values -= set(old)
            elif old and new:  # MOD_REPLACE
                values = set(new)
        return list(values)
