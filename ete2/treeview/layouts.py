# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE).
# http://ete.cgenomics.org
#
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
import numpy
import faces

def basic(node):
    if node.is_leaf():
        node.img_style["size"]=1
        node.img_style["shape"] = "circle"
        faces.add_face_to_node(faces.AttrFace("name","Arial",10,"#4f8f0f",None), node, 0 )

def phylogeny(node):
    leaf_color = "#000000"
    node.img_style["shape"] = "circle"
    if hasattr(node,"evoltype"):
        if node.evoltype == 'D':
            node.img_style["fgcolor"] = "#1d176e"
            node.img_style["hz_line_color"] = "#1d176e"
            node.img_style["vt_line_color"] = "#1d176e"
        elif node.evoltype == 'S':
            node.img_style["fgcolor"] = "#FF0000"
            node.img_style["line_color"] = "#FF0000"
        elif node.evoltype == 'L':
            node.img_style["fgcolor"] = "#777777"
            node.img_style["vt_line_color"] = "#777777"
            node.img_style["hz_line_color"] = "#777777"
            node.img_style["line_type"] = 1
            leaf_color = "#777777"

    if node.is_leaf():
        node.img_style["shape"] = "square"
        node.img_style["size"] = 4
        node.img_style["fgcolor"] = leaf_color
        faces.add_face_to_node( faces.AttrFace("name","Arial",11,leaf_color,None), node, 0 )
        if hasattr(node,"sequence"):
            SequenceFace =  faces.SequenceFace(node.sequence,"aa",13)
            faces.add_face_to_node(SequenceFace, node, 1, aligned=True)
    else:
        node.img_style["size"] = 6

def heatmap(node):
    square_size = 10
    # Extras node info
    node.collapsed = False

    # Color and style
    node.img_style["fgcolor"] = "#3333FF"
    node.img_style["size"] =  0

    ncols = node.arraytable.matrix.shape[1]

    matrix_max = numpy.max(node.arraytable._matrix_max)
    matrix_min = numpy.min(node.arraytable._matrix_min)
    matrix_avg = matrix_min+((matrix_max-matrix_min)/2)
    ProfileFace = faces.ProfileFace(\
      matrix_max,\
        matrix_min,\
        matrix_avg,\
        square_size*ncols,\
        square_size,\
        "heatmap")
    ProfileFace.ymargin=0
    if node.is_leaf():
        # Set colors
        faces.add_face_to_node(ProfileFace, node, 0, aligned=True )




def cluster_cbars(node):
    # Extras node info
    node.collapsed = False
    # Color and style
    node.img_style["fgcolor"] = "#3333FF"
    node.img_style["size"] =  4
    matrix_max = numpy.max(node.arraytable._matrix_map)
    matrix_min = numpy.min(node.arraytable._matrix_min)
    matrix_avg = matrix_min+((matrix_max-matrix_min)/2)
    ProfileFace = faces.ProfileFace(\
                                        matrix_max,\
                                        matrix_min,\
                                        matrix_avg,\
                                        200,\
                                        60,\
                                        "cbars")

    if node.is_leaf():
        nameFace = faces.AttrFace("name",fsize=6 )
        faces.add_face_to_node(nameFace, node, 1, aligned=True )
        faces.add_face_to_node(ProfileFace, node, 0,  aligned=True )
    else:
        # Set custom faces
        faces.add_face_to_node(ProfileFace, node, 0, aligned=True )

def cluster_lines(node):
    # Extras node info
    node.collapsed = False
    # Color and style
    node.img_style["fgcolor"] = "#3333FF"
    node.img_style["size"] = 4
    matrix_max = numpy.max(node.arraytable._matrix_max)
    matrix_min = numpy.min(node.arraytable._matrix_min)
    matrix_avg = matrix_min+((matrix_max-matrix_min)/2)
    ProfileFace = faces.ProfileFace(\
      matrix_max,\
        matrix_min,\
        matrix_avg,\
        200,\
        50,\
        "lines")

    if node.is_leaf():
        nameFace = faces.AttrFace("name",fsize=6 )
        faces.add_face_to_node(nameFace, node, 1,  aligned=True )
        faces.add_face_to_node(ProfileFace, node, 0, aligned=True )
    else:
        # Set custom faces
        faces.add_face_to_node(ProfileFace, node, 0, aligned=True )

def cluster_bars(node):
    # Extras node info
    node.collapsed = False
    # Color and style
    node.img_style["fgcolor"] = "#3333FF"
    node.img_style["size"] = 4

    if node.is_leaf():
        matrix_max = numpy.max(node.arraytable._matrix_max)
        matrix_min = numpy.min(node.arraytable._matrix_min)
        matrix_avg = matrix_min+((matrix_max-matrix_min)/2)
        ProfileFace = faces.ProfileFace(\
          matrix_max,\
            matrix_min,\
            matrix_avg,\
            200,\
            40,\
            "bars")
        nameFace = faces.AttrFace("name",fsize=6 )
        faces.add_face_to_node(nameFace, node, 1, aligned=True )
        faces.add_face_to_node(ProfileFace, node, 0, aligned=True )

def large(node):
    # Color and style
    node.img_style["fgcolor"] = "#3333FF"
    node.img_style["size"] = 0


# Labels to show in qt application menu
layout_functions = {
        "Basic": basic,
        "Phylogenetic tree": phylogeny,
        "Clustering heatmap": heatmap,
        "Clustering validation (bars)": cluster_bars,
        "Clustering validation (profiles)": cluster_cbars,
        "Very large topology": large
        }
