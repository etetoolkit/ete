DESC=''


def populate_args(extract_args_p):
    extract_args = extract_args_p.add_argument_group('TREEMATCHER OPTIONS')

    extract_args.add_argument("--pattern", dest="pattern",
                              nargs=1,
                              help="")
    extract_args.add_argument("--format", dest="format",
                              nargs=1,
                              help="")
    extract_args.add_argument("--quoted-node-names", dest="quoted_node_names",
                              action="store_true",
                              help="")

    extract_args.add_argument("--trees", dest="trees",
                              nargs="*",
                              help="")


def run(args):
    from .. import Tree, PhyloTree, treematcher
    #from ete3 import Tree, PhyloTree
    import treematcher

    if args.pattern is not None:
        p = args.pattern[0]
        pattern = treematcher.TreePattern(p, format=int(args.format[0]), quoted_node_names=args.quoted_node_names)
        if args.trees is not None:
            for t in args.trees:
                t = Tree(t, format=int(args.format[0]), quoted_node_names=args.quoted_node_names)
                print pattern.find_match(t, None)

        else:
            print "please specify a tree"
    else:
        print "please specify a tree pattern"