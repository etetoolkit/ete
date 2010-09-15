import os
import time
import cgi
from hashlib import md5

ALL = ["WebTreeApplication"]

class WebTreeApplication(object):
    def __init__(self):
        self.TreeConstructor = None
        self.NODE_TARGET_ACTIONS = ["node", "face"]
        self.TREE_TARGET_ACTIONS = ["layout", "search", "tree"]
        self.actions = []
        self._layout = None
        self._treeid2layout = {}
        self._external_app_handler = None
        self._treeid2tree = {}
        self._treeid2index = {}
        self.CONFIG = {
            "temp_dir":"/var/www/tmp",
            "temp_url":"http://localhost/tmp",
            "DISPLAY" :":0"
            }

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
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "%s", "%s");' href="javascript:void('%s');">""" %\
                    (int(x1), int(y1), int(x2), int(y2), treeid, nodeid, ','.join(map(str, nid2actions.get(nodeid,[]))), str(nodeid) )
        if img_map["faces"]:
            for x1, y1, x2, y2, nodeid, text in img_map["faces"]:
                html_map += """ <AREA SHAPE="rect" COORDS="%s,%s,%s,%s" onClick='show_context_menu("%s", "%s", "%s", "%s");' href="javascript:void('%s');">""" %\
                    (int(x1),int(y1),int(x2),int(y2), treeid, nodeid, ','.join(map(str, nid2actions.get(nodeid,[])+nid2face_actions.get(nodeid,[])  )), text, text)
        html_map += '</MAP>'
        return html_map

    def _load_tree_from_path(self, treeid):
        tree_path = os.path.join(self.CONFIG["temp_dir"], treeid+".nw")
        t = self._treeid2tree[treeid] = self._tree(tree_path)
        tree_index  = self._treeid2index[treeid] = {}
        for n in t.traverse():
            if hasattr(n, "_nid"):
                tree_index[str(n._nid)] = n
        return t, tree_index

    def _dump_tree_to_file(self, t, treeid):
        tree_path = os.path.join(self.CONFIG["temp_dir"], treeid+".nw")
        open(tree_path, "w").write(t.write(features=[]))

    def _get_tree(self, tree=None, treeid=None, pre_drawing_action=None):
        if not treeid:
            treeid = md5(str(time.time())).hexdigest()

        img_url = os.path.join(self.CONFIG["temp_url"], treeid+".png?"+str(time.time()))
        img_path = os.path.join(self.CONFIG["temp_dir"], treeid+".png")

        debug_track = str(self._treeid2tree.get(treeid, None)) 
        debug_cache = "NOP"
        if not tree and self._treeid2tree.get(treeid, None):
            t = self._treeid2tree[treeid]
            tree_index = self._treeid2index[treeid]
            debug_cache = "SI"
        elif not tree:
            t, tree_index = self._load_tree_from_path(treeid)
        else:
            t = self._tree(tree)
            self._treeid2tree[treeid] = t
            tree_index = self._treeid2index[treeid] = {}

        if pre_drawing_action:
            atype, handler, arguments = pre_drawing_action
            if atype in set(["node", "face"]) and len(arguments)==1 and handler:
                nid = arguments[0]
                #node = get_node_by_id(t, nid)
                #return [nid, str(type(nid)).replace("<",""), cache]
                node = tree_index.get(str(nid), None)
                handler(node)
            elif atype == "tree":
                handler(t)
            elif atype == "search":
                handler(t, arguments[0])
            elif atype == "layout":
                self._treeid2layout[treeid] = handler

        layout_fn = self._treeid2layout.get(treeid, self._layout)
        mapid = "img_map_"+str(time.time())
        img_map = render_tree(t, img_path, self.CONFIG["DISPLAY"], layout_fn)
        html_map = self._get_html_map(img_map, treeid, mapid, t)
        for n in t.traverse():
            self._treeid2index[treeid][str(n._nid)]=n
            if hasattr(n, "_QtItem_"):
                n._QtItem_ = None
                delattr(n, "_QtItem_")

        debug_track+= str(self._treeid2index.get(treeid, None))+debug_cache

        tree_actions = []
        for aindex, (action, target, handler, checker, html_generator) in enumerate(self.actions):
            if target in self.TREE_TARGET_ACTIONS and (not checker or checker(t)):
                tree_actions.append(aindex)

        try:
            version_tag = __VERSION__
        except NameError: 
            version_tag = "ete_dev"

        self._dump_tree_to_file(t, treeid)

        ete_publi = '<div style="margin:0px;padding:0px;text-align:left;"><a href="http://ete.cgenomics.org" style="font-size:7pt;" target="_blank" >%s</a></div>' %\
            (version_tag)
        img_html = """<img class="ete_tree_img" src="%s" USEMAP="#%s" onLoad='javascript:bind_popup();' onclick='javascript:show_context_menu("%s", "", "%s");' >""" %\
            (img_url, mapid, treeid, ','.join(map(str, tree_actions)))

        return html_map+ "<div>"+ img_html + ete_publi + "</div>"

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
            if nodeid: 
                if treeid not in self._treeid2tree:
                    t, tree_index = self._load_tree_from_path(treeid)
                else:
                    tree_index = self._treeid2index[treeid]
                node = tree_index[nodeid]
            else:
                node = None

            if textface: 
                header = str(textface).strip()
            else:
                header = "Menu"
            html = """<div id="ete_popup_header"><span id="ete_popup_header_text">%s</span><img onClick='hide_popup();' src="close.png"></div><ul>""" %\
                (header)
            for i in map(int, actions.split(",")): 
                aname, target, handler, checker, html_generator = self.actions[i]
                if html_generator: 
                    html += html_generator(i, treeid, nodeid, textface, node)
                else:
                    html += """<li><a  href='javascript:void(0)' onClick='run_action("%s", "%s", "%s");'> %s </a></li> """ %\
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

def render_tree(t, img_path, display, layout=None):
    os.environ["DISPLAY"]=display
    return t.render(img_path, layout = layout)
