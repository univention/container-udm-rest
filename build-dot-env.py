#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xxxpylint: disable=invalid-name

"""Extract UCR values from UCS and store in the .env file"""

import subprocess
import sys
from typing import List, Tuple


# default file with the keys to be filled
template_file = '.env.univention-directory-manager-rest.example'
# output file with actual values
output_file = '.env.univention-directory-manager-rest'


def ssh(host: str, command: str) -> List[str]:
    """Run the given command on the UCS system."""
    ssh = subprocess.Popen(["ssh", host, command],
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout = ssh.stdout.readlines()
    if len(stdout) > 0:
        return [ line.decode().strip() for line in stdout ]
    else:
        stderr = ssh.stderr.readlines()
        print("SSH error:")
        print(stderr)
        sys.exit(1)


def read_dot_env(filename: str) -> List[Tuple[str, str]]:
    """Read the given .env file into a list of key-value tuples."""
    with open(filename, 'r', encoding='utf-8') as fd:
        for line in fd.readlines():
            if (not line) \
                or line.startswith('#') \
                or ('=' not in line):
                continue

            key, value = line.split('=', 1)
            yield (key, value)


def write_dot_env(filename: str, vars: dict):
    """Write the given dict to a .env file."""
    with open(filename, 'w', encoding='utf-8') as fd:
        for key, value in vars.items():
            fd.write(f'{key}={value}\n')


def split_key_value(line: str, sep: str) -> List[str]:
    """Substitute for `line.split(sep, 1)` which handles empty values."""
    key, value = line.split(sep, 1)
    value = value.lstrip()
    return (key, value)


if __name__ == '__main__':
    ucs_host = sys.argv[1]

    ucr = dict(split_key_value(line, ':') for line in ssh(ucs_host, 'ucr dump'))
    admin_secret = ssh(ucs_host, 'cat /etc/ldap.secret')[0]
    machine_secret = ssh(ucs_host, 'cat /etc/machine.secret')[0]

    vars = dict(read_dot_env(template_file))

    vars['LDAP_URI'] = f'ldap://{ucr["ldap/master"]}:{ucr["ldap/master/port"]}'
    vars['LDAP_BASE'] = ucr["ldap/base"]
    vars['LDAP_ADMIN_PASSWORD'] = admin_secret
    vars['LDAP_MACHINE_PASSWORD'] = machine_secret

    output = {}
    for key in vars.keys():
        if key.replace('_', '').isupper():
            output[key] = vars[key]
            continue

        if '.' in key:
            print(f'Key already contains dot: {key}')
            sys.exit(1)

        env_key = key.replace('/', '.')
        output[env_key] = ucr[key]

    write_dot_env(output_file, output)
