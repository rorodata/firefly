Sphinx to GitHub
================

ATTENTION!
----------

This project is designed to help you get around the github-pages Jekyll
behaviour of ignoring top level directories starting with an underscore.

This is solved in a much neater way by creating a ``.nojekyll`` in the root
of you github-pages which will disable Jekyll as described `here
<https://github.com/blog/572-bypassing-jekyll-on-github-pages>`__ and `here
<http://pages.github.com/>`__.

This makes this project largely useless! Thank you to `acdha
<https://github.com/acdha>`__ for making me aware of this.

What?
-----

A Python script for preparing the html output of the Sphinx documentation
system for github pages.

It renames any top level folders which start with an underscore and edits any
references to them within the html files.

Why?
----

GitHub processes the incoming html with Jekyll which believes top level folders
starting with an underscore are special and does not let their content be accessible
to the server. This is incompatible with Sphinx which uses underscores at the
start of folder names for static content.

Usage
-----

The ``sphinxtogithub.py`` script can be run on the command line or used as a
Sphinx extension.

Extension
~~~~~~~~~

Place the script on the ``PYTHONPATH`` and add ``sphinxtogithub`` to the
extensions list in the ``conf.py`` file in your Sphinx project::

    extensions = [ "sphinxtogithub" ]

Additionally there are three config variables you can use to control the
extension. The first enables/disables the extension, the second enables verbose
output and the third determines the encoding which is used to read & write
files. The first two are ``True`` by default and the third is set to ``utf-8``::

    sphinx_to_github = True
    sphinx_to_github_verbose = True
    sphinx_to_github_encoding = "utf-8"

Command Line
~~~~~~~~~~~~

Run the script with the path to the ``html`` output directory as the first
argument. There is a ``--verbose`` flag for basic output.

Further Information
-------------------

Install from GitHub
~~~~~~~~~~~~~~~~~~~

It should be possible to install this tool directly from github using pip::

    pip install -e git+git://github.com/michaeljones/sphinx-to-github.git#egg=sphinx-to-github

Thanks to `winhamwr <http://github.com/winhamwr>`_'s work.

Requirements
~~~~~~~~~~~~

The script uses ``/usr/bin/env`` and ``python``.

Running Tests
~~~~~~~~~~~~~

Unit tests can be run using the setuptools ``test`` target. eg::

    $ python setup.py test

Alternatives
~~~~~~~~~~~~

`dinoboff <http://github.com/dinoboff>`_'s project
`github-tools <http://github.com/dinoboff/github-tools>`_ provides similar
functionality combined with a much more comprehensive set of tools for helping
you to manage Python based projects on github.

Credits
-------

Thank you to:

* `mikejs <http://github.com/mikejs>`_
* `certik <http://github.com/certik>`_
* `davvid <http://github.com/davvid>`_
* `winhamwr <http://github.com/winhamwr>`_
* `johnpaulett <http://github.com/johnpaulett>`_
* `boothead <http://github.com/boothead>`_
* `kennethreitz <https://github.com/kennethreitz>`_
* `acdha <https://github.com/acdha>`_
* `garbados <http://github.com/garbados>`_

For their contributions, which are beginning to outweigh mine, to Georg Brandl
for `Sphinx <http://sphinx.pocoo.org/>`_ and the github crew for the pages
functionality.


