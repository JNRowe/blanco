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

__version__ = "0.3.0"
__date__ = "2010-02-19"
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
import time

from email import utils

import configobj
import validate

try:
    import pynotify
except ImportError:
    pynotify = None  # pylint: disable-msg=C0103

try:
    import termstyle
except ImportError:
    termstyle = None  # pylint: disable-msg=C0103

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
    :rtype: ``dict`` of ``str`` keys and ``datetime.date`` values
    :return: Keys of email address, and values of seen date
    """

    if not os.path.exists(path):
        raise IOError("Sent mailbox `%s' not found" % path)
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
        contacts.extend([(address, date.date()) for address in results
                         if not addresses or address in addresses])
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def parse_msmtp(log, all_recipients=False, gmail=False, addresses=None):
    """Parse sent messages mailbox for contact details

    :type log: ``str``
    :param log: Location of the msmtp logfile
    :type all_recipients: ``bool``
    :param all_recipients: Whether to include all recipients in results, or
        just first
    :type gmail: ``bool``
    :param gmail: Log is for a gmail account
    :type addresses: ``list``
    :param addresses: Addresses to look for in sent mail, all if not specified
    :rtype: ``dict`` of ``str`` keys and ``datetime.datetime`` values
    :return: Keys of email address, and values of seen date
    """

    if not os.path.exists(log):
        raise IOError("msmtp sent log `%s' not found" % log)

    matcher = re.compile("recipients=([^ ]+)")
    gmail_date = re.compile("smtpmsg.*OK ([^ ]+)")

    start = datetime.datetime.utcfromtimestamp(os.path.getmtime(log))

    year = start.year
    md = start.month, start.day
    contacts = []
    for line in reversed(filter(lambda s: s.endswith("exitcode=EX_OK\n"),
                                open(log).readlines())):
        if gmail:
            gd = gmail_date.search(line)
            try:
                ts = int(gd.groups()[0])
                parsed = datetime.datetime.utcfromtimestamp(ts)
            except AttributeError:
                raise ValueError("msmtp log is not in gmail format")
            year = parsed.year
            md = parsed.month, parsed.day
        else:
            date = time.strptime(line[:6], "%b %d")[1:3]
            if date > md:
                year = year - 1
            md = date

        results = map(str.lower,
                      matcher.search(line, 16).groups()[0].split(","))
        if not all_recipients:
            results = [results[0], ]
        contacts.extend([(address, datetime.datetime(year, *md).date())
                         for address in results
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

    config_spec = [
        "addressbook = string(default='~/.abook/addressbook')",
        "field = string(default='custom4')",
        "mbox = string(default='~/.sup/sent.mbox')",
        "cc = boolean(default=False)",
        "bcc = boolean(default=False)",
        "log = string(default='~/Mail/.logs/gmail.log')",
        "all = boolean(default=False)",
        "gmail = boolean(default=False)",
        "senttype = string(default='mailbox')",
    ]
    config = configobj.ConfigObj(os.path.expanduser("~/.blancorc"),
                                 configspec=config_spec)
    results = config.validate(validate.Validator())
    if results is not True:
        for key in filter(lambda k: not results[k], results):
            print fail("Config value for `%s' is invalid" % key)
        raise SyntaxError("Invalid configuration file")

    parser = optparse.OptionParser(usage="%prog [options...]",
                                   version="%prog v" + __version__,
                                   description=USAGE)

    parser.set_defaults(addressbook=os.path.expanduser(config["addressbook"]),
                        sent_type=config['senttype'],
                        mbox=os.path.expanduser(config["mbox"]),
                        cc=config["cc"], bcc=config["bcc"],
                        field=config["field"])

    parser.add_option("-a", "--addressbook", action="store",
                      metavar=config["addressbook"],
                      help="Address book to read contacts from")

    parser.add_option("-t", "--sent-type", action="store",
                      choices=("mailbox", "msmtp"),
                      metavar=config["senttype"],
                      help="Sent source type(mailbox or msmtp)")

    mbox_opts = optparse.OptionGroup(parser, "Mailbox options")
    parser.add_option_group(mbox_opts)
    mbox_opts.add_option("-m", "--mbox", action="store",
                      metavar=config["mbox"],
                      help="Mailbox used to store sent mail")
    mbox_opts.add_option("-c", "--cc", action="store_true",
                      help="Include CC fields from sent mail")
    mbox_opts.add_option("-b", "--bcc", action="store_true",
                      help="Include BCC fields from sent mail")

    msmtp_opts = optparse.OptionGroup(parser, "msmtp log options")
    parser.add_option_group(msmtp_opts)
    msmtp_opts.add_option("-l", "--log", action="store",
                          metavar=config["log"],
                          help="msmtp log to parse")
    msmtp_opts.add_option("-r", "--all", action="store_true",
                          help="Include all recipients from msmtp log")
    msmtp_opts.add_option("-g", "--gmail", action="store_true",
                          help="Log from a gmail account(use accurate filter)")

    parser.add_option("-s", "--field", action="store",
                      metavar=config["field"],
                      help="Abook field to use for frequency value")
    parser.add_option("-n", "--notify", action="store_true",
                      help="Display reminders using notification popups")
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
        >>> p.trigger({"jnrowe@gmail.com": datetime.date(1942, 1, 1)})
        datetime.date(1942, 7, 20)

        :type sent: ``dict`` of ``str`` keys and ``datetime.date`` values
        :param sent: Address to last seen dictionary
        :rtype: ``datetime.date``
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

    try:
        options, args = process_command_line()  # pylint: disable-msg=W0612
    except SyntaxError:
        return 1

    if options.notify:
        if not pynotify:
            print fail("Notification popups require the notify-python package")
            return 127
        if not pynotify.init(sys.argv[0]):
            print fail("Unable to initialise pynotify!")
            return 255

    people = People()
    people.parse(options.addressbook, options.field)
    if options.sent_type == "msmtp":
        sent = parse_msmtp(options.log, options.all, options.gmail,
                           people.addresses())
    else:
        sent = parse_sent(options.mbox, options.cc, options.bcc,
                          people.addresses())

    now = datetime.date.today()
    for person in people:
        if not any(address in sent for address in person.addresses):
            if options.notify:
                note = pynotify.Notification("Hey, remember me?",
                                             "No mail record for %s" \
                                                % person.name,
                                             "stock_person")
                if not note.show():
                    raise OSError("Notification failed to display!")
            else:
                print warn("No record of a sent email for %s" % person.name)
            continue
        if now > person.trigger(sent):
            if options.notify:
                note = pynotify.Notification("Hey, remember me?",
                                             "Mail due for %s" % person.name,
                                             "stock_person")
                note.set_urgency(pynotify.URGENCY_CRITICAL)
                note.set_timeout(pynotify.EXPIRES_NEVER)
                if not note.show():
                    raise OSError("Notification failed to display!")
            else:
                print "Due for", person.name

if __name__ == '__main__':
    sys.exit(main())
