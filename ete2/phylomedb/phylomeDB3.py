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
'phylomeDB3' provides an access API to the data stored in the phylogenetic
database PhylomeDB *[1][2].

Methods to perform queries are implemented within the PhylomeDB3Connector class.

 *[1] PhylomeDB: a database for genome-wide collections of gene phylogenies.
      Jaime Huerta-Cepas, Anibal Bueno, Joaquin Dopazo and Toni Gabaldon.
      Nucleic acids research (database issue). 2008.

 *[2] PhylomeDB v3.0: an expanding repository of genome-wide collections of
      trees, alignments and phylogeny-based orthology and paralogy predictions.
      Jaime Huerta-Cepas, Salvador Capella-Gutierrez, Leszek P. Pryszcz, Ivan
      Denisov, Diego Kormes, Marina Marcet-Houben and Toni Gabaldon T.
      Nucleic acids research (database issue). 2010.

      PhylomeDB is a database of complete phylomes derived for different genomes
      within a specific taxonomic range. All phylomes in the database are built
      using a high-quality phylogenetic pipeline that includes evolutionary
      model testing and alignment trimming phases. For each genome, PhylomeDB
      provides the alignments, phylogentic trees and tree-based orthology
      predictions for every single encoded protein.
"""
import re
import MySQLdb
from string import strip
from ete2 import PhyloTree

def extract_species_name(name):
  return name.split("_")[1]

ID_PATTERN = re.compile("^[Pp][Hh][Yy]\w{7}(_\w{2,7})?$")
ITERABLE_TYPES = set([list, set, tuple, frozenset])

__all__ = ["PhylomeDB3Connector"]


class Phylome(object):
  def __str__(self): 
    info = "Phylome %s (%s)\n" %(self.phyid,self.name) +\
        " seed species: %s\n" %(self.tax2name[self.seed_taxid]) +\
        " seed proteome: %s\n" %(self.seed_proteome) +\
        " Species: %d\n" %len(self.species) +\
        " Seed sequences: %d\n" %len(self.seed_ids) +\
        " Trees: %d\n" %len(self.trees) +\
        " Proteome list: %s\n" %','.join(self.proteomes) 
    return info

  def __init__(self, phyid, connector, filter_isoforms=True):
    self.filter_isoforms = filter_isoforms
    self._conn = connector
    self._dsql = connector.cursor(MySQLdb.cursors.DictCursor)
    self._lsql = connector.cursor(MySQLdb.cursors.Cursor)

    # Get seed ids
    cmd = 'SELECT seed_taxid, seed_version, name, description, comments FROM phylome' +\
        ' WHERE phylome_id = %s' % (phyid)
    self._dsql.execute(cmd)
    phyinfo = self._dsql.fetchone()
    self.phyid = phyid 
    self.seed_taxid = phyinfo["seed_taxid"]
    self.prot_vs = phyinfo["seed_version"]
    self.name = phyinfo["name"]
    self.description = phyinfo["description"]
    # Phylome content
    cmd = 'SELECT taxid, version FROM phylome_content' +\
        ' WHERE phylome_id = %s' % (phyid)
    self._lsql.execute(cmd)
    phycontent = self._lsql.fetchall()
    self.species = [int(e[0]) for e in phycontent]    

    # Species info
    cmd = 'SELECT taxid, code, name FROM species' +\
        ' WHERE taxid IN (%s);' %','.join(map(str, self.species))
    self._lsql.execute(cmd)
    sp_info = self._lsql.fetchall()
    self.tax2name = {}
    self.tax2code = {}
    self.code2tax = {}
    for taxid, code, name in sp_info:
      self.tax2name[taxid] = name
      self.tax2code[taxid] = code
      self.code2tax[code] = taxid
    self.proteomes = [self.tax2code[e[0]]+str(e[1]) for e in phycontent] 
    self.seed_proteome = "%s%d" %(self.tax2code[self.seed_taxid], self.prot_vs)

    # Seed ids
    if self.filter_isoforms:
      cmd =  'SELECT DISTINCT CONCAT("Phy", i.longest, "_", s.code) AS protid '
      cmd += 'FROM protein AS p, isoform AS i, species AS s WHERE p.taxid = '
      cmd += '%s AND p.version = %s AND p.protid = i.isoform' % (self.seed_taxid, self.prot_vs)
      cmd += ' AND p.version = i.version AND p.taxid = s.taxid'
    else:
      cmd =  'SELECT DISTINCT CONCAT("Phy", protid, "_", code) AS protid FROM '
      cmd += 'protein AS p, species AS s WHERE p.taxid = %s AND p.' % (self.seed_taxid)
      cmd += 'version = %s AND p.taxid = s.taxid' % (self.prot_vs)
    
    self._lsql.execute(cmd)
    self.seed_ids = [e[0] for e in self._lsql.fetchall()]
    self.load_trees()

  def load_trees(self, seqnames=None, model="best_lk", anotate_trees = True):
    """
    Returns all newick tree for the given set of seqnames and
    model. If no seqnames are provided, all available trees in the
    phylome is returned. 
    """
    def clean_name(name):
      quote = lambda x: '"%s"' %x
      m = re.search("Phy(\w{7})_[\w\d]+", name)
      if m: 
        return quote(m.groups()[0])
     
    if not seqnames: 
      seqids =  map(clean_name, self.seed_ids)
    else:
      seqids =  map(clean_name, seqnames)
      
    tree_table = "tree"
    cmd = 'SELECT  temp.protid, temp.method, temp.lk, temp.newick from ' +\
        ' (SELECT T.protid , T.method, T.newick, T.lk FROM %s AS T WHERE' %(tree_table) +\
        ' T.phylome_id = %s AND T.protid IN (%s)' %(self.phyid, ','.join(seqids)) +\
        ' ORDER BY lk DESC) AS temp GROUP BY protid; '

    self.trees = {}
    if self._lsql.execute(cmd):
      seed_code = self.tax2code[self.seed_taxid]
      for protid, method, lk, nw in self._lsql.fetchall():
        seqid = "Phy%s_%s" %(protid, seed_code)
        self.trees[seqid] = [nw, method, lk]
        #t.add_features(lk=lk, method=method)

  def get_algs(self, seqid, atype="clean"):
    pass

  def get_seed_species(self):
    pass


class PhylomeDB(object):
  def __init__(self, host = "84.88.66.245", db = "phylomedb_3", user = "public",
    passwd = "public", port = 3306):
    """ Connect to a phylomeDB database and return an object to perform queries
        to the database.
    """
    # Establish the connection to the MySQL database where phylomeDB is stored.
    try:
      self._SQLconnection = MySQLdb.connect(host = host, user = user, passwd = \
        passwd, db = db, port = int(port))
    except:
      raise NameError("ERROR: Check your connection parameters")

    self._SQL = self._SQLconnection.cursor(MySQLdb.cursors.DictCursor)

    # Store the connection parameters to use it if the connection is lost.
    self.db = db
    self.host = host
    self.user = user
    self.port = port
    self.passwd = passwd

    # Define the different database views depending on the user profile
    self._trees = "tree_public"
    self._algs = "alignment_public"
    self._phylomes = "phylome_public"
    self._phy_content = "phycontent_public"

  def get_phylome(self, phyid):
    pass

  def get_proteomes(self, protids=[]):
    pass

  def get_seqs(self, seqids=[]):
    'get aa sequence of seqids'
    pass
  
  def search_trees(self, seqid, include_collateral=True):
    'Returns all available trees for seqid'
    pass

  




class PhylomeDB3Connector(object):
  """ Returns a connector to a phylomeDB3 database.

  ARGUMENTS:
  ==========
    db: database name in the host server.
    host: hostname in which phylomeDB is hosted.
    user: username to the database.
    port: port used to connect database.
    passwd: password to connect database.

  RETURNS:
  ========
    An object whose methods can be used to query the database.
  """

  #########
  def _get_phylome(self, phyid):
    return Phylome(phyid, connector = self._SQLconnection)

  ##########

  def __init__(self, host = "84.88.66.245", db = "phylomedb_3", user = "public",
    passwd = "public", port = 3306):
    """ Connect to a phylomeDB database and return an object to perform queries
        to the database.
    """

    # Establish the connection to the MySQL database where phylomeDB is stored.
    try:
      self._SQLconnection = MySQLdb.connect(host = host, user = user, passwd = \
        passwd, db = db, port = int(port))
    except:
      raise NameError("ERROR: Check your connection parameters")

    self._SQL = self._SQLconnection.cursor(MySQLdb.cursors.DictCursor)

    # Store the connection parameters to use it if the connection is lost.
    self.db = db
    self.host = host
    self.user = user
    self.port = port
    self.passwd = passwd

    # Define the different database views depending on the user profile
    self._trees = "tree_public"
    self._algs = "alignment_public"
    self._phylomes = "phylome_public"
    self._phy_content = "phycontent_public"

  def __execute__(self, command):
    """ Check whether a given connection is still open or not. If the connection
        has been closed by the server, try to recover it. Then, execute the
        input MySQL query
    """

    ## Try to either refresh an open cursor or reconnect to the database.
    try:
      self._SQL = self._SQLconnection.cursor(MySQLdb.cursors.DictCursor)
    except:
      try:
        self._SQLconnection = MySQLdb.connect(host = self.host,  db = self.db, \
          user = self.user, passwd = self.passwd, port = int(self.port))
      except:
        raise NameError("ERROR: Impossible to reconnect to the database")
      else:
        self._SQL = self._SQLconnection.cursor(MySQLdb.cursors.DictCursor)

    ## If it is possible to get a cursor, execute the command
    return self._SQL.execute(command)

  def __execute_block__(self, commands):
    """ Executes a multi-line MySQL query
    """

    ## Retrieve the different MySQL lines and split it in an appropiate way
    for query in [l for l in map(strip, commands.split(";")) if l]:
      if not self.__execute__(query):
        raise NameError("__execute_block__ An error occurred during a MySQL op")

  def __fomat_MySQL_to_dict__(self, index, dict):
    """ Takes as an input the result of a MySQL query and returns a dictionary
        using as a key one of the values from the MySQL results
    """

    ## Check whether the input data has the appropiate format <a tuple of dicts>
    ## Check as well if the key is present inside of each dict
    if type(dict) != tuple:
      msg = "__format_MySQL_to_dict__ Check the input structure datatype. "
      raise NameError(("%s It should be a 'tuple'") % (msg))
    for entry in dict:
      if not index in entry:
        raise NameError("__format_MySQL_to_dict__ Define the index")

    formatted_dict = {}
    ## Format the input data
    for entry in dict:
      formatted_dict[entry[index]] = entry
      del formatted_dict[entry[index]][index]
    return formatted_dict

  def __parser_ids__(self, ids):
    """ Returns a string with the input id/s ready to be used in any MySQL query
    """
    if not ids:
      raise NameError(("__parser_ids__: Check your input data '%s'") % str(ids))
    # Define a function to manage the different ids
    parser = lambda id: id[3:10] if ID_PATTERN.match(id) else None

    ids = [ids] if type(ids) == str else ids
    ## If the ids belongs to one of the predefined iterable types,
    ## try to convert each member in a valid phylomeDB code
    if type(ids) in ITERABLE_TYPES:
      parsed = ', ' .join(['"%s"' % parser(n) for n in ids if parser(n)])
      return parsed if parsed else None

    raise NameError(("__parser_ids__: Check your input data '%s'") % str(ids))

  def __check_input_parameter__(self, **kargs):
    """ Check the different input parameters
    """

    ## Define the available checks
    valid_keys = set(["str_number", "single_id", "list_id", "code", "string", \
      "boolean", "number"])

    ## Check that all input keys have associated an verification clause
    if set(kargs) - valid_keys != set():
      raise NameError("check_input_parameter: Invalid datatype")

    ## Check whether all input parameters has a value
    ## Although it is permitted for some 'keys' have 'None' as a value
    for key in kargs:
      if key not in ["number", "string"] and not kargs[key]:
        if kargs[key] not in [0, "", False]:
          return False

    ## Check whether the value is either a positive integer number
    if "number" in kargs:
      if kargs["number"]:
        if not str(kargs["number"]).isdigit() or str(kargs["number"]) == "0":
          return False
    ## ... or a integer number greater or equal to zero
    if "str_number" in kargs and not str(kargs["str_number"]).isdigit():
      return False
    ## ... or a boolean number
    if "boolean" in kargs and type(kargs["boolean"]) != bool:
      return False

    ## Check whether the input parameter should be an single phylomeDB ID
    if "single_id" in kargs:
      if not self.__parser_ids__(kargs["single_id"]) or \
        type(kargs["single_id"]) != str:
        return False
    ## ... or it could be a list of, at least, phylomeDB IDs
    if "list_id" in kargs and not self.__parser_ids__(kargs["list_id"]):
      return False

    ## Check if a single string has been given as an input parameter
    if "string" in kargs:
      if kargs["string"]:
        if type(kargs["string"]) != str or len(kargs["string"].split()) > 1:
          return False

    ## Return true if and only if all input parameters are well-constructed
    return True

  def get_external_ids(self, ids):
    """ Returns all the external IDs registered in the 'external_id' table that
        are associated to the input phylomeDB IDs
    """

    ids = self.__parser_ids__(ids)
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", s.code) as protid, '
    cmd += 'external_db AS db, external_id AS id FROM protein AS p, species AS '
    cmd += 's, external_id AS ex WHERE p.protid IN (%s) AND p.taxid = ' % (ids)
    cmd += 's.taxid AND p.protid = ex.protid'

    external_ids = {}
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        external_ids.setdefault(row["protid"], {})
        external_ids[row["protid"]].setdefault(row["db"], set()).add(row["id"])

    for protid in external_ids:
      for key in external_ids[protid]:
        external_ids[protid][key] = list(external_ids[protid][key])

    return external_ids

  def get_go_ids(self, ids):
    """ Returns all available GO Terms associated to the input phylomeDB IDs
    """

    ids = self.__parser_ids__(ids)
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", s.code) as protid, '
    cmd += 'external_db AS db, CONCAT("GO:", go_term) AS go FROM protein AS p, '
    cmd += 'species AS s, go WHERE p.protid IN (%s) AND p.taxid = s.' % (ids)
    cmd += 'taxid AND p.protid = go.protid'

    external_ids = {}
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        external_ids.setdefault(row["protid"], {})
        external_ids[row["protid"]].setdefault(row["db"], set()).add(row["go"])

    for protid in external_ids:
      for key in external_ids[protid]:
        external_ids[protid][key] = list(external_ids[protid][key])

    return external_ids

  def get_old_phylomedb_ids(self, ids):
    """ Returns all old phylomeDB IDs associated to each of the input phylomeDB
        IDs
    """

    ids = self.__parser_ids__(ids)
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", s.code) as protid, '
    cmd += 'CONCAT(old_code, LPAD(old_protid, 7, "0")) AS old_code FROM protein'
    cmd += ' AS p, species AS s, old_protein AS old WHERE p.protid IN '
    cmd += '(%s) AND p.taxid = s.taxid AND p.protid = old.protid' % (ids)

    old_ids = {}
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        old_ids.setdefault(row["protid"], {}).setdefault("old_phylomedb", set())
        old_ids[row["protid"]]["old_phylomedb"].add(row["old_code"])

    for protid in old_ids:
      for key in old_ids[protid]:
        old_ids[protid][key] = list(old_ids[protid][key])

    return old_ids

  def get_prot_gene_names(self, ids):
    """ Returns all possible protein and gene names associated to the input
        phylomeDB IDs
    """

    ids = self.__parser_ids__(ids)
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", s.code) as protid, '
    cmd += 'prot_name, gene_name FROM protein AS p, species AS s WHERE p.protid'
    cmd += ' IN (%s) AND p.taxid = s.taxid' % (ids)

    name = {}
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        if row["prot_name"]:
          name.setdefault(row["protid"], {}).setdefault("protein_name", set())
          name[row["protid"]]["protein_name"].add(row["prot_name"])
        if row["gene_name"]:
          name.setdefault(row["protid"], {}).setdefault("gene_name", set())
          name[row["protid"]]["gene_name"].add(row["gene_name"])

    for protid in name:
      for key in name[protid]:
        name[protid][key] = list(name[protid][key])

    return name

  def get_new_phylomedb_id(self, old_id):
    """ Return the conversion between an old phylomeDB ID and a new one
    """

    # Check whether the input code is a valid former phylomeDB id or not
    QUERY_OLD_REGEXP_FILTER = "^\w{3}\d{1,}$"
    if not re.match(QUERY_OLD_REGEXP_FILTER, old_id):
      return None

    # Look if the given code can be mapped into the phylomeDB dabatase
    cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) as protid FROM old_'
    cmd += 'protein AS p, species AS s WHERE (s.taxid = p.taxid AND p.old_code '
    cmd += '= "%s" AND p.old_protid = %s)' % (old_id[:3], old_id[3:])

    if self.__execute__(cmd):
      return self._SQL.fetchone()["protid"]
    return None

  def get_info_homologous_seqs(self, protid, phylome_id, tree = None, \
    tree_method = False, sequence = False):
    """ Return all the available information for a given set of homologous
        sequences extracted from a tree from a given phylome.
    """

    ## Depending on the input parameters, recover the best tree for the
    ## input phylomeDB ID in the input phylomeDB. Otherwise, the function
    ## will try to recover the tree reconstructed under the model specific
    data = {}

    if tree == None:
      tree_db = self.get_tree(protid, phylome_id, best_tree = True)

    elif tree and not tree_method:
      tree_db = self.get_tree(protid, phylome_id, best_tree = True)

    elif tree and tree_method:
      tree_db = self.get_tree(protid, phylome_id, method = tree_method)

    ## Check whether it has been possible to recover a tree from the database
    if not tree_db:
      return data
    else:
      method = tree_db.keys()[0]

    ## If it has been required, store the tree in an appropiate data structure.
    if tree:
      data.setdefault("tree", {})
      data["tree"]["method"] = method
      data["tree"]["lk"] = tree_db[method]["lk"]
      data["tree"]["tree"] = tree_db[method]["tree"]
      data["tree"]["best"] = True if not tree_method else False

    ## Recover the leaf names taking into account that there is information
    ## associated to the sequence while there is another information associated
    ## for each copy of the sequence.
    leaves = tree_db[method]["tree"].get_leaf_names()
    ids = set(["_".join(name.split("_")[:2]) for name in leaves])
    protids = self.__parser_ids__(ids)

    ## Establish whether the tree contains more than one copy for each sequence
    ## and if the tree leaf names reflect that situation or not
    copy_var_support = True if len(leaves) == len(set(leaves)) else False

    ## Join and retrieve all the information available in the database for the
    ## unique sequences in the set
    cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) AS protid, s.code, CONC'
    cmd += 'AT(s.code, ".", p.version) AS proteome, p.taxid, p.version, s.name,'
    cmd += ' MAX(copy) AS copy, count(DISTINCT method) AS trees, count(DISTINCT'
    cmd += ' sf.protid, sf.phylome_id) AS collat FROM (protein AS p, species AS'
    cmd += ' s, %s AS ph, %s AS pc) LEFT ' % (self._phylomes,self._phy_content)
    cmd += 'JOIN %s AS t ON (p.protid = t.protid) LEFT JOIN ' % (self._trees)
    cmd += 'seed_friend AS sf ON (p.protid = sf.friend_id) WHERE (p.protid IN '
    cmd += '(%s) AND p.taxid = s.taxid AND p.taxid = ' % (protids)
    cmd += 'pc.taxid AND pc.phylome_id = %s AND ph.phylome_id = ' % (phylome_id)
    cmd += 'pc.phylome_id AND pc.version = p.version) GROUP BY p.protid'

    if self.__execute__(cmd):
      data.setdefault("seq", {})
      for row in self._SQL.fetchall():
        data["seq"].setdefault(row["protid"], {})

        data["seq"][row["protid"]]["copy"] = row["copy"]
        data["seq"][row["protid"]]["trees"] = row["trees"]
        data["seq"][row["protid"]]["taxid"] = row["taxid"]
        data["seq"][row["protid"]]["proteome"] = row["proteome"]
        data["seq"][row["protid"]]["collateral"] = row["collat"]
        data["seq"][row["protid"]]["species_name"] = row["name"]
        data["seq"][row["protid"]]["species_code"] = row["code"]

    ## In some cases, it is necessary as well to recover the protein sequence
    ## for each unique homologous sequence.
    if sequence:

      cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) AS protid, seq FROM '
      cmd += 'protein AS p, species AS s, unique_protein AS u WHERE(p.protid IN'
      cmd += ' (%s) AND p.taxid = s.taxid AND p.protid = u.protid)' % (protids)
      if self.__execute__(cmd):
        for row in self._SQL.fetchall():
          data["seq"][row["protid"]]["seq"] = row["seq"]

    ## Retrieve the external ids for all the unique sequences in the tree
    for protid, external in self.get_external_ids(ids).iteritems():
      data["seq"][protid].setdefault("external", {})
      data["seq"][protid]["external"] = external

    for protid, external in self.get_go_ids(ids).iteritems():
      data["seq"][protid].setdefault("external", {})
      data["seq"][protid]["external"].update(external)

    for protid, external in self.get_old_phylomedb_ids(ids).iteritems():
      data["seq"][protid].setdefault("external", {})
      data["seq"][protid]["external"].update(external)

    for protid, external in self.get_prot_gene_names(ids).iteritems():
      data["seq"][protid].setdefault("external", {})
      data["seq"][protid]["external"].update(external)

    ## The sequence name is as well stored to considerer how many times a given
    ## sequence has been used. That is related to copy number variation cases
    data.setdefault("leaf_names", leaves)

    ## Recover additional information for all leaves in the tree such as
    ## gene/protein names or copy number
    cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) AS protid, copy, '
    cmd += 'prot_name, gene_name FROM protein AS p, species AS s, '
    cmd += '%s AS ph, %s AS pc WHERE (p.' % (self._phylomes, self._phy_content)
    cmd += 'protid IN (%s) AND p.taxid = s.taxid AND p.taxid = pc.' % (protids)
    cmd += 'taxid AND pc.phylome_id = %s AND ph.phylome_id = pc.' % (phylome_id)
    cmd += 'phylome_id AND pc.version = p.version)'

    ## Get specificy information for each tree's leaf, the information will be
    ## the same that for an unique sequence if the copy_var_support is not
    ## set up in advance. The copy_var_support points when there are more than
    ## one copy for at least one unique sequence in the tree and specific
    ## information for each copy can be put it in the tree
    if self.__execute__(cmd):
      data.setdefault("leaves", {})

      for row in self._SQL.fetchall():
        code = row["protid"]

        if data["seq"][row["protid"]]["copy"] > 1 and copy_var_support:
          #code += ("_%d") % (row["copy"])
          pass
        if not copy_var_support and row["copy"] > 1 or not code in leaves:
          continue

        data["leaves"].setdefault(code, {})
        data["leaves"][code]["gene"] = row["gene_name"]
        data["leaves"][code]["protein"] = row["prot_name"]
        data["leaves"][code]["copy_version"] = row["copy"]

    return data

  def get_all_isoforms(self, id):
    """ Returns all the isoforms registered for the input phylomeDB ID
    """

    ## Check if the protein id is well-constructed
    if not self.__check_input_parameter__(single_id = id):
      raise NameError("get_all_isoforms: Check your input data")
    protid = self.__parser_ids__(id)

    ## Look for different isoforms asocciated to the input phylomeDB ID
    cmd =  'SELECT CONCAT("Phy", isoform) AS i, CONCAT("Phy", longest) AS l '
    cmd += 'FROM isoform WHERE(isoform = %s OR longest = %s)' % (protid, protid)

    ## Try to get the isoform for the input ID. Otherwise, return an empty dict
    if not self.__execute__(cmd):
      return {}
    ids = self.__parser_ids__([r[k] for r in self._SQL.fetchall() for k in r])

    ## Recover some details about every isoform
    cmd =  'SELECT CONCAT("Phy", p.protid, "_", code) AS protid, LENGTH(seq) '
    cmd += 'AS ln FROM protein AS p, species AS s, unique_protein AS u WHERE p.'
    cmd += 'protid IN (%s) AND p.protid = u.protid AND p.taxid = s.taxid' %(ids)

    isoforms = {}
    ## Store the information about each isoform if it is not the input one
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        isoforms[row["protid"]] = int(row["ln"])
    return isoforms

  def get_longest_isoform(self, id):
    """ Returns the longest isoform for a given phylomeDB ID
    """

    # Check if the ID is well-constructed
    if not self.__check_input_parameter__(single_id = id):
      raise NameError("get_longest_isoform fuction: Check your input data")
    protid = self.__parser_ids__(id)

    # Look for different isoforms asocciated to the same gene/protein
    cmd  = 'SELECT DISTINCT CONCAT("Phy", p.protid, "_", s.code) as protid, s.'
    cmd += 'code, p.version FROM protein AS p, species AS s, isoform AS i '
    cmd += 'WHERE (i.longest = p.protid AND i.version = p.version AND p.taxid '
    cmd += '= s.taxid AND i.isoform = %s)' % (protid)

    isoforms = {}
    # Return the longest available isoforms for each proteome where the ID is
    # already register
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        isoforms.setdefault(row["code"], {}).setdefault(int(row["version"]), [])
        isoforms[row["code"]][int(row["version"])].append(row["protid"])
    return isoforms

  def get_id_by_external(self, external):
    """ Returns the protein id associated to a given external id
    """

    if not self.__check_input_parameter__(code = external):
      raise NameError("get_id_by_external: Check your input data")

    ## Look at external_db table for any available conversion
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", code) AS protid FROM '
    cmd += 'external_id AS e, protein AS p, species AS s WHERE (e.external_id '
    cmd += '= "%s" AND e.protid = p.protid AND p.taxid = s.taxid)' % (external)

    ids = {}
    ## Recover any available translation
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        for sp, proteome in self.get_longest_isoform(row["protid"]).iteritems():
          for id, proteins in proteome.iteritems():
            ids.setdefault(sp, {}).setdefault(id, [])
            ids[sp][id] += proteins

    ## Extend the information looking at protein and gene names in the protein
    ## table
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", code) AS protid FROM '
    cmd += 'protein AS p, species AS s WHERE ((prot_name = "%s" OR' % (external)
    cmd += ' gene_name = "%s") AND p.taxid = s.taxid)' % (external)

    ## Recover any available translation
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        for sp, proteome in self.get_longest_isoform(row["protid"]).iteritems():
          for id, proteins in proteome.iteritems():
            ids.setdefault(sp, {}).setdefault(id, [])
            ids[sp][id] += proteins

    for sp in ids:
      for proteome in ids[sp]:
        ids[sp][proteome] = list(set(ids[sp][proteome]))

    return ids

  def search_id(self, id):
    """ Returns a list of the longest isoforms for each proteome where the ID is
        already registered. The ID can be a current phylomeDB ID version, former
        phylomeDB ID or an external ID.
    """

    # Check if the ID is well-constructed
    if not self.__check_input_parameter__(string = id):
      raise NameError("search_id: Check your input data")
    query = id.strip()

    # To avoid weird queries which creates slow or invalid MYSQL queries
    QUERY_GEN_REGEXP_FILTER = "^[\w\d\-_,;:.|#@\/\\\()'<>!]+$"
    QUERY_OLD_REGEXP_FILTER = "^\w{3}\d{1,}$"
    QUERY_INT_REGEXP_FILTER = "^[Pp][Hh][Yy]\w{7}(_\w{2,7})?$"

    phylomeDB_matches = {}
    # First, check if it is a current phylomeDB ID
    if re.match(QUERY_INT_REGEXP_FILTER, query):
      phylomeDB_matches = self.get_longest_isoform(query)

    # Second, check if it is a former phylomeDB ID
    if phylomeDB_matches == {} and re.match(QUERY_OLD_REGEXP_FILTER, query):
      currentID = self.get_new_phylomedb_id(query)
      if currentID:
        phylomeDB_matches = self.get_longest_isoform(currentID)

    # Third, check if the query can be mapped using other sources
    if phylomeDB_matches == {} and re.match(QUERY_GEN_REGEXP_FILTER, query):
      phylomeDB_matches = self.get_id_by_external(query)

    return phylomeDB_matches

  def get_id_translations(self, id):
    """ Returns all the registered translations of a given phylomeDB ID
    """

    # Check if the ID is well-constructed
    if not self.__check_input_parameter__(single_id = id):
      raise NameError("get_id_translations: Check your input data")

    conversion = {}
    ## Look at different external IDs sources and retrieve the available info
    info = self.get_external_ids(id)
    if info:
      conversion.update(info[info.keys()[0]])

    info = self.get_go_ids(id)
    if info:
      conversion.update(info[info.keys()[0]])

    info = self.get_old_phylomedb_ids(id)
    if info:
      conversion.update(info[info.keys()[0]])

    info = self.get_prot_gene_names(id)
    if info:
      conversion.update(info[info.keys()[0]])

    return conversion

  def get_translations_for_proteome(self, taxid, version):
    cmd  = 'SELECT protid, prot_name, gene_name FROM protein WHERE taxid=%d AND version=%d' %\
        (taxid, version)

    if self.__execute__(cmd):
      return [(r["protid"], r["prot_name"], r["gene_name"]) for r in self._SQL.fetchall()]
    else:
      return []


  def get_collateral_seeds(self, protid):
    """ Return the trees where the protid is presented as part of the homolog
        sequences to the seed protein
    """

    # Check if the input phylomeDB ID is well-constructed
    if not self.__check_input_parameter__(list_id = protid):
      raise NameError("get_collateral_seeds: Check your input data")
    protid = self.__parser_ids__(protid)

    ## Recover the tree's seed protein and the phylome ID where the sequence is
    ## among the homolog sequences
    cmd  = 'SELECT DISTINCT CONCAT("Phy", p.protid, "_", code) AS protid, sf.'
    cmd += 'phylome_id AS phylome FROM seed_friend AS sf, species AS s, protein'
    cmd += ' AS p, %s AS ph WHERE (friend_id IN (%s)' % (self._phylomes, protid)
    cmd += ' AND sf.protid = p.protid AND p.taxid = s.taxid AND ph.phylome_id ='
    cmd += ' sf.phylome_id)'

    ## Perform and return the query result
    if self.__execute__(cmd):
      return [(r["protid"], r["phylome"]) for r in self._SQL.fetchall()]
    return []

  def get_tree(self, id, phylome_id, method = None, best_tree = False):
    """ Depending in the input parameters select either
        .- a tree with the best evolutionary model in terms of LK (best_tree)
        .- a tree reconstructed using a specific model (method)
        .- all available model/trees for the tuple (phylomeDB ID, phylome ID)
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(single_id = id, str_number = phylome_id):
      raise NameError("get_tree: Check your input data")
    protid = self.__parser_ids__(id)

    if method and best_tree:
      msg =  "get_tree: Impossible to ask for the best model and ask at the "
      msg += "same time for a specific evolutionary model"
      raise NameError(msg)

    # Depending in the input parameters select either a tree with the best
    # evolutionary model in terms of LK, excluiding any possible NJ tree; a tree
    # reconstructed using a specific model or all available model/trees for the
    # input ID associated to the input phylome
    cmd =  'SELECT newick AS tree, method, lk FROM %s WHERE ' % (self._trees)
    cmd += '(protid = %s AND phylome_id = %s)' % (protid, phylome_id)

    if best_tree:
      cmd = cmd[:-1] + ' AND method != "NJ") ORDER BY lk DESC LIMIT 1'
    elif method:
      cmd = cmd[:-1] + ' AND method = "%s")' % (method)

    trees = {}
    ## Execute the MySQL query and then format the query result
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        trees.setdefault(row["method"], {})["lk"] = row["lk"]
        trees.setdefault(row["method"], {})["tree"] = PhyloTree(row["tree"], sp_naming_function=extract_species_name)
    return trees

  def get_best_tree(self, id, phylome_id):
    """ return a tree for input id in the given phylome for the best fitting
        evolutionary model in terms of LK
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(single_id = id, str_number = phylome_id):
      raise NameError("get_tree: Check your input data")

    protid = self.__parser_ids__(id)
    # Select a tree with the best evolutionary model in terms of LK, excluiding
    # any possible NJ tree; a tree
    cmd =  'SELECT newick AS tree, method, lk FROM %s WHERE ' % (self._trees)
    cmd += '(protid = %s AND phylome_id = %s  AND method' % (protid, phylome_id)
    cmd += ' != "NJ") ORDER BY lk DESC LIMIT 1'

    tree = {}
    ## Execute the MySQL query and then format the query result
    if self.__execute__(cmd):
      tree = self._SQL.fetchone()
      tree["tree"] = PhyloTree(tree["tree"], sp_naming_function=extract_species_name)

    return tree

  def get_algs(self, id, phylome_id, raw_alg = True, clean_alg = True):
    """ Return the either the clean, the raw or both alignments for the input
        phylomeDB ID in the input phylome
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(single_id = id, str_number = phylome_id):
      raise NameError("get_algs: Check your input data")
    protid = self.__parser_ids__(id)

    ## Check whether the function has to return, at least, one alignment
    if not raw_alg and not clean_alg:
      return {}

    ## Depending on the input parameters, construct the MySQL query asking for
    ## either clean, raw or both alignments
    cmd = "raw_alg, clean_alg" if raw_alg and clean_alg else "raw_alg" \
      if raw_alg else "clean_alg"

    cmd  = 'SELECT %s, seqnumber FROM %s WHERE ' % (cmd, self._algs)
    cmd += '(phylome_id = %s AND protid = %s)' % (phylome_id, protid)

    if self.__execute__(cmd):
      return self._SQL.fetchone()
    return {}

  def get_raw_alg(self, id, phylome_id):
    """ Return the raw alignment for the input phylomeDB ID in the given phylome
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(single_id = id,str_number=phylome_id):
      raise NameError("get_raw_alg: Check your input data")

    cmd  = 'SELECT raw_alg FROM %s WHERE (phylome_id = ' % (self._algs)
    cmd += '%s AND protid = %s)' % (phylome_id, self.__parser_ids__(id))

    if self.__execute__(cmd):
      return self._SQL.fetchone()["raw_alg"]
    return ""

  def get_clean_alg(self, id, phylome_id):
    """ Return the raw alignment for the input phylomeDB ID in the given phylome
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(single_id = id,str_number=phylome_id):
      raise NameError("get_raw_alg: Check your input data")

    cmd  = 'SELECT clean_alg FROM %s WHERE (phylome_id = ' % (self._algs)
    cmd += '%s AND protid = %s)' % (phylome_id, self.__parser_ids__(id))

    if self.__execute__(cmd):
      return self._SQL.fetchone()["clean_alg"]
    return ""

  def get_seq_info_in_tree(self, id, phylome_id, method = None):
    """ Return all the available information for each sequence from tree/s
        asociated to a tuple (protein, phylome) identifiers.
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(single_id = id, string = method, \
      str_number = phylome_id):
      raise NameError("get_seq_info_in_tree: Check your input data")

    ## Depending on the input parameter, retrieve the best tree associated to
    ## the phylomeDB ID in the given phylomeDB or retrieve the tree generated
    ## under the model indicated in the input parameter. Moreover, all the
    ## available information in the database for tree leaves
    if method:
      return self.get_info_homologous_seqs(id, phylome_id, tree = True, \
        tree_method = method)
    else:
      return self.get_info_homologous_seqs(id, phylome_id, tree = True)

  def get_seq_info_msf(self, id, phylome_id):
    """ Return all available information for the homologous sequences to the
        input phylomeDB ID in the input phylome using the best tree to compute
        the set of homologous sequences
    """

    ## Check the input parameters
    if not self.__check_input_parameter__(single_id = id, str_number = phylome_id):
      raise NameError("get_seq_info_msf: Check your input parameters")

    ## The best tree is used to compute the homologous sequences for the input
    ## phylomeDB ID and phylome ID. The tree is used to compute possible cases
    ## of copy number variation where more than one copy for a given sequence
    ## might be present in the set of homologous
    return self.get_info_homologous_seqs(id, phylome_id, sequence = True)

  def get_seqid_info(self, id):
    """ Returns available information about a given protid
    """

    # Check if the protein id is well-constructed
    if not self.__check_input_parameter__(single_id = id):
      raise NameError("Wrong id [%s]" %id)
    protid = self.__parser_ids__(id)

    ## Join and retrieve all the information available in the database for
    ## the sequence
    cmd =  'SELECT DISTINCT CONCAT("Phy", p.protid, "_", s.code) AS protid, s.'
    cmd += 'code AS species_code, s.name AS species_name, p.taxid, u.seq FROM '
    cmd += 'protein AS p, unique_protein AS u, species AS s WHERE (p.protid = '
    cmd += '%s AND p.protid = u.protid AND p.taxid = s.taxid)' % (protid)

    if not self.__execute__(cmd):
      return {}
    data = self._SQL.fetchone()

    ## Retrieve the information specific for each proteome version as well as
    ## for the different copies inside each proteome
    cmd =  'SELECT version, copy, prot_name, gene_name, comments FROM protein '
    cmd += 'WHERE protid = %s' % (protid)

    if not self.__execute__(cmd):
      return {}

    for row in self._SQL.fetchall():
      proteome = ("%s.%s") % (data["species_code"], row["version"])
      data.setdefault("proteomes", set()).add(proteome)

      data.setdefault("copy", {}).setdefault(proteome, 0)
      data["copy"][proteome] = row["copy"] if data["copy"][proteome] < \
        row["copy"] else data["copy"][proteome]

      if row["prot_name"]:
        data.setdefault("protein", {}).setdefault(proteome, set()).\
          add(row["prot_name"])

      if row["gene_name"]:
        data.setdefault("gene", {}).setdefault(proteome, set()).\
          add(row["gene_name"])

      if row["comments"]:
        data.setdefault("comments", {}).setdefault(proteome, set()).\
          add(row["comments"])

    ## Recover all the isoforms associated to the input phylomeDB ID
    data["isoforms"] = self.get_all_isoforms(data["protid"])

    ## Look at different external IDs sources and retrieve the available info
    info = self.get_external_ids(id)
    data["external"] = info[info.keys()[0]] if info else {}

    info = self.get_go_ids(id)
    if info:
      data["external"].update(info[info.keys()[0]])

    info = self.get_old_phylomedb_ids(id)
    if info:
      data["external"].update(info[info.keys()[0]])

    info = self.get_prot_gene_names(id)
    if info:
      data["external"].update(info[info.keys()[0]])

    return data

  def get_available_trees_by_phylome(self, id, collateral = True):
    """ Returns information about which methods have been used to reconstruct
        every tree for a given phylomeDB ID grouped by phylome
    """

    # Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(list_id = id, boolean = collateral):
      raise NameError("Check your input data")
    protids = self.__parser_ids__(id)

    ## Retrieve which models were used to reconstructed the trees in each
    ## phylome where the input phylomeDB ID was used as a seed
    cmd =  'SELECT DISTINCT phylome_id, method, CONCAT("Phy", p.protid, "_", s.'
    cmd += 'code) AS protid FROM protein AS p, species AS s, %s' % (self._trees)
    cmd += ' AS t WHERE (p.protid IN (%s) AND p.protid = t.protid ' % (protids)
    cmd += 'AND p.taxid = s.taxid)'

    if not self.__execute__(cmd) and not collateral:
      return {}

    t = {}
    ## Create a temporary structure to process the data retrieved
    for r in self._SQL.fetchall():
      t.setdefault(int(r["phylome_id"]), {})
      t[int(r["phylome_id"])].setdefault(r["protid"], set()).add(r["method"])

    trees = {}
    ## Create the definitive data structure where the IDs with the methods used
    ## to reconstructed each tree are grouped by phylome
    for phylome in t:
      trees.setdefault(phylome, [])
      for protid in t[phylome]:
        trees[phylome].append([True, protid, [m for m in t[phylome][protid]]])

    ## Retrieve the trees where the input phylomeDB ID has been used as part of
    ## the set of homologous sequences to make the tree
    if collateral:
      for seed, phylome in self.get_collateral_seeds(id):
        cmd =  'SELECT method FROM %s WHERE protid = ' % (self._trees)
        cmd += '%s AND phylome_id = %s' % (self.__parser_ids__(seed), phylome)
        if self.__execute__(cmd):
          trees.setdefault(int(phylome), []).append([False, seed, [r["method"] \
            for r in self._SQL.fetchall()]])

    return trees

  def count_trees(self, phylome_id):
    """ Retuns the frequency of each evolutionary method in the input phylome
    """
    # Check if the phylome id is well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("count_trees: Check your input data")

    cmd =  'SELECT method, count(*) AS freq FROM %s WHERE ' % (self._trees)
    cmd += '(phylome_id = %s) GROUP BY method' % (phylome_id)

    if self.__execute__(cmd):
      return self.__fomat_MySQL_to_dict__("method", self._SQL.fetchall())
    return {}

  def count_algs(self, phylome_id):
    """ Returns how many alignments are for a given phylome
    """

    # Check if the phylomedb id code is well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("count_algs: Check your input data")

    cmd =  'SELECT count(*) AS freq FROM %s ' % (self._algs)
    cmd += 'WHERE phylome_id = %s' % (phylome_id)

    if self.__execute__(cmd):
      return  int(self._SQL.fetchone()["freq"])
    return 0

  def get_phylome_trees(self, phylome_id):
    """ Returns all trees available for a given phylome
    """

    # Check if the phylome id code is well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("get_phylome_trees: Check your input data")

    ## Get all available trees for a given phylome id
    cmd =  'SELECT CONCAT("Phy", protid, "_", code) AS protid, method, lk, '
    cmd += 'newick FROM %s AS t, %s AS ph, ' % (self._trees, self._phylomes)
    cmd += 'species AS s WHERE (ph.phylome_id = %s AND ph.' % (phylome_id)
    cmd += 'phylome_id = t.phylome_id AND ph.seed_taxid = s.taxid)'

    trees = {}
    ## For each phylomeDB ID used as a seed, return the different evolutionary
    ## model evaluated during the phylogenetic reconstruction as well as the
    ## phylogenetic tree (an ETE object) and its likelihood
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        trees.setdefault(row["protid"], {}).setdefault(row["method"], \
          [row["lk"], PhyloTree(row["newick"], sp_naming_function=extract_species_name)])
    return trees

  def get_phylome_algs(self, phylome_id):
    """ Returns all alignments available for a given phylome
    """

    # Check if the phylome id code is well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("get_phylome_tree: Check your input data")

    ## Retrieve all the available alignments for the input phylome
    cmd =  'SELECT CONCAT("Phy", protid, "_", code) AS protid, raw_alg, clean_'
    cmd += 'alg FROM %s AS a, %s AS ph, species ' % (self._algs, self._phylomes)
    cmd += 'AS s WHERE (ph.phylome_id = %s AND ph.phylome_id = ' % (phylome_id)
    cmd += 'a.phylome_id AND ph.seed_taxid = s.taxid)'

    algs = {}
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        algs.setdefault(row["protid"], {})["raw_alg"] = row["raw_alg"]
        algs.setdefault(row["protid"], {})["clean_alg"] = row["clean_alg"]
    return algs

  def get_species(self):
    """ Returns all current registered species in the database
    """

    if self.__execute__('SELECT taxid, code, name FROM species'):
      return self.__fomat_MySQL_to_dict__("code", self._SQL.fetchall())
    return {}

  def get_species_info(self, taxid = None, code = None):
    """ Returns all information on a given species/code
    """

    # Check if the input parameters is well-constructed
    if not self.__check_input_parameter__(number = taxid, string = code):
      raise NameError("Check your input data")

    if not taxid and not code:
      return {}

    ## Depending on the input parameters, the search in the database is perfomed
    ## using either species taxid, or species code or both of them.
    cmd = 'SELECT taxid, code, name FROM species AS s WHERE ('
    cmd += 'taxid = %s%s' % (taxid, '' if code else ')') if taxid else ""
    cmd += '%s code = "%s")' % (" AND" if taxid else "", code) if code else ""

    ## Return the retrieved information
    if self.__execute__(cmd):
      return self._SQL.fetchone()
    return {}

  def get_genomes(self):
    """ Returns all current available genomes/proteomes
    """

    ## Complete information about each genome adding species information
    cmd =  'SELECT CONCAT(code, ".",version) AS g, g.taxid, source, DATE(date),'
    cmd += ' AS date,name FROM genome AS g, species AS s WHERE s.taxid =g.taxid'

    if self.__execute__(cmd):
      return self.__fomat_MySQL_to_dict__("g", self._SQL.fetchall())
    return {}

  def get_genome_info(self, genome):
    """ Returns all available information about a registered genome/proteome
    """

    # Check if the input parameter is well-constructed
    if not self.__check_input_parameter__(string = genome):
      raise NameError("get_genome_info: Check your input data")

    if genome.count(".") != 1:
      raise NameError("get_genome_info: Expected input 'SpeciesCode.version'")

    code, version = genome.split(".")
    ## If the genome is well-defined, ask for its associated information
    cmd =  'SELECT CONCAT(code, ".", version) AS genome_id, g.taxid, s.name AS '
    cmd += 'species, version, DATE(date) AS date, source, comments FROM species'
    cmd += ' AS s, genome AS g WHERE(s.taxid = g.taxid AND code = "%s"' % (code)
    cmd += ' AND version = %s)' % (version)

    ## Return the available information in a dictionary defined for that
    if self.__execute__(cmd):
      return self._SQL.fetchone()
    return {}

  def get_genome_ids(self, taxid, version, filter_isoforms = True):
    """ Returns the phylomeDB IDs for a given genome in the database filtering
        out, or not, the different isoforms for each ID
    """

    ## Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(str_number = taxid):
      raise NameError("get_genome_ids: Check your input data")
    if not self.__check_input_parameter__(str_number = version):
      raise NameError("get_genome_ids: Check your input data")
    if not self.__check_input_parameter__(boolean = filter_isoforms):
      raise NameError("get_genome_ids: Check your input data")

    ## Depending on if the different isoforms have to be filter out or not, the
    ## query to retrieve the phylomeDB IDs is different
    if filter_isoforms:
      cmd =  'SELECT DISTINCT CONCAT("Phy", i.longest, "_", s.code) AS protid '
      cmd += 'FROM protein AS p, isoform AS i, species AS s WHERE p.taxid = '
      cmd += '%s AND p.version = %s AND p.protid = i.isoform' % (taxid, version)
      cmd += ' AND p.version = i.version AND p.taxid = s.taxid'
    else:
      cmd =  'SELECT DISTINCT CONCAT("Phy", protid, "_", code) AS protid FROM '
      cmd += 'protein AS p, species AS s WHERE p.taxid = %s AND p.' % (taxid)
      cmd += 'version = %s AND p.taxid = s.taxid' % (version)

    if not self.__execute__(cmd):
      return []

    ## Retrieve all the information available for the selected phylomeDB IDs
    return [row["protid"] for row in self._SQL.fetchall()]

  def get_genomes_by_species(self, taxid):
    """ Return all the proteomes/genomes registered for the input taxaid code
    """

    # Check if the input parameter is well-constructed
    if not self.__check_input_parameter__(str_number = taxid):
      raise NameError("Check your input data")

    # Look for the different versions of the input taxid
    cmd =  'SELECT CONCAT(code, ".", version) AS genome FROM species AS s, '
    cmd += 'genome AS g WHERE s.taxid = %s AND s.taxid = g.taxid' % (taxid)

    genomes = {}
    if self.__execute__(cmd):
      genomes[taxid] = [row["genome"] for row in self._SQL.fetchall()]
    return genomes

  def get_phylomes(self):
    """ Returns all current available phylomes
    """

    ## Recover all the phylomes stored in the database
    cmd =  'SELECT phylome_id, seed_taxid, s.name AS seed_species, CONCAT(code,'
    cmd += ' ".", seed_version) AS seed_proteome, DATE(ts) AS date, comments, '
    cmd += 'ph.name FROM species AS s, %s AS ph WHERE seed_' % (self._phylomes)
    cmd += 'taxid = s.taxid'

    ## Generate a dictionary with all phylomes
    if self.__execute__(cmd):
      return self.__fomat_MySQL_to_dict__("phylome_id", self._SQL.fetchall())
    return {}

  def get_phylome_info(self, phylome_id):
    """ Returns available information on a given phylome
    """

    # Check if the phylome id code is well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("get_phylome_info: Check your input data")

    ## Get all available data for the input phylome
    cmd =  'SELECT phylome_id AS id, seed_taxid, s.name AS seed_species, CONCAT'
    cmd += '(code, ".", seed_version) AS seed_proteome, DATE(ts) AS date, ph.'
    cmd += 'name, comments FROM species AS s, %s AS ph WHERE' % (self._phylomes)
    cmd += '(ph.phylome_id = %s AND ph.seed_taxid = s.taxid)' % (phylome_id)

    if self.__execute__(cmd):
      return self._SQL.fetchone()
    return {}

  def get_phylome_seed_ids(self, phylome_id, filter_isoforms = True):
    """ Returns the seed phylomeDB IDs for a given phylome being possible to
        filter out the longest isoforms
    """

    ## Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("get_seed_ids: Check your input data (1)")
    if not self.__check_input_parameter__(boolean = filter_isoforms):
      raise NameError("get_seed_ids: Check your input data (2)")

    ## Get the seed species and version for the input phylome
    cmd =  'SELECT seed_taxid, seed_version FROM %s ' % (self._phylomes)
    cmd += 'WHERE phylome_id = %s' % (phylome_id)

    ## Retrieve the IDs
    if self.__execute__(cmd):
      row = self._SQL.fetchone()
      ## Return the IDs as well as the taxid and proteome version used to
      ## reconstruct the phylome. It might be useful for others functions
      return self.get_genome_ids(row["seed_taxid"], row["seed_version"], \
        filter_isoforms), row["seed_taxid"], row["seed_version"]
    return []

  def get_proteomes_in_phylome(self, phylome_id):
    """ Returns a list of proteomes associated to a given phylome_id
    """

    # Check if the phylome id code is well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("get_proteomes_in_phylome: Check your input data")

    ## Retrieve the proteomes associated to the phylome
    cmd =  'SELECT s.taxid, CONCAT(code, ".", pc.version) AS proteome, s.name,'
    cmd += ' source, date, pc.version FROM species AS s, %s ' % (self._phylomes)
    cmd += 'AS ph, %s AS pc, genome AS g WHERE ph.phylome' % (self._phy_content)
    cmd += '_id = %s AND ph.phylome_id = pc.phylome_id AND pc.' % (phylome_id)
    cmd += 'taxid = s.taxid AND pc.taxid = g.taxid AND pc.version = g.version'

    proteomes = {}
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():
        proteomes.setdefault("proteomes", {}).setdefault(row["proteome"], row)

      cmd =  'SELECT CONCAT(code, ".", ph.seed_version) AS proteome FROM '
      cmd += 'species AS s, %s AS ph WHERE (ph.phylome_id = ' % (self._phylomes)
      cmd += '%s AND ph.seed_taxid = s.taxid)' % (phylome_id)
      if self.__execute__(cmd):
        for row in self._SQL.fetchall():
          proteomes["seed"] = row["proteome"]

    return proteomes

  def get_species_in_phylome(self, phylome_id):
    """ Returns a list of proteomes associated to a given phylome_id
    """
    ## Retrieve taxids associated to a phylome
    cmd =  'SELECT taxid from %s WHERE phylome_id="%s"' % \
        (self._phy_content, phylome_id)
    if self.__execute__(cmd):
      return [values["taxid"] for values in self._SQL.fetchall()]
    else:
      return []

  def get_phylomes_for_seed_ids(self, ids):
    """ Given a list of phylomeDB IDs, return in which phylomes these IDs have
        been used as a seed
    """

    ## Check if the input parameter is well-constructed
    if not self.__check_input_parameter__(list_id = ids):
      raise NameError("get_phylomes_for_seed_ids: Check your input data")

    ## Get all phylomes where the input phylome IDs have been used as a seed
    cmd =  'SELECT CONCAT("Phy", t.protid, "_", code) AS protid, t.phylome_id,'
    cmd += ' ph.name FROM %s AS t, %s AS ph, ' % (self._trees, self._phylomes)
    cmd += 'species AS s WHERE (t.protid IN (%s) ' % (self.__parser_ids__(ids))
    cmd += 'AND t.phylome_id = ph.phylome_id AND ph.seed_taxid = s.taxid) '
    cmd += 'GROUP BY t.protid, ph.phylome_id'

    phylomes = {}
    if self.__execute__(cmd):
      for r in self._SQL.fetchall():
        phylomes.setdefault(r["protid"], []).append((r["phylome_id"],r["name"]))
    return phylomes

  def get_seqs_in_genome(self, taxid, version, filter_isoforms = True):
    """ Returns all sequences of a given proteome, filtering the
    """

    ## Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(str_number = taxid):
      raise NameError("get_seqs_in_genome: Check your input data")
    if not self.__check_input_parameter__(str_number = version):
      raise NameError("get_seqs_in_genome: Check your input data")
    if not self.__check_input_parameter__(boolean = filter_isoforms):
      raise NameError("get_seqs_in_genome: Check your input data")

    ## Retrieve the phylomeDB IDs for the input genome
    ids = self.get_genome_ids(taxid, version, filter_isoforms)

    ## Get all the information
    cmd = 'SELECT CONCAT("Phy", p.protid, "_",code) AS protid, copy, prot_name,'
    cmd += ' gene_name, seq FROM protein AS p, species AS s, unique_protein AS '
    cmd += 'u WHERE p.protid IN (%s) AND p.version' % (self.__parser_ids__(ids))
    cmd += ' = %s AND p.taxid = s.taxid AND p.protid = u.protid' % (version)

    sequences = {}
    ## Store the data into the appropiate data structure having in mind the
    ## copy number variation effect.
    if self.__execute__(cmd):
      for row in self._SQL.fetchall():

        if row["copy"] > 1 and row["protid"] in sequences:
          sequences[("%s_1") % (row["protid"])] = sequences[row["protid"]]
          del sequences[row["protid"]]
        if row["copy"] > 1:
          row["protid"] += ("_%d") % (row["copy"])

        sequences[row["protid"]] = row
        del sequences[row["protid"]]["protid"]

    return sequences

  def get_phylome_seed_ids_info(self, phylome_id, start = 0, offset = None, \
    filter_isoforms = False):
    """
    """

    ## Check if the input parameters are well-constructed
    if not self.__check_input_parameter__(str_number = phylome_id):
      raise NameError("get_phylome_seed_ids_info: Check your input data (1)")
    if not self.__check_input_parameter__(str_number = start, number = offset):
      raise NameError("get_phylome_seed_ids_info: Check your input data (2)")

    ## Determine how many phylomeDB IDs have been used as a seed in the input
    ## phylome
    ids, taxid, version = self.get_phylome_seed_ids(phylome_id, filter_isoforms)
    protids = self.__parser_ids__(ids)

    ## Retrieve the phylomeDB IDs belonging to the input phylome as well the
    ## number of trees for each ID in that phylome
    cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) AS protid, COUNT('
    cmd += 'DISTINCT method) AS trees FROM (protein AS p, species AS s, '
    cmd += '%s AS ph) LEFT JOIN (%s AS t) ON ' % (self._phylomes, self._trees)
    cmd += '(ph.phylome_id = t.phylome_id AND p.protid = t.protid) WHERE (ph.'
    cmd += 'phylome_id = %s AND ph.seed_taxid = p.taxid AND ph.' % (phylome_id)
    cmd += 'seed_version = p.version AND ph.seed_taxid = s.taxid AND p.protid '
    cmd += 'IN (%s)) GROUP BY p.protid ORDER BY trees DESC, protid ' % (protids)
    cmd += 'LIMIT %d,%d' % (start, offset) if offset else ''

    if not self.__execute__(cmd):
      return {}
    seqs = self.__fomat_MySQL_to_dict__("protid", self._SQL.fetchall())

    protids = self.__parser_ids__(seqs.keys())
    cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) AS protid, raw_alg IS '
    cmd += 'NOT NULL AS r, clean_alg IS NOT NULL AS c FROM (protein AS p, speci'
    cmd += 'es AS s) LEFT JOIN (%s AS a) ON (p.protid = a.protid' % (self._algs)
    cmd += ') WHERE (p.protid IN (%s) AND p.version = %s ' % (protids, version)
    cmd += 'AND p.taxid = s.taxid AND a.phylome_id = %s)' % (phylome_id)

    if not self.__execute__(cmd):
      return {}

    for row in self._SQL.fetchall():
      seqs[row["protid"]]["algs"] = 2 if row["r"] and row["c"] else 1 \
        if row["c"] or row["r"] else 0

    cmd =  'SELECT CONCAT("Phy", p.protid, "_", s.code) AS protid, p.comments, '
    cmd += 'gene_name, prot_name, copy, length(seq) AS l FROM protein AS p, uni'
    cmd += 'que_protein AS u, species AS s, %s AS ph WHERE ' % (self._phylomes)
    cmd += '(ph.phylome_id = %s AND p.protid IN (%s) ' % (phylome_id, protids)
    cmd += 'AND ph.seed_version = p.version AND ph.seed_taxid = s.taxid)'

    if not self.__execute__(cmd):
      return {}

    for row in self._SQL.fetchall():
      seqs[row["protid"]]["seq_length"] = row["l"]

      seqs[row["protid"]].setdefault("copy", 0)
      if row["copy"] > seqs[row["protid"]]["copy"]:
        seqs[row["protid"]]["copy"] = row["copy"]

    return seqs, len(ids)
