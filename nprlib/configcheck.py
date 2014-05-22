import os
from nprlib.configobj import ConfigObj
from nprlib.errors import ConfigError

def check_config(fname):
    conf = ConfigObj(fname, list_values=True)
    for k, v in conf.items():
        if '_inherits' in v:
            base = v['_inherits']
            try:
                new_dict = dict(conf[base])
            except KeyError:
                raise ConfigError('[%s] config block is referred in [%s] but not present in config file' %(base, k))
            new_dict.update(v)
            conf[k] = new_dict
            
    for k in conf.iterkeys():
        blocktype = conf[k].get('_app', 'unknown')
        for attr, v in conf[k].items():
            conf[k][attr] = check_type(blocktype, attr, v)
            if isinstance(conf[k][attr], list):
                for i in conf[k][attr]:
                    check_block_link(conf, k, i)
            else:
                check_block_link(conf, k, conf[k][attr])
        for tag, tester in CHECKERS.iteritems():
            if tag[0] == blocktype and (tester[2] and tag[1] not in conf[k]):
                raise ConfigError('[%s] attribute expected in block [%s]' %(tag[1], k))

    # Check that the number of columns in main workflow definition is the same in all attributes
    for flow_name in conf.iterkeys():
        if conf[flow_name].get("_app", "") != "main":
            continue
        npr_config = [len(v) for k, v in conf[flow_name].iteritems()
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

def check_block_link(conf, parent, v):
    if isinstance(v, str) and v.startswith('@') and v[1:] not in conf:
        raise ConfigError('[%s] config block referred in [%s] but not found in config' %(v, parent))


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

CHECKERS = {
    # (app_name, attr_name): (checker_fn, args, required_attr)
    ("main", "_npr"): (is_app_list, {}, True),
    ("main", "_max_seqs"): (is_correlative_integer_list, {"minv":1}, True),
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

    ("supermatrix", "_cog_selector"): (is_app_link, {}, True),
    ("supermatrix", "_alg_concatenator"): (is_app_link, {}, True),
    ("supermatrix", "_aa_tree_builder"): (is_app_link, {}, True),
    ("supermatrix", "_nt_tree_builder"): (is_app_link, {}, True),


    ("concatalg", "_default_aa_model"): (is_text, {}, True),
    ("concatalg", "_default_nt_model"): (is_text, {}, True),
    ("concatalg", "_workflow"): (is_app_link, {"allow_none":False}, True),
    
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
   
    ("raxml", "_aa_model"): (is_text, {}, True),
    ("raxml", "_method"): (is_choice, {"choices":set(['GAMMA', 'CAT'])}, True),
    ("raxml", "_alrt_calculation"): (is_choice, {"choices":set(['phyml', 'raxml'])}, True),

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
    ("appset", "raxml-pthreads-sse3"): (is_appset_entry, {}, True),
    ("appset", "raxml-sse3"): (is_appset_entry, {}, True),
    ("appset", "raxml-pthreads-avx"): (is_appset_entry, {}, True),
    ("appset", "raxml-avx"): (is_appset_entry, {}, True),
    ("appset", "raxml-pthreads-avx2"): (is_appset_entry, {}, True),
    ("appset", "raxml-avx2"): (is_appset_entry, {}, True),
    ("appset", "dialigntx"): (is_appset_entry, {}, True),
    ("appset", "fasttree"): (is_appset_entry, {}, True),
    ("appset", "statal"): (is_appset_entry, {}, True),


    
    }
