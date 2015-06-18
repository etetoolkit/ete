from ete3 import Tree, TextFace, NodeStyle, TreeStyle

t = Tree("((a,b),c);")

right_c0_r0 = TextFace("right_col0_row0")
right_c0_r1 = TextFace("right_col0_row1")
right_c1_r0 = TextFace("right_col1_row0")
right_c1_r1 = TextFace("right_col1_row1")
right_c1_r2 = TextFace("right_col1_row2")

top_c0_r0 = TextFace("top_col0_row0")
top_c0_r1 = TextFace("top_col0_row1")

bottom_c0_r0 = TextFace("bottom_col0_row0")
bottom_c0_r1 = TextFace("bottom_col0_row1")

aligned_c0_r0 = TextFace("aligned_col0_row0")
aligned_c0_r1 = TextFace("aligned_col0_row1")

aligned_c1_r0 = TextFace("aligned_col1_row0")
aligned_c1_r1 = TextFace("aligned_col1_row1")

all_faces = [right_c0_r0, right_c0_r1, right_c1_r0, right_c1_r1, right_c1_r2, top_c0_r0, \
     top_c0_r1, bottom_c0_r0, bottom_c0_r1, aligned_c0_r0, aligned_c0_r1,\
     aligned_c1_r0, aligned_c1_r1]

# set a border in all faces
for f in all_faces:
    f.margin_border.width = 1
    f.margin_bottom = 5
    f.margin_top = 5
    f.margin_right = 10


t.add_face(right_c0_r0, column=0, position="branch-right")
t.add_face(right_c0_r1, column=0, position="branch-right")

t.add_face(right_c1_r0, column=1, position="branch-right")
t.add_face(right_c1_r1, column=1, position="branch-right")
t.add_face(right_c1_r2, column=1, position="branch-right")

t.add_face(top_c0_r0, column=0, position="branch-top")
t.add_face(top_c0_r1, column=0, position="branch-top")

t.add_face(bottom_c0_r0, column=0, position="branch-bottom")
t.add_face(bottom_c0_r1, column=0, position="branch-bottom")

a = t&"a"
a.set_style(NodeStyle())
a.img_style["bgcolor"] = "lightgreen"

b = t&"b"
b.set_style(NodeStyle())
b.img_style["bgcolor"] = "indianred"

c = t&"c"
c.set_style(NodeStyle())
c.img_style["bgcolor"] = "lightblue"

t.set_style(NodeStyle())
t.img_style["bgcolor"] = "lavender"
t.img_style["size"] = 12

for leaf in t.iter_leaves():
    leaf.img_style["size"] = 12
    leaf.add_face(right_c0_r0, 0, "branch-right")
    leaf.add_face(aligned_c0_r1, 0, "aligned")
    leaf.add_face(aligned_c0_r0, 0, "aligned")
    leaf.add_face(aligned_c1_r1, 1, "aligned")
    leaf.add_face(aligned_c1_r0, 1, "aligned")

ts = TreeStyle()
ts.show_scale = False
t.render("face_positions.png", w=800, tree_style=ts)
