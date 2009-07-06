__all__ = ["EvolEvent"]

class EvolEvent:
    """ Basic evolutionary event. It stores all the information about an
    event(node) ocurred in a phylogenetic tree. """
    def __init__(self):
        self.etype         = None   # 'S=speciation D=duplication'
        self.seed          = None   # Seed ID used to start the phylogenetic pipeline
        self.outgroup_spcs = None   # outgroup
        self.e_newick      = None   # 
        self.dup_score     = None   # 
        self.root_age      = None   # estimated time for the outgroup node
        self.inparalogs    = None   
        self.outparalogs   = None 
        self.orthologs     = None 
        self.famSize       = None
        self.allseqs       = []     # all ids grouped by this event
        self.in_seqs       = []
        self.out_seqs      = []
	self.branch_supports  = []

