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
import threading
import ctypes

import six


def decorator(fn):

    @six.wraps(fn)
    def wrapper(*args, **kwargs):

        if len(args) == 1 and len(kwargs) == 0 and six.callable(args[0]):
            return fn(args[0])
        else:
            return lambda _: fn(_, *args, **kwargs)

    return wrapper


def raiseExceptionInThread(thread_obj, exception):
    """ :type thread_obj: threading.Thread
        :type exception: BaseException
        :rtype: bool
    """

    target_tid = thread_obj.ident

    if target_tid not in {thread.ident for thread in threading.enumerate()}:

        return False  # invalid thread object - cannot find thread identity among currently active threads

    affected_count = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), ctypes.py_object(exception))

    if affected_count == 0:

        return False  # invalid thread identity - no thread has been affected

    elif affected_count > 1:

        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid), ctypes.c_long(0))
        raise SystemError('Raising {} in thread {} ({}) failed; the runtime is now in an inconsistent state'.format(
            type(exception).__name__, thread_obj.name, thread_obj.ident
        ))

    return True
