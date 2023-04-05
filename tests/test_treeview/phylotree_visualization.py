from ... import PhyloTree, TreeStyle

alg = """
 >Dme_001
 MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEAL--YYASQTDDIKDRREEAH
 >Dme_002
 MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAH
 >Cfa_001
 MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
 >Mms_001
 MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
 >Hsa_001
 MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
 >Ptr_002
 MAEIPDATIQ-FMALTNVSHNIAVQY--EFGDLNEALNSY--YQTDDQKDRREEAH
 >Mmu_002
 MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
 >Hsa_002
 MAEAPDETIQQFM-LTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
 >Mmu_001
 MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
 >Ptr_001
 MAEIPDATIQ-FMALTNVSHNIAVQY--EFGDLNEALNSY--YQTDDQKDRREEAH
 >Mmu_001
 MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
"""

def get_example_tree():

    # Performs a tree reconciliation analysis
    gene_tree_nw = '((Dme_001,Dme_002),(((Cfa_001,Mms_001),((Hsa_001,Ptr_001),Mmu_001)),(Ptr_002,(Hsa_002,Mmu_002))));'
    species_tree_nw = "((((Hsa, Ptr), Mmu), (Mms, Cfa)), Dme);"
    genetree = PhyloTree(gene_tree_nw)
    sptree = PhyloTree(species_tree_nw)
    recon_tree, events = genetree.reconcile(sptree)
    recon_tree.link_to_alignment(alg)
    return recon_tree, TreeStyle()

if __name__ == "__main__":
    # Visualize the reconciled tree
    t, ts = get_example_tree()
    t.show(tree_style=ts)
    #recon_tree.render("phylotree.png", w=750)

