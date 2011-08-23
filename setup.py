#! /usr/bin/env python

import sys
import ez_setup

try:
    from setuptools import setup, find_packages
except ImportError:
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

#    ["scipy", "Scipy is only required for the clustering validation functions.", 0],
python_dependencies = [
    ["numpy", "Numpy is required for the ArrayTable and ClusterTree classes.", 0],
    ["MySQLdb", "MySQLdb is required for the PhylomeDB access API.", 0],
    ["PyQt4", "PyQt4 is required for tree visualization and rendering.", 0]
]

long_description = open("README").read()

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
                return False
        else:
            return True
    elif mname == "MySQLdb":
        try:
            import MySQLdb
        except ImportError:
            return False
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

ete_version = open("VERSION").readline().strip()
mod_name = ete_version.split("rev")[0]

setup(
    name = mod_name,
    version = ete_version,
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
    provides = [mod_name],
    keywords = "bioinformatics phylogeny evolution phylogenomics genomics tree clustering phylogenetics phylogenetic ete orthology paralogy",
    url = "http://ete.cgenomics.org",
    download_url = "http://ete.cgenomics.org/releases/ete2/",
)
