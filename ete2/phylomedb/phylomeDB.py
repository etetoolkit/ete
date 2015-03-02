# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################


"""
'phylomedb' provides an access API to the data stored in the
phylogenetic database PhylomeDB *[1].

All methods to perform queries are implemented within the
PhylomeDBConnector class.

 *[1] PhylomeDB: a database for genome-wide collections of gene
 phylogenies Jaime Huerta-Cepas, Anibal Bueno, Joaquin Dopazo and Toni
 Gabaldon.

      PhylomeDB is a database of complete phylomes derived for
      different genomes within a specific taxonomic range. All
      phylomes in the database are built using a high-quality
      phylogenetic pipeline that includes evolutionary model testing
      and alignment trimming phases. For each genome, PhylomeDB
      provides the alignments, phylogentic trees and tree-based
      orthology predictions for every single encoded protein.
"""
import re
from string import strip
import MySQLdb
from ete2 import PhyloTree

__all__ = ["PhylomeDBConnector", "ROOTED_PHYLOMES"]

# This dictionary sets the default age dictionary (if any) must be
# used to root certain phylome trees.
ROOTED_PHYLOMES = {
    1: {
        # Basal eukariotes
        "Ath":10, # Arabidopsis thaliana
        "Cre":10,
        "Pfa":10,
        "Pyo":10,
        "Ddi":10,
        "Gth":10,
        "Lma":10, # leismania
        "Pte":10,
        # Fungi
        "Ago":9,
        "Cal":9,
        "Cgl":9,
        "Cne":9,
        "Dha":9,
        "Ecu":9,
        "Gze":9,
        "Kla":9,
        "Ncr":9,
        "Sce":9, # S.cerevisiae
        "Spb":9,
        "Yli":9,
        # metazoa non chordates
        "Aga":8, # Anopheles
        "Dme":8, # Drosophila melanogaster
        "Ame":8, # Apis meliferae
        "Cel":8, # Caenorabditis elegans
        "Cbr":8, # Caenorabditis brigssae
        # chordates non vertebrates
        "Cin":7, # Ciona intestinalis
        # vertebrates non tetrapodes
        "Dre":6, # Danio rerio
        "Tni":6, # Tetraodom
        "Fru":6, # Fugu rubripes
        # tetrapodes non birds nor mammals
        "Xtr":5, # Xenopus
        # birds
        "Gga":4, # Chicken
        # Mammals non primates
        "Mdo":3, # Monodelphis domestica
        "Mms":3, # Mouse
        "Rno":3, # Rat
        "Cfa":3, # Dog
        "Bta":3, # Cow
        # primates non hominids
        "Ptr":2, # chimp
        "Mmu":2, # Macaca
        # hominids
        "Hsa":1, # human
        },

    # Pea aphid Phylome
    16: {
        "Cel" :10, # C.elegans outgroup
        "Hsa" :9,  # Human outgroup
        "Cin" :9,  # Ciona outgroup
        "Dpu":7,
        "Dps":5,
        "Tca":5,
        "Phu":5,
        "Dme":5,
        "Api":5,
        "Dmo":5,
        "Nvi":5,
        "Dya":5,
        "Aga":5,
        "Cpi":5,
        "Bom":5,
        "Ame":5,
        "Aae":5
        }
    }

class PhylomeDBConnector(object):
    """ Reuturns a connector to a phylomeDB database.

    ARGUMENTS:
    ==========
    host: hostname in which phylomeDB is hosted.
    user: username to the database.
    passwd: password to connect database.
    port: port used to connect database.

    RETURNS:
    ========
    An object whose methods can be used to query the database.
  """
    def __init__(self, host="84.88.66.245", \
                   db="phylomeDB", \
                   user="public", \
                   passwd="public", \
                   port=3306):

        """ Connects to a phylomeDB database and returns an object to
        perform custom queries on it. """

        # Reads phylome config file
        self._SQLconnection = MySQLdb.connect(host = host,\
                                                user   = user,\
                                                passwd = passwd,\
                                                db     = db,\
                                                port   = int(port))

        self._SQL = self._SQLconnection.cursor()

        if user == "phyAdmin":
            self._trees_table    = "trees"
            self._algs_table     = "algs"
            self._phylomes_table = "phylomes"
        else:
            self._trees_table    = "trees_"+user
            self._algs_table     = "algs_"+user
            self._phylomes_table = "phylomes_"+user

    def _execute_block(self, cmd):
        """ Executes a multi-line SQL command and returns the nombre of
        affected rows. """
        commands = cmd.split(";")
        for c in commands:
            c = c.strip()
            if c != "":
                try:
                    rows = self._SQL.execute(c+";")
                except MySQLdb.Error:
                    raise
        return rows

    # Access API methods
    def get_longest_isoform(self, phyID):
        """ returns the protID of the """

        try:
            spc_code    = phyID[:3]
            prot_number = int(phyID[3:])
        except ValueError:
            raise ValueError, "invalid phylome protein ID"
        else:
            cmd = ' SELECT species, IF(gene="" OR gene=NULL,%s,protid) FROM proteins WHERE species="%s" AND (gene,proteome_id)=(SELECT gene, proteome_id FROM proteins WHERE species="%s" AND protid=%s) ORDER BY length(seq) DESC LIMIT 1; ' % (prot_number,spc_code,spc_code,prot_number)
            if self._SQL.execute(cmd):
                spc,protid = self._SQL.fetchone()
                return "%s%07d" % (spc,protid)
            else:
                return None

    def get_id_by_external(self, external):
        """ Returns the phylomeID of the given external ID"""

        command = 'SELECT species,protid from id_conversion where external_id="%s"' % (external)
        ids = []
        if self._SQL.execute(command):
            matches = self._SQL.fetchall()
            # Build phyprotID
            for m in matches:
                phyID = self.get_longest_isoform("%s%07d" % (m[0],m[1]))
                if phyID:
                    ids.append( phyID )
        return ids

    def get_id_translations(self, seqid):
        """ returns all the registered translations of a given seqid """

        cmd = 'SELECT external_db,external_id from id_conversion where species="%s" and protid=%d' % (seqid[:3],int(seqid[3:]))
        conversion = {}
        if self._SQL.execute(cmd):
            extids = self._SQL.fetchall()
            for db, eid in extids:
                conversion.setdefault(db, []).append(eid)
        return conversion

    def search_id(self, queryID):
        """ Returns a list of phylome protein Ids associated to the
        given external queryID. If queryID is a phylomeDB id, it
        returns the longest isoform associated to the queryID's gene
        """
        queryID = queryID.strip()

        # This is to avoid weird queryIDs which make create slow or
        # invalid MYSQL queries
        QUERYID_GENERAL_REGEXP_FILTER = "^[\w\d\-_,;:.|#@\/\\\()'<>!]+$"
        QUERYID_INTERNAL_ID_REGEXP_FILTER = "^\w{3}\d{7}$"

        phyID_matches = []
        # First check if id is a phylomeID
        if re.match(QUERYID_INTERNAL_ID_REGEXP_FILTER, queryID):
            phyID = self.get_longest_isoform(queryID)
            phyID_matches.append(phyID)

        elif re.match(QUERYID_GENERAL_REGEXP_FILTER, queryID):
            # Second checks if id is the original name or gene for of a phylome ID
            cmd = 'SELECT species,protid from proteins where name="%s" or gene="%s"' % (queryID,queryID)
            if self._SQL.execute(cmd):
                for spc_code, protid  in self._SQL.fetchall():
                    phyID = self.get_longest_isoform("%s%07d" % (spc_code,protid))
                    phyID_matches.append( phyID )

            # Last checks if id is in the id conversion table and adds the resulting mathes
            hits = self.get_id_by_external(queryID)
            if hits:
                phyID_matches.extend(hits)

        return phyID_matches

    def get_proteomes(self):
        """ Returns all current available proteomes"""
        cmd = 'SELECT * FROM proteomes'
        if self._SQL.execute(cmd):
            return self._SQL.fetchall()

    def get_species(self):
        """ Returns all current available species"""

        cmd = 'SELECT * FROM species'
        if self._SQL.execute(cmd):
            return self._SQL.fetchall()
    def get_phylomes(self):
        """ Returns all current available phylomes """
        cmd = 'SELECT phylome_id,seed_proteome,proteomes,DATE(ts),name,description,comments FROM %s' %(self._phylomes_table)
        phylomes = {}
        if self._SQL.execute(cmd):
            for phylo in self._SQL.fetchall():
                phylome_id = phylo[0]
                phylomes[phylome_id]={}
                phylomes[phylome_id]["seed_proteome"] = phylo[1]
                phylomes[phylome_id]["seed_species"]  = phylo[1][:3]
                phylomes[phylome_id]["proteomes"]     = phylo[2]
                phylomes[phylome_id]["name"]          = phylo[4]
                phylomes[phylome_id]["description"]   = phylo[5]
                phylomes[phylome_id]["date"]          = phylo[3]
                phylomes[phylome_id]["comments"]      = phylo[6]
        return phylomes

    def get_proteomes_in_phylome(self,phylome_id):
        """ Returns a list of proteomes associated to a given phylome_id"""

        cmd = 'SELECT proteomes FROM %s WHERE phylome_id="%s" ' \
            % (self._phylomes_table, phylome_id)
        self._SQL.execute(cmd)
        entries = self._SQL.fetchone()
        if entries:
            proteomes_string = map(strip, entries[0].split(","))
        else:
            proteomes_string = None
        return proteomes_string

    def get_seqids_in_proteome(self, proteome_id, filter_isoforms=True):
        """ Returns all sequences of a given proteome """

        seqids = []
        if filter_isoforms:
            cmd = 'SELECT species,protid,gene,seq FROM proteins WHERE proteome_id="%s" AND species="%s" ' \
                % (proteome_id[3:],proteome_id[:3])
            if self._SQL.execute(cmd):
                entries = self._SQL.fetchall()
                largest_isoforms = {}
                unknown_counter = 0
                for spcs,protid,gene,seq in entries:
                    gene = gene.strip()
                    unknown_counter += 1
                    if not gene:
                        gene="phyunknown%d" % unknown_counter
                        unknown_counter += 1
                    if gene not in largest_isoforms:
                        largest_isoforms[gene] = (spcs,protid,gene,seq)
                    elif len(seq) > len(largest_isoforms[gene][3]):
                        largest_isoforms[gene] = (spcs,protid,gene,seq)
                seqids = ["%s%07d"%(v[0], v[1]) for v in largest_isoforms.values()]
        else:
            cmd = 'SELECT species,protid FROM proteins WHERE proteome_id="%s" AND species="%s" ' \
                % (proteome_id[3:],proteome_id[:3])
            if self._SQL.execute(cmd):
                seqids = ["%s%07d"%(spc,protid) for spc,protid in self._SQL.fetchall()]

        return seqids

    def get_seqs_in_proteome(self, proteome_id, filter_isoforms=True):
        cmd = 'SELECT species,protid,gene,seq FROM proteins WHERE proteome_id="%s" AND species="%s" ' \
            % (proteome_id[3:],proteome_id[:3])
        if self._SQL.execute(cmd):
            entries = self._SQL.fetchall()
            if filter_isoforms:
                largest_isoforms = {}
                unknown_counter = 0
                for spcs,protid,gene,seq in entries:
                    gene = gene.strip()
                    unknown_counter += 1
                    if not gene:
                        gene="phyunknown%d" % unknown_counter
                        unknown_counter += 1
                    if gene not in largest_isoforms:
                        largest_isoforms[gene] = (spcs,protid,gene,seq)
                    elif len(seq) > len(largest_isoforms[gene][3]):
                        largest_isoforms[gene] = (spcs,protid,gene,seq)
                seqs = largest_isoforms.values()
            else:
                seqs = entries
        else:
            seqs = None

        return seqs

    def get_proteome_info(self,proteome_id):
        """ Returns all info about a registered proteome"""

        cmd = 'SELECT proteome_id,species,source,comments,date FROM proteomes WHERE proteome_id ="%s" AND species="%s" ' \
            % (proteome_id[3:],proteome_id[:3])
        info = {}
        if self._SQL.execute(cmd):
            entry = self._SQL.fetchone()
            info["proteome_id"] = entry[0]
            info["species"] = entry[1]
            info["source"] = entry[2]
            info["comments"] = entry[3]
            info["date"] = entry[4]
        return info

    def get_seqid_info(self, protid):
        """ Returns orginal info about a given protid"""
        cmd = 'SELECT species,protid,proteome_id,name,gene,comments,seq FROM proteins WHERE species="%s" and protid="%s"' \
            % (protid[:3],protid[3:])

        info = {}
        if self._SQL.execute(cmd):
            entry = self._SQL.fetchone()
            info["species"] = entry[0]
            info["seqid"] = entry[1]
            info["proteome_id"] = entry[2]
            info["name"] = entry[3]
            info["gene"] = entry[4]
            info["comments"] = entry[5]
            info["seq"] = entry[6]
        return info

    def get_phylome_info(self, phylomeid):
        """ Returns info on a given phylome"""
        cmd = 'SELECT seed_proteome,proteomes,DATE(ts),name,description,comments FROM %s WHERE phylome_id="%s" ' %\
            (self._phylomes_table, phylomeid)
        info = {}
        if self._SQL.execute(cmd):
            all_info = self._SQL.fetchone()
            info["id"]            = int(phylomeid)
            info["seed_proteome"] = all_info[0]
            info["seed_species"]  = all_info[0][:3]
            info["proteomes"]     = all_info[1]
            info["name"]          = all_info[3]
            info["description"]   = all_info[4]
            info["date"]          = all_info[2]
            info["comments"]      = all_info[5]
        return info

    def get_species_info(self, taxid_or_code):
        """ Returns all information on a given species_code"""

        command = 'SELECT taxid,code,name from species where taxid="%s"' % (taxid_or_code)
        if self._SQL.execute(command):
            return self._SQL.fetchone()
        else:
            command = 'SELECT taxid,code,name from species where code="%s"' % (taxid_or_code)
            info = {}
            if self._SQL.execute(command):
                entry = self._SQL.fetchone()
                info["taxid"] = entry[0]
                info["code"] = entry[1]
                info["name"] = entry[2]
            return info

    def get_seed_ids(self, phylome_id, filter_isoforms=True):
        # WORKS VERY SLOW !!
        cmd = 'SELECT seed_proteome FROM %s WHERE phylome_id="%s";' % (self._phylomes_table, phylome_id)
        if self._SQL.execute(cmd):
            seed_proteome = self._SQL.fetchone()[0]
            seedids = self.get_seqids_in_proteome(seed_proteome, filter_isoforms=filter_isoforms)
        else:
            seedids = []
        return seedids

    def get_collateral_seeds(self, seqid):
        cmd = 'SELECT seed_id, phylome_id FROM seed_friends WHERE species="%s" and protid="%s";' %\
            (seqid[:3],int(seqid[3:]))
        if self._SQL.execute(cmd):
            return self._SQL.fetchall()
        else:
            return []

    def get_available_trees(self, seqid, collateral=True):
        trees = {seqid:{}}
        cmd = 'SELECT phylome_id, method FROM %s WHERE species="%s" AND protid="%s" ' \
            %(self._trees_table, seqid[:3], seqid[3:])
        if self._SQL.execute(cmd):
            for phylome_id, method in self._SQL.fetchall():
                if phylome_id in trees[seqid]:
                    trees[seqid][phylome_id].append(method)
                else:
                    trees[seqid][phylome_id] = [method]

        if collateral:
            for cseed, phyid in self.get_collateral_seeds(seqid):
                cmd = 'SELECT method FROM %s WHERE species="%s" AND protid="%s" and phylome_id ="%s" ' \
                    %(self._trees_table, cseed[:3], cseed[3:], phyid)
                if self._SQL.execute(cmd):
                    trees[cseed] = {}
                    trees[cseed][phyid] = [method[0] for method in self._SQL.fetchall()]
        return trees

    def get_available_trees_by_phylome(self, seqid, collateral=True):
        trees = {seqid:{}}
        cmd = 'SELECT phylome_id, method FROM %s WHERE species="%s" AND protid="%s" ' \
            %(self._trees_table, seqid[:3], seqid[3:])

        phyid2trees = {}
        if self._SQL.execute(cmd):
            for phylome_id, method in self._SQL.fetchall():
                if phylome_id not in phyid2trees:
                    phyid2trees[phylome_id] = {seqid: [method]}
                elif seqid in phyid2trees[phylome_id]:
                    phyid2trees[phylome_id][seqid].append(method)
                elif seqid not in phyid2trees[phylome_id]:
                    phyid2trees[phylome_id][seqid] = [method]

        if collateral:
            for cseed, phyid in self.get_collateral_seeds(seqid):
                cmd = 'SELECT method FROM %s WHERE species="%s" AND protid="%s" and phylome_id ="%s" ' \
                    %(self._trees_table, cseed[:3], cseed[3:], phyid)
                if self._SQL.execute(cmd):
                    phyid2trees.setdefault(phyid, {})[cseed] = [method[0] for method in self._SQL.fetchall()]

        return phyid2trees

    def get_available_trees_in_phylome(self, seqid, phylomeid):
        trees = {seqid:{}}
        cmd = 'SELECT method, lk FROM %s WHERE species="%s" AND protid="%s" AND phylome_id=%s' \
            %(self._trees_table, seqid[:3], seqid[3:], phylomeid)
        if self._SQL.execute(cmd):
            return dict(self._SQL.fetchall())
        else:
            return {}

    def get_tree(self, protid, method, phylome_id):
        """ Returns the method-tree associated to a given protid. """

        cmd = 'SELECT newick,lk FROM %s WHERE phylome_id=%s AND species="%s" AND protid="%s" AND method ="%s"' %\
            (self._trees_table, phylome_id, protid[:3],protid[3:],method)
        if self._SQL.execute(cmd):
            entry = self._SQL.fetchone()
            nw = entry[0]
            lk = float(entry[1])
            t  = PhyloTree(nw)
        else:
            t  = None
            lk = None
        return t,lk
    def get_best_tree(self, protid, phylome_id):
        """ Returns the winner ML tree"""

        likelihoods    = {}
        winner_model   = None
        winner_lk      = None
        winner_newick  = None
        t = None
        command ='SELECT newick,method,lk FROM %s WHERE phylome_id=%s AND species="%s" and protid="%s";' \
            % (self._trees_table,phylome_id, protid[:3], protid[3:])
        self._SQL.execute(command)
        result = self._SQL.fetchall()
        for r in result:
            nw,m,lk = r
            if lk < 0:
                likelihoods[m] = lk
                if  winner_lk==None or lk > winner_lk:
                    winner_lk     = lk
                    winner_model  = m
                    winner_newick = nw
        if winner_newick:
            t = PhyloTree(winner_newick)
        return winner_model,likelihoods,t
    def get_algs(self, protid, phylome_id):
        """ Given a protID, it returns a tuple with the raw_alg, clean_alg and
        the number of seqs included.
        """

        command = 'SELECT raw_alg,clean_alg,seqnumber FROM %s WHERE phylome_id=%s AND species="%s" AND protid="%s"' %\
            (self._algs_table, phylome_id, protid[:3],protid[3:])
        self._SQL.execute(command)
        return self._SQL.fetchone()

    def get_raw_alg(self, protid, phylome_id):
        """ Given a protID, it returns a tuple with the raw_alg and
        the number of seqs included.
        """

        command = 'SELECT raw_alg,seqnumber FROM %s WHERE phylome_id=%s AND species="%s" AND protid="%s"' %\
            (self._algs_table, phylome_id, protid[:3],protid[3:])
        if self._SQL.execute(command):
            return self._SQL.fetchone()

    def get_clean_alg(self, protid, phylome_id):
        """ Given a protID, it returns a tuple with the clean_alg and
        the number of seqs included.
        """

        command = 'SELECT clean_alg,seqnumber FROM %s WHERE phylome_id=%s AND species="%s" AND protid="%s"' %\
            (self._algs_table, phylome_id, protid[:3],protid[3:])
        if self._SQL.execute(command):
            return self._SQL.fetchone()


    def get_phylome_trees(self, phylomeid):
        cmd = 'SELECT species, protid, method from %s where phylome_id=%s' \
            %(self._trees_table,phylomeid)
        method2seqid = {}
        if self._SQL.execute(cmd):
            for sp, protid, method in self._SQL.fetchall():
                method2seqid.setdefault(method, []).append("%s%07d" %(sp, protid))
        return method2seqid
    def get_phylome_algs(self, phylomeid):
        cmd = 'SELECT species, protid from %s where phylome_id =%s' \
            %(self._algs_table, phylomeid)
        if self._SQL.execute(cmd):
            return self._SQL.fetchall()
        else:
            return ()

    def count_trees(self, phylomeid):
        cmd = 'SELECT method,count(*) from %s where phylome_id=%s GROUP BY method' \
            %(self._trees_table,phylomeid)
        counter = {}
        if self._SQL.execute(cmd):
            for method, n in self._SQL.fetchall():
                counter[method] = n
        return counter

    def count_algs(self, phylomeid):
        cmd = 'SELECT count(*) from %s where phylome_id=%s;' \
            %(self._algs_table,phylomeid)
        if self._SQL.execute(cmd):
            return  self._SQL.fetchone()[0]
        else:
            return 0

    def get_orthologs(self, seqid, sp2age=None):
        """ Returns the orthology predictions of the given seqid in all
        phylomes.

        Only seed trees will be used to detect orthologies, and trees will
        be rooted as the default policy defined in the API. If phylome has
        an asociated dictionary of species ages,
        root_to_farthest_oldest_leaf algorithm will be applied. Otherwise,
        midpoint is used.

        You can also provide your own species age dictionary to force the
        rooting of the trees according to such data.


        ARGUMENTS:
        ==========

         seqid: the ID of a sequence in the phylomeDB format.
          i.e. Hsa0000001

         sp2age: a dictionary of species code ages (key=species_code,
          value=age).  i.e. {"Hsa":1, "Dme":4, "Ath":10}

        RETURNS:
        =========

        A dictionary of orthologs and inparalogs found in each scanned
        phylomes.

         """
        phylome2or = {}
        if type(seqid) == str:
            seqid = [seqid]
        for sid in seqid:
            avail_trees = self.get_available_trees(sid)
            for seedid, phylomes in avail_trees.iteritems():
                if seedid != sid:
                    continue # Skips collateral trees!!
                for phyid in phylomes:
                    # Get the tree for each seed id
                    method, lks, t = self.get_best_tree(seedid, phyid)
                    # Roots the tree according to a predefined criterion
                    if sp2age is not None:
                        outgroup = t.get_farthest_oldest_leaf(sp2age)
                        t.set_outgroup(outgroup)
                    elif phyid in ROOTED_PHYLOMES:
                        outgroup = t.get_farthest_oldest_leaf( ROOTED_PHYLOMES[phyid] )
                        t.set_outgroup(outgroup)
                    else:
                        t.set_outgroup(t.get_midpoint_outgroup())

                    # Catches the node for our id (not necesarily the
                    # seedid) and obtains its evol events
                    seed_node = t.get_leaves_by_name(sid)[0]
                    evol_events = seed_node.get_my_evol_events()
                    # Predictions are sorted by species.
                    sp2or = {}
                    sp2in = {}
                    or2in = {}
                    for e in filter(lambda x: x.etype=="S", evol_events):
                        for o in e.orthologs:
                            sp = o[:3]
                            # orthologs sorted by species
                            sp2or.setdefault(sp, set([])).add(o)

                            # inparalogs sorted by orthologs
                            or2in.setdefault(o, set([])).update(e.inparalogs)

                            # inparalogs sorted by orthologs
                            sp2in.setdefault(sp, set([])).update(e.inparalogs)

                    phylome2or[phyid] = [sp2or, sp2in, or2in]
        return phylome2or
