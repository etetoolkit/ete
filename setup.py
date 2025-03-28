from setuptools import setup, Extension

from glob import glob
from os.path import isfile

from Cython.Build import cythonize


def make_extension(path):  # to create cython extensions the way we want
    name = path.replace('/', '.')[:-len('.pyx')]  # / -> .  and remove .pyx
    return Extension(name, [path], extra_compile_args=['-O3'])

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
        [make_extension(path) for path in glob('**/*.pyx', recursive=True)],
        compiler_directives={
            'language_level': '3',  # so it compiles for python3 (not python2)
            'embedsignature': True}),  # for call signatures
    data_files=[
        ('share/ete4/static',
         [x for x in glob('ete4/smartview/static/**',
                          recursive=True) if isfile(x)])],
)
