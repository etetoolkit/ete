#!/usr/bin/env python3

from setuptools import setup
from glob import glob
from Cython.Build import cythonize

setup(
    name='ete4',
    packages=['ete4'],
    ext_modules=cythonize([
        'ete4/coretype/tree.pyx',
        'ete4/parser/newick.pyx',
        'ete4/smartview/renderer/gardening.pyx',
        'ete4/smartview/renderer/face_positions.pyx'], language_level='3'),
    data_files=[
        ('examples', glob('examples/*.tree'))]
)
