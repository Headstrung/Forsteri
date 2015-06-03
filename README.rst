Forsteri
========

Forsteri is forecasting and data managing software developed for use in the manufacturing stage of the supply chain.

Installation
------------

Install with ``pip``::

    pip install Forsteri

Install from source::

    git clone https://github.com/achawkins/Forsteri
    cd Forsteri
    python setup.py install

Package Contents
----------------

    bin/
        Script for startup.

    data/
        Native data including preferences and imported files.

    doc/
        Sphinx documentation in reStructuredText. To generate the HTML::

            cd doc/
            make html

    forsteri/
        Forsteri sources.

Usage
-----

Full documentation is available at http://achawkins.github.io/Forsteri/

Supported Operating Environment
-------------------------------

This version of the client software has been tested, and is known to work
against the following language versions and Operating Systems:

Language Versions
~~~~~~~~~~~~~~~~~

* Python 2.7

Operating Systems
~~~~~~~~~~~~~~~~~

* Linux
* Windows 7/8

Requirements
------------

Supports Python 2.7. Uses ``wx``, ``webbrowser``, ``sqlite3``,
``subprocess``, ``threading``, ``datetime``, ``copy``, ``pickle``, ``sys``,
``re``, ``csv``, ``operator``, and ``numpy``.

License
-------

All code contained in this repository is Copyright 2015-Present Andrew C. Hawkins.

This code is released under the MIT license. Please see the LICENSE file for
more details.

Contributors
------------

* Andrew C. Hawkins <andrewh@pqmfg.com>

Changelog
---------

* v.0.0.1 Initial release (2015-06-04)
