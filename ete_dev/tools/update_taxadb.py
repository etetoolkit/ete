import sys
import os
from string import strip
import tarfile
from common import Tree
from utils import ask, ask_filename

def load_ncbi_tree_from_dump(tar):
    # Download: ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
    parent2child = {}
    name2node = {}
    node2taxname = {}
    synonyms = set()
    name2rank = {}
    print "Loading node names..."
    for line in tar.extractfile("names.dmp"):
        fields =  map(strip, line.split("|"))
        nodename = fields[0]
        name_type = fields[3].lower()
        taxname = fields[1]
        if name_type == "scientific name":
            node2taxname[nodename] = taxname
        elif name_type in set(["synonym", "equivalent name", "genbank equivalent name",
                               "anamorph", "genbank synonym", "genbank anamorph", "teleomorph"]):
            synonyms.add( (nodename, taxname) )
    print len(node2taxname), "names loaded."
    print len(synonyms), "synonyms loaded."

    print "Loading nodes..."
    for line in tar.extractfile("nodes.dmp"):
        fields =  line.split("|")
        nodename = fields[0].strip()
        parentname = fields[1].strip()
        n = Tree()
        n.name = nodename
        n.taxname = node2taxname[nodename]
        n.rank = fields[2].strip()
        parent2child[nodename] = parentname
        name2node[nodename] = n
    print len(name2node), "nodes loaded."

    print "Linking nodes..."
    for node in name2node:
       if node == "1":
           t = name2node[node]
       else:
           parent = parent2child[node]
           parent_node = name2node[parent]
           parent_node.add_child(name2node[node])
    print "Tree is loaded."
    return t, synonyms

def generate_table(t):
    OUT = open("taxa.tab", "w")
    for j, n in enumerate(t.traverse()):
        if j%1000 == 0:
            print "\r",j,"nodes inserted into the DB.",
        temp_node = n
        track = []
        while temp_node:
            track.append(temp_node.name)
            temp_node = temp_node.up
        if n.up:
            print >>OUT, '\t'.join([n.name, n.up.name, n.taxname, n.rank, ','.join(track)])
        else:
            print >>OUT, '\t'.join([n.name, "", n.taxname, n.rank, ','.join(track)])
    OUT.close()

def update(targz_file):
    tar = tarfile.open(targz_file, 'r')
    t, synonyms = load_ncbi_tree_from_dump(tar)

    print "Updating database..."
    generate_table(t)
   
    open("syn.tab", "w").write('\n'.join(["%s\t%s" %(v[0],v[1]) for v in synonyms]))
    open("merged.tab", "w").write('\n'.join(['\t'.join(map(strip, line.split('|')[:2])) for line in tar.extractfile("merged.dmp")]))

    CMD = open("commands.tmp", "w")
    cmd = """
DROP TABLE IF EXISTS species;
DROP TABLE IF EXISTS synonym;
DROP TABLE IF EXISTS merged;
CREATE TABLE species (taxid INT PRIMARY KEY, parent INT, spname VARCHAR(50) COLLATE NOCASE, rank VARCHAR(50), track TEXT);
CREATE TABLE synonym (taxid INT,spname VARCHAR(50) COLLATE NOCASE, PRIMARY KEY (spname, taxid));
CREATE TABLE merged (taxid_old INT, taxid_new INT);
CREATE INDEX spname1 ON species (spname COLLATE NOCASE);
CREATE INDEX spname2 ON synonym (spname COLLATE NOCASE);

.separator '\t'
.import taxa.tab species
.import syn.tab synonym
.import merged.tab merged

    """
    CMD.write(cmd)
    CMD.close()
    os.system("sqlite3 taxa.sqlite < commands.tmp")
    os.system("rm syn.tab merged.tab taxa.tab commands.tmp")
    
    print "Creating extended newick file with the whole NCBI tree [ncbi.nw]"
    t.write(outfile="ncbi.nw", features=["name", "taxname"])
  
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        if ask('Download latest ncbi taxonomy dump file?', ['y', 'n']) == 'y':
            status = os.system('wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz')
            if status == 0:
                update('taxdump.tar.gz')
        else:
            fname = ask_filename('path to tar.gz file containing ncbi taxonomy dump:')
            update(fname)
    else:
        update(sys.argv[1])
