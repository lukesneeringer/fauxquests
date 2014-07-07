#!/usr/bin/env python
from distutils.core import setup
from os.path import dirname, realpath
from os import sep
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
import sys


pip_requirements = realpath(dirname(__file__)) + sep + 'requirements.txt'


class Tox(TestCommand):
    """The test command should install and then run tox.

    Based on http://tox.readthedocs.org/en/latest/example/basic.html
    """
    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # Import here, because outside eggs aren't loaded.
        sys.exit(tox.cmdline(self.test_args))


setup(
    # Basic metadata
    name='fauxquests',
    version=open('VERSION').read().strip(),
    author='Luke Sneeringer',
    author_email='luke@sneeringer.com',
    url='https://github.com/lukesneeringer/fauxquests',

    # Additional information
    description=' '.join((
        'Mock HTTP requests sent with the requests package.',
        'For Python 2 or Python 3.',
    )),
    license='New BSD',

    # What does this require?
    install_requires=open(pip_requirements, 'r').read().strip().split('\n'),

    # How to do the install
    provides=[
        'fauxquests',
    ],
    packages=[i for i in find_packages() if i.startswith('fauxquests')],

    # How to do the tests
    tests_require=['tox'],
    cmdclass={'test': Tox },

    # Data files
    package_data={
        'fauxquests': ['VERSION'],
    },

    # PyPI metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
    ],
)
