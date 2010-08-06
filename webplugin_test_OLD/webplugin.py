# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys, os, random, ete_dev
from ete_dev.treeview import drawer
from ete_dev import faces
from mod_python import Cookie
from sitesettings import *

PHYLOMEDB_POINTER = None
rules = []
actionBox = []
ruleProcessors = []

########## FLEXIBLE SECTION #############################

###  STYLES FOR DRAWING THE TREES ###

def nonodestype(node):
    leaf_color = "#000000"
    node.img_style["shape"] = "circle"
    if hasattr(node,"evoltype"):
        if node.evoltype == 'D':
            node.img_style["fgcolor"] = "#1d176e"
            node.img_style["vt_line_color"] = "#000099"
        elif node.evoltype == 'S':
            node.img_style["fgcolor"] = "#FF0000"
            node.img_style["vt_line_color"] = "#990000"
        elif node.evoltype == 'L':
            node.img_style["fgcolor"] = "#777777"
            node.img_style["vt_line_color"] = "#777777"
            node.img_style["hz_line_color"] = "#777777"
            node.img_style["line_type"] = 1
            leaf_color = "#777777"
    if node.is_leaf()  and not node.collapsed:
        node.img_style["shape"] = "square"
        node.img_style["size"] = 4
        node.img_style["fgcolor"] = leaf_color
        faces.add_face_to_node(faces.AttrFace("name","Trebuchet MS",10,leaf_color,None), node, 2)
        if hasattr(node,"sequence"):
            SequenceFace =  faces.SequenceFace(node.sequence,"aa",13)
            faces.add_face_to_node(SequenceFace, node, 1, aligned=True)
    elif node.collapsed:
        node.img_style["size"] = 10
        faces.add_face_to_node(faces.AttrFace("nodes_inside","Trebuchet MS",10,leaf_color,None), node, 0 )
    else:
        node.img_style["size"] = 0

def myphylogeny(node):
    leaf_color = "#000000"
    node.img_style["shape"] = "circle"
    if hasattr(node,"evoltype"):
        if node.evoltype == 'D':
            node.img_style["fgcolor"] = "#1d176e"
            node.img_style["hz_line_color"] = "#1d176e"
            node.img_style["vt_line_color"] = "#1d176e"
        elif node.evoltype == 'S':
            node.img_style["fgcolor"] = "#FF0000"
            node.img_style["line_color"] = "#FF0000"
        elif node.evoltype == 'L':
            node.img_style["fgcolor"] = "#777777"
            node.img_style["vt_line_color"] = "#777777"
            node.img_style["hz_line_color"] = "#777777"
            node.img_style["line_type"] = 1
            leaf_color = "#777777"
    if node.is_leaf() and not node.collapsed:
        node.img_style["shape"] = "square"
        node.img_style["size"] = 4
        if node.name == gene:
            node.img_style["fgcolor"] = "#FF0000"
            faces.add_face_to_node( faces.AttrFace("name","Trebuchet MS",10,"#FF0000",None), node, 0)
        else:
            node.img_style["fgcolor"] = leaf_color
            faces.add_face_to_node( faces.AttrFace("name","Trebuchet MS",10,leaf_color,None), node, 0)
        if hasattr(node,"sequence"):
            SequenceFace =  faces.SequenceFace(node.sequence,"aa",13)
            faces.add_face_to_node(SequenceFace, node, 1, aligned=True)
    elif node.collapsed:
        node.img_style["size"] = 20
        faces.add_face_to_node(faces.AttrFace("nodes_inside","Trebuchet MS",10,leaf_color,None), node, 0 )
    else:
        node.img_style["size"] = 6
        
def red(node):
    leaf_color = "#000000"
    node.img_style["shape"] = "circle"
    if hasattr(node,"evoltype"):
        if node.evoltype == 'D':
            node.img_style["fgcolor"] = "#1d176e"
            node.img_style["hz_line_color"] = "#1d176e"
            node.img_style["vt_line_color"] = "#1d176e"
        elif node.evoltype == 'S':
            node.img_style["fgcolor"] = "#FF0000"
            node.img_style["line_color"] = "#FF0000"
        elif node.evoltype == 'L':
            node.img_style["fgcolor"] = "#777777"
            node.img_style["vt_line_color"] = "#777777"
            node.img_style["hz_line_color"] = "#777777"
            node.img_style["line_type"] = 1
            leaf_color = "#777777"
    if node.is_leaf() and not node.collapsed:
        node.img_style["shape"] = "square"
        node.img_style["size"] = 4
        if node.name == gene:
            node.img_style["fgcolor"] = "#FF0000"
            faces.add_face_to_node( faces.AttrFace("name","Trebuchet MS",10,"#FF0000",None), node, 0)
        else:
            node.img_style["fgcolor"] = leaf_color
            faces.add_face_to_node( faces.AttrFace("name","Trebuchet MS",10,"#FF0000",None), node, 0)
        if hasattr(node,"sequence"):
            SequenceFace =  faces.SequenceFace(node.sequence,"aa",13)
            faces.add_face_to_node(SequenceFace, node, 1, aligned=True)
    elif node.collapsed:
        node.img_style["size"] = 20
        faces.add_face_to_node(faces.AttrFace("nodes_inside","Trebuchet MS",10,"#FF0000",None), node, 0 )
    else:
        node.img_style["size"] = 6

### RULES SYSTEM ##################

# system of registering the rules for menus
#   actionBox.append([ menu type (empty|nodes|faces) , 'unique'|'switch', 'ruleName', 'argument', 'on name', 'off name'])
# - empty = the empty area on the image
# - nodes = then user click on the node
# - faces = then user click on the faces
# - unique = means that this setting can be applied only ones, next usage will erase the previous setting ('off name' ignored)
# - switch = multiple setting allow to use the type of the rule many times in a rules set, and generate two items in menu with a 'on name' and 'off name'
# - ruleName = id of the rule, used in the rule processors
# - argument = used in the rule processor (can be empty if the case of 'nodes' menu type, because in that case in equal to nodeID)
# - 'on name', 'off name' = the strings you will see in the JS menu

actionBox.append(['empty', 'unique', 'style', 'nonodes', 'No nodes style', ''])
actionBox.append(['empty', 'unique', 'style', 'nodes', 'Nodes style', ''])
actionBox.append(['empty', 'unique', 'style', 'red', 'Red style', ''])
actionBox.append(['nodes', 'switch', 'collapse', '', 'Collapse', 'Expand'])
actionBox.append(['nodes', 'unique', 'outgroup', '', 'Make outgroup', ''])
actionBox.append(['nodes', 'switch', 'delete', '', 'Delete', ''])


def stylesProcessor(value):
    if value == 'nonodes':
        mylayout = nonodestype
    elif value == 'red':
        mylayout = red
    else:
        mylayout = myphylogeny
    return mylayout

def collapsProcessor(value, t):
    hotnode = get_node_by_id(t, value)
    hotnode.collapsed = True
    hotnode.add_features(nodes_inside=len(hotnode.get_leaves()))
    return t

def outgroupProcessor(value, t):
    outgroup = get_node_by_id(t, value)
    if t != outgroup:
        t.set_outgroup(outgroup)
    return t
    
def delProcessor(value, t):
    outgroup = get_node_by_id(t, value)
    outgroup.delete()
    return t

ruleProcessors.append(['style', stylesProcessor])
ruleProcessors.append(['collapse', collapsProcessor])
ruleProcessors.append(['outgroup', outgroupProcessor])
ruleProcessors.append(['delete', delProcessor])

def rulesProcesor(t): # called from tree generator
    mylayout = myphylogeny
    for processor in ruleProcessors:
        for item in open(store + "/" + gene + ".rules"):    
            key,value = item.strip().split("\t")
            if processor[0] == 'style':
                if key == processor[0]:
                    mylayout = processor[1](value)
            else:
                if key == processor[0]:
                    t = processor[1](value, t)

    return t, mylayout


### Get info about leave >>> here can be any function of leave ID with HTML return

def get_node_by_id(t,unic_id):
    for n in t.traverse():
        if n.unic_id == int(unic_id):
            return n

def info(req=None, dbid=None):
    import os, sys, MySQLdb, ete_dev
    if req:
        req.content_type = 'text/html'

    def get_pointer():
        global PHYLOMEDB_POINTER
        if PHYLOMEDB_POINTER is None:
            PHYLOMEDB_POINTER = ete_dev.PhylomeDBConnector()            
        return PHYLOMEDB_POINTER

    def close_p():
        global PHYLOMEDB_POINTER
        if PHYLOMEDB_POINTER is not None:
            try:
                PHYLOMEDB_POINTER._SQL.close()
                PHYLOMEDB_POINTER._SQLconnection.close()
                PHYLOMEDB_POINTER = None
            except:
                pass

    # prepare seq for popup window
    def split_code(code):
        output = "<table style='font-family: Courier New; font-size: 8pt;'>"
        c = 1
        for i in range(len(code)/10+1):
            if c == 1:
                output += "<tr>"
            output += "<td>" + code[i*10:(i+1)*10] + "</td>"
            if c == 4:
                output += "</tr>"
                c = 0
            c += 1
        if c == 1:
            output += "</table>"
        else:
            output += "</tr></table>"
        return output

    #p = get_pointer()
    ## get info about DB id
    #info = p.get_seqid_info(dbid)
    #close_p()
    ## put information in show/hide boxes
    #res =  hide_box('Name', info['name'])
    #res += hide_box('Comments', info['comments'])
    #res += hide_box('Sequence', split_code(info['seq']), mode='none') # mode='none' - hide the box content by default
    
    res =  hide_box('Example', 'any information about leave with id = ' + dbid + ' in a hide/show box' )
    
    return res # return information to the popup menu in HTML format



########## "DO NOT TOCH" SECTION !!! #############################

# --- for providing a sessions with use of cookies
def generateHash():  # make the unic ID for session
    import sha, time
    return sha.new(str(time.time())).hexdigest()

def getCookie(req, key):
    cookies = Cookie.get_cookies(req)
    if cookies.has_key(key):
        return str(cookies[key]).split('=')[1]

def setCookie(req, key, value):
    cookie = Cookie.Cookie(key, value)
    Cookie.add_cookie(req, cookie)
# ------------------------------------------------

class WebPlugin:
    def __init__(self, req, temp_folder='/var/tmp', hostname = '/'):
        # --- establish a new session and create a temp folder for it
        if getCookie(req, 'sid'):
            self.sid = getCookie(req, 'sid')
        else:
            self.sid = generateHash()
            setCookie(req, 'sid', self.sid)
        self.tempFolder = temp_folder
        # create a temp folder for session
        self.sessionFolder = os.path.join(self.tempFolder, self.sid)
        if not os.path.exists(self.sessionFolder):
            os.mkdir(self.sessionFolder)
            os.chmod(self.sessionFolder, 0777)
        # -----------------------------------------------------------
        self.hostname = hostname

    def publishTree(self, tree):
        import sha
        full = sha.new(tree).hexdigest()
        treeid = full[:5] + full[len(full)-5:]
        # --- put the clear tree in NW format to the file on the session folder
        TREE = open(os.path.join(self.sessionFolder, treeid+'.tree'), 'w')
        print >> TREE, tree
        # --- return the spetial action-HTML template for the tree manipulation
        return "<img src='"+self.hostname+"loader.gif?rnd="+str(random.random())+"' id='"+treeid+"' onClick=\"mapcheck(this,'"+treeid+"')\" onLoad=\"get_map(this, '"+treeid+"', '"+self.sid+"')\"><div id='scriptarea_"+treeid+"'></div>"



# Generate POPUP js menus on the fly

def emptymenu(req=None, id=None):
    if req:
        req.content_type = 'text/plain'
    ret = ''
    for item in actionBox:
        if item[0] == 'empty':
            if item[1] == 'unique':
                ret += "<a href='javascript:void(0)' onClick=\"unic_rule('"+item[2]+"','"+id+"', '"+item[3]+"')\">"+item[4]+"</a><br>"
            else:
                ret += "<a href='javascript:void(0)' onClick=\"set_rule('"+item[2]+"','"+id+"', '"+item[3]+"')\">"+item[4]+"</a><br>"
                if item[5] != '':
                    ret += "<a href='javascript:void(0)' onClick=\"rem_rule('"+item[2]+"','"+id+"', '"+item[3]+"')\">"+item[5]+"</a><br>"
    
    return ret+"<a href='javascript:void(0)' onClick=\"ask_for_new_image('"+id+"');\">Reload tree</a><br><a href='javascript:void(0)' onClick=\"clear_rules('"+id+"');\">Reset</a>";
    
def nodemenu(req=None, id=None, node=None):
    if req:
        req.content_type = 'text/plain'
    
    ret = ''
    for item in actionBox:
        if item[0] == 'nodes':
            if item[1] == 'unique':
                ret += "<a href='javascript:void(0)' onClick=\"unic_rule('"+item[2]+"','"+id+"', '"+node+"')\">"+item[4]+"</a><br>"
            else:
                ret += "<a href='javascript:void(0)' onClick=\"set_rule('"+item[2]+"','"+id+"', '"+node+"')\">"+item[4]+"</a><br>"
                if item[5] != '':
                    ret += "<a href='javascript:void(0)' onClick=\"rem_rule('"+item[2]+"','"+id+"', '"+node+"')\">"+item[5]+"</a><br>"
    return ret;
    
    return "<a href=\"javascript:set_rule('collapse', '"+id+"',"+node+")\">Collaplse</a><br><a href=\"javascript:rem_rule('collapse', '"+id+"',"+node+")\">Expand</a><br><a href=\"javascript:unic_rule('root', '"+id+"',"+node+")\">Make outgroup</a>";


##  FOR FACES THIS PART SHOLD BE CHANGED
def facesmenu(req=None):
    if req:
        req.content_type = 'text/plain'
    return "<a href=\"javascript:alert('not possible yet')\">Hide this</a><br><a href=\"javascript:alert('not possible yet')\">Some action 1</a><br><a href=\"javascript:alert('not possible yet')\">Some action 2</a>"


# if script called from the command line -> generate the image of tree
try:
    sys.argv[1]
except IndexError:
    pass
else:
    def ask_for_tree(treepath):
        return open(treepath).readline()

    def prep(x):
        # prepare int variables for storing in the map
        if type(x).__name__=='int':
            return "'"+str(x)+"'"
        elif type(x).__name__=='float':
            return "'"+str(int(x))+"'"
        else:
            return "'"+str(x)+"'"

    store = TEMP_FOLDER + '/' + sys.argv[1]
    gene = sys.argv[2]
    os.environ['DISPLAY']=':0.0'
    tree = ask_for_tree(store + "/" + gene + ".tree")
    if tree != 0:
        t = ete_dev.PhyloTree(tree)
        outgroup = t.get_midpoint_outgroup()
        try:
            t.set_outgroup(outgroup)
        except ValueError:
            pass
        else:
            for ev in t.get_descendant_evol_events():
                pass
        a = 1
        for n in t.traverse():
            n.add_features(unic_id=a)
            try:
                n.name
            except AttributeError:
                pass
            else:
                n.name = n.name.split("_")[0]
            a += 1

        # aply rules on the tree
        try:
            open(store + "/" + gene + ".rules")
        except IOError:
            anlayout = myphylogeny
        else:
            t, anlayout = rulesProcesor(t)
        
        #############  should be changed in future ########
        t.render(store+"/"+gene+".png", layout=anlayout)
        w, h =  t._QtItem_.scene().sceneRect().width(), t._QtItem_.scene().sceneRect().height()
        t.render(store+"/"+gene+".png", layout=anlayout, w=w, h=h)
        
        bdata = open(store+"/"+gene+".png", 'rb').read()
        # os.remove(store+"/"+gene+".png")
        ###################################################
        
        # prepare the map lists
        node_list = []
        text_list = []
        face_list = []

        for n in t.traverse():
            try:
                node_coords =  n._QtItem_.mapToScene(0,0)
            except AttributeError:
                pass
            else:
                x1, y1 = node_coords.x(), node_coords.y()
                x2, y2 = x1 + n._QtItem_.rect().width()*2, y1 + n._QtItem_.rect().height()*2
                node_list.append([x1,y1,x2,y2,n.unic_id])
                for item in n._QtItem_.childItems():
                    pos = item.mapToScene(0,0)
                    x1, y1 = pos.x()+5, pos.y()
                    if isinstance(item, drawer._TextItem):
                        x2, y2 = x1+item.face._width(), y1+item.face._height()
                        text_list.append([x1,y1,x2,y2, item.text()])
                    elif isinstance(item, drawer._FaceItem):
                        x2, y2 = x1+item.face._width(), y1+item.face._height()
                        face_list.append([x1,y1,x2,y2])

        # store the map
        try:
            MAP = open(store+"/"+gene+".map","w")
        except IOError:
            pass
        else:
            MAP.write("map['"+gene+"'] = {")
            MAP.write("'nodes':[")
            dev = ""
            for item in node_list:
                MAP.write(dev + "["+",".join(map(prep, item))+"]")
                dev = ","
            MAP.write("],'texts':[")
            dev = ""
            for item in text_list:
                MAP.write(dev + "["+",".join(map(prep, item))+"]")
                dev = ","
            if len(face_list) > 0:
                MAP.write("],'faces':[")
                dev = ""
                for item in face_list:
                    MAP.write(dev + "["+",".join(map(prep, item))+"]")
                    dev = ","
                MAP.write("]};")
            else:
                MAP.write("]};")
            MAP.close()
        
        print bdata

def rtree(req=None, tree=None, sid=None):
    # render the tree image
    from popen2 import Popen3
    proc = Popen3("python "+SCRIPT_FOLDER+"/webplugin.py "+sid+" "+tree)
    proc.tochild.close()
    add = '1'
    fromchild = proc.fromchild.readline()
    while add:
        add = proc.fromchild.readline()
        fromchild += add
    if req:
        req.content_type = 'text/plain'  # for debugging
        # req.content_type = 'image/png'
    return fromchild

def getmap(req=None, seqid=None, sid=None): 
    # read a map from a file or return alert
    THIS_SESSION_PATH = TEMP_FOLDER + '/' + sid
    if req:
        req.content_type = 'text/javascript'
    try:
        res = open(THIS_SESSION_PATH+"/"+seqid+".map")
    except IOError:
        return "alert('no map "+THIS_SESSION_PATH+"');"
    else:
        out = res.readline()
        return out

def addrule(req=None, seqid=None, itemid=None, rule=None, sid=None, unic='0', remove='0', clear='0'):
    THIS_SESSION_PATH = TEMP_FOLDER + '/' + sid
    if req:
        req.content_type = 'text/plain'
    done = False
    rules = set()
    if clear == '1':
        RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules", "w")
        RULES.close()
    else:
        try:
            RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules")
        except IOError:
            pass
        else:
            for item in RULES:
                key, value = item.strip().split('\t')
                if remove == '1' and str(key) == str(rule) and str(value) == str(itemid):
                    pass
                elif unic == '1' and key == rule:
                    pass
                else:
                    rules.add(item.strip())
        if remove == '0':
            rules.add(rule + '\t' + str(itemid))
        RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules", "w")
        sid
        for rule in rules:
            print >> RULES, rule

    return 1

def hide_box(title, content, mode='block'):
        output = "<div style='border: 1px solid #777; padding: 4px; margin-top: 10px;'><div style='margin-top: -14px; position: absolute;'><span class='hide_box_title popup_bg'>" + title + "</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'block'\">Show</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'none'\">Hide</span></div><div style='padding-top: 4px; display: "+mode+"'>" + content + "</div></div>"
        return output

