import sys

from ete_dev import Tree, faces, TreeStyle, NodeStyle

def mylayout(node):
    # If node is a leaf, add the nodes name and a its scientific
    # name
    if node.is_leaf():
        faces.add_face_to_node(aligned, node, column=0, position="aligned")
        faces.add_face_to_node(aligned, node, column=1, position="aligned")
        faces.add_face_to_node(aligned, node, column=3, position="aligned")
    else:
        faces.add_face_to_node(bt, node, column=0, position="branch-top")
        faces.add_face_to_node(bb, node, column=0, position="branch-bottom")
        faces.add_face_to_node(br1, node, column=0, position="branch-right")
        faces.add_face_to_node(rs1, node, column=0, position="branch-right")
        faces.add_face_to_node(br2, node, column=0, position="branch-right")

t = Tree()
t.populate(int(sys.argv[1]))

# Margins, alignment, border and opacity can now be set for any face
rs1 = faces.TextFace("branch-right1-with-margins", fsize=20, fgcolor="#009000")
rs1.margin_top = 10
rs1.margin_bottom = 50
rs1.margin_left = 40
rs1.margin_right = 40
rs1.margin_border = True
rs1.border = True
rs1.opacity = 0.6
rs1.hz_align = 2 # 0 left, 1 center, 2 right
rs1.vt_align = 1 # 0 left, 1 center, 2 right

br1 = faces.TextFace("branch-right2", fsize=12, fgcolor="#009000")
br2 = faces.TextFace("branch-right3", fsize=12, fgcolor="#009000")

# New face positions (branch-top and branch-bottom)
bb = faces.TextFace("branch-bottom", fsize=8, fgcolor="#909000")
bt = faces.TextFace("branch-top", fsize=6, fgcolor="#099000")

# And faces can also be used as headers or foot notes of aligned
# columns
t1 = faces.TextFace("header_up", fsize=12, fgcolor="#099000")
t2 = faces.TextFace("header_down", fsize=12, fgcolor="#099000")

# Attribute faces can now contain prefix and suffix fixed text
aligned = faces.AttrFace("name", fsize=12, fgcolor="#099000", text_prefix="name=(", text_suffix=")")
# horizontal and vertical alignment per face
aligned.hz_align = 1 # 0 left, 1 center, 2 right
aligned.vt_align = 1 

# Node style handling is no longer limited to layout functions. You
# can now create fixed node styles and use them many times, save them
# or even add them to nodes before drawing (this allows to save and
# reproduce an tree image design)
style = NodeStyle()
style["fgcolor"] = "#ff0000"
style["shape"] = "square"
style["vt_line_color"] = "#ff0000"
# add a face to the style. This face will be render in any node
# associated to the style.
fixed = faces.TextFace("FIXED", fsize=11, fgcolor="#099000")
style.add_fixed_face(fixed, "branch-right", 0)
# Bind the precomputed style to the root node 
t.img_style = style


# ETE 2.1 has now support for general image properties 
I = TreeStyle()
# You can add faces to the tree image (without any node
# associated). They will be used as headers and foot notes of the
# aligned columns (aligned faces)
I.aligned_header.add_face(t1, column = 0)
I.aligned_header.add_face(t1, 1)
I.aligned_header.add_face(t1, 2)
I.aligned_header.add_face(t1, 3)
t1.hz_align = 1 # 0 left, 1 center, 2 right 
t1.margin_border = True

I.aligned_foot.add_face(t2, column = 0)
I.aligned_foot.add_face(t2, 1)
I.aligned_foot.add_face(t2, 2)
I.aligned_foot.add_face(t2, 3)
t2.hz_align = 1

# Set tree image style. Note that aligned header and foot is only
# visible in "rect" mode.

I.mode =  "circular" # "rect" # or "circular"
t.show(mylayout, img_properties=I)
# t.render("./test.svg", layout=mylayout, img_properties=I)
