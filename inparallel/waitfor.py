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


def waitfor(in_flight, concurrency_factor=None):
    """ :type in_flight: collections.MutableSequence[concurrent.futures.Future]
        :type concurrency_factor: int|None
        :rtype: collections.Iterable[concurrent.futures.Future|None]
    """

    assert(isinstance(in_flight, collections.MutableSequence))
    assert(concurrency_factor is None or isinstance(concurrency_factor, six.integer_types) and concurrency_factor > 0)

    while True:

        done = [t for t in in_flight if t.done()]

        for task in done:

            in_flight.remove(task)
            yield task

        if concurrency_factor is not None and len(in_flight) < concurrency_factor:

            yield None

        if len(in_flight) == 0:

            break

        time.sleep(0.001)
