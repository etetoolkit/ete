import unittest
import random
from ete_dev import Tree, faces, TreeImageProperties, NodeStyleDict

class TestTreeview(unittest.TestCase):
    rF1 = faces.TextFace("branch-right1")
    rF2 = faces.TextFace("branch-right2", fsize=20)
    rF3 = faces.TextFace("branch-right3", fsize=20, fgcolor="#009000")
    
    nameF = faces.TextFace("name", fsize=11, fgcolor="#909000")
    distF = faces.TextFace("dist", fsize=8)
    
    topF = faces.TextFace("branch-top1", fsize=11, fgcolor="#099000")
    downF = faces.TextFace("branch-down1", fsize=11, fgcolor="#099000")
    
    headerF = faces.TextFace("header_up", fsize=11, fgcolor="#099000")
    footF = faces.TextFace("header_up", fsize=11, fgcolor="#099000")
    fixedF = faces.TextFace("FIXED", fsize=11, fgcolor="#099000")

    def test(self):
        # Text faces

        I = TreeImageProperties()
        I.aligned_face_header.add_face_to_aligned_column(0, self.headerF)
        I.aligned_face_header.add_face_to_aligned_column(1, self.headerF)
        I.aligned_face_header.add_face_to_aligned_column(2, self.headerF)
        I.aligned_face_header.add_face_to_aligned_column(3, self.headerF)

        I.aligned_face_foot.add_face_to_aligned_column(0, self.footF)
        I.aligned_face_foot.add_face_to_aligned_column(1, self.footF)
        I.aligned_face_foot.add_face_to_aligned_column(2, self.footF)
        I.aligned_face_foot.add_face_to_aligned_column(3, self.footF)
        I.draw_lines_from_leaves_to_aligned_faces = True
        I.line_from_leaves_to_aligned_faces_type = 2
 
        I.draw_image_border = True
        I.draw_aligned_faces_as_grid = False

        t = Tree()
        t.dist = 0
        t.populate(10)

        style = NodeStyleDict()
        style["fgcolor"] = "#ff0000"
        style["size"] = 20
        style.add_fixed_face(self.fixedF, "branch-right", 0)
        t.img_style = style
        
        t.show(mylayout, image_properties=I)
        t.show(mylayout2, image_properties=I)


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
