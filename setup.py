from setuptools import setup, find_packages
import os.path

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

__version__ = get_version()

setup(
    name='firefly',
    version=__version__,
    author='rorodata',
    author_email='rorodata.team@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'WebOb==1.7.2',
        'gunicorn==19.7.1'
    ],
    entry_points='''
        [console_scripts]
        firefly=firefly.main:main
    ''',
)
