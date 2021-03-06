#
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

from configparser import MissingSectionHeaderError
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from hiro import Timeline
from pytest import (mark, raises)

from blanco import (Contact, Contacts, notify2, parse_msmtp, parse_sent,
                    process_config, show_note)

TEST_CONTACT = Contact('James Rowe', 'jnrowe@gmail.com', 200)
TEST_CONTACT2 = Contact(
    'James Rowe', ['jnrowe@gmail.com', 'jnrowe@example.com'], 200, 'james.png')


class MockNotification:
    titles: List[str] = []
    bodies: List[str] = []
    icons: List[str] = []

    def __init__(self, t: str, s: str, i: str):
        self.titles.append(t)
        self.bodies.append(s)
        self.icons.append(i)

    def set_urgency(self, u: int):
        self.u = u

    def set_timeout(self, o: int):
        self.o = o

    def show(self):
        return True


def test_missing_mailbox(tmpdir):
    with raises(IOError) as err:
        parse_sent(Path(tmpdir.join('no_such_file')))
    assert str(err.value).endswith(' not found')


def test_unknown_mailbox_format():
    with raises(ValueError) as err:
        parse_sent(Path('/dev/null'))
    assert str(err.value) == 'Unknown mailbox format for ‘/dev/null’'


@mark.parametrize('mbox, recipients, addresses, result', [
    ('sent.maildir', True, None, {
        'nobody@example.com': date(2000, 2, 9),
        'max@example.com': date(2000, 2, 9),
        'test@example.com': date(2010, 2, 9),
        'steven@example.com': date(2000, 2, 9),
        'joe@example.com': date(2000, 2, 9),
    }),
    ('sent.mh', False, None, {
        'nobody@example.com': date(2000, 2, 9),
        'max@example.com': date(2000, 2, 9),
        'test@example.com': date(2010, 2, 9),
        'joe@example.com': date(2000, 2, 9),
    }),
    ('sent.mbox', False, 'joe@example.com', {
        'joe@example.com': date(2000, 2, 9),
    }),
])
def test_parse_sent(mbox: str, recipients: bool, addresses: Optional[str],
                    result: Dict[str, date]):
    assert parse_sent(Path('tests/data') / mbox, recipients, addresses) \
        == result


def test_missing_msmtp_log(tmpdir):
    with raises(IOError) as err:
        parse_msmtp(Path(tmpdir.join('no_such_file')))
    assert str(err.value).endswith(' not found')


@mark.parametrize('log, all_recipients, addresses, gmail, result', [
    ('sent.msmtp', False, None, False, {
        'nobody@example.com': date(2013, 2, 9),
        'test@example.com': date(2013, 2, 9),
        'joe@example.com': date(2013, 2, 9),
    }),
    ('sent.msmtp', True, None, False, {
        'nobody@example.com': date(2013, 2, 9),
        'max@example.com': date(2013, 2, 9),
        'test@example.com': date(2013, 2, 9),
        'steven@example.com': date(2013, 2, 9),
        'joe@example.com': date(2013, 2, 9),
    }),
    ('sent.msmtp', False, [
        'nobody@example.com',
    ], False, {
        'nobody@example.com': date(2013, 2, 9),
    }),
    ('sent_gmail.msmtp', False, None, True, {
        'nobody@example.com': date(2000, 2, 9),
        'test@example.com': date(2010, 2, 9),
        'joe@example.com': date(2000, 2, 9),
    }),
])
def test_parse_msmtp(log: str, all_recipients: bool,
                     addresses: Optional[List[str]], gmail: bool,
                     result: Dict[str, date]):
    with Timeline().freeze(date(2014, 6, 27)):
        assert parse_msmtp(
            Path('tests/data') / log, all_recipients, addresses,
            gmail) == result


def test_parse_msmtp_invalid_gmail():
    with Timeline().freeze(date(2014, 6, 27)):
        with raises(ValueError) as err:
            parse_msmtp(Path('tests/data/sent.msmtp'), False, None, True)
        assert 'not in gmail format' in str(err.value)


def test_process_config(monkeypatch):
    monkeypatch.setattr(
        'jnrbase.xdg_basedir.user_config', lambda s: 'tests/data/valid')
    conf = process_config()
    assert conf['colour'] is False


def test_process_config_invalid(monkeypatch):
    monkeypatch.setattr(
        'jnrbase.xdg_basedir.user_config', lambda s: 'tests/data/invalid')
    with raises(MissingSectionHeaderError) as err:
        process_config()
    assert 'File contains no section headers.' in str(err.value)


def test_process_config_invalid_types(monkeypatch):
    monkeypatch.setattr('jnrbase.xdg_basedir.user_config', lambda s:
                        'tests/data/invalid_values')
    with raises(ValueError) as err:
        process_config()
    assert str(err.value) == "Config value for 'colour' must be a bool"


@mark.parametrize('urgency', [
    notify2.URGENCY_NORMAL,
    notify2.URGENCY_CRITICAL,
])
def test_show_note(urgency: int, capsys):
    show_note(False, 'Note for {}', TEST_CONTACT, urgency=urgency)
    _, err = capsys.readouterr()
    # Use contains to avoid having to mess around with {,no-}colour options
    assert 'Note for James Rowe' in err


@mark.parametrize('show_succeeds', [True, False])
def test_show_note_notify2(show_succeeds: bool, monkeypatch):
    monkeypatch.setattr(notify2,
                        'Notification',
                        MockNotification,
                        raising=False)
    monkeypatch.setattr(notify2, 'get_server_caps', lambda: [], raising=False)
    if show_succeeds:
        show_note(True, 'Note for {}', TEST_CONTACT)
        assert 'Note for James Rowe' in MockNotification.bodies
    else:
        monkeypatch.setattr(notify2.Notification, 'show', lambda s: False)
        with raises(OSError) as err:
            show_note(True, 'Broken note for {}', TEST_CONTACT)
        assert str(err.value) == 'Notification failed to display!'


@mark.parametrize('contact', [TEST_CONTACT, TEST_CONTACT2])
def test_show_note_notify2_icons(contact: Contact, monkeypatch):
    monkeypatch.setattr(notify2,
                        'Notification',
                        MockNotification,
                        raising=False)
    monkeypatch.setattr(notify2, 'get_server_caps', lambda: [], raising=False)
    show_note(True, '{}', contact)
    assert contact.name in MockNotification.bodies
    if TEST_CONTACT.image:
        assert TEST_CONTACT.image in MockNotification.icons
    else:
        assert TEST_CONTACT.image not in MockNotification.icons


def test_Contact__repr__():
    assert repr(TEST_CONTACT) == \
        "Contact('James Rowe', ['jnrowe@gmail.com'], 200, None)"


@mark.parametrize('contact, expected', [
    (TEST_CONTACT, 'James Rowe [jnrowe@gmail.com] (200 days)'),
    (TEST_CONTACT2, 'James Rowe [jnrowe@gmail.com, jnrowe@example.com] '
     '(200 days)'),
])
def test_Contact__str__(contact: Contact, expected: str):
    assert str(contact) == expected


@mark.parametrize('contact, spec, expected', [
    (TEST_CONTACT, '', 'James Rowe [jnrowe@gmail.com] (200 days)'),
    (TEST_CONTACT, 'email', 'James Rowe <jnrowe@gmail.com>'),
    (TEST_CONTACT2, 'email', 'James Rowe <jnrowe@gmail.com>'),
])
def test_Contact__format__(contact: Contact, spec: str, expected: str):
    assert format(contact, spec) == expected


def test_Contact__format___invalid_type():
    with raises(ValueError) as err:
        format(TEST_CONTACT, 'hat style')
    assert str(err.value) == "Unknown format_spec 'hat style'"


def test_trigger():
    assert TEST_CONTACT.trigger({
        'jnrowe@gmail.com': date(1942, 1, 1),
    }) == date(1942, 7, 20)


@mark.parametrize('server_caps, expected', [
    ([], 'James Rowe'),
    (['body-hyperlinks'], "<a href='mailto:jnrowe@gmail.com'>James Rowe</a>"),
])
def test_notify_str(server_caps: List[str], expected: str, monkeypatch):
    monkeypatch.setattr(
        notify2, 'get_server_caps', lambda: server_caps, raising=False)
    assert TEST_CONTACT.notify_str() == expected


def test_Contacts__repr__():
    assert repr(Contacts([TEST_CONTACT, ])) == \
        "Contacts([Contact('James Rowe', ['jnrowe@gmail.com'], 200, None)])"


def test_Contacts_addresses():
    p = Contacts([
        Contact('Bill', ['test@example.com', 'new@example.com'], 30),
        Contact('Joe', ['joe@example.com'], 30)
    ])
    assert p.addresses() == [
        'test@example.com', 'new@example.com', 'joe@example.com'
    ]


def test_parse():
    contacts = Contacts()
    contacts.parse(Path('tests/data/blanco.conf'), 'frequency')

    assert repr(contacts) == \
        ('Contacts(['
            "Contact('Bill', ['test@example.com'], 30, None), "
            "Contact('Joe', ['joe@example.com'], 30, None), "
            "Contact('Steven', ['steven@example.com'], 365, None)"
            '])')


def test_parse_missing_file(tmpdir):
    contacts = Contacts()
    with raises(IOError) as err:
        contacts.parse(Path(tmpdir.join('no_such_file')), 'frequency')
    assert 'Addressbook file not found' in str(err.value)
