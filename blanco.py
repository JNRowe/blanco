#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""blanco - Keep in touch, barely"""
# Copyright (C) 2010  James Rowe <jnrowe@gmail.com>
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
__date__ = "2010-02-10"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2010 James Rowe <jnrowe@gmail.com>"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See git repository"

from email.utils import parseaddr

__doc__ += """.

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

import datetime
import mailbox
import operator
import os
import re
import sys

from email import utils

import configobj

def parse_sent(path=os.path.expanduser("~/.sup/sent.mbox"), mtype="mbox"):
    """Parse sent messages mailbox for contact details"""
    mbox = getattr(mailbox, mtype)(path, create=False)
    contacts = []
    for message in mbox:
        addresses = map(operator.itemgetter(1),
                        utils.getaddresses(message.get_all("to")))
        date = datetime.datetime(*utils.parsedate(message["date"])[:-2])
        contacts.extend([(address, date) for address in addresses])
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def parse_timedelta(delta):
    """Parse human readable frequency

    >>> parse_timedelta("1d")
    1
    >>> parse_timedelta("1 d")
    1
    >>> parse_timedelta("0.5 y")
    182
    >>> parse_timedelta("0.5 Y")
    182
    >>> parse_timedelta("1 k")
    Traceback (most recent call last):
        ...
    ValueError: Invalid 'frequency' value
    """
    match = re.match("^(\d+(?:|\.\d+)) *([dwmy])$", delta, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid 'frequency' value")
    value, units = match.groups()
    units = "dwmy".index(units.lower())
    # days per day/week/month/year
    multiplier = (1, 7, 28, 365)
    return int(float(value) * multiplier[units])


class Person(object):
    """Simple contact class"""

    def __init__(self, name, address, frequency):
        """Initialise a new ``Person`` object"""
        self.name = name
        self.address = address
        self.frequency = frequency

    def __repr__(self):
        """
        >>> Person("James Rowe", "jnrowe@gmail.com", 200)
        Person('James Rowe', 'jnrowe@gmail.com', 200)
        """

        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.name,
                                   self.address, self.frequency)

    def __str__(self):
        """
        >>> print Person("James Rowe", "jnrowe@gmail.com", 200)
        James Rowe <jnrowe@gmail.com> (200 days)
        """
        return "%(name)s <%(address)s> (%(frequency)s days)" % self.__dict__

    def trigger(self, sent):
        """
        >>> p = Person("James Rowe", "jnrowe@gmail.com", 200)
        >>> p.trigger(datetime.datetime(1942, 1, 1))
        datetime.datetime(1942, 7, 20, 0, 0)
        """
        return sent + datetime.timedelta(days=self.frequency)


class People(list):
    """Group of ``Person``"""

    def __init__(self, people=None):
        """Initialise a new ``People`` object"""
        super(People, self).__init__()
        if people:
            self.extend(people)

    def __repr__(self):
        """
        >>> People([Person("James Rowe", "jnrowe@gmail.com", 200), ])
        People([Person('James Rowe', 'jnrowe@gmail.com', 200)])
        """

        return "%s(%r)" % (self.__class__.__name__, self[:])

    def parse(self, file):
        """
        >>> people = People()
        >>> people.parse("test/blanco.conf")
        >>> people
        People([Person('Bill', 'test@example.com', 30),
            Person('Joe', 'joe@emample.com', 30),
            Person('Steven', 'no@example.com', 365)])
        """
        config = configobj.ConfigObj(file)
        reminder_entries = filter(lambda x: "custom4" in x, config.values())
        for entry in reminder_entries:
            self.append(Person(entry["name"], entry["email"],
                               parse_timedelta(entry["custom4"])))


def main(argv):
    """Main script"""
    people = People()
    people.parse(argv[1])
    sent = parse_sent(argv[2])
    now = datetime.datetime.now()
    for person in people:
        if not person.address in sent:
            print "No record of a sent email for", person.name
            continue
        if now > person.trigger(sent[person.address]):
            print "Due for", person.name

if __name__ == '__main__':
    main(sys.argv)
