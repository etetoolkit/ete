# Final import should be like this
# from ete2.webplugin  import WebTreeApplication
import sys
sys.path.insert(0, "/home/jhuerta/_Devel/ete2-webplugin/")
from ete_dev import WebTreeApplication

# USER PART. You can modify this part
from ete_dev import PhyloTree, faces

application = WebTreeApplication()
# Set your temporal dir to allow web user to generate files
application.CONFIG["temp_dir"] = "/var/www/ete.loc/tmp/"
application.CONFIG["temp_url"] = "/tmp/"
# Set the DISPLAY port that ete should use to draw pictures. web user
# (i.e. www-data must have permission on the device)
application.CONFIG["DISPLAY"] = ":0"

# My custom functionality for the plugin
PLUGIN_URL = "/wsgi/webplugin_example.py"
name_face = faces.AttrFace("name", fsize=12)
text_face = faces.TextFace("__ ETE__", fsize=12)

def my_tree_loader(tree):
    t = PhyloTree(tree)
    return t

def collapse(node):
    node.add_feature("hide", 1)
    node.add_feature("bsize", 50)

def expand(node):
    node.add_feature("hide", 0)
    try: 
        node.del_feature("bsize")
    except KeyError: 
        pass

def set_red(node):
    node.add_feature("fgcolor", "#f00000")

def set_as_root(node):
    node.get_tree_root().set_outgroup(node)

def my_layout1(node):
    if hasattr(node, "hide"):
        if node.hide == 1:
            node.img_style["draw_descendants"]= False
    if hasattr(node, "fgcolor"):
        node.img_style["fgcolor"]= node.fgcolor
    else:
        node.img_style["fgcolor"]= "#1F1F9C"
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
    else:
        node.img_style["size"]= 10

    if node.is_leaf():
        faces.add_face_to_node(name_face, node, 0, False)
    faces.add_face_to_node(text_face, node, 1, False)

def my_layout2(node):
    if hasattr(node, "hide"):
        if node.hide == 1:
            node.img_style["draw_descendants"]= False
    if hasattr(node, "fgcolor"):
        node.img_style["fgcolor"]= node.fgcolor
    else:
        node.img_style["fgcolor"]= "#cccccc"
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
    else:
        node.img_style["size"]= 10

    if node.is_leaf():
        faces.add_face_to_node(name_face, node, 0, False)
       

def link_to_my_page(action_index, nodeid, treeid, text, node):
    return """<a href="#"> Example link 1: %s </a><br> """ %(node.name)

def link_to_my_other_page(action_index, nodeid, treeid, text, node):
    return """<a href="#"> Example link 2: %s </a><br> """ %(text)

application.set_tree_loader(my_tree_loader)
application.set_default_layout_fn(my_layout1)

# register_action(action_name, target_type=node|face|layout, action_handler, action_checker,  html_generator_handler )
#
# The algorithm works as follows: 
#
# 1. load the tree and get the map
# 2. for each node and face in the tree, browses all registered actions and run the action_checker function
# 3. if checker(node) returns True, the action will be associated to the context menu of node or face, otherwise it will be hidden
# 4. it uses html_generator function to get the HTML to be shown in the menu
# 5. if action is activated (clicked), action_handler is called
# 
# action_checker = None : Show allways
# html_generator = None : Autogenerate html and link to action
#

can_expand = lambda node: hasattr(node, "hide") and node.hide==True
can_collapse = lambda node: not hasattr(node, "hide") or node.hide==False
is_leaf = lambda node: node.is_leaf()

application.register_action("collapse node", "node", collapse, can_collapse, None)
application.register_action("Expand node", "node", expand, can_expand, None)

application.register_action("set as root", "node", set_as_root, None, None)
application.register_action("set red", "node", set_red, None, None)

application.register_action("notused", "face", None, None, link_to_my_page)
application.register_action("notused", "face", None, is_leaf, link_to_my_other_page)

application.register_action("default", "layout", my_layout1, None, None)
application.register_action("grey", "layout", my_layout2, None, None)


# You can also extend the WSGI web application 
def my_custom_app_extension(environ, start_response, queries):
    path = environ['PATH_INFO'].split("/")                      
    if path[1]=="action1":
        start_response('202 OK', [('content-type', 'text/html')])
        text = queries.get("text", [None])[0]        
        if text:
            return ["ACTION1. You have clicked on<b>%s</b>" %text]
        else:
            return ["ACTION1. Mande?" %text]
        
    if path[1]=="action2":
        start_response('202 OK', [('content-type', 'text/html')])
        text = queries.get("text", [None])[0]        
        if text:
            return ["ACTION2. You have clicked on<b>%s</b>" %text]
        else:
            return ["ACTION2. Mande?" %text]


def link_to_action1(action_index, treeid, nodeid, text, node):
    return """<a href="%s/action1/?text=%s "> Action 1: %s </a><br> """ %(PLUGIN_URL, text, text)

def link_to_action2(action_index, treeid, nodeid, text, node):
    return """<a href="%s/action2/?text=%s "> Action 2: %s </a><br> """ %(PLUGIN_URL, text, text)

def search_form(action_index, treeid, nodeid, text, node):
    return """Search:<input type="text" id="ete_search_node"></input> 
<input onClick='run_action("%s", "%s", "%s",  $("#ete_search_node").val() );' type="submit" value="go!"> """ %\
        (treeid, "void", action_index)

def search_by_name(tree, search_term):
    for n in tree.traverse(): 
        if search_term in n.name: 
            n.add_feature("bsize", 50)
            n.add_feature("fgcolor", "#BB8C2B")


application.register_action("notused", "face", None, is_leaf, link_to_action1)
application.register_action("notused", "face", None, is_leaf, link_to_action2)

application.register_action("search", "search", search_by_name, None, search_form)

# IF no ETE plugin arguments are handled, the query is passed to your WSGI handler
application.register_external_app_handler(my_custom_app_extension)
