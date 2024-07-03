import sys
import operator
import re

LOG_LEVEL = 2


class Logger:
    def __init__(self, buff):
        self.out = buff

    def error(self, *args):
        if LOG_LEVEL >=1:
            print("ERROR - ", ' '.join(map(str, args)), file=self.out)

    def warn(self, *args):
        if LOG_LEVEL >=2:
            print("WARN  - ", ' '.join(map(str, args)), file=self.out)

    def info(self, *args):
        if LOG_LEVEL >=3:
            print("INFO  - ", ' '.join(map(str, args)), file=self.out)

    def debug(self, *args):
        if LOG_LEVEL >=4:
            print("DEBUG - ", ' '.join(map(str, args)), file=self.out)

log = Logger(sys.stderr)


def itertrees(trees, treefile):
    if trees:
        for nw in trees:
            yield nw
    if treefile:
        for line in open(treefile):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            else:
                yield line

def node_matcher(node, filters):
    if not filters:
        return True

    for f in filters:
        node_v = getattr(node, f[0], None)
        if node_v:
            try:
                node_v = type(f[2])(node_v)
            except ValueError:
                pass
            if OPFUNC[f[1]](node_v, f[2]):
                return True
            # else:
            #     print f, node_v, type(node_v)
    return False

def _re(q, exp):
    if re.search(exp, q):
        return True
    return False

POSNAMES = {
    "b-right":"branch-right",
    "b-top":"branch-top",
    "b-bottom":"branch-bottom",
    "float":"float",
    "float-behind":"float-behind",
    "aligned":"aligned",
}

OPFUNC = {
    "<":operator.lt,
    ">":operator.gt,
    "=":operator.eq,
    "==":operator.eq,
    "!=":operator.ne,
    ">=":operator.ge,
    "<-":operator.le,
    "~=":_re,
}


def as_str(v):
    if isinstance(v, float):
        return '%0.2f' %v
    else:
        return str(v)

def shorten_str(string, l, reverse=False):
    if len(string) > l:
        if reverse:
            return "(..)%s" % string[l+4:]
        else:
            return "%s(..)" % string[:l-4]
    else:
        return string

def parse_value(fvalue):
    func_match = re.search("(\w+)\(([^)]*)\)", fvalue)
    if func_match:
        func_name = func_match.groups()[0]
        func_arg = func_match.groups()[1]
    #RETURN SOMETHING

def dump(t, properties=None):
    #if getattr(args, "output", None):
    #    t.write(format=0, features=features)
    #else:
    print(t.write(parser=0, props=properties))

def populate_main_args(main_args_p):
    main_args = main_args_p.add_argument_group('GENERAL OPTIONS')

    main_args.add_argument("-o", dest="output",
                            type=str,
                            help="""Base output file name""")



    #main_args.add_argument('--features', dest='output_features', type=str, nargs="+", default=[])

    #main_args.add_argument("--nocolor", dest="nocolor",
    #                       action="store_true",
    #                       help="If enabled, it will NOT use colors when logging")

    main_args.add_argument("-v", dest="verbosity",
                           type=int, choices= [0, 1, 2, 3, 4], default=2,
                           help=("Verbosity level: 0=totally quite, 1=errors only,"
                           " 2=warning+errors, 3=info+warnings+errors 4=debug "))

def populate_source_args(source_args_p):
    source_args = source_args_p.add_argument_group('SOURCE TREES')

    source_args.add_argument("-t", dest='src_trees',
                             type=str, nargs="*",
                             help=("a list of files with trees in newick format"))

    source_args.add_argument("--src_tree_list", dest="src_tree_list",
                             type=str,
                             help=("path to a file containing many source trees, one per line"))

    source_args.add_argument("--src_tree_attr", dest="src_tree_attr",
                             type=str, default="name",
                             help=("attribute in source tree used as leaf name"))

    source_args.add_argument("--src_attr_parser", dest="src_attr_parser",
                             type=str,
                             help=("Perl regular expression wrapping the portion of the target attribute that should be used."))

    source_args.add_argument('--src_tree_format', dest='src_newick_format', type=int, default=0)

def populate_ref_args(ref_args_p):
    ref_args = ref_args_p.add_argument_group('REFERENCE TREES')

    ref_args.add_argument("-r", dest="ref_trees",
                           type=str, nargs="*",
                           help=("Files with reference trees in newick format"))

    ref_args.add_argument("--ref_tree_list", dest="ref_tree_list",
                             type=str,
                             help="path to a file containing many ref trees, one per line")

    ref_args.add_argument("--ref_tree_attr", dest="ref_tree_attr",
                           type=str, default="name",
                           help=("attribute in ref tree used as leaf name"))

    ref_args.add_argument("--ref_attr_parser", dest="ref_attr_parser",
                           type=str,
                           help=("Perl regular expression wrapping the portion of the target attribute that should be used."))

    ref_args.add_argument('--ref_tree_format', dest='ref_newick_format', type=int, default=0)


def src_tree_iterator(args):
    if not args.src_trees and not sys.stdin.isatty():
        log.debug("Reading trees from standard input...")
        args.src_trees = sys.stdin

    if args.src_trees:
        for stree in args.src_trees:
            yield stree.strip()
    elif args.src_tree_list:
        for line in open(args.src_tree_list):
            line = line.strip()
            if line:
                yield line

def ref_tree_iterator(args):
    if args.ref_trees:
        for stree in args.ref_trees:
            yield stree
    elif args.ref_tree_list:
        for line in open(args.ref_tree_list):
            line = line.strip()
            if line:
                yield line
