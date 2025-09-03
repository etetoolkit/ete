Development
===========

Repositories
------------

We have several repositories for ETE, all in https://github.com/etetoolkit/:

- `ete <https://github.com/etetoolkit/ete/>`_ - Our main repository.
- `ete-data <https://github.com/etetoolkit/ete-data>`_ - Useful but
  big data files, like some example files and the GTDB taxonomy data
  among others.
- `ete-gallery <https://github.com/etetoolkit/ete-gallery>`_ -
  Demonstrations of the graphical capabilities, including tutorials,
  example programs and course notes.

In the future, we consider moving them to `Codeberg
<https://codeberg.org/>`_.


Releases
--------

Before a new release, we make sure that all the tests pass
(``./run_tests.py --include-interactive --include-slow``), decide on
the appropriate version number, and update:

- ``pyproject.toml``
- ``VERSION``
- ``ete4/version.py``

After this update, we make a last commit ("Change to version
``$version``."). And then we tag it:

.. code:: bash

  $ git tag -a $version  # with the appropriate value of $version
  $ git push origin $version

We then make sure that the new version is available in `PyPI
<https://pypi.org/project/ete4/>`_, `GitHub
<https://github.com/etetoolkit/ete/releases>`_, and
`Conda <https://anaconda.org/conda-forge/ete4>`_.


PyPI
~~~~

The Python Package Index (PyPI) is the main repository of software for
Python. ETE 4 has its releases at https://pypi.org/project/ete4/.

The creation of a new release for PyPI is automatically triggered when
we upload a new tag to the repository. This happens according to the
`workflow
<https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows>`_
at ``.github/workflows/publish-to-test-pypi.yml`` (which we originally
wrote following `a publishing guide from python.org
<https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>`_).

Once the latest release appears in PyPI, anyone can install it with:

.. code:: bash

  $ pip install ete4


GitHub
~~~~~~

Our releases are at https://github.com/etetoolkit/ete/releases.

To create a new release, we go to
https://github.com/etetoolkit/ete/releases/new and select the tag we
just created.

The release title we use is simply the new version number, and a
possible (lazy) description can be:

.. code:: null

  Also available in PyPI: https://pypi.org/project/ete4/

  The updated documentation can be found at https://etetoolkit.github.io/ete/

  **Full Changelog since previous release**: https://github.com/etetoolkit/ete/compare/$old_version...$version


Conda
~~~~~

Anaconda.org/conda-forge is a community-led collection of packages and
more, for the `conda package manager
<https://en.wikipedia.org/wiki/Conda_(package_manager)>`_ .

Our releases are at https://anaconda.org/conda-forge/ete4, but someone
is making them for us, and we don't know who but they seem to be
quickly updated. Thank you!

To use the release from conda-forge:

.. code:: bash

  $ conda install conda-forge::ete4


.. TODO: Maybe add section on coding conventions.
