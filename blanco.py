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

__version__ = "0.2.0"
__date__ = "2010-02-11"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2010 James Rowe <jnrowe@gmail.com>"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See git repository"

from email.utils import parseaddr

__doc__ += """.

Check sent mail to make sure you're keeping in contact with your friends.

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

import datetime
import mailbox
import operator
import optparse
import os
import re
import sys

from email import utils

import configobj

try:
    import termstyle
except ImportError:
    termstyle = None # pylint: disable-msg=C0103

# Select colours if terminal is a tty
if termstyle:
    # pylint: disable-msg=C0103
    termstyle.auto()
    success = termstyle.green
    fail = termstyle.red
    warn = termstyle.yellow
else:
    # pylint: disable-msg=C0103
    success = fail = warn = str

# Pull the first paragraph from the docstring
USAGE = __doc__[:__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("blanco", "%prog")


def parse_sent(path, cc=False, bcc=False, addresses=None):
    """Parse sent messages mailbox for contact details

    :type path: ``str``
    :param path: Location of the sent mailbox
    :type cc: ``bool``
    :param cc: Whether to check CC fields for contacts
    :type bcc: ``bool``
    :param bcc: Whether to check BCC fields for contacts
    :type addresses: ``list``
    :param addresses: Addresses to look for in sent mail, all if not specified
    :rtype: ``dict`` of ``str`` keys and ``datetime.datetime`` values
    :return: Keys of email address, and values of seen date
    """

    if not os.path.exists(path):
        raise IOError("File not found")
    if os.path.isdir("%s/new" % path):
        mtype = "Maildir"
    elif os.path.exists("%s/.mh_sequences"):
        mtype = "MHMailbox"
    elif os.path.isfile(path):
        mtype = "mbox"
    else:
        raise ValueError("Unknown mailbox format")
    # Use factory=None to work around the rfc822.Message default for Maildir.
    mbox = getattr(mailbox, mtype)(path, factory=None, create=False)

    contacts = []
    for message in mbox:
        fields = message.get_all("to", [])
        if cc:
            fields.extend(message.get_all("cc", []))
        if bcc:
            fields.extend(message.get_all("bcc", []))
        results = map(str.lower,
                      map(operator.itemgetter(1), utils.getaddresses(fields)))
        date = datetime.datetime(*utils.parsedate(message["date"])[:-2])
        contacts.extend([(address, date) for address in results
                         if not addresses or address in addresses])
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def parse_duration(duration):
    """Parse human readable duration

    >>> parse_duration("1d")
    1
    >>> parse_duration("1 d")
    1
    >>> parse_duration("0.5 y")
    182
    >>> parse_duration("0.5 Y")
    182
    >>> parse_duration("1 k")
    Traceback (most recent call last):
        ...
    ValueError: Invalid 'duration' value

    :type duration: ``str``
    :param duration: Duration definition
    :rtype: ``int``
    :return: Number of days in ``duration``
    :raise ValueError: Invalid value for ``duration``
    """

    match = re.match("^(\d+(?:|\.\d+)) *([dwmy])$", duration, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid 'duration' value")
    value, units = match.groups()
    units = "dwmy".index(units.lower())
    # days per day/week/month/year
    multiplier = (1, 7, 28, 365)
    return int(float(value) * multiplier[units])


def process_command_line():
    """Main command line interface

    :rtype: ``tuple`` of ``optparse`` and ``list``
    :return: Parsed options and arguments
    """
    parser = optparse.OptionParser(usage="%prog [options...]",
                                   version="%prog v" + __version__,
                                   description=USAGE)

    parser.set_defaults(addressbook=os.path.expanduser("~/.abook/addressbook"),
                        mbox=os.path.expanduser("~/.sup/sent.mbox"),
                        field="custom4")

    parser.add_option("-a", "--addressbook", action="store",
                      metavar="~/.abook/addressbook",
                      help="Address book to read contacts from")
    parser.add_option("-m", "--mbox", action="store",
                      metavar="~/.sup/sent.mbox",
                      help="Mailbox used to store sent mail")
    parser.add_option("-c", "--cc", action="store_true",
                      help="Include CC fields from sent mail")
    parser.add_option("-b", "--bcc", action="store_true",
                      help="Include BCC fields from sent mail")
    parser.add_option("-s", "--field", action="store",
                      metavar="custom4",
                      help="Abook field to use for frequency value")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", help="Produce verbose output")
    parser.add_option("-q", "--quiet", action="store_false",
                      dest="verbose",
                      help="Output only matches and errors")

    return parser.parse_args()


class Person(object):
    """Simple contact class"""

    def __init__(self, name, addresses, frequency):
        """Initialise a new ``Person`` object"""
        self.name = name
        if isinstance(addresses, basestring):
            self.addresses = [addresses.lower(), ]
        else:
            self.addresses = map(str.lower, addresses)
        self.frequency = frequency

    def __repr__(self):
        """Self-documenting string representation

        >>> Person("James Rowe", "jnrowe@gmail.com", 200)
        Person('James Rowe', ['jnrowe@gmail.com'], 200)
        """

        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.name,
                                   self.addresses, self.frequency)

    def __str__(self):
        """Pretty printed error string

        >>> print Person("James Rowe", "jnrowe@gmail.com", 200)
        James Rowe <jnrowe@gmail.com> (200 days)
        >>> print Person("James Rowe",
        ...              ["jnrowe@gmail.com", "jnrowe@example.com"], 200)
        James Rowe <jnrowe@gmail.com, jnrowe@example.com> (200 days)
        """
        return "%s <%s> (%i days)" % (self.name, ", ".join(self.addresses),
                                      self.frequency)

    def trigger(self, sent):
        """Calculate trigger date for contact

        >>> p = Person("James Rowe", "jnrowe@gmail.com", 200)
        >>> p.trigger({"jnrowe@gmail.com": datetime.datetime(1942, 1, 1)})
        datetime.datetime(1942, 7, 20, 0, 0)

        :type sent: ``dict`` of ``str`` keys and ``datetime.datetime`` values
        :param sent: Address to last seen dictionary
        :rtype: ``datetime.datetime``
        :return: Date to start reminders on
        """

        matches = sorted([v for k, v in sent.items() if k in self.addresses])
        return matches[-1] + datetime.timedelta(days=self.frequency)


class People(list):
    """Group of ``Person``"""

    def __init__(self, people=None):
        """Initialise a new ``People`` object"""
        super(People, self).__init__()
        if people:
            self.extend(people)

    def __repr__(self):
        """Self-documenting string representation

        >>> People([Person("James Rowe", "jnrowe@gmail.com", 200), ])
        People([Person('James Rowe', ['jnrowe@gmail.com'], 200)])
        """

        return "%s(%r)" % (self.__class__.__name__, self[:])

    def addresses(self):
        """Fetch all addresses of all ``Person`` objects

        >>> p = People(
        ... [Person("Bill", ["test@example.com", "new@example.com"], 30),
        ...  Person("Joe", ["joe@example.com"], 30)])
        >>> p.addresses()
        ['test@example.com', 'new@example.com', 'joe@example.com']

        :rtype: ``list`` of ``str``
        :return: Addresses of every ``Person``
        """
        return reduce(operator.add,
                      map(operator.attrgetter("addresses"), self))

    def parse(self, addressbook, field):
        """Parse address book for usable entries

        >>> people = People()
        >>> people.parse("test/blanco.conf", "custom4")
        >>> people
        People([Person('Bill', ['test@example.com'], 30),
            Person('Joe', ['joe@example.com'], 30),
            Person('Steven', ['steven@example.com'], 365)])

        :type addressbook: ``str``
        :param addressbook: Location of the address book to useful
        :type field: ``str``
        :param field: Address book field to use for contact frequency
        """

        config = configobj.ConfigObj(addressbook)
        reminder_entries = filter(lambda x: field in x, config.values())
        for entry in reminder_entries:
            self.append(Person(entry["name"], entry["email"],
                               parse_duration(entry[field])))


def main():
    """Main script"""

    options, args = process_command_line() # pylint: disable-msg=W0612

    people = People()
    people.parse(options.addressbook, options.field)
    sent = parse_sent(options.mbox, options.cc, options.bcc,
                      people.addresses())

    now = datetime.datetime.now()
    for person in people:
        if not any(address in sent for address in person.addresses):
            print fail("No record of a sent email for %s" % person.name)
            continue
        if now > person.trigger(sent):
            print "Due for", person.name

if __name__ == '__main__':
    sys.exit(main())
