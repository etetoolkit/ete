# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################
import sys
from string import strip
import operator
import re

__CITATION__ = '''#       ** If you use this software for a published work, please cite: **
#  
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon. ETE: a python Environment
# for Tree Exploration. BMC Bioinformatics 2010, 11:24. doi: 10.1186/1471-2105-11-24.'''


LOG_LEVEL = 2
    
class ArgError(ValueError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        # return repr(self.value)
        return self.value
    pass


class Logger(object):
    def __init__(self, buff):
        self.out = buff
    
    def error(self, *args):
        if LOG_LEVEL >=1:
            print >>self.out, "ERROR - ", ' '.join(map(str, args))
            
    def warn(self, *args):
        if LOG_LEVEL >=2:
            print >>self.out, "WARN  - ", ' '.join(map(str, args))
            
    def info(self, *args):
        if LOG_LEVEL >=3:
            print >>self.out, "INFO  - ", ' '.join(map(str, args))
        
    def debug(self, *args):
        if LOG_LEVEL >=4:
            print >>self.out, "DEBUG - ", ' '.join(map(str, args))
    
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

def shorten_str(string, l):
    if len(string) > l:
        return "%s(...)" % string[:l-5]
    else:
        return string  

def parse_value(fvalue):
    func_match = re.search("(\w+)\(([^)]*)\)", fvalue)
    if func_match:
        func_name = func_match.groups()[0]
        func_arg = func_match.groups()[1]
    #RETURN SOMETHING
        
def dump(t, features=None):
    #if getattr(args, "output", None):
    #    t.write(format=0, features=features)
    #else:
    print t.write(format=0, features=features)
    
def populate_main_args(main_args_p):
    main_args = main_args_p.add_argument_group('GENERAL OPTIONS')

    main_args.add_argument("-o", dest="output", 
                            type=str,
                            help="""Base output file name""")
    
    main_args.add_argument('--format', dest='newick_format', type=int, default=0)
    
    main_args.add_argument('--features', dest='output_features', type=str, nargs="+", default=[])
    
    main_args.add_argument("--nocolor", dest="nocolor",
                           action="store_true",
                           help="If enabled, it will NOT use colors when logging")

    main_args.add_argument("-v", dest="verbosity",
                           type=int, choices= [0, 1, 2, 3, 4], default=2,
                           help=("Verbosity level: 0=totally quite, 1=errors only,"
                           " 2=warning+errors, 3=info,warnings and errors 4=debug "))


def populate_source_args(source_args_p):
    source_args = source_args_p.add_argument_group('SOURCE TREES')
    
    source_args.add_argument("-t", dest='src_trees',
                             type=str, nargs="*",
                             help=("a list of trees in newick format (filenames or"
                             " quoted strings)"))
    
    source_args.add_argument("--src_file", dest="src_file", 
                             type=str, 
                             help=("path to a file containing many source trees, one per line"))

    source_args.add_argument("--src_tree_attr", dest="src_tree_attr", 
                             type=str, default="name",
                             help=("attribute in source tree used as leaf name"))
    
    source_args.add_argument("--src_attr_parser", dest="src_attr_parser", 
                             type=str, 
                           help=("Perl regular expression wrapping the portion of the target attribute that should be used."))

def populate_ref_args(ref_args_p):
    ref_args = ref_args_p.add_argument_group('REFERENCE TREES')
    
    ref_args.add_argument("-r", dest="ref_trees", 
                           type=str, nargs="*",
                           help=("One or more reference trees in newick format (filename"
                                 " or quoted string"))

    ref_args.add_argument("--ref_tree_list", dest="ref_tree_list", 
                             type=str, 
                             help="path to a file containing many ref trees, one per line")
    
    ref_args.add_argument("--ref_tree_attr", dest="ref_tree_attr", 
                           type=str, default="name",
                           help=("attribute in ref tree used as leaf name"))
        
    ref_args.add_argument("--ref_attr_parser", dest="ref_attr_parser", 
                           type=str, 
                           help=("Perl regular expression wrapping the portion of the target attribute that should be used."))


