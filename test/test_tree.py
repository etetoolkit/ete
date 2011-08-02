import unittest
import random
import sys
import time

from ete_dev import *
from datasets import *
 
class Test_Coretype_Tree(unittest.TestCase):
    """ Tests tree basics. """
    def test_tree_read_and_write(self):
        """ Tests newick support """
        # Read and write newick tree from file (and support for NHX
        # format): newick parser
        open("/tmp/etetemptree.nw","w").write(nw_full)
        t = Tree("/tmp/etetemptree.nw")
        self.assertEqual(nw_full, t.write(features=["flag","mood"]))
        self.assertEqual(nw_topo,  t.write(format=9))
        self.assertEqual(nw_dist, t.write(format=5))

        # Read and write newick tree from *string* (and support for NHX
        # format)
        t = Tree(nw_full)
        self.assertEqual(nw_full, t.write(features=["flag","mood"]))
        self.assertEqual(nw_topo, t.write(format=9))
        self.assertEqual( nw_dist, t.write(format=5))

        # Read complex newick
        t = Tree(nw2_full)
        self.assertEqual(nw2_full,  t.write())

        # Read wierd topologies
        t = Tree(nw_simple5)
        self.assertEqual(nw_simple5,  t.write(format=9))
        t = Tree(nw_simple6)
        self.assertEqual(nw_simple6,  t.write(format=9))


    def test_newick_formats(self):
        """ tests different newick subformats """
        from ete_dev.parser.newick import print_supported_formats, NW_FORMAT
        print_supported_formats()

        # Let's stress a bit
        for i in xrange(10):
            t = Tree()
            t.populate(50)
            for f in NW_FORMAT:
                self.assertEqual(t.write(format=f), Tree(t.write(format=f),format=f).write(format=f))

        nw0 = "((A:0.813705,(E:0.545591,D:0.411772)1.000000:0.137245)1.000000:0.976306,C:0.074268);"
        nw1 = "((A:0.813705,(E:0.545591,D:0.411772)B:0.137245)A:0.976306,C:0.074268);"
        nw2 = "((A:0.813705,(E:0.545591,D:0.411772)1.000000:0.137245)1.000000:0.976306,C:0.074268);"
        nw3 = "((A:0.813705,(E:0.545591,D:0.411772)B:0.137245)A:0.976306,C:0.074268);"
        nw4 = "((A:0.813705,(E:0.545591,D:0.411772)),C:0.074268);"
        nw5 = "((A:0.813705,(E:0.545591,D:0.411772):0.137245):0.976306,C:0.074268);"
        nw6 = "((A:0.813705,(E:0.545591,D:0.411772)B)A,C:0.074268);"
        nw7 = "((A,(E,D)B)A,C);"
        nw8 = "((A,(E,D)),C);"
        nw9 = "((,(,)),);"


    def test_tree_manipulation(self):
        """ tests operations which modify tree topology """
        nw_tree = "((NoName:1,Turtle:1.3)1:1,(A:0.3,B:2.4)1:0.43);"

        # Manipulate Topologys
        # Adding and removing nodes (add_child, remove_child,
        # add_sister, remove_sister). The resulting neiwck tree should
        # match the nw_tree defined before.
        t = Tree()
        c1 = t.add_child()
        c2 = t.add_child(dist=0.43)
        n = TreeNode()
        _n = c1.add_child(n)
        c3 = _n.add_sister(name="Turtle", dist="1.3")
        c4 = c2.add_child(name="A", dist="0.3")

        c5 = c2.add_child(name="todelete")
        _c5 = c2.remove_child(c5)

        c6 = c2.add_child(name="todelete")
        _c6 = c4.remove_sister(c6)

        c7 = c2.add_child(name="B", dist=2.4)

        self.assertEqual(nw_tree, t.write())
        self.assertEqual(_c5, c5)
        self.assertEqual(_c6, c6)
        self.assertEqual(_n, n)

        # Delete,
        t = Tree("(((A, B), C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D = t.search_nodes(name="D")[0]
        F = t.search_nodes(name="F")[0]
        J = t.search_nodes(name="J")[0]
        root = t.search_nodes(name="root")[0]
        J.delete()
        self.assertEqual(J.up, None)
        self.assertEqual(J in t, False)
        self.assertEqual(D.up, root)
        self.assertEqual(F.up, root)

        #detach
        t = Tree("(((A, B)[&&NHX:name=H], C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D = t.search_nodes(name="D")[0]
        F = t.search_nodes(name="F")[0]
        J = t.search_nodes(name="J")[0]
        root = t.search_nodes(name="root")[0]
        J.detach()
        self.assertEqual(J.up, None)
        self.assertEqual(J in t, False)
        self.assertEqual(set([n.name for n in t.iter_descendants()]),set(["A","B","C","I","H"]))

        #prune
        t1 = Tree()
        t1.populate(50)
        t1.ladderize()
        t1.ladderize(1)

        #prune
        t1 = Tree("(((A, B), C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D1 = t1.search_nodes(name="D")[0]
        t1.prune(["A","C", D1])
        sys.stdout.flush()
        self.assertEqual(set([n.name for n in t1.iter_descendants()]),  set(["A","C","D","I"]))
        
        t1 = Tree("(((A, B), C)[&&NHX:name=I], (D, F)[&&NHX:name=J])[&&NHX:name=root];")
        D1 = t1.search_nodes(name="D")[0]
        t1.prune(["A","B"])
        self.assertEqual( t1.write(), "(A:1,B:1);")

        
        t_fuzzy = Tree("(((A,B), C),(D,E));")
        orig_nw = t_fuzzy.write()
        ref_nodes = t_fuzzy.get_leaves()
        t_fuzzy.populate(100)
        t_fuzzy.prune(ref_nodes)
        self.assertEqual(t_fuzzy.write(),orig_nw)
        # Total number of nodes is correct (no single child nodes)
        self.assertEqual(len(t_fuzzy.get_descendants()), (len(ref_nodes)*2)-2 )

        t = Tree()
        sample_size = 5
        t.populate(10000)
        sample = random.sample(t.get_leaves(), sample_size)
        t.prune(sample)
        self.assertEqual(len(t), sample_size)
        self.assertEqual(len(t.get_descendants()), (sample_size*2)-2 )
       
        # getting nodes, get_childs, get_sisters, get_tree_root,
        # get_common_ancestor, get_nodes_by_name
        # get_descendants_by_name, is_leaf, is_root
        t = Tree("(((A,B),C)[&&NHX:tag=common],D)[&&NHX:tag=root:name=root];")
        A = t.search_nodes(name="A")[0]
        B = t.search_nodes(name="B")[0]
        C = t.search_nodes(name="C")[0]
        root = (t&"root")
        self.assertEqual("A", A.name)

        common  = A.get_common_ancestor(C)
        self.assertEqual("common", common.tag)

        common  = A.get_common_ancestor(C, B)
        self.assertEqual("common", common.tag)

        self.assertEqual(root, t.get_common_ancestor([A, "D"]))

        self.assertEqual("root", A.get_tree_root().tag)
        self.assertEqual("root", B.get_tree_root().tag)
        self.assertEqual("root", C.get_tree_root().tag)
        self.assertEqual("root", common.get_tree_root().tag)

        self.assert_(common.get_tree_root().is_root())
        self.assert_(not A.is_root())
        self.assert_(A.is_leaf())
        self.assert_(not A.get_tree_root().is_leaf())

        # Tree magic python features
        t = Tree(nw_dflt)
        self.assertEqual(len(t), 20)
        self.assert_("Ddi0002240" in t)
        self.assert_(t.children[0] in t)
        for a in t:
            self.assert_(a.name)

        # Populate
        t = Tree(nw_full)
        prev_size= len(t)
        t.populate(25)
        self.assertEqual(len(t), prev_size+25)
        for i in xrange(10):
            t = Tree()
            t.populate(100, reuse_names=False)
            # Checks that all names are actually unique 
            self.assertEqual(len(set(t.get_leaf_names())), 100) 
       
        # Adding and removing features
        t = Tree("(((A,B),C)[&&NHX:tag=common],D)[&&NHX:tag=root];")
        A = t.search_nodes(name="A")[0]

        # Iterators, get_leaves, get_leaf_names
        t = Tree(nw2_full)
        self.assert_(t.get_leaf_names(), [name for name in  t.iter_leaf_names()])
        self.assert_(t.get_leaves(), [name for name in  t.iter_leaves()])
        self.assert_(t.get_descendants(), [n for n in  t.iter_descendants()])

        self.assertEqual(set([n for n in t.traverse("preorder")]), \
                             set([n for n in t.traverse("postorder")]))
        self.assert_(t in set([n for n in t.traverse("preorder")]))

        # Swap childs
        n = t.get_children()
        t.swap_children()
        n.reverse()
        self.assertEqual(n, t.get_children())

        # Distances: get_distance, get_farthest_node,
        # get_farthest_descendant, get_midpoint_outgroup
        t = Tree("(((A:0.1, B:0.01):0.001, C:0.0001):1.0[&&NHX:name=I], (D:0.00001):0.000001[&&NHX:name=J]):2.0[&&NHX:name=root];")
        A = t.search_nodes(name="A")[0]
        B = t.search_nodes(name="B")[0]
        C = t.search_nodes(name="C")[0]
        D = t.search_nodes(name="D")[0]
        I = t.search_nodes(name="I")[0]
        J = t.search_nodes(name="J")[0]
        root = t.search_nodes(name="root")[0]

        self.assertEqual(A.get_common_ancestor(I).name, "I")
        self.assertEqual(A.get_common_ancestor(D).name, "root")
        self.assertEqual(A.get_distance(I), 0.101)
        self.assertEqual(A.get_distance(B), 0.11)
        self.assertEqual(A.get_distance(A), 0)
        self.assertEqual(I.get_distance(I), 0)
        self.assertEqual(A.get_distance(root), root.get_distance(A))

        # Get_farthest_node, get_farthest_leaf
        self.assertEqual(root.get_farthest_leaf(), (A,1.101) )
        self.assertEqual(root.get_farthest_node(), (A,1.101) )
        self.assertEqual(A.get_farthest_leaf(), (A, 0.0))
        self.assertEqual(A.get_farthest_node(), (D, 1.101011))
        self.assertEqual(I.get_farthest_node(), (D, 1.000011))

        # Test set_outgroup and get_midpoint_outgroup
        t = Tree(nw2_full)
        YGR028W = t.get_leaves_by_name("YGR028W")[0]
        YGR138C = t.get_leaves_by_name("YGR138C")[0]
        d1 = YGR138C.get_distance(YGR028W)
        nodes = t.get_descendants()
        t.set_outgroup(t.get_midpoint_outgroup())
        o1, o2 = t.children[0], t.children[1]
        nw_original = t.write()
        d2 = YGR138C.get_distance(YGR028W)
        self.assertEqual(d1, d2)
        # Randomizing outgroup test: Can we recover original state
        # after many manipulations?
        for i in xrange(10):
            for j in xrange(1000):
                n = random.sample(nodes, 1)[0]
                if n is None:
                    print "NONE"
                t.set_outgroup(n)
            t.set_outgroup(t.get_midpoint_outgroup())
            self.assertEqual(set([t.children[0], t.children[1]]), set([o1, o2]))
            ##  I need to sort branches first
            #self.assertEqual(t.write(), nw_original) 
        d3 = YGR138C.get_distance(YGR028W)
        self.assertEqual(d1, d3)
          
    def test_rooting(self):
        """ Check branch support and distances after rooting """

        t = Tree("((((a,b)1,c)2,i)3,(e,d)4)5;", format=1)
        t.set_outgroup(t&"a")


        t = Tree("(((a,b)2,c)x)9;", format=1)
        t.set_outgroup(t&"a")

        # Test branch support and distances after rooting
        SIZE = 35
        t = Tree()
        t.populate(SIZE, reuse_names=False)
        t.unroot()
        for n in t.iter_descendants():
            if n is not t:
                n.support = random.random()
                n.dist = random.random()
        for n in t.children:
            n.support = 0.999
        t2 = t.copy()
        
        names = set(t.get_leaf_names())
        cluster_id2support = {}
        cluster_id2dist = {}
        for n in t.traverse():
            cluster_names = set(n.get_leaf_names())
            cluster_names2 = names - cluster_names
            cluster_id = '_'.join(sorted(cluster_names))
            cluster_id2 = '_'.join(sorted(cluster_names2))
            cluster_id2support[cluster_id] = n.support
            cluster_id2support[cluster_id2] = n.support

            cluster_id2dist[cluster_id] = n.dist
            cluster_id2dist[cluster_id2] = n.dist

            
        for i in xrange(100):
            outgroup = random.sample(t2.get_descendants(), 1)[0]
            t2.set_outgroup(outgroup)
            for n in t2.traverse():
                cluster_names = set(n.get_leaf_names())
                cluster_names2 = names - cluster_names
                cluster_id = '_'.join(sorted(cluster_names))
                cluster_id2 = '_'.join(sorted(cluster_names2))
                self.assertEqual(cluster_id2support.get(cluster_id, None), n.support)
                self.assertEqual(cluster_id2support.get(cluster_id2, None), n.support)
                if n.up and n.up.up:
                    self.assertEqual(cluster_id2dist.get(cluster_id, None), n.dist)
                    
                    
        # Test unrooting
        t = Tree()
        t.populate(20)
        t.unroot()
        # Ascii
        t.get_ascii()

    def test_ultrametric(self):
        t =  Tree()
        # Creates a random tree (not ultrametric)
        t.populate(100)

        # Convert tree to a ultrametric topology in which distance from
        # leaf to root is always 100. Two strategies are available:
        # balanced or fixed
        t.convert_to_ultrametric(200, "balanced")

        # Print distances from all leaves to root. Due to precision issues
        # with the float type.  Branch lengths may show differences at
        # high precision levels, that's way I round to 6 decimal
        # positions.
        dist = set([round(l.get_distance(t), 6) for l in t.iter_leaves()])
        self.assertEqual(dist, set([200.0]))

    def test_traversing_speed(self):
        return
        for x in xrange(10):
            t = Tree()
            t.populate(100000)

            leaves = t.get_leaves()
            sample = random.sample(leaves, 100)

            t1 = time.time()
            a = t.get_common_ancestor_OLD(sample)
            t2 = time.time() - t1
            print "OLD get common", t2

            t1 = time.time()
            b = t.get_common_ancestor(sample)
            t2 = time.time() - t1
            print "NEW get common", t2

            self.assertEqual(a, b)


            t1 = time.time()
            [n for n in t._iter_descendants_postorder_OLD()]
            t2 = time.time() - t1
            print "OLD postorder", t2

            t1 = time.time()
            [n for n in t._iter_descendants_postorder()]
            t2 = time.time() - t1
            print "NEW postorder", t2

