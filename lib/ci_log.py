#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Log init lib for gitlab-ci"""

import logging
import time


# inspired by https://stackoverflow.com/a/26003573/509648
class BraceString(str):
    """Use new-style format for log-messages"""

    def __mod__(self, other):
        return self.format(*other)


# inspired by https://stackoverflow.com/a/26003573/509648
class StyleAdapter(logging.LoggerAdapter):
    """Replace the default adapter just to reference BraceString"""

    def __init__(
        self,
        logger,
        extra=None,
    ):  # noqa: E501; pylint: disable=useless-parent-delegation
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        msg = BraceString(msg)
        return msg, kwargs


def get_logger():
    """Configure the logger and return it"""
    logger = logging.getLogger('ci')
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='{asctime} {name} {levelname:<8s} {message}s',
        datefmt='%Y-%m-%dT%H:%M:%SZ',
        style='{',
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    adapter = StyleAdapter(logger)
    return adapter


log = get_logger()

# [EOF]
