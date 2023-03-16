__all__ = ["EvolEvent"]

class EvolEvent:
    """ Basic evolutionary event. It stores all the information about an
    event(node) ocurred in a phylogenetic tree.

    :attr:`etype` : ``D`` (Duplication), ``S`` (Speciation), ``L`` (gene loss),

    :attr:`in_seqs` : the list of sequences in one side of the event.

    :attr:`out_seqs` : the list of sequences in the other side of the event

    :attr:`node` : link to the event node in the tree

    """

    def __init__(self):
        self.etype         = None   # 'S=speciation D=duplication'
        self.in_seqs       = []
        self.out_seqs      = []
        self.dup_score     = None
        self.sos           = None

        # Not documented
        self.inparalogs    = None
        self.outparalogs   = None
        self.outgroup_spcs = None   # outgroup
        self.e_newick      = None   #
        self.root_age      = None   # estimated time for the outgroup node
        self.orthologs     = None
        self.famSize       = None
        self.seed          = None   # Seed ID used to start the phylogenetic pipeline
        self.branch_supports  = []
