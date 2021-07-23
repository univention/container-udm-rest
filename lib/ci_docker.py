#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Docker lib for gitlab-ci"""

# included
import os

# third party
import sh  # pylint: disable=import-error

# internal imports
from ci_log import log
import ci_vars
import ci_version

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# pylint: disable=not-callable
sh_out = sh(_out='/dev/stdout', _err='/dev/stderr', _cwd=BASE_DIR)


class DockerPullFailed(Exception):
    """Raised if docker pull fails"""


class DockerPushFailed(Exception):
    """Raised if docker pull fails"""


def add_and_push_tag(
    image_name: str,
    tag: str,
    docker_env: dict,
    pull_push_env: dict,
):
    """Adds a tag to an image"""
    log.info('Adding tag {} to {}', tag, image_name)
    sh_out.docker.tag(image_name, tag, _env=docker_env)
    try:
        sh_out.docker.push(tag, _env=pull_push_env)
    # pylint: disable=no-member
    except sh.ErrorReturnCode_1 as docker_pull_failed:
        raise DockerPushFailed from docker_pull_failed
    log.info('Done with this tag')


def add_version_label(app_version: str, image_name: str, docker_env: dict):
    """Adds a version label to an image"""
    log.info('Adding version label {}', app_version)
    sh_out.docker.build(
        '--label',
        'org.opencontainers.app.version={}'.format(app_version),
        '--tag',
        image_name,
        '-',
        _env=docker_env,
        _in='FROM {}'.format(image_name),
    )
    log.info('Done with labeling')


def add_and_push_build_tags(  # pylint: disable=too-many-arguments
    build_path: str,
    push_path: str,
    clean_version: str,
    ci_pipeline_id: str,
    docker_env: dict,
    pull_push_env: dict,
):
    """Add and push build tags"""
    tag = '{}:build-{}'.format(push_path, ci_pipeline_id)
    # push tag "build-<ci-pipeline-id>"
    add_and_push_tag(build_path, tag, docker_env, pull_push_env)

    tag = '{}:{}-{}'.format(push_path, clean_version, ci_pipeline_id)
    # push tag "<version>-<ci-pipeline-id>"
    add_and_push_tag(build_path, tag, docker_env, pull_push_env)


def add_and_push_release_tags(
    build_path: str,
    push_path: str,
    clean_version: str,
    docker_env: dict,
    pull_push_env: dict,
):
    """Add and push latest and version tags"""
    tag = '{}:latest'.format(push_path)
    # push tag "latest"
    add_and_push_tag(build_path, tag, docker_env, pull_push_env)

    tag = '{}:{}'.format(push_path, clean_version)
    # push tag "<version>"
    add_and_push_tag(build_path, tag, docker_env, pull_push_env)


def add_and_push_build_version_label_and_tag(
    image_name: str,
    ci_pipeline_id: str,
    docker_env: dict,
    pull_push_env: dict,
):
    """Get the version, add it as a label and push it as a tag with build-id"""

    upx_image_registry = os.environ.get(
        'UPX_IMAGE_REGISTRY',
        ci_vars.DEFAULT_UPX_IMAGE_REGISTRY,
    )
    upx_image_path = '{}{}'.format(upx_image_registry, image_name)

    build_path = '{}:build-{}'.format(upx_image_path, ci_pipeline_id)
    app_version = ci_version.get_app_version(build_path, docker_env)

    add_version_label(app_version, build_path, docker_env)

    clean_version = ci_version.cleanup_for_docker_tag(app_version)

    # push tag "build-<ci-pipeline-id>" and "<version>-<ci-pipeline-id>"
    #   to univention-harbor
    add_and_push_build_tags(
        build_path,
        upx_image_path,
        clean_version,
        ci_pipeline_id,
        docker_env,
        pull_push_env,
    )


def pull_add_push_publish_version_tag(
    image_name: str,
    ci_pipeline_id: str,
    docker_env: dict,
    pull_push_env: dict,
):
    """Get the version, push latest and version tags"""

    upx_image_registry = os.environ.get(
        'UPX_IMAGE_REGISTRY',
        ci_vars.DEFAULT_UPX_IMAGE_REGISTRY,
    )
    upx_image_path = '{}{}'.format(upx_image_registry, image_name)

    quay_image_registry = os.environ.get(
        'QUAY_IMAGE_REGISTRY',
        ci_vars.DEFAULT_QUAY_IMAGE_REGISTRY,
    )
    quay_image_path = '{}{}'.format(quay_image_registry, image_name)

    build_path = '{}:build-{}'.format(upx_image_path, ci_pipeline_id)

    try:
        sh_out.docker.pull(build_path, _env=pull_push_env)
    # pylint: disable=no-member
    except sh.ErrorReturnCode_1 as docker_pull_failed:
        raise DockerPullFailed from docker_pull_failed

    app_version = ci_version.get_app_version(build_path, docker_env)
    clean_version = ci_version.cleanup_for_docker_tag(app_version)

    # push tag "latest" and "<version>" to univention-harbor
    add_and_push_release_tags(
        build_path,
        upx_image_path,
        clean_version,
        docker_env,
        pull_push_env,
    )

    # push tag "build-<ci-pipeline-id>" and "<version>-<ci-pipeline-id>"
    #   to quay
    add_and_push_build_tags(
        build_path,
        quay_image_path,
        clean_version,
        ci_pipeline_id,
        docker_env,
        pull_push_env,
    )

    # push tag "latest" and "<version>" to quay
    add_and_push_release_tags(  # pylint: disable=too-many-function-args
        build_path,
        quay_image_path,
        clean_version,
        docker_env,
        pull_push_env,
    )


# [EOF]
