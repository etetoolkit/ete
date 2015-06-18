from ete3 import ClusterTree, TreeStyle, AttrFace, ProfileFace, TextFace
from ete3.treeview.faces import add_face_to_node

# To operate with numbers efficiently
import numpy

PATH = "./"
# Loads tree and array
t = ClusterTree(PATH+"diauxic.nw", PATH+"diauxic.array")

# nodes are linked to the array table
array =  t.arraytable

# Calculates some stats on the matrix. Needed to establish the color
# gradients.
matrix_dist = [i for r in xrange(len(array.matrix))\
               for i in array.matrix[r] if numpy.isfinite(i)]
matrix_max = numpy.max(matrix_dist)
matrix_min = numpy.min(matrix_dist)
matrix_avg = matrix_min+((matrix_max-matrix_min)/2)

# Creates a profile face that will represent node's profile as a
# heatmap
profileFace  = ProfileFace(matrix_max, matrix_min, matrix_avg, \
                                         200, 14, "heatmap")
cbarsFace = ProfileFace(matrix_max,matrix_min,matrix_avg,200,70,"cbars")
nameFace = AttrFace("name", fsize=8)
# Creates my own layout function that uses previous faces
def mylayout(node):
    # If node is a leaf
    if node.is_leaf():
        # And a line profile
        add_face_to_node(profileFace, node, 0, aligned=True)
        node.img_style["size"]=0
        add_face_to_node(nameFace, node, 1, aligned=True)

    # If node is internal
    else:
        # If silhouette is good, creates a green bubble
        if node.silhouette>0:
            validationFace = TextFace("Silh=%0.2f" %node.silhouette,
                                      "Verdana", 10, "#056600")
            node.img_style["fgcolor"]="#056600"
        # Otherwise, use red bubbles
        else:
            validationFace = TextFace("Silh=%0.2f" %node.silhouette,
                                      "Verdana", 10, "#940000")
            node.img_style["fgcolor"]="#940000"

        # Sets node size proportional to the silhouette value.
        node.img_style["shape"]="sphere"
        if node.silhouette<=1 and node.silhouette>=-1:
            node.img_style["size"]= 15+int((abs(node.silhouette)*10)**2)

        # If node is very internal, draw also a bar diagram
        # with the average expression of the partition
        add_face_to_node(validationFace, node, 0)
        if len(node)>100:
            add_face_to_node(cbarsFace, node, 1)

# Use my layout to visualize the tree
ts = TreeStyle()
ts.layout_fn = mylayout
t.show(tree_style=ts)
