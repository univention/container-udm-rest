#!/usr/bin/python3
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

"""|UDM| access to handler modules."""

from __future__ import annotations

import copy
import importlib
import locale
import os
from importlib import reload as reload_module
from logging import getLogger
from typing import TYPE_CHECKING, Any, Protocol, overload

import ldap
from ldap.filter import filter_format

import univention.admin
import univention.admin.hook
import univention.admin.syntax
import univention.admin.uldap
from univention.admin import localization
from univention.admin._ucr import configRegistry
from univention.admin.layout import Group, ILayoutElement, Tab


if TYPE_CHECKING:
    from univention.admin.handlers import _Attributes, simpleLdap


class UdmModule(Protocol):
    module: str = ''
    childs: bool = False
    childmodules: list[str] = []
    operations: list[str] = []
    short_description: str = ''
    object_name: str = ''
    object_name_plural: str = ''
    long_description: str = ''
    options: dict[str, univention.admin.option] = {}
    property_descriptions: dict[str, univention.admin.property] = {}
    default_property_descriptions: dict[str, univention.admin.property] = {}
    policy_apply_to: list[str] = []
    policy_position_dn_prefix: str = ''
    policy_oc: str = ''
    docleanup: bool = False
    layout: list[Tab] = []
    mapping: univention.admin.mapping.mapping = None
    initialized: bool = False
    extended_attribute_tabnames: list[str] = []
    extended_udm_attributes: list[univention.admin.extended_attribute] = []

    class object:
        def __init__(self, co: None, lo: univention.admin.uldap.access, position: univention.admin.uldap.position, dn: str = '', superordinate: simpleLdap | None = None, attributes: _Attributes | None = None) -> None:
            pass

    @staticmethod
    def identify(dn: str, attr: dict[str, list[Any]]) -> bool:
        pass

    @staticmethod
    def lookup(co: None, lo: univention.admin.uldap.access, filter: str = '', base: str = '', superordinate: Any = None, scope: str = 'base+one', unique: bool = False, required: bool = False, timeout: int = -1, sizelimit: int = 0) -> list[Any]:
        pass

    @staticmethod
    def lookup_filter(filter_s: str | None = None, lo: univention.admin.uldap.access | None = None) -> univention.admin.filter.conjunction:
        pass


UdmName = UdmModule | str

log = getLogger('ADMIN')

translation = localization.translation('univention/admin')
_ = translation.translate

modules: dict[str, UdmModule] = {}
"""Mapping from module name to Python module."""
_superordinates: set[str] = set()
"""List of all module names (strings) that are _superordinates."""
containers: list[UdmModule] = []


@univention.admin._ldap_cache(ttl=3600)
def _ldap_operational_attribute_names(lo: univention.admin.uldap.access) -> set[str]:
    schema = lo.get_schema()
    attrs = [schema.get_obj(ldap.schema.models.AttributeType, x) for x in schema.listall(ldap.schema.models.AttributeType)]
    usages = [ldap.schema.models.AttributeUsage[o] for o in ('directoryoperation', 'dsaoperation', 'distributedoperation')]
    return {n.lower() for a in attrs for n in a.names if a.usage in usages}


def update() -> None:
    """Scan file system and update internal list of |UDM| handler modules."""
    global modules, _superordinates
    _modules: dict[str, UdmModule] = {}
    superordinates: set[str] = set()

    # since last update(), syntax.d and hooks.d may have changed (Bug #31154)
    univention.admin.syntax.import_syntax_files()
    univention.admin.hook.import_hook_files()

    def _walk(root: str, dir: str, files: list[str]) -> None:
        for file in files:
            if not file.endswith('.py') or file.startswith('__'):
                continue
            package = os.path.join(dir, file)[len(root) + 1:-len('.py')]
            log.debug('admin.modules.update: importing "%s"', package)
            modulepackage = '.'.join(package.split(os.path.sep))
            m: Any = importlib.import_module('univention.admin.handlers.%s' % (modulepackage,))
            m.initialized = False
            if not hasattr(m, 'module'):
                log.error('admin.modules.update: attribute "module" is missing in module %r', modulepackage)
                continue
            _modules[m.module] = m
            if isContainer(m):
                containers.append(m)

            superordinates.update(superordinate_names(m))

    for root in univention.admin.handlers.__path__:  # type: ignore
        for w_root, _w_dirs, w_files in os.walk(root):
            _walk(root, w_root, w_files)
    modules = _modules
    _superordinates = superordinates

    # since last update(), syntax.d may have new choices
    # put here as one syntax wants to provide all modules
    univention.admin.syntax.update_choices()


@overload
def get(module: UdmModule) -> UdmModule:
    pass


@overload
def get(module: str) -> UdmModule | None:
    pass


def get(module: UdmName) -> UdmModule | None:
    """
    Get |UDM| module.

    :param module: either the name (str) of a module or the module itself.
    :returns: the module or `None` if no module exists with the requested name.
    """
    # FIXME: raise Exception instead of returning None
    if not module:
        return None  # type: ignore
    if isinstance(module, str):
        return modules.get(module)  # type: ignore
    return module  # type: ignore[return-value]


def _get(module: UdmModule | str) -> UdmModule:
    """
    Internal function to lazy-load and get |UDM| module.

    :param module: either the name (str) of a module or the module itself.
    :returns: the module
    :raises KeyError: if no module exists with the requested name.
    """
    if not modules:
        update()
    if isinstance(module, str):
        return modules[module]
    return module


def init(lo: univention.admin.uldap.access, position: univention.admin.uldap.position, module: UdmModule, template_object: simpleLdap | None = None, force_reload: bool = False) -> None:
    """
    Initialize |UDM| handler module.

    :param lo: |LDAP| connection.
    :param position: |UDM| position instance.
    :param module: |UDM| handler module.
    :param template_object: Reference to a instance, from which the default values are used.
    :param force_reload: With `True` force Python to reload the module from the file system.
    """
    # you better do a reload if init is called a second time
    # especially because update_extended_attributes
    # called twice will have side-effects
    if force_reload:
        reload_module(module)  # type: ignore
        if module.module == 'users/user':
            # users/self inherits from users/user leading to errors when not reloading it as well
            # TODO: remove when droppng Python2.7 support and all super(object, self) calls have been replaced with super()
            reload_module(univention.admin.modules._get('users/self'))  # type: ignore
    # reset property descriptions to defaults if possible
    if hasattr(module, 'default_property_descriptions'):
        module.property_descriptions = copy.deepcopy(module.default_property_descriptions)
        # log.debug('modules_init: reset default descriptions')

    # overwrite property descriptions
    univention.admin.ucr_overwrite_properties(module, lo)

    # check for properties with the syntax class LDAP_Search
    for pname, prop in module.property_descriptions.items():
        if prop.syntax.name == 'LDAP_Search':
            prop.syntax._load(lo)
            if prop.syntax.viewonly:
                module.mapping.unregister(pname, False)
        elif univention.admin.syntax.is_syntax(prop.syntax, univention.admin.syntax.complex) and hasattr(prop.syntax, 'subsyntaxes'):
            for _text, subsyn in prop.syntax.subsyntaxes:
                if subsyn.name == 'LDAP_Search':
                    subsyn._load(lo)

    # add new properties, only for modules in default ldap base
    if lo.compare_dn(configRegistry['ldap/base'].lower(), getattr(module.object, 'ldap_base', configRegistry['ldap/base']).lower()):
        update_extended_options(lo, module, position)
        update_extended_attributes(lo, module, position)

    # get defaults from template
    if template_object:
        log.debug('modules_init: got template object %s', template_object.dn)
        template_object.open()

        # add template defaults
        for key, tmpl in template_object.items():
            if key == '_options':
                if tmpl not in ([''], []):
                    for option in module.options.keys():
                        module.options[option].default = option in tmpl
            elif key not in {"name", "description"}:  # these keys are part of the template itself
                module.property_descriptions[key].base_default = copy.copy(tmpl)
                module.property_descriptions[key].templates.append(template_object)
        log.debug('modules_init: module.property_description after template: %s', module.property_descriptions)
    else:
        log.debug('modules_init: got no template')

    # re-build layout if there any overwrites defined
    univention.admin.ucr_overwrite_module_layout(module)

    # some choices depend on extended_options/attributes
    univention.admin.syntax.update_choices()

    module.initialized = True


def update_extended_options(lo: univention.admin.uldap.access, module: UdmModule, position: univention.admin.uldap.position) -> None:
    """Overwrite options defined via |LDAP|."""
    # get current language
    lang = locale.getlocale(locale.LC_MESSAGES)[0]
    log.debug('modules update_extended_options: LANG=%s', lang)

    module_filter = filter_format('(univentionUDMOptionModule=%s)', [name(module)])
    if name(module) == 'settings/usertemplate':
        module_filter = '(|(univentionUDMOptionModule=users/user)%s)' % (module_filter,)

    # append UDM extended options
    new_options = copy.copy(module.options) if hasattr(module, 'options') else {}
    for _dn, attrs in lo.search(base=position.getDomainConfigBase(), filter='(&(objectClass=univentionUDMOption)%s)' % (module_filter,)):
        oname = attrs['cn'][0].decode('UTF-8', 'replace')
        shortdesc = _get_translation(lang, attrs, 'univentionUDMOptionTranslationShortDescription;entry-%s', 'univentionUDMOptionShortDescription')
        longdesc = _get_translation(lang, attrs, 'univentionUDMOptionTranslationLongDescription;entry-%s', 'univentionUDMOptionLongDescription')
        default = attrs.get('univentionUDMOptionDefault', [b'0'])[0] == b'1'
        editable = attrs.get('univentionUDMOptionEditable', [b'0'])[0] == b'1'
        classes = [x.decode('UTF-8', 'replace') for x in attrs.get('univentionUDMOptionObjectClass', [])]
        is_app_option = attrs.get('univentionUDMOptionIsApp', [b'0'])[0] == b'1'

        new_options[oname] = univention.admin.option(
            short_description=shortdesc,
            long_description=longdesc,
            default=default,
            editable=editable,
            objectClasses=classes,
            is_app_option=is_app_option)
    module.options = new_options


class EA_Layout(dict):
    """Extended attribute layout."""

    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)

    @property
    def name(self) -> str:
        return self.get('name', '')

    @property
    def overwrite(self) -> str | None:
        return self.get('overwrite', None)

    @property
    def tabName(self) -> str:
        return self.get('tabName', '')

    @property
    def groupName(self) -> str:
        return self.get('groupName', '')

    @property
    def position(self) -> int:
        return self.get('position', -1)

    @property
    def groupPosition(self) -> int:
        return self.get('groupPosition', -1)

    @property
    def advanced(self) -> bool:
        return self.get('advanced', False)

    @property
    def is_app_tab(self) -> bool:
        return self.get('is_app_tab', False)

    def __lt__(self, other):
        return (self.groupName, self.position) < (other.groupName, other.position)

    def __gt__(self, other):
        return (self.groupName, self.position) > (other.groupName, other.position)

    def __eq__(self, other):
        return (self.groupName, self.position) == (other.groupName, other.position)

    def __le__(self, other):
        return (self.groupName, self.position) <= (other.groupName, other.position)

    def __ge__(self, other):
        return (self.groupName, self.position) >= (other.groupName, other.position)

    def __ne__(self, other):
        return (self.groupName, self.position) != (other.groupName, other.position)

    def __hash__(self):
        return hash((self.groupName, self.position))


def update_extended_attributes(lo: univention.admin.uldap.access, module: UdmModule, position: univention.admin.uldap.position) -> None:
    """Load extended attribute from |LDAP| and modify |UDM| handler."""
    # add list of tabnames created by extended attributes
    if not hasattr(module, 'extended_attribute_tabnames'):
        module.extended_attribute_tabnames = []

    # append UDM extended attributes
    properties4tabs: dict[str, list[EA_Layout]] = {}
    overwriteTabList: list[str] = []
    module.extended_udm_attributes = []

    module_filter = filter_format('(univentionUDMPropertyModule=%s)', [name(module)])
    if name(module) == 'settings/usertemplate':
        module_filter = '(|(univentionUDMPropertyModule=users/user)%s)' % (module_filter,)

    new_property_descriptions = copy.copy(module.property_descriptions)
    for _dn, attrs in lo.search(base=position.getDomainConfigBase(), filter='(&(objectClass=univentionUDMProperty)%s(univentionUDMPropertyVersion=2))' % (module_filter,)):
        # get CLI name
        pname = attrs['univentionUDMPropertyCLIName'][0].decode('UTF-8', 'replace')
        object_class = attrs.get('univentionUDMPropertyObjectClass', [])[0].decode('UTF-8', 'replace')
        ldap_attribute_name = attrs['univentionUDMPropertyLdapMapping'][0].decode('UTF-8', 'replace')
        if name(module) == 'settings/usertemplate' and object_class == 'univentionMail' and b'settings/usertemplate' not in attrs.get('univentionUDMPropertyModule', []):
            continue  # since "mail" is a default option, creating a usertemplate with any mail attribute would raise Object class violation: object class 'univentionMail' requires attribute 'uid'

        # get syntax
        propertySyntaxString = attrs.get('univentionUDMPropertySyntax', [b''])[0].decode('utf-8', 'replace')
        if propertySyntaxString and hasattr(univention.admin.syntax, propertySyntaxString):
            propertySyntax = getattr(univention.admin.syntax, propertySyntaxString)
        else:
            if lo.searchDn(filter=filter_format(univention.admin.syntax.LDAP_Search.FILTER_PATTERN, [propertySyntaxString])):
                propertySyntax = univention.admin.syntax.LDAP_Search(propertySyntaxString)
            else:
                propertySyntax = univention.admin.syntax.string()

        # get hooks
        propertyHookString = attrs.get('univentionUDMPropertyHook', [b''])[0].decode('utf-8', 'replace')
        propertyHook = None
        if propertyHookString and hasattr(univention.admin.hook, propertyHookString):
            propertyHook = getattr(univention.admin.hook, propertyHookString)()

        # get default value
        propertyDefault = [x.decode('UTF-8') if x is not None else x for x in attrs.get('univentionUDMPropertyDefault', [None])]

        # value may change
        try:
            mayChange = bool(int(attrs.get('univentionUDMPropertyValueMayChange', [b'0'])[0]))
        except ValueError:
            log.error('modules update_extended_attributes: ERROR: processing univentionUDMPropertyValueMayChange threw exception - assuming mayChange=0')
            mayChange = False

        # prevent UMC default popup
        preventUmcDefaultPopup = bool(int(attrs.get('univentionUDMPropertyPreventUmcDefaultPopup', [b'0'])[0]))

        # value is editable (only via hooks or direkt module.info[] access)
        editable = attrs.get('univentionUDMPropertyValueNotEditable', [b'0'])[0] not in [b'1', b'TRUE']

        copyable = attrs.get('univentionUDMPropertyCopyable', [b'0'])[0] not in [b'1', b'TRUE']

        # value is required
        valueRequired = (attrs.get('univentionUDMPropertyValueRequired', [b'0'])[0].upper() in [b'1', b'TRUE'])

        # value not available for searching
        try:
            doNotSearch = bool(int(attrs.get('univentionUDMPropertyDoNotSearch', [b'0'])[0]))
        except ValueError:
            log.error('modules update_extended_attributes: ERROR: processing univentionUDMPropertyDoNotSearch threw exception - assuming doNotSearch=0')
            doNotSearch = False

        # check if CA is multivalue property
        if attrs.get('univentionUDMPropertyMultivalue', [b''])[0] == b'1':
            multivalue = True
            map_method = None
            unmap_method = None
        else:
            multivalue = False
            map_method = univention.admin.mapping.ListToString
            unmap_method = None
            if propertySyntaxString == 'boolean':
                map_method = univention.admin.mapping.BooleanListToString
                unmap_method = univention.admin.mapping.BooleanUnMap
            # single value ==> use only first value
            propertyDefault = propertyDefault[0]

        # Show this attribute in UDM/UMC?
        if attrs.get('univentionUDMPropertyLayoutDisable', [b''])[0] == b'1':
            layoutDisabled = True
        else:
            layoutDisabled = False

        # get current language
        lang = locale.getlocale(locale.LC_MESSAGES)[0]
        log.debug('modules update_extended_attributes: LANG = %s', str(lang))

        # get descriptions
        shortdesc = _get_translation(lang, attrs, 'univentionUDMPropertyTranslationShortDescription;entry-%s', 'univentionUDMPropertyShortDescription')
        longdesc = _get_translation(lang, attrs, 'univentionUDMPropertyTranslationLongDescription;entry-%s', 'univentionUDMPropertyLongDescription')

        # create property
        fullWidth = (attrs.get('univentionUDMPropertyLayoutFullWidth', [b'0'])[0].upper() in [b'1', b'TRUE'])
        new_property_descriptions[pname] = univention.admin.property(
            short_description=shortdesc,
            long_description=longdesc,
            syntax=propertySyntax,
            multivalue=multivalue,
            options=[x.decode('UTF-8', 'replace') for x in attrs.get('univentionUDMPropertyOptions', [])],
            required=valueRequired,
            may_change=mayChange,
            prevent_umc_default_popup=preventUmcDefaultPopup,
            dontsearch=doNotSearch,
            default=propertyDefault,
            editable=editable,
            copyable=copyable,
            size='Two' if fullWidth else None,
        )

        # add LDAP mapping
        if ldap_attribute_name.lower() != 'objectclass':
            module.mapping.register(pname, ldap_attribute_name, unmap_method, map_method)
        else:
            module.mapping.register(pname, ldap_attribute_name, univention.admin.mapping.nothing, univention.admin.mapping.nothing)

        if hasattr(module, 'layout'):
            tabname = _get_translation(lang, attrs, 'univentionUDMPropertyTranslationTabName;entry-%s', 'univentionUDMPropertyLayoutTabName', _('Custom'))
            overwriteTab = (attrs.get('univentionUDMPropertyLayoutOverwriteTab', [b'0'])[0].upper() in [b'1', b'TRUE'])
            # in the first generation of extended attributes of version 2
            # this field was a position defining the attribute to
            # overwrite. now it is the name of the attribute to overwrite
            overwriteProp: str | None = attrs.get('univentionUDMPropertyLayoutOverwritePosition', [b''])[0].decode('UTF-8', 'replace')
            if overwriteProp == '0':
                overwriteProp = None
            deleteObjectClass = (attrs.get('univentionUDMPropertyDeleteObjectClass', [b'0'])[0].upper() in [b'1', b'TRUE'])
            tabAdvanced = (attrs.get('univentionUDMPropertyLayoutTabAdvanced', [b'0'])[0].upper() in [b'1', b'TRUE'])

            groupname = _get_translation(lang, attrs, 'univentionUDMPropertyTranslationGroupName;entry-%s', 'univentionUDMPropertyLayoutGroupName')
            try:
                groupPosition = int(attrs.get('univentionUDMPropertyLayoutGroupPosition', [b'-1'])[0])
            except TypeError:
                groupPosition = 0

            log.debug('update_extended_attributes: extended attribute (LDAP): %r', attrs)

            # only one is possible ==> overwriteTab wins
            if overwriteTab and overwriteProp:
                overwriteProp = None

            # add tab name to list if missing
            if tabname not in properties4tabs and not layoutDisabled:
                properties4tabs[tabname] = []
                log.debug('modules update_extended_attributes: custom fields init for tab %s', tabname)

            # remember tab for purging if required
            if overwriteTab and tabname not in overwriteTabList and not layoutDisabled:
                overwriteTabList.append(tabname)

            if not layoutDisabled:
                # get position on tab
                # -1 == append on top
                plp = attrs.get('univentionUDMPropertyLayoutPosition', [b'-1'])[0].decode('UTF-8', 'replace')
                try:
                    priority = int(plp)
                    if priority < 1:
                        priority = -1
                except ValueError:
                    log.warning('modules update_extended_attributes: custom field for tab %s: failed to convert tabNumber to int', tabname)
                    priority = -1

                if priority == -1 and properties4tabs[tabname]:
                    priority = max([-1, min(ea_layout.position for ea_layout in properties4tabs[tabname]) - 1])

                properties4tabs[tabname].append(EA_Layout(
                    name=pname,
                    tabName=tabname,
                    position=priority,
                    advanced=tabAdvanced,
                    overwrite=overwriteProp,
                    fullWidth=fullWidth,
                    groupName=groupname,
                    groupPosition=groupPosition,
                    is_app_tab=any(option in [key for (key, value) in getattr(module, 'options', {}).items() if value.is_app_option] for option in attrs.get('univentionUDMPropertyOptions', [])),
                ))
            else:
                for tab in getattr(module, 'layout', []):
                    tab.remove(pname)

            module.extended_udm_attributes.append(univention.admin.extended_attribute(
                name=pname,
                objClass=object_class,
                ldapMapping=ldap_attribute_name,
                deleteObjClass=deleteObjectClass,
                syntax=propertySyntaxString,
                hook=propertyHook,
            ))

            if ldap_attribute_name.lower() in _ldap_operational_attribute_names(lo):
                module.object._static_ldap_attributes.add(ldap_attribute_name)

    module.property_descriptions = new_property_descriptions

    # overwrite tabs that have been added by UDM extended attributes
    for tab in module.extended_attribute_tabnames:
        if tab not in overwriteTabList:
            overwriteTabList.append(tab)

    if properties4tabs:
        # remove layout of tabs that have been marked for replacement
        for tab in module.layout:
            if tab.label in overwriteTabList:
                tab.layout = []

        for tabname, priofields in properties4tabs.items():
            priofields = sorted(priofields)
            currentTab = None
            # get existing fields if tab has not been overwritten
            for tab in module.layout:
                if tab.label == tabname:
                    # found tab in layout
                    currentTab = tab
                    # tab found ==> leave loop
                    break
            else:
                # tab not found in current layout, so add it
                currentTab = Tab(tabname, tabname, advanced=True)
                module.layout.append(currentTab)
                # remember tabs that have been added by UDM extended attributes
                if tabname not in module.extended_attribute_tabnames:
                    module.extended_attribute_tabnames.append(tabname)

            currentTab.is_app_tab = any(x.is_app_tab for x in priofields)

            # check if tab is empty ==> overwritePosition is impossible
            freshTab = not currentTab.layout

            for ea_layout in priofields:
                if currentTab.advanced and not ea_layout.advanced:
                    currentTab.advanced = False

                # if groupName is set check if it exists, otherwise create it
                if ea_layout.groupName:
                    for item in currentTab.layout:
                        if isinstance(item, ILayoutElement) and item.label == ea_layout.groupName:
                            break
                    else:  # group does not exist
                        grp = Group(ea_layout.groupName)
                        if ea_layout.groupPosition > 0:
                            currentTab.layout.insert(ea_layout.groupPosition - 1, grp)
                        else:
                            currentTab.layout.append(grp)

                # - existing property shall be overwritten AND
                # - tab is not new and has not been cleaned before AND
                # - position >= 1 (top left position is defined as 1) AND
                # - old property with given position exists

                if currentTab.exists(ea_layout.name):
                    continue
                elif ea_layout.overwrite and not freshTab:  # we want to overwrite an existing property
                    # in the global fields ...
                    if not ea_layout.groupName:
                        replaced, _layout = currentTab.replace(ea_layout.overwrite, ea_layout.name, recursive=True)
                        if not replaced:  # the property was not found so we'll append it
                            currentTab.layout.append(ea_layout.name)
                    else:
                        for item in currentTab.layout:
                            if isinstance(item, ILayoutElement) and item.label == ea_layout.groupName:
                                replaced, _layout = item.replace(ea_layout.overwrite, ea_layout.name)
                                if not replaced:  # the property was not found so we'll append it
                                    item.layout.append(ea_layout.name)
                else:
                    if not ea_layout.groupName:
                        currentTab.insert(ea_layout.position, ea_layout.name)
                    else:
                        for item in currentTab.layout:
                            if isinstance(item, ILayoutElement) and item.label == ea_layout.groupName:
                                item.insert(ea_layout.position, ea_layout.name)
                                break

    # check for properties with the syntax class LDAP_Search
    for pname, prop in module.property_descriptions.items():
        if prop.syntax.name == 'LDAP_Search':
            prop.syntax._load(lo)
            if prop.syntax.viewonly:
                module.mapping.unregister(pname, False)
        elif univention.admin.syntax.is_syntax(prop.syntax, univention.admin.syntax.complex) and hasattr(prop.syntax, 'subsyntaxes'):
            for _text, subsyn in prop.syntax.subsyntaxes:
                if subsyn.name == 'LDAP_Search':
                    subsyn._load(lo)


def identify(dn: str, attr: dict[str, list[Any]], module_name: str = '', canonical: int = 0, module_base: str | None = None) -> list[UdmModule]:
    """
    Return list of |UDM| handlers capable of handling the given |LDAP| object.

    :param dn: |DN| of the |LDAP| object.
    :param attr: |LDAP| attributes.
    :param module_name: If given only the given module name is used if it is capable to handle the object.
    :param canonical: UNUSED!
    :param module_base: Optional string the module names must start with.
    :returns: the list of |UDM| modules.
    """
    res = [m for m in (
        modules.get(mt.decode('ASCII', 'replace')) for mt in attr.get('univentionObjectType', [])
    ) if m]
    if not res:
        for name, module in modules.items():
            if module_base is not None and not name.startswith(module_base):
                continue
            if not hasattr(module, 'identify'):
                log.debug('module %s does not provide identify', module)
                continue

            if (not module_name or module_name == module.module) and module.identify(dn, attr):
                res.append(module)
    if not res:
        log.debug('object could not be identified')
    for r in res:
        log.debug('identify: found module %s on %s', r.module, dn)
    return res


def identifyOne(dn: str, attr: dict[str, list[Any]], type: str = '') -> UdmModule | None:
    """
    Return the |UDM| handler capable of handling the given |LDAP| object.

    :param dn: |DN| of the |LDAP| object.
    :param atr: |LDAP| attributes.
    :param type: If given only the given module name is used if it is capable to handle the object.
    :returns: the |UDM| modules or `None`.
    """
    res = identify(dn, attr, type)
    if len(res) != 1:
        return None
    else:
        return res[0]


def recognize(module_name: str, dn: str, attr: dict[str, list[Any]]) -> bool:
    module = get(module_name)
    if not hasattr(module, 'identify'):
        return False
    return module.identify(dn, attr)


def name(module: UdmName) -> str:
    """Return name of module."""
    if not module:
        return ''
    return get(module).module


def superordinate_names(module_name: UdmName) -> list[str]:
    """Return name of superordinate module."""
    module = get(module_name)
    names = getattr(module, 'superordinate', [])
    if isinstance(names, str):
        names = [names]
    return names


def superordinate_name(module_name: UdmName) -> str | None:
    """
    Return name of first superordinate module.

    .. deprecated :: UCS 4.2
            Use :py:func:`superordinate_names` instead.
    """
    names = superordinate_names(module_name)
    return names[0] if names else None


def superordinate(module: UdmModule) -> UdmModule:
    """
    Return instance of superordinate module.

    .. deprecated :: UCS 4.2
            Use :py:func:`superordinates` instead.
    """
    return get(superordinate_name(module))


def superordinates(module: UdmName) -> list[UdmModule | None]:
    """Return instance of superordinate module."""
    return [get(x) for x in superordinate_names(module)]


def subordinates(module: UdmName) -> list[UdmModule]:
    """
    Return list of instances of subordinate modules.

    :param module: ???
    :returns: list of |UDM| handler modules.
    """
    return [mod for mod in modules.values() if name(module) in superordinate_names(mod) and not isContainer(mod)]


def find_superordinate(dn: str, co: None, lo: univention.admin.uldap.access) -> UdmModule | None:
    """
    For a given |DN|, search in the |LDAP| path whether this LDAP object is
    below an object that is a superordinate or is a superordinate itself.

    :param dn: |DN|.
    :param co: |UDM| configuation object.
    :param lo: |LDAP| connection.
    :returns: the superordinate module or `None`.
    """
    # walk up the ldap path and stop if we find an object type that is a superordinate
    while dn:
        attr = lo.get(dn)
        module = identifyOne(dn, attr)
        if module and isSuperordinate(module):
            return get(module)
        dn = lo.parentDn(dn)
    return None


def layout(module_name: UdmName, object: Any = None) -> list[Tab]:
    """return layout of properties"""
    module = get(module_name)
    defining_layout = None
    if object:
        log.debug('modules.py layout: got a defined object')

    if object and hasattr(object, 'layout'):  # for dynamic modules like users/self
        log.debug('modules.py layout:: layout is defined by the object')
        defining_layout = object.layout
    elif hasattr(module, 'layout'):
        defining_layout = module.layout
        log.debug('modules.py layout:: layout is defined by the module')

    if defining_layout:
        if object and hasattr(object, 'options'):
            layout = []
            for tab in defining_layout:
                empty = True
                fields = []
                for line in tab.layout:
                    nline = []
                    for row in line:
                        single = False
                        nrow = []
                        if isinstance(row, str):
                            single = True
                            row = [row]
                        for field in row:
                            prop = module.property_descriptions[field]
                            nrow.append(field)
                            if not prop.options or [opt for opt in prop.options if opt in object.options]:
                                if not prop.license or [license for license in prop.license if license in object.lo.licensetypes]:
                                    empty = False
                        if nrow:
                            if single:
                                nrow = nrow[0]
                            nline.append(nrow)
                    if nline:
                        fields.append(nline)
                if fields and not empty:
                    ntab = copy.deepcopy(tab)
                    ntab.layout = fields
                    layout.append(ntab)
            log.debug('modules.py layout:: return layout decreased by given options')
            return layout
        else:
            log.debug('modules.py layout:: return defining_layout.')
            return defining_layout

    else:
        return []


def options(module_name: UdmName) -> dict[str, Any]:
    """return options available for module"""
    module = get(module_name)
    return getattr(module, 'options', {})


def attributes(module_name: UdmName) -> list[dict[str, str]]:
    """
    Return attributes for module.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    """
    module = get(module_name)
    return [
        {'name': attribute, 'description': module.property_descriptions[attribute].short_description}
        for attribute in module.property_descriptions.keys()
    ]


def short_description(module_name: UdmName) -> str:
    """
    Return short description for module.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    :returns: The short descriptive text.
    """
    module = get(module_name)
    if hasattr(module, 'short_description'):
        return module.short_description
    modname = name(module)
    if modname:
        return modname
    return repr(module)


def policy_short_description(module_name: UdmName) -> str:
    """
    Return short description for policy module primarily used for tab headers.

    :param module_name: the name of the |UDM| policy module, e.g. `policies/pwhistory`.
    :returns: The short descriptive text.
    """
    module = get(module_name)
    return getattr(module, 'policy_short_description', short_description(module))


def long_description(module_name: UdmName) -> str:
    """
    Return long description for module.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    :returns: The long descriptive text.
    """
    module = get(module_name)
    return getattr(module, 'long_description', short_description(module))


def childs(module_name: UdmName) -> bool:
    """
    Return whether module may have subordinate modules.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    :returns: `True` if the module has children, `False` otherwise.
    """
    module = get(module_name)
    return getattr(module, 'childs', False)


def virtual(module_name: UdmName) -> bool:
    """
    Return whether the module is virtual (alias for other modules).

    :param module_name: the name of the |UDM| module, e.g. `computers/computer`.
    :returns: `True` if the module is virtual, `False` otherwise.
    """
    module = get(module_name)
    return getattr(module, 'virtual', False)


def lookup(module_name: UdmName, co: None, lo: univention.admin.uldap.access, filter: str = '', base: str = '', superordinate: Any = None, scope: str = 'base+one', unique: bool = False, required: bool = False, timeout: int = -1, sizelimit: int = 0) -> list[Any]:
    """
    Return objects of module that match the given criteria.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    """
    module = get(module_name)
    tmpres = []

    if hasattr(module, 'lookup'):
        tmpres = module.lookup(co, lo, filter, base=base, superordinate=superordinate, scope=scope, unique=unique, required=required, timeout=timeout, sizelimit=sizelimit)

    # check for 'None' items just in case...
    return [item for item in tmpres if item]


def isSuperordinate(module: UdmName) -> bool:
    """
    Check if the module is a |UDM| superordinate module.

    :param module: A |UDM| handler class.
    :returns: `True` if the handler is a superordinate module, `False` otherwise.
    """
    return name(module) in _superordinates


def isContainer(module: UdmModule) -> bool:
    """
    Check if the module is a |UDM| container module.

    :param module: A |UDM| handler class.
    :returns: `True` if the handler is a container module, `False` otherwise.
    """
    return name(module).startswith('container/')


def isPolicy(module: UdmModule) -> bool:
    """
    Check if the module is a |UDM| policy module.

    :param module: A |UDM| handler class.
    :returns: `True` if the handler is a policy module, `False` otherwise.
    """
    return name(module).startswith('policies/')


def defaultPosition(module: UdmModule, superordinate: Any = None) -> str:
    """
    Returns default position for object of module.

    :param module: A |UDM| handler class.
    :param superordinate: A optional superordinate |UDM| object instance.
    :returns: The |DN| of the container for the object.
    """
    rdns = ['users', 'dns', 'dhcp', 'shares', 'printers']
    base = univention.admin.uldap.getBaseDN()
    if superordinate:
        return superordinate.dn
    start = name(module).split('/')[0]
    if start in rdns:
        return 'cn=%s,%s' % (ldap.dn.escape_dn_chars(start), base)
    return base


def supports(module_name: str, operation: str) -> bool:
    """
    Check if module supports operation

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    :param operation: the name of the operation, e.g. 'edit'.
    :returns: `True` if the operation is supported, `False` otherwise.
    """
    module = get(module_name)
    if not hasattr(module, 'operations'):
        return True
    return operation in module.operations


def objectType(co: None, lo: univention.admin.uldap.access, dn: str, attr: _Attributes | None = None, modules: list[UdmModule] = [], module_base: str | None = None) -> list[str]:
    if not dn:
        return []
    if attr is None:
        attr = lo.get(dn)
        if not attr:
            return []
    ot = attr.get('univentionObjectType')
    if ot:
        return [x.decode('utf-8') for x in ot]

    if not modules:
        modules = identify(dn, attr, module_base=module_base)

    return [name(mod) for mod in modules]


def objectShadowType(co: None, lo: univention.admin.uldap.access, dn: str, attr: _Attributes | None = None, modules: list[UdmModule] = []) -> list[Any]:
    # FIXME: This returns a nested list[...list[str]] for containers!
    return [
        objectShadowType(co, lo, lo.parentDn(dn)) if otype and otype.startswith('container/') else otype
        for otype in objectType(co, lo, dn, attr, modules)
    ]


def findObject(co: None, lo: univention.admin.uldap.access, dn: str, type: UdmModule, attr: _Attributes | None = None, module_base: str | None = None) -> Any | None:
    if attr is None:
        attr = lo.get(dn)
        if not attr:
            return None
    ndn = dn
    nattr = attr
    while True:
        for module in identify(ndn, nattr):
            if module and module.module == type:
                s = superordinate(module)
                so = findObject(co, lo, ndn, s) if s else None
                return module.object(co, lo, ndn, superordinate=so)
        ndn = lo.parentDn(ndn)
        if not ndn:
            break
        nattr = lo.get(ndn)
    return None


def policyOc(module_name: UdmName) -> str:
    """
    Return the |LDAP| objectClass used to store the policy.

    :param module_name: the name of the |UDM| policy module, e.g. `policies/pwhistory`.
    :returns: the objectClass.
    """
    module = get(module_name)
    return getattr(module, 'policy_oc', '')


def policiesGroup(module_name: UdmName) -> str:
    """
    Return the name of the group the |UDM| policy belongs to.

    :param module_name: the name of the |UDM| policy module, e.g. `policies/pwhistory`.
    :returns: the group name.
    """
    module = get(module_name)
    return getattr(module, 'policies_group', 'top')


def policies() -> list[univention.admin.policiesGroup]:
    res: dict[str, list[str]] = {}
    for mod in modules.values():
        if not isPolicy(mod):
            continue
        if name(mod) != "policies/policy":
            res.setdefault(policiesGroup(mod), []).append(name(mod))
    return [
        univention.admin.policiesGroup(id=groupname, members=sorted(members))
        for groupname, members in sorted(res.items())
    ]


def policyTypes(module_name: str) -> list[str]:
    """
    Returns a list of policy types applying to the given module.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    :returns: a list of |UDM| policy modules, e.g. `policies/pwhistory`.
    """
    if not module_name:
        return []
    if module_name not in modules:
        return []
    return [
        name
        for name, module in modules.items()
        if name.startswith('policies/') and module_name in getattr(module, 'policy_apply_to', ())
    ]


def policyPositionDnPrefix(module_name: UdmName) -> str:
    """
    Return the relative |DN| for a policy.

    :param module_name: the name of the |UDM| policy module, e.g. `policies/pwhistory`.
    :return: A |DN| string to append to the |LDAP| base to get the container for the policy.
    """
    module = get(module_name)
    if not hasattr(module, 'policy_position_dn_prefix'):
        return ""
    policy_position_dn_prefix = module.policy_position_dn_prefix
    if policy_position_dn_prefix.endswith(','):
        policy_position_dn_prefix = policy_position_dn_prefix[:-1]
    return policy_position_dn_prefix


def defaultContainers(module: simpleLdap) -> list[str]:
    """
    Checks for the attribute default_containers that should contain a
    list of RDNs of default containers.

    :param module: |UDM|
    :returns: a list of DNs.
    """
    base = getattr(module.object, 'ldap_base', configRegistry['ldap/base'])
    return ['%s,%s' % (rdn, base) for rdn in getattr(module, 'default_containers', [])]


def childModules(module_name: UdmName) -> list[str]:
    """
    Return child modules if module is a super module.

    :param module_name: the name of the |UDM| module, e.g. `users/user`.
    :returns: List of child module names.
    """
    module = get(module_name)
    return list(getattr(module, 'childmodules', []))


def _get_translation(locale: str | None, attrs: Any, name: str, defaultname: str, default: str = '') -> str:
    if locale:
        locale = locale.replace('_', '-').lower()
        if name % (locale,) in attrs:
            return attrs[name % (locale,)][0].decode('UTF-8', 'replace')
        locale = locale.split('-', 1)[0]
        name_short_lang = name % (locale,)
        if name_short_lang in attrs:
            return attrs[name_short_lang][0].decode('UTF-8', 'replace')
        for key in attrs:
            if key.startswith(name_short_lang):
                return attrs[key][0].decode('UTF-8', 'replace')
    return attrs.get(defaultname, [default.encode('utf-8')])[0].decode('UTF-8', 'replace')
