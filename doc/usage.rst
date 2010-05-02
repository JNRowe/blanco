Usage
-----

:program:`blanco.py` supports writing to standard output or using popup
notifications.

::

    Ξ Desktop/blanco git:(master) ▶ blanco.py
    Mail due for Luke Legate
    Ξ Desktop/blanco git:(master) ▶

If the :option:`--notify <-n>` option is specified popups will be displayed on the desktop, see the example below.

.. figure:: .static/luke.png

The :option:`--notify <-n>` mode is specifically meant from a desktop startup
sequence, and that is how :mod:`blanco`'s author normally uses it.

Options
'''''''

.. program:: blanco.py

.. cmdoption:: --version

   Show program's version number and exit

.. cmdoption:: -h, --help

   Show this help message and exit

.. cmdoption:: -a <file>, --addressbook=<file>

   Address book to read contacts from

.. cmdoption:: -t <mailbox|msmtp>, --sent-type=<mailbox|msmtp>

   Sent source type(mailbox or msmtp)

.. cmdoption:: -r, --all

   Include all recipients(CC and BCC fields)

.. cmdoption:: --no-all

   Include only the first recipient(TO field)

.. cmdoption:: -s <name>, --field=<name>

   Addressbook field to use for frequency value

.. cmdoption:: -n, --notify

   Display reminders using notification popups

.. cmdoption:: --no-notify

   Display reminders on standard out

.. cmdoption:: -v, --verbose

   Produce verbose output

.. cmdoption:: -q, --quiet

   Output only matches and errors

Mailbox options
~~~~~~~~~~~~~~~

.. cmdoption:: -m <mailbox>, --mbox=<mailbox>

   Mailbox used to store sent mail

msmtp log options
~~~~~~~~~~~~~~~~~

.. cmdoption:: -l <file>, --log=<file>

   msmtp log to parse

.. cmdoption:: -g, --gmail

   Log from a gmail account(use accurate filter)

.. cmdoption:: --no-gmail

   msmtp log for non-gmail account
