#import pil_backend as backend
import qt4_backend as backend
import copy
from pygenomics.treeview import layouts, TreeImageProperties, faces
import numpy

_MIN_NODE_STYLE = {
    "fgcolor": "#FFAA55",
    "bgcolor": "#FFFFFF",
    "hlwidth":  0,
    "line_color": "#000000",
    "line_type":  0,
    "vlwidth": 0,
    "size": 4,
    "shape": "square",
    "faces": None, 
    "draw_descendants": 1, 
    }

def test_layout(node):
    if node.is_leaf():
	faces.add_face(node, 0, faces.AttrFace("name","Arial",10,\
						   "#24416d",None) )
    else:
	faces.add_face(node, 0, faces.ImgFace("bottle.png") )

LAYOUT=test_layout

# The main idea of this functions is to provide a programtic way to
# draw trees (which may contain a variate of 'faces'). First, I update
# the face's pixmaps, calculate their size and I browse the tree to
# know the dimension of the tree and the space spend it by each
# node. After this I just browse back the tree to render lines and
# faces at the right position.  In the begining, I wrote recursive
# functions, but I found some "max recursion deep" problems with very
# large trees. So I decided to port all recursions to iterative
# approaches.  I also want to keep this module backend-independet,
# which means that rendering function uses a standard set of drawing
# functions that can be implemented externally to work with diferent
# graphical backends. So far I just support Qt4 backend (which
# includes also a GUI), but many other should be easy to implement.

def render(start_node, x, y):

    update_node_areas(start_node, 30, TreeImageProperties())
    I = backend.new_image(start_node.fullRegion[0], start_node.fullRegion[1], "white")
    D = backend.new_drawer(I)
    to_visit = [[start_node, False, x]]
    # Draw border
    backend.draw_rectangle(D, start_node, 0, 0, \
			       start_node.fullRegion[0], \
			       start_node.fullRegion[1])
    # Browse the tree in pre and post-order (each internal node is
    # browsed twice)
    while len(to_visit)>0:
	node, traversed, node_start_x = to_visit.pop(0)
	node._x = node_start_x
	if not traversed and not node.is_leaf():
	    for ch in node.children:
		to_visit.insert(0, [ch, False, node_start_x+node.nodeRegion[0]])
	    to_visit.insert(len(node.children), [node, True, node_start_x])
	else:
	    if node.is_leaf():
		node._centered_y = y + (node.fullRegion[1]/2) + node.up._ycorrection
		node._y = y + node.up._ycorrection
		y += node.fullRegion[1]
	    else:
		node._centered_y = abs(node.children[0]._centered_y + node.children[-1]._centered_y)/2
		node._y = node.children[-1]._y - node._ycorrection
		y += node._ycorrection * 2
	    draw_rooted_node(D, node)


def update_node_areas(start_node, scale, props):
    max_w_aligned_face = 0
    for node in start_node.traverse("postorder"):
	node.img_style = copy.copy(_MIN_NODE_STYLE)
	node.img_style["faces"] = []
	LAYOUT(node)

	if props.force_topology:
	    node._dist_xoffset = scale
	else:
	    node._dist_xoffset = float(node.dist * scale) 

	# Calculates the size of the rectangle covered by all node's
	# faces.  Each stack is drawn as a different column. There is
	# an speciall stack of faces which is called "aligned faces"
	# that represent faces that have to be drawn aligned to the
	# most distant node in the tree.
	min_node_height = max(node.img_style["size"], \
				  node.img_style["hlwidth"]*2) 
	max_w         = 0
	max_aligned_w = 0
	max_h         = 0
	for stack in node.img_style["faces"]:
	    stack_h = 0
	    stack_w = 0
	    aligned_f_w = 0
	    aligned_f_h = 0
	    # And each face as a row in a given column
	    for f in stack:
		# If the face is an image, update it
		if f.type == "pixmap":
		    f.update_pixmap()

		if node.is_leaf() and f.aligned:
		    aligned_f_w = max(aligned_f_w, f._width())
		    aligned_f_h += f._height()
		else:
		    stack_w = numpy.max([stack_w, f._width()])
		    stack_h += f._height()

	    max_aligned_w += aligned_f_w
	    max_w += stack_w
	    max_h = numpy.max([aligned_f_h,stack_h,max_h])

	# Updates the max width spent by aligned faces
	if max_aligned_w > max_w_aligned_face:
	    max_w_aligned_face = max_aligned_w

	# Sets faces region
	node.facesRegion = [max_w, max_h]

	# Sets the node region = faces + branch length + node
	# representation
	w = node._dist_xoffset + max_w + node.img_style["size"] 
	h = numpy.max([max_h, min_node_height, props.min_branch_separation])
	node.nodeRegion = [w, h]

	# Sets the node full Region (covering child space
	sum_child_h = 0
	max_child_w = 0

	# Get width and height covered by childs
	for ch in node.children:
	    ch_r = ch.fullRegion
	    sum_child_h += ch_r[1]
	    if ch_r[0]>max_child_w:
		max_child_w = ch_r[0]

	# takes max height: childs or its own faces
	if sum_child_h > h:
	    h = sum_child_h
	    node._ycorrection = 0
	else:
	    node._ycorrection = (h - sum_child_h)/2
	w += max_child_w
	# Sets the total room needed for this node
	node.fullRegion = [w, h]

def draw_rooted_node(drawer, node):
    """ This is the central function which draws a node and all its
    features. Is assumes that x and y positions are already set at in
    the node. """

    # Branch line
    x1 = node._x+node._dist_xoffset
    x2 = node._x
    y = node._centered_y
    backend.draw_line(drawer, node, x1, y, x2, y)

    if not node.is_leaf():
	# Vertical line
	x = node._x + node.nodeRegion[0]
	y1 = node.children[0]._centered_y
	y2 = node.children[-1]._centered_y
	backend.draw_line(drawer, node, x, y1, x, y2)

    # Draw node balls/squares/spheres o whatever
    r = node.img_style["size"]/2
    x = node._x+ node._dist_xoffset
    backend.draw_ellipse(drawer, node, x, node._centered_y-r, 
			 x+r*2, node._centered_y+r)
  

    # Draw faces within the node room
    aligned_start_x = 200
    start_x = node._x + node._dist_xoffset + node.img_style["size"]
    for stack in node.img_style["faces"]:
	# get each stack's height and width
	stack_h         = 0
	stack_w         = 0
	aligned_stack_w = 0
	aligned_stack_h = 0
	# Extract height and width of al faces in this stack
	# Get max width and cumulated height
	for f in stack:
	    if node.is_leaf() and f.aligned:
		aligned_stack_w = max(aligned_stack_w , f._width())
		aligned_stack_h += f._height()
	    else:
		stack_w = max(stack_w ,f._width() )
		stack_h += f._height()

	if node._centered_y + node.nodeRegion[1]/2 <= node.fullRegion[1]/2:
	    cumulated_y = node._centered_y - node.nodeRegion[1]/2 
	else:
	    cumulated_y = node._y - (node.fullRegion[1]/2)-(node.nodeRegion[1]/2)

	cumulated_aligned_y = cumulated_y
	for f in stack:
	    # add each face of this stack into the correct position We
	    # hace middle_y, so start_y is set to place face at such
	    # middle_y possition.
	    if node.is_leaf() and f.aligned:
		start_y = cumulated_aligned_y + (-aligned_stack_h/2)+r
	    else:
		start_y = cumulated_y + (-stack_h/2)+r

	    # If face is aligned and node is terminal, place face
	    # at aligned margin
	    if node.is_leaf() and f.aligned:
		if f.type == "text":
		    backend.draw_text(drawer, start_x, cumulated_aligned_y, f.get_text(), node)
		else:
		    backend.draw_image(drawer, start_x, cumulated_aligned_y, f.pixmap, node)
		cumulated_aligned_y += f._height()

	    # If face has to be draw within the node's room 
	    else:
		if f.type == "text":
		    backend.draw_text(drawer, node, start_x, cumulated_y, f.get_text())
		else:
		    backend.draw_image(drawer, node,  start_x, cumulated_y, f.pixmap)
		cumulated_y += f._height()
		print cumulated_y

	# next stack will start with this x_offset
	start_x += stack_w
	aligned_start_x += aligned_stack_w


def draw_circular_node(node):
    angle_step = mainarc/float(len(starnode))
    next_angle = a
    for n in node.traverse("preorder"):
	if n.is_leaf():
	    next_angle += angle_step
            a = next_angle
            x1  =  cx + d*math.cos(a) # inicio de la liene
            y1  =  cy + d*math.sin(a) # inicio de la liene

            d  +=  (mydist*scale)
            x2  =  cx + d*math.cos(a) # Fin de la linea
            y2  =  cy + d*math.sin(a) # Fin de la linea

            x3  =  cx + (self.diam/2)*math.cos(a) #puntox en la circunferencia al que debe apuntar la linea del nodo
            y3  =  cy + (self.diam/2)*math.sin(a) #puntoy en la circunferencia al que debe apuntar la linea del nodo
	    
	    
    
    
