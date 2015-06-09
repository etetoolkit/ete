#
# INLINE LINE TREE EDITION AND VISUALIZATION
# 

# 'ete generate' produces random trees 
ete generate --size 5 --number 3

# which you could quickly plot on your terminal
ete generate --size 5 --number 3 | ete view --text

# or visualize with using the GUI
ete generate --size 5 --number 3 | ete view

# or just render them as tree images
ete generate --size 5 --number 3 | ete view --image "tree.png"
ls -l *.tree.png

# 'ete mod' allows to modify tree topologies on the fly, i.e. rooting
ete mod -t "(((A, B),C),(D,E));" --outgroup A B  | ete view --text

# and other common operations
ete mod  -t '( ((A, B),C),  (((D, (E,F)), G), (H,I,J)));' --outgroup A B --ladderize \
--ultrametric --resolve_polytomies --prune A B C D E F | ete view --text

# as all ete tools, it also operates on lists of trees
ete generate --size 5 --number 3 | ete mod --outgroup 'aaaaaaaaaa' | ete view --text

# 
# COMPARING TREES
# 


# 'tree compare' shows robinson-foulds distances and % of matching branches
ete compare -t "(((A, B),C),(D,E));" -r "(((A, C),B),(D,E));"

# also for a bunch of trees
ete generate --number 10 | ete compare -r `ete generate` 

# and even trees of different sizes
ete compare -t "(((A, B),C),(D,E));" "((A,B), C);" -r "(((A, C),B),(D,E));"

# 
# NCBI taxonomy module (new in ETE 2.3)
# 

# 'ete ncbiquery' allows to query ncbi taxonomy using a local ETE friendly database
# For example, lets get the tree connecting 4 random taxa (by name or taxid)  
ete ncbiquery --search 9606 'Mus musculus' 'Gallus gallus' 'Afrotheria' --tree | ete view --text 

# the taxonomic tree is actually annotated and plays well with ete visualization
ete ncbiquery --search 9606 'Mus musculus' 'Gallus gallus' 'Afrotheria' --tree | ete view --ncbi
 
# or get extended taxonomy information for taxids and species names
ete ncbiquery --search 9606 'Mus musculus' 'Gallus gallus' 'Afrotheria' --info 

# ncbiquery also supports piping
cat species.txt
cut -f1 species.txt | ete ncbiquery --tree | ete view --ncbi  

# dump descendants
ete ncbiquery --search homo pan Drosophila --descendants

# dump descendant as tree
ete ncbiquery --search Drosophila --tree|ete view --text
ete ncbiquery --search Drosophila --tree --collapse_subspecies | ete view --text



 

# 
# TREE ANNOTATION
# 

# 'ete annotate' allows to add meta data to trees. 
# Taxid translation is supported out of the box
ete annotate -t '((9606, 7727), 9505);' --ncbi | ete view --ncbi

# Custom features can also be attached to trees
cat annotations.txt
ete annotate -t '(((A, B), C), (D,E));' --feature name:func source:annotations.txt | ete view \
--text --sin --show_attributes name func

# 
# ADVANCED TREE VISUALIZATION
# 

# 'ete view' allows a lot of customization, i.e. adding node faces
ete generate --random_branches | ete view --face 'value:@name, color:red, size:20, pos:b-right' \
--face 'value:@dist, color:steelblue, size:7, pos:b-top, nodetype:internal'

# auto distribute colors according to attributes
ete view -t '((A, A, A, (C, C)), B, B, B);' --face 'value:@name, color:auto()'

# even using other attributes as a source 
ete view -t '((A, A, A, (C, C)), B, B, B);' --face 'value:@name, color:auto()' \
--face 'value:@dist, pos:b-top, color:auto(@name)' 

# Common visualization templates are supported out of the box. i.e. alignments:
cat alignment.fa
ete view -t '(A, (B, C));' --alg alignment.fa 

# Although customization is always possible 
ete view -t '((A, A, A, (C, C)), B, B, B);' --face 'value:ABC---AAAAAA---AA-----AA, ftype:blockseq,  bgcolor:auto(@name), pos:aligned' \
--face 'value:ABC---AAAAAAAAAAAAA---AA-----AA, ftype:compactseq, pos:aligned' \
--face 'value:ABC---AAAAAAAAAAAAA---AA-----AA, ftype:fullseq, pos:aligned'

