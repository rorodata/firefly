"""
Firefly
-------

Firefly is a tool to expose Python functions as RESTful APIs.

Install
~~~~~~~

It can be installed using pip.

..code:: bash

    $ pip install firefly-python

Usage
~~~~~

Write a python function:

..code:: python

    # sq.py
    def square(n):
        return n*n

And run it with firefly:

..code:: bash

    $ firefly sq.square
    [2017-06-08 12:45:11 +0530] [20237] [INFO] Starting gunicorn 19.7.1
    [2017-06-08 12:45:11 +0530] [20237] [INFO] Listening at: http://127.0.0.1:8000 (20237)
    ...

Firefly provides a simple client interface to interact with the server.

..code:: python

    >>> from firefly.client import Client
    >>> client = Client("http://127.0.0.1:8000")
    >>> client.square(n=4)
    16

Or, you can use the API directly:

..code:: bash

  $ curl -d '{"n": 4}' http://127.0.0.1:8000/square
  16

Links
~~~~~

* `Documentation <https://firefly-python.readthedocs.io/>`_
* `Github <https://github.com/rorodata/firefly>`_
"""

from setuptools import setup, find_packages
import os.path
import sys

PY2 = (sys.version_info.major == 2)

def get_version():
    """Returns the package version taken from version.py.
    """
    root = os.path.dirname(__file__)
    version_path = os.path.join(root, "firefly/version.py")
    with open(version_path) as f:
        code = f.read()
        env = {}
        exec(code, env, env)
        return env['__version__']

install_requires = [
    'gunicorn==19.7.1',
    'WebOb==1.7.2',
    'requests==2.18.1',
    'PyYAML==3.12'
]

if PY2:
    install_requires.append('funcsigs==1.0.2')

__version__ = get_version()

setup(
    name='firefly-python',
    version=__version__,
    author='rorodata',
    author_email='rorodata.team@gmail.com',
    description='deploying functions made easy',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        firefly=firefly.main:main
    ''',
)
