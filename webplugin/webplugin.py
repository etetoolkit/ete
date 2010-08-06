#!/usr/bin/python

#
# You should place this file in a WSGI apache enabled directory
#
# This structure worked for me
# 
# /var/www/wsgi/webplugin.py 
# /var/www/tmp/                    # 777 
# /var/www/example.html
# /var/www/jquery-1.4.2.min.js
#
#
# you can customize the plugin by modifying the last part of this file
# 


import os
import time
import hashlib
import urlparse 
from ete2 import Tree, PhyloTree, __VERSION__
from ete2.treeview import drawer

CONFIG = {}

class WebTreeApplication(object):
    def __init__(self):
        self.TreeConstructor = Tree
        self.actions = {"node": [], "style": [], "face": []}
        self._layout = None

    def register_action(self, name, target, handler, refresh):
        if target not in self.actions: 
            raise ValueError("Invalid target for action:", target)
        self.actions[target].append([name, handler, refresh])

    def set_tree_loader(self, TreeConstructor):
        self._tree = TreeConstructor
    def set_latout_fn(self, layout_fn):
        self._layout = layout_fn

    def _get_html_map(self, img_map, treeid):
        html_map = '<MAP NAME="imgmap_%s">' %(treeid)
        if img_map["nodes"]:
            for x1, y1, x2, y2, nodeid, text in img_map["nodes"]:
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "node", "%s");' href='javascript:void(%s);'>""" %\
                    (x1, y1, x2, y2, treeid, nodeid, treeid)
        if img_map["faces"]:
            for x1, y1, x2, y2, nodeid, text in img_map["faces"]:
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "face", "%s", "%s");' href='javascript:void(0);'>""" %\
                    (x1,y1,x2,y2, treeid, nodeid, text)
        html_map += '</MAP>'
        return html_map

    def _get_tree(self, tree=None, treeid=None, pre_drawing_action=None):
        if not treeid:
            treeid = hashlib.md5(str(time.time())).hexdigest()

        tree_path = os.path.join(CONFIG["temp_dir"], treeid+".nw")
        img_path = os.path.join(CONFIG["temp_dir"], treeid+".png")
        tree_url = os.path.join(CONFIG["temp_url"], treeid+".nw")
        img_url = os.path.join(CONFIG["temp_url"], treeid+".png?"+str(time.time()))

        if not tree:
            t = self._tree(tree_path)
        else:
            t = self._tree(tree)
        
        if pre_drawing_action:
            atype, handler, arguments = pre_drawing_action
            if atype == "node":
                nid = arguments[0]
                node = get_node_by_id(t, nid)
                handler(node)

            elif atype == "style":
                self.set_layout(handler)

        img_map = render_tree(t, img_path, self._layout)
        html_map = self._get_html_map(img_map, treeid)
        ete_publi = '</br><a href="http://ete.cgenomics.org" style="font-size:8pt;" target="_blank" > %s </a>' %(__VERSION__)
        open(tree_path, "w").write(t.write(features=[]))
        return html_map+"""<img src="%s" USEMAP=#imgmap_%s>""" %(img_url, treeid) + ete_publi + tree_path + treeid

    # WSGI web application 
    def __call__(self, environ, start_response):
        """ This function is executed when the application is called
        by the WSGI apache module. It is, therefore, in charge of
        answering web requests."""

        path = environ['PATH_INFO'].split("/")
        start_response('202 OK', [('content-type', 'text/plain')])
        if environ['REQUEST_METHOD'].upper() == 'GET' and  environ['QUERY_STRING']:
            queries = urlparse.parse_qs(environ['QUERY_STRING'])
        elif environ['REQUEST_METHOD'].upper() == 'POST' and environ['wsgi.input']:
            queries = urlparse.parse_qs(environ['wsgi.input'].read())
        else:
            queries = {}

        method = path[1]
        #return  '\n'.join(map(str, environ.items())) + str(queries) + '\t\n'.join(environ['wsgi.input'])
        action_name = queries.get("action", None)
        action_target = queries.get("target", None)
        nodeid = queries.get("nodeid", None)
        if method == "draw":
            if "tree" in queries and "treeid" in queries:
                treeid = str(queries["treeid"][0])
                tree = str(queries["tree"][0])
                return self._get_tree(tree=tree, treeid=treeid)

            else:
                return "No tree found"

        elif method == "get_menu": 
            atype = str(queries["atype"][0])
            nodeid = str(queries["nid"][0])
            treeid = str(queries["treeid"][0])
            html = ''
            for aindex, (action, handler, refresh) in enumerate(self.actions.get(atype, [])):
                html += """ <a  href='javascript:void(0)' onClick='run_action("%s", "%s", "%s", "%s");'> %s </a></br> """ %\
                    (treeid, atype, nodeid, aindex, action)
            return html+treeid

        elif method == "action":
            atype = str(queries["atype"][0])
            nid = str(queries["nid"][0])
            treeid = str(queries["treeid"][0])
            aindex = int(str(queries["aindex"][0]))
            name, handler, refresh = self.actions[atype][aindex]
            if atype in set(["node","face"]):
                return self._get_tree(treeid=treeid, pre_drawing_action=[atype, handler, [nid]])
            elif atype == "style":
                return self._get_tree(treeid, pre_drawing_action=[atype, handler, []])
            return "Bad guy"
                
        else:
            return  '\n'.join(map(str, environ.items())) + str(queries) + '\t\n'.join(environ['wsgi.input'])


### Get info about leave >>> here can be any function of leave ID with HTML return
def get_node_by_id(t, nid):
    nid = str(nid)
    for n in t.traverse():
        if n._nid == nid:
            return n

def render_tree(t, img_path, layout=None):
    def prep(x):
        # prepare int variables for storing in the map
        if type(x).__name__=='int':
            return "'"+str(x)+"'"
        elif type(x).__name__=='float':
            return "'"+str(int(x))+"'"
        else:
            return "'"+str(x)+"'"
    os.environ["DISPLAY"]=CONFIG["DISPLAY"]
    #############  should be changed in future ########
    t.render(img_path, layout = layout)
    w, h =  t._QtItem_.scene().sceneRect().width(), t._QtItem_.scene().sceneRect().height()
    t.render(img_path, w=w, h=h, layout = layout)
    #bdata = open(img_path, 'rb').read()
    # os.remove(store+"/"+gene+".png")
    ###################################################
        
    # prepare the map lists
    node_list = []
    text_list = []
    face_list = []

    for nid, n in enumerate(t.traverse()):
        n.add_feature("_nid", str(nid))
        try:
            node_coords =  n._QtItem_.mapToScene(0,0)
        except AttributeError:
            pass
        else:
            x1, y1 = node_coords.x(), node_coords.y()
            x2, y2 = x1 + n._QtItem_.rect().width()*2, y1 + n._QtItem_.rect().height()*2
            node_list.append([x1,y1,x2,y2, nid, None])
            for item in n._QtItem_.childItems():
                pos = item.mapToScene(0,0)
                x1, y1 = pos.x()+5, pos.y()
                if isinstance(item, drawer._TextItem):
                    x2, y2 = x1+item.face._width(), y1+item.face._height()
                    face_list.append([x1,y1,x2,y2, nid, str(item.text())])
                elif isinstance(item, drawer._FaceItem):
                    x2, y2 = x1+item.face._width(), y1+item.face._height()
                    face_list.append([x1,y1,x2,y2, nid, None])

    img_map = {"nodes": node_list, "faces": face_list, "text": text_list }
    return img_map











# USER PART. You can modify this part
application = WebTreeApplication()
CONFIG["temp_dir"] = "/var/www/tmp/"
CONFIG["temp_url"] = "http://localhost/tmp/"
CONFIG["DISPLAY"] = ":0"

def my_collapse(node):
    node.collapsed = True
    node.add_feature("bsize", 50)

def my_tree_loader(tree):
    t = PhyloTree(tree)
    return t

def my_layout(node):
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
        node.img_style["fgcolor"]= "#ff0000"
    else:
        node.img_style["size"]= 20


application.set_tree_loader(my_tree_loader)
application.set_latout_fn(my_layout)

# [name, applies to, handler, refresh picture ]
# node/faces -> load current tree, perform action on node and redraw tree
application.register_action("collapse node", "node", my_collapse, True)
application.register_action("what a face!", "face", my_collapse, True)

