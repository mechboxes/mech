# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

from mech import __version__


def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname), "r") as fp:
            return fp.read().strip()
    except IOError:
        return ''


setup(
    name="mech",
    version=__version__,
    author="Kevin Chung, Germán Méndez Bravo",
    author_email="kchung@nyu.edu, german.mb@gmail.com",
    url="https://mechboxes.github.io/mech/",
    download_url="https://github.com/mechboxes/mech/tarball/master",
    license="MIT",
    description="Tool for command line virtual machines",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords=['vagrant', 'vmware', 'vmrun', 'tool', 'virtualization'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Emulators",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    install_requires=['requests', 'clint', 'docopt', 'filelock'],
    packages=['mech'],
    entry_points={
        'console_scripts': [
            'mech = mech.__main__:main'
        ]
    },
)
