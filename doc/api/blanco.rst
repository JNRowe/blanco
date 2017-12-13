.. currentmodule:: blanco

Blanco
======

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`blanco`, and can be skipped if you are simply using the tool from the
  command line.

.. autofunction:: parse_msmtp
.. autofunction:: parse_sent
.. autofunction:: show_note

.. autoclass:: Contact
.. autoclass:: Contacts

Examples
--------

.. testsetup::

    import datetime
    from blanco import Contact

.. doctest::

    >>> contact = Contact('James Rowe', 'jnrowe@gmail.com', 200)
    >>> contact.trigger({'jnrowe@gmail.com': datetime.date(1942, 1, 1)})
    datetime.date(1942, 7, 20)
