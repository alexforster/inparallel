# -*- coding: UTF-8 -*-
#
# Copyright © 2016 Alex Forster. All rights reserved.
# This software is licensed under the 3-Clause ("New") BSD license.
# See the LICENSE file for details.
#

import sys
import os
import time
import functools
import threading
import multiprocessing
import concurrent.futures

import six
import tblib.pickling_support

from . import util


_tasks = None


def _worker():

    global _tasks

    tblib.pickling_support.install()

    while getattr(_worker, 'running'):

        for child_pid, task in six.iteritems(_tasks.copy()):

            future = task[0]
            parent = task[1]
            parent_ex = task[2]

            if parent.poll():

                try:

                    result = parent.recv()

                    parent.close()
                    parent_ex.close()

                    future.set_result(result)

                    del _tasks[child_pid]
                    continue

                except EOFError:

                    pass

            if parent_ex.poll():

                try:

                    ex_type, ex_value, ex_traceback = parent_ex.recv()

                    parent.close()
                    parent_ex.close()

                    if six.PY2:
                        ex = ex_type(ex_value)
                        future.set_exception_info(ex, ex_traceback)
                    elif six.PY3:
                        ex = ex_type(ex_value).with_traceback(ex_traceback)
                        future.set_exception(ex)

                    del _tasks[child_pid]
                    continue

                except EOFError:

                    pass

        time.sleep(0.001)


def _future(child_pid, parent, parent_ex):
    """ :type parent: multiprocessing.Connection
        :type parent_ex: multiprocessing.Connection
        :rtype future: concurrent.futures.Future
    """

    global _tasks

    if getattr(_worker, 'pid', -1) != os.getpid():

        _tasks = {}

        thread = threading.Thread(target=_worker, name='inparallel-{}'.format(os.getpid()))
        thread.setDaemon(True)

        setattr(_worker, 'pid', os.getpid())
        setattr(_worker, 'thread', thread)
        setattr(_worker, 'running', True)

        thread.start()

    future = concurrent.futures.Future()
    future.set_running_or_notify_cancel()

    _tasks[child_pid] = (future, parent, parent_ex)

    return future


@util.decorator
def task(fn):

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        parent, child = multiprocessing.Pipe()
        parent_ex, child_ex = multiprocessing.Pipe()
        child_pid = os.fork()

        if child_pid == 0:

            try:

                child.send(fn(*args, **kwargs))

            except Exception:

                child_ex.send(sys.exc_info())

            finally:

                child.close()
                child_ex.close()

            if hasattr(_worker, 'thread'):

                setattr(_worker, 'running', False)
                getattr(_worker, 'thread').join()

            sys.exit(0)

        return _future(child_pid, parent, parent_ex)

    return wrapper
