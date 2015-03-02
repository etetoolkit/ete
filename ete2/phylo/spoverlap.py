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

from evolevents import EvolEvent

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
    root = node.get_tree_root()

    # Checks that is actually rooted
    outgroups = root.get_children()
    if len(outgroups) != 2:
        raise TypeError, "Tree is not rooted"

    # Cautch the smaller outgroup (will be stored as the tree
    # outgroup)
    o1 = set([n.name for n in outgroups[0].get_leaves()])
    o2 = set([n.name for n in outgroups[1].get_leaves()])

    if len(o2)<len(o1):
        smaller_outg = outgroups[1]
    else:
        smaller_outg = outgroups[0]


    # Prepare to browse tree from leaf to root
    all_events = []
    current  = node
    ref_spcs = node.species
    sister_leaves  = set([])
    browsed_spcs   = set([current.species])
    browsed_leaves = set([current])
    # get family Size
    fSize =  len([n for n in root.get_leaves() if n.species == ref_spcs])

    # Clean previous analysis
    for n in root.get_descendants()+[root]:
        n.del_feature("evoltype")

    while current.up:
        # distances control (0.0 distance check)
        d = 0
        for s in current.get_sisters():
            for leaf in s.get_leaves():
                d += current.get_distance(leaf)
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
        if score > sos_thr:# and d > 0.0: Removed branch control. 
            event.node = current.up
            event.etype = "D"
            event.outparalogs = set([n.name for n in sister_leaves  if n.species == ref_spcs])
            event.orthologs   = set([])
            current.up.add_feature("evoltype","D")
            all_events.append(event)

        # If NO species overlap: speciation
        elif score == sos_thr:
            event.node = current.up
            event.etype = "S"
            event.orthologs = set([n.name for n in sister_leaves if n.species != ref_spcs])
            event.outparalogs = set([])
            current.up.add_feature("evoltype","S")
            all_events.append(event)
        else:
            pass # do not add event if distances == 0

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
    root = node.get_tree_root()

    # Checks that is actually rooted
    outgroups = root.get_children()
    if len(outgroups) != 2:
        raise TypeError, "Tree is not rooted"

    # Cautch the smaller outgroup (will be stored as the tree outgroup)
    o1 = set([n.name for n in outgroups[0].get_leaves()])
    o2 = set([n.name for n in outgroups[1].get_leaves()])


    if len(o2)<len(o1):
        smaller_outg = outgroups[1]
    else:
        smaller_outg = outgroups[0]

    # Get family size
    fSize = len( [n for n in root.get_leaves()] )

    # Clean data from previous analyses
    for n in root.get_descendants()+[root]:
        n.del_feature("evoltype")

    # Gets Prepared to browse the tree from root to leaves
    to_visit = []
    current = root
    all_events = []
    while current:
        # Gets childs and appends them to the To_visit list
        childs = current.get_children()
        to_visit += childs
        if len(childs)>2:
            raise TypeError, "nodes are expected to have two childs."
        elif len(childs)==0:
            pass # leaf
        else:
            # Get leaves and species at both sides of event
            sideA_leaves= set([n for n in childs[0].get_leaves()])
            sideB_leaves= set([n for n in childs[1].get_leaves()])
            sideA_spcs  = set([n.species for n in childs[0].get_leaves()])
            sideB_spcs  = set([n.species for n in childs[1].get_leaves()])
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
                current.add_feature("evoltype","D")
            # If NO species overlap: speciation
            else:
                event.node = current
                event.etype = "S"
                event.orthologs = set([n.name for n in sideB_leaves])
                event.outparalogs = set([])
                current.add_feature("evoltype","S")

            all_events.append(event)
        # Keep visiting nodes
        try:
            current = to_visit.pop(0)
        except IndexError:
            current = None
    return all_events
