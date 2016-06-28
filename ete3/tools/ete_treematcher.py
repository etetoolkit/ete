from .common import log

DESC=''

#ete3 treematcher --pattern "(hello, kk);" --pattern-format 8 --tree-format 8 --trees "(hello,(1,2,3)kk);" --quoted-node-names


def populate_args(extract_args_p):
    extract_args = extract_args_p.add_argument_group('TREEMATCHER OPTIONS')

    extract_args.add_argument("--pattern", dest="pattern",
                              nargs=1,
                              help="")
    extract_args.add_argument("--pattern-format", dest="pattern_format",
                              nargs=1,
                              help="")
    extract_args.add_argument("--quoted-node-names", dest="quoted_node_names",
                              action="store_true",
                              help="")

    extract_args.add_argument("--trees", dest="trees",
                              nargs="*",
                              help="")
    extract_args.add_argument("--tree-format", dest="tree_format",
                              nargs=1,
                              help="")


def run(args):
    from .. import Tree, PhyloTree
    import treematcher

    if args.pattern is not None:
        p = args.pattern[0]
        pattern = treematcher.TreePattern(p, format=int(args.pattern_format[0]), quoted_node_names=args.quoted_node_names)
        if args.trees is not None:
            for t in args.trees:
                t = Tree(t, format=int(args.tree_format[0]), quoted_node_names=args.quoted_node_names)
                print pattern.find_match(t, None)

        else:
            log.error('Please specify a tree to search.')
            sys.exit(-1)
    else:
        log.error('Please specify a pattern to search for.')
        sys.exit(-1)