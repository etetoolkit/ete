import os

from .common import src_tree_iterator

from ete4 import PhyloTree
from ete4.smartview.explorer import explore

DESC = "Launches the ETE smartview tree explorer."


def populate_args(explore_args_p):
    explore_args_p.add_argument(
        "--face", action="append",
        help=("adds a face to the selected nodes; example: --face "
              "'value:@dist, pos:b-top, color:red, size:10, if:@dist>0.9'"))


def run(args):
    try:
        tfile = next(src_tree_iterator(args))
        t = PhyloTree(open(tfile), parser=args.src_newick_format)
        t.explore(name=os.path.basename(tfile))
        input('Running ete explorer. Press enter to finish the session.\n')
    except StopIteration:
        explore()  # if there is no input file, we still open the explorer
    except (KeyboardInterrupt, EOFError):
        pass  # it's okay if the user exits with Ctrl+C too
