#!/usr/bin/env python3

import sys
import os
import pickle
from collections import defaultdict, Counter
import requests
from hashlib import md5

import sqlite3
import math
import tarfile
import warnings

from ete4 import ETE_DATA_HOME, update_ete_data


__all__ = ["NCBITaxa", "is_taxadb_up_to_date"]

DB_VERSION = 2
DEFAULT_TAXADB = ETE_DATA_HOME + '/taxa.sqlite'
DEFAULT_TAXDUMP = ETE_DATA_HOME + '/taxdump.tar.gz'


def as_csv(xs):
    """Return sequence xs as comma-separated values, quoted properly for SQL."""
    return ','.join("'%s'" % str(x).replace("'", "''") for x in xs)


def is_taxadb_up_to_date(dbfile=DEFAULT_TAXADB):
    """Return True if a valid and up-to-date taxa.sqlite database exists.

    If `dbfile` is not specified, DEFAULT_TAXADB is assumed.
    """
    db = sqlite3.connect(dbfile)

    try:
        version = db.execute('SELECT version FROM stats;').fetchone()[0]
    except (sqlite3.OperationalError, ValueError, IndexError, TypeError):
        version = None

    db.close()

    return version == DB_VERSION


class NCBITaxa:
    """
    A local transparent connector to the NCBI taxonomy database.
    """

    def __init__(self, dbfile=None, taxdump_file=None,
                 memory=False, update=True):
        """Open and keep a connection to the NCBI taxonomy database.

        If it is not present in the system, it will download the
        database from the NCBI site first, and convert it to ete's
        format.
        """
        self.dbfile = dbfile or DEFAULT_TAXADB

        if taxdump_file:
            self.update_taxonomy_database(taxdump_file)

        if dbfile != DEFAULT_TAXADB and not os.path.exists(self.dbfile):
            print('NCBI database not present yet (first time used?)',
                  file=sys.stderr)
            self.update_taxonomy_database(taxdump_file)

        if not os.path.exists(self.dbfile):
            raise ValueError("Cannot open taxonomy database: %s" % self.dbfile)

        self.db = None
        self._connect()

        if not is_taxadb_up_to_date(self.dbfile) and update:
            print('NCBI database format is outdated. Upgrading',
                  file=sys.stderr)
            self.update_taxonomy_database(taxdump_file)

        if memory:
            filedb = self.db
            self.db = sqlite3.connect(':memory:')
            filedb.backup(self.db)

    def update_taxonomy_database(self, taxdump_file=None):
        """Update the ncbi taxonomy database.

        It does it by downloading and parsing the latest
        taxdump.tar.gz file from the NCBI site.

        :param taxdump_file: Alternative location of the
            taxdump.tax.gz file.
        """
        update_db(self.dbfile, taxdump_file)

    def _connect(self):
        self.db = sqlite3.connect(self.dbfile)

    def _translate_merged(self, all_taxids):
        conv_all_taxids = set((list(map(int, all_taxids))))

        cmd = ('SELECT taxid_old, taxid_new '
               'FROM merged WHERE taxid_old IN (%s)' %
               as_csv(all_taxids))

        result = self.db.execute(cmd)

        conversion = {}
        for old, new in result.fetchall():
            conv_all_taxids.discard(int(old))
            conv_all_taxids.add(int(new))
            conversion[int(old)] = int(new)

        return conv_all_taxids, conversion

    def get_fuzzy_name_translation(self, name, sim=0.9):
        """Return taxid, species name and match score from the NCBI database.

        The results are for the best match for name in the NCBI
        database of taxa names, with a word similarity >= `sim`.

        :param name: Species name (does not need to be exact).
        :param 0.9 sim: Min word similarity to report a match (from 0 to 1).
        """
        import sqlite3.dbapi2 as dbapi2

        _db = dbapi2.connect(self.dbfile)
        _db.enable_load_extension(True)
        module_path = os.path.split(os.path.realpath(__file__))[0]
        _db.execute("SELECT load_extension('%s/%s')" %
                    (module_path, "SQLite-Levenshtein/levenshtein.sqlext"))

        print("Trying fuzzy search for %s" % name)
        maxdiffs = math.ceil(len(name) * (1-sim))
        cmd = (f'SELECT taxid, spname, LEVENSHTEIN(spname, \'{name}\') AS sim '
               f'FROM species WHERE sim <= {maxdiffs} ORDER BY sim LIMIT 1;')

        taxid, spname, score = None, None, len(name)
        result = _db.execute(cmd)
        try:
            taxid, spname, score = result.fetchone()
        except TypeError:
            cmd = (
                f'SELECT taxid, spname, LEVENSHTEIN(spname, \'{name}\') AS sim '
                f'FROM synonym WHERE sim <= {maxdiffs} ORDER BY sim LIMIT 1;')
            result = _db.execute(cmd)
            try:
                taxid, spname, score = result.fetchone()
            except:
                pass
            else:
                taxid = int(taxid)
        else:
            taxid = int(taxid)

        norm_score = 1 - (float(score) / len(name))
        if taxid:
            print(f'FOUND! {spname} taxid:{taxid} score:{score} ({norm_score})')

        return taxid, spname, norm_score

    def get_rank(self, taxids):
        """Return dict with NCBI taxonomy ranks for each list of taxids."""
        all_ids = set(taxids)
        all_ids.discard(None)
        all_ids.discard("")

        cmd = 'SELECT taxid, rank FROM species WHERE taxid IN (%s);' % as_csv(all_ids)
        result = self.db.execute(cmd)

        id2rank = {}
        for tax, spname in result.fetchall():
            id2rank[tax] = spname

        return id2rank

    def get_lineage_translator(self, taxids):
        """Return dict with lineage tracks corresponding to the given taxids.

        The lineage tracks are a hierarchically sorted list of parent taxids.
        """
        all_ids = set(taxids)
        all_ids.discard(None)
        all_ids.discard("")

        cmd = 'SELECT taxid, track FROM species WHERE taxid IN (%s);' % as_csv(all_ids)
        result = self.db.execute(cmd)

        id2lineages = {}
        for tax, track in result.fetchall():
            id2lineages[tax] = list(map(int, reversed(track.split(','))))

        return id2lineages

    def get_lineage(self, taxid):
        """Return lineage track corresponding to the given taxid.

        The lineage track is a hierarchically sorted list of parent taxids.
        """
        if not taxid:
            return None

        taxid = int(taxid)
        result = self.db.execute(f'SELECT track FROM species WHERE taxid={taxid}')
        raw_track = result.fetchone()
        if not raw_track:
            #perhaps is an obsolete taxid
            _, merged_conversion = self._translate_merged([taxid])
            if taxid in merged_conversion:
                result = self.db.execute(
                    'SELECT track FROM species WHERE taxid=%s' %
                    merged_conversion[taxid])
                raw_track = result.fetchone()

            if not raw_track:
                raise ValueError(f'Could not find taxid: {taxid}')
            else:
                warnings.warn('taxid %s was translated into %s' %
                              (taxid, merged_conversion[taxid]))

        track = list(map(int, raw_track[0].split(',')))
        return list(reversed(track))

    def get_common_names(self, taxids):
        cmd = 'SELECT taxid, common FROM species WHERE taxid IN (%s);' % as_csv(taxids)
        result = self.db.execute(cmd)

        id2name = {}
        for tax, common_name in result.fetchall():
            if common_name:
                id2name[tax] = common_name

        return id2name

    def get_taxid_translator(self, taxids, try_synonyms=True):
        """Return dict with the scientific names corresponding to the taxids."""
        all_ids = set(map(int, taxids))
        all_ids.discard(None)
        all_ids.discard("")

        cmd = 'SELECT taxid, spname FROM species WHERE taxid IN (%s);' % as_csv(all_ids)
        result = self.db.execute(cmd)

        id2name = {}
        for tax, spname in result.fetchall():
            id2name[tax] = spname

        # Any taxid without translation? Let's try in the merged table.
        if len(all_ids) != len(id2name) and try_synonyms:
            not_found_taxids = all_ids - set(id2name.keys())
            taxids, old2new = self._translate_merged(not_found_taxids)
            new2old = {v: k for k,v in old2new.items()}

            if old2new:
                cmd = 'SELECT taxid, spname FROM species WHERE taxid IN (%s);' % as_csv(new2old)
                result = self.db.execute(cmd)
                for tax, spname in result.fetchall():
                    id2name[new2old[tax]] = spname

        return id2name

    def get_name_translator(self, names):
        """Return dict with taxids corresponding to the given scientific names.

        Exact name match is required for translation.
        """
        name2id = {}
        #name2realname = {}
        name2origname = {}
        for n in names:
            name2origname[n.lower()] = n

        names = set(name2origname.keys())

        cmd = 'SELECT spname, taxid FROM species WHERE spname IN (%s)' % as_csv(name2origname.keys())
        result = self.db.execute(cmd)
        for sp, taxid in result.fetchall():
            oname = name2origname[sp.lower()]
            name2id.setdefault(oname, []).append(taxid)
            #name2realname[oname] = sp
        missing =  names - set([n.lower() for n in name2id.keys()])
        if missing:
            result = self.db.execute('SELECT spname, taxid FROM synonym '
                                     'WHERE spname IN (%s)' % as_csv(missing))
            for sp, taxid in result.fetchall():
                oname = name2origname[sp.lower()]
                name2id.setdefault(oname, []).append(taxid)
                #name2realname[oname] = sp
        return name2id

    def translate_to_names(self, taxids):
        """Return list of scientific names corresponding to taxids."""
        id2name = self.get_taxid_translator(taxids)
        names = []
        for sp in taxids:
            names.append(id2name.get(sp, sp))
        return names

    def get_descendant_taxa(self, parent, intermediate_nodes=False,
                            rank_limit=None, collapse_subspecies=False,
                            return_tree=False):
        """Return list of descendant taxids of the given parent.

        Parent can be given as taxid or scientific species name.

        If intermediate_nodes=True, the list will also have the internal nodes.
        """
        try:
            taxid = int(parent)
        except ValueError:
            try:
                taxid = self.get_name_translator([parent])[parent][0]
            except KeyError:
                raise ValueError('%s not found!' %parent)

        # checks if taxid is a deprecated one, and converts into the right one.
        _, conversion = self._translate_merged([taxid]) #try to find taxid in synonyms table
        if conversion:
            taxid = conversion[taxid]

        with open(self.dbfile+".traverse.pkl", "rb") as CACHED_TRAVERSE:
            prepostorder = pickle.load(CACHED_TRAVERSE)
        descendants = {}
        found = 0
        for tid in prepostorder:
            if tid == taxid:
                found += 1
            elif found == 1:
                descendants[tid] = descendants.get(tid, 0) + 1
            elif found == 2:
                break

        if not found:
            raise ValueError("taxid not found:%s" %taxid)
        elif found == 1:
            return [taxid]

        if rank_limit or collapse_subspecies or return_tree:
            tree = self.get_topology(list(descendants.keys()), intermediate_nodes=intermediate_nodes, collapse_subspecies=collapse_subspecies, rank_limit=rank_limit)
            if return_tree:
                return tree
            elif intermediate_nodes:
                return list(map(int, [n.name for n in tree.get_descendants()]))
            else:
                return list(map(int, [n.name for n in tree]))

        elif intermediate_nodes:
            return [tid for tid, count in descendants.items()]
        else:
            return [tid for tid, count in descendants.items() if count == 1]

    def get_topology(self, taxids, intermediate_nodes=False, rank_limit=None,
                     collapse_subspecies=False, annotate=True):
        """Return the minimal pruned NCBI taxonomy tree containing taxids.

        :param False intermediate_nodes: If True, single child nodes
            representing the complete lineage of leaf nodes are kept.
            Otherwise, the tree is pruned to contain the first common
            ancestor of each group.
        :param None rank_limit: If valid NCBI rank name is provided,
            the tree is pruned at that given level. For instance, use
            rank="species" to get rid of sub-species or strain leaf
            nodes.
        :param False collapse_subspecies: If True, any item under the
            species rank will be collapsed into the species upper
            node.
        """
        from .. import PhyloTree
        taxids, merged_conversion = self._translate_merged(taxids)
        if len(taxids) == 1:
            root_taxid = int(list(taxids)[0])
            with open(self.dbfile+".traverse.pkl", "rb") as CACHED_TRAVERSE:
                prepostorder = pickle.load(CACHED_TRAVERSE)
            descendants = {}
            found = 0
            nodes = {}
            hit = 0
            visited = set()
            start = prepostorder.index(root_taxid)
            try:
                end = prepostorder.index(root_taxid, start+1)
                subtree = prepostorder[start:end+1]
            except ValueError:
                # If root taxid is not found in postorder, must be a tip node
                subtree = [root_taxid]
            leaves = set(v for v, count in Counter(subtree).items() if count == 1)
            nodes[root_taxid] = PhyloTree({'name': str(root_taxid)})
            current_parent = nodes[root_taxid]
            for tid in subtree:
                if tid in visited:
                    current_parent = nodes[tid].up
                else:
                    visited.add(tid)
                    nodes[tid] = PhyloTree({'name': str(tid)})
                    current_parent.add_child(nodes[tid])
                    if tid not in leaves:
                        current_parent = nodes[tid]
            root = nodes[root_taxid]
        else:
            taxids = set(map(int, taxids))
            sp2track = {}
            elem2node = {}
            id2lineage = self.get_lineage_translator(taxids)
            all_taxids = set()
            for lineage in id2lineage.values():
                all_taxids.update(lineage)
            id2rank = self.get_rank(all_taxids)
            for sp in taxids:
                track = []
                lineage = id2lineage[sp]

                for elem in lineage:
                    if elem not in elem2node:
                        node = elem2node.setdefault(elem, PhyloTree())
                        node.name = str(elem)
                        node.taxid = elem
                        node.add_prop("rank", str(id2rank.get(int(elem), "no rank")))
                    else:
                        node = elem2node[elem]
                    track.append(node)
                sp2track[sp] = track
            # generate parent child relationships
            for sp, track in sp2track.items():
                parent = None
                for elem in track:
                    if parent and elem not in parent.children:
                        parent.add_child(elem)
                    if rank_limit and elem.props.get('rank') == rank_limit:
                        break
                    parent = elem
            root = elem2node[1]

        #remove onechild-nodes
        if not intermediate_nodes:
            for n in root.descendants():
                if len(n.children) == 1 and int(n.name) not in taxids:
                    n.delete(prevent_nondicotomic=False)

        if len(root.children) == 1:
            tree = root.children[0].detach()
        else:
            tree = root

        if collapse_subspecies:
            to_detach = []
            for node in tree.traverse():
                if node.props.get('rank') == "species":
                    to_detach.extend(node.children)
            for n in to_detach:
                n.detach()

        if annotate:
            self.annotate_tree(tree)

        return tree

    def annotate_tree(self, t, taxid_attr="name", tax2name=None,
                      tax2track=None, tax2rank=None, ignore_unclassified=False):
        """Annotate a tree containing taxids as leaf names.

        The annotation adds the properties: 'taxid', 'sci_name',
        'lineage', 'named_lineage' and 'rank'.

        :param t: a Tree (or Tree derived) instance.
        :param name taxid_attr: Allows to set a custom node attribute
            containing the taxid number associated to each node (i.e.
            species in PhyloTree instances).
        :param tax2name,tax2track,tax2rank: Use these arguments to
            provide pre-calculated dictionaries providing translation
            from taxid number and names,track lineages and ranks.
        """
        taxids = set()
        for n in t.traverse():
            try:
                tid = int(getattr(n, taxid_attr, n.props.get(taxid_attr)))
            except (ValueError, AttributeError, TypeError):
                pass
            else:
                taxids.add(tid)
        merged_conversion = {}

        taxids, merged_conversion = self._translate_merged(taxids)

        if not tax2name or taxids - set(map(int, list(tax2name.keys()))):
            tax2name = self.get_taxid_translator(taxids)
        if not tax2track or taxids - set(map(int, list(tax2track.keys()))):
            tax2track = self.get_lineage_translator(taxids)

        all_taxid_codes = set([_tax for _lin in list(tax2track.values()) for _tax in _lin])
        extra_tax2name = self.get_taxid_translator(list(all_taxid_codes - set(tax2name.keys())))
        tax2name.update(extra_tax2name)
        tax2common_name = self.get_common_names(tax2name.keys())

        if not tax2rank:
            tax2rank = self.get_rank(list(tax2name.keys()))

        n2leaves = t.get_cached_content()

        for n in t.traverse('postorder'):
            try:
                node_taxid = int(getattr(n, taxid_attr, n.props.get(taxid_attr)))
            except (ValueError, AttributeError, TypeError):
                node_taxid = None

            n.add_prop('taxid', node_taxid)
            if node_taxid:
                if node_taxid in merged_conversion:
                    node_taxid = merged_conversion[node_taxid]
                n.add_props(sci_name = tax2name.get(node_taxid, getattr(n, taxid_attr, n.props.get(taxid_attr, ''))),
                               common_name = tax2common_name.get(node_taxid, ''),
                               lineage = tax2track.get(node_taxid, []),
                               rank = tax2rank.get(node_taxid, 'Unknown'),
                               named_lineage = [tax2name.get(tax, str(tax)) for tax in tax2track.get(node_taxid, [])])
            elif n.is_leaf:
                n.add_props(sci_name = getattr(n, taxid_attr, n.props.get(taxid_attr, 'NA')),
                               common_name = '',
                               lineage = [],
                               rank = 'Unknown',
                               named_lineage = [])
            else:
                if ignore_unclassified:
                    vectors = [lf.props.get('lineage') for lf in n2leaves[n] if lf.props.get('lineage')]
                else:
                    vectors = [lf.props.get('lineage') for lf in n2leaves[n]]
                lineage = self._common_lineage(vectors)
                ancestor = lineage[-1]
                n.add_props(sci_name = tax2name.get(ancestor, str(ancestor)),
                            common_name = tax2common_name.get(ancestor, ''),
                            taxid = ancestor,
                            lineage = lineage,
                            rank = tax2rank.get(ancestor, 'Unknown'),
                            named_lineage = [tax2name.get(tax, str(tax)) for tax in lineage])

        return tax2name, tax2track, tax2rank

    def _common_lineage(self, vectors):
        occurrence = defaultdict(int)
        pos = defaultdict(set)
        for v in vectors:
            for i, taxid in enumerate(v):
                occurrence[taxid] += 1
                pos[taxid].add(i)

        common = [taxid for taxid, ocu in occurrence.items() if ocu == len(vectors)]
        if not common:
            return [""]
        else:
            sorted_lineage = sorted(common, key=lambda x: min(pos[x]))
            return sorted_lineage

    def get_broken_branches(self, t, taxa_lineages, n2content=None):
        """Returns a list of NCBI lineage names that are not monophyletic in the
        provided tree, as well as the list of affected branches and their size.

        CURRENTLY EXPERIMENTAL
        """
        if not n2content:
            n2content = t.get_cached_content()

        tax2node = defaultdict(set)

        unknown = set()
        for leaf in t.iter_leaves():
            if leaf.sci_name.lower() != "unknown":
                lineage = taxa_lineages[leaf.taxid]
                for index, tax in enumerate(lineage):
                    tax2node[tax].add(leaf)
            else:
                unknown.add(leaf)

        broken_branches = defaultdict(set)
        broken_clades = set()
        for tax, leaves in tax2node.items():
            if len(leaves) > 1:
                common = t.get_common_ancestor(leaves)
            else:
                common = list(leaves)[0]
            if (leaves ^ set(n2content[common])) - unknown:
                broken_branches[common].add(tax)
                broken_clades.add(tax)

        broken_clade_sizes = [len(tax2node[tax]) for tax in broken_clades]

        return broken_branches, broken_clades, broken_clade_sizes


def load_ncbi_tree_from_dump(tar):
    from .. import Tree
    parent2child = {}
    name2node = {}
    node2taxname = {}
    synonyms = set()
    name2rank = {}
    node2common = {}
    print("Loading node names...")
    unique_nocase_synonyms = set()
    for line in tar.extractfile("names.dmp"):
        line = str(line.decode())
        fields =  [_f.strip() for _f in line.split("|")]
        nodename = fields[0]
        name_type = fields[3].lower()
        taxname = fields[1]

        # Clean up tax names so we make sure the don't include quotes. See https://github.com/etetoolkit/ete/issues/469
        taxname = taxname.rstrip('"').lstrip('"')

        if name_type == "scientific name":
            node2taxname[nodename] = taxname
        if name_type == "genbank common name":
            node2common[nodename] = taxname
        elif name_type in set(["synonym", "equivalent name", "genbank equivalent name",
                               "anamorph", "genbank synonym", "genbank anamorph", "teleomorph"]):

            # Keep track synonyms, but ignore duplicate case-insensitive names. See https://github.com/etetoolkit/ete/issues/469
            synonym_key = (nodename, taxname.lower())
            if synonym_key not in unique_nocase_synonyms:
                unique_nocase_synonyms.add(synonym_key)
                synonyms.add((nodename, taxname))

    print(len(node2taxname), "names loaded.")
    print(len(synonyms), "synonyms loaded.")

    print("Loading nodes...")
    for line in tar.extractfile("nodes.dmp"):
        line = str(line.decode())
        fields =  line.split("|")
        nodename = fields[0].strip()
        parentname = fields[1].strip()
        n = Tree()
        n.name = nodename
        #n.taxname = node2taxname[nodename]
        n.add_prop('taxname', node2taxname[nodename])
        if nodename in node2common:
            n.add_prop('common_name', node2taxname[nodename])
        n.add_prop('rank', fields[2].strip())
        parent2child[nodename] = parentname
        name2node[nodename] = n
    print(len(name2node), "nodes loaded.")

    print("Linking nodes...")
    for node in name2node:
       if node == "1":
           t = name2node[node]
       else:
           parent = parent2child[node]
           parent_node = name2node[parent]
           parent_node.add_child(name2node[node])
    print("Tree is loaded.")
    return t, synonyms

def generate_table(t):
    with open("taxa.tab", "w") as out:
        for j, n in enumerate(t.traverse()):
            if j % 1000 == 0:
                print("\r",j,"generating entries...", end=' ')
            temp_node = n
            track = []
            while temp_node:
                track.append(temp_node.name)
                temp_node = temp_node.up

            n_up_name = n.up.name if n.up else ""

            row = '\t'.join([n.name, n_up_name, n.props.get('taxname'),
                             n.props.get("common_name", ''), n.props.get("rank"),
                             ','.join(track)])

            print(row, file=out)

def update_db(dbfile, targz_file=None):
    basepath = os.path.split(dbfile)[0]
    if basepath and not os.path.exists(basepath):
        os.makedirs(basepath)

    if not targz_file:
        update_local_taxdump(DEFAULT_TAXDUMP)
        targz_file = DEFAULT_TAXDUMP

    tar = tarfile.open(targz_file, 'r')
    t, synonyms = load_ncbi_tree_from_dump(tar)
    prepostorder = [int(node.name) for post, node in t.iter_prepostorder()]
    pickle.dump(prepostorder, open(dbfile+'.traverse.pkl', "wb"), 2)

    print("Updating database: %s ..." %dbfile)
    generate_table(t)

    with open("syn.tab", "w") as SYN:
        SYN.write('\n'.join(["%s\t%s" %(v[0],v[1]) for v in synonyms]))

    with open("merged.tab", "w") as merged:
        for line in tar.extractfile("merged.dmp"):
            line = str(line.decode())
            out_line = '\t'.join([_f.strip() for _f in line.split('|')[:2]])
            merged.write(out_line+'\n')

    upload_data(dbfile)

    os.system("rm syn.tab merged.tab taxa.tab")


def update_local_taxdump(fname=DEFAULT_TAXDUMP):
    """Update contents of file fname with taxdump.tar.gz from the NCBI site."""
    url = 'https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz'

    if not os.path.exists(fname):
        print(f'Downloading {fname} from {url} ...')
        with open(fname, 'wb') as f:
            f.write(requests.get(url).content)
    else:
        md5_local = md5(open(fname, 'rb').read()).hexdigest()
        md5_remote = requests.get(url + '.md5').text.split()[0]

        if md5_local != md5_remote:
            print(f'Updating {fname} from {url} ...')
            with open(fname, 'wb') as f:
                f.write(requests.get(url).content)
        else:
            print(f'File {fname} is already up-to-date with {url} .')


def upload_data(dbfile):
    print()
    print('Uploading to', dbfile)
    basepath = os.path.split(dbfile)[0]
    if basepath and not os.path.exists(basepath):
        os.mkdir(basepath)

    db = sqlite3.connect(dbfile)

    create_cmd = """
    DROP TABLE IF EXISTS stats;
    DROP TABLE IF EXISTS species;
    DROP TABLE IF EXISTS synonym;
    DROP TABLE IF EXISTS merged;
    CREATE TABLE stats (version INT PRIMARY KEY);
    CREATE TABLE species (taxid INT PRIMARY KEY, parent INT, spname VARCHAR(50) COLLATE NOCASE, common VARCHAR(50) COLLATE NOCASE, rank VARCHAR(50), track TEXT);
    CREATE TABLE synonym (taxid INT,spname VARCHAR(50) COLLATE NOCASE, PRIMARY KEY (spname, taxid));
    CREATE TABLE merged (taxid_old INT, taxid_new INT);
    CREATE INDEX spname1 ON species (spname COLLATE NOCASE);
    CREATE INDEX spname2 ON synonym (spname COLLATE NOCASE);
    """
    for cmd in create_cmd.split(';'):
        db.execute(cmd)
    print()

    db.execute("INSERT INTO stats (version) VALUES (%d);" %DB_VERSION)
    db.commit()

    for i, line in enumerate(open("syn.tab")):
        if i % 5000 == 0 :
            print('\rInserting synonyms:     %6d' % i, end=' ', file=sys.stderr)
            sys.stderr.flush()
        taxid, spname = line.strip('\n').split('\t')
        db.execute("INSERT INTO synonym (taxid, spname) VALUES (?, ?);",
                   (taxid, spname))
    print()
    db.commit()
    for i, line in enumerate(open("merged.tab")):
        if i % 5000 == 0 :
            print('\rInserting taxid merges: %6d' % i, end=' ', file=sys.stderr)
            sys.stderr.flush()
        taxid_old, taxid_new = line.strip('\n').split('\t')
        db.execute("INSERT INTO merged (taxid_old, taxid_new) VALUES (?, ?);",
                   (taxid_old, taxid_new))
    print()
    db.commit()
    for i, line in enumerate(open("taxa.tab")):
        if i % 5000 == 0 :
            print('\rInserting taxids:      %6d' % i, end=' ', file=sys.stderr)
            sys.stderr.flush()
        taxid, parentid, spname, common, rank, lineage = line.strip('\n').split('\t')
        db.execute('INSERT INTO species (taxid, parent, spname, common, rank, track) '
                   'VALUES (?, ?, ?, ?, ?, ?);',
                   (taxid, parentid, spname, common, rank, lineage))
    print()
    db.commit()


if __name__ == "__main__":
    ncbi = NCBITaxa()

    a = ncbi.get_descendant_taxa("hominidae")
    print(a)
    print(ncbi.get_common_names(a))
    print(ncbi.get_topology(a))
    b = ncbi.get_descendant_taxa("homo", intermediate_nodes=True, collapse_subspecies=True)
    print(ncbi.get_taxid_translator(b))

    print(ncbi.get_common_names(b))
    #ncbi.update_taxonomy_database()
