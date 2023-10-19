import re

def draw_tree(tree, conf, outfile):
    try:
        from ... import (add_face_to_node, AttrFace, TextFace, TreeStyle, RectFace, CircleFace,
                         random_color, SeqMotifFace)
    except ImportError as e:
        print(e)
        return

    def ly_basic(node):
        if node.is_leaf:
            node.img_style['size'] = 0
        else:
            node.img_style['size'] = 0
            node.img_style['shape'] = 'square'
            if len(MIXED_RES) > 1 and hasattr(node, "tree_seqtype"):
                if node.tree_seqtype == "nt":
                    node.img_style["bgcolor"] = "#CFE6CA"
                    ntF = TextFace("nt", fsize=6, fgcolor='#444', ftype='Helvetica')
                    add_face_to_node(ntF, node, 10, position="branch-bottom")
            if len(NPR_TREES) > 1 and hasattr(node, "tree_type"):
                node.img_style['size'] = 4
                node.img_style['fgcolor'] = "steelblue"

        node.img_style['hz_line_width'] = 1
        node.img_style['vt_line_width'] = 1

    def ly_leaf_names(node):
        if node.is_leaf:
            spF = TextFace(node.species, fsize=10, fgcolor='#444444', fstyle='italic', ftype='Helvetica')
            add_face_to_node(spF, node, column=0, position='branch-right')
            if hasattr(node, 'genename'):
                geneF = TextFace(" (%s)" %node.genename, fsize=8, fgcolor='#777777', ftype='Helvetica')
                add_face_to_node(geneF, node, column=1, position='branch-right')

    def ly_supports(node):
        if not node.is_leaf and node.up:
            supFace = TextFace("%0.2g" %(node.support), fsize=7, fgcolor='indianred')
            add_face_to_node(supFace, node, column=0, position='branch-top')

    def ly_tax_labels(node):
        if node.is_leaf:
            c = LABEL_START_COL
            largest = 0
            for tname in TRACKED_CLADES:
                if hasattr(node, "named_lineage") and tname in node.named_lineage:
                    linF = TextFace(tname, fsize=10, fgcolor='white')
                    linF.margin_left = 3
                    linF.margin_right = 2
                    linF.background.color = lin2color[tname]
                    add_face_to_node(linF, node, c, position='aligned')
                    c += 1

            for n in range(c, len(TRACKED_CLADES)):
                add_face_to_node(TextFace('', fsize=10, fgcolor='slategrey'), node, c, position='aligned')
                c+=1

    def ly_full_alg(node):
        pass

    def ly_block_alg(node):
        if node.is_leaf:
            if 'sequence' in node.features:
                seqFace = SeqMotifFace(node.sequence, [])
                # [10, 100, "[]", None, 10, "black", "rgradient:blue", "arial|8|white|domain Name"],
                motifs = []
                last_lt = None
                for c, lt in enumerate(node.sequence):
                    if lt != '-':
                        if last_lt is None:
                            last_lt = c
                        if c+1 == len(node.sequence):
                            start, end = last_lt, c
                            motifs.append([start, end, "()", 0, 12, "slategrey", "slategrey", None])
                            last_lt = None
                    elif lt == '-':
                        if last_lt is not None:
                            start, end = last_lt, c-1
                            motifs.append([start, end, "()", 0, 12, "grey", "slategrey", None])
                            last_lt = None

                seqFace = SeqMotifFace(node.sequence, motifs,
                                       gap_format="line",
                                       scale_factor=ALG_SCALE)
                add_face_to_node(seqFace, node, ALG_START_COL, aligned=True)


    TRACKED_CLADES = ["Eukaryota", "Viridiplantae",  "Fungi",
                      "Alveolata", "Metazoa", "Stramenopiles", "Rhodophyta",
                      "Amoebozoa", "Crypthophyta", "Bacteria",
                      "Alphaproteobacteria", "Betaproteobacteria", "Cyanobacteria",
                      "Gammaproteobacteria",]

    colors = random_color(num=len(TRACKED_CLADES), s=0.45)
    lin2color = {ln: colors[i] for i, ln in enumerate(TRACKED_CLADES)}

    NAME_FACE = AttrFace('name', fsize=10, fgcolor='#444444')

    LABEL_START_COL = 10
    ALG_START_COL = 40
    ts = TreeStyle()
    ts.draw_aligned_faces_as_table = False
    ts.draw_guiding_lines = False
    ts.show_leaf_name = False
    ts.show_branch_support = False
    ts.layout_fn = [ly_basic, ly_leaf_names, ly_supports, ly_tax_labels]

    MIXED_RES = set()
    MAX_SEQ_LEN = 0
    NPR_TREES = []
    for n in tree.traverse():
        if hasattr(n, "tree_seqtype"):
            MIXED_RES.add(n.tree_seqtype)
        if hasattr(n, "tree_type"):
            NPR_TREES.append(n.tree_type)
        seq = getattr(n, "sequence", "")
        MAX_SEQ_LEN = max(len(seq), MAX_SEQ_LEN)

    if MAX_SEQ_LEN:
        ALG_SCALE = min(1, 1000./MAX_SEQ_LEN)
        ts.layout_fn.append(ly_block_alg)

    if len(NPR_TREES) > 1:
        rF = RectFace(4, 4, "steelblue", "steelblue")
        rF.margin_right = 10
        rF.margin_left = 10
        ts.legend.add_face(rF, 0)
        ts.legend.add_face(TextFace(" NPR node"), 1)
        ts.legend_position = 3

    if len(MIXED_RES) > 1:
        rF = RectFace(20, 20, "#CFE6CA", "#CFE6CA")
        rF.margin_right = 10
        rF.margin_left = 10
        ts.legend.add_face(rF, 0)
        ts.legend.add_face(TextFace(" Nucleotide based alignment"), 1)
        ts.legend_position = 3


    try:
        tree.set_species_naming_function(spname)
        annotate_tree_with_ncbi(tree)
        tree.set_outgroup(out)
        tree.reverse_children()
    except Exception:
        pass

    tree.render(outfile, tree_style=ts, w=170, units='mm', dpi=300)
    tree.render(outfile+'.svg', tree_style=ts, w=170, units='mm', dpi=300)
    tree.render(outfile+'.pdf', tree_style=ts, w=170, units='mm', dpi=300)

def annotate_tree_with_ncbi(tree):
    from ...ncbi_taxonomy import ncbiquery as ncbi
    ncbi.connect_database()
    name2sp = ncbi.get_name_translator(tree.get_species())
    for lf in tree.iter_leaves():
        lf.add_properties(taxid=name2sp.get(lf.species, [0])[0])
        lf.add_properties(genename=re.sub('\{[^}]+\}', '', lf.name).strip())
    ncbi.annotate_tree(tree, attr_name='taxid')

def spname(name):
    m = re.search('\{([^}]+)\}', name)
    if m:
        return m.groups()[0]
    else:
        return name.split('|')[0].strip().replace('_', ' ')
        taxid = name.split('.', 1)[0]

        tax2name = ncbi.get_taxid_translator([taxid])
        if int(taxid) not in tax2name:
            print('name', name, taxid, tax2name)
        return tax2name.get(int(taxid), taxid)
