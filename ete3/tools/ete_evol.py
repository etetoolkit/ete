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
from __future__ import absolute_import
from ..evol.control import PARAMS, AVAIL, PARAMS_DESCRIPTION
from .. import EvolTree
from ..evol import Model
from argparse import RawTextHelpFormatter
from multiprocessing import Pool
import os
from warnings import warn


DESC = "Run evolutionary tests... "

def populate_args(evol_args_p):
    evol_args_p.formatter_class = RawTextHelpFormatter
    evol_args = evol_args_p.add_argument_group('ETE-EVOL OPTIONS')
    evol_args.add_argument("--models", dest="models",
                           choices=AVAIL.keys(),
                           nargs="+", default="fb",
                           help="""choose evolutionary models (Model name) among:
=========== ============================= ==================
Model name  Description                   Model kind
=========== ============================= ==================\n%s
=========== ============================= ==================\n
                           """ % (
                               '\n'.join([' %-8s    %-27s   %-15s' % \
                                          ('%s' % (x), AVAIL[x]['evol'],
                                           AVAIL[x]['typ']) for x in sorted (
                                              sorted (AVAIL.keys()),
                                              key=lambda x: AVAIL[x]['typ'],
                                              reverse=True)])),
                           metavar='[...]')

    evol_args.add_argument("--alg", dest="alg",
                           type=str,
                           help=("Link tree to a multiple sequence alignment (codons)."))

    codeml_mk = evol_args_p.add_argument_group("CODEML TREE CONFIGURATION OPTIONS")

    codeml_mk.add_argument('--mark', dest="mark", nargs='+',
                           help=("mark specific branch of the input tree"))

    codeml_mk.add_argument('--leaves', dest="mark_leaves", action="store_true",
                           help=("Mark successively all the leaves of the input "
                                 "tree and run branch models on each of them."))

    codeml_mk.add_argument('--internals', dest="mark_internals",
                           action="store_true",
                           help=("Mark successively all the internal node of "
                                 "the input tree (but the root) and run branch "
                                 "models on each of them."))

    codeml_gr = evol_args_p.add_argument_group("CODEML MODEL CONFIGURATION OPTIONS")
    for param in PARAMS:
        codeml_gr.add_argument("--" + param, dest=param, metavar="",
                               help=("[%(default)4s] overrides CodeML " +
                                     "%-12s parameter for selected model" % param),
                               default=PARAMS[param])
    codeml_gr.add_argument('--codeml_help', action='store_true', dest='super_help', 
                           help=('show detailed description on model configuration '
                                 'options, and exit.'))

    exec_group = evol_args_p.add_argument_group('EXECUTION MDE OPTIONS')
    exec_group.add_argument("-C", "--cpu", dest="maxcores", type=int,
                            default=1, help="Maximum number of CPU cores"
                            " available in the execution host. If higher"
                            " than 1, tasks with multi-threading"
                            " capabilities will enabled (if 0 all available)"
                            "cores will be used")
        


def clean_tree(tree):
    for n in tree.get_descendants() + [tree]:
        n.mark = ''

def local_run_model(tree, model_name, ctrl_string='', keep=True, **kwargs):
    '''
    '''
    from subprocess import Popen, PIPE
    model_obj = Model(model_name, tree, **kwargs)
    fullpath = os.path.join (tree.workdir, model_obj.name)
    os.system("mkdir -p %s" %fullpath)
    # write tree file
    tree._write_algn(fullpath + '/algn')
    if model_obj.properties['exec'] == 'Slr':
        tree.write(outfile=fullpath+'/tree', format = (11))
    else:
        tree.write(outfile=fullpath+'/tree',
                   format = (10 if model_obj.properties['allow_mark'] else 9))
    # write algn file
    ## MODEL MODEL MDE
    if ctrl_string == '':
        ctrl_string = model_obj.get_ctrl_string(fullpath+'/tmp.ctl')
    else:
        open(fullpath+'/tmp.ctl', 'w').write(ctrl_string)
    hlddir = os.getcwd()
    os.chdir(fullpath)
    binary = os.path.join(tree.execpath, model_obj.properties['exec'])
    try:
        proc = Popen([binary, 'tmp.ctl'], stdout=PIPE)
    except OSError:
        raise Exception(('ERROR: {} not installed, ' +
                         'or wrong path to binary\n').format(binary))
    run, err = proc.communicate()
    if err is not None:
        warn("ERROR: codeml not found!!!\n" +
             "       define your variable EvolTree.execpath")
        return 1
    if b'error' in run or b'Error' in run:
        warn("ERROR: inside codeml!!\n" + run)
        return 1
    os.chdir(hlddir)
    return os.path.join(fullpath,'out'), model_obj

def run_one_model(tree, model_name):
    """
    needed for multiprocessing
    """
    tree.run_model(model_name)

def run(args):

    # more help
    if args.super_help:
        help_str = ('Description of CodeML parameters, see PAML manual for more '
                    'information\n\n')
        for key in PARAMS_DESCRIPTION:
            help_str += ('  - %-12s: %s\n' % (key, ''.join([
                PARAMS_DESCRIPTION[key][i:i + 70] + '\n' + ' ' * 18
                for i in range(0, len(PARAMS_DESCRIPTION[key]), 70)])))
        os.system('echo "%s" | less' % help_str)
        exit()

    # in case we only got 1 model :(
    if isinstance(args.models, str):
        args.models = [args.models]

    for nw in args.src_tree_iterator:
        tree = EvolTree(nw, format=1)
        tree.link_to_alignment(args.alg)

        marks = []
        if args.mark_leaves:
            marks.extend([[n.node_id] for n in tree.iter_leaves()])
        if args.mark_internals:
            marks.extend([n.node_id for s in tree.iter_leaves() if not s.is_leaf()
                          for n in s.iter_descendants()])
            marks.extend([s.node_id for s in tree.iter_leaves() if not s.is_leaf()])

        ########################################################################
        ## TO BE IMPROVED: multiprocessing should be called in a simpler way
        pool = Pool(args.maxcores or None)
        results = []
        for model in args.models:
            for nmark, mark in enumerate(marks):
                if AVAIL[model]['allow_mark'] or not nmark:
                    clean_tree(tree)
                    tree.mark_tree(mark , marks=['#1'])
                    print model, mark
                    results.append(pool.apply_async(local_run_model, args=(tree, model)))
        pool.close()
        pool.join()
        # join back results to tree
        for result in results:
            path, model_obj = result.get()
            setattr(model_obj, 'run', run)
            tree.link_to_evol_model(path, model_obj)
        ########################################################################

        # find cleaver way to test all null models versus alternative models
        # print ('\n\n comparison of models M1 and M2, p-value: ' + str(tree.get_most_likely ('M2','M1')))

        site_models = [m.name for m in tree._models]

        tree.show(histfaces=site_models)





