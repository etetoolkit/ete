#!/usr/bin/python

#
# You should place this file in a WSGI apache enabled directory
#
# This structure worked for me
# 
# /var/www/wsgi/webplugin_example.py 
# /var/www/tmp/                    # 777 
# /var/www/webplugin_example.html
# /var/www/jquery-1.4.2.min.js
# /var/www/ete.js
# /var/www/ete.css
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
# You can customize the plugin by modifying the last part of this
# file. This is the whole idea!! enjoy, this a very draft version.
import os
import time
import hashlib
import cgi

__VERSION__ = "ete_dev"
CONFIG = {}

class WebTreeApplication(object):
    def __init__(self):
        self.TreeConstructor = None
        self.NODE_TARGET_ACTIONS = ["node", "face"]
        self.TREE_TARGET_ACTIONS = ["layout", "search", "tree"]
        self.actions = []
        self._layout = None
        self._treeid2layout = {}
        self._external_app_handler = None

    def register_external_app_handler(self, handler):
        self._external_app_handler = handler

    def register_action(self, name, target, handler, checker, html_generator):
        self.actions.append([name, target, handler, checker, html_generator])

    def set_tree_loader(self, TreeConstructor):
        self._tree = TreeConstructor

    def set_default_layout_fn(self, layout_fn):
        self._layout = layout_fn

    def _get_html_map(self, img_map, treeid, mapid, tree):
        # Scans for node-enabled actions. 
        nid2actions = {}
        nid2face_actions = {}
        for n in tree.traverse():
            for aindex, (action, target, handler, checker, html_generator) in enumerate(self.actions):
                if target == "node" and (not checker or checker(n)):
                    nid2actions.setdefault(int(n._nid), []).append(aindex)
                elif target == "face" and (not checker or checker(n)):
                    nid2face_actions.setdefault(int(n._nid), []).append(aindex)

        html_map = '<MAP NAME="%s" class="ete_tree_img">' %(mapid)
        if img_map["nodes"]:
            for x1, y1, x2, y2, nodeid, text in img_map["nodes"]:
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "%s", "%s");' href='javascript:void("%s");'>""" %\
                    (x1, y1, x2, y2, treeid, nodeid, ','.join(map(str, nid2actions.get(nodeid,[]))), str(len(self.actions)) )
        if img_map["faces"]:
            for x1, y1, x2, y2, nodeid, text in img_map["faces"]:
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "%s", "%s", "%s");' href=javascript:void('%s');>""" %\
                    (x1,y1,x2,y2, treeid, nodeid, ','.join(map(str, nid2actions.get(nodeid,[])+nid2face_actions.get(nodeid,[])  )), text, text)
        html_map += '</MAP>'
        return html_map+str(len(img_map["nodes"]))

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
            if atype in set(["node", "face"]) and len(arguments)==1 and handler:
                nid = arguments[0]
                node = get_node_by_id(t, nid)
                handler(node)
            elif atype == "tree":
                handler(t)
            elif atype == "search":
                handler(t, arguments[0])
            elif atype == "layout":
                self._treeid2layout[treeid] = handler

        layout_fn = self._treeid2layout.get(treeid, self._layout)
        mapid = "img_map_"+str(time.time())
        img_map = render_tree(t, img_path, layout_fn)
        html_map = self._get_html_map(img_map, treeid, mapid, t)

        tree_actions = []
        for aindex, (action, target, handler, checker, html_generator) in enumerate(self.actions):
            if target in self.TREE_TARGET_ACTIONS and (not checker or checker(t)):
                tree_actions.append(aindex)
        
        ete_publi = '</br><a href="http://ete.cgenomics.org" style="font-size:7pt;" target="_blank" > %s </a>' %(__VERSION__)
        open(tree_path, "w").write(t.write(features=[]))
        return html_map+"""<img class="ete_tree_img" src="%s" USEMAP="#%s" onLoad='javascript:bind_popup();' onclick='javascript:show_context_menu("%s", "void", "%s");' >""" %\
            (img_url, mapid, treeid, ','.join(map(str, tree_actions))) \
            + ete_publi

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
        treeid = queries.get("treeid", [None])[0]
        nodeid = queries.get("nid", [None])[0]
        textface = queries.get("textface", [None])[0]
        actions = queries.get("show_actions", [None])[0]
        tree = queries.get("tree", [None])[0]
        search_term = queries.get("search_term", [None])[0]
        aindex = queries.get("aindex", [None])[0]

        if method == "draw":
            if "tree" in queries and "treeid" in queries:
                treeid = str(queries["treeid"][0])
                tree = str(queries["tree"][0])
                return self._get_tree(tree=tree, treeid=treeid)
            else:
                return "No tree found"

        elif method == "get_menu": 
            html = """<div onClick='hide_popup();' style='text-align:right;' id="close_popup">[X]</div><ul>"""
            for i in map(int, actions.split(",")): 
                aname, target, handler, checker, html_generator = self.actions[i]
                if html_generator: 
                    html += html_generator(i, treeid, nodeid, textface)
                else:
                    html += """<li> <a  href='javascript:void(0)' onClick='run_action("%s", "%s", "%s");'> %s </a></li> """ %\
                        (treeid, nodeid, i, aname)
            html += '</ul>'
            return html

        elif method == "action":
            aname, target, handler, checker, html_generator = self.actions[int(aindex)]
            if target in set(["node","face", "tree", "layout"]):
                return self._get_tree(treeid=treeid, pre_drawing_action=[target, handler, [nodeid]])
            elif target in set(["search"]):
                return self._get_tree(treeid=treeid, pre_drawing_action=[target, handler, [search_term]])
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
    os.environ["DISPLAY"]=CONFIG["DISPLAY"]
    #############  should be changed in future ########
    return t.render(img_path, layout = layout)

    w, h =  t._QtItem_.scene().sceneRect().width(), t._QtItem_.scene().sceneRect().height()
    t.render(img_path, w=w, h=h, layout = layout)
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
                    face_list.append([x1,y1,x2,y2, nid, str(item.face.get_text())])
                elif isinstance(item, drawer._FaceItem):
                    x2, y2 = x1+item.face._width(), y1+item.face._height()
                    face_list.append([x1,y1,x2,y2, nid, None])

    img_map = {"nodes": node_list, "faces": face_list, "text": text_list }
    return img_map
