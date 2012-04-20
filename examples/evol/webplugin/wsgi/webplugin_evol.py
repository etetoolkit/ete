import sys
import re
import os

#sys.path.insert(0, "/home/services/software/ete2-webplugin/")
sys.path.insert(0, "/var/www/webplugin/wsgi")

from ete_dev import WebTreeApplication # Required to use the webplugin

from ete_dev.evol import evol_clean_layout, evol_layout
from ete_dev.evol import EvolTree
#from ete_dev import PhyloTree as EvolTree
from ete_dev.evol.model import Model
from ete_dev.evol.control import AVAIL
from ete_dev import faces # Required by my custom
                                     # application
from ete_dev import TreeImageProperties

from struct import pack
from random import randint, choice

# ==============================================================================
# TREE LOADER
#
# This is my tree loading functions. I want the WebTreeApplication to
# is this method to load the trees
# ==============================================================================

# Custom Tree loader
def extract_species_code(name):
    return str(name).split("_")[-1].strip()

def my_tree_loader(tree):
    """ This is function is used to load trees within the
    WebTreeApplication object. """
    t = EvolTree(tree, sp_naming_function=extract_species_code)
    application.set_img_properties (None)
    return t

# ==============================================================================
# CUSTOM LAYOUTS
#
# This are my layout functions. I want the WebTreeApplication to use
# them for rendering trees
# ==============================================================================

LEAVE_FACES = [] # Global var that stores the faces that are rendered
                 # by the layout function

def codeml_cartoon_layout(node):
    evol_layout(node)

def codeml_clean_layout(node):
    '''
    layout for CodemlTree
    '''
    for f, fkey, pos in LEAVE_FACES:
        if hasattr(node, fkey):
            if not (fkey == 'name' and node.name =='NoName'):
                if node.is_leaf():
                    faces.add_face_to_node(f, node, column=pos, position="branch-right")
                elif fkey == 'species':
                    if node.species != "Unknown":
                        faces.add_face_to_node (faces.TextFace(' (%s)'%(node.species),
                                                               fsize=6, fgcolor="#787878"),
                                                node, -1, position="branch-bottom")
                else:
                    faces.add_face_to_node(f, node, column=pos, position="branch-bottom")
    if hasattr (node, 'dN'):
        faces.add_face_to_node (faces.TextFace('%.4f'%(node.w), fsize=6,
                                               fgcolor="#7D2D2D"),
                                node, 0, position="branch-top")
        faces.add_face_to_node (faces.TextFace('%.2f/%.2f'% (100*node.dN,
                                                             100*node.dS),
                                              fsize=6, fgcolor="#787878"),
                                node, 0, position="branch-bottom")
    if not node.is_leaf():
        node.img_style["shape"] = "sphere"
        node.img_style["size"] = 5
        # Add special faces on collapsed nodes
        if hasattr(node, "hide") and int(node.hide) == 1:
            node.img_style["draw_descendants"]= False
            collapsed_face = faces.TextFace(\
                " %s collapsed leaves." %len(node), \
                    fsize=10, fgcolor="#444", ftype="Arial")
            faces.add_face_to_node(collapsed_face, node, 0)
        else:
            node.img_style["draw_descendants"]= True
    else:
        node.img_style["size"] = 2
        node.img_style["shape"] = "square"
        if hasattr (node, "sequence"):
            seqface =  faces.SequenceFace(node.sequence, "aa", 11)
            faces.add_face_to_node(seqface, node, 1, aligned=True)
    leaf_color = "#000000"
    node.img_style["fgcolor"] = leaf_color
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
    if hasattr(node, "shape"):
        node.img_style["shape"]= node.shape
    if hasattr(node, "bgcolor"):
        node.img_style["bgcolor"]= node.bgcolor
    if hasattr(node, "fgcolor"):
        node.img_style["fgcolor"]= node.fgcolor


# ==============================================================================
# Checker function definitions:
#
# All checker actions must receive a node instance as unique argument
# and return True (node passes the filters) or False (node does not
# passes the filters).
#
# ==============================================================================

can_expand    = lambda node: not node.is_leaf() and (hasattr(node, "hide") and node.hide==True)
can_collapse  = lambda node: not node.is_leaf() and (not hasattr(node, "hide") or node.hide==False)
is_leaf       = lambda node: node.is_leaf()
is_not_leaf   = lambda node: not node.is_leaf()
is_marked     = lambda node: node.mark.startswith ('#')
is_not_marked = lambda node: not (node.mark.startswith ('#'))

# ==============================================================================
# Handler function definitions:
#
# All action handler functions must receive a node instance as unique
# argument. Returns are ignored.
#
# Note that there is a special action handler designed for searches
# within the tree. Handler receives node and searched term.
#
# ==============================================================================

def collapse(node):
    node.add_feature("hide", 1)
    node.add_feature("bsize", 25)
    node.add_feature("shape", "sphere")
    node.add_feature("fgcolor", "#bbbbbb")

def expand(node):
    try:
        node.del_feature("hide")
        node.del_feature("bsize")
        node.del_feature("shape")
        node.del_feature("fgcolor")
    except (KeyError, AttributeError):
        pass

def swap_branches(node):
    node.children.reverse()

def mark_branch (node):
    node.add_feature ('mark', '#1')
    node.img_style['hz_line_color'] = '#ff0000'

def clean_marks (node):
    node.mark = ''
    node.img_style['hz_line_color'] = '#000000'

def next_mark (node):
    colors = ['#000099', '#CC0099', '#00FFFF', '#009900',
              '#FF6600', '#666699', '#660000', '#663300']*2
    num = int (node.mark[1:])
    node.mark = '#' + str (num + 1)
    node.img_style['hz_line_color'] = colors [num-1]
    
    
def set_bg(node):
    node.add_feature("bgcolor",
                     '#' + str (pack('BBB',
                                     randint(100, 150),
                                     randint(80, 200),
                                     randint(10, 100))).encode('hex'))
    #node.add_feature("bgcolor", "#CEDBC4")

def set_as_root(node):
    node.get_tree_root().set_outgroup(node)

def load_model (node, model):
    '''
    supra specia action
    link to evolutionnary model
    '''
    model = model ['loadmodel']
    T     = node.get_tree_root()
    model = T._models [model]
    T.change_dist_to_evol ('bL', model, True)
    if model.properties['typ'] == 'site':
        model.set_histface (up=False, typ='protamine',
                            lines = [1.0,0.3], col_lines=['black','grey'])
        I = TreeImageProperties()
        I.aligned_foot.add_face (model.properties['histface'], 1)
        application.set_img_properties (I)
    elif (model.properties['typ'] == 'branch_ancestor'):
        I = TreeImageProperties()
        for n in sorted (T.get_descendants()+[T],
                         key=lambda x: x.paml_id):
            if n.is_leaf(): continue
            anc_face = faces.SequenceFace (n.sequence, 'aa', fsize=11)
            I.aligned_foot.add_face(anc_face, 1)
            I.aligned_foot.add_face(faces.TextFace('paml_id: #%d '%(n.paml_id),
                                                   fsize=8), 0)
        application.set_img_properties (I)
    else:
        application.set_img_properties (None)

def compute_model (node, ctrl_args):
    ''' Super Special action'''
    model_name = ctrl_args ['MODEL']
    del (ctrl_args ['MODEL'])
    node.get_tree_root().run_model (model_name, **ctrl_args)

def search_by_feature(tree, search_term):
    ''' Special action '''
    attr, term = search_term.split("::")
    if not term:
        return None
    elif attr == "clean" and term == "clean":
        for n in tree.traverse():
            try:
                n.del_feature("bsize")
                n.del_feature("shape")
                n.del_feature("fgcolor")
            except:
                pass
    else:
        for n in tree.traverse():
            if hasattr(n, attr) and \
                    re.search(term,  str(getattr(n, attr)), re.IGNORECASE):
                n.add_feature("bsize", 16)
                n.add_feature("shape", "sphere")
                n.add_feature("fgcolor", "#BB8C2B")


# ==============================================================================
# HTML generators
#
# Actions will be automatically added to the popup menus and attached
# to the action handler function. However, if just want to add
# informative items to the popup menu or external actions not
# associated to any handler, you can overwrite the default html
# generator of each action.
#
# html generators receive all information attached to the node and
# action in 5 arguments:
#
# * aindex: index of the action associated to this html generator
#
# * nodeid: id of the node to which action is attached
#
# * treeid: id of the tree in which node is present
#
# * text: the text string associated to the element that raised the
# action (only applicable to text faces actions)
#
# * node: node instance in which action will be executed.
#
#
# Html generator should return a text string encoding a html list
# item:
#
# Example: return "<li> my text </li>"
#
# ==============================================================================


def branch_info(aindex, nodeid, treeid, text, node):
    ''' It shows some info of the node in the popup menu '''
    return '''
           <li style="background:#eee; font-size:8pt;">
           <div style="text-align:left;font-weight:bold;">
            NODE ACTIONS
           </div>
            (<b>Branch: </b>%0.3f <b>Support:</b> %0.3f)<br>
           </li>'''  %\
        (node.dist, node.support)

def search_in_ensmbl(aindex, nodeid, treeid, text, node):
    return '''<li>
              <a target="_blank" href="http://www.ensembl.org/common/Search/Results?species=all;idx=;q=%s">
              <img src=""> Search in ensembl: %s >
              </a>
              </li> ''' %\
            (node.name, node.name)

def get_computed_models (tree):
    '''
    return a list of computed models for a given tree
    '''
    models = []
    for rep in os.listdir (tree.workdir):
        models.append (rep)
    return models

def get_summary_models (tree):
    '''
    parse computed models and return a dict
    with all values (lnL) of all dictionnaries.
    '''
    summary = 'var models_sum = {'
    for rep in os.listdir (tree.workdir):
        tree.link_to_evol_model (tree.workdir +  '/' + rep + '/out', rep)
        summary += "'%s': '<font size=2>log likelihood: %s<br>num parameters: %s</font>', " % \
                   (rep, tree.get_evol_model (rep).lnL, tree.get_evol_model (rep).np)
    return summary [:-1] + '}'


def get_model_values (tree):
    '''
    parse computed models and return a dict
    with all values (lnL) of all dictionnaries.
    '''
    summary = 'var models_sum = {'
    for rep in os.listdir (tree.workdir):
        tree.link_to_evol_model (tree.workdir +  '/' + rep + '/out', rep)
        summary += "'%s': [%s, %s], " % \
                   (rep, tree.get_evol_model (rep).lnL, tree.get_evol_model (rep).np)
    return summary [:-1] + '}'


def get_ctrl_string ():
    '''
    given a model name returns table in html format of
    parameters given to paml
    '''
    tree = EvolTree ()
    ctrl_table = 'var all_models = {'
    for model in AVAIL:
        m = Model (model, tree)
        ctrl_table += "'"+model + "':'<tr>"
        for i, line in enumerate (m.get_ctrl_string().split ('\n')[4:]):
            if not line:
                continue
            if '*' in line:
                line = line.split()[1] + '=' + line.split()[0]
            param, value = map (lambda x: x.strip(), line.split('='))
            #ctrl_table += '<tr><td>%s</td><td>%s</td></tr>' % (param, value)
            ctrl_table += '<td><font size=1> %s </font></td><td><font size=1> <input typ=text id=%s size=4 value=%s></font></td>' % (param, param, value)
            if (i+1)%3 == 0:
                ctrl_table += '</tr><tr>'
        ctrl_table += "</tr>',"
    return ctrl_table[:-1] + '};'


def get_ctrl_keys ():
    '''
    given a model name returns table in html format of
    parameters given to paml
    '''
    tree = EvolTree ()
    ctrl_table = 'var all_models = {'
    for model in AVAIL:
        m = Model (model, tree)
        ctrl_table += "'"+model + "': ["
        for line in m.get_ctrl_string().split ('\n')[4:]:
            if not line:
                continue
            if '*' in line:
                line = line.split()[1] + '=' + line.split()[0]
            param, value = map (lambda x: x.strip(), line.split('='))
            #ctrl_table += '<tr><td>%s</td><td>%s</td></tr>' % (param, value)
            ctrl_table += "'%s'," % (param)
        ctrl_table = ctrl_table [:-1]
        ctrl_table += "],"
    return ctrl_table[:-1] + '};'


def topology_action_divider (aindex, nodeid, treeid, text, node):
    return '''<li style="background:#eee;"><b>Tree node actions</b></li>'''

# ==============================================================================
# TREE RENDERER
#
# By default, ETE will render the tree as a png image and will return
# a simplistic HTML code to show the image and interact with
# it. However, it is possible to wrap such functionality to preprocess
# trees in a particular way, read extra parameters from the URL query
# and/or produce enriched HTML applications.
#
# Tree renderer wrappers receive the tree object, its id, and the WSGI
# application object. They MUST call the
# application._get_tree_img(tree) method and return the a HTML
# string.
#
# A simplistic wrapper that emulates the default WebTreeApplication
# behaviour would be:
#
# def tree_renderer(tree, treeid, application):
#    html = application._get_tree_img(treeid = treeid)
#    return html
#
# ==============================================================================

def tree_renderer(tree, treeid, alignment, application, img_prop=None):
    # The following part controls the features that are attched to
    # leaf nodes and that will be shown in the tree image. Node styles
    # are set it here, and faces are also created. The idea is the
    # following: user can pass feature names using the URL argument
    # "tree_features". If the feature is handled by our function and
    # it is available in nodes, a face will be created and added to
    # the global variable LEAVE_FACES. Remember that our layout
    # function uses such variable to add faces to nodes during
    # rendering.

    # Extracts from URL query the features that must be drawn in the tree 
    asked_features = application.queries.get("show_features", ["name"])[0].split(",")
    def update_features_avail(feature_key, name, col, fsize, fcolor, prefix, suffix):
        text_features_avail.setdefault(feature_key, [name, 0, col, fsize, fcolor, prefix, suffix])
        text_features_avail[feature_key][1] += 1

    tree.add_feature("fgcolor", "#833DB4")
    tree.add_feature("shape", "sphere")
    tree.add_feature("bsize", "8")
    tree.dist = 0
    if not hasattr (tree.get_leaves ()[0], 'nt_sequence'):
        tree.link_to_alignment (alignment)
    tree.workdir = '/var/www/webplugin/tmp/' + treeid
    os.system ('mkdir -p ' + tree.workdir)

    # This are the features that I wanto to convert into image
    # faces. I use an automatic function to do this. Each element in
    # the dictionary is a list that contains the information about how
    # to create a textFace with the feature.
    leaves = tree.get_leaves()
    formated_features =  {
        # feature_name: ["Description", face column position, text_size, color, text_prefix, text_suffix ]
        "name": ["Leaf name", len(leaves), 0, 12, "#000000", "", ""],
        "spname": ["Species name", len(leaves), 1, 12, "#f00000", " Species:", ""],
        }

    # MODELS available
    model_avail = {'--None--': 'None'}
    for model in AVAIL:
        if model.startswith ('fb'):
            model_avail  ['%s (%s)' % \
                          (model, AVAIL[model]['typ'])] = model
        else:
            model_avail  ['%s (%s%s)' % \
                          (model, AVAIL[model]['typ'],
                           ', need marks' * AVAIL[model]['allow_mark'])] = model

    # populates the global LEAVE_FACES variable
    global LEAVE_FACES
    LEAVE_FACES = []
    unknown_faces_pos = 2
    for fkey in asked_features:
        if fkey in formated_features:
            _, _, pos, size, color, prefix, suffix = formated_features[fkey]
            f = faces.AttrFace(fkey, ftype="Arial", fsize=size, fgcolor=color,
                               text_prefix=prefix, text_suffix=suffix)
            LEAVE_FACES.append([f, fkey, pos])
        else:
            # If the feature has no associated format, let's add something standard
            prefix = " %s: " %fkey
            f = faces.AttrFace(fkey, ftype="Arial", fsize=10, fgcolor="#666666",
                               text_prefix=prefix, text_suffix="")
            LEAVE_FACES.append([f, fkey, unknown_faces_pos])
            unknown_faces_pos += 1

    text_features_avail = {}
    for l in leaves:
        for f in l.features: 
            if not f.startswith("_"):
                text_features_avail.setdefault(f, 0)
                text_features_avail[f] = text_features_avail[f] + 1

    html_features = '''
      <div id="tree_features_box">
      <div class="tree_box_header">Available tree features
      <img src="/webplugin/close.png" onclick='$(this).closest("#tree_features_box").hide();'>
      </div>
      <form action='javascript: set_tree_features("", "", "");'>

      '''
    for fkey, counter in text_features_avail.iteritems():
        if fkey in asked_features:
            tag = "CHECKED"
        else:
            tag = ""

        fname = formated_features.get(fkey, [fkey])[0]

        html_features += '<INPUT NAME="tree_feature_selector" TYPE=CHECKBOX %s VALUE="%s">%s (%s/%s leaves)</input><br> ' %\
            (tag, fkey, fname, counter, len(leaves))

    html_features += '''<input type="submit" value="Refresh" 
                        onclick='javascript:
                                // This piece of js code extracts the checked features from menu and redraw the tree sending such information
                                var allVals = [];
                                $(this).parent().children("input[name=tree_feature_selector]").each(function(){
                                if ($(this).is(":checked")){
                                    allVals.push($(this).val());
                                }});
                                draw_tree("%s", "", "", "#img1", {"show_features": allVals.join(",")} );'
                       >
                       </form></div>''' %(treeid)

    features_button = '''
     <li><pre>        </pre><a href="#" title="Select features to display" onclick='show_box(event, $(this).closest("#tree_panel").children("#tree_features_box"));'>
     <img width=24 height=24 BORDER=0 src="/webplugin/icon_tools.png" alt="Select Tree features">
     </a></li>'''

    download_button = '''
     <li><pre>      </pre><a href="/webplugin/tmp/%s.png" title="Download tree image" target="_blank">
     <img width=24 height=24 BORDER=0 src="/webplugin/icon_attachment.png" alt="Download tree image">
     </a></li>''' %(treeid)

    search_button = '''
      <li><pre>      </pre><a href="#" title="Search in tree" onclick='javascript:
          var box = $(this).closest("#tree_panel").children("#search_in_tree_box");
          show_box(event, box); '>
      <img width=24 height=24 BORDER=0 src="/webplugin/icon_search.png" alt="Search in tree">
      </a></li>'''

    evol_button = '''
      <li><pre>      </pre><a href="#" title="Compute evolutionary model" onclick='javascript:
          var box = $(this).closest("#tree_panel").children("#evol_box");
          show_box(event, box); '>
      <img width=24 height=24 BORDER=0 src="/webplugin/icon_calc_gray.gif" alt="Compute Evol Model">
      </a></li>'''

    load_model_button = '''
      <li><pre>      </pre><a href="#" title="Load computed evolutionary model" onclick='javascript:
          var box = $(this).closest("#tree_panel").children("#load_model_box");
          show_box(event, box); '>
      <img width=24 height=24 BORDER=0 src="/webplugin/evolution.gif" alt="Clear search results">
      </a></li>'''

    compare_model_button = '''
      <li><pre>      </pre><a href="#" title="Compare (LRT) computed evolutionary model" onclick='javascript:
          var box = $(this).closest("#tree_panel").children("#compare_model_box");
          show_box(event, box); '>
      <img width=24 height=24 BORDER=0 src="/webplugin/balance_icon.png" alt="Compare models">
      </a></li>'''

    clean_search_button = '''
      <li><pre>       </pre><a href="#" title="Clean tree" onclick='run_action("%s", "", %s, "clean::clean");'>
      <img width=24 height=24 BORDER=0 src="/webplugin/icon_cancel_search.png" alt="Clear search results">
      </a></li>''' % \
        (treeid, 0)

    buttons = '<div id="ete_tree_buttons"><table border="0">' +\
        '<tr align="center" halign="bottom"><td>' + features_button + \
        '</td><td>' + search_button + \
        '</td><td>' + clean_search_button + \
        '</td><td>' + evol_button + \
        '</td><td>' + load_model_button + \
        '</td><td>' + compare_model_button + \
        '</td><td>' + download_button + '</td></tr></table></div>'

    search_select = '<select id="ete_search_target">'
    for fkey in text_features_avail:
        search_select += '<option value="%s">%s</option>' % (fkey, fkey)
    search_select += '</select>'

    search_form = '''
     <div id="search_in_tree_box">
     <div class="tree_box_header"> Search in Tree
     <img src="/webplugin/close.png" onclick='$(this).closest("#search_in_tree_box").hide();'>
     </div>
     <form onsubmit='javascript:
                     search_in_tree("%s", "%s",
                                    $(this).closest("form").children("#ete_search_term").val(),
                                    $(this).closest("form").children("#ete_search_target").val());'
          action="javascript:void(0);">
     %s
     <input id="ete_search_term" type="text" value=""></input>
     <br><i>(Searches are not case sensitive and accept Perl regular expressions)</i>
     <br>
     </form>
     <i> (Press ENTER to initiate the search)</i>
     </div>
     ''' % \
        (treeid, 0, search_select) # 0 is the action index associated
                                   # to the search functionality. This
                                   # means that this action is the
                                   # first to be registered in WebApplication.

    load_model_select = '''<select id="model_to_load" onchange="javascript:
    %s;
    var objContent = document.getElementById('summary_model');
    objContent.innerHTML = models_sum[$(this).val()];
    ">
    ''' % (get_summary_models (tree))

    runned_models = ['--None--'] + get_computed_models (tree)
    for fkey in sorted (runned_models):
        if fkey == '--None--':
            load_model_select += \
                              '<option selected value="None" >--None--</option>\n'
            continue
        load_model_select += '<option value="%s">%s</option>\n' % \
                             (fkey, fkey)
    load_model_select += '</select>'

    load_model_form = '''
     <div id="load_model_box">
         <div class="tree_box_header"> Load Evolutionary Model
           <img src="/webplugin/close.png" onclick='$(this).closest("#load_model_box").hide();' onload='$(this).closest("#load_model_box").hide();'>
         </div>
         <form action="javascript:void(0);">
         <font size=2> Computed model:</font>
         %s
         </form>
         <font size="1">
         <br><br><br>
         <div class="contentBox" style="text-align:left" id="summary_model"></div>
         <div style="text-align:left">
         <br><i>If your model does not appear here, try refreshing, <br> -> first icon "Available tree features"</i><br>
         </div>
         <input type="submit" value="Load" onclick="javascript:
         var model = document.getElementById ('model_to_load').value;
         load_model ('%s', model);
         var allVals = [%s];
         if (model.match(/fb_anc.*/)) {
             allVals.push('paml_id');
         }
         draw_tree('%s', '', '', '#img1', {'show_features': allVals.join(',')} );
         "></font>
     </div>
     ''' % (load_model_select, treeid, "'"+"','".join (asked_features)+"'", treeid) #"


    # first model
    load_first_model_select = '''<select id="first_model_to_load" onchange="javascript:
    %s;
    ">
    ''' % (get_model_values (tree))
    runned_models = ['--None--'] + get_computed_models (tree)
    for fkey in sorted (runned_models):
        if fkey == '--None--':
            load_first_model_select += \
                              '<option selected value="None" >--None--</option>\n'
            continue
        load_first_model_select += '<option value="%s">%s</option>\n' % \
                             (fkey, fkey)
    load_first_model_select += '</select>'

    # second model
    load_second_model_select = '''<select id="second_model_to_load" onchange="javascript:
    %s;
    ">
    ''' % (get_model_values (tree))
    runned_models = ['--None--'] + get_computed_models (tree)
    for fkey in sorted (runned_models):
        if fkey == '--None--':
            load_second_model_select += \
                              '<option selected value="None" >--None--</option>\n'
            continue
        load_second_model_select += '<option value="%s">%s</option>\n' % \
                             (fkey, fkey)
    load_second_model_select += '</select>'

    doc = '<table border=1><tr><th colspan=2>Usual comparisons (Alternative vs Null)</tr><tr><td>'
    doc += '</td></tr><tr><td>'.join (re.findall ('([A-Za-z0-9_]+ +vs +[A-Za-z0-9_]+ +-> +[A-Za-z0-9 =!()]+)',
                                             tree.get_most_likely.__doc__))
    doc = re.sub ('->', '</td><td>', doc)
    doc += '</tr></table>'

    compare_model_form = '''
     <div id="compare_model_box">
         <div class="tree_box_header"> Compare Evolutionary Model
           <img src="/webplugin/close.png" onclick='$(this).closest("#compare_model_box").hide();' onload='$(this).closest("#compare_model_box").hide();'>
         </div>
         <form action="javascript:void(0);">
         <font size=2> Alternative model:</font>
         %s
         <font size=2> Null model:</font>
         %s
         </form>
         <br><br>
         <font size=1>
         <div align="center">
         %s
         </div>
         </font>
         <br>
         <font size="2">
         <div class="contentBox" style="text-align:left" id="delta_df"></div>
         </font>
         <br>
         p-value (that alternative model is the best):<br>
         <rep>       </rep><input typ=text id=result size=8 value=""><br>
         <input type="submit" value="Compare" onclick="javascript:
         %s;
         calculate([models_sum[document.getElementById ('first_model_to_load').value], models_sum [document.getElementById ('second_model_to_load').value], document.getElementById ('result'), document.getElementById ('delta_df')]);">
     </div>
     ''' % (load_first_model_select, load_second_model_select, doc,  get_model_values (tree))


    model_select = '''<select id="model_target" onchange="javascript:
    %s
    var objContent = document.getElementById('ctrl_table');
    objContent.innerHTML = all_models[$(this).val()];
    ">
    ''' % (get_ctrl_string()) # get control string returns a string to build
                              # a hash "all_models" in javascript.
    for fkey in sorted (model_avail):
        if fkey == '--None--':
            model_select += '<option selected value="None" >--None--</option>\n'
            continue
        model_select += '<option value="%s">%s</option>\n' % \
                        (model_avail [fkey], fkey)
    model_select += '</select>'

    evol_form = '''
     <div id="evol_box">
         <div class="tree_box_header"> Compute Evolutionary Model
           <img src="/webplugin/close.png" onclick='$(this).closest("#evol_box").hide();' onload='$(this).closest("#evol_box").hide();'>
         </div>
         <form action="javascript:void(0);">
         <font size=2> Model:</font>
         %s
         </form>
         <font size="2">
             name extention**:
             <input id="extention" type="text" value="%s">
         </font>
         <font size="1">
         <table border="0">
         <div class="contentBox" id="ctrl_table">Select a model</div> 
         </table> </font>
         <font size="2"><i>
             (*)  stars in text field figure for default parameters  <br>
             (**) optional, but usefull specially for branch analysis
             </i>
         </font> <br>
         <input type="submit" value="Run" onclick="javascript:
         var allVals = {};
         %s
         var model = document.getElementById ('model_target').value;
         for (var i in all_models[model]){
               allVals[all_models[model][i]]=document.getElementById (all_models[model][i]).value;
             };
         if (document.getElementById ('extention').value != ''){
            model += '.' + document.getElementById ('extention').value;
         }
         run_model ('%s', model, allVals);
         draw_tree('%s', '', '', '#img1', '');
         ">
     </div>
     ''' % (model_select, #"
         ''.join ([choice ('abcdefghijklmnopqrstuvwxyz') for _ in xrange (4)]),
                  get_ctrl_keys(), treeid, treeid)


    tree_panel_html = '<div id="tree_panel">' + search_form + evol_form \
                      + load_model_form + compare_model_form + html_features + buttons + '</div>'

    # Now we render the tree into image and get the HTML that handles it
    tree_html = application._get_tree_img (treeid = treeid)

    # Let's return enriched HTML
    return tree_panel_html + tree_html

# ==============================================================================
#
# Main WSGI Application
#
# ==============================================================================

# Create a basic ETE WebTreeApplication
application = WebTreeApplication()

# Set your temporal dir to allow web user to generate files. This two
# paths should point to the same place, one using the absolute path in
# your system, and the other the URL to access the same
# directory. Note that the referred directory must be writable by the
# webserver.
#application.CONFIG["temp_dir"] = "/home/services/web/ete.cgenomics.org/webpluin/tmp/"
application.CONFIG["temp_dir"] = "/var/www/webplugin/tmp/"
application.CONFIG["temp_url"] = "/webplugin/tmp/" # Relative to web site Document Root

# Set the DISPLAY port that ETE should use to draw pictures. You will
# need a X server installed in your server and allow webserver user to
# access the display. If the X server is started by a different user
# and www-data (usally the apache user) cannot access display, try
# modifiying DISPLAY permisions by executing "xhost +"
application.CONFIG["DISPLAY"] = ":0" # This is the most common
                                     # configuration

# We extend the minimum WebTreeApplication with our own WSGI
# application
#application.set_external_app_handler(example_app)

# Lets now apply our custom tree loader function to the main
# application
application.set_tree_loader(my_tree_loader)

# And our layout as the default one to render trees
application.set_default_layout_fn(codeml_clean_layout)

# No img properties at start
application.set_img_properties (None)

# I want to make up how tree image in shown using a custrom tree
# renderer that adds much more HTML code
application.set_external_tree_renderer(tree_renderer)


# ==============================================================================
# ADD CUSTOM ACTIONS TO THE APPLICATION
#
# The function "register_action" allows to attach functionality to
# nodes in the image. All registered accions will be shown in the
# popup menu bound to the nodes and faces in the web image.
#
#
# register_action(action_name, target_type=["node"|"face"|"layout"|"search"|"compute"], \
#                 action_handler, action_checker, html_generator_handler)
#
# When the Application is executed it will read your registered
# acctions and will do the following:
#
# 1. Load the tree and get the image map
#
# 2. For each node and face in the tree, it will browse all registered
# actions and will run the action_checker function to determine if the
# action must be activated for such node or face
#
# 3. If action_checker(node) returns True, the action will be attached
# to the context menu of that specific node or face, otherwise it will
# be hidden.
#
# 4. When a click is done on a specific node, popup menus will be
# built using their active actions. For this, ETE will use the
# html_generator function associated to each function if
# available. Otherwise, a popup entry will be added automatically.
#
# 5. When a certain action is pressed in the popup menus, the
# action_handler function attached to the action will be executed over
# its corresponding node, and the tree image will be refreshed.
#
# Special values:
#
#  action_checker = None : It will be interpreted as "Show allways"
#  html_generator = None : Autogenerate html and link to action
#  action_handler = None : Action will be ignored
#
# ==============================================================================

# We first register the special action "search" which is attached to
# our custom search function.
application.register_action ("", "search", search_by_feature, None, None)

# MY custom run model action "compute" which is attached to MY
# custom compute function.
application.register_action ("", "compute"  , compute_model, None, None)
application.register_action ("", "loadmodel", load_model   , None, None)

# Node manipulation options (bound to node items and all their faces)
application.register_action ("branch_info", "node",
                             None, None, branch_info)
application.register_action ("<b>Collapse</b>", "node",
                             collapse, can_collapse, None)
application.register_action ("Expand", "node", expand,
                             can_expand, None)
application.register_action ("Highlight background", "node",
                             set_bg, None, None)
application.register_action ("Mark branch", "node",
                             mark_branch, is_not_marked, None)
application.register_action ("Clean mark", "node",
                             clean_marks, is_marked, None)
application.register_action ("Following mark", "node",
                             next_mark, is_marked, None)
application.register_action ("Set as root", "node",
                             set_as_root, None, None)
application.register_action ("Swap children", "node",
                             swap_branches, is_not_leaf, None)

#application.register_action ("Default layout", "layout", main_layout, None, None)
application.register_action ("Clean PAML layout", "layout",
                             codeml_clean_layout, None, None)
application.register_action ("Complimented PAML layout", "layout",
                             codeml_cartoon_layout, None, None)


