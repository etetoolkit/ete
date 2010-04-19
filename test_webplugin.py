from ete_dev import Tree
from ete_dev import faces
from ete_dev.treeview import drawer

def ly(node):
    if node.is_leaf():
        node.img_style["size"]=3
        node.img_style["shape"] = "square"
        faces.add_face_to_node(faces.AttrFace("name","Arial",10,"#4f8f0f",None), node, 0 )
    else:
        if node.name == "D":
            faces.add_face_to_node(faces.TextFace("TextoExtra","Arial",10,"#000000",None), node, 0 )
            node.img_style["size"]=15

        elif node.name == "root":
            faces.add_face_to_node(faces.ImgFace("./human.png"), node, 0 )
            

t = Tree("(A,(B,C)D)root;", format=1)
print t.render("test.png", layout=ly)
print t._QtItem_.rect()
for n in t.traverse():
    node_coords =  n._QtItem_.mapToScene(0,0)
    x1, y1 = node_coords.x(), node_coords.y()
    x2, y2 =  n._QtItem_.rect().width(), n._QtItem_.rect().height()
    print "node", x1,y1, x2,y2
    for item in n._QtItem_.childItems():
        pos = item.mapToScene(0,0)
        x1, x2 = pos.x(), pos.y()
        if isinstance(item, drawer._TextItem):
            x2, y2 = x1+item.face._width(), x2+item.face._height()
            print "text", x1,y1,x2,y2, item.text()
        elif isinstance(item, drawer._FaceItem):
            x2, y2 = x1+item.face._width(), x2+item.face._height()
            print "face", x1,y1,x2,y2
