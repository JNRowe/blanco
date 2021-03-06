#! /usr/bin/python -tt
"""blanco - Keep in touch, barely.

Check sent mail to make sure you’re keeping in contact with your friends.
"""
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

from . import _version

__version__ = _version.dotted
__date__ = _version.date
__copyright__ = 'Copyright (C) 2010-2014  James Rowe <jnrowe@gmail.com>'

import configparser
import datetime
import errno
import mailbox
import operator
import pathlib
import sys
import time

from email.utils import (formataddr, getaddresses, parsedate)
from enum import Enum
from types import ModuleType
from typing import Dict, List, Optional, Union
try:
    from importlib import resources
except ImportError:  # pragma: no cover
    import importlib_resources as resources

import click
import parse

try:
    import notify2
except ImportError:

    class _Fake_Notify2(Enum):  # NOQA
        URGENCY_CRITICAL = 2
        URGENCY_NORMAL = 1
        URGENCY_LOW = 0
        EXPIRES_DEFAULT = -1
        EXPIRES_NEVER = 0

    notify2 = _Fake_Notify2  # NOQA

from jnrbase import (colourise, human_time, xdg_basedir)


def parse_sent(path: pathlib.Path,
               all_recipients: bool = False,
               addresses: List[str] = None) -> Dict[str, datetime.datetime]:
    """Parse sent messages mailbox for contact details.

    Args:
        path: Location of the sent mailbox
        all_recipients: Whether to include CC and BCC addresses in
            results, or just the first
        addresses: Addresses to look for in sent mail, all if not
            specified

    Returns:
        Keys of email address, and values of seen date
    """
    if not path.exists():
        raise IOError(f'Sent mailbox ‘{path}’ not found')
    if path.is_file():
        mtype = mailbox.mbox
    elif path.is_dir() and path.joinpath('new').exists():
        mtype = mailbox.Maildir
    elif path.is_dir() and path.joinpath('.mh_sequences').exists():
        mtype = mailbox.MH
    else:
        raise ValueError(f'Unknown mailbox format for ‘{path}’')
    # Use factory=None to work around the rfc822.Message default for Maildir.
    mbox = mtype(path.as_posix(), factory=None, create=False)

    contacts = []
    for message in mbox:
        fields = message.get_all('to', [])
        if all_recipients:
            fields.extend(message.get_all('cc', []))
            fields.extend(message.get_all('bcc', []))
        results = [x[1].lower() for x in getaddresses(fields)]
        date = datetime.datetime(*parsedate(message['date'])[:-2])
        contacts.extend([(address, date.date()) for address in results
                         if not addresses or address in addresses])
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def parse_msmtp(log: pathlib.Path,
                all_recipients: bool = False,
                addresses: List[str] = None,
                gmail: bool = False) -> Dict[str, datetime.datetime]:
    """Parse sent messages mailbox for contact details.

    Args:
        log: Location of the msmtp logfile
        all_recipients: Whether to include all recipients in results,
            or just the first
        addresses: Addresses to look for in sent mail, all if not
            specified
        gmail: Log is for a gmail account

    Returns:
        Keys of email address, and values of seen date
    """
    if not log.exists():
        raise IOError(f'msmtp sent log ‘{log}’ not found')

    matcher = parse.compile(' recipients={recip:S} ')
    gmail_date = parse.compile(' OK {timestamp:d} ')

    start = datetime.datetime.utcfromtimestamp(log.stat().st_mtime)

    year = start.year
    md = start.month, start.day
    contacts = []
    for line in (line for line in reversed(log.open().readlines())
                 if line.endswith('exitcode=EX_OK\n')):
        if gmail:
            gd = gmail_date.search(line)
            if gd:
                parsed = datetime.datetime.utcfromtimestamp(gd['timestamp'])
            else:
                raise ValueError(f'msmtp {log!r} log is not in gmail format')
            year = parsed.year
            md = parsed.month, parsed.day
        else:
            date = time.strptime(line[:6], '%b %d')[1:3]
            if date > md:
                year = year - 1
            md = date

        results = [s.lower() for s in matcher.search(line)['recip'].split(',')]
        if not all_recipients:
            results = [
                results[0],
            ]
        contacts.extend([(address, datetime.datetime(year, *md).date())
                         for address in results
                         if not addresses or address in addresses])
    # Sorting prior to making the dictionary means we only use the latest
    # entry.
    return dict(sorted(contacts, key=operator.itemgetter(1)))


def process_config() -> Dict[str, Union[bool, str]]:
    """Main configuration file.

    Returns:
        Parsed configuration file
    """
    conf_file = pathlib.Path(xdg_basedir.user_config('blanco')) / 'config.ini'
    bool_keys = ['all', 'colour', 'gmail', 'notify', 'verbose']
    config = configparser.ConfigParser()
    config.read_string(resources.read_text('blanco', 'config'), 'pkg config')
    config.read(conf_file.as_posix())
    parsed = {}
    for key, value in config['blanco'].items():
        if key in bool_keys:
            try:
                parsed[key] = config.getboolean('blanco', key)
            except ValueError:
                raise ValueError(f'Config value for {key!r} must be a bool')
        else:
            parsed[key] = config.get('blanco', key)
    return parsed


def show_note(notify: bool,
              message: str,
              contact: 'Contact',
              urgency: int = notify2.URGENCY_NORMAL,
              expires: int = notify2.EXPIRES_DEFAULT) -> None:
    """Display reminder.

    Args:
        notify: Whether to use notification popup
        message: Message string to show
        contact: Contact to show message for
        urgency: Urgency state for message
        expires: Time to show notification popup in milliseconds

    Raises
        OSError: Failure to show notification
    """
    if notify:
        if contact.image:
            image = contact.image
        else:
            image = 'stock_person'
        note = notify2.Notification('Hey, remember me?',
                                    message.format(contact.notify_str()),
                                    image)
        note.set_urgency(urgency)
        note.set_timeout(expires)

        if not note.show():
            raise OSError('Notification failed to display!')
    else:
        if urgency == notify2.URGENCY_CRITICAL:
            colourise.pfail(message.format(contact.name))
        else:
            colourise.pwarn(message.format(contact.name))


class Contact:
    """Simple contact class."""

    def __init__(self,
                 name: str,
                 addresses: Union[str, List[str]],
                 frequency: int,
                 image: Optional[str] = None):
        """Initialise a new `Contact` object."""
        self.name = name
        if isinstance(addresses, str):
            self.addresses = [
                addresses.lower(),
            ]
        else:
            self.addresses = [s.lower() for s in addresses]
        self.frequency = frequency
        self.image = image

    def __repr__(self) -> str:
        """Self-documenting string representation."""
        return '{}({!r}, {!r}, {!r}, {!r})'.format(self.__class__.__name__,
                                                   self.name, self.addresses,
                                                   self.frequency, self.image)

    def __str__(self) -> str:
        """Pretty printed contact string."""
        return '{} [{}] ({} days)'.format(self.name, ', '.join(self.addresses),
                                          self.frequency)

    def __format__(self, format_spec: str) -> str:
        """Extended pretty printing for `Contact` strings.

        Args:
            format_spec: Coordinate formatting system to use

        Returns:
            Human readable string representation of `Contact` object

        Raises:
            ValueError: Unknown value for ``format_spec``
        """
        if not format_spec:  # default format calls set format_spec to ''
            return str(self)
        elif format_spec == 'email':
            return formataddr((self.name, self.addresses[0]))
        else:
            raise ValueError(f'Unknown format_spec {format_spec!r}')

    def trigger(self, sent: Dict[str, datetime.datetime]) -> datetime.datetime:
        """Calculate trigger date for contact.

        Args:
            sent: Address to last seen dictionary

        Returns:
            Date to start reminders on
        """
        match = sorted([v for k, v in sent.items() if k in self.addresses])[0]
        return match + datetime.timedelta(days=self.frequency)

    def notify_str(self) -> str:
        """Calculate trigger date for contact.

        Returns:
            Stylised name for use with notifications
        """
        if 'body-hyperlinks' in notify2.get_server_caps():
            name = f"<a href='mailto:{self.addresses[0]}'>{self.name}</a>"
        else:
            name = self.name
        return name


class Contacts(list):
    """Group of `Contact`."""

    def __init__(self, contacts: Optional[Contact] = None):
        """Initialise a new `Contacts` object."""
        super(Contacts, self).__init__()
        if contacts:
            self.extend(contacts)

    def __repr__(self) -> str:
        """Self-documenting string representation."""
        return '{}({!r})'.format(
            self.__class__.__name__,
            sorted(self[:], key=operator.attrgetter('name')))

    def addresses(self) -> List[str]:
        """Fetch all addresses of all `Contact` objects.

        Returns:
            Addresses of every `Contact`
        """
        return [address for contact in self for address in contact.addresses]

    def parse(self, addressbook: pathlib.Path, field: str) -> None:
        """Parse address book for usable entries.

        Args:
            addressbook: Location of the address book to useful
            field: Address book field to use for contact frequency
        """
        if not addressbook.is_file():
            raise IOError(f'Addressbook file not found {addressbook!r}')
        config = configparser.ConfigParser()
        config.read(addressbook.as_posix())

        for entry in config.values():
            if field not in entry:
                continue
            self.append(
                Contact(entry.get('name'), entry.get('email'),
                        human_time.parse_timedelta(entry.get(field)).days,
                        entry.get('image')))


CONFIG_DATA: Dict[str, Union[bool, str]] = process_config()


@click.command(help='Check sent mail to make sure you’re keeping in contact '
               'with your friends.',
               epilog='Please report bugs to jnrowe@gmail.com')
@click.option('-a',
              '--addressbook',
              type=pathlib.Path,
              metavar='FILENAME',
              default=CONFIG_DATA['addressbook'],
              help='Address book to read contacts from.')
@click.option('-t',
              '--sent-type',
              type=click.Choice(['mailbox', 'msmtp']),
              default=CONFIG_DATA['sent type'],
              help='Sent source type.')
@click.option('-r',
              '--all/--no-all',
              default=CONFIG_DATA['all'],
              help='Include all recipients(CC and BCC fields).')
@click.option('-m',
              '--mbox',
              type=pathlib.Path,
              metavar='FILENAME',
              default=CONFIG_DATA['mbox'],
              help='Mailbox used to store sent mail.')
@click.option('-l',
              '--log',
              type=pathlib.Path,
              metavar='FILENAME',
              default=CONFIG_DATA['log'],
              help='msmtp log to parse.')
@click.option('-g',
              '--gmail/--no-gmail',
              default=CONFIG_DATA['gmail'],
              help='Log from a gmail account(use accurate filter).')
@click.option('-s',
              '--field',
              default=CONFIG_DATA['field'],
              help='Addressbook field to use for frequency value.')
@click.option('-n',
              '--notify/--no-notify',
              default=CONFIG_DATA['notify'],
              help='Display reminders using notification popups.')
@click.option('--colour/--no-colour',
              envvar='BLANCO_COLOUR',
              default=CONFIG_DATA['colour'],
              help='Output colourised informational text.')
@click.option('-v', '--verbose/--no-verbose', help='Produce verbose output.')
@click.version_option(_version.dotted)
def main(addressbook: pathlib.Path, sent_type: str, all: bool,
         mbox: pathlib.Path, log: pathlib.Path, gmail: bool, field: str,
         notify: bool, colour: bool,
         verbose: bool) -> Optional[int]:  # pragma: no cover
    """Main script."""
    colourise.COLOUR = colour

    if notify and type(notify2) != ModuleType:
        raise click.UsageError(
            colourise.fail(
                'Notification popups require the notify2 package\n'))

    if notify:
        if not notify2.init(sys.argv[0]):
            colourise.pfail('Unable to initialise notify2!')
            return errno.EIO

    contacts = Contacts()
    contacts.parse(addressbook.expanduser(), field)
    try:
        if sent_type == 'msmtp':
            sent = parse_msmtp(log.expanduser(), all, contacts.addresses(),
                               gmail)
        else:
            sent = parse_sent(mbox.expanduser(), all, contacts.addresses())
    except IOError as e:
        colourise.pfail(e.args[0])
        return errno.EPERM

    now = datetime.datetime.utcnow().date()
    for contact in contacts:
        if not any(address in sent for address in contact.addresses):
            show_note(notify, 'No mail record for {}', contact)
        elif now > contact.trigger(sent):
            show_note(notify, 'Mail due for {}', contact,
                      notify2.URGENCY_CRITICAL, notify2.EXPIRES_NEVER)
