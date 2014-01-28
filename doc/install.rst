Installation
------------

You can download releases from the `downloads page`_ on GitHub_.

``blanco`` requires Python_ v2.6(or newer) and the following Python modules:

* arrow_

The following optional packages will be used if available:

* `libnotify Python bindings`_ for popup notifications
* blessings_ for coloured output in the terminal

If you're using Gentoo_ the hard dependencies are available from the main tree,
and the optional dependencies are available from a combination of the main tree
and `my overlay`_.

From source
'''''''''''

One you have downloaded a source tarball you can install it with the following
steps::

    $ python setup.py build
    # python setup.py install  # to install in Python's site-packages
    $ python setup.py install --user  # to install for a single user

.. _downloads page: https://github.com/JNRowe/blanco/downloads
.. _GitHub: https://github.com/
.. _Python: http://www.python.org/
.. _arrow: https://crate.io/packages/arrow/
.. _libnotify Python bindings: http://www.galago-project.org/downloads.php
.. _blessings: https://crate.io/packages/blessings/
.. _Gentoo: http://www.gentoo.org/
.. _my overlay: http://github.com/JNRowe/misc-overlay
