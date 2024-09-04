import sys
import random
import itertools
import json
from tempfile import NamedTemporaryFile
import unittest

from ete4 import Tree, PhyloTree
from ete4.core.tree import TreeError
from ete4.parser.newick import NewickError
from ete4.parser import newick

from . import datasets as ds


def strip(text):
    """Return the given text stripping the empty lines and indentation."""
    # Helps compare tree visualizations.
    indent = min(len(line) - len(line.lstrip())
                 for line in text.splitlines() if line.strip())
    return '\n'.join(line[indent:].rstrip()
        for line in text.splitlines() if line.strip())


class Test_Core_Tree(unittest.TestCase):
    """Test the basic Tree class."""

    def assertLooks(self, tree, text):
        """Assert that tree looks like the given text (as ascii)."""
        self.assertEqual(tree.to_str(compact=True, props=['name']),
                         strip(text))

    def test_read_write_exceptions(self):
        """Test that the right exceptions are risen."""
        def wrong_dist():
            t = Tree()
            t.dist = '1a'

        def wrong_support():
            t = Tree()
            t.support = '1a'

        def wrong_up():
            t = Tree()
            t.up = 'Something'

        def wrong_children():
            t = Tree()
            t.children = 'Something'

        self.assertRaises(ValueError, wrong_dist)
        self.assertRaises(ValueError, wrong_support)
        self.assertRaises(TypeError, wrong_up)
        self.assertRaises(TreeError, wrong_children)

    def test_add_remove_properties(self):
        t = Tree()
        t.add_props(testf1=1, testf2="1", testf3=[1])
        t.add_prop('testf4', set([1]))
        self.assertEqual(t.props["testf1"], 1)
        self.assertEqual(t.props["testf2"], "1")
        self.assertEqual(t.props["testf3"], [1])
        self.assertEqual(t.props["testf4"], set([1]))

        t.del_prop('testf4')
        self.assertTrue('testf4' not in t.props)

    def test_basic_properties(self):
        t = Tree('((a:1,b:2)0.8:3,c:4);')

        self.assertTrue(type(t['a'].dist) == float)
        self.assertTrue(type(t[0].support) == float)

        t[0].support = None
        self.assertTrue('support' not in t[0].props)
        self.assertTrue(t[0].support is None)

        t[0].dist = None
        self.assertTrue('dist' not in t[0].props)
        self.assertTrue(t[0].dist is None)

        a = t['a']
        a.name = None
        self.assertTrue('name' not in a.props)
        self.assertTrue(a.name is None)

        a.name = 5
        self.assertTrue(a.name == '5')

    def test_tree_read_and_write(self):
        """Test newick support."""
        # Read and write newick tree from/to file.
        with NamedTemporaryFile() as f_tree:  # test reading from file
            f_tree.write(ds.nw_full.encode('utf8'))
            f_tree.flush()
            t = Tree(open(f_tree.name))

        self.assertEqual(ds.nw_full, t.write(props=["flag", "mood"]))
        self.assertEqual(ds.nw_topo, t.write(parser=9))
        self.assertEqual(ds.nw_dist, t.write(parser=5))

        with NamedTemporaryFile() as f_writetest:  # test writing to file
            t.write(outfile=f_writetest.name)
            self.assertEqual(Tree(open(f_writetest.name)).write(), t.write())

        # Read and write newick tree from/to string.
        t = Tree(ds.nw_full)

        self.assertEqual(ds.nw_full, t.write(props=["flag", "mood"]))
        self.assertEqual(ds.nw_topo, t.write(parser=9))
        self.assertEqual(ds.nw_dist, t.write(parser=5))

        # Read complex newick.
        t = Tree(ds.nw2_full)
        self.assertEqual(ds.nw2_full, t.write())

        # Read weird topologies.
        t = Tree(ds.nw_simple5)
        self.assertEqual(ds.nw_simple5, t.write(parser=9))

        t = Tree(ds.nw_simple6)
        self.assertEqual(ds.nw_simple6, t.write(parser=9))

        # Read single node trees.
        self.assertEqual(Tree("hello;").write(parser=9, format_root_node=True), "hello;")
        self.assertEqual(Tree("(hello);").write(parser=9), "(hello);")

        # Export root features.
        newick = "(((A[&&NHX:name=A],B[&&NHX:name=B])[&&NHX:name=NoName],C[&&NHX:name=C])[&&NHX:name=I],(D[&&NHX:name=D],F[&&NHX:name=F])[&&NHX:name=J])[&&NHX:name=root];"
        t = Tree(newick)
        self.assertEqual(t.write(parser=9, props=['name'], format_root_node=True), '(((A,B)[&&NHX:name=NoName],C)[&&NHX:name=I],(D,F)[&&NHX:name=J])[&&NHX:name=root];')

        # Export ordered features.
        t = Tree("((A,B),C);")
        expected_nw = "((A,B[&&NHX:0=0:1=1:2=2:3=3:4=4:5=5:6=6:7=7:8=8:9=9:a=a:b=b:c=c:d=d:e=e:f=f:g=g:h=h:i=i:j=j:k=k:l=l:m=m:n=n:o=o:p=p:q=q:r=r:s=s:t=t:u=u:v=v:w=w]),C);"
        features = list("abcdefghijklmnopqrstuvw0123456789")
        random.shuffle(features)
        for letter in features:
            t['B'].add_prop(letter, letter)
        self.assertEqual(expected_nw, t.write(props=None))

    def test_repr(self):
        """Test that the Tree representation looks like we expect."""
        t = Tree()
        r1, r2, r3 = t.__repr__(), repr(t), '%r' % t
        self.assertTrue(r1 == r2 == r3)
        self.assertTrue(r1.startswith('<Tree '))
        self.assertTrue(r1.endswith('>'))
        self.assertTrue(' at 0x' in r1)

    def test_to_str(self):
        """Test that the ascii representation (to use when printing) works."""
        t = Tree('((a,b)x,(c,d)y);', parser=1)

        self.assertEqual(t.to_str(props=['name']), strip("""
               ╭╴a
           ╭╴x╶┤
           │   ╰╴b
        ╴⊗╶┤
           │   ╭╴c
           ╰╴y╶┤
               ╰╴d
        """))
        self.assertEqual(t.to_str(compact=True, show_internal=False, props=['name']), strip("""
         ╭─┬╴a
        ─┤ ╰╴b
         ╰─┬╴c
           ╰╴d
        """))
        self.assertEqual(t.to_str(props=['name'], cascade=True), strip("""
        ⊗
        ├─┐x
        │ ├─╴a
        │ └─╴b
        └─┐y
          ├─╴c
          └─╴d
        """))
        self.assertEqual(t.to_str(props=['dist', 'support']), strip("""
                   ╭╴⊗,⊗
             ╭╴⊗,⊗╶┤
             │     ╰╴⊗,⊗
        ╴⊗,⊗╶┤
             │     ╭╴⊗,⊗
             ╰╴⊗,⊗╶┤
                   ╰╴⊗,⊗
        """))

        t2 = Tree('((a:1,b:2)x:3,(c:4,d:5)y:6);', parser=1)
        self.assertEqual(t2.to_str(props=['dist']), strip("""
                 ╭╴1.0
           ╭╴3.0╶┤
           │     ╰╴2.0
        ╴⊗╶┤
           │     ╭╴4.0
           ╰╴6.0╶┤
                 ╰╴5.0
        """))

        self.assertEqual(t2.to_str(), strip("""
                            ╭╴name=a,dist=1.0
          ╭╴name=x,dist=3.0╶┤
          │                 ╰╴name=b,dist=2.0
        ──┤
          │                 ╭╴name=c,dist=4.0
          ╰╴name=y,dist=6.0╶┤
                            ╰╴name=d,dist=5.0
        """))

    def test_concat_trees(self):
        t1 = Tree('((A, B), C);')
        t2 = Tree('((a, b), c);')

        concat_tree = t1 + t2
        concat_tree.sort_descendants()
        self.assertEqual(concat_tree.write(parser=9), '(((A,B),C),((a,b),c));')

        t3 = PhyloTree('((a, b), c);')

        mixed_types = lambda: t1 + t3
        self.assertRaises(TreeError, mixed_types)

    def test_newick_formats(self):
        """Test different newick subformats."""
        NW_FORMAT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # predefined parsers ("formats")

        # Let's stress a bit
        for i in range(10):
            t = Tree()
            t.populate(4, dist_fn=random.random, support_fn=random.random)
            for n in t.traverse():
                n.name = n.name or 'NoName'
                n.support = n.support or 1
            for f in NW_FORMAT:
                self.assertEqual(t.write(parser=f), Tree(t.write(parser=f),parser=f).write(parser=f))

        # Format 0 = ((H:1,(G:1,F:1)1:1)1:1,I:1)1:1;
        # Format 1 = ((H:1,(G:1,F:1):1):1,I:1):1;
        # Format 2 = ((H:1,(G:1,F:1)1:1)1:1,I:1)1:1;
        # Format 3 = ((H:1,(G:1,F:1)NoName:1)NoName:1,I:1)NoName:1;
        # Format 4 = ((H:1,(G:1,F:1)),I:1);
        # Format 5 = ((H:1,(G:1,F:1):1):1,I:1):1;
        # Format 6 = ((H,(G,F):1):1,I):1;
        # Format 7 = ((H:1,(G:1,F:1)NoName)NoName,I:1)NoName;
        # Format 8 = ((H,(G,F)NoName)NoName,I)NoName;
        # Format 9 = ((H,(G,F)),I);
        # Format 100 = ((,(,)),);

        t = Tree()
        t.populate(50, dist_fn=random.random, support_fn=random.random)
        for n in t.traverse():
            n.name = n.name or 'NoName'
        t.sort_descendants()
        expected_distances = [round(n.dist, 6) for n in t.traverse('postorder') if n.up]
        expected_leaf_distances = [round(n.dist, 6) for n in t]
        expected_internal_distances = [round(n.dist, 6) for n in t.traverse('postorder') if not n.is_leaf and n.up]
        expected_supports = [round(n.support, 6) for n in t.traverse('postorder') if not n.is_leaf and n.up]
        expected_leaf_names = [n.name for n in t]

        # Check that all formats read names correctly
        for f in [0,1,2,3,5,6,7,8,9]:
            t2 = Tree(t.write(parser=f), parser=f)
            t2.sort_descendants()
            observed_names = [n.name for n in t]
            self.assertEqual(observed_names, expected_leaf_names)

        # Check that all formats reading distances, recover original distances
        for f in [0,1,2,3,5]:
            t2 = Tree(t.write(parser=f), parser=f)
            t2.dist, t2.support = 0, 1
            t2.sort_descendants()
            observed_distances = [n.dist for n in t2.traverse('postorder')]
            self.assertTrue(all(abs(x - y) < 1e-6 for x, y in zip(observed_distances, expected_distances)))

        # formats reading only leaf distances
        for f in [4,7]:
            t2 = Tree(t.write(parser=f), parser=f)
            t2.dist, t2.support = 0, 1
            t2.sort_descendants()
            observed_distances = [n.dist for n in t2]
            self.assertTrue(all(abs(x - y) < 1e-6 for x, y in zip(observed_distances, expected_leaf_distances)))

        # formats reading only leaf distances
        for f in [6]:
            t2 = Tree(t.write(parser=f), parser=f)
            t2.dist, t2.support = 0, 1
            t2.sort_descendants()
            observed_distances = [n.dist for n in t2.traverse('postorder') if not n.is_leaf]
            self.assertTrue(all(abs(x - y) < 1e-6 for x, y in zip(observed_distances, expected_internal_distances)))


        # Check that all formats reading supports, recover original distances
        for f in [0,2]:
            t2 = Tree(t.write(parser=f), parser=f)
            t2.dist, t2.support = 0, 1
            t2.sort_descendants()
            observed_supports = [n.support for n in t2.traverse('postorder') if not n.is_leaf]
            self.assertTrue(all(abs(x - y) < 1e-6 for x, y in zip(observed_supports, expected_supports)))


       # Check that formats reading supports, do not accept node names
        for f in [0,2]:
            # format 3 forces dumping internal node names, NoName in case is missing
            self.assertRaises(Exception, Tree, t.write(parser=3), parser=f)

       # Check that formats reading names, do not load supports
        for f in [1, 3]:
            t2 = Tree(t.write(parser=0), parser=f)
            default_supports = set([n.support for n in t2.traverse()])
            self.assertEqual({None}, default_supports)


        # Check errors reading numbers
        error_nw1 = "((A:0.813705,(E:0.545591,D:0.411772)error:0.137245)1.000000:0.976306,C:0.074268);"
        for f in [0, 2]:
            self.assertRaises(NewickError, Tree, error_nw1, parser=f)

        error_nw2 = "((A:0.813705,(E:0.545error,D:0.411772)1.0:0.137245)1.000000:0.976306,C:0.074268);"
        for f in [0, 1, 2]:
            self.assertRaises(NewickError, Tree, error_nw2, parser=f)


        error_nw3 = "((A:0.813705,(E:0.545error,D:0.411772)1.0:0.137245)1.000000:0.976306,C:0.074268);"
        for f in [0, 1, 2]:
            self.assertRaises(NewickError, Tree, error_nw2, parser=f)

        # Check errors derived from reading names with weird or illegal chars
        base_nw = "((NAME1:0.813705,(NAME2:0.545,NAME3:0.411772)NAME6:0.137245)NAME5:0.976306,NAME4:0.074268);"
#        valid_names = ['[name]', '[name', '"name"', "'name'", "'name", 'name', '[]\'"&%$!*.']
        valid_names = ['name']
#        error_names = ['error)', '(error', "erro()r",  ":error", "error:", "err:or", ",error",  "error,"]
        error_names = ['error)', "erro()r",  ":error", "error:", "err:or"]
        for ename in error_names:
            self.assertRaises(NewickError, Tree, base_nw.replace('NAME2', ename), parser=1)
            if not ename.startswith(','):
                self.assertRaises(NewickError, Tree, base_nw.replace('NAME6', ename), parser=1)

        for vname in valid_names:
            expected_names = set(['NAME1', vname, 'NAME3', 'NAME4'])
            self.assertEqual(set([n.name for n in Tree(base_nw.replace('NAME2', vname), parser=1)]),
                             expected_names)

        # invalid NHX format
        self.assertRaises(NewickError, Tree, "(((A, B), C)[&&NHX:nameI]);")
        # unsupported newick stream
        self.assertRaises(Exception, Tree, [1,2,3])

    def test_newick_multisupport(self):
        nw = '((a,b)2/3:4,(c,d)5/6:7);'
        t = Tree(nw, parser='multisupport')
        self.assertEqual(t.write(parser='multisupport'), nw)

    def test_quoted_names(self):
        complex_name = "((A:0.0001[&&NHX:hello=true],B:0.011)90:0.01[&&NHX:hello=true],(C:0.01, D:0.001)hello:0.01);"
        # A quoted tree within a tree
        nw1 = '(("A:0.1":1,"%s":2)"C:0.00":3,"D":4);' % complex_name
        nw1_normalized = "(('A:0.1':1,'%s':2)'C:0.00':3,D:4);" % complex_name
        #escaped quotes
        nw2 = '''(("A:\\"0.1\\"":1,"%s":2)"C:'0.00'":3,"D'sd'x":4);''' % complex_name
        nw2_normalized = '''(('A:\\"0.1\\"':1,'%s':2)'C:''0.00''\':3,'D''sd''x':4);''' % complex_name
        for nw, nw_normalized in [(nw1, nw1_normalized), (nw2, nw2_normalized)]:
            self.assertRaises(NewickError, Tree, nw, parser=0)
            t = Tree(nw, parser=1)
            self.assertTrue(any(n for n in t if n.name == '%s' % complex_name))
            # test writing and reloading tree
            nw_back = t.write(parser=1)
            t2 = Tree(nw, parser=1)
            nw_back2 = t2.write(parser=1)
            self.assertEqual(nw_normalized, nw_back)
            self.assertEqual(nw_normalized, nw_back2)

    def test_custom_formatting_formats(self):
        """Test change dist, name and support formatters."""
        t = Tree('((A:1.1111,B:2.2222)C:3.3333[&&NHX:support=1],D:4.4444);',
                 parser=1)
        t.sort_descendants()

        check = [[0, '((TEST-A:1.1,TEST-B:2.2)SUP-1.0:3.3,TEST-D:4.4);'],
                 [1, '((TEST-A:1.1,TEST-B:2.2)TEST-C:3.3,TEST-D:4.4);'],
                 [2, '((TEST-A:1.1,TEST-B:2.2)SUP-1.0:3.3,TEST-D:4.4);'],
                 [3, '((TEST-A:1.1,TEST-B:2.2)TEST-C:3.3,TEST-D:4.4);'],
                 [4, '((TEST-A:1.1,TEST-B:2.2),TEST-D:4.4);'],
                 [5, '((TEST-A:1.1,TEST-B:2.2):3.3,TEST-D:4.4);'],
                 [6, '((TEST-A,TEST-B):3.3,TEST-D);'],
                 [7, '((TEST-A:1.1,TEST-B:2.2)TEST-C,TEST-D:4.4);'],
                 [8, '((TEST-A,TEST-B)TEST-C,TEST-D);'],
                 [9, '((TEST-A,TEST-B),TEST-D);']]

        for f, result in check:
            parser = newick.make_parser(f, dist='%0.1f', name='TEST-%s', support='SUP-%0.1f')
            nw = t.write(parser=parser)
            self.assertEqual(nw, result)

    def test_tree_manipulation(self):
        """Test operations which modify the tree topology."""
        nw_tree = "((Hi:1,Turtle:1.3)1:1,(A:0.3,B:2.4)1:0.43);"

        # Manipulate Topologies
        # Adding and removing nodes (add_child, remove_child,
        # add_sister, remove_sister). The resulting newick tree should
        # match the nw_tree defined before.
        t = Tree()

        remove_child_except = lambda: t.remove_child(t)
        add_sister_except = lambda: t.add_sister()
        self.assertRaises(TreeError, remove_child_except)
        self.assertRaises(TreeError, add_sister_except)


        c1 = t.add_child(dist=1, support=1)
        c2 = t.add_child(dist=0.43, support=1)
        n = Tree({'name': 'Hi', 'dist': 1, 'support': 1})
        _n = c1.add_child(n)
        c3 = _n.add_sister(name="Turtle", dist="1.3")
        c4 = c2.add_child(name="A", dist="0.3")

        c5 = c2.add_child(name="todelete")
        _c5 = c2.remove_child(c5)

        c6 = c2.add_child(name="todelete")
        _c6 = c4.remove_sister()

        c7 = c2.add_child(name="B", dist=2.4)

        self.assertEqual(nw_tree, t.write(parser=0))
        self.assertEqual(_c5, c5)
        self.assertEqual(_c6, c6)
        self.assertEqual(_n, n)

        # Delete,
        t = Tree("(((A, B), C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D = t['D']
        F = t['F']
        J = t['J']
        root = t['root']
        J.delete()
        self.assertEqual(J.up, None)
        self.assertEqual(J in t, False)
        self.assertEqual(D.up, root)
        self.assertEqual(F.up, root)

        # Delete preventing non dicotomic
        t = Tree('((((A:1,B:1):1,C:1):1,D:1):1,E:1):0;')
        orig_dist = t.get_distance(t, 'A')
        C = t['C']
        C.delete(preserve_branch_length=True)
        self.assertEqual(orig_dist, t.get_distance(t, 'A'))

        t = Tree('((((A:1,B:1):1,C:1):1,D:1):1,E:1):0;')
        orig_dist = t.get_distance(t, 'A')
        C = t['C']
        C.delete(preserve_branch_length=False)
        self.assertEqual(orig_dist, t.get_distance(t, 'A')+1)

        t = Tree('((((A:1,B:1):1,C:1):1,D:1):1,E:1):0;')
        orig_dist = t.get_distance(t, 'A')
        C = t['C']
        C.delete(prevent_nondicotomic=False)
        self.assertEqual(orig_dist, t.get_distance(t, 'A'))

        #detach
        t = Tree("(((A, B)[&&NHX:name=H], C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D = t["D"]
        F = t["F"]
        J = t["J"]
        root = t["root"]
        J.detach()
        self.assertEqual(J.up, None)
        self.assertEqual(J in t, False)
        self.assertEqual(set([n.name for n in t.descendants()]),set(["A","B","C","I","H"]))

        # sorting branches
        t1 = Tree('((A,B),(C,D,E,F), (G,H,I));')
        t1.ladderize()
        self.assertEqual(list(t1.leaf_names()), [_ for _ in 'ABGHICDEF'])
        t1.ladderize(reverse=True)
        self.assertEqual(list(t1.leaf_names()), [_ for _ in 'CDEFGHIAB'])
        t1.sort_descendants()
        self.assertEqual(list(t1.leaf_names()), [_ for _ in 'ABCDEFGHI'])

        # prune
        t1 = Tree("(((A, B), C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D1 = t1['D']
        t1.prune(["A","C", D1])
        sys.stdout.flush()
        self.assertEqual(set([n.name for n in t1.descendants()]),  set(["A","C","D","I"]))

        t1 = Tree("(((A, B), C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D1 = t1['D']
        t1.prune(["A","B"])
        self.assertEqual( t1.write(), "(A,B);")

        # test prune keeping internal nodes

        t1 = Tree('(((((A,B)C)D,E)F,G)H,(I,J)K)root;', parser=1)
        t1.prune(['A', 'B', 'F', 'H'])
        self.assertEqual(set([n.name for n in t1.traverse()]),
                         set(['A', 'B', 'F', 'H', 'root']))

        t1 = Tree('(((((A,B)C)D,E)F,G)H,(I,J)K)root;', parser=1)
        t1.prune(['A', 'B'])
        self.assertEqual(set([n.name for n in t1.traverse()]),
                         set(['A', 'B', 'root']))

        t1 = Tree('(((((A,B)C)D,E)F,G)H,(I,J)K)root;', parser=1)
        t1.prune(['A', 'B', 'C'])
        self.assertEqual(set([n.name for n in t1.traverse()]),
                         set(['A', 'B', 'C', 'root']))

        t1 = Tree('(((((A,B)C)D,E)F,G)H,(I,J)K)root;', parser=1)
        t1.prune(['A', 'B', 'I'])
        self.assertEqual(set([n.name for n in t1.traverse()]),
                         set(['A', 'B', 'C', 'I', 'root']))

    def test_remove_child(self):
        """Test removing children."""
        t = Tree()
        t.populate(20)

        # Removed node loses its parent.
        node1 = t[1]
        self.assertEqual(node1.up, t)  # no surprise here

        node1_returned = t.remove_child(t[1])
        self.assertEqual(node1_returned, node1)
        self.assertEqual(node1.up, None)  # node1 lost its parent

        t.add_child(node1)  # ok, let's put it back

        # A node that was already "stolen" does not lose its parent.
        node0 = t[0]  # first child from t, node that we will be moving around

        t2 = Tree()
        t2.add_child(node0)  # "steals" the first child from t

        self.assertEqual(t[0], t2[0])  # they should be the same node

        t.remove_child(node0)
        self.assertTrue(t[0] != node0)  # node is no longer a child of t

        self.assertEqual(node0.up, t2)  # but has not lost track of its parent
        self.assertEqual(t2[0], node0)

    def test_pop_child(self):
        """Test popping children."""
        t = Tree()
        t.populate(20)

        # Removed node loses its parent.
        node1 = t[1]
        self.assertEqual(node1.up, t)  # no surprise here

        node1_returned = t.pop_child()
        self.assertEqual(node1_returned, node1)
        self.assertEqual(node1.up, None)  # node1 lost its parent

        t.add_child(node1)  # ok, let's put it back

        # A node that was already "stolen" does not lose its parent.
        node0 = t[0]  # first child from t, node that we will be moving around

        t2 = Tree()
        t2.add_child(node0)  # "steals" the first child from t

        self.assertEqual(t[0], t2[0])  # they should be the same node

        t.pop_child(0)
        self.assertTrue(t[0] != node0)  # node is no longer a child of t

        self.assertEqual(node0.up, t2)  # but has not lost track of its parent
        self.assertEqual(t2[0], node0)

    def test_pruning(self):
        # test prune preserving distances
        for i in range(3):  # NOTE: each iteration is quite slow
            t = Tree()
            t.populate(40, dist_fn=random.random, support_fn=random.random)
            orig_nw = t.write()
            distances = {}
            for a in t.leaves():
                for b in t.leaves():
                    distances[(a,b)] = round(t.get_distance(a, b), 6)

            to_keep = set(random.sample(list(t.leaves()), 6))
            t.prune(to_keep, preserve_branch_length=True)
            for a,b in distances:
                if a in to_keep and b in to_keep:
                    self.assertEqual(distances[(a,b)], round(t.get_distance(a, b), 6))

        # Total number of nodes is correct (no single child nodes)
        for x in range(10):
            t_fuzzy = Tree("(((A,B)1, C)2,(D,E)3)root;", parser=1)
            t_fuzzy.sort_descendants()
            orig_nw = t_fuzzy.write()
            ref_nodes = list(t_fuzzy.descendants())
            t_fuzzy.populate(10)
            t_fuzzy['1'].populate(3)
            t_fuzzy['2'].populate(5)
            t_fuzzy['3'].populate(5)
            t_fuzzy.prune(ref_nodes)
            t_fuzzy.sort_descendants()
            self.assertEqual(orig_nw, t_fuzzy.write())
            self.assertEqual(len(list(t_fuzzy.descendants())), len(ref_nodes) )

        # Total number of nodes is correct (no single child nodes)
        t = Tree()
        sample_size = 5
        t.populate(1000)
        sample = random.sample(list(t.leaves()), sample_size)
        t.prune(sample)
        self.assertEqual(len(t), sample_size)
        self.assertEqual(len(list(t.descendants())), (sample_size*2)-2 )

        # Test preserve branch dist when pruning
        t = Tree()
        t.populate(100, dist_fn=random.random, support_fn=random.random)
        sample_size = 10  # NOTE: big values make this test very slow
        sample = random.sample(list(t.leaves()), sample_size)
        matrix1 = ["%f" % t.get_distance(a, b) for (a,b) in itertools.product(sample, sample)]
        t.prune(sample, preserve_branch_length=True)
        matrix2 = ["%f" % t.get_distance(a, b) for (a,b) in itertools.product(sample, sample)]

        self.assertEqual(matrix1, matrix2)
        self.assertEqual(len(list(t.descendants())), (sample_size*2)-2 )

    def test_resolve_polytomy(self):
        t = Tree('((a,a,a,a),(b,b,b,(c,c,c)));')
        t.resolve_polytomy()
        self.assertEqual(t.write(parser=9), '((((a,a),a),a),(((b,b),b),((c,c),c)));')

        t = Tree('((((a,a,a,a))),(b,b,b,(c,c,c)));')
        t.standardize()  # calls resolve_polytomy() internally too
        self.assertEqual(t.write(parser=9), '((((b,b),b),((c,c),c)),(((a,a),a),a));')

    def test_common_ancestors(self):
        # getting nodes, get_childs, get_sisters, root,
        # get_common_ancestor, get_nodes_by_name
        # get_descendants_by_name, is_leaf, is_root
        t = Tree("(((A,B)N1,C)N2[&&NHX:tag=common],D)[&&NHX:tag=root:name=root];",
                 parser=1)
        self.assertEqual(t.get_sisters(), [])

        A, B, C = t['A'], t['B'], t['C']
        root = t['root']
        self.assertEqual("A", A.name)
        test_not_found = lambda: t['notfound']
        self.assertRaises(TreeError, test_not_found)

        self.assertEqual("common", t.common_ancestor([A, C]).props["tag"])
        self.assertEqual("common", t.common_ancestor([C, B]).props["tag"])
        self.assertEqual(root, t.common_ancestor([A, "D"]))

        self.assertEqual("root", A.root.props["tag"])
        self.assertEqual("root", B.root.props["tag"])
        self.assertEqual("root", C.root.props["tag"])

        common = t.common_ancestor([C])
        self.assertEqual("root", common.root.props["tag"])

        self.assertTrue(common.root.is_root)
        self.assertTrue(not A.is_root)
        self.assertTrue(A.is_leaf)
        self.assertTrue(not A.root.is_leaf)
        self.assertRaises(TreeError, A.common_ancestor, [Tree()])

        # Test multiple target nodes and lineage
        N1, N2 = t['N1'], t['N2']
        common = t.common_ancestor(['A', 'C'])
        self.assertEqual(common, N2)

        expected_paths = {A: [A, N1, N2, root], C: [C, N2, root]}

        for node in expected_paths:
            self.assertEqual(list(node.lineage()), expected_paths[node])

        # Test common ancestor function using self as single argument (issue #398)
        common = A.common_ancestor([A])
        self.assertEqual(common, A)
        common = C.common_ancestor(["C"])
        self.assertEqual(common, C)

    def test_getters_iters(self):

        # Iter ancestors
        t = Tree("(((((a,b)A,c)B,d)C,e)D,f)root;", parser=1)
        ancestor_names = [n.name for n in (t["a"]).ancestors()]
        self.assertEqual(ancestor_names, ["A", "B", "C", "D", "root"])
        ancestor_names = [n.name for n in (t["B"]).ancestors()]
        self.assertEqual(ancestor_names, ["C", "D", "root"])


        # Tree magic python features
        t = Tree(ds.nw_dflt)
        self.assertEqual(len(t), 20)
        self.assertTrue("Ddi0002240" in t)
        self.assertTrue(t.children[0] in t)
        for a in t:
            self.assertTrue(a.name)

        # Populate
        t = Tree(ds.nw_full)
        prev_size= len(t)
        t.populate(25)
        self.assertEqual(len(t), prev_size+25)
        for i in range(10):
            t = Tree()
            t.populate(100)
            # Checks that all names are actually unique
            self.assertEqual(len(set(t.leaf_names())), 100)

        # Adding and removing features
        t = Tree("(((A,B),C)[&&NHX:tag=common],D)[&&NHX:tag=root];")
        A = t['A']

        # Check gettters and itters return the same
        t = Tree(ds.nw2_full)

        self.assertEqual(set([n for n in t.traverse("preorder")]), \
                             set([n for n in t.traverse("postorder")]))
        self.assertTrue(t in set([n for n in t.traverse("preorder")]))

        # Check order or visiting nodes

        t = Tree("((3,4)2,(6,7)5)1;", parser=1)
        postorder = "3426751"
        preorder = "1234567"
        levelorder = "1253467"

        self.assertEqual(preorder,
                         ''.join(n.name for n in t.traverse("preorder")))

        self.assertEqual(postorder,
                         ''.join(n.name for n in t.traverse("postorder")))

        self.assertEqual(levelorder,
                         ''.join(n.name for n in t.traverse("levelorder")))

        # Swap children.
        n = t.get_children()
        t.reverse_children()
        n.reverse()
        self.assertEqual(n, t.get_children())

    def test_distances(self):
        # Distances: get_distance, get_farthest_node,
        # get_farthest_descendant, get_midpoint_outgroup
        t = Tree('(((A:0.1, B:0.01):0.001, C:0.0001):1.0[&&NHX:name=I], '
                 '(D:0.00001):0.000001[&&NHX:name=J]):2.0[&&NHX:name=root];')
        A = t['A']
        B = t['B']
        C = t['C']
        D = t['D']
        I = t['I']
        J = t['J']
        root = t['root']

        def assertApprox(x, y):
            self.assertTrue(abs(x - y) < 1e-8)  # approximately equal numbers

        self.assertEqual(t.common_ancestor([A, I]).name, "I")
        self.assertEqual(t.common_ancestor([A, D]).name, "root")
        assertApprox(t.get_distance(A, I), 0.101)
        assertApprox(t.get_distance(A, B), 0.11)
        assertApprox(t.get_distance(A, A), 0)
        assertApprox(t.get_distance(I, I), 0)
        assertApprox(t.get_distance(A, root), t.get_distance(root, A))

        assertApprox(t.get_distance(A, root), t.get_distance(root, A))
        assertApprox(t.get_distance(root, A), t.get_distance(A, root))

        # Get_farthest_node, get_farthest_leaf
        self.assertEqual(root.get_farthest_leaf(), (A,1.101) )
        self.assertEqual(root.get_farthest_node(), (A,1.101) )
        self.assertEqual(A.get_farthest_leaf(), (A, 0.0))
        self.assertEqual(A.get_farthest_node(), (D, 1.101011))
        self.assertEqual(I.get_farthest_node(), (D, 1.000011))

        # Topology only distances
        t = Tree('(((A:0.5, B:1.0):1.0, C:5.0):1, (D:10.0, F:1.0):2.0):20;')

        self.assertEqual(t.get_closest_leaf(), (t['A'], 2.5))
        self.assertEqual(t.get_farthest_leaf(), (t['D'], 12.0))
        self.assertEqual(t.get_farthest_leaf(topological=True), (t['A'], 2.0))
        self.assertEqual(t.get_closest_leaf(topological=True), (t['C'], 1.0))
        self.assertEqual(t.get_distance(t, t), 0.0)
        self.assertEqual(t.get_distance(t, t, topological=True), 0.0)
        self.assertEqual(t.get_distance(t, t['A'], topological=True), 3.0)

        self.assertEqual((t['F']).get_farthest_node(topological=True), (t['A'], 3.0))
        self.assertEqual((t['F']).get_farthest_node(topological=False), (t['D'], 11.0))

    def test_rooting_topology(self):
        """Test topology changes after rooting"""
        t = Tree('((d,e)b,(f,g)c);', parser=1)
        self.assertLooks(t, """
                   ╭╴b╶┬╴d
                ╴⊗╶┤   ╰╴e
                   ╰╴c╶┬╴f
                       ╰╴g
        """)

        t.set_outgroup(t['e'])
        self.assertLooks(t, """
                ╴⊗╶┬╴e
                   ╰╴b╶┬╴d
                       ╰╴c╶┬╴f
                           ╰╴g
        """)

        t.set_outgroup(t['d'])
        self.assertLooks(t, """
                   ╭╴d
                ╴⊗╶┤   ╭╴c╶┬╴f
                   ╰╴b╶┤   ╰╴g
                       ╰╴e
        """)

        t.set_outgroup(t['c'])
        self.assertLooks(t, """
                   ╭╴c╶┬╴f
                ╴⊗╶┤   ╰╴g
                   ╰╴b╶┬╴e
                       ╰╴d
        """)

        t.set_outgroup(t['b'])
        self.assertLooks(t, """
                   ╭╴b╶┬╴e
                ╴⊗╶┤   ╰╴d
                   ╰╴c╶┬╴f
                       ╰╴g
        """)

    def test_rooting_distances(self):
        """ Tests that set_outgroup operations never changes distance relationships between nodes"""

        # Loads a large tree with different node distance
        t = Tree(ds.nw2_full)

        # records the distance between two random nodes
        YGR028W = t['YGR028W']
        YGR138C = t['YGR138C']
        d1 = t.get_distance(YGR138C, YGR028W)

        # records original sum up distances
        sum_distances = sum([n.dist for n in t.traverse() if n.dist])

        # gets midpoint outgroup and re-root the tree there
        midpoint = t.get_midpoint_outgroup()
        t.set_outgroup(midpoint)

        # saves the two nodes that split the tree by midpoint
        o1, o2 = t.children[0], t.children[1]

        # Test node distances is preserved
        d2 = t.get_distance(YGR138C, YGR028W)
        self.assertEqual(d1, d2)

        # Test sum up distance is intact after rooting
        self.assertEqual(sum_distances,
                         sum(n.dist for n in t.traverse() if n.dist))

        # Let's now test whether can we recover the original state of the tree
        # after many random re-rooting operations

        nodes = list(t.descendants())

        for i in range(100):
            for j in range(100):
                # root at a random place
                n = random.sample(nodes, 1)[0]
                t.set_outgroup(n)

            # Restore original midpoint outgroup. If everything was ok, sum up
            # distance and the same two root branches should be restoredœ
            midpoint = t.get_midpoint_outgroup()
            t.set_outgroup(midpoint)
            self.assertEqual(set([t.children[0], t.children[1]]), set([o1, o2]))

            d3 = t.get_distance(t["YGR138C"], t["YGR028W"])
            self.assertEqual(d1, d3)

            # Test sum up distance is intact after rooting
            self.assertTrue(abs(
                sum_distances -
                sum(n.dist for n in t.traverse() if n.dist))
                            < 1e-8)

        # Test that the distance of the two root branches after
        # rooting are balanced.
        t = Tree('((A:10,B:1),(C:1,D:1)E:1)root;', parser=1);
        t.set_outgroup(t.get_midpoint_outgroup())
        self.assertEqual(t.children[0].dist, 5.0)
        self.assertEqual(t.children[1].dist, 5.0)

        # Test that set_outgroup can root an "unrooted" tree (that is, a tree
        # whose root has more than 2 children).
        t = Tree('(A:10,B:1,(C:1,D:1)E:1)root;', parser=1);
        self.assertEqual(t.children[0], t['A'])
        t.set_outgroup(t['A'])

        # Test that the distance of the two root branches
        # after rooting are balanced even for unrooted trees
        self.assertEqual(t.children[0].dist, 5.0)
        self.assertEqual(t.children[1].dist, 5.0)

    def test_unroot(self):
        # Simple case. We start with a dicotomy from the root.
        t = Tree('((a:0.5,b:0.5):0.5,(c:0.2,d:0.2):0.8);')
        t.unroot()
        self.assertEqual('(a:0.5,b:0.5,(c:0.2,d:0.2):1.3);', t.write())

        # If we unroot an unrooted tree, it should stay the same:
        t.unroot()
        self.assertEqual('(a:0.5,b:0.5,(c:0.2,d:0.2):1.3);', t.write())

        # Test unrooting when we have more branch properties.
        t = Tree('((a:0.5[&&NHX:color=green],b:0.5[&&NHX:color=red]):0.5'
                 '[&&NHX:color=green],(c:0.2[&&NHX:color=green],d:0.2'
                 '[&&NHX:color=blue]):0.8[&&NHX:color=green]);')
        t.unroot(bprops=['color'])
        self.assertEqual(t.write(props=None),
            '(a:0.5[&&NHX:color=green],b:0.5[&&NHX:color=red],(c:0.2'
            '[&&NHX:color=green],d:0.2[&&NHX:color=blue]):1.3[&&NHX:color=green]);')

        # If the branch properties are not consistent, we have an exception.
        t = Tree('((a:0.5[&&NHX:color=green],b:0.5[&&NHX:color=red]):0.5'
                 '[&&NHX:color=green],(c:0.2[&&NHX:color=green],d:0.2'
                 '[&&NHX:color=blue]):0.8[&&NHX:color=red]);')
        self.assertRaises(AssertionError, t.unroot, bprops=['color'])

    def test_tree_navigation(self):
        t = Tree('(((A,B)H,C)I,(D,F)J)root;', parser=1)
        postorder = [n.name for n in t.traverse("postorder")]
        preorder = [n.name for n in t.traverse("preorder")]
        levelorder = [n.name for n in t.traverse("levelorder")]

        self.assertEqual(postorder, ['A', 'B', 'H', 'C', 'I', 'D', 'F', 'J', 'root'])
        self.assertEqual(preorder, ['root', 'I', 'H', 'A', 'B', 'C', 'J', 'D', 'F'])
        self.assertEqual(levelorder, ['root', 'I', 'J', 'H', 'C', 'D', 'F', 'A', 'B'])
        ancestors = [n.name for n in (t['B']).ancestors()]
        self.assertEqual(ancestors, ['H', 'I', 'root'])
        self.assertEqual(list(t.ancestors()), [])

        # add something of is_leaf_fn etc...
        custom_test = lambda x: x.name in 'JCH'
        custom_leaves = t.leaves(is_leaf_fn=custom_test)
        self.assertEqual({n.name for n in custom_leaves}, {'J', 'H', 'C'})

        # Test cached content
        t = Tree()
        t.populate(20)

        cache_node = t.get_cached_content()
        cache_node_leaves_only_false = t.get_cached_content(leaves_only=False)
        self.assertEqual(cache_node[t], set(t.leaves()))
        self.assertEqual(cache_node_leaves_only_false[t], set(t.traverse()))

        cache_name = t.get_cached_content('name')
        cache_name_leaves_only_false = t.get_cached_content('name', leaves_only=False)
        self.assertEqual(cache_name[t], set(t.leaf_names()))
        self.assertEqual(cache_name_leaves_only_false[t], set(n.name for n in t.traverse()))

        cache_many = {n: {(ni.name, ni.dist, ni.support) for ni in nodes}
                      for n, nodes in t.get_cached_content().items()}
        cache_many_lof = {n: {(ni.name, ni.dist, ni.support) for ni in nodes}
                          for n, nodes in t.get_cached_content(leaves_only=False).items()}
        self.assertEqual(cache_many[t], set([(leaf.name, leaf.dist, leaf.support) for leaf in t.leaves()]))
        self.assertEqual(cache_many_lof[t], set((n.name, n.dist, n.support) for n in t.traverse()))


        #self.assertEqual(cache_name_lof[t], [t.name])

    def test_rooting_branch_support(self):
        """Test that branch support, distances and custom branch properties are correctly handled after re-rooting."""

        # Generate a random tree. Test branch support and distances after rooting.
        t = Tree()
        t.populate(50, dist_fn=random.random, support_fn=lambda: random.uniform(0, 100))
        t.unroot()

        # Add a branch property.
        rand_value = random.random()
        for ch in t.children:
            ch.props['bprop'] = rand_value

        for n in t.descendants():
            if n.up is not t:
                n.props['bprop'] = random.random()

        # Record the distance and support value of all clades, based on its content
        names = set(t.leaf_names())
        cluster_id2support = {}
        cluster_id2dist = {}
        cluster_id2bprop = {}
        for n in t.descendants():
            cluster_names = set(n.leaf_names())
            cluster_names2 = names - cluster_names
            cluster_id = '_'.join(sorted(cluster_names))
            cluster_id2 = '_'.join(sorted(cluster_names2))
            cluster_id2support[cluster_id] = n.support
            cluster_id2support[cluster_id2] = n.support

            cluster_id2dist[cluster_id] = n.dist
            cluster_id2dist[cluster_id2] = n.dist
            cluster_id2bprop[cluster_id] = n.props["bprop"]
            cluster_id2bprop[cluster_id2] = n.props["bprop"]



        # Root to every single node in the tree and test whether all partitions conserve their properties
        for outgroup in t.descendants():
            t.set_outgroup(outgroup, bprops=["bprop"])

            for n in t.descendants():
                cluster_names = set(n.leaf_names())
                cluster_names2 = names - cluster_names
                cluster_id = '_'.join(sorted(cluster_names))
                cluster_id2 = '_'.join(sorted(cluster_names2))

                self.assertEqual(cluster_id2support.get(cluster_id, None), n.support)
                self.assertEqual(cluster_id2support.get(cluster_id2, None), n.support)

                self.assertEqual(cluster_id2bprop.get(cluster_id, None), n.props.get("bprop"))
                self.assertEqual(cluster_id2bprop.get(cluster_id2, None), n.props.get("bprop"))

                if n.up and n.up.up:
                    self.assertEqual(cluster_id2dist.get(cluster_id, None), n.dist)

    def test_describe(self):
        self.assertEqual(Tree().describe(),
                         'Number of leaf nodes: 1\n'
                         'Total number of nodes: 1\n'
                         'Rooted: No children\n'
                         'Most distant node: \n'
                         'Max. distance: 0')
        self.assertEqual(Tree('(a,b,c);').describe(),
                         'Number of leaf nodes: 3\n'
                         'Total number of nodes: 4\n'
                         'Rooted: No\n'
                         'Most distant node: a\n'
                         'Max. distance: 1')
        self.assertEqual(Tree('(a,(b,c));').describe(),
                         'Number of leaf nodes: 3\n'
                         'Total number of nodes: 5\n'
                         'Rooted: Yes\n'
                         'Most distant node: b\n'
                         'Max. distance: 2')

    def test_treeid(self):
        t = Tree()
        t.populate(50, dist_fn=random.random, support_fn=random.random)
        orig_id = t.get_topology_id()
        nodes = list(t.descendants())
        for i in range(20):
            for n in random.sample(nodes, 10):
                n.reverse_children()
                self.assertEqual(t.get_topology_id(), orig_id)

    def test_node_id(self):
        """Test the node_id corresponding to a node inside a tree."""
        t = Tree('((a,b)x,(c,d)y);', parser=1)
        #     ╭╴x (0,)╶┬╴a (0,0)
        # ╴()╶┤        ╰╴b (0,1)
        #     ╰╴y (1,)╶┬╴c (1,0)
        #              ╰╴d (1,1)

        self.assertEqual(t.id, ())
        self.assertEqual(t['x'].id, (0,))
        self.assertEqual(t['y'].id, (1,))
        self.assertEqual(t['a'].id, (0,0))
        self.assertEqual(t['d'].id, (1,1))

    def test_ultrametric(self):
        EPSILON = 1e-5  # small number for the purposes of comparing distances

        # Convert tree to a ultrametric, in which the distance from
        # leafs to root is always the same.
        t = Tree()
        t.populate(80, dist_fn=random.random, support_fn=random.random)
        max_dist = max(t.get_distance(t, n) for n in t)

        t.to_ultrametric()
        self.assertTrue(all(abs(t.get_distance(t, n) - max_dist) < EPSILON for n in t))

        t2 = Tree()
        t2.populate(80, dist_fn=random.random, support_fn=random.random)
        max_dist = max(t2.get_distance(t2, n) for n in t2)

        t2.to_ultrametric(topological=True)
        self.assertTrue(all(abs(t2.get_distance(t2, n) - max_dist) < EPSILON for n in t2))
        leaf, _ = t2.get_farthest_leaf(topological=True)
        self.assertTrue(all(abs(node.dist - leaf.dist) < EPSILON
                            for node in leaf.ancestors() if not node.is_root))

    def test_expand_polytomies_rf(self):
        gtree = Tree('((a:1, (b:1, (c:1, d:1):1):1), (e:1, (f:1, g:1):1):1);')
        ref1 = Tree('((a:1, (b:1, c:1, d:1):1):1, (e:1, (f:1, g:1):1):1);')
        ref2 = Tree('((a:1, (b:1, c:1, d:1):1):1, (e:1, f:1, g:1):1);')

        for ref in [ref1, ref2]:
            gtree.robinson_foulds(ref, expand_polytomies=True)[0]

        gtree = Tree('((g, h), (a, (b, (c, (d,( e, f))))));')
        ref3 = Tree('((a, b, c, (d, e, f)), (g, h));')
        ref4 = Tree('((a, b, c, d, e, f), (g, h));')
        ref5 = Tree('((a, b, (c, d, (e, f))), (g, h));')

        for ref in [ref3, ref4, ref5]:
            gtree.robinson_foulds(ref, expand_polytomies=True,
                                  polytomy_size_limit=8)[0]

        gtree = Tree('((g, h), (a, b, (c, d, (e, f))));')
        ref6 = Tree('((a, b, (c, d, e, f)), (g, h));')
        ref7 = Tree('((a, (b, (c, d, e, f))), (g, h));')
        ref8 = Tree('((a, b, c, (d, e, f)), (g, h));')
        ref9 = Tree('((d, b, c, (a, e, f)), (g, h));')

        for ref in [ref6, ref7, ref8, ref9]:
            gtree.robinson_foulds(ref, expand_polytomies=True)[0]

        gtree = Tree('((g, h), ((a, b), (c, d), (e, f)));')
        ref10 = Tree('((g, h), ((a, c), ((b, d), (e, f))));')

        for ref in [ref10]:
            gtree.robinson_foulds(ref, expand_polytomies=True,
                                  polytomy_size_limit=8)[0]

    # TODO: Fix the compare() function and this test.
    # def test_tree_compare(self):
    #     def _astuple(d):
    #         keynames = ["norm_rf", "rf", "max_rf", "ref_edges_in_source",
    #                     "source_edges_in_ref", "effective_tree_size",
    #                     "source_subtrees", "treeko_dist"]
    #         return tuple([d[v] for v in keynames])

    #     ref1 = Tree('((((A, B)0.91, (C, D))0.9, (E,F)0.96), (G, H));', parser=0)
    #     ref2 = Tree('(((A, B)0.91, (C, D))0.9, (E,F)0.96);', parser=0)
    #     s1 = Tree('(((A, B)0.9, (C, D))0.9, (E,F)0.9);', parser=0)

    #     small = Tree("((A, B), C);")
    #     # RF unrooted in too small trees for rf, but with at least one internal node
    #     self.assertEqual(_astuple(small.compare(ref1, unrooted=True)),
    #                      ("NA", "NA", 0.0, 1.0, 1.0, 3, 1, "NA"))

    #     small = Tree("(A, B);")
    #     # RF unrooted in too small trees
    #     self.assertEqual(_astuple(small.compare(ref1, unrooted=True)),
    #                      ("NA", "NA", 0.0, "NA", "NA", 2, 1, "NA"))

    #     small = Tree("(A, B);")
    #     # RF unrooted in too small trees
    #     self.assertEqual(_astuple(small.compare(ref1, unrooted=False)),
    #                      ("NA", "NA", 0.0, "NA", "NA", 2, 1, "NA"))

    #     # identical trees, 8 rooted partitions in total (4 an 4), and 6 unrooted
    #     self.assertEqual(_astuple(s1.compare(ref1)),
    #                      (0.0, 0.0, 8, 1.0, 1.0, 6, 1, "NA"))

    #     self.assertEqual(_astuple(s1.compare(ref1, unrooted=True)),
    #                      (0.0, 0.0, 6, 1.0, 1.0, 6, 1, "NA"))

    #     # The same stats should be return discarding branches, as the topology
    #     # is still identical, but branches used should be different
    #     self.assertEqual(_astuple(s1.compare(ref1, min_support_source=0.99, min_support_ref=.99)),
    #                      (0.0, 0.0, 2, 1.0, 1.0, 6, 1, "NA"))

    #     self.assertEqual(_astuple(s1.compare(ref1, min_support_source=0.99, min_support_ref=.99, unrooted=True)),
    #                      (0.0, 0.0, 2, 1.0, 1.0, 6, 1, "NA"))


    #     self.assertEqual(_astuple(s1.compare(ref1, min_support_source=0.99)),
    #                      (0.0, 0.0, 5, 1/4., 1.0, 6, 1, "NA"))


    #     self.assertEqual(_astuple(s1.compare(ref1, min_support_source=0.99, unrooted=True)),
    #                      (0.0, 0.0, 4, 6/8., 1.0, 6, 1, "NA"))


    #     self.assertEqual(_astuple(s1.compare(ref1, min_support_ref=0.99)),
    #                      (0.0, 0.0, 5, 1.0, 1/4., 6, 1, "NA"))


    #     self.assertEqual(_astuple(s1.compare(ref1, min_support_ref=0.99, unrooted=True)),
    #                      (0.0, 0.0, 4, 1.0, 6/8., 6, 1, "NA"))


    #     # Three partitions different
    #     s2 = Tree('(((A, E)0.9, (C, D))0.98, (B,F)0.95);')
    #     self.assertEqual(_astuple(s2.compare(ref1)),
    #                      (6/8., 6, 8, 1/4., 1/4., 6, 1, "NA"))

    #     self.assertEqual(_astuple(s2.compare(ref1, unrooted=True)),
    #                      (4/6., 4, 6, 6/8., 6/8., 6, 1, "NA"))

    #     # lets discard one branch from source tree.  there are 4 valid edges in
    #     # ref, 3 in source there is only 2 edges in common, CD and root (which
    #     # should be discounted for % of found branches)
    #     self.assertEqual(_astuple(s2.compare(ref1, min_support_source=0.95)),
    #                      (5/7., 5, 7, 1/4., 1/3., 6, 1, "NA"))

    #     # similar in unrooted, but we don not need to discount root edges
    #     self.assertEqual(_astuple(s2.compare(ref1, min_support_source=0.95, unrooted=True)),
    #                      (3/5., 3, 5, 6/8., 6/7., 6, 1, "NA"))


    #     # totally different trees
    #     s3 = Tree('(((A, C)0.9, (E, D))0.98, (B,F)0.95);')
    #     self.assertEqual(_astuple(s3.compare(ref1)),
    #                      (1.0, 8, 8, 0.0, 0.0, 6, 1, "NA"))

    # TODO: Merge this function with the previous one? (test_tree_compare())
    def test_robinson_foulds_and_more(self):
        # this is the result of 100 Ktreedist runs on random trees, using rooted
        # and unrooted topologies. ETE should provide the same RF result
        samples = [
        [28, True, '(((z,y),(x,(w,v))),(u,t),((s,r),((q,(p,o)),((n,(m,(l,(k,j)))),(i,(h,g))))));', '(((k,(j,(i,(h,g)))),z),(y,x),((w,v),((u,(t,(s,(r,q)))),(p,(o,(n,(m,l)))))));'],
        [28, False, '(((t,s),((r,(q,p)),(o,n))),(((m,(l,(k,j))),(i,(h,g))),(z,(y,(x,(w,(v,u)))))));', '((((k,(j,i)),((h,g),z)),((y,(x,w)),((v,(u,t)),(s,(r,(q,p)))))),((o,n),(m,l)));'],
        [18, True, '(((v,(u,(t,s))),((r,(q,(p,o))),((n,m),(l,k)))),(j,(i,(h,g))),(z,(y,(x,w))));', '(((z,(y,(x,w))),(v,(u,(t,s)))),((r,(q,p)),(o,(n,m))),((l,(k,(j,i))),(h,g)));'],
        [26, True, '(((l,k),(j,i)),((h,g),(z,(y,(x,w)))),((v,(u,(t,(s,(r,q))))),((p,o),(n,m))));', '(((p,o),((n,(m,l)),(k,j))),((i,(h,g)),(z,y)),((x,(w,v)),((u,(t,s)),(r,q))));'],
        [24, True, '(((o,(n,m)),(l,(k,(j,(i,(h,g)))))),(z,(y,x)),((w,v),((u,(t,(s,r))),(q,p))));', '(((t,(s,(r,(q,(p,o))))),(n,m)),((l,k),(j,(i,(h,g)))),((z,y),((x,w),(v,u))));'],
        [24, True, '(((y,(x,(w,v))),(u,t)),((s,(r,(q,(p,o)))),(n,m)),((l,k),((j,(i,(h,g))),z)));', '(((z,(y,(x,w))),(v,(u,t))),(s,(r,(q,(p,(o,(n,(m,(l,k)))))))),(j,(i,(h,g))));'],
        [28, False, '(((p,(o,(n,(m,l)))),((k,(j,i)),(h,g))),((z,y),((x,(w,(v,u))),(t,(s,(r,q))))));', '((((t,(s,r)),(q,p)),((o,n),(m,(l,(k,(j,i)))))),(((h,g),(z,(y,(x,w)))),(v,u)));'],
        [28, True, '((((i,(h,g)),z),(y,x)),((w,v),((u,(t,(s,r))),(q,p))),((o,n),(m,(l,(k,j)))));', '((((h,g),z),(y,x)),(w,(v,u)),((t,s),((r,(q,p)),((o,(n,m)),(l,(k,(j,i)))))));'],
        [28, True, '(((x,(w,(v,(u,(t,(s,(r,(q,(p,o))))))))),((n,(m,l)),(k,(j,i)))),(h,g),(z,y));', '(((u,t),(s,r)),((q,p),(o,(n,m))),(((l,(k,(j,i))),((h,g),(z,(y,x)))),(w,v)));'],
        [22, False, '(((x,(w,(v,u))),((t,(s,r)),(q,p))),((o,(n,(m,l))),((k,j),((i,(h,g)),(z,y)))));', '(((z,(y,(x,(w,(v,u))))),(t,(s,r))),((q,(p,(o,(n,m)))),((l,k),(j,(i,(h,g))))));'],
        [26, True, '((z,(y,(x,w))),(v,(u,(t,s))),((r,(q,(p,(o,(n,m))))),((l,k),(j,(i,(h,g))))));', '(((v,(u,t)),((s,r),((q,(p,o)),(n,(m,l))))),((k,j),((i,(h,g)),z)),(y,(x,w)));'],
        [34, False, '((((i,(h,g)),(z,(y,x))),(w,v)),((u,t),((s,r),((q,(p,(o,n))),(m,(l,(k,j)))))));', '(((p,(o,(n,(m,(l,k))))),((j,i),(h,g))),(z,(y,(x,(w,(v,(u,(t,(s,(r,q))))))))));'],
        [30, False, '(((i,(h,g)),(z,y)),((x,w),((v,(u,(t,(s,(r,q))))),(p,(o,(n,(m,(l,(k,j)))))))));', '((((l,k),(j,(i,(h,g)))),(z,(y,(x,w)))),((v,u),((t,s),((r,(q,p)),(o,(n,m))))));'],
        [26, False, '(((v,(u,t)),((s,(r,q)),((p,o),((n,m),((l,k),(j,i)))))),((h,g),(z,(y,(x,w)))));', '(((y,(x,(w,v))),(u,(t,s))),(((r,q),((p,o),(n,(m,(l,k))))),((j,i),((h,g),z))));'],
        [20, False, '(((u,(t,s)),(r,q)),(((p,o),((n,m),((l,k),((j,i),((h,g),z))))),(y,(x,(w,v)))));', '((((u,t),(s,r)),(((q,p),(o,(n,m))),(((l,k),(j,i)),((h,g),z)))),((y,x),(w,v)));'],
        [20, True, '(((y,x),(w,v)),((u,(t,s)),((r,q),(p,(o,(n,(m,(l,k))))))),((j,(i,(h,g))),z));', '(((r,q),((p,o),(n,(m,(l,(k,j)))))),((i,(h,g)),(z,(y,(x,(w,v))))),(u,(t,s)));'],
        [24, True, '((((k,(j,i)),(h,g)),((z,(y,(x,w))),((v,(u,t)),(s,r)))),(q,(p,(o,n))),(m,l));', '((((s,r),((q,p),(o,(n,m)))),((l,k),((j,i),((h,g),z)))),(y,x),(w,(v,(u,t))));'],
        [18, True, '((w,(v,(u,(t,s)))),(r,q),((p,(o,n)),((m,(l,k)),((j,(i,(h,g))),(z,(y,x))))));', '(((y,x),((w,v),(u,(t,s)))),((r,(q,(p,(o,n)))),(m,l)),((k,j),((i,(h,g)),z)));'],
        [26, True, '(((j,(i,(h,g))),(z,(y,(x,(w,(v,(u,t))))))),(s,r),((q,p),((o,(n,m)),(l,k))));', '(((s,(r,(q,(p,(o,(n,(m,l))))))),(k,j)),((i,(h,g)),(z,y)),((x,(w,v)),(u,t)));'],
        [30, True, '((((r,(q,(p,(o,n)))),((m,l),(k,(j,i)))),((h,g),z)),(y,(x,(w,v))),(u,(t,s)));', '(((u,t),(s,r)),((q,p),(o,(n,(m,(l,(k,j)))))),(((i,(h,g)),(z,(y,x))),(w,v)));'],
        [30, False, '((((m,(l,k)),(j,i)),(((h,g),(z,y)),(x,w))),((v,u),(t,(s,(r,(q,(p,(o,n))))))));', '(((u,t),((s,(r,q)),(p,(o,(n,(m,(l,k))))))),((j,(i,(h,g))),(z,(y,(x,(w,v))))));'],
        [22, False, '(((k,(j,i)),(h,g)),((z,(y,x)),((w,(v,(u,(t,(s,r))))),((q,(p,(o,n))),(m,l)))));', '(((w,(v,u)),((t,(s,r)),((q,p),((o,(n,(m,l))),((k,(j,i)),((h,g),z)))))),(y,x));'],
        [26, False, '(((x,(w,(v,(u,(t,s))))),(r,q)),((p,(o,(n,(m,l)))),((k,j),((i,(h,g)),(z,y)))));', '(((o,(n,m)),(l,(k,j))),(((i,(h,g)),(z,y)),((x,w),((v,u),((t,(s,r)),(q,p))))));'],
        [28, True, '(((x,(w,v)),(u,(t,s))),((r,(q,(p,(o,(n,m))))),(l,(k,(j,(i,(h,g)))))),(z,y));', '((((i,(h,g)),(z,(y,x))),((w,v),((u,t),(s,(r,(q,p)))))),(o,n),((m,l),(k,j)));'],
        [20, False, '((((m,l),(k,(j,(i,(h,g))))),(z,y)),((x,(w,(v,(u,(t,s))))),(r,(q,(p,(o,n))))));', '((((m,l),((k,(j,i)),(h,g))),(z,(y,(x,(w,v))))),((u,t),(s,(r,(q,(p,(o,n)))))));'],
        [26, True, '(((o,(n,(m,(l,k)))),(j,i)),((h,g),(z,y)),((x,(w,(v,(u,(t,s))))),(r,(q,p))));', '((((t,(s,(r,(q,(p,(o,n)))))),(m,(l,k))),((j,i),(h,g))),(z,(y,x)),(w,(v,u)));'],
        [22, False, '((((p,o),((n,m),((l,k),(j,i)))),((h,g),(z,y))),((x,(w,(v,u))),((t,s),(r,q))));', '((((v,(u,(t,s))),(r,q)),((p,o),((n,m),(l,k)))),(((j,i),(h,g)),(z,(y,(x,w)))));'],
        [28, False, '((((r,(q,(p,(o,n)))),(m,(l,k))),(((j,i),(h,g)),((z,y),(x,w)))),((v,u),(t,s)));', '((((k,j),((i,(h,g)),(z,y))),(x,w)),(((v,(u,t)),(s,r)),((q,p),((o,n),(m,l)))));'],
        [20, True, '((((q,(p,o)),(n,m)),((l,k),((j,i),(h,g)))),(z,(y,x)),((w,v),(u,(t,(s,r)))));', '((((l,(k,(j,i))),(h,g)),((z,y),(x,(w,v)))),(u,t),((s,(r,(q,(p,o)))),(n,m)));'],
        [28, False, '(((t,(s,r)),(q,(p,o))),(((n,(m,(l,k))),(j,(i,(h,g)))),((z,y),(x,(w,(v,u))))));', '(((w,(v,u)),(t,s)),(((r,(q,p)),(o,n)),(((m,l),((k,j),((i,(h,g)),z))),(y,x))));'],
        [24, True, '((((h,g),(z,y)),((x,(w,(v,u))),(t,(s,(r,q))))),(p,o),((n,m),((l,k),(j,i))));', '(((t,s),((r,(q,p)),((o,(n,(m,l))),((k,j),(i,(h,g)))))),(z,y),(x,(w,(v,u))));'],
        [20, True, '(((p,o),(n,(m,(l,(k,(j,i)))))),((h,g),z),((y,(x,w)),((v,u),(t,(s,(r,q))))));', '(((y,(x,w)),(v,(u,t))),((s,r),(q,p)),((o,(n,m)),((l,(k,(j,i))),((h,g),z))));'],
        [32, True, '((((s,(r,q)),((p,(o,n)),(m,(l,k)))),((j,(i,(h,g))),(z,y))),(x,w),(v,(u,t)));', '(((u,(t,(s,r))),((q,(p,o)),((n,(m,l)),(k,(j,i))))),((h,g),(z,(y,x))),(w,v));'],
        [26, True, '(((z,(y,x)),(w,(v,(u,t)))),(s,(r,(q,(p,(o,n))))),((m,l),(k,(j,(i,(h,g))))));', '(((u,t),((s,r),((q,p),((o,n),((m,(l,k)),((j,i),((h,g),z))))))),(y,x),(w,v));'],
        [10, True, '(((p,o),((n,m),((l,(k,(j,i))),((h,g),(z,y))))),(x,(w,(v,u))),((t,s),(r,q)));', '((((n,m),((l,(k,(j,i))),((h,g),(z,y)))),(x,w)),(v,(u,(t,(s,(r,q))))),(p,o));'],
        [30, True, '((((h,g),z),((y,x),((w,v),(u,t)))),(s,r),((q,p),((o,n),((m,l),(k,(j,i))))));', '((((v,(u,(t,(s,r)))),(q,(p,o))),((n,m),((l,k),(j,(i,(h,g)))))),(z,y),(x,w));'],
        [30, False, '(((q,(p,o)),((n,m),((l,(k,(j,(i,(h,g))))),(z,y)))),((x,(w,v)),(u,(t,(s,r)))));', '((((t,s),((r,q),((p,o),(n,m)))),((l,k),(j,i))),(((h,g),z),((y,(x,w)),(v,u))));'],
        [24, False, '(((p,o),(n,m)),(((l,(k,(j,i))),(h,g)),((z,y),((x,w),((v,u),(t,(s,(r,q))))))));', '((x,(w,v)),((u,(t,(s,(r,q)))),((p,(o,(n,(m,(l,(k,(j,(i,(h,g))))))))),(z,y))));'],
        [28, False, '(((z,y),((x,w),((v,u),(t,s)))),((r,(q,(p,(o,(n,m))))),((l,k),((j,i),(h,g)))));', '((((s,(r,q)),((p,o),((n,(m,l)),(k,(j,(i,(h,g))))))),(z,y)),((x,w),(v,(u,t))));'],
        [24, False, '((((o,n),((m,l),((k,(j,i)),(h,g)))),(z,(y,x))),((w,(v,(u,(t,(s,r))))),(q,p)));', '(((q,(p,(o,(n,m)))),((l,(k,j)),(i,(h,g)))),(z,(y,(x,(w,(v,(u,(t,(s,r)))))))));'],
        [22, True, '(((p,(o,(n,m))),((l,k),((j,i),((h,g),(z,y))))),(x,w),((v,u),((t,s),(r,q))));', '(((u,(t,(s,(r,(q,(p,(o,(n,m)))))))),((l,k),((j,i),((h,g),(z,(y,x)))))),w,v);'],
        [28, False, '((((r,q),((p,o),(n,(m,l)))),((k,(j,i)),(h,g))),((z,y),((x,(w,v)),(u,(t,s)))));', '(((h,g),z),((y,x),((w,v),((u,t),((s,(r,(q,(p,(o,(n,m)))))),(l,(k,(j,i))))))));'],
        [30, True, '((((h,g),z),((y,(x,(w,(v,u)))),((t,s),((r,(q,(p,o))),(n,m))))),(l,k),(j,i));', '((((o,n),((m,(l,(k,j))),((i,(h,g)),z))),(y,(x,(w,v)))),(u,(t,s)),(r,(q,p)));'],
        [30, True, '(((v,u),(t,(s,(r,(q,p))))),((o,(n,m)),((l,(k,j)),((i,(h,g)),z))),(y,(x,w)));', '((((m,(l,k)),((j,i),(h,g))),(z,y)),(x,w),((v,(u,(t,(s,(r,q))))),(p,(o,n))));'],
        [26, True, '(((q,p),((o,(n,(m,l))),(k,(j,i)))),((h,g),z),((y,x),((w,(v,(u,t))),(s,r))));', '((((j,(i,(h,g))),(z,(y,x))),((w,v),(u,t))),(s,(r,q)),((p,o),(n,(m,(l,k)))));'],
        [20, False, '((((o,(n,m)),((l,k),((j,i),((h,g),z)))),(y,x)),(((w,v),(u,t)),((s,r),(q,p))));', '((((j,i),((h,g),z)),((y,x),(w,(v,(u,(t,(s,r))))))),((q,p),((o,n),(m,(l,k)))));'],
        [30, False, '(((x,w),(v,(u,(t,(s,(r,(q,(p,(o,(n,m)))))))))),((l,k),((j,(i,(h,g))),(z,y))));', '(((m,l),((k,(j,(i,(h,g)))),z)),((y,(x,(w,(v,(u,t))))),((s,r),((q,p),(o,n)))));'],
        [32, True, '((((y,x),(w,v)),((u,(t,(s,r))),(q,(p,o)))),((n,m),(l,(k,j))),((i,(h,g)),z));', '(((m,l),(k,(j,i))),((h,g),z),((y,(x,w)),((v,u),((t,s),(r,(q,(p,(o,n))))))));'],
        [28, True, '(((v,u),((t,(s,(r,(q,p)))),((o,n),((m,l),(k,(j,(i,(h,g)))))))),(z,y),(x,w));', '((((n,m),((l,k),((j,i),((h,g),(z,(y,(x,(w,(v,u))))))))),(t,s)),(r,q),(p,o));'],
        [32, False, '(((r,(q,p)),(o,n)),(((m,(l,k)),(j,i)),(((h,g),(z,y)),((x,w),((v,u),(t,s))))));', '(((y,x),((w,v),(u,(t,(s,r))))),(((q,(p,(o,n))),(m,l)),((k,(j,(i,(h,g)))),z)));'],
        [20, True, '(((w,v),((u,(t,(s,r))),((q,p),((o,(n,(m,l))),((k,j),((i,(h,g)),z)))))),y,x);', '(((w,v),((u,t),(s,(r,q)))),((p,o),((n,(m,l)),(k,j))),((i,(h,g)),(z,(y,x))));'],
        [24, False, '(((x,(w,v)),((u,(t,s)),(r,q))),(((p,o),((n,(m,l)),(k,j))),((i,(h,g)),(z,y))));', '((((i,(h,g)),z),((y,x),(w,v))),((u,(t,s)),((r,(q,(p,(o,(n,m))))),(l,(k,j)))));'],
        [22, False, '((((k,(j,(i,(h,g)))),(z,(y,x))),((w,v),(u,t))),((s,(r,(q,(p,o)))),(n,(m,l))));', '(((w,v),(u,(t,(s,(r,(q,(p,o))))))),(((n,m),((l,(k,(j,i))),((h,g),z))),(y,x)));'],
        [28, True, '(((x,w),((v,u),((t,s),(r,(q,p))))),((o,n),(m,l)),((k,(j,i)),((h,g),(z,y))));', '((((p,o),(n,m)),((l,(k,(j,i))),((h,g),z))),(y,(x,(w,v))),((u,t),(s,(r,q))));'],
        [30, False, '(((q,p),((o,(n,(m,l))),((k,(j,(i,(h,g)))),z))),((y,x),((w,(v,u)),(t,(s,r)))));', '((((m,(l,k)),((j,(i,(h,g))),z)),(y,(x,w))),((v,(u,(t,(s,(r,q))))),(p,(o,n))));'],
        [30, False, '(((y,x),((w,(v,(u,(t,(s,r))))),(q,p))),((o,(n,(m,(l,(k,(j,i)))))),((h,g),z)));', '((((t,(s,(r,q))),((p,(o,(n,(m,l)))),((k,(j,i)),(h,g)))),(z,y)),((x,w),(v,u)));'],
        [20, False, '(((u,(t,s)),(r,(q,(p,(o,(n,(m,(l,(k,j))))))))),(((i,(h,g)),z),(y,(x,(w,v)))));', '(((o,n),(m,(l,(k,j)))),(((i,(h,g)),(z,y)),((x,(w,v)),((u,(t,(s,r))),(q,p)))));'],
        [26, False, '(((t,s),((r,(q,(p,(o,n)))),(m,(l,k)))),(((j,i),((h,g),z)),((y,(x,w)),(v,u))));', '(((r,(q,(p,o))),((n,(m,(l,k))),((j,i),(h,g)))),((z,(y,(x,(w,v)))),(u,(t,s))));'],
        [28, True, '((((r,q),((p,(o,(n,(m,l)))),((k,(j,i)),(h,g)))),(z,(y,(x,w)))),(v,u),(t,s));', '(((x,(w,(v,(u,(t,s))))),(r,(q,(p,o)))),(n,m),((l,k),((j,(i,(h,g))),(z,y))));'],
        [28, False, '(((t,s),((r,(q,p)),((o,n),(m,(l,(k,(j,i))))))),(((h,g),(z,y)),(x,(w,(v,u)))));', '((((h,g),(z,(y,(x,(w,v))))),(u,(t,(s,r)))),((q,(p,(o,(n,m)))),(l,(k,(j,i)))));'],
        [26, True, '((((q,(p,o)),((n,m),((l,(k,(j,i))),(h,g)))),(z,(y,x))),(w,v),(u,(t,(s,r))));', '(((y,x),(w,(v,u))),((t,(s,r)),((q,p),(o,n))),((m,(l,k)),((j,(i,(h,g))),z)));'],
        [28, False, '((((q,(p,(o,n))),((m,(l,k)),((j,(i,(h,g))),z))),(y,x)),((w,(v,(u,t))),(s,r)));', '(((z,(y,x)),(w,v)),(((u,t),((s,(r,(q,p))),((o,n),(m,l)))),((k,(j,i)),(h,g))));'],
        [22, True, '(((x,w),((v,(u,(t,s))),(r,q))),((p,(o,n)),((m,(l,k)),(j,(i,(h,g))))),(z,y));', '((((j,(i,(h,g))),(z,(y,x))),(w,(v,u))),((t,s),((r,q),(p,o))),((n,m),(l,k)));'],
        [26, False, '((((n,(m,l)),(k,j)),(((i,(h,g)),(z,y)),((x,w),((v,u),(t,s))))),((r,q),(p,o)));', '(((v,u),(t,s)),(((r,(q,(p,(o,n)))),((m,(l,k)),(j,i))),((h,g),(z,(y,(x,w))))));'],
        [32, False, '((((n,(m,(l,(k,j)))),((i,(h,g)),z)),(y,x)),((w,v),((u,(t,(s,r))),(q,(p,o)))));', '((((v,u),(t,(s,(r,(q,p))))),((o,(n,(m,(l,k)))),(j,(i,(h,g))))),((z,y),(x,w)));'],
        [20, False, '((((q,(p,(o,n))),(m,l)),((k,(j,(i,(h,g)))),z)),((y,(x,(w,(v,(u,t))))),(s,r)));', '(((w,(v,(u,t))),(s,r)),(((q,p),(o,n)),(((m,l),(k,(j,i))),((h,g),(z,(y,x))))));'],
        [20, True, '(((z,(y,(x,w))),(v,u)),((t,(s,r)),(q,(p,o))),((n,(m,l)),((k,(j,i)),(h,g))));', '((((q,(p,(o,n))),(m,l)),((k,j),(i,(h,g)))),(z,y),((x,w),((v,u),(t,(s,r)))));'],
        [34, False, '(((w,(v,(u,(t,(s,(r,q)))))),(p,o)),(((n,m),(l,(k,j))),((i,(h,g)),(z,(y,x)))));', '(((y,(x,(w,(v,u)))),(t,(s,r))),(((q,(p,(o,(n,(m,(l,k)))))),(j,i)),((h,g),z)));'],
        [26, False, '(((y,x),(w,(v,(u,t)))),(((s,r),((q,(p,o)),(n,(m,l)))),((k,(j,(i,(h,g)))),z)));', '(((s,(r,(q,(p,o)))),(n,m)),(((l,k),((j,i),((h,g),(z,(y,(x,w)))))),(v,(u,t))));'],
        [30, False, '(((v,(u,t)),((s,r),((q,p),((o,(n,(m,(l,k)))),(j,i))))),(((h,g),z),(y,(x,w))));', '(((y,(x,(w,v))),((u,(t,s)),(r,(q,(p,o))))),((n,(m,l)),((k,(j,i)),((h,g),z))));'],
        [26, False, '(((y,x),(w,v)),(((u,t),((s,(r,(q,p))),(o,n))),((m,(l,k)),((j,i),((h,g),z)))));', '((((s,(r,q)),((p,(o,n)),((m,l),(k,(j,i))))),((h,g),z)),((y,(x,w)),(v,(u,t))));'],
        [22, True, '(((w,v),(u,t)),((s,r),((q,p),((o,(n,m)),((l,k),((j,i),(h,g)))))),(z,(y,x)));', '(((z,y),(x,(w,(v,u)))),(t,(s,r)),((q,(p,o)),((n,m),((l,(k,(j,i))),(h,g)))));'],
        [28, False, '(((y,x),(w,(v,(u,t)))),(((s,(r,q)),((p,o),(n,(m,(l,k))))),((j,i),((h,g),z))));', '((((i,(h,g)),(z,(y,x))),((w,(v,u)),(t,s))),((r,q),((p,o),((n,m),(l,(k,j))))));'],
        [26, False, '(((v,(u,(t,s))),(r,(q,p))),(((o,n),((m,(l,(k,j))),((i,(h,g)),(z,y)))),(x,w)));', '(((q,p),((o,n),((m,l),((k,j),((i,(h,g)),z))))),(y,(x,(w,(v,(u,(t,(s,r))))))));'],
        [26, True, '(((t,(s,(r,q))),((p,o),((n,(m,l)),((k,j),((i,(h,g)),z))))),(y,x),(w,(v,u)));', '(((z,y),(x,w)),(v,u),((t,(s,r)),((q,(p,(o,(n,(m,l))))),((k,(j,i)),(h,g)))));'],
        [30, True, '(((w,(v,(u,(t,(s,r))))),(q,p)),((o,(n,m)),((l,k),(j,i))),(((h,g),z),(y,x)));', '((((p,o),(n,(m,(l,(k,(j,(i,(h,g)))))))),(z,(y,x))),(w,(v,u)),((t,s),(r,q)));'],
        [26, True, '((((i,(h,g)),(z,y)),(x,w)),((v,u),((t,(s,r)),(q,p))),((o,n),(m,(l,(k,j)))));', '(((l,k),((j,i),((h,g),(z,y)))),(x,w),((v,u),((t,s),((r,(q,(p,o))),(n,m)))));'],
        [26, False, '(((x,w),((v,(u,(t,s))),((r,(q,p)),((o,(n,(m,(l,k)))),((j,i),(h,g)))))),(z,y));', '(((p,(o,(n,m))),(l,k)),(((j,i),(h,g)),((z,y),((x,(w,v)),((u,t),(s,(r,q)))))));'],
        [24, True, '(((x,w),((v,(u,t)),(s,r))),((q,p),(o,(n,(m,(l,k))))),((j,i),((h,g),(z,y))));', '(((h,g),(z,y)),(x,(w,(v,u))),((t,(s,r)),(q,(p,(o,(n,(m,(l,(k,(j,i))))))))));'],
        [24, True, '(((y,x),(w,v)),((u,t),((s,r),((q,p),((o,n),(m,(l,k)))))),((j,(i,(h,g))),z));', '((((r,(q,p)),(o,(n,(m,(l,(k,(j,(i,(h,g))))))))),(z,y)),(x,(w,v)),(u,(t,s)));'],
        [28, False, '(((y,(x,(w,v))),((u,t),((s,(r,q)),((p,(o,n)),((m,l),(k,(j,i))))))),((h,g),z));', '(((v,u),(t,(s,(r,(q,(p,(o,n))))))),(((m,l),((k,j),((i,(h,g)),z))),(y,(x,w))));'],
        [26, True, '((((h,g),z),((y,x),((w,(v,u)),((t,(s,(r,q))),(p,(o,n)))))),(m,(l,k)),(j,i));', '((z,y),(x,(w,(v,(u,t)))),((s,r),((q,p),((o,n),((m,(l,k)),(j,(i,(h,g))))))));'],
        [24, True, '(((u,t),(s,r)),((q,p),((o,n),((m,(l,(k,(j,(i,(h,g)))))),z))),(y,(x,(w,v))));', '((((j,(i,(h,g))),z),(y,x)),(w,(v,(u,t))),((s,(r,(q,p))),((o,(n,m)),(l,k))));'],
        [30, True, '(((t,(s,r)),((q,p),((o,n),(m,(l,(k,j)))))),((i,(h,g)),z),((y,x),(w,(v,u))));', '((((w,(v,(u,t))),(s,(r,q))),((p,(o,(n,m))),(l,k))),((j,i),(h,g)),(z,(y,x)));'],
        [30, False, '((((x,(w,v)),(u,t)),((s,(r,q)),(p,o))),(((n,m),((l,k),((j,i),(h,g)))),(z,y)));', '((r,q),((p,(o,n)),((m,(l,(k,(j,i)))),((h,g),(z,(y,(x,(w,(v,(u,(t,s)))))))))));'],
        [28, True, '((((k,j),((i,(h,g)),(z,(y,x)))),(w,v)),(u,t),((s,(r,q)),(p,(o,(n,(m,l))))));', '(((z,y),(x,w)),(v,(u,(t,(s,(r,q))))),((p,o),((n,(m,(l,(k,(j,i))))),(h,g))));'],
        [18, True, '(((t,s),((r,(q,(p,o))),(n,m))),((l,(k,j)),((i,(h,g)),(z,y))),((x,w),(v,u)));', '((((l,k),(j,i)),(((h,g),(z,y)),(x,w))),((v,u),(t,s)),((r,q),((p,o),(n,m))));'],
        [26, True, '(((h,g),z),(y,(x,w)),((v,(u,(t,s))),((r,(q,p)),((o,(n,(m,l))),(k,(j,i))))));', '(((s,r),(q,p)),((o,n),(m,l)),(((k,j),((i,(h,g)),(z,(y,x)))),(w,(v,(u,t)))));'],
        [30, True, '(((x,w),((v,(u,(t,(s,(r,(q,(p,(o,n)))))))),((m,(l,k)),((j,i),(h,g))))),z,y);', '((((h,g),z),(y,x)),((w,v),((u,(t,s)),(r,q))),((p,(o,(n,(m,l)))),(k,(j,i))));'],
        [30, False, '(((v,(u,(t,(s,(r,q))))),((p,(o,(n,m))),((l,(k,(j,i))),(h,g)))),((z,y),(x,w)));', '(((v,u),((t,(s,(r,(q,(p,o))))),(n,(m,(l,(k,j)))))),((i,(h,g)),(z,(y,(x,w)))));'],
        [22, True, '(((z,y),((x,(w,v)),((u,(t,(s,r))),(q,(p,o))))),(n,m),((l,k),(j,(i,(h,g)))));', '(((r,q),(p,(o,(n,m)))),((l,(k,(j,(i,(h,g))))),(z,y)),((x,w),(v,(u,(t,s)))));'],
        [30, True, '(((x,w),((v,(u,(t,(s,r)))),(q,p))),((o,n),(m,l)),((k,j),((i,(h,g)),(z,y))));', '((((p,o),((n,(m,(l,k))),((j,i),(h,g)))),((z,y),(x,(w,v)))),(u,t),(s,(r,q)));'],
        [32, False, '(((r,(q,p)),(o,(n,m))),(((l,(k,(j,i))),(h,g)),((z,(y,(x,(w,(v,u))))),(t,s))));', '((((j,(i,(h,g))),(z,y)),(x,(w,(v,(u,t))))),(((s,r),(q,(p,o))),((n,m),(l,k))));'],
        [30, False, '((((q,p),((o,(n,(m,(l,k)))),((j,(i,(h,g))),(z,y)))),(x,w)),((v,u),(t,(s,r))));', '((((o,(n,m)),((l,(k,(j,i))),((h,g),z))),(y,x)),((w,v),((u,t),((s,r),(q,p)))));'],
        [28, False, '((((s,r),((q,(p,o)),(n,(m,l)))),((k,(j,i)),(h,g))),((z,(y,x)),(w,(v,(u,t)))));', '(((m,l),(k,j)),(((i,(h,g)),z),((y,x),((w,(v,(u,(t,(s,r))))),((q,p),(o,n))))));'],
        [20, True, '((((z,y),(x,(w,(v,u)))),((t,s),(r,q))),((p,o),(n,(m,l))),((k,(j,i)),(h,g)));', '(((j,i),(h,g)),(z,(y,x)),((w,(v,u)),((t,(s,(r,q))),((p,o),((n,m),(l,k))))));'],
        [20, False, '(((v,u),((t,s),(r,q))),(((p,o),(n,(m,l))),(((k,(j,i)),((h,g),z)),(y,(x,w)))));', '((((s,(r,q)),(p,o)),(((n,(m,l)),(k,(j,i))),((h,g),z))),((y,x),((w,v),(u,t))));'],
        [28, True, '((z,y),(x,w),((v,u),((t,(s,(r,q))),((p,(o,(n,m))),(l,(k,(j,(i,(h,g)))))))));', '((((r,q),((p,o),((n,m),((l,k),(j,i))))),((h,g),(z,(y,x)))),(w,v),(u,(t,s)));'],
        [24, False, '((((k,(j,(i,(h,g)))),(z,y)),(x,(w,v))),(((u,t),(s,(r,q))),((p,o),(n,(m,l)))));', '(((w,v),(u,(t,s))),(((r,(q,(p,o))),((n,m),(l,(k,(j,(i,(h,g))))))),(z,(y,x))));'],
        [24, True, '((((n,m),((l,(k,j)),(i,(h,g)))),(z,y)),(x,(w,v)),((u,(t,(s,(r,q)))),(p,o)));', '(((r,q),(p,o)),((n,(m,l)),((k,j),((i,(h,g)),z))),((y,x),(w,(v,(u,(t,s))))));']]

        # test RF exceptions
        t1 = Tree('(a,b,(c,d,e));')
        t2 = Tree('((a,b),(c,d,e));')
        # testing unrooted trees
        self.assertRaises(TreeError, t1.robinson_foulds, t2=t2)

        # expand polytomies and unrooted trees
        self.assertRaises(TreeError, t1.robinson_foulds, t2=t2,
                          unrooted_trees=True, expand_polytomies=True)

        # usisng expand_polytomies and correct_by_size at the same time
        self.assertRaises(TreeError, t1.robinson_foulds, t2=t1,
                          unrooted_trees=True, expand_polytomies=True,
                          correct_by_polytomy_size=True)

        # correct by size when polytomies in both sides
        self.assertRaises(TreeError, t1.robinson_foulds, t2=t1,
                          unrooted_trees=True, correct_by_polytomy_size=True)

        # polytomy larger than deafult limit
        self.assertRaises(TreeError, t2.robinson_foulds, t2=Tree('(a, (b,c,d,e,f,g,h));'),
                          expand_polytomies=True)

        # duplicated items
        t3 = Tree('(a, (b, (c, c)));')
        self.assertRaises(TreeError, t3.robinson_foulds, t2=t2)
        self.assertRaises(TreeError, t2.robinson_foulds, t2=t3)



        # test RF using a knonw set of results
        for RF, unrooted, nw1, nw2 in samples:
            t1 = Tree(nw1)
            t2 = Tree(nw2)
            rf, rf_max, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, unrooted_trees=unrooted)
            real_max = (20*2) - 4 if not unrooted else (20*2) - 6

            self.assertEqual(len(names), 20)
            self.assertEqual(rf_max, real_max)
            self.assertEqual(rf, RF)

            comp = t1.compare(t2, unrooted=unrooted)
            self.assertEqual(20, comp['effective_tree_size'])
            self.assertEqual(rf_max, comp['max_rf'])
            self.assertEqual(RF, comp['rf'])
            # Let's insert some random nodes, that should be ignored
            for target in random.sample([n for n in t2.descendants() if not n.is_leaf], 5):
                target.populate(5)
            comp = t1.compare(t2, unrooted=unrooted)
            self.assertEqual(20, comp['effective_tree_size'])
            self.assertEqual(rf_max, comp['max_rf'])
            self.assertEqual(RF, comp['rf'])

        # test treeko functionality
        t = PhyloTree('((((A,B),C), ((A,B),C)), (((A,B),C), ((A,B),C)));')
        ref = Tree('((A,B),C);')
        comp = t.compare(ref, has_duplications=True)

        self.assertEqual(comp['effective_tree_size'], 3)
        self.assertEqual(comp['treeko_dist'], 0.0)
        self.assertEqual(comp['norm_rf'], 0.0)
        self.assertEqual(comp['rf'], 0.0)
        self.assertEqual(comp['max_rf'], 2)
        self.assertEqual(comp['source_subtrees'], 4)

        # test polytomy corrections

        ref2 = Tree("((a:1, (b:1, c:1, d:1):1):1, (e:1, f:1, g:1):1);")
        gtree = Tree("((a:1, (b:1, (c:1, d:1):1):1), (e:1, (f:1, g:1):1):1);")

        # Basic polytomy
        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref2)
        self.assertEqual(rf, 2)
        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref2, expand_polytomies=True)
        self.assertEqual(rf, 0)


        # nested polytomies
        gtree = Tree('((g, h), (a, (b, (c, (d,( e, f))))));')
        ref3 = Tree('((a, b, c, (d, e, f)), (g, h));')
        ref4 = Tree('((a, b, c, d, e, f), (g, h));')
        ref5 = Tree('((a, b, (c, d, (e, f))), (g, h));')

        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref3)
        self.assertEqual(rf, 3)
        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref3, expand_polytomies=True)
        self.assertEqual(rf, 0)

        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref4)
        self.assertEqual(rf, 4)
        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref4, expand_polytomies=True,
                                                                  polytomy_size_limit=6)
        self.assertEqual(rf, 0)

        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref5)
        self.assertEqual(rf, 2)
        rf, max_rf, names, r1, r2, d1, d2 = gtree.robinson_foulds(ref5, expand_polytomies=True)
        self.assertEqual(rf, 0)

        # two side polytomies
        t1 = Tree("((a:1, (b:1, c:1, d:1):1):1, (e:1, f:1, g:1):1);")
        t2 = Tree("((a:1, (b:1, c:1, d:1):1), (e:1, (f:1, g:1):1):1);")
        rf, max_rf, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, expand_polytomies=True)
        self.assertEqual(rf, 0)


        # test auto pruned tree topology
        for RF, unrooted, nw1, nw2 in samples:
            # Add fake tips in the newick
            for x in "clanger":
                nw1 = nw1.replace(x, "(%s,%s1)" %(x, x) )
                nw2 = nw2.replace(x, "(%s,%s2)" %(x, x) )
            t1 = Tree(nw1)
            t2 = Tree(nw2)
            rf, rf_max, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, unrooted_trees=unrooted)
            self.assertEqual(len(names), 20)
            real_max = (20*2) - 4 if not unrooted else (20*2) - 6
            self.assertEqual(rf_max, real_max)
            self.assertEqual(rf, RF)

        # TODO: Fix the tests from this line to the end of this function.
        # # Testing RF with branch support thresholds.
        # # test discarding lowly supported branches
        # for RF, unrooted, nw1, nw2 in samples:
        #     # Add fake internal nodes with low support
        #     for x in "jlnqr":
        #         nw1 = nw1.replace(x, "(%s,(%s1, %s11)0.6)" %(x, x, x) )
        #         nw2 = nw2.replace(x, "(%s,(%s1, %s11)0.5)" %(x, x, x) )
        #     t1 = Tree(nw1, parser=0)
        #     t2 = Tree(nw2, parser=0)
        #     rf, rf_max, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, unrooted_trees=unrooted,
        #                                                            min_support_t1 = 0.1, min_support_t2 = 0.1)
        #     self.assertEqual(len(names), 30)
        #     real_max = (30*2) - 4 if not unrooted else (30*2) - 6
        #     self.assertEqual(rf_max, real_max)
        #     self.assertEqual(rf, RF)

        #     rf, rf_max, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, unrooted_trees=unrooted,
        #                                                            min_support_t1 = 0.0, min_support_t2 = 0.51)
        #     self.assertEqual(len(names), 30)
        #     real_max = (30*2) - 4 - 5 if not unrooted else (30*2) - 6 -5 # -5 to discount low support branches
        #     self.assertEqual(rf_max, real_max)
        #     self.assertEqual(rf, RF)

        #     rf, rf_max, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, unrooted_trees=unrooted,
        #                                                            min_support_t1 = 0.61, min_support_t2 = 0.0)
        #     self.assertEqual(len(names), 30)
        #     real_max = (30*2) - 4 - 5 if not unrooted else (30*2) - 6 -5 # -5 to discount low support branches
        #     self.assertEqual(rf_max, real_max)
        #     self.assertEqual(rf, RF)


        #     rf, rf_max, names, r1, r2, d1, d2 = t1.robinson_foulds(t2, unrooted_trees=unrooted,
        #                                                            min_support_t1 = 0.61, min_support_t2 = 0.51)
        #     self.assertEqual(len(names), 30)
        #     real_max = (30*2) - 4 - 10 if not unrooted else (30*2) - 6 -10 # -10 to discount low support branches
        #     self.assertEqual(rf_max, real_max)
        #     self.assertEqual(rf, RF)

    # TODO: Fix the check_monophyly() function and this test.
    def test_monophyly(self):
        """Checks for monophyletic, paraphyletic, and polyphyletic groups."""
        t = Tree("((((((a, e), i), o),h), u), ((f, g), j));")
        #          ╭─┬╴a
        #        ╭─┤ ╰╴e
        #      ╭─┤ ╰╴i
        #    ╭─┤ ╰╴o
        #  ╭─┤ ╰╴h
        # ─┤ ╰╴u
        #  │ ╭─┬╴f
        #  ╰─┤ ╰╴g
        #    ╰╴j

        is_mono, monotype, extra  = t.check_monophyly(values=['a', 'e', 'i', 'o', 'u'])
        self.assertEqual(is_mono, False)
        self.assertEqual(monotype, 'paraphyletic')

        is_mono, monotype, extra= t.check_monophyly(values=['a', 'e', 'i', 'o'])
        self.assertEqual(is_mono, True)
        self.assertEqual(monotype, 'monophyletic')

        is_mono, monotype, extra =  t.check_monophyly(values=['i', 'o'])
        self.assertEqual(is_mono, False)
        self.assertEqual(monotype, 'paraphyletic')

        # Now with unrooted trees, and using species instead of names.
        t = PhyloTree('(aaa1, (aaa3, (aaa4, (bbb1, bbb2))));',
                      sp_naming_function=lambda name: name[:3])
        # ─┬╴aaa1        # the species will be 'aaa' for this node, etc.
        #  ╰─┬╴aaa3
        #    ╰─┬╴aaa4
        #      ╰─┬╴bbb1
        #        ╰╴bbb2

        self.assertEqual(t.check_monophyly(values={'aaa'},
                                           prop='species', unrooted=True),
                         (True, 'monophyletic', set()))

        # Variations on that tree.
        t = PhyloTree('(aaa1, (bbb3, (aaa4, (bbb1, bbb2))));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'aaa'},
                                              prop='species', unrooted=True)
        self.assertFalse(is_mono)
        self.assertEqual(extra, {t['bbb3']})

        t = PhyloTree('(aaa1, (aaa3, (aaa4, (bbb1, bbb2))));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'bbb'},
                                              prop='species', unrooted=True)
        self.assertTrue(is_mono)
        self.assertEqual(extra, set())

        t = PhyloTree('(aaa1, (aaa3, (aaa4, (bbb1, ccc2))));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'bbb', 'ccc'},
                                              prop='species', unrooted=True)
        self.assertTrue(is_mono)
        self.assertEqual(extra, set())

        t = PhyloTree('(aaa1, (aaa3, (bbb4, (bbb1, bbb2))));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'bbb4', 'bbb2'},
                                              prop='name', unrooted=True)
        self.assertFalse(is_mono)
        self.assertEqual(extra, {t['bbb1']})

        t = PhyloTree('(aaa1, (aaa3, (bbb4, (bbb1, bbb2))));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'bbb1', 'bbb2'},
                                              prop='name', unrooted=True)
        self.assertTrue(is_mono)
        self.assertEqual(extra, set())

        t = PhyloTree('(aaa1, aaa3, (aaa4, (bbb1, bbb2)));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'aaa'},
                                              prop='species', unrooted=True)
        self.assertTrue(is_mono)
        self.assertEqual(extra, set())

        t = PhyloTree('(aaa1, bbb3, (aaa4, (bbb1, bbb2)));',
                      sp_naming_function=lambda name: name[:3])
        is_mono, _, extra = t.check_monophyly(values={'aaa'},
                                              prop='species', unrooted=True)
        self.assertFalse(is_mono)
        self.assertEqual(extra, {t['bbb3']})

        # # Check monophyly randomization test
        # t = PhyloTree(,
        # t.populate(100)
        # ancestor = t.common_ancestor(['aaaaaaaaaa', 'aaaaaaaaab', 'aaaaaaaaac'])
        # all_nodes = list(t.descendants())
        # # I test every possible node as root for the tree. The content of ancestor
        # # should allways be detected as monophyletic
        # results = set()
        # for x in all_nodes:
        #     mono, part, extra = t.check_monophyly(values=set(ancestor.leaf_names()), prop='name', unrooted=True)
        #     results.add(mono)
        #     t.set_outgroup(x)
        # self.assertEqual(list(results), [True])

        # TODO: The previous test looks like it is wrong. Review with Jaime.

        # Testing get_monophyly
        t = Tree('((((((4, e), i)M1, o),h), u), ((3, 4), (i, june))M2);',
                 parser=1)
        # we annotate the tree using external data
        colors = {'a': 'red', 'e': 'green', 'i': 'yellow',
                  'o': 'black', 'u': 'purple', '4':'green',
                  '3': 'yellow', '1': 'white', '5': 'red',
                  'june': 'yellow'}
        for leaf in t:
            leaf.add_props(color=colors.get(leaf.name, 'none'))
        green_yellow_nodes = {t['M1'], t['M2']}
        mono_nodes = t.get_monophyletic(values=['green', 'yellow'],
                                        prop='color')
        self.assertEqual(set(mono_nodes), green_yellow_nodes)

    def test_copy(self):
        t = Tree("((A, B)Internal_1:0.7, (C, D)Internal_2:0.5)root:1.3;",
                 parser=1)
        # we add a custom annotation to the node named A
        t['A'].add_props(label="custom Value")
        # we add a complex feature to the A node, consisting of a list of lists
        t['A'].add_props(complex=[[0,1], [2,3], [1,11], [1,0]])

        nw2 = t.write(props=None, format_root_node=True, parser=1)

        t_nw  = t.copy("newick")
        t_nwx = t.copy("newick-extended")
        t_pkl = t.copy("cpickle")
        t['A'].props['testfn'] = lambda: "YES"
        t_deep = t.copy("deepcopy")

        self.assertEqual((t_nw["root"]).name, "root")
        self.assertEqual((t_nwx["A"]).props['label'], "custom Value")
        self.assertEqual((t_pkl["A"]).props['complex'][0], [0,1])
        self.assertEqual((t_deep["A"]).props['testfn'](), "YES")

    def test_cophenetic_matrix(self):
        t = Tree(ds.nw_full)
        dists, leaves = t.cophenetic_matrix()
        actualdists = [
            [0, 2.3662779999999994, 2.350554999999999, 2.7002369999999996, 3.527812, 3.305472, 2.424086, 2.424086,
             2.432288, 2.483421, 2.3355079999999995, 2.3355079999999995, 2.389350999999999, 2.3812519999999995,
             2.404005999999999, 2.3945459999999996, 2.4035289999999994, 2.3689599999999995, 2.4048339999999997,
             2.6487609999999995],
            [2.3662779999999994, 0, 0.079009, 1.122461, 2.38897, 2.16663, 0.47755000000000003, 0.47755000000000003,
             0.4857520000000001, 0.5368850000000001, 0.320202, 0.32020200000000004, 0.133729, 0.12563,
             0.14838400000000002, 0.230406, 0.168047, 0.113338, 0.16935199999999997, 0.633455],
            [2.350554999999999, 0.079009, 0, 1.106738, 2.373247, 2.150907, 0.461827, 0.461827, 0.47002900000000003,
             0.521162, 0.304479, 0.30447900000000006, 0.11800599999999999, 0.10990699999999998, 0.132661, 0.214683,
             0.152324, 0.09761499999999998, 0.153629, 0.617732],
            [2.7002369999999996, 1.122461, 1.106738, 0, 2.7229289999999997, 2.5005889999999997, 1.180269, 1.180269,
             1.188471, 1.239604, 1.091691, 1.091691, 1.145534, 1.137435, 1.160189, 1.1507290000000001, 1.159712,
             1.125143, 1.161017, 1.404944],
            [3.527812, 2.38897, 2.373247, 2.7229289999999997, 0, 2.6926, 2.446778, 2.446778, 2.45498, 2.506113,
             2.3581999999999996, 2.3581999999999996, 2.412043, 2.403944, 2.426698, 2.4172379999999998,
             2.4262209999999995, 2.391652, 2.427526, 2.6714529999999996],
            [3.305472, 2.16663, 2.150907, 2.5005889999999997, 2.6926, 0, 2.224438, 2.224438, 2.23264, 2.283773, 2.13586,
             2.13586, 2.189703, 2.181604, 2.204358, 2.194898, 2.2038809999999995, 2.169312, 2.205186, 2.449113],
            [2.424086, 0.47755000000000003, 0.461827, 1.180269, 2.446778, 2.224438, 0, 0.0, 0.01366,
             0.30963300000000005, 0.44678, 0.44677999999999995, 0.5006229999999999, 0.49252399999999996, 0.515278,
             0.505818, 0.5148010000000001, 0.480232, 0.5161060000000001, 0.7600329999999998],
            [2.424086, 0.47755000000000003, 0.461827, 1.180269, 2.446778, 2.224438, 0.0, 0, 0.01366,
             0.30963300000000005, 0.44678, 0.44677999999999995, 0.5006229999999999, 0.49252399999999996, 0.515278,
             0.505818, 0.5148010000000001, 0.480232, 0.5161060000000001, 0.7600329999999998],
            [2.432288, 0.4857520000000001, 0.47002900000000003, 1.188471, 2.45498, 2.23264, 0.01366, 0.01366, 0,
             0.317835, 0.45498200000000005, 0.454982, 0.508825, 0.500726, 0.5234800000000001, 0.51402, 0.523003,
             0.48843400000000003, 0.524308, 0.7682349999999999],
            [2.483421, 0.5368850000000001, 0.521162, 1.239604, 2.506113, 2.283773, 0.30963300000000005,
             0.30963300000000005, 0.317835, 0, 0.506115, 0.506115, 0.559958, 0.551859, 0.574613, 0.565153, 0.574136,
             0.539567, 0.5754410000000001, 0.8193679999999999],
            [2.3355079999999995, 0.320202, 0.304479, 1.091691, 2.3581999999999996, 2.13586, 0.44678, 0.44678,
             0.45498200000000005, 0.506115, 0, 0.0, 0.343275, 0.33517600000000003, 0.35793, 0.34847,
             0.35745299999999997, 0.322884, 0.35875799999999997, 0.531709],
            [2.3355079999999995, 0.32020200000000004, 0.30447900000000006, 1.091691, 2.3581999999999996, 2.13586,
             0.44677999999999995, 0.44677999999999995, 0.454982, 0.506115, 0.0, 0, 0.34327500000000005,
             0.33517600000000003, 0.35793, 0.34847, 0.357453, 0.32288400000000006, 0.358758, 0.531709],
            [2.389350999999999, 0.133729, 0.11800599999999999, 1.145534, 2.412043, 2.189703, 0.5006229999999999,
             0.5006229999999999, 0.508825, 0.559958, 0.343275, 0.34327500000000005, 0, 0.013558999999999998, 0.021967,
             0.25347900000000007, 0.19112, 0.031257, 0.192425, 0.656528],
            [2.3812519999999995, 0.12563, 0.10990699999999998, 1.137435, 2.403944, 2.181604, 0.49252399999999996,
             0.49252399999999996, 0.500726, 0.551859, 0.33517600000000003, 0.33517600000000003, 0.013558999999999998, 0,
             0.028214, 0.24538000000000004, 0.183021, 0.023157999999999998, 0.184326, 0.648429],
            [2.404005999999999, 0.14838400000000002, 0.132661, 1.160189, 2.426698, 2.204358, 0.515278, 0.515278,
             0.5234800000000001, 0.574613, 0.35793, 0.35793, 0.021967, 0.028214, 0, 0.26813400000000004,
             0.20577499999999999, 0.045912, 0.20708, 0.6711830000000001],
            [2.3945459999999996, 0.230406, 0.214683, 1.1507290000000001, 2.4172379999999998, 2.194898, 0.505818,
             0.505818, 0.51402, 0.565153, 0.34847, 0.34847, 0.25347900000000007, 0.24538000000000004,
             0.26813400000000004, 0, 0.267657, 0.233088, 0.268962, 0.661723],
            [2.4035289999999994, 0.168047, 0.152324, 1.159712, 2.4262209999999995, 2.2038809999999995,
             0.5148010000000001, 0.5148010000000001, 0.523003, 0.574136, 0.35745299999999997, 0.357453, 0.19112,
             0.183021, 0.20577499999999999, 0.267657, 0, 0.170729, 0.057269, 0.670706],
            [2.3689599999999995, 0.113338, 0.09761499999999998, 1.125143, 2.391652, 2.169312, 0.480232, 0.480232,
             0.48843400000000003, 0.539567, 0.322884, 0.32288400000000006, 0.031257, 0.023157999999999998, 0.045912,
             0.233088, 0.170729, 0, 0.17203399999999996, 0.636137],
            [2.4048339999999997, 0.16935199999999997, 0.153629, 1.161017, 2.427526, 2.205186, 0.5161060000000001,
             0.5161060000000001, 0.524308, 0.5754410000000001, 0.35875799999999997, 0.358758, 0.192425, 0.184326,
             0.20708, 0.268962, 0.057269, 0.17203399999999996, 0, 0.672011],
            [2.6487609999999995, 0.633455, 0.617732, 1.404944, 2.6714529999999996, 2.449113, 0.7600329999999998,
             0.7600329999999998, 0.7682349999999999, 0.8193679999999999, 0.531709, 0.531709, 0.656528, 0.648429,
             0.6711830000000001, 0.661723, 0.670706, 0.636137, 0.672011, 0]
        ]

        actualleaves = ['Aga0007658', 'Bta0018700', 'Cfa0016700', 'Cin0011239', 'Ddi0002240', 'Dme0014628',
                        'Dre0008390', 'Dre0008391', 'Dre0008392', 'Fru0004507', 'Gga0000981', 'Gga0000982',
                        'Hsa0000001', 'Hsa0010711', 'Hsa0010730', 'Mdo0014718', 'Mms0024821', 'Ptr0000001',
                        'Rno0030248', 'Xtr0044988']

        for i in range(len(actualdists)):
            for j in range(len(actualdists[i])):
                self.assertAlmostEqual(actualdists[i][j], dists[i][j], places=4)
        self.assertEqual(actualleaves, leaves)


if __name__ == '__main__':
    unittest.main()
