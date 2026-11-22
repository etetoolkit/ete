import os

from .common import dump, src_tree_iterator

DESC = ""

def populate_args(mod_args_p):
    mod_args = mod_args_p.add_argument_group('TREE EDIT OPTIONS')

    mod_args.add_argument("--outgroup", dest="outgroup",
                           nargs = "+",
                           help=("Root the tree using the provided outgroup."
                                 " If several names are provided, the first common ancestor grouping"
                                 " all of them will be selected as outgroup."))

    mod_args.add_argument("--ultrametric", dest="ultrametric",
                          type=float, nargs="?", const=0,
                           help=("Convert tree into ultrametric (all leaves have the same distance"
                                 " to root). If an argument is provided, it will be used as the"
                                 " expected tree length."))

    mod_args.add_argument("--prune", dest="prune",
                          type=str, nargs= "+",
                           help=("Remove all nodes in the tree except the ones provided."))

    mod_args.add_argument("--prune_preserve_lengths", dest="prune_preserve_lengths",
                          action="store_true",
                           help=("branch lengths of the removed nodes are added to the kept branches, "
                                 "thus preserving original tree length."))


    mod_args.add_argument("--unroot", dest="unroot",
                          action = "store_true",
                           help="Unroots the tree.")


    mod_args.add_argument("--sort_branches", dest="sort",
                           action="store_true",
                           help="""Sort branches according to node names.""")

    mod_args.add_argument("--ladderize", dest="ladderize",
                           action="store_true",
                           help="""Sort branches by partition size.""")

    mod_args.add_argument("--resolve_polytomies", dest="resolve_polytomies",
                          action='store_true',
                           help="""Converts polytomies into random bifurcations""")

    mod_args.add_argument("--standardize", dest="standardize",
                          action = "store_true",
                           help="Standardize tree topology by expanding polytomies and single child nodes.")



def run(args):
    from .. import Tree

    for ftree in src_tree_iterator(args):  # a file name, or a newick read from stdin
        t = Tree(open(ftree) if os.path.isfile(ftree) else ftree,
                 parser=args.src_newick_format)
        mod_tree(t, args)
        dump(t)

def mod_tree(t, args):
    if args.ladderize and args.sort:
        raise ValueError("--sort-branches and --ladderize options are mutually exclusive")

    if args.prune:
        t.prune(args.prune, preserve_branch_length=args.prune_preserve_lengths)

    if args.outgroup and args.unroot:
        raise ValueError("--ourgroup and --unroot options are mutually exclusive")
    elif args.outgroup:
        if len(args.outgroup) > 1:
            outgroup = t.common_ancestor(args.outgroup)
        else:
            outgroup = t[args.outgroup[0]]
        t.set_outgroup(outgroup)
    elif args.unroot:
        t.unroot()

    if args.resolve_polytomies:
        t.resolve_polytomy()

    if args.standardize:
        t.standardize()

    if args.ladderize:
        t.ladderize()
    if args.sort:
        t.sort_descendants()

    if args.ultrametric is not None:
        t.to_ultrametric()
        if args.ultrametric > 0:  # scale to the requested root-to-leaf distance
            height = t.get_distance(t, next(t.leaves()))
            for node in t.descendants():
                node.dist *= args.ultrametric / height

    # remove, prune branches
    # ncbi_root
