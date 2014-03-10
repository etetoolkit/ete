#!/usr/bin/python

import sys
from common import argparse, PhyloTree, orthoxml


__DESCRIPTION__ = """
etree2orthoxml is a python script that extracts evolutionary events
(speciation and duplication) from a newick tree and exports them as a
OrthoXML file.

## ########################################################################
##
##           YOU CAN FIND EXAMPLES AND DOCUMENTATION AT:
##
##   http://pythonhosted.org/ete2/tutorial/tutorial_etree2orthoxml.html
## 
## ########################################################################

"""
SPECIES_NAME_DELIMITER = ""
SPECIES_NAME_POS = 0

def extract_spname(node_name):
    return node_name.split(SPECIES_NAME_DELIMITER)[SPECIES_NAME_POS]

def export_as_orthoXML(t, database, evoltype_attr="evoltype"):
    """ This function takes a ETE PhyloTree instance and export all
    its speciation and duplication events as OrthoXML format.

    Note that this function can be enriched or customized to include
    more orthoXML features using the orthoxml.py module. 
    """
    
    # Creates an empty orthoXML object
    O = orthoxml.orthoXML()

    #Generate the structure containing sequence information
    leaf2id= {}
    sp2genes = {}
    for genid, leaf in enumerate(t.iter_leaves()):
        spname=extract_spname(leaf.name)
        if spname not in sp2genes:
            sp = orthoxml.species(spname)
            db = orthoxml.database(name=database)
            genes = orthoxml.genes()
            sp.add_database(db)
            db.set_genes(genes)
            sp2genes[spname] = genes
            # add info to the orthoXML document
            O.add_species(sp)
        else:
            genes = sp2genes[spname]

        gn = orthoxml.gene(protId=leaf.name, id=genid)
        leaf2id[leaf] = genid
        genes.add_gene(gn)
        
    # Add an ortho group container to the orthoXML document
    ortho_groups = orthoxml.groups()
    O.set_groups(ortho_groups)
    
    # OrthoXML does not support duplication events to be at the root
    # of the tree, so we search for the top most speciation events in
    # the tree and export them as separate ortholog groups
    is_speciation = lambda n: getattr(n, evoltype_attr, "") == "S" or not n.children
    for speciation_root in t.iter_leaves(is_leaf_fn=is_speciation):
        # Creates an orthogroup in which all events will be added
        node2event = {}
        node2event[speciation_root] = orthoxml.group()
        ortho_groups.add_orthologGroup(node2event[speciation_root])

        # if root node is a leaf, just export an orphan sequence within the group
        if speciation_root.is_leaf():
            node2event[speciation_root].add_geneRef(orthoxml.geneRef(leaf2id[speciation_root]))

        # otherwise, descend the tree and export orthology structure
        for node in speciation_root.traverse("preorder"):
            if node.is_leaf():
                continue
            parent_event = node2event[node]
            for ch in node.children:
                if ch.is_leaf():
                    parent_event.add_geneRef(orthoxml.geneRef(leaf2id[ch]))
                else:
                    node2event[ch] = orthoxml.group()
                    try:
                        evoltype = getattr(ch, evoltype_attr)
                    except AttributeError:
                        if not ch.is_leaf():
                            print ch.features
                            raise AttributeError("\n\nUnknown evolutionary event. Please use [S] for speciation and [D] for duplication: %s" %ch.get_ascii())
                    
                    if evoltype == "D":
                        parent_event.add_paralogGroup(node2event[ch])
                    elif evoltype == "S":
                        parent_event.add_orthologGroup(node2event[ch])
    O.export(sys.stdout, 0, namespace_="")

       
def main(argv):
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('tree', metavar='tree_file', type=str, nargs=1,
                      help='A tree file (or text string) in newick format.')


    parser.add_argument("--sp_delimiter", dest="species_delimiter",
                        type=str, default="_",
                        help=("When species names are guessed from node names,"
                              " this argument specifies how to split node name to guess"
                              " the species code"))
                        
    parser.add_argument("--sp_field", dest="species_field", 
                          type=int, default=1,
                          help=("When species names are guessed from node names,"
                                " this argument specifies the position of the species"
                                " name code relative to the name splitting delimiter"))

    parser.add_argument("--root", dest="root", 
                        type=str, nargs="*",
                        help="Roots the tree to the node grouping the list"
                        " of node names provided (space separated). In example:"
                        "'--root human rat mouse'")

    
    parser.add_argument("--skip_ortholog_detection", dest="skip_ortholog_detection", 
                        action="store_true",
                        help=("Skip automatic detection of"
                              " speciation and duplication events, thus relying in the"
                              " correct annotation of the provided tree using"
                              " the extended newick format (i.e. '((A, A)[&&NHX:evoltype=D], B)[&&NHX:evoltype=S];')"))
    
    parser.add_argument("--evoltype_attr", dest="evoltype_attr", 
                          type=str, default="evoltype",
                          help=("When orthology detection is disabled,"
                                " the attribute name provided here will be expected to exist"
                                " in all internal nodes and read from the extended newick format"))
    
    parser.add_argument("--database", dest="database", 
                        type=str, default="",
                        help=("Database name"))


    parser.add_argument("--show", dest="show", 
                        action="store_true", default="",
                        help=("Show the tree and its evolutionary events before orthoXML export"))

    parser.add_argument("--ascii", dest="ascii", 
                        action="store_true", default="",
                        help=("Show the tree using ASCII representation and all its evolutionary"
                              " events before orthoXML export"))

    parser.add_argument("--newick", dest="newick", 
                        action="store_true", default="",
                        help=("print the extended newick format for provided tree using"
                              " ASCII representation and all its evolutionary events"
                              " before orthoXML export"))
    
    
    args = parser.parse_args()
    newick = args.tree[0]

    SPECIES_NAME_POS = args.species_field
    SPECIES_NAME_DELIMITER = args.species_delimiter

    # load a phylomeDB Tree provided as a newick file in the command line
    t = PhyloTree(newick, sp_naming_function=extract_spname)

    if args.root:
        if len(args.root) > 1:
            outgroup = t.get_common_ancestor(args.root)
        else:
            outgroup = t & args.root[0]
        t.set_outgroup(outgroup)


    if not args.skip_ortholog_detection:
        # detect speciation and duplication events using the species overlap
        # algorithm used in phylomeDB
        t.get_descendant_evol_events()
        
    if args.ascii:
        print t.get_ascii(attributes=[args.evoltype_attr, "name"], show_internal=True)
        
    if args.newick:
        print t.write(features=[args.evoltype_attr], format_root_node=True)
        
    if args.show:
        t.show()
    
    export_as_orthoXML(t, args.database, args.evoltype_attr)


if __name__ == '__main__':
    main(sys.argv[1:])
