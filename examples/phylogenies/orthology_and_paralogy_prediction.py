from ete4 import PhyloTree

# Load an example tree.
nw = """
((Dme_001,Dme_002),(((Cfa_001,Mms_001),((Hsa_001,Ptr_001),Mmu_001)),
(Ptr_002,(Hsa_002,Mmu_002))));
"""

t = PhyloTree(nw)

print(t)
#  ╭─┬╴Dme_001
#  │ ╰╴Dme_002
# ─┤   ╭─┬╴Cfa_001
#  │ ╭─┤ ╰╴Mms_001
#  │ │ │ ╭─┬╴Hsa_001
#  ╰─┤ ╰─┤ ╰╴Ptr_001
#    │   ╰╴Mmu_001
#    ╰─┬╴Ptr_002
#      ╰─┬╴Hsa_002
#        ╰╴Mmu_002

# To obtain all the evolutionary events involving a given leaf node we
# use the get_my_evol_events method.
human_seq = t['Hsa_001']

events = human_seq.get_my_evol_events()  # obtain its evolutionary events

# Print its orthology and paralogy relationships.
print('Events detected that involve Hsa_001:')
for ev in events:
    r = {'S': 'Orthology', 'D': 'Paralogy'}[ev.etype]  # relationship
    print('%11s: %s <==> %s' % (r, ','.join(ev.in_seqs), ','.join(ev.out_seqs)))

# Events detected that involve Hsa_001:
#   Orthology: Hsa_001 <==> Ptr_001
#   Orthology: Ptr_001,Hsa_001 <==> Mmu_001
#   Orthology: Ptr_001,Hsa_001,Mmu_001 <==> Mms_001,Cfa_001
#    Paralogy: Mms_001,Mmu_001,Ptr_001,Hsa_001,Cfa_001 <==> Ptr_002,Mmu_002,Hsa_002
#   Orthology: Hsa_002,Mms_001,Mmu_001,Ptr_001,Hsa_001,Ptr_002,Mmu_002,Cfa_001 <==> Dme_001,Dme_002

# Alternatively, you can scan the whole tree topology.
events = t.get_descendant_evol_events()

# Print its orthology and paralogy relationships.
print('Events detected from the root of the tree:')
for ev in events:
    r = {'S': 'Orthology', 'D': 'Paralogy'}[ev.etype]  # relationship
    print('%11s: %s <==> %s' % (r, ','.join(ev.in_seqs), ','.join(ev.out_seqs)))
# Events detected from the root of the tree:
#   Orthology: Dme_001,Dme_002 <==> Hsa_002,Mms_001,Mmu_001,Ptr_001,Hsa_001,Ptr_002,Mmu_002,Cfa_001
#    Paralogy: Dme_001 <==> Dme_002
#    Paralogy: Mms_001,Mmu_001,Ptr_001,Hsa_001,Cfa_001 <==> Ptr_002,Mmu_002,Hsa_002
#   Orthology: Mms_001,Cfa_001 <==> Ptr_001,Hsa_001,Mmu_001
#   Orthology: Ptr_002 <==> Mmu_002,Hsa_002
#   Orthology: Cfa_001 <==> Mms_001
#   Orthology: Ptr_001,Hsa_001 <==> Mmu_001
#   Orthology: Hsa_002 <==> Mmu_002
#   Orthology: Hsa_001 <==> Ptr_001

# If we are only interested in the orthology and paralogy relationship
# among a given set of species, we can filter the list of sequences.
def fseqs(slist):
    """Return only the sequences in slist that are from human or mouse."""
    return [s for s in slist if s.startswith('Hsa') or s.startswith('Mms')]

print('Paralogy relationships among human and mouse:')
for ev in events:
    if ev.etype == 'D':
        # Prints paralogy relationships considering only human and
        # mouse. Some duplication events may not involve such species,
        # so they will be empty.
        print(','.join(fseqs(ev.in_seqs)), '<==>', ','.join(fseqs(ev.out_seqs)))
# Paralogy relationships among human and mouse:
#  <==>
# Hsa_001,Mms_001 <==> Hsa_002

# Note that besides the list of events returned, the detection
# algorithm has labeled the tree nodes according with the
# predictions. We can use such lables as normal node features.
dups = list(t.search_nodes(evoltype='D'))  # get all duplication nodes
