from .evolevents import EvolEvent

__all__ = ["get_evol_events_from_leaf", "get_evol_events_from_root"]

def get_evol_events_from_leaf(node, sos_thr=0.0):
    """ Returns a list of duplication and speciation events in
    which the current node has been involved. Scanned nodes are
    also labeled internally as dup=True|False. You can access this
    labels using the 'node.dup' sintaxis.

    Method: the algorithm scans all nodes from the given leafName to
    the root. Nodes are assumed to be duplications when a species
    overlap is found between its child linages. Method is described
    more detail in:

    "The Human Phylome." Huerta-Cepas J, Dopazo H, Dopazo J, Gabaldon
    T. Genome Biol. 2007;8(6):R109.
    """
    # Get the tree's root
    root = node.root

    try:
        outg1, outg2 = root.get_children()  # outgroups
    except ValueError:
        raise TypeError("Tree is not rooted")

    smaller_outg = outg1 if len(outg1) < len(outg2) else outg2

    # Prepare to browse tree from leaf to root
    all_events = []
    current  = node
    ref_spcs = node.species
    sister_leaves  = set([])
    browsed_spcs   = set([current.species])
    browsed_leaves = set([current])
    # get family Size
    fSize = sum(1 for n in root.leaves() if n.species == ref_spcs)

    # Clean previous analysis
    for n in root.traverse():
        n.del_prop("evoltype")

    while current.up:
        for s in current.get_sisters():
            for leaf in s.leaves():
                sister_leaves.add(leaf)
        # Process sister node only if there is any new sequence.
        # (previene dupliaciones por nombres repetidos)
        sister_leaves = sister_leaves.difference(browsed_leaves)
        if len(sister_leaves)==0:
            current = current.up
            continue
        # Gets species at both sides of event
        sister_spcs     = set([n.species for n in sister_leaves])
        overlaped_spces = browsed_spcs & sister_spcs
        all_spcs        = browsed_spcs | sister_spcs
        score = float(len(overlaped_spces))/len(all_spcs)
        # Creates a new evolEvent
        event = EvolEvent()
        event.fam_size   = fSize
        event.seed      = node.name
        # event.e_newick  = current.up.get_newick()  # high mem usage!!
        event.sos = score
        event.outgroup  = smaller_outg.name
        # event.allseqs   = set(current.up.get_leaf_names())
        event.in_seqs = set([n.name for n in browsed_leaves])
        event.out_seqs = set([n.name for n in sister_leaves])
        event.inparalogs  = set([n.name for n in browsed_leaves if n.species == ref_spcs])

        # If species overlap: duplication
        if score > sos_thr:
            event.node = current.up
            event.etype = "D"
            event.outparalogs = set([n.name for n in sister_leaves  if n.species == ref_spcs])
            event.orthologs   = set([])
            current.up.add_prop("evoltype","D")
            all_events.append(event)

        # If NO species overlap: speciation
        elif score <= sos_thr:
            event.node = current.up
            event.etype = "S"
            event.orthologs = set([n.name for n in sister_leaves if n.species != ref_spcs])
            event.outparalogs = set([])
            current.up.add_prop("evoltype","S")
            all_events.append(event)

        # Updates browsed species
        browsed_spcs   |= sister_spcs
        browsed_leaves |= sister_leaves
        sister_leaves  = set([])
        # And keep ascending
        current = current.up
    return all_events

def get_evol_events_from_root(node, sos_thr):
    """ Returns a list of **all** duplication and speciation
    events detected after this node. Nodes are assumed to be
    duplications when a species overlap is found between its child
    linages. Method is described more detail in:

    "The Human Phylome." Huerta-Cepas J, Dopazo H, Dopazo J, Gabaldon
    T. Genome Biol. 2007;8(6):R109.
    """

    # Get the tree's root
    root = node.root

    # Checks that is actually rooted
    outgroups = root.get_children()
    if len(outgroups) != 2:
        raise TypeError("Tree is not rooted")

    # Cautch the smaller outgroup (will be stored as the tree outgroup)
    o1 = set([n.name for n in outgroups[0].leaves()])
    o2 = set([n.name for n in outgroups[1].leaves()])


    if len(o2)<len(o1):
        smaller_outg = outgroups[1]
    else:
        smaller_outg = outgroups[0]

    # Get family size
    fSize = len( [n for n in root.leaves()] )

    # Clean data from previous analyses
    for n in list(root.descendants())+[root]:
        n.del_prop("evoltype")

    # Gets Prepared to browse the tree from root to leaves
    to_visit = []
    current = root
    all_events = []
    while current:
        # Gets childs and appends them to the To_visit list
        childs = current.get_children()
        to_visit += childs
        if len(childs)>2:
            raise TypeError("nodes are expected to have two childs.")
        elif len(childs)==0:
            pass # leaf
        else:
            # Get leaves and species at both sides of event
            sideA_leaves= set([n for n in childs[0].leaves()])
            sideB_leaves= set([n for n in childs[1].leaves()])
            sideA_spcs  = set([n.species for n in childs[0].leaves()])
            sideB_spcs  = set([n.species for n in childs[1].leaves()])
            # Calculates species overlap
            overlaped_spcs = sideA_spcs & sideB_spcs
            all_spcs       = sideA_spcs | sideB_spcs
            score = float(len(overlaped_spcs))/len(all_spcs)

            # Creates a new evolEvent
            event = EvolEvent()
            event.fam_size   = fSize
            event.branch_supports = [current.support, current.children[0].support, current.children[1].support]
            # event.seed      = leafName
            # event.e_newick  = current.up.get_newick()  # high mem usage!!
            event.sos = score
            event.outgroup_spcs  = smaller_outg.get_species()
            event.in_seqs = set([n.name for n in sideA_leaves])
            event.out_seqs = set([n.name for n in sideB_leaves])
            event.inparalogs  = set([n.name for n in sideA_leaves])
            # If species overlap: duplication
            if score >sos_thr:
                event.node = current
                event.etype = "D"
                event.outparalogs = set([n.name for n in sideB_leaves])
                event.orthologs   = set([])
                current.add_prop("evoltype","D")
            # If NO species overlap: speciation
            else:
                event.node = current
                event.etype = "S"
                event.orthologs = set([n.name for n in sideB_leaves])
                event.outparalogs = set([])
                current.add_prop("evoltype","S")

            all_events.append(event)
        # Keep visiting nodes
        try:
            current = to_visit.pop(0)
        except IndexError:
            current = None
    return all_events
