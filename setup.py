import ez_setup
from setuptools import setup, find_packages
ez_setup.use_setuptools()

python_dependencies = [
    ["numpy", "Error", 0],
    ["scipy", "Error", 0],
    ["stats", "Error", 0],
    ["MySQLdb", "Error", 0]
]

def can_import(mname):
    try:
	return __import__(mname)
    except:
	return None

print "ETE (The python Environment for Tree Exploration)."
for mname, msg, ex in python_dependencies:
    if not can_import(mname):
	print msg, mname, "cannot be imported."


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
    description = "Python Comparative Genomics Tools (ETE Package)",
    license = "GPLv2",
    keywords = "bioinformatics phylogeny phylogenomics genomics ete tree clustering phylogenetics",
    url = "http://ete.cgenomics.org",   # project home page, if any


)


