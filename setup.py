# -*- coding: utf-8 -*-

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="nginxctl",
    version="1.0",
    author="Rackspace",
    author_email="luke.shirnia@rackspace.co.uk",
    description=("A utility to report on nginx server blocks"),
#    license="LGPLv2",
    keywords="linux nginx",
    url="https://github.com/LukeShirnia/nginxctl",
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python",
    ],
    py_modules = ['nginxctl'],
    entry_points={'console_scripts':['nginxctl = nginxctl:main']}
)
