from setuptools import setup

from glob import glob
from os.path import isfile

from Cython.Build import cythonize


setup(
    name='ete4',
    packages=['ete4',
              'ete4/core',
              'ete4/parser',
              'ete4/treematcher',
              'ete4/phylo',
              'ete4/phyloxml',
              'ete4/gtdb_taxonomy',
              'ete4/ncbi_taxonomy',
              'ete4/tools',
              'ete4/evol',
              'ete4/evol/parser',
              'ete4/orthoxml',
              'ete4/smartview',
              'ete4/treeview'],
    ext_modules=cythonize(
        glob('**/*.pyx', recursive=True),
        language_level=3,  # so it compiles for python3 (and not python2)
        compiler_directives={'embedsignature': True}),  # for call signatures
    data_files=[
        ('share/ete4/static',
         [x for x in glob('ete4/smartview/static/**',
                          recursive=True) if isfile(x)])],
)
