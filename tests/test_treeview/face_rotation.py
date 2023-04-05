from ... import Tree, TreeStyle, add_face_to_node, TextFace

from random import randint

def rotation_layout(node):
    if node.is_leaf():
        F = TextFace(node.name, tight_text=True)
        F.rotation = randint(0, 360)
        add_face_to_node(TextFace("third" ), node, column=8, position="branch-right")
        add_face_to_node(TextFace("second" ), node, column=2, position="branch-right")
        add_face_to_node(F, node, column=0, position="branch-right")

        F.border.width = 1
        F.inner_border.width = 1

def get_example_tree():
    t = Tree()
    t.populate(10)
    ts = TreeStyle()
    ts.rotation = 45
    ts.show_leaf_name = False
    ts.layout_fn = rotation_layout

    return t, ts

if __name__ == "__main__":
    t, ts = get_example_tree()
    t.show(tree_style=ts)


