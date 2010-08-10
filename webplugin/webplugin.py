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
# My apache config para el sitio "default":
#
# <VirtualHost *:80>
#         ServerAdmin webmaster@localhost

#        WSGIDaemonProcess site-1 user=www-data group=www-data processes=1 threads=1
#        WSGIProcessGroup site-1

#  
#         DocumentRoot /var/www
#         <Directory />
#         	Options +FollowSymLinks
#         	AllowOverride None
#         </Directory>
#  
#  
#         <Directory /var/www/wsgi/>
#         	Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
#          	SetHandler wsgi-script
#         	Order allow,deny
#         	Allow from all
#                 AddHandler wsgi-script .py  
#         </Directory>
#  
#         ErrorLog /var/log/apache2/error.log
#  
#         # Possible values include: debug, info, notice, warn, error, crit,
#         # alert, emerg.
#         LogLevel warn
#  
#         CustomLog /var/log/apache2/access.log combined
#  
#  
# </VirtualHost>
#
#
#
#
# You can customize the plugin by modifying the last part of this
# file. This is the whole idea!! enjoy, this a very draft version.
# 

import os
import time
import hashlib
import cgi

from ete2 import Tree, PhyloTree, __VERSION__
from ete2.treeview import drawer
CONFIG = {}

class WebTreeApplication(object):
    def __init__(self):
        self.TreeConstructor = Tree
        self.actions = {"node": [], "layout": [], "face": []}
        self._layout = None
        self._treeid2layout = {}
        self._external_app_handler = None

    def register_action(self, name, target, handler, refresh):
        if target not in self.actions: 
            raise ValueError("Invalid target for action:", target)
        self.actions[target].append([name, handler, refresh])

    def set_tree_loader(self, TreeConstructor):
        self._tree = TreeConstructor
    def set_layout_fn(self, layout_fn):
        self._layout = layout_fn

    def _get_html_map(self, img_map, treeid):

        html_map = '<MAP NAME="imgmap_%s">' %(treeid)
        if img_map["nodes"]:
            for x1, y1, x2, y2, nodeid, text in img_map["nodes"]:
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "node", "%s");' href='javascript:void(0);'>""" %\
                    (x1, y1, x2, y2, treeid, nodeid)
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
            elif atype == "layout":
                self._treeid2layout[treeid] = handler

        layout_fn = self._treeid2layout.get(treeid, self._layout)
        img_map = render_tree(t, img_path, layout_fn)
        html_map = self._get_html_map(img_map, treeid)
        ete_publi = '</br><a href="http://ete.cgenomics.org" style="font-size:7pt;" target="_blank" > %s </a>' %(__VERSION__)
        open(tree_path, "w").write(t.write(features=[]))
        return html_map+"""<img src="%s" USEMAP="#imgmap_%s" onclick='javascript:show_context_menu("%s", "layout", "void", "void");' >""" %(img_url, treeid, treeid) + ete_publi

    # WSGI web application 
    def __call__(self, environ, start_response):
        """ This function is executed when the application is called
        by the WSGI apache module. It is, therefore, in charge of
        answering web requests."""
        path = environ['PATH_INFO'].split("/")
        start_response('202 OK', [('content-type', 'text/plain')])
        if environ['REQUEST_METHOD'].upper() == 'GET' and  environ['QUERY_STRING']:
            queries = cgi.parse_qs(environ['QUERY_STRING'])
        elif environ['REQUEST_METHOD'].upper() == 'POST' and environ['wsgi.input']:
            queries = cgi.parse_qs(environ['wsgi.input'].read())
        else:
            queries = {}

        method = path[1]
        #return  '\n'.join(map(str, environ.items())) + str(queries) + '\t\n'.join(environ['wsgi.input'])
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
                html += """ <a  href='javascript:void(["%s", "%s", "%s", "%s"])' onClick='run_action("%s", "%s", "%s", "%s");'> %s </a><br> """ %\
                    (treeid, atype, nodeid, aindex, treeid, atype, nodeid, aindex, action)
            return html+treeid

        elif method == "action":
            atype = str(queries["atype"][0])
            nid = str(queries["nid"][0])
            treeid = str(queries["treeid"][0])
            aindex = int(str(queries["aindex"][0]))
            name, handler, refresh = self.actions[atype][aindex]
            if atype in set(["node","face"]):
                return self._get_tree(treeid=treeid, pre_drawing_action=[atype, handler, [nid]])
            elif atype == "layout":
                return self._get_tree(treeid=treeid, pre_drawing_action=[atype, handler, []])
            return "Bad guy"
                
        elif self._external_app_handler:
            return self._external_app_handler(environ, start_response, queries)
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
    #drawer._QApp.quit()
    #drawer._QApp = None
    
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
    #drawer._QApp.quit()
    #drawer._QApp = None

    return img_map

# USER PART. You can modify this part
application = WebTreeApplication()
#CONFIG["temp_dir"] = "/home/services/web/jaime.phylomedb.org/tmp/"
#CONFIG["temp_url"] = "http://jaime.phylomedb.org/tmp/"
CONFIG["temp_dir"] = "/var/www/tmp/"
CONFIG["temp_url"] = "http://localhost/tmp/"

CONFIG["DISPLAY"] = ":0"

def my_collapse(node):
    node.collapsed = True
    node.add_feature("bsize", 50)

def my_tree_loader(tree):
    t = PhyloTree(tree)
    return t

def set_as_root(node):
    node.get_tree_root().set_outgroup(node)

def my_layout(node):
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
        node.img_style["fgcolor"]= "#ff0000"
    else:
        node.img_style["size"]= 20
        node.img_style["fgcolor"]= "#cccccc"

def ly2(node):
    if hasattr(node, "bsize"):
        node.img_style["size"]= int(node.bsize)
        node.img_style["fgcolor"]= "#00ff00"
    else:
        node.img_style["size"]= 20


application.set_tree_loader(my_tree_loader)
#application.set_layout_fn(my_layout)

# [name, applies to, handler, refresh picture ]
# node/faces -> load current tree, perform action on node and redraw tree
application.register_action("collapse node", "node", my_collapse, True)
application.register_action("set as root", "node", set_as_root, True)
application.register_action("what a face!", "face", my_collapse, True)
application.register_action("style 1", "layout", ly2, True)
application.register_action("style 2", "layout", my_layout, True)
application.register_action("style 3", "layout", None, True)

