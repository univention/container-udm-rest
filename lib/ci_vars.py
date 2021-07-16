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

ADDITIONAL_PULL_PUSH_VARS = (
    'DBUS_SESSION_BUS_ADDRESS',
    'PATH',
)

ADDITIONAL_COMPOSE_VARS = (
    'CI_COMMIT_SHA',
    'CI_JOB_STARTED_AT',
    'CI_PIPELINE_ID',
    'CI_PROJECT_URL',
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
    git_dir, pull_push: bool = False, compose: bool = False
) -> dict:
    """Collect env-vars for docker and compose calls"""
    envs = {}

    docker_env = get_env_vars(MINIMAL_DOCKER_VARS)
    envs['docker'] = docker_env

    if pull_push is True:
        pull_push_env = get_env_vars(ADDITIONAL_PULL_PUSH_VARS)
        pull_push_env.update(docker_env)
        envs['pull_push'] = docker_env

    if compose is True:
        compose_env = {
            'COMPOSE_DOCKER_CLI_BUILD': '0',
            'CI_PROJECT_URL': 'unset',
            'CI_PIPELINE_ID': DEFAULT_CI_PIPELINE_ID,
            'LANG': 'C.UTF-8',
        }

        if 'CI_JOB_STARTED_AT' not in os.environ:
            compose_env['CI_JOB_STARTED_AT'] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )

        if 'CI_COMMIT_SHA' not in os.environ:
            compose_env['CI_COMMIT_SHA'] = (
                sh.git(  # pylint: disable=too-many-function-args,unexpected-keyword-arg
                    'rev-parse',
                    'HEAD',
                    _cwd=git_dir,
                ).stdout.rstrip().decode('ascii')
            )

        compose_env.update(get_env_vars(ADDITIONAL_COMPOSE_VARS))
        compose_env.update(docker_env)
        envs['compose'] = compose_env

    return envs


# [EOF]
