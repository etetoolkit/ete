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

import os
from ...utils import print_table
from .configobj import ConfigObj
from .errors import ConfigError
from .utils import colorify
from .apps import APP2CLASS, OPTION2APPTYPE, APPTYPES

import six
from six.moves import map

def build_supermatrix_workflow(wname):
    try:
        cog_selector, alg_concatenator, treebuilder = map(lambda x: "@%s" %x, wname.split("-"))
    except ValueError:
        raise ConfigError("Invalid supermatrix workflow: %s" %wname)
    
    workflow = {wname: {
        "_app": "supermatrix",
        "_cog_selector": cog_selector,
        "_alg_concatenator": alg_concatenator, 
        "_aa_tree_builder": treebuilder,
        "_nt_tree_builder": treebuilder, 
        "_appset":"@builtin_apps"}
    }
    return workflow

def build_genetree_workflow(wname):
    try:
        aligner, trimmer, modeltester, treebuilder = map(lambda x: "none" if x.lower() == "none" else "@%s"%x,
                                                         wname.split("-"))
    except ValueError:
        raise ConfigError("Invalid genetree workflow: %s" %wname)
    
    workflow = {wname: {
        "_app": "genetree",
        "_aa_aligner": aligner,
        "_aa_alg_cleaner": trimmer, 
        "_aa_model_tester": modeltester,
        "_aa_tree_builder": treebuilder,
        "_nt_aligner": aligner,
        "_nt_alg_cleaner": trimmer,
        "_nt_model_tester": modeltester,
        "_nt_tree_builder": treebuilder, 
        "_appset":"@builtin_apps"}
    }
    return workflow

def list_workflows(config, target_type=None):

    if not target_type or target_type == 'supermatrix':
        print()
        avail_meta = [(k, config["workflow_desc"].get(k, ""), len(v)) for k,v in six.iteritems(config.get('supermatrix_meta_workflow', {}))]
        print_table(avail_meta, fix_col_width=[45, 60, 10], header=["Worflow name", "Description", "threads"], title="Supermatrix shortcut workflow names", row_line=True)
        
    if not target_type or target_type == 'genetree':        
        print()
        avail_meta = [(k, config["workflow_desc"].get(k, ""), len(v)) for k,v in six.iteritems(config.get('genetree_meta_workflow', {}))]
        print_table(avail_meta, fix_col_width=[45, 60, 10], header=["Worflow name", "Description", "threads"], title="GeneTree shortcut workflow names", row_line=True)


def list_apps(config, target_apps = None):
    for appname, validapps in APPTYPES.items():
        if target_apps:
            if appname not in target_apps and target_apps & validapps:
                validapps = target_apps & validapps
            elif appname in target_apps:
                pass
            else:
                continue
                        
        avail_blocks = [[blockname, block["_app"], block.get("_desc", "")] for blockname, block in config.items() if block.get("_app") in validapps]
        print_table(avail_blocks, header=["name", "app type", "desc."], max_col_width=70, title=appname, row_line=True)
        print()

def block_detail(block_name, config, color=True):
    blocks_to_show = {}
    iterable_types = set([set, list, tuple, frozenset])
    if block_name not in config:
        try:
            next_block = [x.lstrip('@') for x in config.get('genetree_meta_workflow', {})[block_name]]
            metaworkflow = True
        except Exception as e:
            print(e)
            raise ValueError('block name not found [%s]' %block_name)
    else:
        metaworkflow = False
        next_block = [block_name]

    pos = 0
    while next_block:
        block = next_block.pop()
        blocks_to_show[block] = pos
        for k1, v1 in six.iteritems(config[block]):
            if type(v1) in iterable_types:
                for v2 in v1:
                    if isinstance(v2, str) and v2.startswith('@'):
                        next_block.append(v2[1:])
            elif isinstance(v1, str) and v1.startswith('@'):
                next_block.append(v1[1:])
        pos += 1

    if metaworkflow and color:
        print(colorify('[genetree_meta_workflow]', 'yellow'))
        print("%s = %s" %(block_name, ', '.join(config["genetree_meta_workflow"][block_name])))
        print()
    elif metaworkflow:
        print('[genetree_meta_workflow]')
        print("%s = %s" %(block_name, ', '.join(config["genetree_meta_workflow"][block_name])))
        print()

    for b, pos in sorted(list(blocks_to_show.items()), key=lambda x: x[1]):
        if b == "builtin_apps":
            continue
        if color:
            print(colorify('[%s]' %b, 'green'))
        else:
            print('[%s]' %b)

        for k,v in sorted(config[b].items()):
            if k == "_inherits":
                continue
            if type(v) in iterable_types:
                v = ', '.join(map(str, v))+','

            if color:
                if k == '_app':
                    print(colorify('% 35s = %s' %(k, v), "lblue"))
                else:
                    print('%s = %s' %(colorify("% 35s" %k, "orange"), v))
            else:
                print('% 40s = %s' %(k, v))
        print()

def parse_block(blockname, conf):
    blocktype = conf[blockname].get('_app', 'unknown')
    for attr, v in list(conf[blockname].items()):
        conf[blockname][attr] = check_type(blocktype, attr, v)
        if isinstance(conf[blockname][attr], list):
            for i in conf[blockname][attr]:
                check_block_link(conf, blockname, i, attr)
        else:
            check_block_link(conf, blockname, conf[blockname][attr], attr)
            
    # Check for missing attributes     
    for tag, tester in six.iteritems(CHECKERS):
        if tag[0] == blocktype and (tester[2] and tag[1] not in conf[blockname]):
            raise ConfigError('[%s] attribute expected in block [%s]' %(tag[1], blockname))
            
def check_config(fname):
    conf = ConfigObj(fname, list_values=True)

    # expand meta_workflows
    for meta_name, meta_wf in conf["genetree_meta_workflow"].items():
        for wkname in meta_wf:        
            conf.update(build_genetree_workflow(wkname.lstrip("@")))
    for meta_name, meta_wf in conf["supermatrix_meta_workflow"].items():
        for wkname in meta_wf:        
            conf.update(build_supermatrix_workflow(wkname.lstrip("@")))
            
    # expand inherits options 
    for k, v in list(conf.items()):
        if '_inherits' in v:
            base = v['_inherits']
            try:
                new_dict = dict(conf[base])
            except KeyError:
                raise ConfigError('[%s] config block is referred in [%s] but not present in config file' %(base, k))
            new_dict.update(v)
            conf[k] = new_dict

    # check blocks
    for blockname in list(conf.keys()):
        parse_block(blockname, conf)

    # Check that the number of columns in main workflow definition is the same in all attributes
    for flow_name in six.iterkeys(conf):
        if conf[flow_name].get("_app", "") != "main":
            continue
        npr_config = [len(v) for k, v in six.iteritems(conf[flow_name])
                      if type(v) == list and k != "target_levels"]
        if len(set(npr_config)) != 1:
            raise ConfigError("List values in [%s] should all have the same length" %flow_name)
    return conf

def check_type(blocktype, attr, v):
    tag = (blocktype, attr)
    if tag in CHECKERS:
        tester, kargs, required = CHECKERS[tag]
        return tester(v, **kargs)
    else:
        return v

def check_block_link(conf, parent, v, attr_name):
    if isinstance(v, str) and v.startswith('@'):
        if v[1:] not in conf:
            raise ConfigError('[%s] config block referred in [%s] but not found in config' %(v, parent))
        if attr_name in OPTION2APPTYPE and conf[v[1:]]["_app"] not in OPTION2APPTYPE[attr_name]:
            raise ConfigError('[%s] is not valid [%s] application block' %(v, attr_name))

def is_file(value):
    if os.path.isfile(value):
        return value
    else:
        raise ConfigError("Not valid file")

def is_dir(value):
    if os.path.isdir(value):
        return value
    else:
        raise ConfigError("Not valid file")

def check_number(value, cast, minv=0, maxv=None):
    try:
        typed_value = cast(value)
    except ValueError:
        raise ConfigError("Expected [%s] number. Found [%s]" %(cast, value))
    else:
        if (minv is not None and typed_value < cast(minv)) or \
           (maxv is not None and typed_value > cast(maxv)):
            _minv = minv if minv is not None else "any"
            _maxv = maxv if maxv is not None else "any"
            raise ConfigError("[%s] not in the range (%s,%s)" %
                              (value, _minv, _maxv))
    return typed_value

def is_set(value):
    if not isinstance(value, list):
        raise ConfigError("Expected a list of values. Found [%s]" %value)
    return set(value)

def is_appset_entry(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ConfigError("unexpected application format [%s]. Expected [appname, maxcpus] format" %value)
    try:
        cores = int(value[2])
    except ValueError:
        raise ConfigError("unexpected application format [%s]. Expected [appname, maxcpus] format (maxcpus as integer)" %value)

    return [value[0], cores]

def is_float_list(value, minv=0, maxv=None):
    is_list(value)
    typed_value = []
    for v in value:
        typed_value.append(check_number(v, float, minv, maxv))
    return typed_value

def is_integer_list(value, minv=0, maxv=None):
    is_list(value)
    typed_value = []
    for v in value:
        typed_value.append(check_number(v, int, minv, maxv))
    return typed_value

def is_float(value, minv=None, maxv=None):
    return check_number(value, float, minv, maxv)

def is_integer(value, minv=None, maxv=None):
    return check_number(value, int, minv, maxv)


def is_list(value):
    if not isinstance(value, list):
        raise ConfigError("[%s] is not a list" %value)
    return value

def is_app_link(value, allow_none=True):
    if allow_none and value == 'none':
        return value
    elif value.startswith('@'):
        return value
    else:
        raise ConfigError('[%s] is not a valid block link' %value)

def is_app_list(value, allow_none=True):
    is_list(value)
    for v in value:
        is_app_link(v, allow_none=allow_none)
    return value


def is_boolean(value):
    if str(value).lower() in set(["1", "true", "yes"]):
        return True
    elif str(value).lower() in set(["0", "false", "no"]):
        return False
    else:
        raise ConfigError('[%s] is not a boolean value' %(value))

def is_integer_list(value, maxv=None, minv=None):
    is_list(value)
    return [is_integer(v, maxv=maxv, minv=minv) for v in value]

def is_correlative_integer_list(value, minv=None, maxv=None):
    is_list(value)
    typed_value = []
    last_value = 0
    for v in value:
        cv = is_integer(v, minv=None, maxv=None)
        typed_value.append(cv)
        if cv <= last_value:
            raise ConfigError("[%s] Numeric values are not correlative" %value)
        last_value = cv
    return typed_value

def is_text(value):
    if isinstance(value, str):
        return value
    else:
        raise ConfigError("[%s] is not a valid text string" %value)

def is_percent(value):
    try:
        is_float(value.rstrip('%'))
    except ConfigError:
        raise ConfigError('[%s] should a percentage value (i.e. 0.4%%)' %value)
    return value

def is_integer_or_percent(value):
    try:
        return is_integer(value)
    except ConfigError:
        try:
            is_percent(value)
        except ConfigError:
            raise ConfigError('[%s] should be an integer or a percentage (i.e. 15 or 0.4%%)' %value)
    return value

def is_choice(value, choices):
    if value in choices:
        return value
    else:
        raise ConfigError('[%s] should be one of %s' %(value, choices))

def is_raxml_bootstrap(value):
    try:
        return is_integer(value)
    except ValueError:
        if value == 'alrt' or value == 'alrt_phyml':
            return value
        else:
            raise ConfigError('[%s] bootstrap value should an integer, "alrt" or "phyml_alrt"' %(value))



CHECKERS = {
    # (app_name, attr_name): (checker_fn, args, required_attr)
    ("main", "_npr"): (is_app_list, {}, True),
    ("main", "_workflow"): (is_app_list, {"allow_none":False}, True),
    ("main", "_appset"): (is_app_link, {"allow_none":False}, True),

    ("npr", "_max_iters"): (is_integer, {"minv":1}, True),
    ("npr", "_switch_aa_similarity"): (is_float, {"minv":0, "maxv":1}, True),
    ("npr", "_max_seq_similarity"): (is_float, {"minv":0, "maxv":1}, True),
    ("npr", "_min_branch_support"): (is_float, {"minv":0, "maxv":1}, True),
    ("npr", "_min_npr_size"): (is_integer, {"minv":3}, True),
    ("npr", "_tree_splitter"): (is_app_link, {}, True),
    ("npr", "_target_levels"): (is_list, {}, False),

    ("genetree", "_aa_aligner"): (is_app_link, {}, True),
    ("genetree", "_nt_aligner"): (is_app_link, {}, True),
    ("genetree", "_aa_alg_cleaner"): (is_app_link, {}, True),
    ("genetree", "_nt_alg_cleaner"): (is_app_link, {}, True),
    ("genetree", "_aa_model_tester"): (is_app_link, {}, True),
    ("genetree", "_nt_model_tester"): (is_app_link, {}, True),
    ("genetree", "_aa_tree_builder"): (is_app_link, {}, True),
    ("genetree", "_nt_tree_builder"): (is_app_link, {}, True),
    ("genetree", "_appset"): (is_app_link, {"allow_none":False}, True),

    ("supermatrix", "_cog_selector"): (is_app_link, {}, True),
    ("supermatrix", "_alg_concatenator"): (is_app_link, {}, True),
    ("supermatrix", "_aa_tree_builder"): (is_app_link, {}, True),
    ("supermatrix", "_nt_tree_builder"): (is_app_link, {}, True),
    ("genetree", "_appset"): (is_app_link, {"allow_none":False}, True),

    ("concatalg", "_default_aa_model"): (is_text, {}, True),
    ("concatalg", "_default_nt_model"): (is_text, {}, True),

    #("concatalg", "_workflow"): (is_app_link, {"allow_none":False}, True),

    ("cogselector", "_species_missing_factor"): (is_float, {"minv":0, "maxv":1}, True),
    ("cogselector", "_max_cogs"): (is_integer, {"minv":1}, True),

    ("treesplitter", "_max_outgroup_size"): (is_integer_or_percent, {}, True),
    ("treesplitter", "_min_outgroup_support"): (is_float, {"minv":0, "maxv":1}, True),
    ("treesplitter", "_outgroup_topology_dist"): (is_boolean, {}, True),
    ("treesplitter", "_first_split"): (is_text, {}, True),

    ("metaaligner", "_aligners"): (is_app_list, {}, True),
    ("metaaligner", "_alg_trimming"): (is_boolean, {}, True),

    ("prottest", "_lk_mode"): (is_choice, {"choices":set(['phyml', 'raxml'])}, True),
    ("prottest", "_models"): (is_list, {}, True),


    ("pmodeltest", "_aa_models"): (is_text, {}, True),
    ("pmodeltest", "_nt_models"): (is_text, {}, True),
        
    ("raxml", "_aa_model"): (is_text, {}, True),
    ("raxml", "_method"): (is_choice, {"choices":set(['GAMMA', 'CAT'])}, True),
    ("raxml", "_bootstrap"): (is_raxml_bootstrap, {}, True),
    ("raxml", "_model_suffix"): (is_text, {}, True),

    ("raxml-sse", "_aa_model"): (is_text, {}, True),
    ("raxml-sse", "_method"): (is_choice, {"choices":set(['GAMMA', 'CAT'])}, True),
    ("raxml-sse", "_alrt_calculation"): (is_choice, {"choices":set(['phyml', 'raxml'])}, True),

    ("raxml-avx", "_aa_model"): (is_text, {}, True),
    ("raxml-avx", "_method"): (is_choice, {"choices":set(['GAMMA', 'CAT'])}, True),
    ("raxml-avx", "_alrt_calculation"): (is_choice, {"choices":set(['phyml', 'raxml'])}, True),

    ("appset", "muscle"): (is_appset_entry, {}, True),
    ("appset", "mafft"): (is_appset_entry, {}, True),
    ("appset", "clustalo"): (is_appset_entry, {}, True),
    ("appset", "trimal"): (is_appset_entry, {}, True),
    ("appset", "readal"): (is_appset_entry, {}, True),
    ("appset", "tcoffee"): (is_appset_entry, {}, True),
    ("appset", "phyml"): (is_appset_entry, {}, True),
    ("appset", "raxml-pthreads"): (is_appset_entry, {}, True),
    ("appset", "raxml"): (is_appset_entry, {}, True),
    # ("appset", "raxml-pthreads-sse3"): (is_appset_entry, {}, True),
    # ("appset", "raxml-sse3"): (is_appset_entry, {}, True),
    # ("appset", "raxml-pthreads-avx"): (is_appset_entry, {}, True),
    # ("appset", "raxml-avx"): (is_appset_entry, {}, True),
    # ("appset", "raxml-pthreads-avx2"): (is_appset_entry, {}, True),
    # ("appset", "raxml-avx2"): (is_appset_entry, {}, True),
    ("appset", "dialigntx"): (is_appset_entry, {}, True),
    ("appset", "fasttree"): (is_appset_entry, {}, True),
    ("appset", "statal"): (is_appset_entry, {}, True),



    }
