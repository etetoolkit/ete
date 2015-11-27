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
from __future__ import print_function

from ..evol.control import PARAMS, AVAIL, PARAMS_DESCRIPTION
from .. import EvolTree, random_color, add_face_to_node, TextFace, TreeStyle
from ..evol import Model
from argparse import RawTextHelpFormatter
from multiprocessing import Pool
import sys
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

    evol_args.add_argument("--dir", dest="dir",
                           type=str, nargs='+',
                           help=("directory where precalculated models are "
                                 "stored, followed by coma model-name.\n"
                                 "example: --dir /path1/,M2 /path2/,M1\n"
                                 "will load models from path1 under the name "
                                 "'M2', and from path2 into 'M1'"))

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

    codeml_ts = evol_args_p.add_argument_group("CODEML TEST OPTIONS")

    codeml_ts.add_argument('--tests', dest="tests", nargs='+', default='auto',
                           type=str,
                           help=("Defines the set of tests to perform.\n"
                                 " example: --test M1,M2 b_neut,b_free\n"
                                 "Will do a likelihood ratio tests between "
                                 "M1 and M2, and between any b_neut and b_free"
                                 "computed\n(only trees with identical marks "
                                 "will be caompared)."))

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
    exec_group.add_argument("--codeml_binary", dest="codeml_binary",
                            default="~/.etetoolkit/ext_apps-latest/bin/codeml")
                            
    
def marking_layout(node):
    '''
    layout for interactively marking CodemlTree
    '''
    color_cycle = random_color(num=10, h=0.5)
    # [u'#E24A33', u'#348ABD', u'#988ED5',
    #                u'#777777', u'#FBC15E', u'#8EBA42',
    #                u'#FFB5B8']
    node.img_style["size"] = 0
    
    if hasattr(node, "collapsed"):
        if node.collapsed == 1:
            node.img_style["draw_descendants"]= False
            
    if hasattr(node, 'mark') and node.mark != '':
        mark = int(node.mark.replace('#', ''))        
        node_color = color_cycle[(mark - 1)]
        node.img_style["fgcolor"] = node_color
        label_face = TextFace(str(mark).center(3), fsize=12, fgcolor="white", ftype="courier")
        label_face.inner_background.color = node_color              
    else:
        node_color = 'slateGrey'
        label_face = TextFace("   ", fsize=12, fgcolor="white", ftype="courier")
        label_face.inner_background.color = node_color
        
    label_face.inner_border.width = 1
    label_face.margin_top = 2
    label_face.margin_bottom = 2
    
    add_face_to_node(label_face, node, column=0, position="branch-right")
    
    if node.is_leaf():
        add_face_to_node(TextFace(" %s" %node.name, ftype="courier", fgcolor="#666666"), node, column=10, position="branch-right")
    else:
        add_face_to_node(TextFace(" %s" %node.name, fsize=8, ftype="courier", fgcolor="#666666"), node, column=0, position="branch-top")        
    
def clean_tree(tree):
    """
    remove marks from tree
    """
    for n in tree.get_descendants() + [tree]:
        n.mark = ''

def local_run_model(tree, model_name, codeml_binary, ctrl_string='', **kwargs):
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
        
    proc = Popen([codeml_binary, 'tmp.ctl'], stdout=PIPE)

    run, err = proc.communicate()
    if err is not None or b'error' in run or b'Error' in run:
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

    codeml_binary = os.path.expanduser(args.codeml_binary)
    if not os.path.exists(codeml_binary):        
        print("ERROR: Codeml binary does not exist at %s"%args.codeml_binary, file=sys.stderr)
        print("       provide another route with --codeml_binary, or install it by executing 'ete3 install-external-tools paml'", file=sys.stderr)
        exit(-1)

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
        nodes = []
        if args.mark_gui:
            if args.mark_leaves or args.mark_internals or args.mark:
                exit('ERROR: incompatible marking options')
            ts = TreeStyle()
            ts.layout_fn = marking_layout
            ts.show_leaf_name = False
            tree.show(tree_style=ts)
        if args.mark:
            if args.mark_leaves or args.mark_internals:
                exit('ERROR: incompatible marking options')
            for group in args.mark:
                marks.append([])
                nodes.append([])
                group = group.replace(',,,', '@;;;@')
                group = group.replace(',,', '@;;@')
                group = group.replace(',', '@;@')
                for mark, subgroup in enumerate(group.split('@;@'), 1):
                    if '@;;' in subgroup:
                        node1, node2 = subgroup.split('@;;;@' if '@;;;@' in
                                                      subgroup else '@;;@')
                        node1 = get_node(tree, node1)
                        node2 = get_node(tree, node2)
                        anc = tree.get_common_ancestor(node1, node2)
                        # mark from ancestor
                        if '@;;;@' in subgroup:
                            for node in anc.get_descendants() + [anc]:
                                marks[-1].append('#' + str(mark))
                                nodes[-1].append(node.node_id)
                        # mark at ancestor
                        elif '@;;@' in subgroup:
                            marks[-1].append('#' + str(mark))
                            nodes[-1].append(anc.node_id)
                    # mark in single node
                    else:
                        node = get_node(tree, subgroup)
                        marks[-1].append('#' + str(mark))
                        nodes[-1].append(node.node_id)
            
        tree.link_to_alignment(args.alg)

        if args.mark_leaves:
            if args.mark:
                exit('ERROR: incompatible marking options')
            marks.extend([['#1'] for n in tree.iter_leaves()])
            nodes.extend([[n.node_id] for n in tree.iter_leaves()])
        if args.mark_internals:
            if args.mark:
                exit('ERROR: incompatible marking options')
            marks.extend(['#1' for s in tree.iter_leaves() if not s.is_leaf()
                          for n in s.iter_descendants()])
            nodes.extend([n.node_id for s in tree.iter_leaves() if not s.is_leaf()
                          for n in s.iter_descendants()])
            marks.extend(['#1' for s in tree.iter_leaves() if not s.is_leaf()])
            nodes.extend([s.node_id for s in tree.iter_leaves() if not s.is_leaf()])

        ########################################################################
        ## TO BE IMPROVED: multiprocessing should be called in a simpler way

        print("\nRUNNING CODEML")
        pool = Pool(args.maxcores or None)
        results = []
        for model in args.models:
            print('  - processing model %s' % model)
            if AVAIL[model.split('.')[0]]['allow_mark']:
                for mark, node in zip(marks, nodes):
                    print('       marking branches %s\n' %
                          ', '.join([str(m) for m in node]))
                    clean_tree(tree)
                    tree.mark_tree(node , marks=mark)
                    modmodel = model + '.' + '_'.join([str(n) for n in node])
                    print('          %s\n' % (
                        tree.write()))
                    results.append(pool.apply_async(
                        local_run_model,
                        args=(tree, modmodel, codeml_binary)))
            else:
                results.append(pool.apply_async(
                    local_run_model, args=(tree, model, codeml_binary)))

        pool.close()
        pool.join()
        # join back results to tree
        for result in results:
            path, model_obj = result.get()
            setattr(model_obj, 'run', run)
            try:
                tree.link_to_evol_model(path, model_obj)
            except KeyError:
                warn('ERROR: model %s failed' % (model_obj.name))
                
        ########################################################################

        # find cleaver way to test all null models versus alternative models
        # print ('\n\n comparison of models M1 and M2, p-value: ' + str(tree.get_most_likely ('M2','M1')))

        
        tests = "\nLRT\n\n"
        tests += ('%25s |%25s | %s\n' % ('Null model', 'Alternative model',
                                         'p-value'))
        tests += (' ' * 5 + ('-' * 60))
        tests += ('\n')
        at_least_one_come_on = False
        results = {}
        if args.tests != 'auto':
            wanted = [t.split(',') for t in args.tests]
        else:
            wanted = []
        bests = []
        for null in tree._models:
            for altn in tree._models:
                if tree._models[null].np >= tree._models[altn].np:
                    continue
                # we usually want to compare models of the same kind
                if (((AVAIL[null.split('.')[0]]['typ']=='site' and
                      AVAIL[altn.split('.')[0]]['typ']=='branch') or
                     (AVAIL[altn.split('.')[0]]['typ']=='site' and
                      AVAIL[null.split('.')[0]]['typ']=='branch'))
                    and args.tests == 'auto'):
                    continue
                # we usually want to compare models marked in the same way
                if (('.' in altn and '.' in null) and
                    (altn.split('.')[1] != null.split('.')[1])):
                    continue
                if args.tests != 'auto':
                    if not any([(null.split('.')[0] in test and
                                 altn.split('.')[0] in test)
                                for test in wanted]):
                        continue
                results[(null, altn)] = tree.get_most_likely(altn, null)
                bests.append(null if results[(null, altn)] > 0.05 else altn)
                
                tests += ('%25s |%25s | %f%s\n' % (
                    null, altn, results[(null, altn)],
                    '**' if results[(null, altn)] < 0.01 else '*'
                    if results[(null, altn)] < 0.05 else ''))
                at_least_one_come_on = True

        if at_least_one_come_on:
            print(tests)

        print(bests)
            
        # apply evol model (best branch model?) to tree for display
        # TODO: best needs to be guessed from LRT
        best = max([m for m in tree._models
                    if AVAIL[m.split('.')[0]]['typ']=='branch'],
                   key=lambda x: tree._models[x].lnL)
        print(best)
        tree.change_dist_to_evol('bL', tree._models[best], fill=True)

        # get all site models for display
        site_models = [m for m in tree._models
                       if AVAIL[m.split('.')[0]]['typ']=='site']

        tree.show(histfaces=site_models)

