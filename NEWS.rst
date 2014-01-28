``blanco``
==========

User-visible changes
--------------------

.. contents::

0.5.0 - 2010-05-16
------------------

* Full documentation using Sphinx_
* ``--no-`` prefix options for overriding configuration file from the command
  line
* Basic ``setup.py`` script for installation, using distutils_

.. _Sphinx: http://sphinx.pocoo.org/
.. _distutils: http://docs.python.org/library/distutils.html

0.4.0 - 2010-05-02
------------------

* Popup notifications support, for use in desktop environments, using
  notify-python_

.. _notify-python: http://www.galago-project.org/

0.3.0 - 2010-02-19
------------------

* Support for setting command line options in ``~/.blancorc``, the format is
  ``<option>=<value>`` with no leading dashes in option names
* Much faster processing for large sent mailboxes
* Support for reading msmtp_ logs as an alternative to parsing sent mail
* Optional gmail_-specific log parser for increased accuracy in log parsing

.. _msmtp: http://msmtp.sourceforge.net/
.. _gmail: http://mail.google.com/

0.2.0 - 2010-02-11
------------------

* Support for optionally checking ``CC`` and ``BCC`` fields for last contacts
* User defined abook field for storing frequency information
* Contacts with multiple addresses are now supported
* Support for sent mail in maildir and MH formats
* Coloured output with termstyle_

.. _termstyle: https://github.com/gfxmonk/termstyle

0.1.0 - 2010-02-10
------------------

* Initial release
