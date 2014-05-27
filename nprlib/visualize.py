import re

def draw_tree(tree, conf, outfile):
    try:
        from ete_dev import (add_face_to_node, AttrFace, TextFace, TreeStyle,
                             SequenceFace, random_color, SeqMotifFace)
    except ImportError as e:
        print e
        return
  
    def ly_basic(node):
        if node.is_leaf():
            node.img_style['size'] = 0
        else:
            node.img_style['size'] = 0
            node.img_style['shape'] = 'square'

        node.img_style['hz_line_width'] = 1
        node.img_style['vt_line_width'] = 1
        
            
    def ly_leaf_names(node):
        if node.is_leaf():
            spF = TextFace(node.species, fsize=10, fgcolor='#444444', fstyle='italic', ftype='Helvetica')
            geneF = TextFace(" (%s)" %node.genename, fsize=8, fgcolor='#777777', ftype='Helvetica')
            add_face_to_node(spF, node, column=0, position='branch-right')
            add_face_to_node(geneF, node, column=1, position='branch-right')

    def ly_supports(node):
        if not node.is_leaf():
            if node.support <= 0.99:
                supFace = TextFace("%d" %(node.support*100), fsize=7, fgcolor='indianred')
                add_face_to_node(supFace, node, column=0, position='branch-top')
            
    def ly_tax_labels(node):
        if node.is_leaf():
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
            
            for n in xrange(c, len(TRACKED_CLADES)):
                add_face_to_node(TextFace('', fsize=10, fgcolor='slategrey'), node, c, position='aligned')
                c+=1

    def ly_full_alg(node):
        pass

    def ly_block_alg(node):
        if node.is_leaf():
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
                            w = end-start
                            motifs.append([start, end, "[]", w, 12, "slategrey", "slategrey", None])
                            last_lt = None
                    elif lt == '-':
                        if last_lt is not None:
                            start, end = last_lt, c-1
                            w = end-start
                            motifs.append([start, end, "[]", w, 12, "grey", "slategrey", None])
                            last_lt = None

                seqFace = SeqMotifFace(node.sequence, motifs,
                                       intermotif_format="line",
                                       seqtail_format="line", scale_factor=1)
                add_face_to_node(seqFace, node, ALG_START_COL, aligned=True)

                
    TRACKED_CLADES = ["Eukaryota", "Viridiplantae",  "Fungi",
                      "Alveolata", "Metazoa", "Stramenopiles", "Rhodophyta",
                      "Amoebozoa", "Crypthophyta", "Bacteria",
                      "Alphaproteobacteria", "Betaproteobacteria", "Cyanobacteria",
                      "Gammaproteobacteria",]
    
    # ["Opisthokonta",  "Apicomplexa"]
    
    colors = random_color(num=len(TRACKED_CLADES), s=0.45)
    lin2color = dict([(ln, colors[i]) for i, ln in enumerate(TRACKED_CLADES)])

    NAME_FACE = AttrFace('name', fsize=10, fgcolor='#444444')
        
    LABEL_START_COL = 10
    ALG_START_COL = 40
    ts = TreeStyle()
    ts.draw_aligned_faces_as_table = True
    ts.draw_guiding_lines = False
    ts.show_leaf_name = False
    ts.show_branch_support = False
    ts.scale = 160
    ts.layout_fn = [ly_basic, ly_leaf_names, ly_supports, ly_tax_labels]
    #tree.show(tree_style=ts)

    tree.set_species_naming_function(spname)
    annotate_tree_with_ncbi(tree)
    a = tree.search_nodes(species='Dictyostelium discoideum')[0]
    b = tree.search_nodes(species='Chondrus crispus')[0]
    tree.set_outgroup(tree.get_common_ancestor([a, b]))
    tree.swap_children()
    
    tree.render(outfile, tree_style=ts, w=170, units='mm', dpi=150)
    tree.render(outfile+'.svg', tree_style=ts, w=170, units='mm', dpi=150)
    tree.render(outfile+'.pdf', tree_style=ts, w=170, units='mm', dpi=150)


def annotate_tree_with_ncbi(tree):
    from ete_dev.ncbi_taxonomy import ncbiquery as ncbi
    ncbi.connect_database()
    name2sp = ncbi.get_name_translator(tree.get_species())
    for lf in tree.iter_leaves():
        lf.add_features(taxid=name2sp.get(lf.species, 0))
        lf.add_features(genename=re.sub('\{[^}]+\}', '', lf.name).strip())
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
            print 'name', name        , taxid, tax2name
        return tax2name.get(int(taxid), taxid)
