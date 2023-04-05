from ... import Tree, faces, TreeStyle, NodeStyle

def get_example_tree():
    t = Tree()
    t.populate(10)

    # Margins, alignment, border, background and opacity can now be set for any face
    rs1 = faces.TextFace("branch-right\nmargins&borders",
                         fsize=12, fgcolor="#009000")
    rs1.margin_top = 10
    rs1.margin_bottom = 50
    rs1.margin_left = 40
    rs1.margin_right = 40
    rs1.border.width = 1
    rs1.background.color = "lightgreen"
    rs1.inner_border.width = 0
    rs1.inner_border.line_style = 1
    rs1.inner_border.color= "red"
    rs1.opacity = 0.6
    rs1.hz_align = 2 # 0 left, 1 center, 2 right
    rs1.vt_align = 1 # 0 left, 1 center, 2 right

    br1 = faces.TextFace("branch-right1", fsize=12, fgcolor="#009000")
    br2 = faces.TextFace("branch-right3", fsize=12, fgcolor="#009000")

    # New face positions (branch-top and branch-bottom)
    bb = faces.TextFace("branch-bottom 1", fsize=8, fgcolor="#909000")
    bb2 = faces.TextFace("branch-bottom 2", fsize=8, fgcolor="#909000")
    bt = faces.TextFace("branch-top 1", fsize=6, fgcolor="#099000")

    # And faces can also be used as headers or foot notes of aligned
    # columns
    t1 = faces.TextFace("Header Face", fsize=12, fgcolor="#aa0000")
    t2 = faces.TextFace("Footer Face", fsize=12, fgcolor="#0000aa")

    # Attribute faces can now contain prefix and suffix fixed text
    aligned = faces.AttrFace("name", fsize=12, fgcolor="RoyalBlue",
                             text_prefix="Aligned (", text_suffix=")")
    # horizontal and vertical alignment per face
    aligned.hz_align = 1 # 0 left, 1 center, 2 right
    aligned.vt_align = 1

    # Node style handling is no longer limited to layout functions. You
    # can now create fixed node styles and use them many times, save them
    # or even add them to nodes before drawing (this allows to save and
    # reproduce an tree image design)
    style = NodeStyle()
    style["fgcolor"] = "Gold"
    style["shape"] = "square"
    style["size"] = 15
    style["vt_line_color"] = "#ff0000"
    t.set_style(style)
    # add a face to the style. This face will be render in any node
    # associated to the style.
    fixed = faces.TextFace("FIXED branch-right", fsize=11, fgcolor="blue")
    t.add_face(fixed, column=1, position="branch-right")
    # Bind the precomputed style to the root node

    # ETE 2.1 has now support for general image properties
    ts = TreeStyle()

    # You can add faces to the tree image (without any node
    # associated). They will be used as headers and foot notes of the
    # aligned columns (aligned faces)
    ts.aligned_header.add_face(t1, column = 0)
    ts.aligned_header.add_face(t1, 1)
    ts.aligned_header.add_face(t1, 2)
    ts.aligned_header.add_face(t1, 3)
    t1.hz_align = 1 # 0 left, 1 center, 2 right
    t1.border.width = 1

    ts.aligned_foot.add_face(t2, column = 0)
    ts.aligned_foot.add_face(t2, 1)
    ts.aligned_foot.add_face(t2, 2)
    ts.aligned_foot.add_face(t2, 3)
    t2.hz_align = 1

    # Set tree image style. Note that aligned header and foot is only
    # visible in "rect" mode.

    ts.mode =  "r"
    ts.scale = 10
    for node in t.traverse():
        # If node is a leaf, add the nodes name and a its scientific
        # name
        if node.is_leaf():
            node.add_face(aligned, column=0, position="aligned")
            node.add_face(aligned, column=1, position="aligned")
            node.add_face(aligned, column=3, position="aligned")
        else:
            node.add_face(bt, column=0, position="branch-top")
            node.add_face(bb, column=0, position="branch-bottom")
            node.add_face(bb2, column=0, position="branch-bottom")
            node.add_face(br1, column=0, position="branch-right")
            node.add_face(rs1, column=0, position="branch-right")
            node.add_face(br2, column=0, position="branch-right")

    return t, ts

if __name__ == "__main__":
    t, ts = get_example_tree()
    t.show(tree_style=ts)

