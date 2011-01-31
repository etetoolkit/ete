import unittest
import random
from ete_dev import Tree, faces
from ete_dev.treeview.main import TreeImage, NodeStyleDict


class TestTreeview(unittest.TestCase):
    rF1 = faces.TextFace("branch-right1")
    rF2 = faces.TextFace("branch-right2", fsize=20)
    rF3 = faces.TextFace("branch-right3", fsize=20, fgcolor="#009000")
    
    nameF = faces.TextFace("name", fsize=11, fgcolor="#909000")
    distF = faces.TextFace("dist", fsize=8)
    
    topF = faces.TextFace("branch-top1", fsize=11, fgcolor="#099000")
    downF = faces.TextFace("branch-down1", fsize=11, fgcolor="#099000")
    
    headerF = faces.TextFace("header_up", fsize=11, fgcolor="#099000")
    headerF.margin_right = 10
    footF = faces.TextFace("header_up", fsize=11, fgcolor="#099000")
    fixedF = faces.TextFace("FIXED", fsize=11, fgcolor="#099000")

    def test(self):
        # Text faces

        I = TreeImage()
        I.mode = "rect"
        I.aligned_header.add_face(self.headerF, 0)
        I.aligned_header.add_face(self.headerF, 1)
        I.aligned_header.add_face(self.headerF, 2)
        I.aligned_header.add_face(self.headerF, 3)

        I.aligned_foot.add_face(self.footF, 0)
        I.aligned_foot.add_face(self.footF, 1)
        I.aligned_foot.add_face(self.footF, 2)
        I.aligned_foot.add_face(self.footF, 3) 
        I.draw_aligned_faces_as_grid = True
        t = Tree()
        t.dist = 0
        t.populate(10)

        style = NodeStyleDict()
        style["fgcolor"] = "#ff0000"
        style["size"] = 20
        style.add_fixed_face(self.fixedF, "branch-right", 0)
        t.img_style = style
        
        #t.render("./test.svg", layout=mylayout, img_properties=I)
        t.show(mylayout, img_properties=I)
        t.show(mylayout2, img_properties=I)


def mylayout(node):
    T = TestTreeview
    node.img_style["size"]=random.sample(range(4,30),1)[0]
    if node.is_leaf():
        faces.add_face_to_node(T.nameF, node, column=0, position="aligned")
        faces.add_face_to_node(T.nameF, node, column=2, position="aligned")
        faces.add_face_to_node(T.nameF, node, column=3, position="aligned")
    else:
        faces.add_face_to_node(T.topF, node, column=1, position="branch-top")
        faces.add_face_to_node(T.topF, node, column=1, position="branch-top")
        faces.add_face_to_node(T.topF, node, column=1, position="branch-top")
        faces.add_face_to_node(T.topF, node, column=1, position="branch-top")
        faces.add_face_to_node(T.downF, node, column=1, position="branch-bottom")
        faces.add_face_to_node(T.downF, node, column=1, position="branch-bottom")
        faces.add_face_to_node(T.rF1, node, column=1, position="branch-right")
        faces.add_face_to_node(T.rF2, node, column=1, position="branch-right")
        faces.add_face_to_node(T.rF3, node, column=2, position="branch-right")


def mylayout2(node):
    node.img_style["size"]=10
    if node.is_leaf():
        return

if __name__ == '__main__':
    unittest.main()
