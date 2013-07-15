from ete2 import Tree, faces

# Saving Tree files
pass 

# NEW ROOTING APPROACHES
def root_min_dupli(tree, orto_mode, tree_mode):
	tree,num_nodes = name_nodes(tree)
	nw = tree.write(features = ["node_name"])
	root = {}
	minim = ""
	i = 0
	while i < num_nodes:
		t = ete2.PhyloTree(nw,format=1)
		name = "n"+str(i)
		node = t.search_nodes(node_name = name)[0]
		if not node.is_root():
			t.set_outgroup(node)
			if orto_mode == "s":
				t = annotate_tree(t)
				duplis = len(t.search_nodes(evoltype = "D"))
				mduplis = len(t.search_nodes(evoltype = "MD"))
				number = duplis + mduplis
			else:
				sys.exit("If the manual ortology descritpion mode was chosen, the tree should be rooted")
			root[name] = number
			if number < minim or minim == "":
				minim = number
		i = i + 1
	possible_roots = [m for m in root if root[m] == minim]
	possible_roots.sort()

	if len(possible_roots) == 1:
		outgroup = tree.search_nodes(node_name = possible_roots[0])[0]
		tree.set_outgroup(outgroup)
	else:
		outgroup = most_distant(nw,possible_roots,tree_mode)
		outgroup = tree.search_nodes(node_name = outgroup)[0]
	return outgroup

def name_nodes(tree):
	i = 0
	for node in tree.traverse():
		name = "n"+str(i)
		node.add_features(node_name = name)
		i = i + 1
	return tree,i

def most_distant(nw, possible_roots,tree_mode):
	distances = {}
	for r in possible_roots:
		tree = ete2.PhyloTree(nw,format=1)
		node = tree.search_nodes(node_name = r)[0]
		for leaf in tree.get_leaves():
			try:
				d = node.get_distance(leaf)
				if r not in distances:
					distances[r] = d
				else:
					if d > distances[r]:
						distances[r] = d
			except:
				pass
	maxim = ""
	outgroup = possible_roots[0]
	for r,d in distances.iteritems():
		if maxim == "" or d > maxim:
			maxim = d
			outgroup = r
	return outgroup

def annotate_tree(tree):
	for node in tree.traverse("postorder"):
	  if len(node.get_children()) != 2:
		  if node.is_root():
			  node.add_feature("evoltype","R")
		  else:
			  dupli = False
			  for ch1 in node.get_children():
				  for ch2 in node.get_children():
					  if ch1 != ch2:
						  spe1 = ch1.get_species()
						  spe2 = ch2.get_species()
						  common = spe1.intersection(spe2)
						  if common != set([]):
							  dupli = True
			  if dupli:
				  node.add_feature("evoltype","MD")
			  else:
				  node.add_feature("evoltype","MS")
	  else:
		  common = []
		  spe1 = node.get_children()[0].get_species()
		  spe2 = node.get_children()[1].get_species()
		  common = spe1.intersection(spe2)
		  if common != set([]):
			  node.add_feature("evoltype","D")
		  else:
			  node.add_feature("evoltype","S")
	return tree



import ete2

def improve_outgroup_prediction(current_outgroup,spec):
	current_age = spec[list(current_outgroup.get_species())[0]]
	same_age = True
	while same_age:
		sisters = current_outgroup.get_sisters()
		for sis in sisters:
			if current_age == sis.get_age(spec):
				for l in list(sis.get_species()):
					if spec[l] != current_age:
						same_age = False
			else:
				same_age = False
		if same_age:
			if current_outgroup.is_root():
				same_age = False
			else:
				current_outgroup = current_outgroup.up
	return current_outgroup

def root_at_youngest_leaf(tree,spec):
	trobat = False
	for sp in spec:
		if not trobat:
			n = tree.search_nodes(species=sp)
			if len(n) > 0:
				tree.set_outgroup(n[0])
				trobat = True
	return tree

def root_to_farthest_node(tree,spe2age):
	all_present = True
	for species in tree.get_species():
		if species not in spe2age:
			spe2age[species] = 1
			all_present = False
	if not all_present:
		print "WARNING: not all the species in your tree were present in the anotation file, a default value of 1 has been assigned as their age value"
	tree = root_at_youngest_leaf(tree,spe2age)
	outgroup = tree.get_farthest_oldest_leaf(spe2age)
	outgroup = improve_outgroup_prediction(outgroup,spe2age)
	return outgroup



# SORT TREE LEAVES
pass
# SET DEFAULT DIST TO 0.0 and SUPPORT to 1.0
pass

# ULTRAMETRIC
def convert_to_ultrametric(self, tree_length, strategy="balanced"):
    ''' Converts a tree to ultrametric topology (all leaves have the
    same distance two root).'''

    # pre-calculate how many splits remain under each node
    node2max_depth = {}
    for node in t.traverse("postorder"):
        if not node.is_leaf():
            max_depth = max([node2max_depth[c] for c in node.children]) + 1
            node2max_depth[node] = max_depth
        else:
            node2max_depth[node] = 1
    node2dist = {self: 0.0}
    tree_length = float(tree_length)
    step = tree_length / node2max_depth[t]
    for node in t.iter_descendants("levelorder"):
        if strategy == "balanced":
            node.dist = (tree_length - node2dist[node.up]) / node2max_depth[node]
            node2dist[node] =  node.dist + node2dist[node.up]
        elif strategy == "fixed":
            if not node.is_leaf():
                node.dist = step
            else:
                node.dist = tree_length - ((node2dist[node.up]) * step)
            node2dist[node] = node2dist[node.up] + 1
        node.dist = node.dist

def ultrametric_layout(node):
    # node balls consume space in the tree picture, so partitions with
    # many splits are not well aligned with partitions having less
    # splits. To solve it,  I set node sphere size to 0
    node.img_style["size"] = 0
    if node.is_leaf():
        faces.add_face_to_node(nameFace, node, 0)

def test_ultrametric():
    t =  Tree()
    # Creates a random tree (not ultrametric)
    t.populate(100)

    # Convert tree to a ultrametric topology in which distance from
    # leaf to root is always 100. Two strategies are available:
    # balanced or fixed
    convert_to_ultrametric(t, 1.0, "balanced")

    # Print distances from all leaves to root. Due to precision issues
    # with the float type.  Branch lengths may show differences at
    # high precision levels, that's way I round to 6 decimal
    # positions.
    print "distance from all leaves to root:", \
          set([round(l.get_distance(t), 6)for l in t.iter_leaves()])
    nameFace = faces.AttrFace("name")
    t.show(ultrametric_layout)

if __name__ == "__main__":
    test_ultrametric()
