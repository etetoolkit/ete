from ... import Tree, faces, AttrFace, TreeStyle, NodeStyle

def layout(node):
    # If node is a leaf, add the nodes name and a its scientific name
    if node.is_leaf():
        faces.add_face_to_node(AttrFace("name"), node, column=0)

def get_example_tree():

    t = Tree()
    t.populate(8)

    # Node style handling is no longer limited to layout functions. You
    # can now create fixed node styles and use them many times, save them
    # or even add them to nodes before drawing (this allows to save and
    # reproduce an tree image design)

    # Set bold red branch to the root node
    style = NodeStyle()
    style["fgcolor"] = "#0f0f0f"
    style["size"] = 0
    style["vt_line_color"] = "#ff0000"
    style["hz_line_color"] = "#ff0000"
    style["vt_line_width"] = 8
    style["hz_line_width"] = 8
    style["vt_line_type"] = 0 # 0 solid, 1 dashed, 2 dotted
    style["hz_line_type"] = 0
    t.set_style(style)

    #Set dotted red lines to the first two branches
    style1 = NodeStyle()
    style1["fgcolor"] = "#0f0f0f"
    style1["size"] = 0
    style1["vt_line_color"] = "#ff0000"
    style1["hz_line_color"] = "#ff0000"
    style1["vt_line_width"] = 2
    style1["hz_line_width"] = 2
    style1["vt_line_type"] = 2 # 0 solid, 1 dashed, 2 dotted
    style1["hz_line_type"] = 2
    t.children[0].img_style = style1
    t.children[1].img_style = style1

    # Set dashed blue lines in all leaves
    style2 = NodeStyle()
    style2["fgcolor"] = "#000000"
    style2["shape"] = "circle"
    style2["vt_line_color"] = "#0000aa"
    style2["hz_line_color"] = "#0000aa"
    style2["vt_line_width"] = 2
    style2["hz_line_width"] = 2
    style2["vt_line_type"] = 1 # 0 solid, 1 dashed, 2 dotted
    style2["hz_line_type"] = 1
    for l in t.iter_leaves():
        l.img_style = style2

    ts = TreeStyle()
    ts.layout_fn = layout
    ts.show_leaf_name = False

    return t, ts

if __name__ == "__main__":
    t, ts = get_example_tree()
    t.show(tree_style=ts)
    #t.render("node_style.png", w=400, tree_style=ts)

