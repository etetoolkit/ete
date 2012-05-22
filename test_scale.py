import sys
sys.path.insert(0, "./")
from ete_dev import Tree, TreeStyle, faces

def layout(node):
    node.img_style["size"] = 5
    node.img_style["hz_line_width"] = 0
    node.img_style["vt_line_width"] = 0
    if node.is_leaf():
        f = faces.AttrFace("name", fsize=20)
        faces.add_face_to_node(f, node, 0, position="aligned")
        
        f = faces.AttrFace("name", fsize=20)
        faces.add_face_to_node(f, node, 0, position="branch-right")
        

ts = TreeStyle()
ts.mode = "c"
ts.layout_fn = layout 
ts.show_leaf_name = False
ts.draw_guiding_lines = False
t = Tree()
t.populate(1000)
t.write(outfile="test.nw")
t.show(tree_style=ts)


    
        