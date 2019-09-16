``blanco`` - *“Hey, remember me?”*
==================================

|status| |travis| |coveralls| |readthedocs| |develop|

Introduction
------------

``blanco`` is a simple tool to help you, or more specifically *me*, keep in
touch with people.  All it does is notify you if you’re failing to keep in
contact.  It is just a quick solution to a simple problem, as long as you use
abook_ and your sent mail is locally accessible.

It is written in Python_ and licensed under the `GPL v3`_.

Configuration
-------------

``blanco`` expects your abook_ entries to have a frequency value in the
``frequency`` field [#]_.  The format is “<n> <units>”, where ``n`` is a number
and ``units`` is a character from the set ``[dwmy]``.  For example, an entry
with a frequency of ``3 m`` will be triggered if there hasn’t been a mail sent
to that address in three months.

If you add the following snippet to your ``~/.abook/abookrc`` the abook_
interface will display “Frequency” in the interface when editing the ``other``
tab for a contact.

::

    field frequency = Frequency

    view OTHER = frequency

.. [#] You can select a different field using the ``--field`` option to
       ``blanco``.

Example
-------

``blanco`` expects you to give it the location of an abook_ addressbook file and
the location of your sent mail in mbox format, and informs you if you’re
forgetting to contact somebody.

::

    $ ./blanco.py --no-notify -a tests/data/blanco.conf -m tests/data/sent.mbox
    Mail due for Bill
    Mail due for Joe
    No mail record for Steven
    $ ./blanco.py --no-notify -a tests/data/blanco.conf -m tests/data/sent.mbox --all
    Mail due for Bill
    Mail due for Joe
    Mail due for Steven

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

I’d like to thank the following people who have contributed to this repository.

Ideas
'''''

* Morgan Lane

If I’ve forgotten to include your name I wholeheartedly apologise.  Just drop me
an mail_ and I’ll update the list!

Bugs
----

If you find any problems, bugs or just have a question about this package either
file an issue_ or drop me a mail_.

If you’ve found a bug please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _abook: http://abook.sourceforge.net/
.. _GPL v3: http://www.gnu.org/licenses/
.. _Python: http://www.python.org/
.. _mail: jnrowe@gmail.com
.. _issue: https://github.com/JNRowe/blanco/issues
.. _ini: http://www.cloanto.com/specs/ini/

.. |travis| image:: https://img.shields.io/travis/JNRowe/blanco.png
   :target: https://travis-ci.org/JNRowe/blanco
   :alt: Test state on master

.. |develop| image:: https://img.shields.io/github/commits-since/JNRowe/blanco/latest.png
   :target: https://github.com/JNRowe/blanco
   :alt: Recent developments

.. |status| image:: https://img.shields.io/pypi/status/blanco.png
   :alt: Development status

.. |coveralls| image:: https://img.shields.io/coveralls/github/JNRowe/blanco/master.png
   :target: https://coveralls.io/repos/JNRowe/blanco
   :alt: Coverage state on master

.. |readthedocs| image:: https://img.shields.io/readthedocs/blanco/stable.png
   :target: https://blanco.readthedocs.io/
   :alt: Documentation
