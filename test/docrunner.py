#! /usr/bin/python -tt
#
"""docrunner - Execute shell tests"""
# Copyright (C) 2010-2012  James Rowe <jnrowe@gmail.com>
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

__version__ = "0.1.0"
__date__ = "2010-02-12"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2010-2012  James Rowe <jnrowe@gmail.com>"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See git repository"

try:
    from email.utils import parseaddr
except ImportError:  # Python 2.4
    from email.Utils import parseaddr

__doc__ += """.

Run shell examples in reST literal blocks.

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

import doctest
import os
import sys

import shelldoctest as sd

if __name__ == "__main__":
    os.chdir(os.path.abspath(__file__).rsplit(os.sep, 2)[0])

    sys.exit(doctest.testfile("README.rst", module_relative=False,
                              extraglobs={"system_command": sd.system_command},
                              parser=sd.ShellDocTestParser())[0])
