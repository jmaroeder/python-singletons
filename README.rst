========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-singletons/badge/?style=flat
    :target: https://readthedocs.org/projects/python-singletons
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/jamesmallen/python-singletons.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/jamesmallen/python-singletons

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/jamesmallen/python-singletons?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/jamesmallen/python-singletons

.. |requires| image:: https://requires.io/github/jamesmallen/python-singletons/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/jamesmallen/python-singletons/requirements/?branch=master

.. |version| image:: https://img.shields.io/pypi/v/singletons.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/singletons

.. |commits-since| image:: https://img.shields.io/github/commits-since/jamesmallen/python-singletons/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/jamesmallen/python-singletons/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/singletons.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/singletons

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/singletons.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/singletons

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/singletons.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/singletons


.. end-badges

An example package. Generated with cookiecutter-pylibrary.

* Free software: MIT license

Installation
============

::

    pip install singletons

Documentation
=============

https://python-singletons.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
