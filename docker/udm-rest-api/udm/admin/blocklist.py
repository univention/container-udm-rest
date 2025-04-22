# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2024 Univention GmbH
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

"""|UDM| functions to check and create blocklist entries"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable  # noqa: F401
from datetime import datetime
from typing import TYPE_CHECKING

import ldap
from dateutil.relativedelta import relativedelta

import univention.admin.localization
import univention.admin.uexceptions
import univention.admin.uldap
from univention.admin._ucr import configRegistry


if TYPE_CHECKING:
    import univention.admin.handlers
    import univention.admin.handlers.blocklists.list  # noqa: TCH004


translation = univention.admin.localization.translation('univention.admin.handlers')
_ = translation.translate

BLOCKLIST_BASE = 'cn=blocklists,cn=internal'


try:
    unicode  # noqa: B018
except NameError:
    unicode = str


def hash_blocklist_value(value):  # type: (bytes) -> str
    return 'sha256:%s' % hashlib.sha256(value.lower()).hexdigest()


def parse_timedelta(timedelta_string):
    # type: (str) -> relativedelta | None
    """
    Parse time delta.

    >>> parse_timedelta("1y10m340d")
    relativedelta(years=+1, months=+10, days=+340)
    """
    match = re.match(r'((?P<years>-?\d+)y)?((?P<months>-?\d+)m)?((?P<days>-?\d+)d)?', timedelta_string)
    if match:
        parts = {unit: int(value) for unit, value in match.groupdict().items() if value}
        return relativedelta(**parts)


@univention.admin._ldap_cache(ttl=120)
def get_blocklist_config(lo):
    # type: (univention.admin.uldap.access) -> dict
    config = {}
    try:
        for blist in univention.admin.handlers.blocklists.list.lookup(None, lo, 'entryUUID=*', base=BLOCKLIST_BASE, scope='one'):
            config[blist.dn] = blist.get('retentionTime', '30d')
            for mod, prop in blist.get('blockingProperties', []):
                config.setdefault(mod, {})[prop] = blist.dn
    except univention.admin.uexceptions.noObject:
        # that means cn=internal is not (yet) available
        # return an empty config, without cn=internal, there is no config
        pass
    return config


def get_blocking_udm_properties(udm_obj):
    # type: (univention.admin.handlers.simpleLdap) -> dict
    config = get_blocklist_config(udm_obj.lo_machine_primary)
    return config.get(udm_obj.module, {})


def get_blockeduntil(dn, lo):
    # type: (str, univention.admin.uldap.access) -> str
    config = get_blocklist_config(lo)
    retention = config.get(dn, '30d')
    blocking_duration = parse_timedelta(retention)
    blocked_until = datetime.utcnow() + blocking_duration
    return datetime.strftime(blocked_until, '%Y%m%d%H%M%SZ')


def blocklist_enabled(udm_obj):
    # type: (univention.admin.handlers.simpleLdap) -> bool
    return not udm_obj.module.startswith('blocklists/') and configRegistry.is_true('directory/manager/blocklist/enabled', False)


def get_blocklist_values_from_udm_property(udm_property_value, udm_property_name):
    # type: (Any, str) -> list[Any]
    if isinstance(udm_property_value, str | unicode):
        return [udm_property_value]
    if not isinstance(udm_property_value, list) or not all(isinstance(mem, str | unicode) for mem in udm_property_value):
        raise RuntimeError('The property %r uses a complex syntax. This is not supported for blocklist objects.' % udm_property_name)
    return udm_property_value


def create_blocklistentry(udm_obj):
    # type: (univention.admin.handlers.simpleLdap) -> list
    if not blocklist_enabled(udm_obj):
        return []
    blocklist_entries = []
    for prop, bl_dn in get_blocking_udm_properties(udm_obj).items():
        if (not udm_obj.exists() and udm_obj.oldinfo.get(prop)) or (udm_obj.hasChanged(prop) and udm_obj.oldinfo.get(prop)):
            blocklist_position = univention.admin.uldap.position(bl_dn)
            for value in get_blocklist_values_from_udm_property(udm_obj.oldinfo[prop], prop):
                blocklistentry = univention.admin.handlers.blocklists.entry.object(None, udm_obj.lo_machine_primary, blocklist_position)
                blocklistentry.open()
                blocklistentry['value'] = value
                blocklistentry['originUniventionObjectIdentifier'] = udm_obj.entry_uuid
                blocklistentry['blockedUntil'] = get_blockeduntil(bl_dn, udm_obj.lo_machine_primary)
                try:
                    blocklistentry.create(ignore_license=True)
                except univention.admin.uexceptions.objectExists:
                    pass
                else:
                    blocklist_entries.append(blocklistentry.dn)
    return blocklist_entries


def check_blocklistentry(udm_obj):
    # type: (univention.admin.handlers.simpleLdap) -> None
    if not blocklist_enabled(udm_obj):
        return
    for prop, bl_dn in get_blocking_udm_properties(udm_obj).items():
        if udm_obj.hasChanged(prop) and udm_obj.info.get(prop):
            for value in get_blocklist_values_from_udm_property(udm_obj.info[prop], prop):
                hashed_value = ldap.dn.escape_dn_chars(hash_blocklist_value(value.encode(*udm_obj.mapping.getEncoding(prop))))
                dn = 'cn=%s,%s' % (hashed_value, bl_dn)
                obj = udm_obj.lo_machine_primary.get(dn)
                if obj and obj['originUniventionObjectIdentifier'][0].decode('utf-8') != udm_obj.entry_uuid:
                    raise univention.admin.uexceptions.valueError(_('The value "%(value)s" is blocked for the property "%(prop)s".') % {'value': value, 'prop': prop}, property=prop)


def cleanup_blocklistentry(blocklist_entries, udm_obj):
    # type: (Iterable, univention.admin.handlers.simpleLdap) -> None
    for entry in blocklist_entries:
        try:
            udm_obj.lo_machine_primary.delete(entry)
        except univention.admin.uexceptions.noObject:
            pass
