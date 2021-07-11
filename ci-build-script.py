#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""Build script for gitlab-ci"""

# included
import os
import sys
import time

# third party
import sh  # pylint: disable=import-error

sh2 = sh(_out='/dev/stdout', _err='/dev/stderr')  # pylint: disable=not-callable

MANDATORY_ENV_VARS = (
    'DOCKER_COMPOSE_BUILD_FILES',
    'UPX_IMAGE_REGISTRY',
)


class AppVersionNotFound(Exception):
    """Raised if /version file could not be read"""


def add_version_label(image_name):
    """Adds a version label to an image"""
    print('Retrieving /version from {}'.format(image_name))
    result = sh2.docker.run(
        '--rm',
        '--entrypoint=/bin/cat',
        image_name,
        '/version',
        _out=None,
    ).stdout
    app_version = result.rstrip().decode('ascii')
    if not app_version:
        raise AppVersionNotFound
    print('Adding version label {}'.format(app_version))
    sh2.docker.build(
        '--label',
        'org.opencontainers.app.version={}'.format(app_version),
        '--tag',
        image_name,
        '-',
        _in='FROM {}'.format(image_name),
    )
    print('Done with labeling')


def main():
    """The main script builds, labels and pushes"""
    for env_var_name in MANDATORY_ENV_VARS:
        if env_var_name not in os.environ:
            print('Please define "{}"!'.format(env_var_name))
            return 1

    if 'CI_JOB_STARTED_AT' not in os.environ:
        time_stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        os.environ['CI_JOB_STARTED_AT'] = time_stamp

    if 'CI_COMMIT_SHA' not in os.environ:
        sha_hash = sh.git('rev-parse', 'HEAD').stdout.rstrip().decode('ascii')
        os.environ['CI_COMMIT_SHA'] = sha_hash

    if 'CI_PIPELINE_ID' not in os.environ:
        os.environ['CI_PIPELINE_ID'] = 'none'

    docker_compose_build_files = os.environ['DOCKER_COMPOSE_BUILD_FILES']
    upx_image_registry = os.environ['UPX_IMAGE_REGISTRY']
    ci_pipeline_id = os.environ['CI_PIPELINE_ID']

    print('DEBUG')
    print(os.environ)

    sh2.cp(
        '.env.univention-directory-manager-rest.example',
        '.env.univention-directory-manager-rest',
    )
    sh2.docker_compose(
        docker_compose_build_files.split(),
        'build',
        '--parallel',
    )

    image_name = '{}container-udm-rest/udm:{}-test'.format(
        upx_image_registry, ci_pipeline_id
    )
    try:
        add_version_label(image_name)
    except AppVersionNotFound:
        return 2

    sh2.docker_compose(
        docker_compose_build_files.split(),
        'push',
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())

# [EOF]
