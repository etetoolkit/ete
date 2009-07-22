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
from setuptools import setup, find_packages
ez_setup.use_setuptools()

python_dependencies = [
    ["numpy", "Numpy is required for the ArrayTable class among others", 0],
    ["scipy", "Scipy is required for the ArrayTable class among others", 0],
    ["MySQLdb", "MySQLdb is required for the PhylomeDB access API", 0],
    ["PyQt4", "PyQt4 is required for tree visualization", 0]
]

def can_import(mname):
    try:
	return __import__(mname)
    except:
	return None

def ask(string,valid_values,default=-1,case_sensitive=False):
    """ Asks for a keyborad answer """
    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        v = raw_input("%s [%s]" % (string,l2s(valid_values,sep=",") ))
        if v == '' and default>=0:
            v = valid_values[default]
        if not case_sensitive:
            v = v.lower()
    return v



print "ETE (The python Environment for Tree Exploration)."
print "Checking dependencies..."
for mname, msg, ex in python_dependencies:
    if not can_import(mname):
	print mname, "cannot be imported."
	print msg
	con = ask( "Do you want to continue with the installation?", ["y", "n"])
	if con == "n":
	    sys.exit()


# SETUP
setup(
    name = "ete2",
    version = open("VERSION").readline(),
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
    description = "A python Environment for Tree Exploration",
    license = "GPLv3",
    keywords = "bioinformatics phylogeny phylogenomics genomics ete tree clustering phylogenetics",
    url = "http://ete.cgenomics.org",   # project home page, if any
)


