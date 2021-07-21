#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Vars lib for gitlab-ci"""

# included
import os
import time

# third party
import sh  # pylint: disable=import-error

DEFAULT_UPX_IMAGE_REGISTRY = 'artifacts.knut.univention.de/upx/'

DEFAULT_QUAY_IMAGE_REGISTRY = 'quay.io/univention/'

DEFAULT_CI_PIPELINE_ID = 'none'

MINIMAL_DOCKER_VARS = ['DOCKER_HOST']

COMMON_VARS = (
    'CI_PIPELINE_ID',
    'UPX_IMAGE_REGISTRY',
)

ADDITIONAL_PULL_PUSH_VARS = (
    'DBUS_SESSION_BUS_ADDRESS',
    'PATH',
)

COMMON_BUILD_VARS = (
    'CI_COMMIT_SHA',
    'CI_JOB_STARTED_AT',
    'CI_PROJECT_URL',
)

ADDITIONAL_COMPOSE_BUILD_VARS = (
    'DBUS_SESSION_BUS_ADDRESS',
    'LANG',
    'PWD',
)

DEFAULT_DOCKER_COMPOSE_BUILD_FILES = (
    '--file docker-compose.yaml'
    ' --file docker-compose.override.yaml'
    ' --file docker-compose.prod.yaml'
)


def get_env_vars(var_names):
    """Check for environmental variables and return them as a dict"""
    return {
        var_name: os.environ[var_name]
        for var_name in var_names if var_name in os.environ
    }


def get_docker_envs(
    git_dir,
    pull_push: bool = False,
    build: bool = False,
    compose: bool = False,
) -> dict:
    """Collect env-vars for docker and compose calls"""
    envs = {}

    # variables used in ci-scripts but not as environment
    common_env = {
        'CI_PIPELINE_ID': DEFAULT_CI_PIPELINE_ID,
        'UPX_IMAGE_REGISTRY': DEFAULT_UPX_IMAGE_REGISTRY,
    }
    common_env.update(get_env_vars(COMMON_VARS))
    envs['common'] = common_env

    # environment used by all docker and compose calls
    docker_env = get_env_vars(MINIMAL_DOCKER_VARS)
    envs['docker'] = docker_env

    # environment used by docker pull and push
    if pull_push is True:
        pull_push_env = get_env_vars(ADDITIONAL_PULL_PUSH_VARS)
        pull_push_env.update(docker_env)
        envs['pull_push'] = docker_env

    # labels shared between docker(-compose) build calls
    if build is True or compose is True:
        base_build_env = {
            'CI_PROJECT_URL': 'unset',
        }

        if 'CI_JOB_STARTED_AT' not in os.environ:
            base_build_env['CI_JOB_STARTED_AT'] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )

        if 'CI_COMMIT_SHA' not in os.environ:
            base_build_env['CI_COMMIT_SHA'] = (
                sh.git(  # noqa: E501 ; pylint: disable=too-many-function-args,unexpected-keyword-arg
                    'rev-parse',
                    'HEAD',
                    _cwd=git_dir,
                )
                .stdout.rstrip()
                .decode('ascii')
            )

        base_build_env.update(get_env_vars(COMMON_BUILD_VARS))

    # publish ci-variables in common if building with docker
    if build is True:
        envs['common'].update(base_build_env)

    # environment used by docker-compose
    if compose is True:
        envs['common']['DOCKER_COMPOSE_BUILD_FILES'] = os.environ.get(
            'DOCKER_COMPOSE_BUILD_FILES', DEFAULT_DOCKER_COMPOSE_BUILD_FILES
        )
        compose_env = {
            'CI_PIPELINE_ID': envs['common']['CI_PIPELINE_ID'],
            'COMPOSE_DOCKER_CLI_BUILD': '0',
            'LANG': 'C.UTF-8',
        }
        compose_env.update(base_build_env)
        compose_env.update(get_env_vars(ADDITIONAL_COMPOSE_BUILD_VARS))
        compose_env.update(docker_env)
        envs['compose'] = compose_env

    return envs


# [EOF]
