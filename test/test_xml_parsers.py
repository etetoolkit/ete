from __future__ import print_function
import unittest
import os
import time
from ete_dev import nexml, phyloxml
import sys

ETEPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0]+'/../')

# Fix path for 2to3 builds
if ETEPATH.endswith('build/lib'):
    ETEPATH = ETEPATH.replace('build/lib', '')
EXAMPLE_DIR = os.path.join(ETEPATH, 'examples')

# Determine python version to use
PYTHON_BIN = "python%d" % sys.version_info.major

class Test_PhyloXML(unittest.TestCase):
    def test_phyloxml_parser(self):
        path = os.path.join(EXAMPLE_DIR, 'phyloxml')
        for fname in os.listdir(path):
            if fname.endswith(".xml"):
                W = open("/tmp/test_xml_parser", "wb")
                print(fname, "...", end=' ') 
                fpath = os.path.join(path, fname)
                p = phyloxml.Phyloxml()
                t1 = time.time()
                p.build_from_file(fpath)
                etime = time.time()-t1
                print("%0.1f secs" %(etime))
                p.export(outfile = W)

    def test_examples(self):
        path = os.path.join(EXAMPLE_DIR, 'phyloxml')
        for ex in os.listdir(path):
            print("testing", ex) 
            if ex.endswith(".py"):
                s = os.system("cd %s && %s %s" %(path, PYTHON_BIN, ex))
                if s: 
                    raise Exception("Example crashed!")

class Test_NeXML(unittest.TestCase):
    def test_nexml_parser(self):
        path = os.path.join(EXAMPLE_DIR, 'nexml')
        for fname in os.listdir(path):
            if fname.endswith(".xml"):
                W = open("/tmp/test_xml_parser", "w")
                print(fname, "...", end=' ') 
                fpath = os.path.join(path, fname)
                p = nexml.Nexml()
                t1 = time.time()
                p.build_from_file(fpath)
                etime = time.time()-t1
                print("%0.1f secs" %(etime))
                p.export(outfile = W)

    def test_examples(self):
        path = os.path.join(EXAMPLE_DIR, 'nexml')
        for ex in os.listdir(path):
            print("testing", ex) 
            if ex.endswith(".py"):
                s = os.system("cd %s && %s %s" %(path, PYTHON_BIN, ex))
                if s: 
                    raise Exception("Example crashed!")

if __name__ == '__main__':
    unittest.main()
