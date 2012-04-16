Download and Install
**********************

.. contents:: 

GNU/Linux 
===========

ETE requires python>=2.5 (python 3 is not supported) as well as several
dependencies (required only to enable particular functions, but highly
recommended):

- python-qt4 (>=4.5) [Enables tree visualization and image rendering]
- python-mysqldb (>=1.2) [Enables programmatic access to PhylomeDB]
- python-numpy (Required to work with clustering trees)
- python-lxml [Required to work whit NexML and PhyloXML phylogenetic formats]
- python-setuptools [Optional. Allows to install and upgrade ETE]


Meeting dependencies (Debian based distributions)
------------------------------------------------------

ETE is developed and tested under Debian based distributions
(i.e. Ubuntu). All the above mentioned dependencies are in the
official repositories of Debian and can be installed using a package
manager such as APT, Synaptics or Adept. For instance, in Ubuntu you
can use the following shell command to install all dependencies:

:: 

  $ apt-get install python-setuptools python-numpy python-qt4 python-scipy python-mysqldb python-lxml


Meeting dependencies (other GNU/Linux distributions)
------------------------------------------------------

In Non Debian based distributions, dependencies may not be necessarily
found in their official repositories. If this occurs, libraries should
be downloaded separately or installed from third part repositories. In
general, this process should not entail important difficulties, except
for PyQt4, which is a python binding to the new Qt4 libraries. Some
distributions (i.e. CentOS, Fefora) do not include recent packages and
cross-dependencies for such libraries yet. In such cases, manual
compilation of libraries could be required.

 
Installing or Upgrading ETE
--------------------------------

Easy Install is the best way to install ETE and keep it up to
date. EasyInstall is a python module bundled with setuptools that lets
you automatically download, build, install, and manage Python
packages. If the easy_install command is available in your system, you
can execute this shell command to install/update ETE.

:: 

  $ easy_install -U ete2

Alternatively, you can download the last version of ETE from
http://pypi.python.org/pypi/ete2/, decompress the file and install the
package by executing the setup installer:

::

  $ python setup.py install 
 
MacOS
=======

ETE and all its dependencies are supported by MacOS Intel
environments, however you will need to install some libraries from the
external GNU/open-source repositories. This can be done easily by
using MacPorts.

The following recipe has been reported to work in MacOS 10.5.8 (thanks to Marco Mariotti and Alexis Grimaldi at the CRG):

  1. Install Mac Developer tools and X11 (required by Macports)
  2. Install Macports in your system: http://www.macports.org/install.php
  3. Install the following packages from the macports repository by using the "sudo port install [package_name]"  syntax (note that some packages may take a long time to be built and that you will need to have an active internet connection during the installation process):
     * python26
     * py26-numpy
     * py26-scipy
     * py26-pyqt4
     * py26-mysql
     * py26-lxml
  4. Download the setup installer of the last ETE version (http://ete.cgenomics.org/releases/ete2), uncompress it, enter its folder and run: "sudo python setup.py install" Once the installation has finished,  you will be able to load ETE (import ete2) when running the "right" python binary.

.. note:: 
   
   If step 4 doesn't work, make sure that the python version your are
   using to install ETE is the one installed by MacPorts. This is
   usually located in
   ``/opt/local/Library/Frameworks/Python.framework/Versions/2.6/bin/python2.6``.
   By contrast, non-Macport python version is the one located in
   ``/Library/Frameworks/Python.framework/Versions/2.6/bin/python2.6``,
   so check that you are using the correct python executable.


Older Versions
================
Older ETE versions can be found at http://ete.cgenomics.org/releases/ete2/
