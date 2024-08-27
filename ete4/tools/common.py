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
    return False

POSNAMES = {
    'b-right': 'branch-right',
    'b-top': 'branch-top',
    'b-bottom': 'branch-bottom',
    'float': 'float',
    'float-behind': 'float-behind',
    'aligned': 'aligned',
}

OPFUNC = {
    '<': operator.lt,
    '>': operator.gt,
    '=': operator.eq,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '<=': operator.le,
    '=~': lambda string, pattern: re.search(pattern, string),
}


def as_str(v):
    return ('%0.2f' % v) if isinstance(v, float) else str(v)

def shorten_str(string, l, reverse=False):
    if len(string) > l:
        if reverse:
            return "(..)%s" % string[l+4:]
        else:
            return "%s(..)" % string[:l-4]
    else:
        return string

def parse_value(fvalue):
    func_match = re.search(r"(\w+)\(([^)]*)\)", fvalue)
    if func_match:
        func_name = func_match.groups()[0]
        func_arg = func_match.groups()[1]
    #RETURN SOMETHING

def dump(t, properties=None):
    print(t.write(parser=0, props=properties))


def populate_main_args(parser):
    add = parser.add_argument_group('GENERAL OPTIONS').add_argument

    add('-o', '--output', help='base output file name')

    add('-v', '--verbosity', type=int, choices=[0, 1, 2, 3, 4], default=2,
        help='verbosity level: 0=quiet, 1=error, 2=warning, 3=info, 4=debug')


def populate_source_args(parser):
    add = parser.add_argument_group('SOURCE TREES').add_argument

    add('-t', '--src_trees', metavar='FILE', nargs='*', help='files with trees in newick format')
    add('--src_tree_list', metavar='FILE', help='path to a file containing many source trees, one per line')
    add('--src_tree_attr', metavar='ATTR', default='name', help='attribute in source tree used as leaf name')
    add('--src_attr_parser', metavar='REGEX', help='regular expression wrapping the portion of the target attribute that should be used')
    add('--src_tree_format', metavar='FMT', dest='src_newick_format', type=int, default=0, help='newick format (0-9,100)')


def populate_ref_args(parser):
    add = parser.add_argument_group('REFERENCE TREES').add_argument

    add('-r', '--ref_trees', metavar='FILE', nargs='*', help='files with reference trees in newick format')
    add('--ref_tree_list', metavar='FILE', help='path to a file containing many ref trees, one per line')
    add('--ref_tree_attr', metavar='ATTR', default='name', help='attribute in ref tree used as leaf name')
    add('--ref_attr_parser', metavar='REGEX', help='regular expression wrapping the portion of the target attribute that should be used')
    add('--ref_tree_format', metavar='FMT', dest='ref_newick_format', type=int, default=0, help='newick format (0-9,100)')


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
