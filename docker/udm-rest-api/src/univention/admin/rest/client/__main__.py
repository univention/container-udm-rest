#!/usr/bin/python3
#
# Univention Management Console
#  Univention Directory Manager Module
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2019-2023 Univention GmbH
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


import argparse
import io
import json
import locale
import os
import sys

import ldap
import ldap.dn

from univention.admin.rest.client import (
    UDM, ConnectionError, HTTPError, NotFound, ServerError, ServiceUnavailable, Unauthorized, UnprocessableEntity,
)
from univention.config_registry import ucr


class CLIClient:

    def init(self, parser, args):
        self.parser = parser
        username = args.binddn
        try:
            username = ldap.dn.str2dn(username)[0][0][1]
        except (ldap.DECODING_ERROR, IndexError):
            pass
        self.udm = UDM('https://%(hostname)s.%(domainname)s/univention/udm/' % ucr, username, args.bindpwd, user_agent='univention.cli/%(version/version)s-%(version/patchlevel)s-errata%(version/erratalevel)s' % ucr, language=args.language)

    def get_modules(self):
        return self.udm.modules()

    def show_modules(self, args):
        self.print_line('All modules')
        for mod, modtitle in sorted({(x.name, x.title) for x in self.get_modules()}):
            self.print_line(mod, modtitle, prefix='  ')

    def get_module(self, object_type):
        module = self.udm.get(object_type)
        if module is None:
            self.show_modules(None)
            self.print_error('The given module is not known. Choose one of the above.')
            raise SystemExit(1)
        return module

    def create_object(self, args):
        module = self.get_module(args.object_type)
        obj = module.new(position=args.position, superordinate=args.superordinate, template=args.template)
        if args.position:
            obj.position = args.position
        self.set_properties(obj, args)
        self.save_object(obj)
        self.print_line('Object created', obj.dn)

    def modify_object(self, args):
        module = self.get_module(args.object_type)
        # TODO: re-execute if changed in between
        try:
            obj = module.get(args.dn)
        except (NotFound, UnprocessableEntity):
            if args.ignore_not_exists:
                self.print_line('Object not found', args.dn)
                return
            else:
                raise
        self.set_properties(obj, args)
        self.save_object(obj)
        self.print_line('Object modified', obj.dn)

    def remove_object(self, args):
        module = self.get_module(args.object_type)
        try:
            obj = module.get(args.dn)
        except (NotFound, UnprocessableEntity):
            if args.ignore_not_exists:
                self.print_line('Object not found', args.dn)
                return
            else:
                raise
        obj.delete(args.remove_referring)
        self.print_line('Object removed', obj.dn)

    def move_object(self, args):
        module = self.get_module(args.object_type)
        obj = module.get(args.dn)
        obj.position = args.position
        self.save_object(obj)
        self.print_line('Object modified', obj.dn)

    def copy_object(self, args):
        pass

    def save_object(self, obj):
        try:
            obj.save()
        except UnprocessableEntity as exc:
            self.handle_unprocessible_entity(exc.error_details)
            raise SystemExit(2)

    def set_properties(self, obj, args):
        obj.superordinate = getattr(args, 'superordinate', None)
        for key, value in obj.options.items():
            if key in args.option or key in args.append_option:
                obj.options[key] = True
            if key in args.remove_option:
                obj.options[key] = False

        for key_val in args.set:
            key, value = self.parse_input(key_val)
            obj.properties[key] = value

        for key_val in args.append:
            key, value = self.parse_input(key_val)
            obj.properties[key].append(value)

        for key_val in getattr(args, 'remove', []):
            if '=' not in key_val:
                obj.properties[key_val] = None
            else:
                key, value = self.parse_input(key_val)
                if obj.properties[key] == value:
                    obj.properties[key] = None
                elif isinstance(obj.properties[key], list) and value in obj.properties[key]:
                    obj.properties[key].remove(value)

        for policy_dn in args.policy_reference:
            # FIXME: we need to know the type, use policies/policy so far
            obj.policies.setdefault('policies/policy', []).append(policy_dn)

        for policy_dn in getattr(args, 'policy_dereference', []):
            for values in obj.policies.values():
                if policy_dn in values:
                    values.remove(policy_dn)

    def parse_input(self, key_val):
        key, _, value = key_val.partition('=')
        key, convert, type_ = key.partition(':')
        if value.startswith('@'):
            try:
                value = open(value[1:], 'rb').read().decode('UTF-8')
            except (OSError, ValueError) as exc:
                self.print_error(f'{key}: {exc}')
                raise SystemExit(2)
        if convert:
            if type_ in ('array', 'object', 'list', 'string', 'str'):
                value = json.loads(value)
            elif type_ == 'int':
                value = int(value)
            elif type_ == 'null':
                value = None
        return key, value

    def get_object(self, args):
        args.superordinate = None
        self.list_objects(args)

    def list_objects(self, args):
        try:
            return self._list_objects(args)
        except UnprocessableEntity as exc:
            self.handle_unprocessible_entity(exc.error_details)
            raise SystemExit(2)

    def _list_objects(self, args):
        module = self.get_module(args.object_type)

        for entry in module.search(args.filter, args.position, opened=True, superordinate=args.superordinate):
            self.print_line('')
            self.print_line('DN', entry.dn)
            self.print_line('URL', entry.uri)
            self.print_line('Object-Type', entry.object_type)
            if args.as_json:
                print(json.dumps(entry.options, indent=4, ensure_ascii=False))
                print(json.dumps(entry.properties, indent=4, ensure_ascii=False))
                print(json.dumps(entry.policies, indent=4, ensure_ascii=False))
                continue
            for key, value in sorted(entry.properties.items()):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, (str, bytes, int, float)):
                            self.print_line(key, item, '  ')
                        else:
                            self.print_line(key, json.dumps(item, ensure_ascii=False), '  ')
                elif value is None:
                    self.print_line(key, '', '  ')
                elif isinstance(value, (bool, int, float)):
                    self.print_line(key, str(value), '  ')
                elif isinstance(value, (str, bytes, int, float)):
                    if set(value) & set('\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f'):
                        key = key + ':'
                        value = value.encode('base64').rstrip()
                    self.print_line(key, value, '  ')
                elif isinstance(value, dict):
                    self.print_line(key, json.dumps(value, ensure_ascii=False, indent=4), '  ')
                else:
                    self.print_line(key, repr(value), '  ')
            if args.policies:
                self.print_line('Policy-based Settings:', '', '  ')
                entry.reload()  # expensive when done for every object of the search
                self.policy_result_for(entry, indent='    ')

    def list_choices(self, args):
        module = self.get_module(args.object_type)
        choices = module.get_property_choices(args.property)
        for value, label in choices:
            self.print_line('Label', label)
            self.print_line('Value', value)
            self.print_line('')

    def policy_result(self, args):
        module = self.get_module(args.object_type)
        entry = module.get(args.dn)
        self.policy_result_for(entry)

    def policy_result_for(self, entry, indent=''):
        for key in entry.policies:
            vals = entry.policy_result(key)
            for prop, items in vals.items():
                if not isinstance(items, list):
                    items = [items]
                # TODO: support different output types like -s/--shell, -b/--basic
                self.print_line('Policy-Type', key, indent)
                for item in items:
                    self.print_line('Policy', item['policy'], indent + '  ')
                    self.print_line('Attribute', prop, indent + '  ')
                    self.print_line('Value', item['value'], indent + '  ')
                    self.print_line('Fixed', item['fixed'], indent + '  ')
                    self.print_line('')

    def list_reports(self, args):
        module = self.get_module(args.object_type)
        for report_type in module.get_report_types():
            self.print_line('Report-Type', report_type)

    def create_report(self, args):
        module = self.get_module(args.object_type)
        report = module.create_report(args.report_type, args.dns)
        args.output.write(report)

    def print_line(self, key, value='', prefix='', stream=sys.stdout):
        # prints and makes sure that no ANSI escape sequences or binary data is printed
        if key:
            key = f'{key}: '
        value = f'{prefix}{key}{value}'
        value = value.replace('\n', f'\n{prefix}')
        print(''.join(v for v in value if v not in '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f'), file=stream)

    def print_warning(self, value='', prefix='Warning'):
        self.print_line(prefix, value, '', stream=sys.stderr)

    def print_error(self, value='', prefix='Error'):
        self.print_line(prefix, value, '', stream=sys.stderr)

    def get_info(self, args, stream=sys.stdout):
        module = self.get_module(args.object_type)
        module.load_relations()
        # mod = self.udm.client.resolve_relation(module.relations, 'create-form', template={'position': '', 'superordinate': ''})  # TODO: integrate in client.py?
        properties = module.get_properties()
        layout = module.get_layout()

        for layout in layout:
            print('  %s - %s:' % (layout['label'], layout['description']), file=stream)
            for sub in layout['layout']:
                self.print_layout(sub, properties, stream=stream)
            print('', file=stream)

    def print_layout(self, sub, properties, indent=1, stream=None):
        def _print_prop(prop):
            def _get_flags(vals):
                flags = []
                if vals.get('required'):
                    flags.append('c')
                if vals.get('identifies') and vals.get('editable'):
                    flags.append('m')
                    flags.append('r')
                if not vals.get('editable', True):
                    flags.append('e')
                flags.extend(vals.get('options', []))
                if vals.get('multivalue'):
                    flags.append('[]')
                return ' (%s)' % ','.join(flags) if flags else ''

            def _print(prop):
                if isinstance(prop, dict):
                    print(repr(prop), file=stream)
                    return
                vals = properties.get(prop, {})
                print('\t\t%s%s' % ((prop + _get_flags(vals)).ljust(41), vals.get('label')), file=stream)

            if isinstance(prop, list):
                for prop in prop:
                    _print(prop)
            else:
                _print(prop)

        if isinstance(sub, dict):
            print('\t%s %s' % (sub['label'], sub['description']), file=stream)
            for prop in sub['layout']:
                if isinstance(prop, dict):
                    self.print_layout(prop, properties, indent + 1, stream=stream)
                else:
                    _print_prop(prop)
        else:
            if isinstance(sub, dict):
                self.print_layout(prop, properties, indent + 1, stream=stream)
            else:
                _print_prop(sub)

    def license(self, args):
        pass

    def handle_unprocessible_entity(self, error):
        for err in error['error']:
            location = '.'.join(err['location'][1:])
            self.print_error(f"{location}({err['type']}): {err['message']}")

    def handle_server_error(self, error):
        for e in ('title', 'message', 'traceback'):
            error.setdefault(e, '')
        self.print_error('%(title)s: %(message)s\n%(traceback)s' % error)
        self.handle_unprocessible_entity(error)


def Unicode(bytestring):
    if isinstance(bytestring, bytes):
        return bytestring.decode(sys.getfilesystemencoding())
    return bytestring


def parse_known_args(parser, client, known_args=None, subparsers=None):
    class Format(argparse.ArgumentDefaultsHelpFormatter):
        def format_help(self):
            raise SystemExit(0)

    def supress_errors(message):
        raise SystemExit(1)
    formatter = parser.formatter_class
    error = parser.error
    try:
        parser.formatter_class = Format
        parser.error = supress_errors
        args, opts = parser.parse_known_args()
        args.options = opts
        return args
    except SystemExit:
        if subparsers:
            parser.formatter_class = argparse_module_help(client, parser, known_args, subparsers)
            parser.print_help()
            raise
    finally:
        parser.error = error
        parser.formatter_class = formatter


def argparse_module_help(client, parser, known_args, subparsers):
    # class FormatModule(argparse.ArgumentDefaultsHelpFormatter):
    class FormatModule(argparse.RawTextHelpFormatter):

        def format_help(self):
            help_string = super().format_help()
            if known_args:
                known_args.subparsers = subparsers
                try:
                    client.init(parser, known_args)
                    x = io.StringIO()
                    client.get_info(known_args, stream=x)
                    help_string += '\n' + x.getvalue()
                except (HTTPError, ConnectionError):
                    pass
            return help_string

        def start_section(self, section):
            super().start_section(section)
            if section == 'actions':
                for sub in subparsers.choices.values():
                    self.add_text(sub.format_help())

    return FormatModule


def main():
    client = CLIClient()
    locale.setlocale(locale.LC_ALL, os.environ.get('LANG', 'C'))
    description = '%(prog)s command line interface for managing UCS\ncopyright (c) 2001-2023 Univention GmbH, Germany\n\nUsage:\n %(prog)s module action [options]\n %(prog)s [--help] [--version]\n'
    parser = argparse.ArgumentParser(
        prog='univention-directory-manager',
        # usage=argparse.SUPPRESS,
        usage=description,
        #description='\n'.join(x.ljust(64, 'x') for x in description.splitlines()),
        # add_help=False,
        epilog='''Description:
univention-directory-manager is a tool to handle the configuration for UCS on command line level.
Use "univention-directory-manager modules" for a list of available modules.''',
    )
    parser.set_defaults(parser=parser)
    parser.add_argument('--binddn', help='bind DN', default='Administrator', type=Unicode)
    parser.add_argument('--bindpwd', help='bind password', default='univention', type=Unicode)
    parser.add_argument('--bindpwdfile', help='file containing bind password', type=Unicode)
    parser.add_argument('--logfile', help='path and name of the logfile to be used', type=Unicode)
    parser.add_argument('--language', default=(locale.getlocale(locale.LC_MESSAGES)[0] or 'en_US').replace('_', '-'), help=argparse.SUPPRESS)
    parser.add_argument('--tls', choices=['0', '1', '2'], default='2', help='0 (no); 1 (try); 2 (must)')
    parser.add_argument('--version', action='version', version='%(prog)s VERSION TODO', help='print version information')  # FIXME: version number

    parser.add_argument('object_type')
    known_args = parse_known_args(parser, client)

#    if known_args and known_args.object_type in ('license', 'modules'):
#        mods = object_type.add_parser(str('modules'), description='Show all available modules')
#        mods.set_defaults(func=client.show_modules)
#
#        license = object_type.add_parser(str('license'), description='View or modify license information')
#        license.set_defaults(func=client.license)
#        license.add_argument('--request', action='store_true')
#        license.add_argument('--check', action='store_true')
#        license.add_argument('--import')

    subparsers = add_object_action_arguments(parser, client)
    parser.formatter_class = argparse_module_help(client, parser, known_args, subparsers)
    parse_known_args(parser, client, known_args, subparsers)

    args = parser.parse_args()
    try:
        client.init(parser, args)
        args.func(args)
    except ConnectionError:
        parser.error('The connection to the service failed. Retry again later.')
    except Unauthorized:
        parser.error('The authentication has failed.')
    except ServerError as exc:
        error = exc.error_details
        if error:
            client.handle_server_error(error)
        parser.error(str(exc))
    except ServiceUnavailable:
        parser.error('The service is currently unavailable. Retry again later.')


def add_object_action_arguments(parser, client):
    subparsers = parser.add_subparsers(dest='action', title='actions', description='All available actions')
    parser.set_defaults(subparsers=subparsers, func=client.get_info)

    def add_subparser(name, *args, **kwargs):
        kwargs.setdefault('description', '%s: %s' % (name, kwargs.get('help', '')))
        kwargs.setdefault('add_help', False)
        return subparsers.add_parser(name, *args, **kwargs)

    create = add_subparser('create', help='Create a new object', usage=argparse.SUPPRESS)
    create.set_defaults(func=client.create_object)
    create.add_argument('--position', help='Set position in tree', type=Unicode)
    # create.add_argument('--default-position', action='store_true', help='Create in the default position')  # TODO: probably better make this the default?
    create.add_argument('--template', help='Use template for creation', type=Unicode)
    create.add_argument('--set', action='append', help='Set property to value, e.g. foo=bar', default=[], type=Unicode)
    create.add_argument('--append', action='append', help='Append value to property, e.g. foo=bar', default=[], type=Unicode)
    create.add_argument('--remove', action='append', help='Remove value from property, e.g. foo=bar', default=[], type=Unicode)
    create.add_argument('--superordinate', help='Use superordinate', type=Unicode)
    create.add_argument('--option', action='append', help='Use only given module options', default=[], type=Unicode)
    create.add_argument('--append-option', action='append', help='Append the module options', default=[], type=Unicode)
    create.add_argument('--remove-option', action='append', help='Remove the module options', default=[], type=Unicode)
    create.add_argument('--policy-reference', action='append', help='Reference to policy given by DN', default=[], type=Unicode)
    create.add_argument('--ignore-exists', action='store_true', help='ignore if object already exists')

    modify = add_subparser('modify', help='Modify an existing object', usage=argparse.SUPPRESS)
    modify.set_defaults(func=client.modify_object)
    modify.add_argument('--dn', help='Edit object with DN', type=Unicode)
    modify.add_argument('--set', action='append', help='Set property to value, e.g. foo=bar', default=[], type=Unicode)
    modify.add_argument('--append', action='append', help='Append value to property, e.g. foo=bar', default=[], type=Unicode)
    modify.add_argument('--remove', action='append', help='Remove value from property, e.g. foo=bar', default=[], type=Unicode)
    modify.add_argument('--option', action='append', help='Use only given module options', default=[], type=Unicode)
    modify.add_argument('--append-option', action='append', help='Append the module options', default=[], type=Unicode)
    modify.add_argument('--remove-option', action='append', help='Remove the module options', default=[], type=Unicode)
    modify.add_argument('--policy-reference', action='append', help='Reference to policy given by DN', default=[], type=Unicode)
    modify.add_argument('--policy-dereference', action='append', help='Remove reference to policy given by DN', default=[], type=Unicode)
    modify.add_argument('--ignore-not-exists', action='store_true', help='ignore if object does not exists')

    remove = add_subparser('remove', help='Remove an existing object', usage=argparse.SUPPRESS)
    remove.set_defaults(func=client.remove_object)
    remove.add_argument('--dn', help='Remove object with DN', type=Unicode)
    # remove.add_argument('--superordinate', help='Use superordinate', type=Unicode)  # not required
    remove.add_argument('--filter', help='Lookup filter e.g. foo=bar', type=Unicode)
    remove.add_argument('--remove-referring', action='store_true', help='remove referring objects', default=False)
    remove.add_argument('--ignore-not-exists', action='store_true', help='ignore if object does not exists')

    list_ = add_subparser('list', help='List objects', usage=argparse.SUPPRESS)
    list_.set_defaults(func=client.list_objects)
    list_.add_argument('--filter', help='Lookup filter e.g. foo=bar', default='', type=Unicode)
    list_.add_argument('--position', help='Search underneath of position in tree', type=Unicode)
    list_.add_argument('--superordinate', help='Use superordinate', type=Unicode)
    list_.add_argument('--policies', help='List policy-based settings: 0:short, 1:long (with policy-DN)', type=Unicode)
    list_.add_argument('--as-json', help='Print JSON (developer mode)', action='store_true')

    get = add_subparser('get', help='Get object', usage=argparse.SUPPRESS)
    get.set_defaults(func=client.get_object)
    get.add_argument('position', metavar='dn', help='The object LDAP DN', type=Unicode)
    get.add_argument('--filter', help='Lookup filter e.g. foo=bar', default='', type=Unicode)
    get.add_argument('--policies', help='List policy-based settings: 0:short, 1:long (with policy-DN)', type=Unicode)
    get.add_argument('--as-json', help='Print JSON (developer mode)', action='store_true')

    move = add_subparser('move', help='Move object in directory tree', usage=argparse.SUPPRESS)
    move.set_defaults(func=client.move_object)
    move.add_argument('--dn', help='Move object with DN', type=Unicode)
    move.add_argument('--position', help='Move to position in tree', type=Unicode)

    copy = add_subparser('copy', help='Copy object in directory tree', usage=argparse.SUPPRESS)
    copy.set_defaults(func=client.copy_object)

    list_choices = add_subparser('list-choices', help='List all possible choices for the selected property', usage=argparse.SUPPRESS)
    list_choices.set_defaults(func=client.list_choices)
    list_choices.add_argument('property', help='The property to list choices for')

    policy_result = add_subparser('policy-result', help='List all possible choices for the selected property', usage=argparse.SUPPRESS)
    policy_result.set_defaults(func=client.policy_result)
    policy_result.add_argument('dn')

    list_reports = add_subparser('list-reports', help='List all possible report types for selected object type', usage=argparse.SUPPRESS)
    list_reports.set_defaults(func=client.list_reports)

    reports = add_subparser('create-report', help='Create report for selected objects', usage=argparse.SUPPRESS)
    reports.set_defaults(func=client.create_report)
    reports.add_argument('-o', '--output', type=argparse.FileType('w'), default='-', help='Filename to write report to')
    reports.add_argument('report_type')
    reports.add_argument('dns', nargs='*')

    info = add_subparser('info', help='Print information about the object type', usage=argparse.SUPPRESS)
    info.set_defaults(func=client.get_info)

    return subparsers


if __name__ == '__main__':
    main()
