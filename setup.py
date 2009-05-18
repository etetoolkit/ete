import ez_setup

ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "ete2",
    version = open("VERSION").readline(),
    packages = find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
	],

    package_data = {
    },
    # metadata for upload to PyPI
    author = "Jaime Huerta-Cepas",
    author_email = "jhcepas@gmail.com",
    description = "Python Comparative Genomics Tools",
    license = "GPLv2",
    keywords = "bioinformatics phylogeny phylogenomics genomics ete",
    url = "http://ete.cgenomics.org",   # project home page, if any
)
