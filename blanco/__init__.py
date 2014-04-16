#! /usr/bin/python -tt
# coding=utf-8
"""blanco - Keep in touch, barely."""
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

from __future__ import print_function

from . import _version

__version__ = _version.dotted
__date__ = _version.date
__author__ = 'James Rowe <jnrowe@gmail.com>'
__copyright__ = 'Copyright (C) 2010-2014  James Rowe <jnrowe@gmail.com>'
__license__ = 'GNU General Public License Version 3'
__credits__ = ''
__history__ = 'See git repository'

from email.utils import parseaddr

__doc__ += """.

Check sent mail to make sure you're keeping in contact with your friends.

.. moduleauthor:: `%s <mailto:%s>`__
""" % parseaddr(__author__)

import argparse
import errno
import mailbox
import operator
import os
import re
import sys

from email.utils import (formataddr, getaddresses)

import arrow
import blessings
import configobj
import validate

try:
    import pynotify
except ImportError:  # pragma: no cover
    class _Fake_PyNotify(object):  # NOQA
        URGENCY_CRITICAL = 2
        URGENCY_NORMAL = 1
        URGENCY_LOW = 0
        EXPIRES_DEFAULT = -1
        EXPIRES_NEVER = 0
    pynotify = _Fake_PyNotify  # NOQA

from .i18n import _
from .compat import (PY2, basestring, mangle_repr_type, open)

T = blessings.Terminal()


# Set up informational message functions
COLOUR = True
def _colourise(text, colour):
    """Colour text, if possible.

    :param str text: Text to colourise
    :param str colour: Colour to display text in
    :rtype: `str`
    :return: Colourised text, if possible
    """
    if COLOUR:
        return getattr(T, colour.replace(' ', '_'))(text)
    else:
        return text


def success(text):
    return _colourise(text, 'bright green')


def fail(text):
    return _colourise(text, 'bright red')


def warn(text):
    return _colourise(text, 'bright yellow')


USAGE = _("Check sent mail to make sure you're keeping in contact with your "
          "friends.")


def parse_sent(path, all_recipients=False, addresses=None):
    """Parse sent messages mailbox for contact details.

    :param str path: Location of the sent mailbox
    :param bool all_recipients: Whether to include CC and BCC addresses in
        results, or just the first
    :param list addresses: Addresses to look for in sent mail, all if not
        specified
    :rtype: `dict` of `str` keys and `arrow.Arrow` values
    :return: Keys of email address, and values of seen date
    """
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        raise IOError(_('Sent mailbox %r not found') % path)
    if os.path.isdir('%s/new' % path):
        mtype = mailbox.Maildir
    elif os.path.exists('%s/.mh_sequences' % path):
        mtype = mailbox.MH
    elif os.path.isfile(path):
        mtype = mailbox.mbox
    else:
        raise ValueError(_('Unknown mailbox format for %r') % path)
    # Use factory=None to work around the rfc822.Message default for Maildir.
    if PY2:
        mbox = mtype(path.encode(), factory=None, create=False)
    else:
        mbox = mtype(path, factory=None, create=False)

    contacts = []
    for message in mbox:
        fields = message.get_all('to', [])
        if all_recipients:
            fields.extend(message.get_all('cc', []))
            fields.extend(message.get_all('bcc', []))
        results = [x[1].lower() for x in getaddresses(fields)]
        date = arrow.get(message['date'], 'ddd, DD MMM YYYY HH:mm:ss Z')
        contacts.extend([(address, date.date()) for address in results
                         if not addresses or address in addresses])
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def parse_msmtp(log, all_recipients=False, addresses=None, gmail=False):
    """Parse sent messages mailbox for contact details.

    :param str log: Location of the msmtp logfile
    :param bool all_recipients: Whether to include all recipients in results,
        or just the first
    :param list addresses: Addresses to look for in sent mail, all if not
        specified
    :param bool gmail: Log is for a gmail account
    :rtype: `dict` of `str` keys and `arrow.Arrow` values
    :return: Keys of email address, and values of seen date
    """
    if not os.path.exists(log):
        raise IOError(_('msmtp sent log %r not found') % log)

    matcher = re.compile('recipients=([^ ]+)')
    gmail_date = re.compile('smtpmsg.*OK ([^ ]+)')

    start = arrow.get(os.path.getmtime(log))

    year = start.year
    md = start.month, start.day
    contacts = []
    for line in reversed([line for line in open(log)
                          if line.endswith('exitcode=EX_OK\n')]):
        if gmail:
            gd = gmail_date.search(line)
            try:
                ts = int(gd.groups()[0])
                parsed = arrow.get(ts)
            except AttributeError:
                raise ValueError(_('msmtp %r log is not in gmail format')
                                 % log)
            year = parsed.year
            md = parsed.month, parsed.day
        else:
            parsed = arrow.get(line[:6], 'MMM DD')
            date = parsed.month, parsed.day
            if date > md:
                year = year - 1
            md = date

        recips = matcher.search(line, re.DOTALL)
        results = [s.lower() for s in recips.groups()[0].split(',')]
        if not all_recipients:
            results = [results[0], ]
        contacts.extend([(address, arrow.get(year, *md).date())
                         for address in results
                         if not addresses or address in addresses])
    # Sorting prior to making the dictionary means we only use the latest
    # entry.
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def parse_duration(duration):
    """Parse human readable duration.

    :param str duration: Duration definition
    :rtype: `int`
    :return: Number of days in ``duration``
    :raise ValueError: Invalid value for ``duration``
    """
    match = re.match('^(\d+(?:|\.\d+)) *([dwmy])$', duration, re.IGNORECASE)
    if not match:
        raise ValueError(_('Invalid duration value %r') % duration)
    value, units = match.groups()
    units = 'dwmy'.index(units.lower())
    # days per day/week/month/year
    multiplier = (1, 7, 28, 365)
    return int(float(value) * multiplier[units])


def process_command_line():
    """Main command line interface.

    :rtype: `argparse.Namespace`
    :return: Parsed options and arguments
    """
    # XDG basedir config location, using the glib bindings to get this would be
    # easier but the dependency is a bit too large for just that
    xdg_config_dir = os.environ.get('XDG_CONFIG_HOME',
                                    os.path.join(os.environ.get('HOME', '/'),
                                                 '.config'))
    config_file = os.path.join(xdg_config_dir, 'blanco', 'config.ini')
    config_spec = [
        'colour = boolean(default=True)',
        "addressbook = string(default='~/.abook/addressbook')",
        "sent type = string(default='mailbox')",
        'all = boolean(default=False)',
        "mbox = string(default='~/Mail/Sent')",
        "log = string(default='~/Mail/.logs/gmail.log')",
        'gmail = boolean(default=True)',
        "field = string(default='frequency')",
        'notify = boolean(default=False)',
        'verbose = boolean(default=False)',
    ]
    config = configobj.ConfigObj(config_file, configspec=config_spec)
    results = config.validate(validate.Validator())
    if results is not True:
        for key in results:
            if results[key]:
                continue
            print(fail(_('Config value for %r is invalid') % key))
        raise SyntaxError(_('Invalid configuration file %r') % config_file)

    if not config['colour'] or os.getenv('NO_COLOUR'):
        global COLOUR
        COLOUR = False

    parser = argparse.ArgumentParser(
        description=USAGE,
        epilog=_('Please report bugs to jnrowe@gmail.com'))
    parser.add_argument('--version', action='version',
                        version='%(prog)s v' + __version__)

    parser.set_defaults(addressbook=os.path.expanduser(config['addressbook']),
                        sent_type=config['sent type'],
                        all=config['all'],
                        mbox=os.path.expanduser(config['mbox']),
                        log=os.path.expanduser(config['log']),
                        gmail=config['gmail'],
                        field=config['field'],
                        notify=config['notify'],
                        verbose=config['verbose'])

    parser.add_argument('-a', '--addressbook', metavar=config['addressbook'],
                        help=_('address book to read contacts from'))

    parser.add_argument('-t', '--sent-type', choices=('mailbox', 'msmtp'),
                        metavar=config['sent type'],
                        help=_('sent source type(mailbox or msmtp)'))
    parser.add_argument('-r', '--all', action='store_true',
                        help=_('include all recipients(CC and BCC fields)'))
    parser.add_argument('--no-all', action='store_false', dest='all',
                        help=_('include only the first recipient(TO field)'))

    mbox_opts = parser.add_argument_group('Mailbox options')
    parser.add_argument_group(mbox_opts)
    mbox_opts.add_argument('-m', '--mbox', metavar=config['mbox'],
                           help=_('mailbox used to store sent mail'))

    msmtp_opts = parser.add_argument_group('msmtp log options')
    parser.add_argument_group(msmtp_opts)
    msmtp_opts.add_argument('-l', '--log', metavar=config['log'],
                            help=_('msmtp log to parse'))
    msmtp_opts.add_argument('-g', '--gmail', action='store_true',
                            help=_('log from a gmail account(use accurate '
                                   'filter)'))
    msmtp_opts.add_argument('--no-gmail', action='store_false', dest='gmail',
                            help=_('msmtp log for non-gmail account'))

    parser.add_argument('-s', '--field', metavar=config['field'],
                        help=_('addressbook field to use for frequency value'))
    parser.add_argument('-n', '--notify', action='store_true',
                        help=_('display reminders using notification popups'))
    parser.add_argument('--no-notify', action='store_false', dest='notify',
                        help=_('display reminders on standard out'))

    parser.add_argument('-v', '--verbose', action='store_true',
                        help=_('produce verbose output'))
    parser.add_argument('-q', '--quiet', action='store_false', dest='verbose',
                        help=_('output only matches and errors'))

    args = parser.parse_args()
    if args.notify and pynotify is _Fake_PyNotify:
        parser.exit(errno.ENOENT,
                    fail(_('Notification popups require the notify-python '
                           'package') + '\n'))

    return args


def show_note(notify, message, contact, urgency=pynotify.URGENCY_NORMAL,
              expires=pynotify.EXPIRES_DEFAULT):
    """Display reminder.

    :param bool notify: Whether to use notification popup
    :param str message: Message string to show
    :param Contact contact: Contact to show message for
    :param int urgency: Urgency state for message
    :param int expires: Time to show notification popup in milliseconds
    :raise OSError: Failure to show notification
    """
    if notify:
        note = pynotify.Notification(_('Hey, remember me?'),
                                     message % contact.notify_str(),
                                     'stock_person')
        note.set_urgency(urgency)
        note.set_timeout(expires)

        if not note.show():
            raise OSError(_('Notification failed to display!'))
    else:
        if urgency == pynotify.URGENCY_CRITICAL:
            print(success(message % contact.name))
        else:
            print(warn(message % contact.name))


@mangle_repr_type
class Contact(object):

    """Simple contact class."""

    def __init__(self, name, addresses, frequency):
        """Initialise a new `Contact` object."""
        self.name = name
        if isinstance(addresses, basestring):
            self.addresses = [addresses.lower(), ]
        else:
            self.addresses = [s.lower() for s in addresses]
        self.frequency = frequency

    def __repr__(self):
        """Self-documenting string representation."""
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.name,
                                   self.addresses, self.frequency)

    def __str__(self):
        """Pretty printed contact string."""
        return '%s <%s> (%i days)' % (self.name, ', '.join(self.addresses),
                                      self.frequency)

    def __format__(self, format_spec):
        """Extended pretty printing for `Contact` strings.

        :param str format_spec: Coordinate formatting system to use
        :rtype: `str`
        :return: Human readable string representation of `Contact` object
        :raise ValueError: Unknown value for ``format_spec``
        """
        if not format_spec:  # default format calls set format_spec to ''
            return str(self)
        elif format_spec == 'email':
            return formataddr((self.name, self.addresses[0]))
        else:
            raise ValueError(_('Unknown format_spec %r') % format_spec)

    def trigger(self, sent):
        """Calculate trigger date for contact.

        :type sent: `dict` of `str` keys and `arrow.Arrow` values
        :param sent: Address to last seen dictionary
        :rtype: `arrow.Arrow`
        :return: Date to start reminders on
        """
        match = sorted([v for k, v in sent.items() if k in self.addresses])[0]
        return arrow.get(*match.timetuple()[:3]).replace(days=self.frequency)

    def notify_str(self):
        """Calculate trigger date for contact.

        :rtype: `str`
        :return: Stylised name for use with notifications
        """
        if 'body-hyperlinks' in pynotify.get_server_caps():
            name = "<a href='mailto:%s'>%s</a>" \
                % (self.addresses[0], self.name)
        else:
            name = self.name
        return name


@mangle_repr_type
class Contacts(list):

    """Group of `Contact`."""

    def __init__(self, contacts=None):
        """Initialise a new `Contacts` object."""
        super(Contacts, self).__init__()
        if contacts:
            self.extend(contacts)

    def __repr__(self):
        """Self-documenting string representation."""
        return '%s(%r)' % (self.__class__.__name__,
                           sorted(self[:], key=operator.attrgetter('name')))

    def addresses(self):
        """Fetch all addresses of all `Contact` objects.

        :rtype: `list` of `str`
        :return: Addresses of every `Contact`
        """
        return [address for contact in self for address in contact.addresses]

    def parse(self, addressbook, field):
        """Parse address book for usable entries.

        :param str addressbook: Location of the address book to useful
        :param str field: Address book field to use for contact frequency
        """
        if not os.path.isfile(addressbook):
            raise IOError('Addressbook file not found %r' % addressbook)
        config = configobj.ConfigObj(os.path.expanduser(addressbook))

        for entry in config.values():
            if not field in entry:
                continue
            self.append(Contact(entry['name'], entry['email'],
                                parse_duration(entry[field])))


def main():
    """Main script."""
    args = process_command_line()

    if args.notify:
        if not pynotify.init(sys.argv[0]):
            print(fail(_('Unable to initialise pynotify!')))
            return errno.EIO

    contacts = Contacts()
    contacts.parse(args.addressbook, args.field)
    try:
        if args.sent_type == 'msmtp':
            sent = parse_msmtp(args.log, args.all, contacts.addresses(),
                               args.gmail)
        else:
            sent = parse_sent(args.mbox, args.all, contacts.addresses())
    except IOError as e:
        print(fail(e.args[0]))
        return errno.EPERM

    now = arrow.now()
    for contact in contacts:
        if not any(address in sent for address in contact.addresses):
            show_note(args.notify, _('No mail record for %s'), contact)
        elif now > contact.trigger(sent):
            show_note(args.notify, _('Mail due for %s'), contact,
                      pynotify.URGENCY_CRITICAL, pynotify.EXPIRES_NEVER)
