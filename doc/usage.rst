Usage
-----

:program:`blanco.py` supports writing to standard output or using popup
notifications.

.. code-block:: sh

    $ blanco
    Mail due for Luke Legate
    $

If the :option:`--notify <-n>` option is specified popups will be displayed on
the desktop, see the example below.

.. figure:: .static/luke.png

The :option:`--notify <-n>` mode is specifically meant from a desktop startup
sequence, and that is how :mod:`blanco`'s author normally uses it.

Options
'''''''

.. program:: blanco.py

.. option:: --version

   Show program's version number and exit

.. option:: -h, --help

   Show this help message and exit

.. option:: -a <file>, --addressbook=<file>

   Address book to read contacts from

.. option:: -t <mailbox|msmtp>, --sent-type=<mailbox|msmtp>

   Sent source type(mailbox or msmtp)

.. option:: -r, --all

   Include all recipients(CC and BCC fields)

.. option:: --no-all

   Include only the first recipient(TO field)

.. option:: -s <name>, --field=<name>

   Addressbook field to use for frequency value

.. option:: -n, --notify

   Display reminders using notification popups

.. option:: --no-notify

   Display reminders on standard out

.. option:: -v, --verbose

   Produce verbose output

.. option:: -q, --quiet

   Output only matches and errors

Mailbox options
~~~~~~~~~~~~~~~

.. option:: -m <mailbox>, --mbox=<mailbox>

   Mailbox used to store sent mail

msmtp log options
~~~~~~~~~~~~~~~~~

.. option:: -l <file>, --log=<file>

   msmtp log to parse

.. option:: -g, --gmail

   Log from a gmail account(use accurate filter)

.. option:: --no-gmail

   msmtp log for non-gmail account
