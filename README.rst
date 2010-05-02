``blanco`` - *"Hey, remember me?"*
==================================

Introduction
------------

``blanco`` is a simple tool to help you, or more specifically *me*. keep in
touch with people.  All it does is notify you if you're failing to keep in
contact.  It is just a quick solution to a simple problem, as long as you use
abook_ and your sent mail is easily accessible that is.

It is written in Python_ and licensed under the `GPL v3`_.

Configuration
-------------

``blanco`` expects your abook_ entries to have a frequency value in
the ``custom4`` field [#]_.  The format is "<n> <units>", where ``n`` is
a number and ``units`` is a character from the set ``[dwmy]``.  For example, an
entry with a frequency of ``3 m`` will be triggered if there hasn't been a mail
sent to that address in three months.

If you set ``customfield 4 Frequency`` in your ``~/.abook/abookrc`` the abook_
interface will display "Frequency" in the interface when editing the custom
fields.  You do *not* need to set this for ``blanco`` to work, but it makes the
purpose of the field clearer.

.. [#] You can select a different field using the ``--field`` option to
       ``blanco``.

Example
-------

``blanco`` expects you to give it the location of an abook_ addressbook file and
the location of your sent mail in mbox format, and informs you if you're
forgetting to contact somebody.

::

    $ ./date.py
    2010-02-15
    $ ./blanco.py -a test/blanco.conf -m test/sent.mbox
    Due for Joe
    No record of a sent email for Steven
    $ ./blanco.py -a test/blanco.conf -m test/sent.mbox --cc
    Due for Joe
    Due for Steven

Without abook
'''''''''''''

``blanco`` can be used without abook_, as it only requires a ini_ formatted
contacts file and access to a mailbox containing sent mail.  To create your own
contacts file without abook follow the format below::

    [0]
    name=Bill
    email=test@example.com
    frequency=30d

    [1]
    name=Joe
    email=joe@example.com
    frequency=30d

If you use the layout above you should specify ``--field=frequency`` when
calling ``blanco``.

Another alternative would be to use abook_ just to convert your current address
book in to a suitable format.  Check the output of ``abook --formats`` for the
file formats supported by your version of abook_.

Contributors
------------

I'd like to thank the following people who have contributed to this repository.

Ideas
'''''

* Morgan Lane

If I've forgotten to include your name I wholeheartedly apologise.  Just drop me
an mail_ and I'll update the list!

Bugs
----

If you find any problems, bugs or just have a question about this package either
drop me a mail_ or file an issue_.  Locally bugs are managed with ditz_, so if
you're working with a clone of the repository you can report, list and fix bugs
using ``ditz``.

If you've found a bug please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _abook: http://abook.sourceforge.net/
.. _GPL v3: http://www.gnu.org/licenses/
.. _Python: http://www.python.org/
.. _mail: jnrowe@gmail.com
.. _issue: http://github.com/JNRowe/blanco/issues
.. _ditz: http://ditz.rubyforge.org/
.. _ini: http://www.cloanto.com/specs/ini/

..
    :vim: set ft=rst ts=4 sw=4 et:

