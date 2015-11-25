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
from argparse import RawTextHelpFormatter
from multiprocessing import Pool
from os import system

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
        

def run(args):
    from .. import EvolTree

    # more help
    if args.super_help:
        help_str = ('Description of CodeML parameters, see PAML manual for more '
                    'information\n\n')
        for key in PARAMS_DESCRIPTION:
            help_str += ('  - %-12s: %s\n' % (key, ''.join([
                PARAMS_DESCRIPTION[key][i:i + 70] + '\n' + ' ' * 18
                for i in range(0, len(PARAMS_DESCRIPTION[key]), 70)])))
        system('echo "%s" | less' % help_str)
        exit()

    # in case we only got 1 model :(
    if isinstance(args.models, str):
        args.models = [args.models]

    for nw in args.src_tree_iterator:
        t = EvolTree(nw, format=1)
        t.link_to_alignment(args.alg)
        
        procs = Pool(args.maxcores or None)
        for model in args.models:
            procs.apply_async(t.run_model, args=(model, ))
        t.show()
        




