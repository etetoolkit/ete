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
from __future__ import absolute_import
from __future__ import print_function

import random
import re
import colorsys
from collections import defaultdict

from .common import log, POSNAMES, node_matcher, src_tree_iterator
from .. import (Tree, PhyloTree, TextFace, RectFace, faces, TreeStyle, CircleFace, AttrFace,
                add_face_to_node, random_color)
from six.moves import map

DESC = ""
FACES = []

paired_colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
                 '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
                 '#ffff99', '#b15928']

COLOR_RANKS = { "superclass": "#a6cee3", "class": "#a6cee3", "subclass": "#a6cee3", "infraclass": "#a6cee3",
                "superfamily": "#1f78b4", "family": "#1f78b4", "subfamily": "#1f78b4",
                "superkingdom": "#b2df8a", "kingdom": "#b2df8a", "subkingdom": "#b2df8a", "superorder": "#33a02c",
                "order": "#33a02c", "suborder": "#33a02c", "infraorder": "#33a02c", "parvorder": "#33a02c",
                "superphylum": "#fdbf6f", "phylum": "#fdbf6f",  "subphylum": "#fdbf6f"}
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





def populate_args(view_args_p):
    view_args_p.add_argument("--face", action="append",
                             help="adds a face to the selected nodes. In example --face 'value:@dist, pos:b-top, color:red, size:10, if:@dist>0.9' ")

    img_gr = view_args_p.add_argument_group("TREE IMAGE GENERAL OPTIONS")

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

    img_gr.add_argument("--tree_width", dest="tree_width",
                        type=int, default=300,
                        help=("Adjust tree scale so the distance from root to the"
                              " farthest leaf uses a fixed width in pixels."))


    edit_gr = view_args_p.add_argument_group("TREE EDIT OPTIONS")

    edit_gr.add_argument("--color_by_rank", dest="color_by_rank",
                         type=str, nargs="+",
                         help="""If the attribute rank is present in nodes """)

    edit_gr.add_argument("--raxml", dest="raxml",
                        action="store_true",
                         help=("Parses the newick string and extracts bootstrap values from"
                         " a non-standard RAxML newick file (i.e '((A,B)[100]);'"))

    phylo_gr = view_args_p.add_argument_group("PHYLOGENETIC OPTIONS")

    phylo_gr.add_argument("--alg", dest="alg",
                        type=str,
                        help="""Link tree to a multiple sequence alignment.""")

    phylo_gr.add_argument("--alg_type", dest="alg_type",
                          choices=['blockseq', 'compactseq', 'fullseq'], default='blockseq',
                          help="How sequence alignment should be drawn in the tree")


    phylo_gr.add_argument("--alg_format", dest="alg_format",
                        type=str, default="fasta",
                        help="fasta, phylip, iphylip, relaxed_iphylip, relaxed_phylip.")

    phylo_gr.add_argument("--ncbi", dest="as_ncbi",
                          action="store_true" ,
                          help="""If enabled, default style will be applied to show ncbi taxonomy annotations""")


    features_gr = view_args_p.add_argument_group("DRAWING FEATURES")

    phylo_gr.add_argument("--heatmap", dest="heatmap",
                        type=str,
                          help="""attr_name \t v1, v2, v3, v4""")

    phylo_gr.add_argument("--profile", dest="profile",
                        type=str,
                          help="""attr_name \t v1, v2, v3, v4""")

    phylo_gr.add_argument("--bubbles", dest="bubbles",
                        type=str,
                          help='')


def run(args):    
    if args.text_mode:
        for tindex, tfile in enumerate(src_tree_iterator(args)):
            #print tfile
            if args.raxml:
                nw = re.sub(":(\d+\.\d+)\[(\d+)\]", ":\\1[&&NHX:support=\\2]", open(tfile).read())
                t = Tree(nw, format=args.src_newick_format)
            else:
                t = Tree(tfile, format=args.src_newick_format)

            print(t.get_ascii(show_internal=args.show_internal_names,
                              attributes=args.show_attributes))
        return

    global FACES

    if args.face:
        FACES = parse_faces(args.face)
    else:
        FACES = []

    # VISUALIZATION
    ts = TreeStyle()
    ts.mode = args.mode
    ts.show_leaf_name = True
    ts.tree_width = args.tree_width


    for f in FACES:
        if f["value"] == "@name":
            ts.show_leaf_name = False
            break

    if args.as_ncbi:
        ts.show_leaf_name = False
        FACES.extend(parse_faces(
            ['value:@sci_name, size:10, fstyle:italic',
             'value:@taxid, color:grey, size:6, format:" - %s"',
             'value:@sci_name, color:steelblue, size:7, pos:b-top, nodetype:internal',
             'value:@rank, color:indianred, size:6, pos:b-bottom, nodetype:internal',
         ]))


    if args.alg:
        FACES.extend(parse_faces(
            ['value:@sequence, size:10, pos:aligned, ftype:%s' %args.alg_type]
         ))

    if args.heatmap:
        FACES.extend(parse_faces(
            ['value:@name, size:10, pos:aligned, ftype:heatmap']
         ))

    if args.bubbles:
        for bubble in args.bubbles:
            FACES.extend(parse_faces(
                ['value:@%s, pos:float, ftype:bubble, opacity:0.4' %bubble,
             ]))

    ts.branch_vertical_margin = args.branch_separation
    if args.show_support:
        ts.show_branch_support = True
    if args.show_branch_length:
        ts.show_branch_length = True
    if args.force_topology:
        ts.force_topology = True
    ts.layout_fn = lambda x: None

    for tindex, tfile in enumerate(src_tree_iterator(args)):
        #print tfile
        if args.raxml:
            nw = re.sub(":(\d+\.\d+)\[(\d+)\]", ":\\1[&&NHX:support=\\2]", open(tfile).read())
            t = PhyloTree(nw, format=args.src_newick_format)
        else:
            t = PhyloTree(tfile, format=args.src_newick_format)


        if args.alg:
            t.link_to_alignment(args.alg, alg_format=args.alg_format)

        if args.heatmap:
            DEFAULT_COLOR_SATURATION = 0.3
            BASE_LIGHTNESS = 0.7
            def gradient_color(value, max_value, saturation=0.5, hue=0.1):
                def rgb2hex(rgb):
                    return '#%02x%02x%02x' % rgb
                def hls2hex(h, l, s):
                    return rgb2hex( tuple([int(x*255) for x in colorsys.hls_to_rgb(h, l, s)]))

                lightness = 1 - (value * BASE_LIGHTNESS) / max_value
                return hls2hex(hue, lightness, DEFAULT_COLOR_SATURATION)


            heatmap_data = {}
            max_value, min_value = None, None
            for line in open(args.heatmap):
                if line.startswith('#COLNAMES'):
                    pass
                elif line.startswith('#') or not line.strip():
                    pass
                else:
                    fields = line.split('\t')
                    name = fields[0].strip()

                    values = [float(x) if x else None for x in fields[1:]]

                    maxv = max(values)
                    minv = min(values)
                    if max_value is None or maxv > max_value:
                        max_value = maxv
                    if min_value is None or minv < min_value:
                        min_value = minv
                    heatmap_data[name] = values

            heatmap_center_value = 0
            heatmap_color_center = "white"
            heatmap_color_up = 0.3
            heatmap_color_down = 0.7
            heatmap_color_missing = "black"

            heatmap_max_value = abs(heatmap_center_value - max_value)
            heatmap_min_value = abs(heatmap_center_value - min_value)

            if heatmap_center_value <= min_value:
                heatmap_max_value = heatmap_min_value + heatmap_max_value
            else:
                heatmap_max_value = max(heatmap_min_value, heatmap_max_value)



        # scale the tree
        if not args.height:
            args.height = None
        if not args.width:
            args.width = None

        f2color = {}
        f2last_seed = {}
        for node in t.traverse():
            node.img_style['size'] = 0
            if len(node.children) == 1:
                node.img_style['size'] = 2
                node.img_style['shape'] = "square"
                node.img_style['fgcolor'] = "steelblue"

            ftype_pos = defaultdict(int)

            for findex, f in enumerate(FACES):
                if (f['nodetype'] == 'any' or
                    (f['nodetype'] == 'leaf' and node.is_leaf()) or
                    (f['nodetype'] == 'internal' and not node.is_leaf())):


                    # if node passes face filters
                    if node_matcher(node, f["filters"]):
                        if f["value"].startswith("@"):
                            fvalue = getattr(node, f["value"][1:], None)
                        else:
                            fvalue = f["value"]

                        # if node's attribute has content, generate face
                        if fvalue is not None:
                            fsize = f["size"]
                            fbgcolor = f["bgcolor"]
                            fcolor = f['color']

                            if fcolor:
                                # Parse color options
                                auto_m = re.search("auto\(([^)]*)\)", fcolor)
                                if auto_m:
                                    target_attr = auto_m.groups()[0].strip()
                                    if not target_attr :
                                        color_keyattr = f["value"]
                                    else:
                                        color_keyattr = target_attr

                                    color_keyattr = color_keyattr.lstrip('@')
                                    color_bin = getattr(node, color_keyattr, None)

                                    last_seed = f2last_seed.setdefault(color_keyattr, random.random())

                                    seed = last_seed + 0.10 + random.uniform(0.1, 0.2)
                                    f2last_seed[color_keyattr] = seed

                                    fcolor = f2color.setdefault(color_bin, random_color(h=seed))

                            if fbgcolor:
                                # Parse color options
                                auto_m = re.search("auto\(([^)]*)\)", fbgcolor)
                                if auto_m:
                                    target_attr = auto_m.groups()[0].strip()
                                    if not target_attr :
                                        color_keyattr = f["value"]
                                    else:
                                        color_keyattr = target_attr

                                    color_keyattr = color_keyattr.lstrip('@')
                                    color_bin = getattr(node, color_keyattr, None)

                                    last_seed = f2last_seed.setdefault(color_keyattr, random.random())

                                    seed = last_seed + 0.10 + random.uniform(0.1, 0.2)
                                    f2last_seed[color_keyattr] = seed

                                    fbgcolor = f2color.setdefault(color_bin, random_color(h=seed))

                            if f["ftype"] == "text":
                                if f.get("format", None):
                                    fvalue = f["format"] % fvalue

                                F = TextFace(fvalue,
                                             fsize = fsize,
                                             fgcolor = fcolor or "black",
                                             fstyle = f.get('fstyle', None))

                            elif f["ftype"] == "fullseq":
                                F = faces.SeqMotifFace(seq=fvalue, seq_format="seq",
                                                       gap_format="line",
                                                       height=fsize)
                            elif f["ftype"] == "compactseq":
                                F = faces.SeqMotifFace(seq=fvalue, seq_format="compactseq",
                                                       gap_format="compactseq",
                                                       height=fsize)
                            elif f["ftype"] == "blockseq":
                                F = faces.SeqMotifFace(seq=fvalue, 
                                                       height=fsize,
                                                       fgcolor=fcolor or "slategrey",
                                                       bgcolor=fbgcolor or "slategrey",
                                                       scale_factor = 1.0)
                                fbgcolor = None
                            elif f["ftype"] == "bubble":
                                try:
                                    v = float(fvalue)
                                except ValueError:
                                    rad = fsize
                                else:
                                    rad = fsize * v
                                F = faces.CircleFace(radius=rad, style="sphere",
                                                     color=fcolor or "steelblue")

                            elif f["ftype"] == "heatmap":
                                if not f['column']:
                                    col = ftype_pos[f["pos"]]
                                else:
                                    col = f["column"]

                                for i, value in enumerate(heatmap_data.get(node.name, [])):
                                    ftype_pos[f["pos"]] += 1

                                    if value is None:
                                        color = heatmap_color_missing
                                    elif value > heatmap_center_value:
                                        color = gradient_color(abs(heatmap_center_value - value), heatmap_max_value, hue=heatmap_color_up)
                                    elif value < heatmap_center_value:
                                        color = gradient_color(abs(heatmap_center_value - value), heatmap_max_value, hue=heatmap_color_down)
                                    else:
                                        color = heatmap_color_center
                                    node.add_face(RectFace(20, 20, color, color), position="aligned", column=col + i)
                                    # Add header
                                    # for i, name in enumerate(header):
                                    #    nameF = TextFace(name, fsize=7)
                                    #    nameF.rotation = -90
                                    #    tree_style.aligned_header.add_face(nameF, column=i)
                                F = None

                            elif f["ftype"] == "profile":
                                # internal profiles?
                                F = None
                            elif f["ftype"] == "barchart":
                                F = None
                            elif f["ftype"] == "piechart":
                                F = None



                            # Add the Face
                            if F:
                                F.opacity = f['opacity'] or 1.0

                                # Set face general attributes
                                if fbgcolor:
                                    F.background.color = fbgcolor

                                if not f['column']:
                                    col = ftype_pos[f["pos"]]
                                    ftype_pos[f["pos"]] += 1
                                else:
                                    col = f["column"]
                                node.add_face(F, column=col, position=f["pos"])

        if args.image:
            if tindex > 0: 
                t.render("t%d.%s" %(tindex, args.image),
                         tree_style=ts, w=args.width, h=args.height, units=args.size_units)
            else:
                t.render("%s" %(args.image),
                         tree_style=ts, w=args.width, h=args.height, units=args.size_units)                
        else:
            t.show(None, tree_style=ts)


def parse_faces(face_args):
    faces = []
    for fargs in face_args:
        face = {"filters":[],
                "ftype":"text",
                "value":None,
                "pos": "branch-right",
                "color": None,
                "bgcolor": None,
                "size": 12,
                "fstyle":None, # review this name
                "column":None,
                "format":None,
                "nodetype":"leaf",
                "opacity":None,
        }

        for clause in map(str.strip,fargs.split(',')):
            key, value = list(map(str.strip, clause.split(":")))
            key = key.lower()
            if key == "if":
                m = re.search("([^=><~!]+)(>=|<=|!=|~=|=|>|<)([^=><~!]+)", value)
                if not m:
                    raise ValueError("Invalid syntaxis in 'if' clause: %s" %clause)
                else:
                    target, op, value = list(map(str.strip, m.groups()))
                    target = target.lstrip('@')
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                    face["filters"].append([target, op, value])
            elif key == "pos":
                try:
                    face["pos"] = POSNAMES[value]
                except KeyError:
                    raise ValueError("Invalid face position: %s" %clause)
            elif key == "nodetype":
                value = value.lower()
                if value != "any" and value != "internal" and value != "leaf":
                    raise ValueError("Invalid nodetype: %s" %clause)
                face["nodetype"] = value
            elif key == "size":
                face["size"] = int(value)
            elif key == "opacity":
                face["opacity"] = float(value)
            elif key == "column":
                face["column"] = int(value)
            elif key == "color":
                if value.endswith("()"):
                    func_name = value[0:-2]
                face[key] = value
            elif key == "fstyle":
                if value != 'italic' and value != 'bold':
                    raise ValueError("valid style formats are: italic, bold [%s]" %clause)
                face[key] = value
            elif key == "format":
                if "%" not in value:
                    print(value)
                    raise ValueError("format attribute should contain one format char: ie. %%s [%s]" %clause)
                face[key] = value.strip("\"")
            elif key in face:
                face[key] = value
            else:
                raise ValueError("unknown keyword in face options: %s" %clause )
        faces.append(face)
    return faces

def maptrees_layout(node):
    node.img_style["size"] = 0
    if getattr(node, "maptrees_support", "NA") != "NA":
        f = CircleFace(radius=float(node.maptrees_support)/10, color="blue", style="sphere")        
        f.opacity = 0.5
        add_face_to_node(f, node, column=1, position="float")       
        add_face_to_node(AttrFace("maptrees_support"), node, column=1, position="branch-top")
        
    if getattr(node, "maptrees_treeko_support", "NA") != "NA":
        add_face_to_node(f, node, column=1, position="float")       
        add_face_to_node(AttrFace("maptrees_treeko_support"), node, column=1, position="branch-bottom")




