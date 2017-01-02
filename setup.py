# -*- coding: UTF-8 -*-
#
# Copyright © 2016 Alex Forster. All rights reserved.
# This software is licensed under the 3-Clause ("New") BSD license.
# See the LICENSE file for details.
#

import sys

from setuptools import setup


requires = ''

if (4, 0) > sys.version_info >= (3, 4):

    requires = '''
        six<1.12.0
        tblib<1.4.0
    '''

elif (3, 0) > sys.version_info >= (2, 7):

    requires = '''
        six<1.12.0
        futures<3.1.0
        tblib<1.4.0
    '''

else:

    print('inparallel requires CPython v2.7+ or v3.4+')
    sys.exit(1)


setup(
    name='inparallel',
    version='1.0.2',
    author='Alex Forster',
    author_email='alex@alexforster.com',
    maintainer='Alex Forster',
    maintainer_email='alex@alexforster.com',
    url='https://github.com/AlexForster/inparallel',
    description='A novel take on process-based parallelism in Python (CPython 2.7 or 3.4+)',
    license='3-Clause ("New") BSD license',
    download_url='https://pypi.python.org/pypi/inparallel',
    packages=['inparallel'],
    package_dir={'inparallel': './inparallel'},
    package_data={'inparallel': [
        'README*',
        'LICENSE',
    ]},
    install_requires=[r for r in requires.splitlines() if r],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],
)
