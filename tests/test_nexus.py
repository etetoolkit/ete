"""
Tests related to the nexus module.
"""

# Here you can find more information on the nexus format and examples:
#   https://en.wikipedia.org/wiki/Nexus_file
#   http://wiki.christophchamp.com/index.php?title=NEXUS_file_format
#   http://hydrodictyon.eeb.uconn.edu/eebedia/index.php/Phylogenetics:_NEXUS_Format

from tempfile import TemporaryFile
import unittest

from ete4 import Tree
from ete4.parser import nexus


class TestNexus(unittest.TestCase):

    def test_loads(self):
        with TemporaryFile(mode='w+t') as fp:
            fp.write("""#NEXUS
BEGIN TAXA;
    TaxLabels Scarabaeus Drosophila Aranaeus;
END;

BEGIN TREES;
    Translate beetle Scarabaeus, fly Drosophila, spider Aranaeus;
    Tree tree1 = ((1,2),3);
    Tree tree2 = ((beetle,fly),spider);
    Tree tree3 = ((Scarabaeus,Drosophila),Aranaeus);
END;
            """)
            fp.seek(0)

            trees = nexus.load(fp)

            newicks = {name: t.write() for name, t in trees.items()}

            assert newicks == {
                'tree1': '((1,2),3);',
                'tree2': '((Scarabaeus,Drosophila),Aranaeus);',
                'tree3': '((Scarabaeus,Drosophila),Aranaeus);'}


    def test_loads_bad_file(self):
        def read_bad_file():
            with TemporaryFile(mode='w+t') as fp:
                fp.write("""not a nexus file

                anything.""")
                fp.seek(0)

                nexus.load(fp)

            self.assertRaises(nexus.NexusError, read_bad_file)


    def test_get_trees(self):
        text = """#nexus
begin trees;
  translate
    1 Ephedra,
    2 Gnetum,
    3 Welwitschia,
    4 Ginkgo,
    5 Pinus
  ;
  tree one = [&U] (1,2,(3,(4,5)));
  tree two = [&U] (1,3,(5,(2,4)));
end;
    """

        trees = nexus.get_trees(text)

        assert trees == {
            'one': '(Ephedra,Gnetum,(Welwitschia,(Ginkgo,Pinus)));',
            'two': '(Ephedra,Welwitschia,(Pinus,(Gnetum,Ginkgo)));'}

    def test_loads_without_trees(self):
        with TemporaryFile(mode='w+t') as fp:
            fp.write("""#NEXUS
    BEGIN TAXA;
        TaxLabels Scarabaeus Drosophila Aranaeus;
    END;

    BEGIN TREES;
    END;
            """)
            fp.seek(0)

            trees = nexus.load(fp)
            assert trees == {}


        with TemporaryFile(mode='w+t') as fp:
            fp.write("""#NEXUS
    BEGIN TAXA;
        TaxLabels Scarabaeus Drosophila Aranaeus;
    END;
            """)
            fp.seek(0)

            trees = nexus.load(fp)
            assert trees == {}
