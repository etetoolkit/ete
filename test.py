from ete_dev import Tree, faces, TreeImageProperties, NodeStyleDict
import random

rs1 = faces.TextFace("branch-right1", fsize=20, fgcolor="#009000")

rs1.margin_top = 10
rs1.margin_top = 50
rs1.margin_left = 40
rs1.margin_right = 40

rs2 = faces.TextFace("branch-right2", fsize=20, fgcolor="#009000")
rs3 = faces.TextFace("branch-right3", fsize=20, fgcolor="#009000")
bd  = faces.TextFace("branch-bottom", fsize=11, fgcolor="#909000")
ud  = faces.TextFace("branch-top", fsize=11, fgcolor="#099000")
t1  = faces.TextFace("header_up", fsize=11, fgcolor="#099000")
t2  = faces.TextFace("header_down", fsize=11, fgcolor="#099000")

fixed = faces.TextFace("FIXED", fsize=11, fgcolor="#099000")

content = faces.AttrFace("name", fsize=12, fgcolor="#099000")
image = faces.ImgFace("/home/jhuerta/_Devel/test/doc/tutorial/examples/human.png")
def mylayout(node):
    # If node is a leaf, add the nodes name and a its scientific
    # name
    node.img_style["size"]=random.sample(range(20),1)[0]
    if node.is_leaf():
        faces.add_face_to_node(content, node, column=0, position="aligned")
        faces.add_face_to_node(content, node, column=1, position="aligned")
 
        faces.add_face_to_node(content, node, column=3, position="aligned")
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

        faces.add_face_to_node(rs2, node, column=1, position="branch-right")
        faces.add_face_to_node(rs1, node, column=1, position="branch-right")
        faces.add_face_to_node(rs2, node, column=1, position="branch-right")
        faces.add_face_to_node(rs2, node, column=1, position="branch-right")
        faces.add_face_to_node(rs2, node, column=1, position="branch-right")
        faces.add_face_to_node(rs2, node, column=1, position="branch-right")

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
I.aligned_header.add_face(t1, 0)
I.aligned_header.add_face(t1, 0)
I.aligned_header.add_face(t1, 0)
I.aligned_header.add_face(t1, 0)

I.aligned_foot.add_face(t2, 0)
I.aligned_foot.add_face(t2, 1)
I.aligned_foot.add_face(t2, 2)
I.aligned_foot.add_face(t2, 3)
I.draw_guidelines= True
I.guidelines_type = 2
I.draw_image_border = True
I.draw_aligned_faces_as_grid = True

t = Tree()
t.dist = 0
t.populate(5)


style = NodeStyleDict()
style["fgcolor"] = "#ff0000"
style["bgcolor"] = "#aaaaaa"
style["size"] = 20
style.add_fixed_face(fixed, "branch-right", 0)
t.img_style = style
t.render("./test.svg", layout=mylayout, img_properties=I)
t.show(mylayout, img_properties=I)
t.show(mylayout2, img_properties=I)
