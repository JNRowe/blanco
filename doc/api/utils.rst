.. currentmodule:: blanco

Utilities
=========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  :mod:`blanco`, and can be skipped if you are simply using the tool from the
  command line.

Time handling
'''''''''''''

.. autofunction:: parse_duration

Text formatting
'''''''''''''''

.. autofunction:: _colourise
.. autofunction:: success
.. autofunction:: fail
.. autofunction:: warn

Examples
--------

Time handling
'''''''''''''

.. testsetup::

    from blanco import parse_duration

.. doctest::

    >>> parse_duration('4w')
    28
    >>> parse_duration('2 m')
    56

Text formatting
'''''''''''''''

.. need to figure out way to expose colouring in a sane manner

.. testsetup::

    from blanco import (T, fail, success, warn)
    T._does_styling = False

.. doctest::

    >>> fail('Error!')
    'Error!'
    >>> success('Excellent')
    'Excellent'
    >>> warn('Ick')
    'Ick'
