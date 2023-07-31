from .common import src_tree_iterator

DESC = ""



def populate_args(extract_args_p):
    extract_args = extract_args_p.add_argument_group('TREE EDIT OPTIONS')

    extract_args.add_argument("--orthologs", dest="orthologs",
                              nargs="*",
                              help="")

    extract_args.add_argument("--duplications", dest="duplications",
                              action="store_true",
                              help="")

def run(args):
    from .. import Tree, PhyloTree
    for ftree in src_tree_iterator(args):
        if args.orthologs is not None:
            t = PhyloTree(open(ftree))
            for e in t.get_descendant_evol_events():
                print(e.in_seqs, e.out_seqs)
