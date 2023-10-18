from .common import src_tree_iterator

from ete4 import PhyloTree
from ete4.smartview import TreeStyle
from ete4.smartview.gui.server import run_smartview

DESC = "Launches an instance of the ETE smartview tree explorer server."

def populate_args(explore_args_p):
    explore_args_p.add_argument(
        "--face", action="append",
        help=("adds a face to the selected nodes; example: --face "
              "'value:@dist, pos:b-top, color:red, size:10, if:@dist>0.9'"))



def run(args):

    # VISUALIZATION
    # Basic tree style
    ts = TreeStyle()
    ts.show_leaf_name = True
    try:
        tfile = next(src_tree_iterator(args))
    except StopIteration:
        run_smartview()
    else:
        t = PhyloTree(open(tfile), parser=args.src_newick_format)
        t.explore(name=tfile)
        try:
            input('Running ete explorer. Press enter to finish the session.\n')
        except KeyboardInterrupt:
            pass  # it's okay if the user exits with Ctrl+C too
