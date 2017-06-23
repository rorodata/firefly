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
    name='Firefly',
    version=__version__,
    author='rorodata',
    author_email='rorodata.team@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        firefly=firefly.main:main
    ''',
)
