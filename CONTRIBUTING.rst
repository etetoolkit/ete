Contributing to ETE
===================

Development status
------------------

Current stable version is ETE v2.3, which supports Python 2 only. Source code is in
the following branch: https://github.com/jhcepas/ete/tree/2.3

ETE v3.0 is the development branch and should support Python 2.7 and Python
3.4. Although it is mostly functional, this version is currently under active
development. Problems are still expected. The module name for ETE v3.0 has
changed form "ete2" to "ete3". Both versions (ETE v2.3 and ETE v3.0) can co-exist.

BUGs and Feature Request
------------------------

The preferred way to report a problem or request/disccuss new features is by
opening a new issue at http://github.com/jhcepas/ete/issues.  (Please, make sure
there is no other issues pointing to the same topic)


Pull Requests (either code or documentation)
--------------------------------------------

Contributions to the main code, unit-tests and documentation are very
welcome. ETE's main source code is hosted at http://github.com/jhcepas/ete.
There are currently 2 active branches:

- "2.3" is the latest stable. Only bug fixes are accepted.
- "master" is the development branch, focused on the upcoming version
  3.0. Bug fixes, new features, tests and documentation are accepted and highly
  appreciated.
  
**contact info**

- There is no mailing list for developers, but you can open a new github issue for
  discussion or send an email directly to jhcepas [at] gmail.com.
  
- There is also chat room for developers:

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/jhcepas/ete
   :target: https://gitter.im/jhcepas/ete?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge 


Running tests (development version)
-----------------------------------

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
