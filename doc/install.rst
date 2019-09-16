Installation
------------

.. highlight:: console

You can download releases from the `downloads page`_ on GitHub_.

``blanco`` requires Python_ v3.6(or newer) and the following Python modules:

* jnrbase_

The following optional packages will be used if available:

* `libnotify Python bindings`_ for popup notifications

From source
'''''''''''

One you have downloaded a source tarball you can install it with the following
steps::

    $ python setup.py build
    # python setup.py install  # to install in Python’s site-packages
    $ python setup.py install --user  # to install for a single user

.. _downloads page: https://github.com/JNRowe/blanco/downloads
.. _GitHub: https://github.com/
.. _Python: http://www.python.org/
.. _jnrbase: https://pypi.python.org/pypi/jnrbase/
.. _libnotify Python bindings: http://www.galago-project.org/downloads.php
