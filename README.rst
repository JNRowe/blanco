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
``customfield4``.  The format is "<n> <units>", where ``n`` is a number and
``units`` is a character from the set ``[dwmy]``.  For example, an entry with
a frequency of ``3 m`` will be triggered if there hasn't been a mail sent to
that address in three months.

If you set ``customfield 4 Frequency`` in your ``~/.abook/abookrc`` the abook_
interface will display "Frequency" in the interface when editing the custom
fields.  You do *not* need to set this for ``blanco`` to work, but you must use
``customfield4`` (see bug 2d6).

Example
-------

``blanco`` expects you to give it the location of an abook_ addressbook file and
the location of your sent mail in mbox format, and informs you if you're
forgetting to contact somebody.

..

    $ ./blanco.py -a test/blanco.conf -m test/sent.mbox
    Due for Joe
    No record of a sent email for Steven
    $ ./blanco.py -a test/blanco.conf -m test/sent.mbox --cc
    Due for Joe
    Due for Steven

Bugs
----

If you find any problems, bugs or just have a question about this package either
drop me a mail_ or file an issue_.  Locally bugs are managed with ditz_, so if
you're working with a clone of the repository you can report, list and fix bugs
using ``ditz``.

If you've found please attempt to include a minimal testcase so I can reproduce
the problem, or even better a patch!

.. _abook: http://abook.sourceforge.net/
.. _GPL v3: http://www.gnu.org/licenses/
.. _Python: http://www.python.org/
.. _mail: jnrowe@gmail.com
.. _issue: http://github.com/JNRowe/blanco/issues
.. _ditz: http://ditz.rubyforge.org/

..
    :vim: set ft=rst ts=4 sw=4 et:

