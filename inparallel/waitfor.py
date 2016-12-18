# -*- coding: UTF-8 -*-
#
# Copyright © 2016 Alex Forster. All rights reserved.
# This software is licensed under the 3-Clause ("New") BSD license.
# See the LICENSE file for details.
#

import sys
import os
import time
import collections
import concurrent.futures

import six


def waitfor(tasks):
    """ :type tasks: list[concurrent.futures.Future]
        :rtype: list[concurrent.futures.Future]
    """

    assert(isinstance(tasks, collections.Iterable))

    tasks = list(tasks)

    while True:

        done = [t for t in tasks if t.done()]

        for task in done:

            yield task

        tasks = [t for t in tasks if t not in done]

        if len(tasks) == 0:

            break

        time.sleep(0.001)
