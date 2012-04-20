import sys
import os
import time
import cgi
from hashlib import md5

ALL = ["WebTreeApplication"]

class WebTreeApplication(object):
    """ Provides a basic WSGI application object which can handle ETE
        tree visualization and interactions.  Please, see the
        webplugin example provided with the ETE installation package
        (http://pypi.python.org/pypi/ete_dev)."""

    def __init__(self):
        # Redirects normal output msgs to stderr, since stdout in web
        # application is for the browser
        sys.stdout = sys.stderr 

        self.TreeConstructor = None
        self.NODE_TARGET_ACTIONS = ["node", "face"]
        self.TREE_TARGET_ACTIONS = ["layout", "search"]
        self.actions = []
        self._layout = None
        self._tree_style = None
        self._width = None
        self._height = None
        self._size_units = "px" 
        self._custom_tree_renderer = None
        self._treeid2layout = {}
        self._external_app_handler = None
        self._treeid2tree = {}
        self._treeid2index = {}
        self._img_properties = None
        self.queries = {}
        self.CONFIG = {
            "temp_dir":"/var/www/webplugin/",
            "temp_url":"http://localhost/webplugin/tmp",
            "DISPLAY" :":0" # Used by ete to render images
            }

    def set_tree_size(self, w, h, units="px"):
        """ Fix the size of tree image """
        self._width = w
        self._height = h
        self._size_units = units

    def set_external_app_handler(self, handler):
        """ Sets a custom function that will extend current WSGI
        application."""
        self._external_app_handler = handler

    def set_external_tree_renderer(self, handler):
        """ If the tree needs to be processed every time is going to
        be drawn, the task can be delegated. """
        self._custom_tree_renderer = handler

    def register_action(self, name, target, handler, checker, html_generator):
        """ Adds a new web interactive function associated to tree
        nodes. """
        self.actions.append([name, target, handler, checker, html_generator])

    def set_tree_loader(self, TreeConstructor):
        """ Delegate tree constructor. It allows to customize the Tree
        class used to create new tree instances. """
        self._tree = TreeConstructor

    def set_default_layout_fn(self, layout_fn):
        """ Fix the layout function used to render the tree. """
        self._layout = layout_fn

    def set_tree_style(self, handler):
        """ Fix a :class:`TreeStyle` instance to render tree images. """
        self._tree_style = handler

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

    def _load_tree(self, treeid, tree=None):
        # if a tree is given, it overwrites previous versions
        if tree:
            t = self._tree(tree)
            self._treeid2tree[treeid] = t
            self._load_tree_index(treeid)

        # if no tree is given, and not in memmory, it tries to loaded
        # from previous sessions
        if treeid not in self._treeid2tree:
            self._load_tree_from_path(treeid)

        # Returns True if tree and indexes are loaded
        return (treeid in self._treeid2tree) and (treeid in self._treeid2index)

    def _load_tree_from_path(self, treeid):
        tree_path = os.path.join(self.CONFIG["temp_dir"], treeid+".nw")
        if os.path.exists(tree_path):
            t = self._treeid2tree[treeid] = self._tree(tree_path)
            self._load_tree_index(treeid)
            return True
        else:
            return False

    def _load_tree_index(self, treeid):
        if not self._treeid2index.get(treeid, {}):
            tree_index = self._treeid2index[treeid] = {}
            t = self._treeid2tree[treeid] 
            for n in t.traverse():
                if hasattr(n, "_nid"):
                    tree_index[str(n._nid)] = n
            return True
        else:
            return False

    def _dump_tree_to_file(self, t, treeid):
        tree_path = os.path.join(self.CONFIG["temp_dir"], treeid+".nw")
        open(tree_path, "w").write(t.write(features=[], format=0))

    def _get_tree_img(self, treeid, pre_drawing_action=None, img_prop=None):
        img_url = os.path.join(self.CONFIG["temp_url"], treeid+".png?"+str(time.time()))
        img_path = os.path.join(self.CONFIG["temp_dir"], treeid+".png")

        t = self._treeid2tree[treeid]
        tree_index = self._treeid2index[treeid]

        self._dump_tree_to_file(t, treeid)
        if pre_drawing_action:
            atype, handler, arguments = pre_drawing_action
            if atype in set(["node", "face"]) and len(arguments)==1 and handler:
                nid = arguments[0]
                node = tree_index.get(str(nid), None)
                handler(node)
            elif atype == "tree":
                handler(t, arguments[0])
            elif atype == "search":
                handler(t, arguments[0])
            elif atype == "layout":
                self._treeid2layout[treeid] = handler
            elif atype == "compute":
                handler(t, arguments[0])
            elif atype == "loadmodel":
                handler(t, arguments[0])

        layout_fn = self._treeid2layout.get(treeid, self._layout)
        img_prop  = self._img_properties
        mapid = "img_map_"+str(time.time())
        img_map = _render_tree(t, img_path, self.CONFIG["DISPLAY"], layout = layout_fn, 
                               tree_style = self._tree_style, 
                               w=self._width,
                               h=self._height,
                               units=self._size_units)
        html_map = self._get_html_map(img_map, treeid, mapid, t)
        for n in t.traverse():
            self._treeid2index[treeid][str(n._nid)]=n
            if hasattr(n, "_QtItem_"):
                n._QtItem_ = None
                delattr(n, "_QtItem_")

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
        img_html = """<img class="ete_tree_img" border="0" src="%s" USEMAP="#%s" onLoad='javascript:bind_popup();' onclick='javascript:show_context_menu("%s", "", "%s");' >""" %\
            (img_url, mapid, treeid, ','.join(map(str, tree_actions)))

        tree_div_id = "ETE_tree_"+str(treeid)
        return html_map+ '<div id="%s" >'%tree_div_id + img_html + ete_publi + "</div>"

    # WSGI web application 
    def __call__(self, environ, start_response):
        """ This function is executed when the application is called
        by the WSGI apache module. It is, therefore, in charge of
        answering web requests."""
        path = environ['PATH_INFO'].split("/")
        start_response('202 OK', [('content-type', 'text/plain')])
        if environ['REQUEST_METHOD'].upper() == 'GET' and  environ['QUERY_STRING']:
            self.queries = cgi.parse_qs(environ['QUERY_STRING'])
        elif environ['REQUEST_METHOD'].upper() == 'POST' and environ['wsgi.input']:
            self.queries = cgi.parse_qs(environ['wsgi.input'].read())
        else:
            self.queries = {}
        method = path[1]
        treeid = self.queries.get("treeid", [None])[0]
        alignment = self.queries.get("alignment", [None])[0]
        nodeid = self.queries.get("nid", [None])[0]
        textface = self.queries.get("textface", [None])[0]
        actions = self.queries.get("show_actions", [None])[0]
        tree = self.queries.get("tree", [None])[0]
        search_term = self.queries.get("search_term", [None])[0]
        aindex = self.queries.get("aindex", [None])[0]

        if method == "draw":
            # if not treeid is given, generate one 
            if not treeid:
                treeid = md5(str(time.time())).hexdigest()

            if not self._load_tree(treeid, tree):
                return "draw: Cannot load the tree: %s" %treeid

            if self._custom_tree_renderer:
                t = self._treeid2tree[treeid]
                return self._custom_tree_renderer(t, treeid, alignment, self)
            elif t and treeid: 
                return self._get_tree_img(treeid=treeid)
            else:
                return "No tree to draw"

        elif method == "get_menu": 
            if not self._load_tree(treeid):
                return "get_menu: Cannot load the tree: %s" %treeid
            
            if nodeid:
                tree_index = self._treeid2index[treeid]
                node = tree_index[str (nodeid)]
            else:
                node = None

            if textface: 
                header = str(textface).strip()
            else:
                header = "Menu"
            html = """<div id="ete_popup_header"><span id="ete_popup_header_text">%s</span><div id="ete_close_popup" onClick='hide_popup();'></div></div><ul>""" %\
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
            if not self._load_tree(treeid):
                return "action: Cannot load the tree: %s" %treeid

            if aindex is None:
                # just refresh tree
                stderr.write ('refresh tree\n\n')
                return self._get_tree_img(treeid=treeid)
            else: 
                aname, target, handler, checker, html_generator = self.actions[int(aindex)]

            if target in set(["node", "face", "layout"]):
                return self._get_tree_img(treeid=treeid, pre_drawing_action=[target, handler, [nodeid]])
            elif target in set(["compute"]):
                from re import sub
                params = {}
                for key in self.queries:
                    if not 'run_params' in key:
                        continue
                    params [sub ('run_params\[(\w+)\]',
                                 '\\1' ,key)] = self.queries [key][0]
                #stderr.write ('run_params: '+ str (self.queries)+'\n\n')
                return self._get_tree_img(treeid=treeid, pre_drawing_action=[target, handler, [params]])
            elif target in set(["loadmodel"]):
                from re import sub
                params = {}
                for key in self.queries:
                    if not 'loadmodel' in key:
                        continue
                    params [sub ('loadmodel\[(\w+)\]',
                                 '\\1' ,key)] = self.queries [key][0]
                #stderr.write ('run_params: '+ str (self.queries)+'\n\n')
                return self._get_tree_img(treeid=treeid, pre_drawing_action=[target, handler, [params]])
            elif target in set(["search"]):
                return self._get_tree_img(treeid=treeid, pre_drawing_action=[target, handler, [search_term]])
            elif target in set(["refresh"]):
                return self._get_tree_img(treeid=treeid)
            return "Bad guy"

        elif self._external_app_handler:
            return self._external_app_handler(environ, start_response, self.queries)
        else:
            return  '\n'.join(map(str, environ.items())) + str(self.queries) + '\t\n'.join(environ['wsgi.input'])

def _render_tree(t, img_path, display, layout=None, tree_style=None, 
                 w=None, h=None, units="px"):
    os.environ["DISPLAY"]=display
    return t.render(img_path, layout = layout, tree_style=tree_style, 
                    w=w, h=h, units=units)
