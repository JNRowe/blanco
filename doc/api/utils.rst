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
