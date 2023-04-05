# Import Tree instance and faces module
from ... import Tree, faces, TreeStyle

# Loads an example tree
nw = """
(((Dre:0.008339,Dme:0.300613)1.000000:0.596401,
(Cfa:0.640858,Hsa:0.753230)1.000000:0.182035)1.000000:0.106234,
((Dre:0.271621,Cfa:0.046042)1.000000:0.953250,
(Hsa:0.061813,Mms:0.110769)1.000000:0.204419)1.000000:0.973467);
"""
t = Tree(nw)

# You can create any random tree containing the same leaf names, and
# layout will work equally
#
# t = Tree()
# Creates a random tree with 8 leaves using a given set of names
# t.populate(8, ["Dme", "Dre", "Hsa", "Ptr", "Cfa", "Mms"])

# Set the path in which images are located
img_path = "./"
# Create faces based on external images
humanFace = faces.ImgFace(img_path+"human.png")
mouseFace = faces.ImgFace(img_path+"mouse.png")
dogFace = faces.ImgFace(img_path+"dog.png")
chimpFace = faces.ImgFace(img_path+"chimp.png")
fishFace = faces.ImgFace(img_path+"fish.png")
flyFace = faces.ImgFace(img_path+"fly.png")

# Create a faces ready to read the name attribute of nodes
#nameFace = faces.TextFace(open("text").readline().strip(), fsize=20, fgcolor="#009000")
nameFace = faces.AttrFace("name", fsize=20, fgcolor="#009000")

# Create a conversion between leaf names and real names
code2name = {
        "Dre":"Drosophila melanogaster",
        "Dme":"Danio rerio",
        "Hsa":"Homo sapiens",
        "Ptr":"Pan troglodytes",
        "Mms":"Mus musculus",
        "Cfa":"Canis familiaris"
        }

# Creates a dictionary with the descriptions of each leaf name
code2desc = {
        "Dre":"""The zebrafish, also known as Danio rerio,
is a tropical freshwater fish belonging to the
minnow family (Cyprinidae).""",
        "Dme":"""True flies are insects of the order Diptera,
possessing a single pair of wings on the
mesothorax and a pair of halteres, derived from
the hind wings, on the metathorax""",
        "Hsa":"""A human is a member of a species
of bipedal primates in the family Hominidae.""",
        "Ptr":"""Chimpanzee, sometimes colloquially
chimp, is the common name for the
two extant species of ape in the genus Pan.""",
        "Mms":"""A mouse is a small mammal belonging to the
order of rodents.""",
        "Cfa": """The dog (Canis lupus familiaris) is a
domesticated subspecies of the Gray Wolf,
a member of the Canidae family of the
orderCarnivora."""
        }

# Creates my own layout function. I will use all previously created
# faces and will set different node styles depending on the type of
# node.
def mylayout(node):
    # If node is a leaf, add the nodes name and a its scientific
    # name
    if node.is_leaf():
        # Add an static face that handles the node name
        faces.add_face_to_node(nameFace, node, column=0)
        # We can also create faces on the fly
        longNameFace = faces.TextFace(code2name[node.name])
        faces.add_face_to_node(longNameFace, node, column=0)

        # text faces support multiline. We add a text face
        # with the whole description of each leaf.
        descFace = faces.TextFace(code2desc[node.name], fsize=10)
        descFace.margin_top = 10
        descFace.margin_bottom = 10
        descFace.border.margin = 1

        # Note that this faces is added in "aligned" mode
        faces.add_face_to_node(descFace, node, column=0, aligned=True)

        # Sets the style of leaf nodes
        node.img_style["size"] = 12
        node.img_style["shape"] = "circle"
    #If node is an internal node
    else:
        # Sets the style of internal nodes
        node.img_style["size"] = 6
        node.img_style["shape"] = "circle"
        node.img_style["fgcolor"] = "#000000"

    # If an internal node contains more than 4 leaves, add the
    # images of the represented species sorted in columns of 2
    # images max.
    if len(node)>=4:
        col = 0
        for i, name in enumerate(set(node.get_leaf_names())):
            if i>0 and i%2 == 0:
                col += 1
            # Add the corresponding face to the node
            if name.startswith("Dme"):
                faces.add_face_to_node(flyFace, node, column=col)
            elif name.startswith("Dre"):
                faces.add_face_to_node(fishFace, node, column=col)
            elif name.startswith("Mms"):
                faces.add_face_to_node(mouseFace, node, column=col)
            elif name.startswith("Ptr"):
                faces.add_face_to_node(chimpFace, node, column=col)
            elif name.startswith("Hsa"):
                faces.add_face_to_node(humanFace, node, column=col)
            elif name.startswith("Cfa"):
                faces.add_face_to_node(dogFace, node, column=col)

            # Modifies this node's style
            node.img_style["size"] = 16
            node.img_style["shape"] = "sphere"
            node.img_style["fgcolor"] = "#AA0000"

    # If leaf is "Hsa" (homo sapiens), highlight it using a
    # different background.
    if node.is_leaf() and node.name.startswith("Hsa"):
        node.img_style["bgcolor"] = "#9db0cf"

# And, finally, Visualize the tree using my own layout function
ts = TreeStyle()
ts.layout_fn = mylayout
t.render("img_faces.png", w=600, tree_style = ts)

