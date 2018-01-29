========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |travis|
    * - package
      - |version| |supported-versions| |supported-implementations|
        |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-singletons/badge/?style=flat
    :target: https://readthedocs.org/projects/python-singletons
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/jamesmallen/python-singletons.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/jamesmallen/python-singletons

.. |version| image:: https://img.shields.io/pypi/v/singletons.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/singletons

.. |commits-since| image:: https://img.shields.io/github/commits-since/jamesmallen/python-singletons/v0.2.1.svg
    :alt: Commits since latest release
    :target: https://github.com/jamesmallen/python-singletons/compare/v0.2.1...master

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/singletons.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/singletons

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/singletons.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/singletons


.. end-badges

Declaring singleton classes and singleton factories with different scopes of instantiation, striving for thread-safety and simplicity.

* Free software: MIT license

Installation
============

::

    pip install singletons

Quick Example
=============

::

	import singletons

    @singletons.GlobalFactory
    def my_uuid():
        return uuid.uuid4()

    # elsewhere...
    my_uuid()  # will return the global instance of a UUID object

Documentation
=============

https://python-singletons.readthedocs.io/

Development
===========

To run the all tests run::

    tox
