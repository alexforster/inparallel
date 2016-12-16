# -*- coding: UTF-8 -*-
#
# Copyright © 2016 Alex Forster. All rights reserved.
# This software is licensed under the 3-Clause ("New") BSD license.
# See the LICENSE file for details.
#

import sys
import os
import re
import functools

import six


def decorator(fn):

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        if len(args) == 1 and len(kwargs) == 0 and six.callable(args[0]):
            return fn(args[0])
        else:
            return lambda _: fn(_, *args, **kwargs)

    return wrapper


def extract(text, regex):
    """ :type text: str
        :type regex: str
        :rtype: tuple[str]|str|None
    """

    matches = re.findall(regex, text, flags=re.MULTILINE)

    if matches is None or len(matches) == 0:
        return None

    if len(matches) == 1:
        return matches[0]

    return matches
