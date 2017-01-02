in\ *parallel*
==============

in\ *parallel* is a novel take on process-based parallelism in Python using ``fork()`` to implement futures-based
concurrency.

:Author:
    Alex Forster (alex@alexforster.com)
:License:
    BSD 3-Clause

Installation
------------

``pip install inparallel``

| **GitHub:** https://github.com/alexforster/inparallel/tree/v1.0.2
| **PyPI:** https://pypi.python.org/pypi/inparallel/1.0.2

**Dependencies**

-  ``six`` – Python 2 and 3 compatibility shims
-  ``tblib`` – pickling support for ``traceback`` objects
-  ``futures`` – backport of ``concurrent.futures`` *(Python 2 only)*

in\ *parallel* is compatible with both Python 2.7 and 3.4+

Documentation
-------------

There are just two objects exported by the in\ *parallel* library–

    **@task**

    A decorator used to annotate functions or class methods that you
    want to invoke asynchronously

    **waitfor(in_flight, concurrency_factor=None) -> Future**

    A generator used to manage the lifecycle of asynchronous invocations

    Arguments–

    -  **in_flight** : ``collections.MutableSequence`` (read: ``list``)
       of ``Future`` objects
    -  **concurrency_factor** : ``int|None`` representing the
       desired maximum number of active asynchronous tasks

Check out the guided examples below to learn how this library is unique.

Examples
--------

Here's an example that demonstrates how to run a function in the background
and use the ``concurrent.futures.Future`` object to wait for its result–

.. code:: python

    #!/usr/bin/env python

    import time
    from inparallel import task, waitfor

    if __name__ == '__main__':

    # Notice how we decorate say_hello() with the @task decorator.
    # That's how you make a function run asynchronously when it's called.

        @task
        def say_hello(to):

            time.sleep(3)
            return 'Hello, {}!'.format(to)

        hello_future = say_hello('Emily')  # returns a concurrent.futures.Future object

        hello_future.wait()  # waits for three seconds

        print(hello_future.result())  # prints "Hello, Emily!"

Here's an example that concurrently logs in to a list of servers and
gathers their ``uname`` outputs–

.. code:: python

    #!/usr/bin/env python

    from paramiko import SSHClient
    from inparallel import task, waitfor

    if __name__ == '__main__':

        servers = [
            'alpha.local', 'bravo.local',
            'charlie.local', 'delta.local',
            'echo.local', 'foxtrot.local',
            'golf.local', 'hotel.local',
            'india.local', 'juliet.local',
            'kilo.local', 'lima.local'
        ]

        @task
        def getOS(server):

            with SSHClient() as ssh:

                ssh.connect(server, username='root', password='root')

                sin, sout, serr = ssh.exec_command('uname -a')

                return sout.read()

        active_futures = []

        while len(servers) > 0:

            active_futures.append(getOS(servers.pop(0))

    # The Python interpreter was actually just fork()'ed during each of
    # those getOS() calls, and the real function began running in a new
    # subprocess.

    # At the same time, our parent process spawned a thread to supervise
    # these new subprocesses, and then handed us back Future objects,
    # representing the "future results" of each getOS() function call.

    # When getOS() finishes running in its subprocess, its return value
    # (or Exception) will be marshaled back to us in the parent process,
    # and the fork()'ed subprocess will die. Our supervisor thread will
    # receive the marshaled result, and mark its Future as completed.

        for future in waitfor(active_futures):

            print(future.result())

    # Because managing a bunch of Future objects is a pain, this library
    # also provides a simple but powerful waitfor() function which is a
    # generator that takes a (mutable!) list of Futures and busy-waits
    # on them, immediatley yielding Futures that complete.

    # The MutableSequence (read: list) that you pass to waitfor() will
    # be modified in-place by the waitfor() function. Specifically, as
    # futures complete, they will be removed from the list and yielded
    # back to the caller.

    # The waitfor() function can also be used to manage the concurrency
    # factor of your tasks, as demonstrated below.

Here's the same example from above, modified to use the
``concurrency_factor`` argument of ``waitfor()`` to ensure that only 3
asynchronous tasks run at a time–

.. code:: python

    #!/usr/bin/env python

    from paramiko import SSHClient
    from inparallel import task, waitfor

    if __name__ == '__main__':

        servers = [
            'alpha.local', 'bravo.local',
            'charlie.local', 'delta.local',
            'echo.local', 'foxtrot.local',
            'golf.local', 'hotel.local',
            'india.local', 'juliet.local',
            'kilo.local', 'lima.local'
        ]

        @task
        def getOS(server):

            with SSHClient() as ssh:

                ssh.connect(server, username='root', password='root')

                sin, sout, serr = ssh.exec_command('uname -a')

                return sout.read()

    # When you pass the concurrency_factor argument to waitfor(), its
    # behavior changes slightly.

        active_futures = []

        for future in waitfor(active_futures, concurrency_factor=3):

    # As in the first example, waitfor() will still yield each future
    # as it completes, but now it may also yield None. In fact, at
    # this point in the example, there aren't any active futures yet!

            if future is not None:

                # waitfor() yielded a completed future

                print(future.result())

            else:

                # waitfor() wants you to run more tasks

                if len(servers) > 0:  # do we have any more?

                    active_futures.append(getOS(servers.pop(0)))

    # Here's the trick: when waitfor() yields None, it's asking you to
    # run another task. waitfor() will keep asking you for more tasks
    # until it has reached its target concurrency_factor high watermark,
    # so you should only run one additional task for each iteration
    # where you receive a None. This is how waitfor() is able to ensure
    # that only a certain number of tasks are running at one time.

    # When waitfor() has no more active futures, it will ask you to run
    # another task one last time. If you don't run another task, then
    # it will break the loop.

Notes
-----

-  This library is only compatible with CPython, and only on platforms
   that support POSIX ``fork()`` semantics. This is unavoidable due to the
   nature of the library.
-  When a function is decorated with ``@task``, the only data that will
   survive is what the function returns. Any modifications to global
   objects will not persist past the function call.
-  The data that you return from a ``@task`` must be picklable, since
   multiple processes are involved. If this presents a challenge, check out
   the ``dill`` library.
-  You can invoke ``@task`` functions from inside of other ``@task`` functions,
   but be mindful that each invocation spawns a subprocess of the calling
   process, so deep recursion is unwise. On the other hand, this allows you to
   build complex asynchronous task hierarchies if desired.
-  Class methods (those with ``self`` parameters) can be decorated with
   ``@task`` and used normally, without the need for partial bindings.
-  Exceptions will bubble from the child interpreter to the parent with
   accurate tracebacks, thanks to the ``tblib`` library.
