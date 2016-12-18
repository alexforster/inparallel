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
    """ :type tasks: collections.MutableSequence[concurrent.futures.Future]
        :rtype: collections.Iterable[concurrent.futures.Future]
    """

    assert(isinstance(tasks, collections.MutableSequence))

    while True:

        done = [t for t in tasks if t.done()]

        for task in done:

            tasks.remove(task)
            yield task

        if len(tasks) == 0:

            break

        time.sleep(0.001)
