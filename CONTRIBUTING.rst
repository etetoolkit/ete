Contributing to ETE
===================

Pull requests and development workflow
-----------------------------------------

Official versioned releases are done via conda and pypi. However, the master
branch at GitHub is also expected to stable and receives more frequent additions
and fixes.

All development should occur in feature specific git branches or forks from
master. Pull requests to master are merged after reviewing changes and
confirming that all tests are passed.

If you start working on a new feature or a fix, consider letting others know
(i.e. opening a updating GitHub issues).


Bugs and Feature Requests
---------------------------

The preferred way to report a problem or request/disccuss new features is by
opening a new issue at http://github.com/jhcepas/ete/issues. (Please check for
duplicate reports).

  There is also chat room for developers:

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/jhcepas/ete
   :target: https://gitter.im/jhcepas/ete?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge 


Running tests
---------------------------------

In order to run the tests, first clone ete::

    git clone https://github.com/jhcepas/ete

then while having a ``virtualenv`` active or while using some other python container run::

    pip install -e ete/

If this finished without errors you can install the necessary tools using::

    ete3 build install_tools

And again if everything finished without errors, tests can finally be executed with::

    python -m ete3.test.test_all


Coverage report
---------------

In addition to the test execution above, if you wish to calculate test coverage, first install ``coverage``::

    pip install coverage

and then run::

    coverage run -m ete3.test.test_all

If in addition you want a pretty html report of test coverage run::

    coverage html

and use a web-browser to open ``htmlcov/index.html``.
