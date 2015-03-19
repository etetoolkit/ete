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
from common import dump

DESC = ""

def populate_args(mod_args_p):
    mod_args = mod_args_p.add_argument_group('TREE EDIT OPTIONS')
    
    mod_args.add_argument("--outgroup", dest="outgroup", 
                           nargs = "+",
                           help=("Root the tree using the provided outgroup."
                                 " If several names are provided, the first common ancestor grouping"
                                 " all of them will be selected as outgroup."))

    mod_args.add_argument("--ultrametric", dest="ultrametric",
                          type=float, nargs= "*", default="-1",
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
    from ete2 import Tree
    
    for nw in args.src_tree_iterator:
        t = Tree(nw)
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
            outgroup = t.get_common_ancestor(args.outgroup)
        else:
            outgroup = t & args.outgroup[0]
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

    if args.ultrametric:
        t.convert_to_ultrametric()
    
    # remove, prune branches
    # ncbi_root
