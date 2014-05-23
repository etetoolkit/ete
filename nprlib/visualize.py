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
            node.img_style['size'] = 4
            node.img_style['shape'] = 'square'
    
    def ly_leaf_names(node):
        if node.is_leaf():
            add_face_to_node(NAME_FACE, node, column=0, position='branch-right')

    def ly_supports(node):
        if not node.is_leaf():
            if node.support <= 0.99:
                supFace = TextFace("%0.2g" %node.support, fsize=7, fgcolor='brick')
                add_face_to_node(supFace, node, column=0, position='branch-top')
            
    def ly_tax_labels(node):
        if node.is_leaf():
            c = LABEL_START_COL
            for tname in TRACKED_CLADES:
                if hasattr(node, "named_lineage") and tname in node.named_lineage:
                    linF = TextFace(tname, fsize=10, fgcolor='white')
                    linF.margin_left = 3
                    linF.background.color = lin2color[tname]
                    add_face_to_node(linF, node, c, position='aligned')
                    c += 1
            for n in xrange(c, len(TRACKED_CLADES) - (c-1)):
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

                
    TRACKED_CLADES = ["Eukaryota", "Viridiplantae", "Opisthokonta", "Fungi",
                      "Alveolata", "Metazoa", "Stramenopiles", "Rhodophyta",
                      "Amoebozoa", "Crypthophyta", "Bacteria",
                      "Alphaproteobacteria", "Betaproteobacteria", "Cyanobacteria",
                      "Gammaproteobacteria", "Apicomplexa"]
      
    colors = random_color(num=len(TRACKED_CLADES))
    lin2color = dict([(ln, colors[i]) for i, ln in enumerate(TRACKED_CLADES)])

    NAME_FACE = AttrFace('name', fsize=10, fgcolor='#444444')
        
    LABEL_START_COL = 10
    ALG_START_COL = 40
    ts = TreeStyle()
    ts.draw_aligned_faces_as_table = True
    ts.draw_guiding_lines = False
    ts.show_leaf_name = False
    ts.show_branch_support = False
    ts.layout_fn = [ly_basic, ly_leaf_names, ly_supports, ly_tax_labels, ly_block_alg]
    #tree.show(tree_style=ts)
    tree.render(outfile, tree_style=ts)

        

    

    
