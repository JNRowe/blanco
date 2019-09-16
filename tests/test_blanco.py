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

from io import StringIO

from hiro import Timeline
from pytest import (mark, raises)

from blanco import (Contact, Contacts, parse_duration, parse_msmtp,
                    parse_sent, process_config, pynotify, show_note)


TEST_CONTACT = Contact('James Rowe', 'jnrowe@gmail.com', 200)
TEST_CONTACT2 = Contact('James Rowe',
                        ['jnrowe@gmail.com', 'jnrowe@example.com'],
                        200)


def test_missing_mailbox():
    with raises(IOError) as err:
        parse_sent('None')
    assert str(err.value) == 'Sent mailbox ‘None’ not found'


def test_unknown_mailbox_format():
    with raises(ValueError) as err:
        parse_sent('/dev/null')
    assert str(err.value) == 'Unknown mailbox format for ‘/dev/null’'


@mark.parametrize('mbox, recipients, addresses, result', [
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
])
def test_parse_sent(mbox, recipients, addresses, result):
    assert parse_sent(mbox, recipients, addresses) == result


def test_missing_msmtp_log():
    with raises(IOError) as err:
        parse_msmtp('None')
    assert str(err.value) == 'msmtp sent log ‘None’ not found'


@mark.parametrize('log, all_recipients, addresses, gmail, result', [
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
])
def test_parse_msmtp(log, all_recipients, addresses, gmail, result):
    with Timeline().freeze(date(2014, 6, 27)):
        assert parse_msmtp(log, all_recipients, addresses, gmail) == result


def test_parse_msmtp_invalid_gmail():
    with Timeline().freeze(date(2014, 6, 27)):
        with raises(ValueError) as err:
            parse_msmtp('tests/data/sent.msmtp', False, None, True)
        assert 'not in gmail format' in str(err.value)


def test_invalid_duration():
    with raises(ValueError) as err:
        parse_duration('1 k')
    assert str(err.value) == 'Invalid duration value ‘1 k’'


@mark.parametrize('duration, result', [
    ('1d', 1),
    ('1 d', 1),
    ('0.5 y', 182),
    ('0.5 Y', 182),
])
def test_parse_duration(duration, result):
    assert parse_duration(duration) == result


def test_process_config(monkeypatch):
    monkeypatch.setattr('jnrbase.xdg_basedir.user_config',
                        lambda s: 'tests/data/valid')
    conf = process_config()
    assert conf['colour'] is False


def test_process_config_invalid(monkeypatch):
    monkeypatch.setattr('jnrbase.xdg_basedir.user_config',
                        lambda s: 'tests/data/invalid')
    with raises(MissingSectionHeaderError) as err:
        process_config()
    assert 'File contains no section headers.' in str(err.value)


def test_process_config_invalid_types(monkeypatch):
    monkeypatch.setattr('jnrbase.xdg_basedir.user_config',
                        lambda s: 'tests/data/invalid_values')
    with raises(ValueError) as err:
        process_config()
    assert str(err.value) == "Config value for 'colour' must be a bool"


@mark.parametrize('urgency', [
    pynotify.URGENCY_NORMAL,
    pynotify.URGENCY_CRITICAL,
])
def test_show_note(urgency, capsys):
    show_note(False, 'Note for {}', TEST_CONTACT, urgency=urgency)
    _, err = capsys.readouterr()
    # Use contains to avoid having to mess around with {,no-}colour options
    assert 'Note for James Rowe' in err


@mark.parametrize('show_succeeds', [True, False])
def test_show_note_pynotify(show_succeeds, monkeypatch):
    class Notification:
        titles = bodies = icons = []

        def __init__(self, t, s, i):
            self.titles.append(t)
            self.bodies.append(s)
            self.icons.append(i)

        def set_urgency(self, u):
            self.u = u

        def set_timeout(self, o):
            self.o = o

        def show(self):
            return True
    monkeypatch.setattr(pynotify, 'Notification', Notification,
                        raising=False)
    monkeypatch.setattr(pynotify, 'get_server_caps',
                        staticmethod(lambda: []), raising=False)
    if show_succeeds:
        show_note(True, 'Note for {}', TEST_CONTACT)
        assert 'Note for James Rowe' in Notification.bodies
    else:
        monkeypatch.setattr(pynotify.Notification, 'show', lambda s: False)
        with raises(OSError) as err:
            show_note(True, 'Broken note for {}', TEST_CONTACT)
        assert str(err.value) == 'Notification failed to display!'


def test_Contact__repr__():
    assert repr(TEST_CONTACT) == \
        "Contact('James Rowe', ['jnrowe@gmail.com'], 200)"


@mark.parametrize('contact, expected', [
    (TEST_CONTACT, 'James Rowe <jnrowe@gmail.com> (200 days)'),
    (TEST_CONTACT2, 'James Rowe <jnrowe@gmail.com, jnrowe@example.com> '
                    '(200 days)'),
])
def test_Contact__str__(contact, expected):
    assert str(contact) == expected


@mark.parametrize('contact, spec, expected', [
    (TEST_CONTACT, '', 'James Rowe <jnrowe@gmail.com> (200 days)'),
    (TEST_CONTACT, 'email', 'James Rowe <jnrowe@gmail.com>'),
    (TEST_CONTACT2, 'email', 'James Rowe <jnrowe@gmail.com>'),
])
def test_Contact__format__(contact, spec, expected):
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
    (['body-hyperlinks'],
        "<a href='mailto:jnrowe@gmail.com'>James Rowe</a>"),
])
def test_notify_str(server_caps, expected, monkeypatch):
    monkeypatch.setattr(pynotify, 'get_server_caps',
                        staticmethod(lambda: server_caps), raising=False)
    assert TEST_CONTACT.notify_str() == expected


def test_Contacts__repr__():
    assert repr(Contacts([TEST_CONTACT, ])) == \
        "Contacts([Contact('James Rowe', ['jnrowe@gmail.com'], 200)])"


def test_Contacts_addresses():
    p = Contacts([
        Contact('Bill', ['test@example.com', 'new@example.com'], 30),
        Contact('Joe', ['joe@example.com'], 30)
    ])
    assert p.addresses() == ['test@example.com', 'new@example.com',
                             'joe@example.com']


def test_parse():
    contacts = Contacts()
    contacts.parse('tests/data/blanco.conf', 'frequency')

    assert repr(contacts) == \
        ('Contacts(['
            "Contact('Bill', ['test@example.com'], 30), "
            "Contact('Joe', ['joe@example.com'], 30), "
            "Contact('Steven', ['steven@example.com'], 365)"
            '])')


def test_parse_missing_file(tmpdir):
    contacts = Contacts()
    with raises(IOError) as err:
        contacts.parse(str(tmpdir.join('no_such_file')), 'frequency')
    assert 'Addressbook file not found' in str(err.value)
