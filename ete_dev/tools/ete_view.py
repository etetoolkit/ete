#! /usr/bin/python 
import os 
import re
import sys

from common import argparse, PhyloTree, TreeStyle, faces

__all__ = ["main"]

__DESCRIPTION__ = """
The ETE tree viewer. 
"""

paired_colors = ['#a6cee3',
                 '#1f78b4',
                 '#b2df8a',
                 '#33a02c',
                 '#fb9a99',
                 '#e31a1c',
                 '#fdbf6f',
                 '#ff7f00',
                 '#cab2d6',
                 '#6a3d9a',
                 '#ffff99',
                 '#b15928']

COLOR_RANKS = {
    "superclass": "#a6cee3",
    "class": "#a6cee3",
    "subclass": "#a6cee3",
    "infraclass": "#a6cee3",
    
    "superfamily": "#1f78b4",
    "family": "#1f78b4",
    "subfamily": "#1f78b4",

    "superkingdom": "#b2df8a",
    "kingdom": "#b2df8a",
    "subkingdom": "#b2df8a",
    
    "superorder": "#33a02c",
    "order": "#33a02c",
    "suborder": "#33a02c",
    "infraorder": "#33a02c",
    "parvorder": "#33a02c",

    "superphylum": "#fdbf6f",
    "phylum": "#fdbf6f",
    "subphylum": "#fdbf6f",

#    "species group": "",
#    "species subgroup": "",
#    "species": "",
#    "subspecies": "",

#    "genus": "",
#    "subgenus": "",

#    "no rank": "",
#    "forma": "",

#    "tribe": "",
#    "subtribe": "",
#    "varietas"
    }

NAME_FONT_SIZE = 14
LEAF_NAME_POSITION = "branch-right"

LEAF_ATTRIBUTES = {"name": 1}
INTERNAL_ATTRIBUTES = {}

SPCODE_REGEXP = None
def user_species_naming_function(name):
    try:
        return SPCODE_REGEXP.search(name).groups()[0]
    except Exception:
        print >>sys.stderr, "Unable to capture species code in: ", name
        return "Unknown"

def master_layout(node):
    node.img_style["shape"] = "square"
    node.img_style["fgcolor"] = "steelblue"
    if hasattr(node, "bgcolor"):
        node.img_style["bgcolor"] = node.bgcolor
        N = faces.AttrFace("name", fsize=NAME_FONT_SIZE)
        N.margin_left = 1
        faces.add_face_to_node(N, node, 0, position="branch-top")

        
    if node.is_leaf():
        node.img_style["size"] = 0
        for aname, pos in LEAF_ATTRIBUTES.iteritems():
            if aname == "sequence":
                N = faces.SeqMotifFace(node.sequence, seq_format="compactseq")
                faces.add_face_to_node(N, node, pos, position="aligned")
            else:
                N = faces.AttrFace(aname, fsize=NAME_FONT_SIZE)
                N.margin_left = 1
                faces.add_face_to_node(N, node, pos, position=LEAF_NAME_POSITION)
    else:
        node.img_style["size"] = 5
        for aname, pos in INTERNAL_ATTRIBUTES.iteritems():
            N = faces.AttrFace(aname, fsize=NAME_FONT_SIZE)
            N.margin_left = 1
            faces.add_face_to_node(N, node, pos, position=LEAF_NAME_POSITION)
        
        
def main(argv):
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    input_gr = parser.add_argument_group("TREE INPUT OPTIONS\n=================")
    
    input_gr.add_argument('tree', metavar='tree_file', type=str, nargs=1,
                      help='A tree file (or text string) in newick format.')

    input_gr.add_argument("--raxml", dest="raxml", 
                        action="store_true",
                        help="""Process newick as raxml bootstrap values""")
    
    img_gr = parser.add_argument_group("TREE IMAGE OPTIONS\n=================")
        
    img_gr.add_argument("-m", "--mode", dest="mode", 
                        choices=["c", "r"], default="r",
                        help="""(r)ectangular or (c)ircular visualization""")
  

    img_gr.add_argument("-i", "--image", dest="image", 
                        type=str, 
                        help="Render tree image instead of showing it. A filename "
                        " should be provided. PDF, SVG and PNG file extensions are"
                        " supported (i.e. -i tree.svg)"
                        )

    img_gr.add_argument("--text", dest="text_mode", 
                        action="store_true",
                        help="Shows the tree using ASCII characters")

    img_gr.add_argument("--attr", "--show_attributes", dest="show_attributes", 
                        nargs="+",
                        help="Display the value of the specified attributes, if available")    
    
    img_gr.add_argument("--Iw", "--width", dest="width", 
                        type=int, default=0, 
                        help="width of the rendered image in pixels (see --size-units)."
                        )

    img_gr.add_argument("--Ih", "--height", dest="height", 
                        type=int, default=0,
                        help="height of the rendered image in pixels (see --size-units)."
                        )

    img_gr.add_argument("--Ir", "--resolution", dest="resolution", 
                        type=int, default=300,
                        help="Resolution if the tree image (DPI)"
                        )

    img_gr.add_argument("--Iu", "--size_units", dest="size_units", 
                        choices=["px", "mm", "in"], default="px",
                        help="Units used to specify the size of the image."
                        " (px:pixels, mm:millimeters, in:inches). "
                        )

    img_gr.add_argument("-mbs", "--min_branch_separation", dest="branch_separation", 
                        type=int, default = 3, 
                        help="Min number of pixels to separate branches vertically."
                        )

    img_gr.add_argument("--ss", "--show_support", dest="show_support", 
                        action="store_true",
                        help="""Shows branch bootstrap/support values""")

    img_gr.add_argument("--sbl", "--show_branch_length", dest="show_branch_length", 
                        action="store_true",
                        help="""Show branch lengths.""")

    img_gr.add_argument("--ft", "--force_topology", dest="force_topology", 
                        action="store_true",
                        help="""Force branch length to have a minimum length in the image""")

    img_gr.add_argument("--hln", "--hide_leaf_names", dest="hide_leaf_names", 
                        action="store_true",
                        help="""Hide leaf names.""")

    img_gr.add_argument("--sin", "--show_internal_names", dest="show_internal_names", 
                        action="store_true",
                        help="""Show the name attribute of all internal nodes.""")

    edit_gr = parser.add_argument_group("TREE EDIT OPTIONS\n=================")
    
    edit_gr.add_argument("-r", "--root", dest="root", 
                         type=str, nargs="*",
                         help="Roots the tree to the node grouping the list"
                         " of node names provided (space separated). In example:"
                         "'--root human rat mouse'")
    
    edit_gr.add_argument("-s", "--sort_branches", dest="sort", 
                        action="store_true",
                        help="""Sort branches according to node names.""")

    edit_gr.add_argument("-l", "--ladderize", dest="ladderize", 
                        action="store_true",
                        help="""Sort branches by partition size.""")
    
    edit_gr.add_argument("--color_by_rank", dest="color_by_rank", 
                         type=str, nargs="+",
                         help="""If the attribute rank is present in nodes """)

    edit_gr.add_argument("--ncbi", dest="ncbi", 
                         action="store_true",
                         help=""" Annotate tree using the NCBI taxonomy database""")

    edit_gr.add_argument("--taxid_attr", dest="taxid_attr", 
                         type=str, default="name",
                         help="node attribute encoding for valid taxid numbers.")

    edit_gr.add_argument("--taxid_attr_regexp", dest="taxid_attr_regexp", 
                         type=str,
                         help="If taxid number is encoded as part of another text string, i.e. gene name, use this argument to define a Perl regular expression to extract taxid numbers.")
    
    phylo_gr = parser.add_argument_group("PHYLOGENETIC OPTIONS\n=================")
    
    phylo_gr.add_argument("--alg", dest="alg", 
                        type=str, 
                        help="""Link tree to a multiple sequence alignment.""")

    phylo_gr.add_argument("--alg_format", dest="alg_format", 
                        type=str, default="fasta",
                        help="""fasta, phylip, iphylip, relaxed_iphylip, relaxed_phylip.""")
    
    phylo_gr.add_argument("--sp_discovery", dest="species_discovery_regexp", 
                          type=str, default="^[^_]+_(.+)",
                          help="Perl regular expression used to capture species"
                          " code from node names. By default, node names"
                          " are expected to follow the NAME_SPCODE format = '^[^_]+_(.+)' ")
    
    args = parser.parse_args(argv)

    tfile = args.tree[0]


    if args.ladderize and args.sort:
        raise ValueError("--sort-branches and --ladderize options are mutually exclusive")
    
    if args.raxml:
        nw = re.sub(":(\d+\.\d+)\[(\d+)\]", ":\\1[&&NHX:support=\\2]", open(tfile).read())
        t = PhyloTree(nw)
    else:
        t = PhyloTree(tfile)

    if args.ncbi:
        if args.taxid_attr_regexp:
            TAXIDMATCHER = re.compile(args.taxid_attr_regexp)

        for lf in t:
            if args.taxid_attr_regexp:
                lf.taxid = re.search(TAXIDMATCHER, getattr(lf, args.taxid_attr)).groups()[0]
            else:
                lf.taxid = getattr(lf, args.taxid_attr)
        t.annotate_ncbi_taxa(taxid_attr="taxid")
        
    if args.alg:
        t.link_to_alignment(args.alg, alg_format=args.alg_format)
        LEAF_ATTRIBUTES["sequence"] = 1
        
    if args.species_discovery_regexp:
        SPCODE_REGEXP = re.compile(args.species_discovery_regexp)
        t.set_species_naming_function(user_species_naming_function)
        
    if args.ladderize:
        t.ladderize()
    if args.sort:
        t.sort_descendants()

    if args.root:
        if len(args.root) > 1:
            outgroup = t.get_common_ancestor(args.root)
        else:
            outgroup = t & args.root[0]
        t.set_outgroup(outgroup)

    # VISUALIZATION
        
    ts = TreeStyle()
    ts.mode = args.mode
    ts.show_leaf_name = False
    ts.branch_vertical_margin = args.branch_separation
    if args.show_support:
        ts.show_branch_support = True
    if args.show_branch_length:
        ts.show_branch_length = True
    if args.force_topology:
        ts.force_topology = True
        
    if args.hide_leaf_names:
        del LEAF_ATTRIBUTES["name"]

    if args.show_internal_names:
        INTERNAL_ATTRIBUTES["name"] = 1

    # scale the tree
    if not args.height: 
        args.height = None
    if not args.width: 
        args.width = None

    if args.text_mode:
        print t.get_ascii(show_internal=args.show_internal_names, attributes = args.show_attributes)
    else:    
        ts.layout_fn = master_layout        
        if args.image:
            t.render(args.image, tree_style=ts, w=args.width, h=args.height, units=args.size_units)
        else:
            t.show(None, tree_style=ts)
        
if __name__ == '__main__':
    print sys.argv
    main(sys.argv[1:])
