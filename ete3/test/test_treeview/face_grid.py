from ... import Tree, TextFace, NodeStyle, TreeStyle

def get_example_tree():
    t = Tree("((a,b),c);")

    right_c0_r0 = TextFace("right_col0_row0")
    right_c0_r1 = TextFace("right_col0_row1")
    right_c1_r0 = TextFace("right_col1_row0")
    right_c1_r1 = TextFace("right_col1_row1")
    right_c1_r2 = TextFace("right_col1_row2")

    top_c0_r0 = TextFace("top_col0_row0")
    top_c0_r1 = TextFace("top_col0_row1")

    bottom_c0_r0 = TextFace("bottom_col0_row0")
    bottom_c1_r0 = TextFace("bottom_col1_row0")

    aligned_c0_r0 = TextFace("aligned_col0_row0")
    aligned_c0_r1 = TextFace("aligned_col0_row1")

    aligned_c1_r0 = TextFace("aligned_col1_row0")
    aligned_c1_r1 = TextFace("aligned_col1_row1")


    t.add_face(right_c0_r1, column=1, position="branch-right")
    t.add_face(right_c0_r0, column=0, position="branch-right")

    t.add_face(right_c1_r2, column=2, position="branch-right")
    t.add_face(right_c1_r1, column=1, position="branch-right")
    t.add_face(right_c1_r0, column=0, position="branch-right")

    t.add_face(top_c0_r1, column=1, position="branch-top")
    t.add_face(top_c0_r0, column=0, position="branch-top")

    t.add_face(bottom_c0_r0, column=0, position="branch-bottom")
    t.add_face(bottom_c1_r0, column=1, position="branch-bottom")

    for leaf in t.iter_leaves():
        leaf.add_face(aligned_c0_r1, 0, "aligned")
        leaf.add_face(aligned_c0_r0, 0, "aligned")
        leaf.add_face(aligned_c1_r1, 0, "aligned")
        leaf.add_face(aligned_c1_r0, 0, "aligned")

    return t, TreeStyle()

if __name__ == "__main__":
    t, ts = get_example_tree()
    t.show()
