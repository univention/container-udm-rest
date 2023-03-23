#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xxxpylint: disable=invalid-name

"""Extract UCR values from UCS and store in the .env file"""

import socket
import subprocess
import sys
from typing import List, Tuple

# default file with the keys to be filled
TEMPLATE_FILE = '.env.univention-directory-manager-rest.example'
# output file with actual values
OUTPU_FILE = '.env.univention-directory-manager-rest'


def ssh(host: str, command: str) -> List[str]:
    """Run the given command on the UCS system."""
    with subprocess.Popen(
        ["ssh", host, command],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        stdout = proc.stdout.readlines()
        if len(stdout) == 0:
            stderr = proc.stderr.readlines()
            print("SSH error:")
            print(stderr)
            sys.exit(1)

        return [line.decode().strip() for line in stdout]


def read_dot_env(filename: str) -> List[Tuple[str, str]]:
    """Read the given .env file into a list of key-value tuples."""
    with open(filename, 'r', encoding='utf-8') as file_handler:
        for line in file_handler.readlines():
            if (not line) or line.startswith('#') or ('=' not in line):
                continue

            key, value = line.split('=', 1)
            yield (key, value)


def write_dot_env(filename: str, variables: dict):
    """Write the given dict to a .env file."""
    with open(filename, 'w', encoding='utf-8') as file_handler:
        for key, value in variables.items():
            file_handler.write(f'{key}={value}\n')


def split_key_value(line: str, sep: str) -> List[str]:
    """Substitute for `line.split(sep, 1)` which handles empty values."""
    key, value = line.split(sep, 1)
    value = value.lstrip()
    return (key, value)


if __name__ == '__main__':
    UCS_HOST = sys.argv[1]

    # grab information from the UCS machine
    ucr = dict(
        split_key_value(line, ':') for line in ssh(UCS_HOST, 'ucr dump')
    )
    admin_secret = ssh(UCS_HOST, 'cat /etc/ldap.secret')[0]
    machine_secret = ssh(UCS_HOST, 'cat /etc/machine.secret')[0]

    envs = dict(read_dot_env(TEMPLATE_FILE))

    # capital variable names will be environment vars
    envs['LDAP_URI'] = f'ldap://{ucr["ldap/master"]}:{ucr["ldap/master/port"]}'
    envs['LDAP_BASE'] = ucr["ldap/base"]
    envs['LDAP_ADMIN_PASSWORD'] = admin_secret
    envs['LDAP_MACHINE_PASSWORD'] = machine_secret

    # fill all other variable names with values from UCR
    output = {}
    for key in envs.keys():
        if key.replace('_', '').isupper():
            output[key] = envs[key]
            continue

        if '.' in key:
            print(f'Key already contains dot: {key}')
            sys.exit(1)

        env_key = key.replace('/', '.')
        output[env_key] = ucr[key]

    # This is the fqdn of the UDM REST server, not the UCS host.
    # Thus we have to get it from the local system, not from UCR.
    output['hostname'], output['domainname'] = socket.getfqdn().split('.', 1)

    write_dot_env(OUTPU_FILE, output)
