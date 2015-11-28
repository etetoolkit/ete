#! /usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import ez_setup
import hashlib
import time, random
import re
try:
    from urllib2 import quote
    from urllib2 import urlopen
    from urllib2 import HTTPError
except ImportError:
    from urllib.parse import quote
    from urllib.request import urlopen
    from urllib.error import HTTPError

HERE = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])

if "--donottrackinstall" in sys.argv:
    TRACKINSTALL = None
    sys.argv.remove("--donottrackinstall")
else:
    # Avoids importing self module
    orig_path = list(sys.path)
    _wd = os.getcwd()
    try:
        sys.path.remove(_wd)
    except ValueError:
        pass
    try:
        sys.path.remove("")
    except ValueError:
        pass

    # Is this and upgrade or a new install?
    try:
        import ete3
    except ImportError:
        TRACKINSTALL = "ete-new-installation"
    else:
        TRACKINSTALL = "ete-upgrade"

    sys.path = orig_path


try:
    from setuptools import setup, find_packages
except ImportError:
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages


PYTHON_DEPENDENCIES = [
    ["numpy", "Numpy is required for the ArrayTable and ClusterTree classes.", 0],
    ["PyQt4", "PyQt4 is required for tree visualization and image rendering.", 0],
    ["lxml", "lxml is required from Nexml and Phyloxml support.", 0]
]

CLASSIFIERS= [
    "Development Status :: 6 - Mature",
    "Environment :: Console",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: Developers",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]

def can_import(mname):
    'Test if a module can be imported '
    if mname == "PyQt4":
        try:
            __import__("PyQt4.QtCore")
            __import__("PyQt4.QtGui")
        except ImportError:
            return False
        else:
            return True
    else:
        try:
            __import__(mname)
        except ImportError:
            return False
        else:
            return True

try:
    ETE_VERSION = open(os.path.join(HERE, "VERSION")).readline().strip()
except IOError:
    ETE_VERSION = 'unknown'

print("\nInstalling ETE (%s) \n" %ETE_VERSION)
print()


    
MOD_NAME = "ete3"

LONG_DESCRIPTION="""
The Environment for Tree Exploration (ETE) is a Python programming
toolkit that assists in the recontruction, manipulation, analysis and
visualization of phylogenetic trees (although clustering trees or any
other tree-like data structure are also supported).

ETE is currently developed as a tool for researchers working in
phylogenetics and genomics. If you use ETE for a published work,
please cite:

::

  Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon. ETE: a python
  Environment for Tree Exploration. BMC Bioinformatics 2010, 11:24.

Visit http://etetoolkit.org for more info.
"""

try:
    _s = setup(
        include_package_data = True,

        name = MOD_NAME,
        version = ETE_VERSION,
        packages = find_packages(),

        entry_points = {"console_scripts":
                        ["ete3 = %s.tools.ete:main" %MOD_NAME]},
        requires = ["six"],

        # Project uses reStructuredText, so ensure that the docutils get
        # installed or upgraded on the target machine
        install_requires = [
            ],
        package_data = {

        },
        data_files = [("%s/tools" %MOD_NAME, ["%s/tools/phylobuild.cfg" %MOD_NAME])],

        # metadata for upload to PyPI
        author = "Jaime Huerta-Cepas",
        author_email = "jhcepas@gmail.com",
        maintainer = "Jaime Huerta-Cepas",
        maintainer_email = "huerta@embl.de",
        platforms = "OS Independent",
        license = "GPLv3",
        description = "A Python Environment for (phylogenetic) Tree Exploration",
        long_description = LONG_DESCRIPTION,
        classifiers = CLASSIFIERS,
        provides = [MOD_NAME],
        keywords = "tree, tree reconstruction, tree visualization, tree comparison, phylogeny, phylogenetics, phylogenomics",
        url = "http://etetoolkit.org",
        download_url = "http://etetoolkit.org/static/releases/ete3/",

    )

except:
    print("\033[91m - Errors found! - \033[0m")
    raise

else:

    print("\033[92m - Done! - \033[0m")
    missing = False
    for mname, msg, ex in PYTHON_DEPENDENCIES:
        if not can_import(mname):
            print(" Warning:\033[93m Optional library [%s] could not be found \033[0m" %mname)
            print("  ",msg)
            missing=True

    notwanted = set(["-h", "--help", "-n", "--dry-run"])
    seen = set(_s.script_args)
    wanted = set(["install", "bdist", "bdist_egg"])
    if TRACKINSTALL is not None and (wanted & seen) and not (notwanted & seen):
        try:
            welcome = quote("New alien in earth! (%s %s)" %(TRACKINSTALL, time.ctime()))
            urlopen("http://etetoolkit.org/static/et_phone_home.php?ID=%s&VERSION=%s&MSG=%s"
                            %(TRACKINSTALL, ETE_VERSION, welcome))
        except Exception:
            pass
