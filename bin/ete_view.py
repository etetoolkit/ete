#! /usr/bin/python 
import os 
import re
import sys

from common import parse_faces, node_matcher
from ete_dev import Tree, PhyloTree, TextFace, faces, TreeStyle, add_face_to_node, random_color
from collections import defaultdict
import random

__all__ = ["main"]

__DESCRIPTION__ = """
The ETE tree viewer. 
"""

FACES = []

def user_species_naming_function(name):
    try:
        return SPCODE_REGEXP.search(name).groups()[0]
    except Exception:
        print >>sys.stderr, "Unable to capture species code in: ", name
        return "Unknown"

def layout_heatmap(node):
    if node.is_leaf():
        if getattr(node, heatmap_attr, None):
            for i, v in enumerate(heatmap_array.get(getattr(node, heatmap_attr, []))):
                heatmap_fg = heatmap_bg = heatmap_color_profile[v]                
                rF = RectFace(heatmap_w, heatmap_h, heatmap_fg, heatmap_bg)
                add_face_to_node(rF, node, heatmmap_colstart + i, position='aligned')

def layout_faces(node):
    ftype_pos = defaultdict(int)
    for f in FACES:
        if (f['nodetype'] == 'any' or 
            (f['nodetype'] == 'leaf' and node.is_leaf()) or
            (f['nodetype'] == 'internal' and not node.is_leaf())):            
            if node_matcher(node, f["filters"]):
                if f["value"].startswith("@"):
                    attr = getattr(node, f["value"][1:], None)
                else:
                    attr = f["value"]                    
                if attr != None:
                    F = TextFace(attr,
                                 fsize=f.get("size", 10),
                                 fgcolor=f.get('color', 'black'))
                    
                    if f['bgcolor']:
                        F.background.color = f['bgcolor']

                    if not f['column']:
                        col = ftype_pos[f["pos"]]
                        ftype_pos[f["pos"]] += 1    
                    else:
                        col = f["column"]
                    # Add the Face
                    add_face_to_node(F, node, column=col,
                                     position=f["pos"])
                    
                    
def layout_block_alg(node):
    pass
                
def main(args):
    global FACES
    
    if args.face:
        FACES = parse_faces(args.face)
    
    tfile = args.src_trees[0]

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

    if args.outgroup:
        if len(args.outgroup) > 1:
            outgroup = t.get_common_ancestor(args.outgroup)
        else:
            outgroup = t & args.outgroup[0]
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
        
    # scale the tree
    if not args.height: 
        args.height = None
    if not args.width: 
        args.width = None

    if args.text_mode:
        print t.get_ascii(show_internal=args.show_internal_names, attributes = args.show_attributes)
    else:    
        #ts.layout_fn = [layout_faces]
        t.populate(10)
        
        f2color = {}
        f2last_seed = {}
        for node in t.traverse():
            ftype_pos = defaultdict(int)
            for f in FACES:
                last_seed = f2last_seed.setdefault(f["value"], random.random())
                if (f['nodetype'] == 'any' or 
                    (f['nodetype'] == 'leaf' and node.is_leaf()) or
                    (f['nodetype'] == 'internal' and not node.is_leaf())):            
                    if node_matcher(node, f["filters"]):
                        if f["value"].startswith("@"):
                            attr = getattr(node, f["value"][1:], None)
                        else:
                            attr = f["value"]                    
                        if attr != None:
                            if f['color'] == 'auto()':
                                seed = last_seed + 0.10 + random.uniform(0.1, 0.2)
                                f2last_seed[f["value"]] = seed
                                color = f2color.setdefault(attr, random_color(h=seed))

                            else:
                                color = f['color']
                            F = TextFace(attr,
                                         fsize=f.get("size", 10),
                                         fgcolor=color)

                            if f['bgcolor']:
                                F.background.color = f['bgcolor']

                            if not f['column']:
                                col = ftype_pos[f["pos"]]
                                ftype_pos[f["pos"]] += 1    
                            else:
                                col = f["column"]
                            # Add the Face
                            node.add_face(F, column=col, position=f["pos"])

        
        if args.image:
            t.render(args.image, tree_style=ts, w=args.width, h=args.height, units=args.size_units)
        else:
            t.show(None, tree_style=ts)
