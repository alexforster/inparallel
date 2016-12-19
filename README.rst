in\ *parallel*
==============

in\ *parallel* is a novel take on process-based parallelism in Python.

:Author:
    Alex Forster (alex@alexforster.com)
:License:
    BSD 3-Clause

Installation
------------

``pip install inparallel``

**Requirements**

-  ``six`` – Python 2 and 3 compatibility shims
-  ``tblib`` – pickling support for ``traceback`` objects
-  ``futures`` – backport of ``concurrent.futures`` *(Python 2 only)*

in\ *parallel* is compatible with both Python 2.7 and 3.4+

Documentation
-------------

There are only two objects exported by the in\ *parallel* library–

    **@task**

    A decorator used to annotate functions or class methods that you
    want to invoke asynchronously

    **waitfor(in_flight, concurrency_factor=None)**

    A generator used to manage the lifecycle of asynchronous invocations

    Arguments–

    -  **in_flight** : ``collections.MutableSequence`` of ``Future``
       objects
    -  **concurrency_factor** : ``int|None`` representing the
       desired maximum number of active asynchronous tasks

Example Code
------------

Here's an example that concurrently logs in to a list of servers and
gathers their ``uname`` outputs–

.. code:: python

    #!/usr/bin/env python

    from paramiko import SSHClient
    from inparallel import task, waitfor

    if __name__ == '__main__':

        servers = [
            'alpha.local',   'bravo.local',
            'charlie.local', 'delta.local',
            'echo.local',    'foxtrot.local',
            'golf.local',    'hotel.local',
            'india.local',   'juliet.local',
            'kilo.local',    'lima.local'
        ]

    # Notice how we decorate getOS() with the @task decorator. That's how
    # you annotate a function to make it run asynchronously.

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

    # The waitfor() function can also be used to manage the concurrency
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
    # run another task. You can run as many as you want, but you don't
    # have to keep track of how many are in flight, because waitfor()
    # will keep asking you for more tasks until it has reached its
    # target concurrency_factor high watermark.

    # When waitfor() has no more active futures, it will ask you to run
    # another task one last time. If you don't run another task, then
    # it will break the loop.
