.. currentmodule:: ete4.treematcher.treematcher

Tree matcher
============

.. contents::

The *tree matcher* in ete4 can find sub-tree patterns in a tree.

It allows to search for topological realations, at the same time as
imposing arbitrary requirements in the nodes of the subtree to be
matched. We could see it as a regular-expression search on a tree,
only more powerful.

We are going to look at the two most useful parts of this module: the
class :class:`TreePattern` and the method :func:`~TreePattern.search`
defined in it.


A simple example (only topology)
--------------------------------

Let's start with a simple tree::

  from ete4 import Tree

  t = Tree('((K:4,((A:1,B:2)G:3,C:1)H:0.5,D:1)I:0.5,(E:1,F:2)J:1)root;', parser=1)

  print(t.to_str(props=['name', 'dist']))
  #                 ╭╴K,4.0
  #                 │
  #                 │               ╭╴A,1.0
  #                 │       ╭╴G,3.0╶┤
  #         ╭╴I,0.5╶┼╴H,0.5╶┤       ╰╴B,2.0
  #         │       │       │
  #         │       │       ╰╴C,1.0
  # ╴root,⊗╶┤       │
  #         │       ╰╴D,1.0
  #         │
  #         │       ╭╴E,1.0
  #         ╰╴J,1.0╶┤
  #                 ╰╴F,2.0

In the tree, there is a node that has 3 children. Let's imagine we
want to find all such nodes. We could traverse the tree with ETE and
so on, but we could also do this with the tree matcher::

  from ete4.treematcher import TreePattern

  tp = TreePattern(' ( , , ) ')

  print(tp)
  #    ╭╴⊗
  #    │
  # ╴⊗╶┼╴⊗
  #    │
  #    ╰╴⊗

  for node in tp.search(t):
      print('Match on node', node.name)
  # Match on node I

Okay, it found the node!

The ``tp.search(t)`` iterates over the nodes of tree ``t``, yielding
the ones that match the tree pattern ``tp`` that we defined.

How about if we also wanted that at least one of the children has two
children?

::

  tp = TreePattern(' ( ( , ), , ) ')

  print(tp)
  #        ╭╴⊗
  #    ╭╴⊗╶┤
  #    │   ╰╴⊗
  # ╴⊗╶┤
  #    ├╴⊗
  #    │
  #    ╰╴⊗

It requires one of the three children to have two children. But it
seems like it is the first of the children, and the one with two in
``t`` is the second. Will it match?

::

  for node in tp.search(t):
      print('Match on node', node.name)
  # Match on node I

Yes, it matches again. The reason is that the pattern we look for is a
topological one, so the tree matcher is going to try all the
permutations to see if any one matches. This is what we normally want
when looking for a subtree pattern.


A less simple example (with node expressions)
---------------------------------------------

The pattern is no limited to the tree structure. Each node can contain
(and often does) a condition to check in that node. For example::

  tp = TreePattern("""
  (
      ( 'any(regex("A|a", n.name) for n in node.leaves())' ,
      ),
      'len(ch) < 3 and dist < 10',
  )
  """)

  print(tp)
  #        ╭╴any(regex("A|a", n.name) for n in node.leaves())
  #    ╭╴⊗╶┤
  #    │   ╰╴⊗
  # ╴⊗╶┤
  #    ├╴len(ch) < 3 and dist < 10
  #    │
  #    ╰╴⊗


We use triple quotes (``"""``) to then use quotes (``'`` and ``"``)
freely in the conditions. This is so the newick parser can distinguish
the parenthesis related to function calls and the parenthesis related
to the newick structure.

Also, the conditions in each node are arbitrary Python expressions.
The tree matcher automatically compiles them for efficiency, and then
we can search::

  for node in tp.search(t):
      print('Match on node', node.name)
  # Match on node I

Note that the same node matched. Feel free to change the expression in
the pattern and run new variants to see when it produces a match, when
it doesn't, and the kind of errors that we could have (like incorrect
use of quotes, or incorrect python expressions).

Inside each expression, ``node`` will be evaluated to the node existing
in that position of the tree pattern. In addition to that, we can use
a few shortcuts to write short expressions. The main ones correspond
to this dictionary::

  context = {
      'node': node,
      'name': node.props.get('name', ''),  # node.name could be None
      'dist': node.dist, 'd': node.dist,
      'support': node.support, 'sup': node.support,
      'up': node.up, 'parent': node.up,
      'children': node.children, 'ch': node.children,
      'is_leaf': node.is_leaf, 'is_root': node.is_root,
      'props': node.props, 'p': node.props,
      'species': getattr(node, 'species', ''),  # for PhyloTree
      'regex': re.search,
    }

The idea is to be able to write relatively complex searches in a
compact and legible way.


Outside variables
-----------------

In our node expressions we can include variables outside of the ones
we described before. For example, if we substitute the 3 in our
previous pattern for ``nchildren``::

  tp = TreePattern("""
  (
      ( 'any(regex("A|a", n.name) for n in node.leaves())' ,
      ),
      'len(ch) < nchildren and dist < 10',
  )
  """)

  print(tp)
  #        ╭╴any(regex("A|a", n.name) for n in node.leaves())
  #    ╭╴⊗╶┤
  #    │   ╰╴⊗
  # ╴⊗╶┤
  #    ├╴len(ch) < nchildren and dist < 10
  #    │
  #    ╰╴⊗

If now we did a search with ``tp.search(t)`` it would produce an
exception, since it doesn't know what ``nchildren`` is.

But we can tell it::

  for node in tp.search(t, {'nchildren': 4}):
      print('Match on node', node.name)
  # Match on node I

We just passed a dictionary to the ``search()`` function with the
substitutions that we want it to make for any extra variables. If we
run again with a different value for ``nchildren``::

  for node in tp.search(t, {'nchildren': 0}):
      print('Match on node', node.name)
  # (no output)

There are no matches now. Of course: no children have a negative number of children.

One common use is when we want to do checks on the leaf descendants of
a node, and we cached them beforehand by calling
``t.get_cached_content()``. If we did something like that for our
example, it would look like::

  n2leaves = t.get_cached_content()

  # Like before, but instead of node.leaves() we use n2leaves[node].
  tp = TreePattern("""
  (
      ( 'any(regex("A|a", n.name) for n in n2leaves[node])' ,
      ),
      'len(ch) < nchildren and dist < 10',
  )
  """)

  print(tp)
  #        ╭╴any(regex("A|a", n.name) for n in n2leaves[node])
  #    ╭╴⊗╶┤
  #    │   ╰╴⊗
  # ╴⊗╶┤
  #    ├╴len(ch) < nchildren and dist < 10
  #    │
  #    ╰╴⊗

  # Find matches.
  for node in tp.search(t, {'nchildren': 3, 'n2leaves': n2leaves}):
      print('Match on node', node.name)
  # Match on node I

A final tip related to the variables: in our program, specially when
we are trying things quickly on the console, we can pass Python's
``locals()`` as the dictionary. It will already contain all the
variables that we have defined in our session.

This can be quite comfortable, but not always the best option. Use
sparingly and enjoy!


Examples from the test suite
----------------------------

Finally, for a few more examples, let's take from the ETE test suite
one of the test patterns and several trees where we check for matches::

  pattern = TreePattern("""
  (
      "len(ch) > 2",
      "name in ['hello', 'bye']"
  )
  "(len(name) < 3 or name == 'accept') and d >= 0.5"
  """)

  print(pattern)
  #                                                   ╭╴len(ch) > 2
  # ╴(len(name) < 3 or name == 'accept') and d >= 0.5╶┤
  #                                                   ╰╴name in ['hello', 'bye']

We are going to construct several trees, and see the matches that this
pattern has on them::

  for newick, expected_result in [
      ('((hello:1,(1:1,2:1,3:1)xx:1)accept:1, NODE):0;',   ['accept']),  # node "accept" will match
      ('((hello:1,(1:1,2:1,3:1)xx:1)accept:0.4, NODE):0;', []),          # no node will match
      ('(hello:1,(1:1,2:1,3:1)xx:1)accept:1;',             ['accept']),  # etc.
      ('((bye:1,(1:1,2:1,3:1)xx:1)none:1, NODE):0;',       []),
      ('((bye:1,(1:1,2:1,3:1)xx:1)y:1, NODE):0;',          ['y']),
      ('((bye,(,,))x:1,((,,),bye)y:1):0;',                 ['x', 'y'])]:
      print()
      print('\nSearching pattern in the tree:')
      t = Tree(newick, parser=1)
      print(t.to_str())

      matches = [n.name for n in pattern.search(t)]

      print()
      print('Expected result:', expected_result)
      print('Matches found:  ', matches)
      if matches == expected_result:
          print('TreePattern for the win!')

We end with the produced results::

  Searching pattern in the tree:
                                   ╭╴name=hello,dist=1.0
                                   │
            ╭╴name=accept,dist=1.0╶┤                  ╭╴name=1,dist=1.0
            │                      │                  │
            │                      ╰╴name=xx,dist=1.0╶┼╴name=2,dist=1.0
  ╴dist=0.0╶┤                                         │
            │                                         ╰╴name=3,dist=1.0
            │
            ╰╴name=NODE

  Expected result: ['accept']
  Matches found:   ['accept']
  TreePattern for the win!


  Searching pattern in the tree:
                                   ╭╴name=hello,dist=1.0
                                   │
            ╭╴name=accept,dist=0.4╶┤                  ╭╴name=1,dist=1.0
            │                      │                  │
            │                      ╰╴name=xx,dist=1.0╶┼╴name=2,dist=1.0
  ╴dist=0.0╶┤                                         │
            │                                         ╰╴name=3,dist=1.0
            │
            ╰╴name=NODE

  Expected result: []
  Matches found:   []
  TreePattern for the win!


  Searching pattern in the tree:
                        ╭╴name=hello,dist=1.0
                        │
  ╴name=accept,dist=1.0╶┤                  ╭╴name=1,dist=1.0
                        │                  │
                        ╰╴name=xx,dist=1.0╶┼╴name=2,dist=1.0
                                           │
                                           ╰╴name=3,dist=1.0

  Expected result: ['accept']
  Matches found:   ['accept']
  TreePattern for the win!


  Searching pattern in the tree:
                                 ╭╴name=bye,dist=1.0
                                 │
            ╭╴name=none,dist=1.0╶┤                  ╭╴name=1,dist=1.0
            │                    │                  │
            │                    ╰╴name=xx,dist=1.0╶┼╴name=2,dist=1.0
  ╴dist=0.0╶┤                                       │
            │                                       ╰╴name=3,dist=1.0
            │
            ╰╴name=NODE

  Expected result: []
  Matches found:   []
  TreePattern for the win!


  Searching pattern in the tree:
                              ╭╴name=bye,dist=1.0
                              │
            ╭╴name=y,dist=1.0╶┤                  ╭╴name=1,dist=1.0
            │                 │                  │
            │                 ╰╴name=xx,dist=1.0╶┼╴name=2,dist=1.0
  ╴dist=0.0╶┤                                    │
            │                                    ╰╴name=3,dist=1.0
            │
            ╰╴name=NODE

  Expected result: ['y']
  Matches found:   ['y']
  TreePattern for the win!


  Searching pattern in the tree:
                              ╭╴name=bye
                              │
            ╭╴name=x,dist=1.0╶┤  ╭╴
            │                 │  │
            │                 ╰──┼╴
            │                    │
            │                    ╰╴
  ╴dist=0.0╶┤
            │                    ╭╴
            │                    │
            │                 ╭──┼╴
            │                 │  │
            ╰╴name=y,dist=1.0╶┤  ╰╴
                              │
                              ╰╴name=bye

  Expected result: ['x', 'y']
  Matches found:   ['x', 'y']
  TreePattern for the win!
