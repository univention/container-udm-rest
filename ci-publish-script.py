#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""Build script for gitlab-ci"""

# included
import os
import sys

# internal imports
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LIBS_DIR = os.path.join(BASE_DIR, 'lib')
sys.path.insert(1, LIBS_DIR)

import ci_docker  # noqa: E402,E501; pylint: disable=import-error,wrong-import-position
from ci_log import (  # noqa: E402,E501; pylint: disable=import-error,wrong-import-position
    log,
)
import ci_vars  # noqa: E402; pylint: disable=import-error,wrong-import-position
import ci_version  # noqa: E402,E501; pylint: disable=import-error,wrong-import-position


def main():
    """The main script builds, labels and pushes"""

    image_name = 'upx-udm-rest'

    envs = ci_vars.get_docker_envs(BASE_DIR, pull_push=True)

    try:
        # push tags "latest" and "<version>"
        ci_docker.pull_add_push_publish_version_tag(
            image_name,
            envs['common']['CI_PIPELINE_ID'],
            envs['docker'],
            envs['pull_push'],
        )
    except ci_version.AppVersionNotFound:
        log.error('app version not found')
        return 2
    except ci_docker.DockerPullFailed:
        log.error('docker pull failed')
        return 1
    except ci_docker.DockerPushFailed:
        log.error('docker push failed')
        return 3

    return 0


if __name__ == '__main__':
    sys.exit(main())

# [EOF]
