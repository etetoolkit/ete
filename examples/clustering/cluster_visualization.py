# Import Tree instance and faces module
from ete3 import ClusterTree
# Example of a minimalistic numerical matrix. It is encoded as a text
# string for convenience, but it usally be loaded from a text file.
matrix = """
#Names\tcol1\tcol2\tcol3\tcol4\tcol5\tcol6\tcol7
A\t-1.23\t-0.81\t1.79\t0.78\t-0.42\t-0.69\t0.58
B\t-1.76\t-0.94\t1.16\t0.36\t0.41\t-0.35\t1.12
C\t-2.19\t0.13\t0.65\t-0.51\t0.52\t1.04\t0.36
D\t-1.22\t-0.98\t0.79\t-0.76\t-0.29\t1.54\t0.93
E\t-1.47\t-0.83\t0.85\t0.07\t-0.81\t1.53\t0.65
F\t-1.04\t-1.11\t0.87\t-0.14\t-0.80\t1.74\t0.48
G\t-1.57\t-1.17\t1.29\t0.23\t-0.20\t1.17\t0.26
H\t-1.53\t-1.25\t0.59\t-0.30\t0.32\t1.41\t0.77
"""
print "Example numerical matrix"
print matrix
# #Names  col1    col2    col3    col4    col5    col6    col7
# A       -1.23   -0.81   1.79    0.78    -0.42   -0.69   0.58
# B       -1.76   -0.94   1.16    0.36    0.41    -0.35   1.12
# C       -2.19   0.13    0.65    -0.51   0.52    1.04    0.36
# D       -1.22   -0.98   0.79    -0.76   -0.29   1.54    0.93
# E       -1.47   -0.83   0.85    0.07    -0.81   1.53    0.65
# F       -1.04   -1.11   0.87    -0.14   -0.80   1.74    0.48
# G       -1.57   -1.17   1.29    0.23    -0.20   1.17    0.26
# H       -1.53   -1.25   0.59    -0.30   0.32    1.41    0.77
#
#
# We load a tree structure whose leaf nodes correspond to rows in the
# numerical matrix. We use the text_array argument to link the tree
# with numerical matrix.
t = ClusterTree("(((A,B),(C,(D,E))),(F,(G,H)));", text_array=matrix)
t.show("heatmap")
t.show("cluster_cbars")
t.show("cluster_bars")
t.show("cluster_lines")
