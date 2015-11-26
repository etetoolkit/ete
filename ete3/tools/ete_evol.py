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

    evol_args.add_argument("--model_folder", dest="model_folder",
                           type=str, nargs='+', 
                           help=("Link tree to a CodeML models previously run "
                                 "in the input directory"))

    codeml_mk = evol_args_p.add_argument_group("CODEML TREE CONFIGURATION OPTIONS")

    codeml_mk.add_argument('--mark', dest="mark", nargs='+',
                           help=(
                               "mark branches of the input tree. PAML node IDs "
                               "or names can be used. \n - Names separated by "
                               "single coma will be marked individualy. \n - "
                               "Names separated by double comas will mark the "
                               "tree at the common ancestor. \n - Names "
                               "separated by "
                               "triple comas will mark the tree from the common"
                               "ancestor.\nSpaces will be used between these "
                               "elements for new marks. \n"
                               "Example: '--mark "
                               "Homo,,,Chimp Orang,Gorilla Mouse,,Rat' \n"
                               "Will result in marking with #1 Homo, Chimp and "
                               "their common ancestor; \nwith #2 Orang and "
                               "Gorilla nothing else; \nand with #3 the common "
                               "ancestor of Mouse and Rat, but not the leaves."
                               ))

    codeml_mk.add_argument('--interactive', dest="mark_gui", action="store_true",
                           help=("open the input tree in GUI to allow to "
                                 "interactive marking of branches for CodeML."))

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

def marking_layout(node):
    '''
    layout for interactively marking CodemlTree
    '''
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
    color_cycle = [u'#E24A33', u'#348ABD', u'#988ED5',
                   u'#777777', u'#FBC15E', u'#8EBA42',
                   u'#FFB5B8']
    node.img_style["size"] = 15
    if hasattr(node, 'mark') and node.mark != '':
        node.img_style["fgcolor"] = color_cycle[(int(node.mark.replace('#', '')) - 1) % 7]
    else:
        node.img_style["fgcolor"] = '#000000'

def clean_tree(tree):
    """
    remove marks from tree
    """
    for n in tree.get_descendants() + [tree]:
        n.mark = ''

def local_run_model(tree, model_name, ctrl_string='', **kwargs):
    '''
    local verison of model runner. Needed for multiprocessing pickling...
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


def get_node(tree, node):
    res = tree.search_nodes(name=node)
    if len(res) > 1:
        exit('ERROR: more than 1 node with name: %s' % node)
    elif len(res) < 1:
        res = tree.search_nodes(node_id=int(node))
        if len(res) < 1:
            exit('ERROR: node %s not found' % node)
    return res[0]

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
        marks = []
        marked = False
        if args.mark_gui:
            if args.mark_leaves or args.mark_internals or args.mark:
                exit('ERROR: incompatible marking options')
            tree.show(layout=marking_layout)
        if args.mark:
            marked = True
            if args.mark_leaves or args.mark_internals:
                exit('ERROR: incompatible marking options')
            for mark, group in enumerate(args.mark, 1):
                group = group.replace(',,,', '@;;;@')
                group = group.replace(',,', '@;;@')
                group = group.replace(',', '@;@')
                for subgroup in group.split('@;@'):
                    if '@;;' in subgroup:
                        node1, node2 = subgroup.split('@;;;@' if '@;;;@' in
                                                      subgroup else '@;;@')
                        node1 = get_node(tree, node1)
                        node2 = get_node(tree, node2)
                        anc = tree.get_common_ancestor(node1, node2)
                        # mark from ancestor
                        if '@;;;@' in subgroup:
                            for node in anc.get_descendants() + [anc]:
                                node.mark = ' #' + str(mark)
                        # mark at ancestor
                        elif '@;;@' in subgroup:
                            anc.mark = ' #' + str(mark)
                    # mark in single node
                    else:
                        node = get_node(tree, subgroup)
                        node.mark = ' #' + str(mark)
            
        tree.link_to_alignment(args.alg)

        if args.mark_leaves:
            if args.mark:
                exit('ERROR: incompatible marking options')
            marks.extend([[n.node_id] for n in tree.iter_leaves()])
        if args.mark_internals:
            if args.mark:
                exit('ERROR: incompatible marking options')
            marks.extend([n.node_id for s in tree.iter_leaves() if not s.is_leaf()
                          for n in s.iter_descendants()])
            marks.extend([s.node_id for s in tree.iter_leaves() if not s.is_leaf()])

        print('\nMARKED TREE: ' + tree.write())
        ########################################################################
        ## TO BE IMPROVED: multiprocessing should be called in a simpler way
        print("\nRUNNING CODEML")
        pool = Pool(args.maxcores or None)
        results = []
        for model in args.models:
            print('  - processing model %s' % model)
            if AVAIL[model.split('.')[0]]['allow_mark']:
                if marked:
                    results.append(pool.apply_async(local_run_model,
                                                    args=(tree, model)))
                for mark in marks:
                    print('       marking branches %s' %
                          ', '.join([str(m) for m in mark]))
                    clean_tree(tree)
                    tree.mark_tree(mark , marks=['#1'] * len(mark))
                    model = model + '.' +'_'.join([str(m) for m in mark])
                    results.append(pool.apply_async(local_run_model,
                                                    args=(tree, model)))
            else:
                results.append(pool.apply_async(local_run_model,
                                                args=(tree, model)))

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

        
        tests = "\nLRT\n\n"
        tests += ('%20s |%20s | %s\n' % ('Null model', 'Alternative model',
                                       'p-value'))
        tests += ('-' * 55)
        tests += ('\n')
        at_least_one_come_on = False
        results = {}
        for null in tree._models:
            for altn in tree._models:
                if tree._models[null].np >= tree._models[altn].np:
                    continue
                if ((AVAIL[null.split('.')[0]]['typ']=='site' and
                     AVAIL[altn.split('.')[0]]['typ']=='branch') or
                    (AVAIL[altn.split('.')[0]]['typ']=='site' and
                     AVAIL[null.split('.')[0]]['typ']=='branch')):
                    continue
                results[(null, altn)] = tree.get_most_likely(altn, null)
                tests += ('%20s |%20s | %f%s\n' % (
                    null, altn, results[(null, altn)],
                    '**' if results[(null, altn)] < 0.01 else '*'
                    if results[(null, altn)] < 0.05 else ''))
                at_least_one_come_on = True

        if at_least_one_come_on:
            print(tests)
            
        # apply evol model (best branch model?) to tree for display
        # TODO: best needs to be guessed from LRT
        best = max([m for m in tree._models
                    if AVAIL[m.split('.')[0]]['typ']=='branch'],
                   key=lambda x: tree._models[x].lnL)
        print (best)
        tree.change_dist_to_evol('bL', tree._models[best], fill=True)

        # get all site models for display
        site_models = [m for m in tree._models
                       if AVAIL[m.split('.')[0]]['typ']=='site']

        tree.show(histfaces=site_models)


