from ete_dev import Tree, faces
import random

rs = faces.TextFace("branch-right", fsize=20, fgcolor="#009000")
bd = faces.TextFace("branch-bottom", fsize=11, fgcolor="#909000")
ud = faces.TextFace("branch-top", fsize=11, fgcolor="#099000")


def mylayout(node):
    # If node is a leaf, add the nodes name and a its scientific
    # name
    node.img_style["size"]=random.sample(range(20),1)[0]
    if node.is_leaf():
        return
        #faces.add_face_to_node(t1, node, column=0, position="aligned")
        #faces.add_face_to_node(t1, node, column=0, position="aligned")
        faces.add_face_to_node(rs, node, column=0, position="branch-right")
        faces.add_face_to_node(rs, node, column=1, position="branch-right")
        faces.add_face_to_node(rs, node, column=1, position="branch-right")
        return
        faces.add_face_to_node(bd, node, column=1, position="branch-bottom")
        faces.add_face_to_node(bd, node, column=1, position="branch-bottom")

        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
    else:
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(ud, node, column=1, position="branch-top")
        faces.add_face_to_node(bd, node, column=1, position="branch-bottom")
        faces.add_face_to_node(bd, node, column=1, position="branch-bottom")
        faces.add_face_to_node(rs, node, column=0, position="branch-right")
        faces.add_face_to_node(rs, node, column=1, position="branch-right")
        faces.add_face_to_node(rs, node, column=1, position="branch-right")


        #faces.add_face_to_node(t1, node, column=1, position="branch-right")

        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")
        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")
        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")
        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")



def mylayout2(node):
    node.img_style["size"]=10
    if node.is_leaf():
        return

        
t = Tree()
t.dist = 0
t.populate(5)
t.show(mylayout)
