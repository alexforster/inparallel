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

from tblib.pickling_support import pickle_traceback, unpickle_traceback

from . import util


_pid = None
""":type: int"""
_thread = None
""":type: threading.Thread"""
_tasks = None
""":type: dict[int, tuple[multiprocessing.Connection, multiprocessing.Connection, concurrent.futures.Future]]"""


def _worker():

    global _pid, _thread, _tasks

    while True:

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

                finally:

                    try:
                        os.waitpid(child_pid, 0)
                    except OSError:
                        pass

            if parent_ex.poll():

                try:

                    ex_type, ex_value, ex_traceback = parent_ex.recv()

                    ex_traceback = unpickle_traceback(*ex_traceback)

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

                finally:

                    try:
                        os.waitpid(child_pid, 0)
                    except OSError:
                        pass

        time.sleep(0.001)


def _future(child_pid, parent, parent_ex):
    """ :type parent: multiprocessing.Connection
        :type parent_ex: multiprocessing.Connection
        :rtype future: concurrent.futures.Future
    """

    global _pid, _thread, _tasks

    if _pid != os.getpid():

        _tasks = {}

        _pid = os.getpid()
        _thread = threading.Thread(target=_worker, name='inparallel-{}'.format(os.getpid()))
        _thread.setDaemon(True)
        _thread.start()

    future = concurrent.futures.Future()
    future.set_running_or_notify_cancel()

    _tasks[child_pid] = (future, parent, parent_ex)

    return future


@util.decorator
def task(fn):

    @six.wraps(fn)
    def wrapper(*args, **kwargs):

        global _pid, _thread, _tasks

        parent, child = multiprocessing.Pipe()
        parent_ex, child_ex = multiprocessing.Pipe()
        child_pid = os.fork()

        if child_pid == 0:

            try:

                child.send(fn(*args, **kwargs))

            except Exception:

                ex_type, ex_value, ex_traceback = sys.exc_info()
                _, ex_traceback = pickle_traceback(ex_traceback)

                child_ex.send((ex_type, ex_value, ex_traceback))

            finally:

                child.close()
                child_ex.close()

            if _thread:

                util.raiseExceptionInThread(_thread, SystemExit)
                _thread.join()

            os._exit(0)

        return _future(child_pid, parent, parent_ex)

    return wrapper
