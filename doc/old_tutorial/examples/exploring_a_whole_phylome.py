from ete3 import PhylomeDBConnector
# This connects to the main phylomeDB server (default parameters)
p = PhylomeDBConnector()
PHYLOME_ID = 1
# This is the species code/age dictionary used to correctly root the
# tree in the human phylome. You can define your own, or use the
# midpoint outgroup method
species2age = {'Aga': 8, 'Ago': 9, 'Ame': 8, 'Ath': 10, 'Bta': 3, 'Cal': 9, 'Cbr': 8,\
             'Cel': 8, 'Cfa': 3, 'Cgl': 9, 'Cin': 7, 'Cne': 9, 'Cre': 10, 'Ddi': 10, \
             'Dha': 9, 'Dme': 8, 'Dre': 6, 'Ecu': 9, 'Fru': 6, 'Gga': 4, 'Gth': 10,\
             'Gze': 9, 'Hsa': 1, 'Kla': 9, 'Lma': 10, 'Mdo': 3, 'Mms': 3, 'Mmu': 2,\
             'Ncr': 9, 'Pfa': 10, 'Pte': 10, 'Ptr': 2, 'Pyo': 10, 'Rno': 3, 'Sce': 9,\
             'Spb': 9, 'Tni': 6, 'Xtr': 5, 'Yli': 9      }
# Iterator over each sequence in the human proteme
for i, seqid in enumerate(p.get_seed_ids(PHYLOME_ID)):
    if i>2: break # Just process the first 2 ids
    winner_model, lks, t = p.get_best_tree(seqid, PHYLOME_ID)
    # If tree was sucsesfully reconstructed, runs the species overalp algorithm
    if t and seqid in t:
        outgroup = t.get_farthest_oldest_leaf(species2age)
        # Returned outgroup is used to root the tree
        t.set_outgroup(outgroup)
        # Finds the node representing the seed sequence.
        # We want the orthology relationships of such sequence.
        seed_node = t.search_nodes(name=seqid)[0]
        evol_events = seed_node.get_my_evol_events()
        for ev in evol_events:
            # Speciation event
            if ev.etype == "S":
                inparalogs = filter(lambda n: n.startswith("Hsa"), ev.in_seqs)
                print 'ORTHOLOGY RELATIONSHIP:', ','.join(inparalogs), "<===>", ','.join(ev.out_seqs)
