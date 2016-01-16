from __future__ import absolute_import
from __future__ import print_function

import sys
import os
from argparse import ArgumentParser

from os.path import join as pjoin
from os.path import split as psplit
from os.path import exists as pexist

from six.moves import input

from .utils import colorify

import tarfile
try:
    from urllib import urlretrieve
except ImportError:
    # python 3
    from urllib.request import urlretrieve

def _main():
    parser = ArgumentParser()
    parser.add_argument("-v", dest="verbose", action="store_true")
    parser.add_argument("--debug", dest="debug", action="store_true")
    parser.add_argument("--dir", dest='directory', type=str, default='')
    parser.add_argument("--cpu", dest='cores', type=int, default=1)
    parser.add_argument(dest="targets", nargs="*")    
    args = parser.parse_args()
    APPSPATH = os.path.expanduser("~/.etetoolkit/ext_apps-latest/")
    ETEHOMEDIR = os.path.expanduser("~/.etetoolkit/")

    if pexist(pjoin('/etc/etetoolkit/', 'ext_apps-latest')):
        # if a copy of apps is part of the ete distro, use if by default
        APPSPATH = pjoin('/etc/etetoolkit/', 'ext_apps-latest')
        ETEHOMEDIR = '/etc/etetoolkit/'
    else:
        # if not, try a user local copy
        APPSPATH = pjoin(ETEHOMEDIR, 'ext_apps-latest')

    
    TARGET_DIR = args.directory
    
    while not pexist(TARGET_DIR):
        TARGET_DIR = input('target directory? [%s]:' %ETEHOMEDIR).strip()
        if TARGET_DIR == '':
            TARGET_DIR = ETEHOMEDIR
            break

    if TARGET_DIR == ETEHOMEDIR:
        try:
            os.mkdir(ETEHOMEDIR)
        except OSError:
            pass

    version_file = "latest.tar.gz"
    print (colorify('Downloading latest version of tools...', "green"), file=sys.stderr)
    sys.stderr.flush()

    urlretrieve("https://github.com/jhcepas/ext_apps/archive/%s" %version_file, pjoin(TARGET_DIR, version_file))
    print(colorify('Decompressing...', "green"), file=sys.stderr)
    tfile = tarfile.open(pjoin(TARGET_DIR, version_file), 'r:gz')
    tfile.extractall(TARGET_DIR)
    print(colorify('Compiling tools...', "green"), file=sys.stderr)
    sys.path.insert(0, pjoin(TARGET_DIR, 'ext_apps-latest'))
    import compile_all
    errors = compile_all.compile_all(targets=args.targets, verbose=args.verbose, cores=args.cores)

