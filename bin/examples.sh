PATH=$PATH:./

# compare trees: calculate distances
ete_dev compare -t "(((A, B),C),(D,E));" -r "(((A, C),B),(D,E));"
 
ete_dev generate --number 10 | ete_dev compare -r `ete_dev generate` 

# quick view
ete_dev generate | ete_dev view

# quick view text mode 
ete_dev generate | ete_dev view --text

# customize visualization
ete_dev generate | ete_dev view --face 'value:@name, color:red, size:20, pos:b-right' \
    --face 'value:@dist, color:steelblue, size:7, pos:b-top, nodetype:internal'

# auto distribute colors according to attributes
ete_dev view -t '((A, A, A, (C, C)), B, B, B);' --face 'value:@name, color:auto()'

# even using other attributes as source 
ete_dev view -t '((A, A, A, (C, C)), B, B, B);' --face 'value:@name, color:auto()' \
        --face 'value:@dist, pos:b-top, color:auto(@name)' 


# Annotate and visualize a tree with taxids
ete_dev annotate -t '((9606, 7727), 9505);' --ncbi | ete_dev view --ncbi

# render many tree images at once
./ete_dev generate --number 3 | ete_dev view --image 'mytree.png'

