#! /usr/bin/env python
import sys
import os
import ez_setup
import hashlib 
import time, random
import re
import urllib2

try:
    from setuptools import setup, find_packages
except ImportError:
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

# Generates a unique id for ete installation. If this is an upgrade,
# use the previous id. ETEID is only used to get basic statistics
# about number of users/installations. The id generated is just a
# random unique text string. This installation script does not collect
# any personal information about you or your system.
ETEID = None
try:
    # Avoids importing a previously generated id
    _wd = os.getcwd()
    try:
        sys.path.remove(_wd)
    except ValueError:
        _fix_path = False
        pass
    else:
        _fix_path = True

    # Is there a previous ETE installation? If so, use the same id
    from ete2 import __ETEID__ as ETEID

    if _fix_path:
        sys.path.insert(0, _wd)
except ImportError:
    ETEID = None
    
if not ETEID:
    ETEID = hashlib.md5(str(time.time()+random.random())).hexdigest()

PYTHON_DEPENDENCIES = [
    ["numpy", "Numpy is required for the ArrayTable and ClusterTree classes.", 0],
#    ["MySQLdb", "MySQLdb only is required by the PhylomeDB access API.", 0],        #  Only PhylomeDB requires it is now deprecated
    ["PyQt4", "PyQt4 is required for tree visualization and image rendering.", 0],
    ["lxml", "lxml is required from Nexml and Phyloxml support.", 0]
]

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
    'Test if a module can be imported '
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

print
print "Installing ETE (A python Environment for Tree Exploration)."
print

print "Checking dependencies..."
missing = False
for mname, msg, ex in PYTHON_DEPENDENCIES:
    if not can_import(mname):
        
        print "WARNING:\033[93m Optional library [%s] could not be found \033[0m" %mname
        print "  ",msg
        missing=True

# writes installation id as a variable into the main module
init_content = open("ete2/__init__.py").read()
init_content = re.sub('__ETEID__="[\w\d]*"', '__ETEID__="%s"'
                      %ETEID, init_content)
open("ete2/__init__.py", "w").write(init_content)

print "Your installation ID is:", ETEID

ete_version = open("VERSION").readline().strip()
revision = ete_version.split("rev")[-1]
mod_name = "ete2"

long_description = open("README").read()
long_description += open("INSTALL").read()
long_description.replace("ete2", mod_name)

try:
    _s = setup(
        name = "ete2",
        version = ete_version,
        packages = find_packages(),

        entry_points = {"console_scripts":
                        ["ete = ete2.tools.ete:main"]}, 
        requires = [],
        
        # Project uses reStructuredText, so ensure that the docutils get
        # installed or upgraded on the target machine
        install_requires = [
            ],
        package_data = {
            },
        data_files = [("ete2/tools/", ["ete2/tools/phylobuild.cfg"])], 
        
        
        # metadata for upload to PyPI
        author = "Jaime Huerta-Cepas",
        author_email = "jhcepas@gmail.com",
        maintainer = "Jaime Huerta-Cepas",
        maintainer_email = "jhcepas@gmail.com",
        platforms = "OS Independent",
        license = "GPLv3",
        description = "A python Environment for (phylogenetic) Tree Exploration",
        long_description = long_description,
        classifiers = TAGS,
        provides = ["ete2"],
        keywords = "Tree handling, manipulation, analysis and visualization",
        url = "http://etetoolkit.org",
        download_url = "http://etetoolkit.org/static/releases/ete2/",
    )
except: 
    raise
else:
    notwanted = set(["-h", "--help", "-n", "--dry-run"])
    seen = set(_s.script_args)
    wanted = set(["install", "bdist", "bdist_egg"])
    if (wanted & seen) and not (notwanted & seen):
        try:
            welcome = urllib2.quote("New alien in earth!")
            urllib2.urlopen("http://etetoolkit.org/static/et_phone_home.php?ID=%s&VERSION=%s&MSG=%s"
                            %(ETEID, ete_version, welcome))
        except urllib2.HTTPError, e: 
            pass
