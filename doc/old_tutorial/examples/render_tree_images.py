from ete3 import Tree
t = Tree()
# Generate a random tree with 50 leaves
t.populate(50)
# Render  tree in png and pdf format using the default size
t.render("./random_tree.png")
t.render("./random_tree.pdf")
# Render tree in pdf setting a custom width. height will be imputed
t.render("./random_tree.pdf", w=300)
# Render tree in pdf setting a custom height. Width will be imputed
t.render("./random_tree.pdf", h=600)
# Render tree in pdf setting a custom width and height
t.render("./random_tree.pdf", w=300, h=300)
