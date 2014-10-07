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

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA

from hiro import Timeline
from jnrbase import compat
from pytest import (mark, raises)

from blanco import (Contact, Contacts, parse_duration, parse_msmtp,
                    parse_sent, process_config, pynotify, show_note)


def test_missing_mailbox():
    with raises(IOError) as err:
        parse_sent('None')
    assert err.value.message == "Sent mailbox 'None' not found"


def test_unknown_mailbox_format():
    with raises(ValueError) as err:
        parse_sent('/dev/null')
    assert err.value.message == "Unknown mailbox format for '/dev/null'"


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
    assert err.value.message == "msmtp sent log 'None' not found"


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
        assert 'not in gmail format' in err.value.message


def test_invalid_duration():
    with raises(ValueError) as err:
        parse_duration('1 k')
    assert err.value.message == "Invalid duration value '1 k'"


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
    assert conf.get('colour') is False


def test_process_config_invalid(monkeypatch):
    monkeypatch.setattr('jnrbase.xdg_basedir.user_config',
                        lambda s: 'tests/data/invalid')
    with raises(SyntaxError) as err:
        process_config()
    assert 'Invalid configuration file' in err.value.message


class TestShowNote:
    @classmethod
    def setup_class(cls):
        cls.contact1 = Contact('James Rowe', 'jnrowe@gmail.com', 200)

    @mark.parametrize('urgency', [
        pynotify.URGENCY_NORMAL,
        pynotify.URGENCY_CRITICAL,
    ])
    def test_show_note(self, urgency, capsys):
        show_note(False, 'Note for %s', self.contact1, urgency=urgency)
        out, _ = capsys.readouterr()
        # Use contains to avoid having to mess around with {,no-}colour options
        assert 'Note for James Rowe' in out

    @mark.parametrize('show_succeeds', [True, False])
    def test_show_note_pynotify(self, show_succeeds, monkeypatch):
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
            show_note(True, 'Note for %s', self.contact1)
            assert 'Note for James Rowe' in Notification.bodies
        else:
            monkeypatch.setattr(pynotify.Notification, 'show', lambda s: False)
            with raises(OSError) as err:
                show_note(True, 'Broken note for %s', self.contact1)
            assert err.value.message == 'Notification failed to display!'


class TestContact:
    def setUp(self):  # NOQA
        self.contact = Contact('James Rowe', 'jnrowe@gmail.com', 200)

    def test___repr__(self):
        assert repr(self.contact) == \
            "Contact('James Rowe', ['jnrowe@gmail.com'], 200)"

    def test___str__(self):
        assert str(self.contact) == \
            'James Rowe <jnrowe@gmail.com> (200 days)'
        assert str(Contact(
            'James Rowe', ['jnrowe@gmail.com', 'jnrowe@example.com'],
            200)) == \
            'James Rowe <jnrowe@gmail.com, jnrowe@example.com> (200 days)'

    def test___format__(self):
        assert format(self.contact) == \
            'James Rowe <jnrowe@gmail.com> (200 days)'
        assert format(self.contact, 'email') == \
            'James Rowe <jnrowe@gmail.com>'
        assert format(Contact, 'email'(
            'James Rowe', ['jnrowe@gmail.com', 'jnrowe@example.com'],
            200)) == \
            'James Rowe <jnrowe@gmail.com>'

    def trigger(self, sent):
        assert self.contact.trigger({
            'jnrowe@gmail.com': date(1942, 1, 1)}
        ) == date(1942, 7, 20)

    def notify_str(self, monkeypatch):
        monkeypatch('pynotify.get_server_caps', lambda: [])
        assert self.contact.notify_str() == 'James Rowe'
        monkeypatch('pynotify.get_server_caps', lambda: ['body-hyperlinks', ])
        assert self.contact.notify_str() == \
            "<a href='mailto:jnrowe@gmail.com'>James Rowe</a>"



class TestContacts:
    def test___repr__(self):
        assert repr(Contacts([
            Contact('James Rowe', 'jnrowe@gmail.com', 200),
        ])) == \
            "Contacts([Contact('James Rowe', ['jnrowe@gmail.com'], 200)])"

    def test_addresses(self):
        p = Contacts([
            Contact('Bill', ['test@example.com', 'new@example.com'], 30),
            Contact('Joe', ['joe@example.com'], 30)
        ])
        assert p.addresses() == ['test@example.com', 'new@example.com',
                                 'joe@example.com']

    def test_parse(self):
        contacts = Contacts()
        contacts.parse('tests/data/blanco.conf', 'frequency')

        # Dirty, dirty, way to handle Unicode type repr differences... sorry
        assert repr(contacts) == \
            ('Contacts(['
             "Contact(u'Bill', [u'test@example.com'], 30), "
             "Contact(u'Joe', [u'joe@example.com'], 30), "
             "Contact(u'Steven', [u'steven@example.com'], 365)"
             '])'.replace("u'", "u'" if compat.PY2 else "'"))

    def test_parse_missing_file(self, tmpdir):
        contacts = Contacts()
        with raises(IOError) as err:
            contacts.parse(str(tmpdir.join('no_such_file')), 'frequency')
        assert 'Addressbook file not found' in err.value.message
