from ete_dev import Tree, faces, TreeImageProperties
import random

rs1 = faces.TextFace("branch-right1", fsize=20, fgcolor="#009000")
rs2 = faces.TextFace("branch-right2", fsize=20, fgcolor="#009000")
rs3 = faces.TextFace("branch-right3", fsize=20, fgcolor="#009000")
bd = faces.TextFace("branch-bottom", fsize=11, fgcolor="#909000")
ud = faces.TextFace("branch-top", fsize=11, fgcolor="#099000")
t1 = faces.TextFace("Aligned", fsize=11, fgcolor="#099000")
t3 = faces.TextFace("pus", fsize=11, fgcolor="#099000")
t2 = faces.ImgFace("/home/jhuerta/_Devel/test/doc/tutorial/examples/human.png")
def mylayout(node):
    # If node is a leaf, add the nodes name and a its scientific
    # name
    node.img_style["size"]=random.sample(range(20),1)[0]
    if node.is_leaf():
        faces.add_face_to_node(t1, node, column=0, position="aligned")
        faces.add_face_to_node(t3, node, column=1, position="aligned")
        faces.add_face_to_node(t2, node, column=2, position="aligned")
        faces.add_face_to_node(t1, node, column=3, position="aligned")
        return
        faces.add_face_to_node(t1, node, column=0, position="aligned")
        faces.add_face_to_node(t1, node, column=0, position="aligned")
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
        faces.add_face_to_node(rs1, node, column=1, position="branch-right")

        #faces.add_face_to_node(rs, node, column=1, position="branch-right")
        #faces.add_face_to_node(rs, node, column=1, position="branch-right")


        #faces.add_face_to_node(t1, node, column=1, position="branch-right")

        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")
        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")
        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")
        #faces.add_face_to_node(t1, node, column=1, position="branch-bottom")

def mylayout2(node):
    node.img_style["size"]=10
    if node.is_leaf():
        return

I = TreeImageProperties()
I.header.add_face_to_aligned_column(0, t2)
I.header.add_face_to_aligned_column(1, t2)
I.header.add_face_to_aligned_column(2, t2)
I.header.add_face_to_aligned_column(3, t2)

t = Tree()
t.dist = 0
t.populate(5)
t.show(mylayout, image_properties=I)
