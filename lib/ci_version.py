#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Version lib for gitlab-ci"""

# included
import os

# third party
import sh  # pylint: disable=import-error

# internal imports
from ci_log import log

# Characters which are not allowed in docker tags and their substitution
DOCKER_TAG_TRANSLATION = {
    '~': '-',
    '+': 'x',
    ':': '.',
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# pylint: disable=not-callable
sh_out = sh(_out='/dev/stdout', _err='/dev/stderr', _cwd=BASE_DIR)


class AppVersionNotFound(Exception):
    """Raised if /version file could not be read"""


def get_app_version(image_name, docker_env):
    """Retrieves content of /version file from a container"""
    log.info('Retrieving /version from {}', image_name)
    result = sh_out.docker.run(
        '--rm',
        '--entrypoint=/bin/cat',
        image_name,
        '/version',
        _env=docker_env,
        _out=None,
    ).stdout
    app_version = result.rstrip().decode('ascii')
    if not app_version:
        raise AppVersionNotFound
    return app_version


def cleanup_for_docker_tag(app_version):
    """Cleanup version for docker tags"""
    return app_version.translate(str.maketrans(DOCKER_TAG_TRANSLATION))


# [EOF]
