import ete2, sys, os
from ete2.treeview import drawer
from ete2 import faces

store = '/home/services/web/ivan.phylomedb.org/temp/' + sys.argv[1]
gene = sys.argv[2]
   
def nonodestype(node):
    # the style for drowing trees with ETE2
    leaf_color = "#000000"
    node.img_style["shape"] = "circle"
    # add a function in each node
    # faces.add_face_to_node(faces.AttrFace("function","Courier New",10,leaf_color,None), node, 0)
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

def phylogeny(node):
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
        

def ask_for_tree(treepath):
    # in future here should be request to DB
    return open(treepath).readline()

def prep(x):
    # prepare variables for storing in the map
    if type(x).__name__=='int':
        return "'"+str(x)+"'"
    elif type(x).__name__=='float':        
        return "'"+str(int(x))+"'"
    else:
        return "'"+str(x)+"'"

def get_node_by_id(t,unic_id):
    a = 1
    for n in t.traverse():
        if a == int(unic_id):
            return n
        a += 1

# the place with write permissions
os.environ['DISPLAY']=':0.0'

tree = ask_for_tree(store + "/" + gene + ".tree")

if tree != 0:
    t = ete2.PhyloTree(tree)
    
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
    
    ####################    THE RULES PROCESSOR #################################

    try:
        open(store + "/" + gene + ".rules")
    except IOError:
        pass
    else:
        # collapse processing
        for item in open(store + "/" + gene + ".rules"):
            key,value = item.strip().split("\t")
            if key == 'collapse':
                hotnode = get_node_by_id(t, value)
                hotnode.collapsed = True
                hotnode.add_features(nodes_inside=len(hotnode.get_leaves()))

        # outgroup processing
        for item in open(store + "/" + gene + ".rules"):
            key,value = item.strip().split("\t")
            if key == 'root':
                outgroup = get_node_by_id(t, value)
                if t != outgroup:
                    t.set_outgroup(outgroup)
                    
        # styles processing 

        for item in open(store + "/" + gene + ".rules"):
            key,value = item.strip().split("\t")
            if key == 'style':
                if value == 'nonodes':
                    phylogeny = nonodestype

        #   ADD NEW RULES HERE

    ###############################################################################
    
   
    #############  should be changed in future ########
    t.render(store+"/"+gene+".png", layout=phylogeny)
    w, h =  t._QtItem_.scene().sceneRect().width(), t._QtItem_.scene().sceneRect().height()
    t.render(store+"/"+gene+".png", layout=phylogeny, w=w, h=h)
    
    bdata = open(store+"/"+gene+".png", 'rb').read()
    os.remove(store+"/"+gene+".png")
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
    MAP = open(store+"/"+gene+".map","w")
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
