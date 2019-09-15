blanco.py
=========

*“Hey, remember me?”*
"""""""""""""""""""""

:Author: James Rowe <jnrowe@gmail.com>
:Date: 2010-05-02
:Copyright: GPL v3
:Manual section: 1
:Manual group: Email

SYNOPSIS
--------

    blanco.py [option]...

DESCRIPTION
-----------

A simple tool to help you, or more specifically *me*, keep in touch with people.
All it does is notify you if you’re failing to keep in contact.  It is just
a quick solution to a simple problem, as long as you use `abook
<http://abook.sourceforge.net/>`_ and your sent mail is easily accessible.

OPTIONS
-------

-a, --addressbook FILENAME
    Address book to read contacts from.

-t, --sent-type [mailbox|msmtp]
    Sent source type.

-r, --all / --no-all
    Include all recipients(CC and BCC fields).

-m, --mbox FILENAME
    Mailbox used to store sent mail.

-l, --log FILENAME
    msmtp log to parse.

-g, --gmail / --no-gmail
    Log from a gmail account(use accurate filter).

-s, --field TEXT
    Addressbook field to use for frequency value.

-n, --notify / --no-notify
    Display reminders using notification popups.

-v, --verbose / --no-verbose
    Produce verbose output.

--version
    Show the version and exit.

--help
    Show this message and exit.

CONFIGURATION FILE
------------------

The configuration file, **${XDG_CONFIG_HOME:-~/.config}/blanco/config.ini**, is
a simple **INI** format file for storing defaults for the command line options.
For example:

.. code-block:: ini

    sent type = msmtp
    field = custom5

With the above configuration file the default sent mail source will be a msmtp
logfile, and frequency information will be stored in abook’s ``custom5`` field.

BUGS
----

None known.

AUTHOR
------

Written by `James Rowe <mailto:jnrowe@gmail.com>`__

RESOURCES
---------

Home page: https://github.com/JNRowe/blanco

COPYING
-------

Copyright © 2010-2014  James Rowe.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
