Jirafs-Pandoc
=============

Automatically converts supported markup into either HTML or a PDF
when uploading to JIRA.

Requirements
------------

* HTML Output: Pandoc.
* PDF Output: Pandoc and xelatex.

Installation
------------

1. Install from PIP::

    pip install jirafs-pandoc

2. Enable for a ticket folder::

    jirafs config --set plugins.pandoc on

Note that you can globally enable this (or any) plugin by adding the
``--global`` flag to the above command::

    jirafs config --global --set plugins.pandoc on

Supported Formats and Extensions
--------------------------------

* ``extra``

  * ``*.text``
  * ``*.txt``

* ``html``

  * ``*.html``
  * ``*.htm``

* ``json``

  * ``*.json``

* ``latex``

  * ``*.latex``
  * ``*.tex``
  * ``*.ltx``

* ``markdown``

  * ``*.markdown``
  * ``*.mkd``
  * ``*.md``
  * ``*.pandoc``
  * ``*.pdk``
  * ``*.pd``
  * ``*.pdc``

* ``native``

  * ``*.hs``

* ``rst``

  * ``*.rst``

* ``textile``

  * ``*.textile``

Optional Configuration
----------------------

By default, all supported files will be converted into PDF files, but
you can convert to HTML instead by setting the
``pandoc.output_format`` setting::

    jirafs config --set pandoc.output_format html

Additionally, you can limit which files will be transformed on a format
or extension basis.

To limit to only specific extensions, set the
``pandoc.enabled_input_extensions`` setting; for example, to only transform
reStructuredText and textile documents into PDFs, you would run::

    jirafs config --set pandoc.enabled_input_extensions rst,textile

To limit to only specific formats, set the
``pandoc.enabled_input_formats`` setting.  To limit to transforming only
markdown and latex documents, you could run::

    jirafs config --set pandoc.enabled_input_formats markdown,latex
