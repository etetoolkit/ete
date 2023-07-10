from setuptools import setup

from glob import glob
from os.path import isfile

from Cython.Build import cythonize


setup(
    name='ete4',
    packages=['ete4',
              'ete4/clustering',
              'ete4/coretype',
              'ete4/evol',
              'ete4/evol/parser',
              'ete4/gtdb_taxonomy',
              'ete4/ncbi_taxonomy',
              'ete4/nexml',
              'ete4/orthoxml',
              'ete4/parser',
              'ete4/phylo',
              'ete4/phyloxml',
              'ete4/smartview',
              'ete4/smartview/gui',
              'ete4/smartview/renderer',
              'ete4/smartview/renderer/layouts',
              'ete4/tools',
              'ete4/treematcher',
              'ete4/treeview'],
    ext_modules=cythonize([
        'ete4/coretype/tree.pyx',
        'ete4/parser/newick.pyx',
        'ete4/smartview/renderer/gardening.pyx',
        'ete4/smartview/renderer/face_positions.pyx'], language_level='3'),
    data_files=[
        ('share/ete4/static',
         [x for x in glob('ete4/smartview/gui/static/**',
                          recursive=True) if isfile(x)])],
)
