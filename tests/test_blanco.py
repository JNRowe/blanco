#
# coding=utf-8
"""test_blanco - Test blanco functionality"""
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


from datetime import date
from unittest import TestCase

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA

from expecter import expect
from hiro import Timeline
from mock import patch
from nose2.tools import params

from blanco import (Contact, Contacts, PY2, parse_duration, parse_msmtp,
                    parse_sent, show_note)


def test_missing_mailbox():
    with expect.raises(IOError, "Sent mailbox 'None' not found"):
        parse_sent('None')


def test_unknown_mailbox_format():
    with expect.raises(ValueError, "Unknown mailbox format for '/dev/null'"):
        parse_sent('/dev/null')


@params(
    ('tests/data/sent.maildir', True, None, {
        'nobody@example.com': date(2000, 2, 9),
        'max@example.com': date(2000, 2, 9),
        'test@example.com': date(2010, 2, 9),
        'steven@example.com': date(2000, 2, 9),
        'joe@example.com': date(2000, 2, 9),
    }),
    ('tests/data/sent.mh', False, None, {
        'nobody@example.com': date(2000, 2, 9),
        'max@example.com': date(2000, 2, 9),
        'test@example.com': date(2010, 2, 9),
        'joe@example.com': date(2000, 2, 9),
    }),
    ('tests/data/sent.mbox', False, 'joe@example.com', {
        'joe@example.com': date(2000, 2, 9),
    }),
)
def test_parse_sent(mbox, recipients, addresses, result):
    expect(parse_sent(mbox, recipients, addresses)) == result


def test_missing_msmtp_log():
    with expect.raises(IOError, "msmtp sent log 'None' not found"):
        parse_msmtp('None')


@params(
    ('tests/data/sent.msmtp', False, None, False, {
        'nobody@example.com': date(2013, 2, 9),
        'test@example.com': date(2013, 2, 9),
        'joe@example.com': date(2013, 2, 9),
    }),
    ('tests/data/sent.msmtp', True, None, False, {
        'nobody@example.com': date(2013, 2, 9),
        'max@example.com': date(2013, 2, 9),
        'test@example.com': date(2013, 2, 9),
        'steven@example.com': date(2013, 2, 9),
        'joe@example.com': date(2013, 2, 9),
    }),
    ('tests/data/sent.msmtp', False, ['nobody@example.com', ], False, {
        'nobody@example.com': date(2013, 2, 9),
    }),
    ('tests/data/sent_gmail.msmtp', False, None, True, {
        'nobody@example.com': date(2000, 2, 9),
        'test@example.com': date(2010, 2, 9),
        'joe@example.com': date(2000, 2, 9),
    }),
)
def test_parse_msmtp(log, all_recipients, addresses, gmail, result):
    with Timeline().freeze(date(2014, 6, 27)):
        expect(parse_msmtp(log, all_recipients, addresses, gmail)) == result


def test_invalid_duration():
    with expect.raises(ValueError, "Invalid duration value '1 k'"):
        parse_duration('1 k')


@params(
    ('1d', 1),
    ('1 d', 1),
    ('0.5 y', 182),
    ('0.5 Y', 182),
)
def test_parse_duration(duration, result):
    expect(parse_duration(duration)) == result


@patch('sys.stdout', new_callable=StringIO)
def test_show_note(stdout):
    show_note(False, 'Note for %s',
              Contact('James Rowe', 'jnrowe@gmail.com', 200))
    # Use contains to avoid having to mess around with {,no-}colour options
    expect(stdout.getvalue()).contains('Note for James Rowe')


class ContactTest:
    def setUp(self):  # NOQA
        self.contact = Contact('James Rowe', 'jnrowe@gmail.com', 200)

    def test___repr__(self):
        expect(repr(self.contact)) == \
            "Contact('James Rowe', ['jnrowe@gmail.com'], 200)"

    def test___str__(self):
        expect(str(self.contact)) == \
            'James Rowe <jnrowe@gmail.com> (200 days)'
        expect(str(Contact(
            'James Rowe', ['jnrowe@gmail.com', 'jnrowe@example.com'],
            200))) == \
            'James Rowe <jnrowe@gmail.com, jnrowe@example.com> (200 days)'

    def test___format__(self):
        expect(format(self.contact)) == \
            'James Rowe <jnrowe@gmail.com> (200 days)'
        expect(format(self.contact, 'email')) == \
            'James Rowe <jnrowe@gmail.com>'
        expect(format(Contact, 'email'(
            'James Rowe', ['jnrowe@gmail.com', 'jnrowe@example.com'],
            200))) == \
            'James Rowe <jnrowe@gmail.com>'

    def trigger(self, sent):
        expect(self.contact.trigger({
            'jnrowe@gmail.com': date(1942, 1, 1)}
        )) == date(1942, 7, 20)

    @patch('blanco.pynotify')
    def notify_str(self, pynotify):
        pynotify.get_server_caps.return_value = []
        expect(self.contact.notify_str()) == 'James Rowe'
        pynotify.get_server_caps.return_value = ['body-hyperlinks', ]
        expect(self.contact.notify_str()) == \
            "<a href='mailto:jnrowe@gmail.com'>James Rowe</a>"


class ContactsTest(TestCase):
    def test___repr__(self):
        expect(repr(Contacts([
            Contact('James Rowe', 'jnrowe@gmail.com', 200),
        ]))) == \
            "Contacts([Contact('James Rowe', ['jnrowe@gmail.com'], 200)])"

    def test_addresses(self):
        p = Contacts([
            Contact('Bill', ['test@example.com', 'new@example.com'], 30),
            Contact('Joe', ['joe@example.com'], 30)
        ])
        expect(p.addresses()) == ['test@example.com', 'new@example.com',
                                  'joe@example.com']

    def test_parse(self):
        contacts = Contacts()
        contacts.parse('tests/data/blanco.conf', 'frequency')

        # Dirty, dirty, way to handle Unicode type repr differences... sorry
        expect(repr(contacts)) == \
            ('Contacts(['
             "Contact(u'Bill', [u'test@example.com'], 30), "
             "Contact(u'Joe', [u'joe@example.com'], 30), "
             "Contact(u'Steven', [u'steven@example.com'], 365)"
             '])'.replace("u'", "u'" if PY2 else "'"))
