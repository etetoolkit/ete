from __future__ import absolute_import
from __future__ import print_function
import unittest
import os
import time
from .. import nexml, phyloxml

ETEPATH = os.path.abspath(os.path.split(os.path.realpath(__file__))[0]+'/../../')

class Test_PhyloXML(unittest.TestCase):
    def test_phyloxml_parser(self):
        path = os.path.join(ETEPATH, "examples/phyloxml/")
        for fname in os.listdir(path):
            if fname.endswith(".xml"):
                W = open("/tmp/test_xml_parser", "w")
                print(fname, "...", end=' ')
                fpath = os.path.join(path, fname)
                p = phyloxml.Phyloxml()
                t1 = time.time()
                p.build_from_file(fpath)
                etime = time.time()-t1
                print("%0.1f secs" %(etime))
                p.export(outfile = W)

    def test_examples(self):
        path = os.path.join(ETEPATH, "examples/phyloxml/")
        for ex in os.listdir(path):
            print("testing", ex)
            if ex.endswith(".py"):
                s = os.system("cd %s && python %s" %(path, ex))
                if s:
                    raise Exception("Example crashed!")



class Test_NeXML(unittest.TestCase):
    def test_nexml_parser(self):
        path = os.path.join(ETEPATH, "examples/nexml/")
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
        path = os.path.join(ETEPATH, "examples/nexml/")
        for ex in os.listdir(path):
            print("testing", ex)
            if ex.endswith(".py"):
                s = os.system("cd %s && python %s" %(path, ex))
                if s:
                    raise Exception("Example crashed!")



if __name__ == '__main__':
    unittest.main()
