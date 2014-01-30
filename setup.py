#! /usr/bin/python -tt
# coding=utf-8
"""setup.py - Setuptools tasks and config for blanco"""
# Copyright © 2010-2014  James Rowe <jnrowe@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import imp

from setuptools import setup

# Hack to import _version file without importing blanco/__init__.py, its
# purpose is to allow import without requiring dependencies at this point.
ver_file = open('blanco/_version.py')
_version = imp.load_module('_version', ver_file, ver_file.name,
                           ('.py', ver_file.mode, imp.PY_SOURCE))

install_requires = [line.strip() for line in open('extra/requirements.txt')]

setup(
    name='blanco',
    version=_version.dotted,
    description='Keep in touch, barely',
    long_description=open('README.rst').read(),
    author='James Rowe',
    author_email='jnrowe@gmail.com',
    url='https://github.com/JNRowe/blanco',
    license='GPL-3',
    keywords='reminder mail contact',
    packages=['blanco', ],
    include_package_data=True,
    package_data={'': ['config', 'blanco/locale/*/LC_MESSAGES/*.mo']},
    entry_points={'console_scripts': ['blanco = blanco:main', ]},
    install_requires=install_requires,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Communications :: Email :: Filters',
        'Topic :: Desktop Environment',
        'Topic :: Utilities',
    ],
)
