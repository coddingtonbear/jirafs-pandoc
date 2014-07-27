Jirafs-Pandoc
=============

Automatically converts supported markup into fancy PDF files
(or any other Pandoc-supported format) when uploading to JIRA.

Installation
------------

1. Install from PIP::

    pip install jirafs-pandoc

2. Enable for a ticket folder::

    jirafs plugins --enable=pandoc

Note that you can globally enable this (or any) plugin by adding the
``--global`` flag to the above command::

    jirafs plugins --global --enable=pandoc

Requirements
------------

Depending upon which output format you utilize, your requirements
may vary:

* **PDF Output**: Both pandoc and xelatex are required.
* **Other output formats**: Only pandoc is required.

Supported Input Formats and Extensions
--------------------------------------

* Text Formats (``extra``)

  * ``*.text``
  * ``*.txt``

* HTML (``html``)

  * ``*.html``
  * ``*.htm``

* JSON (pandoc AST) (``json``)

  * ``*.json``

* Latex (``latex``)

  * ``*.latex``
  * ``*.tex``
  * ``*.ltx``

* Markdown (``markdown``)

  * ``*.markdown``
  * ``*.mkd``
  * ``*.md``
  * ``*.pandoc``
  * ``*.pdk``
  * ``*.pd``
  * ``*.pdc``

* Native Pandoc (``native``)

  * ``*.hs``

* reStructuredText (``rst``)

  * ``*.rst``

* Textile (``textile``)

  * ``*.textile``

Supported Output Formats
------------------------

Common output formats include:

* PDF (``pdf``)
* HTML (``html``)
* RTF (``rtf``)

But, you can use any output format supported by Pandoc.  Please check
which formats your version of Pandoc supports by running::

    pandoc --help

Optional Configuration
----------------------

By default, markdown, reStructuredText, latex, and textile files will be
converted into PDF files, but you can convert to HTML (or any other
supported format) instead by setting the ``pandoc.output_format`` setting::

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
