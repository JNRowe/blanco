Setup
-----

:program:`blanco` requires access to your sent mail for calculating last
contact times, and also access to a map of contact-to-frequency for calculating
forgotten people.

If you can’t fulfil the requirements in the following two sections then
:program:`blanco` is not for you!

Sent mail
'''''''''

mbox_, maildir_ and MH_ mailbox formats are supported, thanks to the
wonderful mailbox_ Python module.

msmtp_ logs are also supported, and using them is the preferred method.  Parsing
simple log entries is appreciably faster than processing mailboxes, and this
method should be chosen if at all possible.

There is also a faster gmail_ specific option when you’re using the msmtp_ log
method, which takes advantage of the extra data included in Google_’s responses
to calculate the date a mail was sent.

Addressbook
'''''''''''

The default addressbook format is the format used by abook_, where one of the
custom fields allowed by :program:`abook` is used to store frequency
information.

:program:`blanco` expects your :program:`abook` entries to have a frequency
value in the ``frequency`` field [#]_.  The format is “<n> <units>”, where
``n`` is a number and ``units`` is a character from the set ``[dwmy]``.  For
example, an entry with a frequency of ``3 m`` will be triggered if there hasn’t
been a mail sent to that address in three months.

You can add the following snippet to your :file:`~/.abook/abookrc` file to
display a frequency field in the ``other`` tab::

    field frequency = Frequency

    view OTHER = frequency

.. figure:: .static/abook_rach.png

You do *not* need to set this for :program:`blanco` to work, but it makes the
purpose of the field clearer.

If you wish to use custom icons for contact reminders you can specify a local
image location with an  ``image`` field in your addressbook.

:program:`blanco` can be used without :program:`abook`, as it only requires
a ini_ formatted contacts file.  To create your own contacts file without abook
follow the format below:

.. code-block:: ini

    [0]
    name=Bill
    email=test@example.com
    image=/var/cache/avatars/55502f40dc8b7c769880b10874abc9d0.png
    freq=30d

    [1]
    name=Joe
    email=joe@example.com
    freq=30d

If you use the layout above you should specify ``--field=freq`` when calling
:program:`blanco`.

Another alternative would be to use :program:`abook` just to convert your
current address book in to a suitable format.  Check the output of ``abook
--formats`` for the file formats supported by your version of :program:`abook`.

.. [#] You can select a different field using the :option:`--field <-s>` option
       to ``blanco``.

Configuration
-------------

:program:`blanco` stores its configuration in
:file:`${XDG_CONFIG_HOME}/blanco/config.ini` [#]_.

The configuration file is a simple ``INI`` format file,   The file is processed
with the configobj_ module, the documentation for which will describe some of
the advanced features available within the configuration file.

You can specify command line options in the configuration file as defaults, and
optionally override them from the command line.  To toggle boolean options from
the command line use their ``--no-`` prefixed versions.

An example configuration file is below:

.. code-block:: ini

    sent type = msmtp
    field = custom5

.. [#] The default value for ``${XDG_CONFIG_HOME}`` is system dependent, but
       likely to be ``~/.config`` if you haven’t set it.  For more information
       see `XDG base directory specification`_.

.. _mbox: https://en.m.wikipedia.org/wiki/Mbox
.. _maildir: https://en.m.wikipedia.org/wiki/Maildir
.. _mh: https://en.m.wikipedia.org/wiki/MH_Message_Handling_System
.. _mailbox: http://docs.python.org/library/mailbox.html
.. _msmtp: http://msmtp.sourceforge.net/
.. _gmail: http://mail.google.com/
.. _google: http://google.com/
.. _abook: http://abook.sourceforge.net/
.. _ini: http://www.cloanto.com/specs/ini/
.. _configobj: http://configobj.readthedocs.org/
.. _XDG base directory specification: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
