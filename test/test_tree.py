import unittest
import random
import sys
import time
import itertools

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

        #Read single node trees:
        self.assertEqual(Tree("hola;").write(format=9),  "hola;")
        self.assertEqual(Tree("(hola);").write(format=9),  "(hola);")

        #TEst export root features
        t = Tree("(((A[&&NHX:name=A],B[&&NHX:name=B])[&&NHX:name=NoName],C[&&NHX:name=C])[&&NHX:name=I],(D[&&NHX:name=D],F[&&NHX:name=F])[&&NHX:name=J])[&&NHX:name=root];")
        self.assertEqual(t.write(format=9, features=["name"], format_root_node=True),
                         "(((A[&&NHX:name=A],B[&&NHX:name=B])[&&NHX:name=NoName],C[&&NHX:name=C])[&&NHX:name=I],(D[&&NHX:name=D],F[&&NHX:name=F])[&&NHX:name=J])[&&NHX:name=root];")
        
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
        nw_tree = "((Hola:1,Turtle:1.3)1:1,(A:0.3,B:2.4)1:0.43);"

        # Manipulate Topologys
        # Adding and removing nodes (add_child, remove_child,
        # add_sister, remove_sister). The resulting neiwck tree should
        # match the nw_tree defined before.
        t = Tree()
        c1 = t.add_child(dist=1, support=1)
        c2 = t.add_child(dist=0.43, support=1)
        n = TreeNode(name="Hola", dist=1, support=1)
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

        # test prune preserving distances
        for i in xrange(3):
            t = Tree()
            t.populate(50, random_branches=True)
            distances = {}
            for a in t.iter_leaves():
                for b in t.iter_leaves():
                    distances[(a,b)] = round(a.get_distance(b), 10)

            to_keep = set(random.sample(t.get_leaves(), 10))
            t.prune(to_keep, preserve_branch_length=True)
            for a,b in distances:
                if a in to_keep and b in to_keep:
                    self.assertEqual(distances[(a,b)], round(a.get_distance(b), 10))

        # Total number of nodes is correct (no single child nodes)                    
        t_fuzzy = Tree("(((A,B), C),(D,E));")
        orig_nw = t_fuzzy.write()
        ref_nodes = t_fuzzy.get_leaves()
        t_fuzzy.populate(100)
        t_fuzzy.prune(ref_nodes)
        self.assertEqual(t_fuzzy.write(),orig_nw)
        self.assertEqual(len(t_fuzzy.get_descendants()), (len(ref_nodes)*2)-2 )

        # Total number of nodes is correct (no single child nodes)
        t = Tree()
        sample_size = 5
        t.populate(1000)
        sample = random.sample(t.get_leaves(), sample_size)
        t.prune(sample)
        self.assertEqual(len(t), sample_size)
        self.assertEqual(len(t.get_descendants()), (sample_size*2)-2 )

        # TEst preserve branch dist when pruning
        t = Tree()
        t.populate(100, random_branches=True)
        orig_leaves = t.get_leaves()
        sample_size = 50
        sample= random.sample(t.get_leaves(), sample_size)
        matrix1 = ["%f" %t.get_distance(a, b) for (a,b) in itertools.product(sample, sample)]
        t.prune(sample, preserve_branch_length=True)
        matrix2 = ["%f" %t.get_distance(a, b) for (a,b)in itertools.product(sample, sample)]
       
        self.assertListEqual(matrix1, matrix2)
        self.assertEqual(len(t.get_descendants()), (sample_size*2)-2 )

        # resolve polytomy
        t = Tree("((a,a,a,a), (b,b,b,(c,c,c)));")
        t.resolve_polytomy()
        t.ladderize()
        self.assertEqual(t.write(format=9), "((a,(a,(a,a))),(b,(b,(b,(c,(c,c))))));")
              
        
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


        # Iter ancestors
        t = Tree("(((((a,b)A,c)B,d)C,e)D,f)root;", format=1)
        ancestor_names = [n.name for n in (t&"a").get_ancestors()]
        self.assertListEqual(ancestor_names, ["A", "B", "C", "D", "root"])
        ancestor_names = [n.name for n in (t&"B").get_ancestors()]
        self.assertListEqual(ancestor_names, ["C", "D", "root"])

        
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

        # Check gettters and itters return the same
        t = Tree(nw2_full)
        self.assert_(t.get_leaf_names(), [name for name in  t.iter_leaf_names()])
        self.assert_(t.get_leaves(), [name for name in  t.iter_leaves()])
        self.assert_(t.get_descendants(), [n for n in  t.iter_descendants()])

        self.assertEqual(set([n for n in t.traverse("preorder")]), \
                             set([n for n in t.traverse("postorder")]))
        self.assert_(t in set([n for n in t.traverse("preorder")]))

        # Check order or visiting nodes

        t = Tree("((3,4)2,(6,7)5)1;", format=1)
        #t = Tree("(((A, B)C, (D, E)F)G, (H, (I, J)K)L)M;", format=1)
        #postorder = [c for c in "ABCDEFGHIJKLM"]
        #preorder =  [c for c in reversed(postorder)]
        #levelorder = [c for c in "MGLCFHKABDEIJ"]
        postorder = "3426751"
        preorder = "1234567"
        levelorder = "1253467"
                
        self.assertEqual(preorder, 
                          ''.join([n.name for n in t.traverse("preorder")]))

        self.assertEqual(postorder, 
                         ''.join([n.name for n in t.traverse("postorder")]))

        self.assertEqual(levelorder, 
                         ''.join([n.name for n in t.traverse("levelorder")]))

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


    def test_tree_navigation(self):
        t = Tree("(((A, B)H, C)I, (D, F)J)root;", format=1)
        postorder = [n.name for n in t.traverse("postorder")]
        preorder = [n.name for n in t.traverse("preorder")]
        levelorder = [n.name for n in t.traverse("levelorder")]

        self.assertEqual(postorder, ['A', 'B', 'H', 'C', 'I', 'D', 'F', 'J', 'root'])
        self.assertEqual(preorder, ['root', 'I', 'H', 'A', 'B', 'C', 'J', 'D', 'F'])
        self.assertEqual(levelorder, ['root', 'I', 'J', 'H', 'C', 'D', 'F', 'A', 'B'])
        ancestors = [n.name for n in (t&"B").get_ancestors()]
        self.assertEqual(ancestors, ["H", "I", "root"])
        self.assertEqual(t.get_ancestors(), [])

        # add something of is_leaf_fn etc...
        custom_test = lambda x: x.name in set("JCH")
        custom_leaves = t.get_leaves(is_leaf_fn=custom_test)
        self.assertEqual(set([n.name for n in custom_leaves]), set("JHC"))
        
        # Test cached content
        t = Tree()
        t.populate(20)
        cache_name = t.get_cached_content(store_attr="name")
        cache_node = t.get_cached_content()
        self.assertSetEqual(cache_name[t], set(t.get_leaf_names()))
        self.assertSetEqual(cache_node[t], set(t.get_leaves()))
        
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
        
        # Printing and info 
        t.get_ascii()

        t.describe()

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

    def test_tree_diff(self):
        # this is a result of 100 Ktreedist runs. ETE should provide the same RF result
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

        for RF, unrooted, nw1, nw2 in samples:
            t1 = Tree(nw1)
            t2 = Tree(nw2)
            rf, rf_max, names, r1, r2 = t1.robinson_foulds(t2, unrooted_trees=unrooted)
            self.assertEqual(rf, RF)
        
    def test_monophyly(self):
        t =  Tree("((((((a, e), i), o),h), u), ((f, g), j));")
        is_mono, monotype = t.check_monophyly(values=["a", "e", "i", "o", "u"], target_attr="name")
        self.assertEqual(is_mono, False)
        self.assertEqual(monotype, "polyphyletic")
        is_mono, monotype = t.check_monophyly(values=["a", "e", "i", "o"], target_attr="name")
        self.assertEqual(is_mono, True)
        self.assertEqual(monotype, "monophyletic")
        is_mono, monotype =  t.check_monophyly(values=["i", "o"], target_attr="name")
        self.assertEqual(is_mono, False)
        self.assertEqual(monotype, "paraphyletic")
                   
        
        t =  Tree("((((((4, e), i)M1, o),h), u), ((3, 4), (i, june))M2);", format=1)
        # we annotate the tree using external data
        colors = {"a":"red", "e":"green", "i":"yellow", 
                  "o":"black", "u":"purple", "4":"green",
                  "3":"yellow", "1":"white", "5":"red", 
                  "june":"yellow"}
        for leaf in t:
            leaf.add_features(color=colors.get(leaf.name, "none"))
        green_yellow_nodes = set([t&"M1", t&"M2"])
        mono_nodes = t.get_monophyletic(values=["green", "yellow"], target_attr="color")
        self.assertSetEqual(set(mono_nodes), green_yellow_nodes)

        
    def test_copy(self):
        t = Tree("((A, B)Internal_1:0.7, (C, D)Internal_2:0.5)root:1.3;", format=1)
        # we add a custom annotation to the node named A
        (t & "A").add_features(label="custom Value")
        # we add a complex feature to the A node, consisting of a list of lists
        (t & "A").add_features(complex=[[0,1], [2,3], [1,11], [1,0]])

       
        t_nw  = t.copy("newick")
        t_nwx = t.copy("newick-extended")
        t_pkl = t.copy("cpickle")
        (t & "A").testfn = lambda: "YES"
        t_deep = t.copy("deepcopy")
        
        self.assertEqual((t_nw & "root").name, "root")
        self.assertEqual((t_nwx & "A").label, "custom Value")
        self.assertListEqual((t_pkl & "A").complex[0], [0,1])
        self.assertEqual((t_deep & "A").testfn(), "YES")
        

        
        
    # def test_traversing_speed(self):
    #     return
    #     for x in xrange(10):
    #         t = Tree()
    #         t.populate(100000)

    #         leaves = t.get_leaves()
    #         sample = random.sample(leaves, 100)

    #         t1 = time.time()
    #         a = t.get_common_ancestor_OLD(sample)
    #         t2 = time.time() - t1
    #         print "OLD get common", t2

    #         t1 = time.time()
    #         b = t.get_common_ancestor(sample)
    #         t2 = time.time() - t1
    #         print "NEW get common", t2

    #         self.assertEqual(a, b)


    #         t1 = time.time()
    #         [n for n in t._iter_descendants_postorder_OLD()]
    #         t2 = time.time() - t1
    #         print "OLD postorder", t2

    #         t1 = time.time()
    #         [n for n in t._iter_descendants_postorder()]
    #         t2 = time.time() - t1
    #         print "NEW postorder", t2

if __name__ == '__main__':
    unittest.main()
