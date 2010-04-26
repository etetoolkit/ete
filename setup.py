#! /usr/bin/env python

# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
import sys
import ez_setup

try:
    from setuptools import setup, find_packages
except ImportError:
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

python_dependencies = [
    ["numpy", "Numpy is required for the ArrayTable and ClusterTree classes.", 0],
    ["scipy", "Scipy is only required for the clustering validation functions.", 0],
    ["MySQLdb", "MySQLdb is required for the PhylomeDB access API.", 0],
    ["PyQt4", "PyQt4 is required for tree visualization and rendering.", 0]
]

DESCRIPTION="""ETE is a python programming toolkit that assists in the automated
manipulation, analysis and visualization of hierarchical
trees. Besides a broad set of tree handling options, ETE provides
specific methods to work on phylogenetics and clustering analyses. ETE
supports large tree data structures, node annotation, topology
manipulation and provides a highly customizable visualization
framework."""

TAGS = [
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
    if mname=="PyQt4":
        try:
            __import__("PyQt4.QtCore")
            __import__("PyQt4.QtGui")
        except ImportError:
            try:
                __import__("QtCore")
                __import__("QtGui")
            except ImportError:
                return None
        else:
            return True
    else:
        try:
            __import__(mname)
        except ImportError:
            return None
        else:
            return True

def ask(string,valid_values,default=-1,case_sensitive=False):
    """ Asks for a keyborad answer """
    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        v = raw_input("%s [%s]" % (string,','.join(valid_values)))
        if v == '' and default>=0:
            v = valid_values[default]
        if not case_sensitive:
            v = v.lower()
    return v

print
print "Installing ETE (A python Environment for Tree Exploration)."
print
print "Checking dependencies..."
missing = False
for mname, msg, ex in python_dependencies:
    if not can_import(mname):
        print mname, "cannot be found in your python installation."
        print msg
        missing=True
if missing:
    print "\nHowever, you can still install ETE without such funtionalites."
    con = ask( "Do you want to continue with the installation?", ["y", "n"])
    if con == "n":
        sys.exit()

# SETUP
setup(
    name = "ete2",
    version = open("VERSION").readline().strip(),
    packages = find_packages(),

    requires = [],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        ],

    package_data = {
    },
    # metadata for upload to PyPI
    author = "Jaime Huerta-Cepas",
    author_email = "jhcepas@gmail.com",
    maintainer = "Jaime Huerta-Cepas",
    maintainer_email = "jhcepas@gmail.com",
    platforms = "OS Independent",
    license = "GPLv3",
    description = "A python Environment for Tree Exploration",
    long_description = DESCRIPTION.replace("\n", " "),
    classifiers = TAGS,
    provides = ['ete2'],
    keywords = "bioinformatics phylogeny evolution phylogenomics genomics tree clustering phylogenetics phylogenetic ete orthology paralogy",
    url = "http://ete.cgenomics.org",
    download_url = "http://ete.cgenomics.org/releases/ete2/",
)
