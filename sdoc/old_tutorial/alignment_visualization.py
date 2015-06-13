from ete3 import PhyloTree, PhylomeDBConnector, SeqGroup

p = PhylomeDBConnector()
w,x, t =  p.get_best_tree("Hsa0000001", 1)
a, l = p.get_clean_alg("Hsa0000001", 1)
A = SeqGroup(a, "iphylip")
for s in A.id2seq:
    A.id2seq[s]=A.id2seq[s][:30]
t.link_to_alignment(A)
print t.get_species()
print t
t.set_outgroup(t&"Ddi0002240")

sp = PhyloTree("(((((((((((Hsa, Ptr), Mmu), ((Mms, Rno), (Bta, Cfa))), Mdo), Gga), Xtr), (Dre, Fru))),Cin) (Dme, Aga)), Ddi);")
reconciled, evs = t.reconcile(sp)
print reconciled
reconciled.show()
