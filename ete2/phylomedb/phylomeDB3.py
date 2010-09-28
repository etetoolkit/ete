# #START_LICENSE###########################################################
#
# Copyright (C) 2010 by Jaime Huerta Cepas, Salvador Capella Gutierrez.
# All rights reserved. email: jhcepas@gmail.com, salcagu@gmail.com
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

"""
'phylomedb' provides an access API to the data stored in the
phylogenetic database PhylomeDB *[1].

All methods to perform queries are implemented within the PhylomeDB3Connector
class.

 *[1] PhylomeDB: a database for genome-wide collections of gene phylogenies.
      Jaime Huerta-Cepas, Anibal Bueno, Joaquin Dopazo and Toni Gabaldon.

      PhylomeDB is a database of complete phylomes derived for different genomes
      within a specific taxonomic range. All phylomes in the database are built
      using a high-quality phylogenetic pipeline that includes evolutionary
      model testing and alignment trimming phases. For each genome, PhylomeDB
      provides the alignments, phylogentic trees and tree-based orthology
      predictions for every single encoded protein.
"""
import re
from string import strip
import MySQLdb
from ete_dev import PhyloTree

ID_PATTERN = re.compile("^[Pp][Hh][Yy]\w{7}(_\w{2,7})?$")
ITERABLE_TYPES = set([list, set, tuple, frozenset])

__all__ = ["PhylomeDB3Connector"]

class PhylomeDB3Connector(object):
  """ Returns a connector to a phylomeDB3 database.

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

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def __init__(self, host = "84.88.66.245", db = "phylomedb_3", user = "public",\
    passwd = "public", port = 3306):
    """ Connects to a phylomeDB database and returns an object to perform custom
        queries on it.
    """

    # Establish the connection to the MySQL database where phylomeDB is stored.
    try:
      self._SQLconnection = MySQLdb.connect(host = host, user = user, passwd = \
        passwd, db = db, port = int(port))
    except:
      raise NameError("ERROR: Check your connection parameters")

    self._SQL = self._SQLconnection.cursor()

    # Define the different database views depending on the user profile
    self._trees_table    = "tree_public"
    self._phylomes_table = "phylome_public"
    self._algs_table     = "alignment_public"
    self._phylomes_content_table = "phycontent_public"
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def execute_block(self, commands):
    """ Executes a multi-line MySQL command.
    """

    for line in commands.split(";"):
      line = ("%s") % (line.strip())
      if not line:
        continue
      try:
        self._SQL.execute(line)
      except:
        print ("'%s'") % (line)
        raise NameError("An error ocurred during MySQL operation")
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def parser_ids(self, ids):
    """ Returns a string with the input id/s ready to be used in any MySQL query
    """

    # Check if it a valid data structure
    if not ids:
      raise NameError(("Empty data structure. '%s'") % (str(ids)))

    # Define a function to manage the different ids
    parser = lambda id: id[3:10] if ID_PATTERN.match(id) else None

    # If the id is a single string, turn it into a list
    if type(ids) == str:
      ids = [ids]

    # If the ids belongs to one of the predefined iterable types, try to convert
    # each member in a valid phylomeDB code
    if type(ids) in ITERABLE_TYPES:
      parsed = ', ' .join(['"%s"' % parser(n) for n in ids if parser(n)])
      if parsed:
        return parsed
      return None

    # If the ids is not a valid iterable type or it hasn't been possible to
    # convert any code into a phylomeDB code, return None
    else:
      raise NameError("Check your input data")
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def check_input_parameter(self, **kargs):
    """ Check the different input parameters
    """

    ## Define the available checks
    valid_keys = set(["str_number", "single_id", "list_id", "code", "string", \
      "boolean", "number"])

    ## Check that all input keys have associated an verification clause
    for key in kargs:
      if not key in valid_keys:
        raise NameError("Invalid key")

    ## Check number. It should be either None or an integer positive number
    if "number" in kargs:
      if kargs["number"]:
        try:    int(kargs["number"])
        except: return False
        if int(kargs["number"]) < 1:
          return False

    ## Check phylome id format. It should be an integer positive number
    if "str_number" in kargs:
      try:
        int(kargs["str_number"])
      except:
        return False
      if int(kargs["str_number"]) < 0:
        return False

    ## Check if a unique protid has been given as an input parameter
    if "single_id" in kargs:
      protid = self.parser_ids(kargs["single_id"])
      if not protid or type(kargs["single_id"]) != str:
        return False

    ## Check if at least one protid has been given as an input parameter
    if "list_id" in kargs:
      if not self.parser_ids(kargs["list_id"]):
        return False

    ## check if a single string has been given as an input parameter
    if "code" in kargs:
      if not kargs["code"] or type(kargs["code"]) != str:
        return False

    ## check if an input parameter is different of None and then, if it is
    ## an string or not
    if "string" in kargs:
      if kargs["string"] != None and type(kargs["string"]) != str:
        return False
      if kargs["string"] != None and len(kargs["string"].split()) > 1:
        return False

    ## check if an input parameter is an boolean or not
    if "boolean" in kargs:
      if type(kargs["boolean"]) != bool:
        return False

    ## Return true if and only if all input parameters are well-constructed
    return True
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_conversion_protein(self, code):
    """ Returns the conversion between old phylome id codes and the new ones
    """

    # Check if the code is well-constructed
    if not self.check_input_parameter(code = code):
      raise NameError("Check your input data")

    # Check whether the input code is a valid former phylomeDB id or not
    QUERY_OLD_REGEXP_FILTER = "^\w{3}\d{1,}$"
    if not re.match(QUERY_OLD_REGEXP_FILTER, code):
      return None

    # Look if the given code can be mapped into the phylomeDB dabatase
    cmd =  'SELECT protid, code FROM old_protein, species WHERE (species.taxid '
    cmd += '= old_protein.taxid AND old_code = "%s" AND old_protid =' % code[:3]
    cmd += ' %s)' % code[3:]

    # If everything is fine, return the new id
    if self._SQL.execute(cmd):
      protid, species = self._SQL.fetchone()
      if protid and species:
        return ("Phy%s_%s") % (protid, species)
      return None
    raise NameError("Error during MySQL query")
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_longest_isoform(self, id):
    """ Returns the longest isoform for a given id
    """

    # Check if the id is well-constructed
    if not self.check_input_parameter(single_id = id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    # Look for different isoforms asocciated to the same gene/protein
    cmd =  'SELECT distinct p.protid, s.code, p.version FROM protein AS p, sp'
    cmd += 'ecies AS s, isoform AS i WHERE (i.longest = p.protid AND i.version'
    cmd += ' = p.version AND p.taxid = s.taxid AND i.isoform = %s)' % protid

    # Return the longest available isoforms for each proteome where the id is
    # already register
    isoforms = {}
    if self._SQL.execute(cmd):
      for id, code, version in self._SQL.fetchall():
        protid = ("Phy%s_%s") % (id, code)
        isoforms.setdefault(code, {}).setdefault(int(version), []).append(protid)
    return isoforms
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def search_id(self, id):
    """ Returns a list of the longest isoforms for each proteome where the id is
        already registered. The id can be a current id version, former phylomeDB
        id or an external id.
    """

    # Check if the id is well-constructed
    if not self.check_input_parameter(code = id):
      raise NameError("Check your input data")

    # To avoid weird queries which makes create slow or invalid MYSQL queries
    QUERY_GEN_REGEXP_FILTER = "^[\w\d\-_,;:.|#@\/\\\()'<>!]+$"
    QUERY_OLD_REGEXP_FILTER = "^\w{3}\d{1,}$"
    QUERY_INT_REGEXP_FILTER = "^[Pp][Hh][Yy]\w{7}(_\w{2,7})?$"

    query = id.strip()
    phylomeDB_matches = {}

    # First, check if it is a current phylomeDB ID
    if re.match(QUERY_INT_REGEXP_FILTER, query):
      phylomeDB_matches.update(self.get_longest_isoform(query))

    # Second, check if it is a former phylomeDB ID
    if phylomeDB_matches == {}:
      if re.match(QUERY_OLD_REGEXP_FILTER, query):
        currentID = self.get_conversion_protein(query)
        if currentID:
          phylomeDB_matches.update(self.get_longest_isoform(currentID))

      # Third, check if the query can be mapped using other sources
      if re.match(QUERY_GEN_REGEXP_FILTER, query) and phylomeDB_matches == {}:
        cmd =  'SELECT distinct protid FROM protein WHERE'
        cmd += '(prot_name = "%s" OR gene_name = "%s")' % (query, query)

        if self._SQL.execute(cmd):
          # Check if the query is the original (protein or gene) name for a
          # given protein
          for id in self._SQL.fetchall():
            protid = ("Phy%s") % (id[0])
            phylomeDB_matches.update(self.get_longest_isoform(protid))

        # Check if it is possible to map the id using an external database
        external_ids = self.get_id_by_external(query)
        if external_ids:
          phylomeDB_matches.update(external_ids)

    return phylomeDB_matches
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_id_by_external(self, external):
    """ Returns the protein id associated to a given external id
    """

    # Check if the external code is well-constructed
    if not self.check_input_parameter(code = external):
      raise NameError("Check your input data")

    ## Look at external_db table for any available conversion
    cmd =  'SELECT p.protid, code FROM external_id AS e, protein AS p, species '
    cmd += 'AS s WHERE (e.external_id = "%s" AND e.protid = p.protid' % external
    cmd += ' AND p.taxid = s.taxid)'

    ids = {}
    ## Recover any available translation
    if self._SQL.execute(cmd):
      for id, code in self._SQL.fetchall():
        ids.update(self.get_longest_isoform(("Phy%s_%s") % (id, code)))

    ## Extend the information looking at protein and gene names in the protein
    ## table
    cmd =  'SELECT distinct protid, code FROM protein AS p, species AS s WHERE '
    cmd += '((prot_name = "%s" OR gene_name = "%s") AND ' % (external, external)
    cmd += 'p.taxid = s.taxid)'

    ## Recover any available translation
    if self._SQL.execute(cmd):
      for id, code in self._SQL.fetchall():
        ids.update(self.get_longest_isoform(("Phy%s_%s") % (id, code)))

    return ids
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_id_translations(self, id):
    """ Returns all the registered translations of a given protid
    """

    # Check if the id is well-constructed
    if not self.check_input_parameter(single_id = id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Look at the external_id table for any possible translation from phylomeDB
    ## ids to external ones
    cmd =  'SELECT external_db, external_id FROM external_id WHERE protid = '
    cmd += '%s' % protid

    conversion = {}
    ## Recover any possible match
    if self._SQL.execute(cmd):
      for db, id in self._SQL.fetchall():
        conversion.setdefault(db, []).append(id)

    ## Look for other possible translation sources, in this case, in the protein
    ## table
    cmd =  'SELECT distinct prot_name, gene_name FROM protein WHERE protid = '
    cmd += '%s' % protid

    ## Extend any possible recovered information
    if self._SQL.execute(cmd):
      conversion.setdefault("protein_name", [])
      conversion.setdefault("gene_name", [])

      for protein, gene in self._SQL.fetchall():
        if protein:
          conversion["protein_name"].append(protein)
        if gene:
          conversion["gene_name"].append(protein)

      ## Delete any possible duplicate entry
      conversion["gene_name"] = list(set(conversion["gene_name"]))
      conversion["protein_name"] = list(set(conversion["protein_name"]))
    return conversion
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_collateral_seeds(self, protid):
    """ Returns the trees where the protid is presented as part of the homolog
        sequences to the seed protein
    """

    # Check if the protid is well-constructed
    if not self.check_input_parameter(list_id = protid):
      raise NameError("Check your input data")
    protid = self.parser_ids(protid)

    ## Recover the tree's seed protein and the phylome id where the sequence is
    ## among the homolog sequences
    cmd  = 'SELECT distinct p.protid, code, phylome_id FROM seed_friend AS sf, '
    cmd += 'species AS s, protein AS p WHERE (friend_id IN (%s) AND ' % (protid)
    cmd += 'sf.protid = p.protid AND p.taxid = s.taxid)'

    ## Execute and format the query result
    if self._SQL.execute(cmd):
      seeds = [(("Phy%s_%s") % (id, code), phylome_id) for id, code, phylome_id\
        in self._SQL.fetchall()]
      return tuple(seeds)
    return tuple()
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_tree(self, id, phylome_id, method = None):
    """ Returns the tree associated with a given method for a the tuple (id,
        phylome_id). If method is not defined then the functions returns all
        available trees for the protid in the given phylome_id
    """

    # Check if the input parameters are well-constructed
    if not self.check_input_parameter(single_id = id, str_number = phylome_id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Recover the information associated to the input id for the input phylome.
    ## Depending on if the method is defined or not, the function returns only
    ## the tree for that method or not.
    cmd =  'SELECT newick, method, lk FROM %s WHERE ' % self._trees_table
    cmd += '(phylome_id = %s AND protid = %s' % (phylome_id, protid)
    cmd += ' AND method = "%s")' % method if method else ')'

    trees = {}
    ## Execute the MySQL query and then format the query result
    if self._SQL.execute(cmd):
      for tree, method, lk in self._SQL.fetchall():
        trees.setdefault(method, {})["lk"] = lk
        trees.setdefault(method, {})["tree"] = PhyloTree(tree)
    return trees
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seq_info_in_tree(self, id, phylome_id, method = None):
    """ Returns all the available information for each sequence from tree/s
        asociated to a tuple (protein, phylome) identifiers.
    """

    # Check if the input parameters are well-constructed
    if not self.check_input_parameter(single_id = id, str_number = phylome_id,\
      string = method):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Look for the protid in the given phylome and recover, if the method is
    ## not defined, the best tree for that protein id in that phylome
    cmd =  'SELECT newick, method, lk FROM %s AS t WHERE ' % (self._trees_table)
    cmd += '(protid = %s AND phylome_id = %s AND method ' % (protid, phylome_id)
    cmd += '= "%s"' % (method) if method else '!= "NJ"'
    cmd += ') ORDER BY lk DESC LIMIT 1'

    info = {}
    if self._SQL.execute(cmd):
      newick, tree_method, lk = self._SQL.fetchone()
      info.setdefault("tree", {})["tree"] = PhyloTree(newick)
      info.setdefault("tree", {})["method"] = tree_method
      info.setdefault("tree", {})["best"] = True if not method else False
      info.setdefault("tree", {})["lk"] = lk

    ## If there is not associated tree to the protein id in that phylome, return
    if info == {}:
      return info

    ## Retrieve those sequences present in the recovered tree
    cmd = 'SELECT friend_id FROM seed_friend WHERE (protid = %s AND ' % (protid)
    cmd += 'phylome_id = %s)' % (phylome_id)

    ## Define the ids set to get the available information associated to them
    ids = protid
    if self._SQL.execute(cmd):
      ids = ",".join([protid] + ['"%s"' % id[0] for id in self._SQL.fetchall()])

    ph_tbl, pc_tbl = self._phylomes_table, self._phylomes_content_table
    tr_tbl = self._trees_table
    ## Join and retrieve all the information available in the database for the
    ## sequences in the tree.
    cmd =  'SELECT p.protid, p.taxid, p.version, s.code, s.name, p.prot_name, '
    cmd += 'p.gene_name, MAX(p.copy), count(distinct method), count(distinct '
    cmd += 'sf.protid, sf.phylome_id) FROM (protein AS p, unique_protein AS u, '
    cmd += 'species AS s, %s AS ph, %s AS pc) LEFT JOIN ' % (ph_tbl, pc_tbl)
    cmd += '%s AS t ON (p.protid = t.protid) LEFT JOIN seed_friend ' % (tr_tbl)
    cmd += 'AS sf ON (p.protid = sf.friend_id) WHERE (p.protid IN (%s) ' % (ids)
    cmd += 'AND p.taxid = s.taxid AND p.protid = u.protid AND p.taxid = pc.'
    cmd += 'taxid AND ph.phylome_id = %s AND pc.phylome_id = ph.' % (phylome_id)
    cmd += 'phylome_id AND pc.version = p.version) GROUP BY p.protid'

    ## Store the information. For those sequences with more than one copy, the
    ## sequence identifier is saved for an extended search.
    if self._SQL.execute(cmd):
      extended = []
      for entry in self._SQL.fetchall():
        code = ("Phy%s_%s") % (entry[0], entry[3])
        proteome = ("%s.%s") % (entry[3], entry[2])
        info.setdefault("seq", {}).setdefault(code, {})

        info["seq"][code].setdefault("species", entry[3])
        info["seq"][code].setdefault("taxid", entry[1])
        info["seq"][code].setdefault("proteome", proteome)
        info["seq"][code].setdefault("sps_name", entry[4])
        info["seq"][code].setdefault("protein", set())
        if entry[5]:
          info["seq"][code]["protein"].add(entry[5])
        info["seq"][code].setdefault("gene", set())
        if entry[6]:
          info["seq"][code]["gene"].add(entry[5])
        copy = int(entry[7]) if entry[7] else 0
        info["seq"][code].setdefault("copy", copy)
        info["seq"][code].setdefault("trees", entry[8])
        info["seq"][code].setdefault("collateral", entry[9])
        info["seq"][code].setdefault("external", {})

        if info["seq"][code]["copy"] > 1:
          extended.append(entry[0])

      ## Look for alternative protein or/and gene names for those sequences with
      ## more that one copy
      if extended:
        ext = ",".join(['"%s"' % id for id in extended])

        cmd =  'SELECT p.protid, s.code, p.prot_name, p.gene_name FROM protein '
        cmd += 'AS p, species AS s, %s AS ph, %s AS pc WHERE' % (ph_tbl, pc_tbl)
        cmd += '(p.protid IN (%s) AND p.taxid = s.taxid AND ph.phylome_' % (ext)
        cmd += 'id = %s AND ph.phylome_id = pc.phylome_id AND p.' % (phylome_id)
        cmd += 'taxid = pc.taxid AND pc.version = p.version)'

        if self._SQL.execute(cmd):
          for entry in self._SQL.fetchall():
            code = ("Phy%s_%s") % (entry[0], entry[1])
            if entry[2]:
              info["seq"][code]["protein"].add(entry[2])
            if entry[3]:
              info["seq"][code]["gene"].add(entry[3])

    ## Get the external ids associated to each sequence in the tree.
    cmd = 'SELECT distinct p.protid, s.code, e.external_db, e.external_id FROM '
    cmd += 'protein AS p, external_id AS e, species AS s WHERE (e.protid = p.'
    cmd += 'protid AND p.protid IN (%s) AND p.taxid = s.taxid)' % (ids)

    if self._SQL.execute(cmd):
      for protid, code, db, id in self._SQL.fetchall():
        code = ("Phy%s_%s") % (protid, code)
        info["seq"][code]["external"].setdefault(db, []).append(id)

    ## Return all available information for the homolog sequences in the tree
    return info
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_available_trees_by_phylome(self, id, collateral = True):
    """ Returns all available tress for a given protid grouped by phylomes
    """

    # Check if the input parameters are well-constructed
    if not self.check_input_parameter(list_id = id, boolean = collateral):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    tr_tbl = self._trees_table
    ## Recover all trees where the input protid has been used as seed
    cmd = 'SELECT distinct phylome_id, method, p.protid, code FROM %s ' % tr_tbl
    cmd += 'AS t, species AS s, protein AS p WHERE (p.protid IN (%s) ' % protid
    cmd += 'AND p.protid = t.protid AND p.taxid = s.taxid)'

    tmp = {}
    ## Create a temporal data structure to manipulate the MySQL query results
    if self._SQL.execute(cmd):
      for phylome_id, method, prot_id, code in self._SQL.fetchall():
        prot_id = ("Phy%s_%s") % (prot_id, code)
        tmp.setdefault(str(phylome_id) + "|" + prot_id, []).append(method)

    trees = {}
    ## Create the data stucture where the functions stores the phylomes where
    ## the input protid has been used as a seed.
    for key, methods in tmp.iteritems():
      phylome_id, prot_id = key.split("|")
      trees.setdefault(int(phylome_id), []).append([True, prot_id, methods])

    ## Look for those trees where the input protid has been used as an homolog
    ## to the tree's seed protein
    if collateral:
      ## Retrieves, for each tuple (seed_protein, phylome_id), the evolutionary
      ## model/method used to generate that tree
      for seed, phylome_id in self.get_collateral_seeds(id):
        friend = self.parser_ids(seed)
        cmd =  'SELECT method FROM %s WHERE (protid = %s ' % (tr_tbl, friend)
        cmd += 'AND phylome_id = %s)' % (phylome_id)
        ## Store properly the MySQL query results
        if self._SQL.execute(cmd):
          trees.setdefault(int(phylome_id), []).append([False, seed, [m[0] \
            for m in self._SQL.fetchall()]])

    return trees
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def count_trees(self, phylome_id):
    """ Retuns the trees number for each method in a given phylome
    """

    # Check if the phylome id is well-constructed
    if not self.check_input_parameter(str_number = phylome_id):
      raise NameError("Check your input data")

    cmd =  'SELECT method, count(*) FROM %s WHERE phylome' % (self._trees_table)
    cmd += '_id = %s GROUP BY method' % (phylome_id)

    counter = {}
    if self._SQL.execute(cmd):
      for method, n in self._SQL.fetchall():
        counter[method] = int(n)
    return counter
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_phylome_trees(self, phylome_id):
    """ Returns all trees available for a given phylome
    """

    # Check if the phylome id code is well-constructed
    if not self.check_input_parameter(str_number = phylome_id):
      raise NameError("Check your input data")

    ## Get all available trees for a given phylome id
    cmd = 'SELECT protid, code, method, lk, newick FROM %s' %(self._trees_table)
    cmd += ' AS t, species AS s, %s AS ph WHERE (ph.' % (self._phylomes_table)
    cmd += 'phylome_id = %s AND ph.phylome_id = t.phylome_id AND ' %(phylome_id)
    cmd += 'ph.seed_taxid = s.taxid)'

    trees = {}
    ## Return a dictionary organized by protid. For each protid, there is a
    ## dictionary where method is used as a key of tuple (lk, newick)
    if self._SQL.execute(cmd):
      for protid, code, method, lk, newick in self._SQL.fetchall():
        id = ("Phy%s_%s") % (protid, code)
        trees.setdefault(id, {}).setdefault(method, [lk, PhyloTree(newick)])
    return trees
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seq_info_msf(self, id, phylome_id):
    """ Returns all available information for the different homologs sequences
        associated to a given seed protid and phylome id
    """

    ## Check the input parameters
    if not self.check_input_parameter(single_id = id, str_number = phylome_id):
      raise NameError("Check your input parameters")
    protid = self.parser_ids(id)

    ## Select as well the homolog sequences for the seed protein in the input
    ## phylome
    cmd =  'SELECT friend_id FROM seed_friend WHERE (protid = %s ' % (protid)
    cmd += 'AND phylome_id = %s)' % (phylome_id)

    ## Define the ids set to get the available information associated to them
    ids = None
    if self._SQL.execute(cmd):
      ids = ",".join([protid] + ['"%s"' % id[0] for id in self._SQL.fetchall()])

    ## Return an empty dictionary for those cases where there is not available
    ## information for the input protein id in the input phylome
    if not ids:
      return {}

    ph_tbl, pc_tbl = self._phylomes_table, self._phylomes_content_table
    ## Get the available information fot all of these ids
    cmd =  'SELECT p.protid, s.code, prot_name, gene_name, p.comments, seq, '
    cmd += 'MAX(copy) FROM protein AS p, unique_protein AS u, species AS s, '
    cmd += '%s AS ph, %s AS pc WHERE (p.protid IN (%s) ' % (ph_tbl, pc_tbl, ids)
    cmd += 'AND p.taxid = s.taxid AND p.protid = u.protid AND p.taxid = pc.'
    cmd += 'taxid AND ph.phylome_id = %s AND pc.phylome_id = ph.' % (phylome_id)
    cmd += 'phylome_id AND pc.version = p.version) GROUP BY p.protid'

    info = {}
    ## Store normal results and add for an extended search those sequences with
    ## more than one copy
    if self._SQL.execute(cmd):
      extended = []
      for id, code, prot, gene, comments, seq, copy in self._SQL.fetchall():

        prot_id = ("Phy%s_%s") % (id, code)
        info.setdefault(prot_id, {}).setdefault("seq", seq)
        info[prot_id].setdefault("seq_leng", len(seq))
        info[prot_id].setdefault("copy", copy if copy else 0)

        info[prot_id].setdefault("gene", set())
        info[prot_id].setdefault("protein", set())
        info[prot_id].setdefault("comments", set())

        if gene:
          info[prot_id]["gene"].add(gene)
        if prot:
          info[prot_id]["protein"].add(prot)
        if comments:
          info[prot_id]["comments"].add(comments)

        info[prot_id].setdefault("external", {})

        if info[prot_id]["copy"] > 1:
          extended.append(id)

      ## Look for alternative protein or/and gene names for those sequences with
      ## more that one copy
      if extended:
        ext = ",".join(['"%s"' % id for id in extended])

        cmd =  'SELECT protid, code, prot_name, gene_name, p.comments FROM '
        cmd += 'protein AS p, species AS s, %s AS ph, %s AS ' % (ph_tbl, pc_tbl)
        cmd += 'pc WHERE(p.protid IN (%s) AND p.taxid = s.taxid AND ph.' % (ext)
        cmd += 'phylome_id = %s AND ph.phylome_id = pc.phylome_' % (phylome_id)
        cmd += 'id AND p.taxid = pc.taxid AND pc.version = p.version)'

        if self._SQL.execute(cmd):
          for id, code, prot, gene, comments in self._SQL.fetchall():
            prot_id = ("Phy%s_%s") % (id, code)
            if gene:
              info[prot_id]["gene"].add(gene)
            if prot:
              info[prot_id]["protein"].add(prot)
            if comments:
              info[prot_id]["comments"].add(comments)

    ## Recover external references for each homolog sequences
    cmd =  'SELECT distinct p.protid, s.code, e.external_db, e.external_id FROM'
    cmd += ' protein AS p, external_id AS e, species AS s WHERE (e.protid = p.'
    cmd += 'protid AND p.protid IN (%s) AND p.taxid = s.taxid)' % ids

    if self._SQL.execute(cmd):
      for protid,code,db,id in self._SQL.fetchall():
        code = ("Phy%s_%s") % (protid, code)
        info[code]["external"].setdefault(db, []).append(id)

    ## Return the available information
    return info
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_algs(self, id, phylome_id):
    """ Given a protID, it returns a tuple with the raw_alg, clean_alg and the
        number of seqs included.
    """

    # Check if the phylome id code is well-constructed
    if not self.check_input_parameter(single_id = id, str_number = phylome_id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Get the raw and clean aligs for the input protid in the input phylome
    cmd =  'SELECT raw_alg, clean_alg, seqnumber FROM %s ' % (self._algs_table)
    cmd += 'WHERE (phylome_id = %s AND protid = %s)' % (phylome_id, protid)

    alg = {}
    ## Return the MySQL result in the proper data structure
    if self._SQL.execute(cmd):
      alg["raw_alg"], alg["clean_alg"], alg["seqnumber"] = self._SQL.fetchone()
    return alg
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_raw_alg(self, id, phylome_id):
    """ Given a protein identifier, it returns the raw alignment for that id
         in the input phylome
    """

    # Check if the input parameters are well-constructed
    if not self.check_input_parameter(single_id = id, str_number = phylome_id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Ask for the raw alignment for a given protein in the input phylome
    cmd =  'SELECT raw_alg FROM %s WHERE (phylome_id = ' % (self._algs_table)
    cmd += '%s AND protid = %s)' % (phylome_id, protid)

    if self._SQL.execute(cmd):
      return self._SQL.fetchone()[0]
    return ""
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_clean_alg(self, id, phylome_id):
    """ Given a protein identifier, it returns the clean alignment for that id
         in the input phylome
    """

    # Check if the input parameters are well-constructed
    if not self.check_input_parameter(single_id = id, str_number = phylome_id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Ask for the raw alignment for a given protein in the input phylome
    cmd =  'SELECT clean_alg FROM %s WHERE (phylome_id = ' % (self._algs_table)
    cmd += '%s AND protid = %s)' % (phylome_id, protid)

    if self._SQL.execute(cmd):
      return self._SQL.fetchone()[0]
    return ""
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def count_algs(self, phylome_id):
    """ Returns how many alignments are for a given phylome
    """

    # Check if the phylomedb id code is well-constructed
    if not self.check_input_parameter(str_number = phylome_id):
      raise NameError("Check your input data")

    al_tbl = self._algs_table
    cmd = 'SELECT count(*) FROM %s WHERE phylome_id = %s' % (al_tbl, phylome_id)

    if self._SQL.execute(cmd):
      return  int(self._SQL.fetchone()[0])
    return 0
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_phylome_algs(self, phylome_id):
    """ Returns all trees available for a given phylome
    """

    # Check if the phylome id code is well-constructed
    if not self.check_input_parameter(str_number = phylome_id):
      raise NameError("Check your input data")

    cmd = 'SELECT protid, code, raw_alg, clean_alg FROM %s ' % self._algs_table
    cmd += 'AS a, species AS s, %s AS ph WHERE (ph.' % self._phylomes_table
    cmd += 'phylome_id = %s AND ph.phylome_id = a.phylome_id AND ' % phylome_id
    cmd += 'ph.seed_taxid = s.taxid)'

    algs = {}
    if self._SQL.execute(cmd):
      for protid, code, raw, clean in self._SQL.fetchall():
        id = ("Phy%s_%s") % (protid, code)
        algs.setdefault(id, {})["raw_alg"] = raw
        algs.setdefault(id, {})["clean_alg"] = clean
    return algs
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_species(self):
    """ Returns all current registered species in the database
    """

    species = {}
    ## Returns all species that have been registered in the database
    if self._SQL.execute('SELECT taxid, code, name FROM species'):
      for taxid, code, name in self._SQL.fetchall():
        species.setdefault(code, {})["taxid"] = taxid
        species[code]["code"]  = code
        species[code]["name"]  = name

    return species
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_species_info(self, taxid = None, code = None):
    """ Returns all information on a given species/code
    """

    # Check if the input parameters is well-constructed
    if not self.check_input_parameter(number = taxid, string = code):
      raise NameError("Check your input data")

    if not taxid and not code:
      raise NameError("Define at least one input parameter")

    ## Depending on the input parameters, the search in the database is perfomed
    ## using either species taxid, or species code or both of them.
    cmd = 'SELECT taxid, code, name FROM species AS s WHERE ('
    if taxid:
      cmd += 'taxid = %s' % taxid
      cmd += '' if code else ')'

    if code:
      cmd += ' AND ' if taxid else ""
      cmd += 'code = "%s")' % code

    species = {}
    ## Return the retrieved information
    if self._SQL.execute(cmd):
      species["taxid"], species["code"], species["name"] = self._SQL.fetchone()
    return species
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_genomes(self):
    """ Returns all current available genomes/proteomes
    """

    ## Complete information about each genome adding species information
    cmd = 'SELECT g.taxid, code, version, name, source, DATE(date) FROM genome '
    cmd += 'AS g, species AS s WHERE s.taxid = g.taxid'

    genomes = []
    if self._SQL.execute(cmd):
      genomes = [ map(str, genome) for genome in self._SQL.fetchall()]
    return genomes
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_genome_info(self, genome):
    """ Returns all available information about a registered genome/proteome
    """

    # Check if the input parameter is well-constructed
    if not self.check_input_parameter(string = genome):
      raise NameError("Check your input data")

    try:
      code, version = genome.split(".")
    except:
      raise NameError("A proteome/genome should be 'species_code.version'")

    ## If the genome is well-defined, ask for its associated information
    cmd = 'SELECT g.taxid, code, version, s.name, DATE(date), source, comments '
    cmd += 'FROM genome AS g, species AS s WHERE (s.taxid = g.taxid AND code = '
    cmd += '"%s" AND version = %s)' % (code, version)

    info = {}
    ## Return the available information in a dictionary defined for that
    if self._SQL.execute(cmd):
      taxid, code, version, name, date, source, comments  = self._SQL.fetchone()
      info["date"]      = date
      info["taxid"]     = taxid
      info["source"]    = source
      info["version"]   = version
      info["species"]   = name
      info["comments"]  = comments
      info["genome_id"] = ("%s.%s") % (code, version)
    return info
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_genomes_by_species(self, taxid):
    """ Returns the different proteome/genome versions, if exists, for a given
        species
    """

    # Check if the input parameter is well-constructed
    if not self.check_input_parameter(str_number = taxid):
      raise NameError("Check your input data")

    # Look for the different versions of the input taxid
    cmd = 'SELECT taxid, version FROM genome WHERE taxid = %s ' % (taxid)

    genomes = {}
    if self._SQL.execute(cmd):
      for taxid, version in self._SQL.fetchall():
        genomes.setdefault(taxid, []).append(version)
    return genomes
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_phylomes(self):
    """ Returns all current available phylomes
    """

    ph_tbl = self._phylomes_table
    ## Recover all the phylomes stored in the database
    cmd =  'SELECT phylome_id, seed_taxid, s.name, code, seed_version, DATE'
    cmd += '(ts), ph.name, comments FROM species AS s, %s AS ph ' % (ph_tbl)
    cmd += 'WHERE (ph.seed_taxid = s.taxid)'

    phylomes = {}
    ## Generate a dictionary with all phylomes
    if self._SQL.execute(cmd):
      for phylome_id, taxid, sps_name, code, version, date, name, comments in \
        self._SQL.fetchall():

        phylomes[phylome_id] = {}
        phylomes[phylome_id]["date"]          = date
        phylomes[phylome_id]["name"]          = name
        phylomes[phylome_id]["comments"]      = comments
        phylomes[phylome_id]["seed_taxid"]    = taxid
        phylomes[phylome_id]["seed_species"]  = sps_name
        phylomes[phylome_id]["seed_proteome"] = ("%s.%s") % (code, version)

    return phylomes
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_phylome_info(self, phylome_id):
    """ Returns available information on a given phylome
    """

    # Check if the phylome id code is well-constructed
    if not self.check_input_parameter(str_number = phylome_id):
      raise NameError("Check your input data")

    ph_tbl = self._phylomes_table
    ## Get all available data for the input phylome
    cmd = 'SELECT seed_taxid, code, seed_version, DATE(ts), ph.name, comments, '
    cmd += 's.name FROM species AS s, %s AS ph WHERE (ph.phylome_id ' % (ph_tbl)
    cmd += '= %s AND ph.seed_taxid = s.taxid)' % phylome_id

    info = {}
    ## Generate a dictionary with the retrieved information
    if self._SQL.execute(cmd):
      taxid, code, version, date, name, comments, sp_name = self._SQL.fetchone()
      info["id"] = phylome_id
      info["date"]          = date
      info["name"]          = name
      info["comments"]      = comments
      info["seed_taxid"]    = taxid
      info["seed_species"]  = sp_name
      info["seed_version"]  = version
      info["seed_proteome"] = ("%s.%s") % (code, version)

    return info
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_proteomes_in_phylome(self, phylome_id):
    """ Returns a list of proteomes associated to a given phylome_id
    """

    # Check if the phylome id code is well-constructed
    if not self.check_input_parameter(str_number = phylome_id):
      raise NameError("Check your input data")

    ph_tbl, pc_tbl = self._phylomes_table, self._phylomes_content_table
    ## Retrieve all available information for those proteomes associated to the
    ## input phylome
    cmd = 'SELECT s.taxid, code, pc.version, s.name, source, date FROM species '
    cmd += 'AS s, %s AS ph, %s AS pc, genome AS g WHERE (ph.' % (ph_tbl, pc_tbl)
    cmd += 'phylome_id = %s AND ph.phylome_id = pc.phylome_id ' % (phylome_id)
    cmd += 'AND pc.taxid = s.taxid AND pc.taxid = g.taxid AND pc.version = g.'
    cmd += 'version)'

    proteomes = []
    if self._SQL.execute(cmd):
      proteomes = [ map(str, proteome) for proteome in self._SQL.fetchall()]
    return proteomes
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seqid_info(self, id):
    """ Returns available information about a given protid
    """

    # Check if the protein id is well-constructed
    if not self.check_input_parameter(single_id = id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Recover all the available information for the input protein id, including
    ## number of copies for each proteome where the protein is present among
    ## other parameters
    cmd =  'SELECT p.protid, p.taxid, version, code, name, prot_name, gene_'
    cmd += 'name, comments, seq, copy FROM protein AS p, unique_protein AS u, '
    cmd += 'species AS s WHERE (p.protid = %s AND p.protid = u.' % (protid)
    cmd += 'protid AND s.taxid = p.taxid)'

    info = {}
    ## Store the information
    if self._SQL.execute(cmd):
      for id, taxid, version, code, sp_name, prot, gene, comments, seq, copy in\
        self._SQL.fetchall():

        if not id: break
        proteome = ("%s.%s") % (code, version)
        prot_id = ("Phy%s_%s") % (id, code)

        info.setdefault("seq", seq)
        info.setdefault("taxid", taxid)
        info.setdefault("protid", prot_id)
        info.setdefault("species", sp_name)
        info.setdefault("external", {})
        info.setdefault("proteome", set()).add(proteome)

        info.setdefault("copy_number", 0)
        if info["copy_number"] < copy:
          info["copy_number"] = copy

        info.setdefault("name", {})
        info.setdefault("gene", {})
        info.setdefault("comments", {})
        if prot:
          info["name"].setdefault(proteome, set()).add(prot)
        if gene:
          info["gene"].setdefault(proteome, set()).add(gene)
        if comments:
          info["comments"].setdefault(proteome, set()).add(comments)

    ## Get additional information
    if info:
      info["isoforms"] = self.get_all_isoforms(info["protid"])

    if info:
      ## Recover external references for each homolog sequences
      cmd =  'SELECT distinct external_db, external_id FROM external_id WHERE '
      cmd += 'protid = %s' % (protid)

      if self._SQL.execute (cmd):
        for db, id in self._SQL.fetchall():
          info["external"].setdefault(db, []).append(id)

    return info
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_all_isoforms(self, id):
    """ Returns the longest isoform for a given query
    """

    ## Check if the protein id is well-constructed
    if not self.check_input_parameter(single_id = id):
      raise NameError("Check your input data")
    protid = self.parser_ids(id)

    ## Look for different isoforms asocciated to the same gene/protein
    cmd = 'SELECT isoform, longest FROM isoform WHERE (isoform = %s ' % (protid)
    cmd += 'OR longest = %s)' % (protid)

    isoforms = {}
    ## Get all posible isoforms
    if self._SQL.execute(cmd):
      ids = []
      for prot_1, prot_2 in self._SQL.fetchall():
        ids += [("Phy%s") % (prot_1), ("Phy%s") % (prot_2)]
      ids = self.parser_ids(ids)

      ## Recover some details about every isoform
      cmd = 'SELECT p.protid, code, length(u.seq) FROM protein AS p, species '
      cmd += 'AS s, unique_protein AS u WHERE (p.protid IN (%s) AND p.' % (ids)
      cmd += 'protid = u.protid AND p.taxid = s.taxid)'

      ## Store the information about each isoform if it is not the input one
      if self._SQL.execute(cmd):
        for id, species, len in self._SQL.fetchall():
          code = ("Phy%s_%s") % (id, species)
          if protid != code:
            isoforms[code] = len

    return isoforms
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seqs_in_genome(self, taxid, version, filter_isoforms = True):
    """ Returns all sequences of a given proteome
    """

    ## Check if the input parameters are well-constructed
    if not self.check_input_parameter(str_number = taxid):
      raise NameError("Check your input data")
    if not self.check_input_parameter(str_number = version, boolean = \
      filter_isoforms):
      raise NameError("Check your input data")

    if filter_isoforms:
      cmd =  'SELECT p.protid, code, prot_name, gene_name, copy, seq FROM '
      cmd += 'protein AS p, species AS s, unique_protein AS u, isoform AS i '
      cmd += 'WHERE (p.taxid = %s AND p.version = %s AND p.' % (taxid, version)
      cmd += 'protid = i.isoform AND i.version = %s AND i.longest = ' % version
      cmd += 'p.protid AND p.taxid = s.taxid AND p.protid = u.protid) GROUP BY '
      cmd += 'p.protid'
    else:
      cmd =  'SELECT p.protid, code, prot_name, gene_name, copy, seq FROM '
      cmd += 'protein AS p, species AS s, unique_protein AS u WHERE (p.taxid = '
      cmd += '%s AND p.version = %s AND p.taxid = s.taxid ' % (taxid, version)
      cmd += 'AND p.protid = u.protid) GROUP BY p.protid'

    sequences = {}
    if self._SQL.execute(cmd):
      for id, code, protein, gene, copy, seq in self._SQL.fetchall():
        protid = ("Phy%s_%s") % (id, code)
        sequences.setdefault(protid, {}).setdefault("seq", seq)
        sequences.setdefault(protid, {}).setdefault("gene", set())
        sequences.setdefault(protid, {}).setdefault("protein", set())
        if protein:
          sequences[protid]["protein"].add(protein)
        if gene:
          sequences[protid]["gene"].add(gene)

    return sequences
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seed_ids_in_phylome(self, phylome_id, start = 0, offset = None):
    """
    """

    ## Check if the input parameters are well-constructed
    if not self.check_input_parameter(str_number = phylome_id, number = offset):
      raise NameError("Check your input data")

    if not self.check_input_parameter(str_number = start):
      raise NameError("Check your input data")

    al_tbl = self._algs_table
    ph_tbl, tr_tbl = self._phylomes_table, self._trees_table
    ## Count how many proteins have been used as a seed for the input phylome
    cmd =  'SELECT count(p.protid) FROM protein AS p, %s AS ph WHERE' % (ph_tbl)
    cmd += '(phylome_id = %s AND seed_taxid = taxid AND seed_' % (phylome_id)
    cmd += 'version = version)'

    upper_limit = 0
    if self._SQL.execute(cmd):
      upper_limit = int(self._SQL.fetchone()[0])

    ## Get all information associated for a given set, it can be the whole
    ## proteome or just a subset of it, of seed protein from the input phylome
    cmd =  'SELECT p.protid, code, p.comments, gene_name, prot_name, MAX(copy),'
    cmd += ' length(seq) FROM protein AS p, %s AS ph, unique_protein' % (ph_tbl)
    cmd += ' AS u, species AS s WHERE (ph.phylome_id = %s AND ph' % (phylome_id)
    cmd += '.seed_taxid = p.taxid AND ph.seed_version = p.version AND p.protid '
    cmd += '= u.protid AND p.taxid = s.taxid) GROUP BY p.protid ORDER BY gene_'
    cmd += 'name DESC, length(seq) ASC'
    cmd += ' LIMIT %d,%d' % (start, offset) if offset else ''

    seqs, link = {}, {}
    ## Store the retrieved information and save those protein ids with more than
    ## one copy in order to extended their information such as alternative gene
    ## or protein names, comments, etc
    if self._SQL.execute(cmd):
      extended = []
      for id, code, comments, gene, prot, copy, length in self._SQL.fetchall():
        protid = ("Phy%s_%s") % (id, code)

        link.setdefault(id, protid)
        seqs.setdefault(protid, {})

        seqs[protid]["algs"] = 0
        seqs[protid]["trees"] = 0
        seqs[protid]["seq_length"] = length
        seqs[protid]["copy_number"] = copy

        seqs[protid]["comments"] = set()
        seqs[protid]["gene_name"] = set()
        seqs[protid]["prot_name"] = set()
        if gene:
          seqs[protid]["gene_name"].add(gene)
        if prot:
          seqs[protid]["prot_name"].add(prot)
        if comments:
          seqs[protid]["comments"].add(comments)

        if copy > 1:
          extended.append(id)

      ## Look for alternative protein or/and gene names for those sequences with
      ## more that one copy
      if extended:
        ext = ",".join(['"%s"' % id for id in extended])

        cmd =  'SELECT protid, code, prot_name, gene_name, p.comments FROM '
        cmd += 'protein AS p, species AS s, %s AS ph WHERE(p.protid ' % (ph_tbl)
        cmd += 'IN (%s) AND p.taxid = s.taxid AND ph.phylome_id = ' % (ext)
        cmd += '%s AND ph.seed_taxid = p.taxid AND ph.seed_' % (phylome_id)
        cmd += 'version = p.version)'

        if self._SQL.execute(cmd):
          for id, code, prot, gene, comments in self._SQL.fetchall():
            protid = ("Phy%s_%s") % (id, code)
            if gene:
              seqs[protid]["gene_name"].add(gene)
            if prot:
              seqs[protid]["prot_name"].add(gene)
            if comments:
              seqs[protid]["comments"].add(comments)

    ids = self.parser_ids(seqs.keys())
    ## Get how many trees are associated to the set of seed proteins selected
    cmd =  'SELECT protid, count(method) FROM %s WHERE (protid IN ' % (tr_tbl)
    cmd += '(%s) AND phylome_id = %s) GROUP BY protid' % (ids, phylome_id)

    if self._SQL.execute(cmd):
      for id, tree_number in self._SQL.fetchall():
        seqs[link[id]]["trees"] = int(tree_number)

    ## Get how many aligs are associated to the set of seed porteins selected
    cmd  = 'SELECT protid, raw_alg IS NOT NULL, clean_alg IS NOT NULL FROM '
    cmd += '%s WHERE (protid IN (%s) AND phylome_id = ' % (al_tbl, ids)
    cmd += '%s) GROUP BY protid' % (phylome_id)

    if self._SQL.execute(cmd):
      for id, raw, clean in self._SQL.fetchall():
        seqs[link[id]]["algs"] += 1 if raw != '0' else 0
        seqs[link[id]]["algs"] += 1 if clean != '0' else 0

    ## Return the selected set of seed proteins and the seed proteins total
    ## number for the input phylome
    return seqs, upper_limit
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_phylomes_for_seed_ids(self, seed_ids):
    """ Given a list of protein ids, return in which phylomes these proteins
        have been used as a seed
    """

    ## Check if the input parameter is well-constructed
    if not self.check_input_parameter(list_id = seed_ids):
      raise NameError("Check your input data")
    ids = self.parser_ids(seed_ids)

    tr_tbl, ph_tbl = self._trees_table, self._phylomes_table
    ## Get all phylomes where the input proteins have been used as a seed
    cmd =  'SELECT t.protid, s.code, t.phylome_id, ph.name FROM species AS s, '
    cmd += '%s AS t, %s AS ph WHERE (t.protid IN (%s) ' % (tr_tbl, ph_tbl, ids)
    cmd += 'AND t.phylome_id = ph.phylome_id AND ph.seed_taxid = s.taxid) '
    cmd += 'GROUP BY t.protid, ph.phylome_id'

    phylomes = {}
    if self._SQL.execute(cmd):
      for protid, code, phylome_id, name in self._SQL.fetchall():
        code = ("Phy%s_%s") % (protid, code)
        phylomes.setdefault(code, []).append((phylome_id, name))

    return phylomes
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seed_ids(self, phylome_id, filter_isoforms = True):
    """ Returns the seed protein ids for a given phylome being possible to
        filter out this set keeping only the longest isoforms for each one
    """

    ## Check if the input parameters are well-constructed
    if not self.check_input_parameter(str_number = phylome_id, boolean = \
      filter_isoforms):
      raise NameError("Check your input data")

    ## Get the seed species and version for the input phylome
    cmd =  'SELECT seed_taxid, seed_version FROM %s ' % (self._phylomes_table)
    cmd += 'WHERE phylome_id = %s' % (phylome_id)

    seeds = []
    ## If the phylome is registred in the database, then, get its proteome
    if self._SQL.execute(cmd):
      taxid, version = self._SQL.fetchone()

    ## if there is no information about the given phylome code, return an empty
    ## list. Otherwise, retrieve the protein ids depending on the longest
    ## isoform flag
    if not taxid or not version:
      return seeds

    if filter_isoforms:
      cmd =  'SELECT p.protid, code FROM protein AS p, species AS s, isoform '
      cmd += 'AS i WHERE (p.taxid = %s AND p.version = %s ' % (taxid, version)
      cmd += 'AND p.protid = i.isoform AND p.version = i.version AND i.longest '
      cmd += '= p.protid AND p.taxid = s.taxid)'
    else:
      cmd =  'SELECT p.protid, code FROM protein AS p, species AS s WHERE (p.'
      cmd += 'taxid = %s AND p.version = %s AND p.taxid = s.' % (taxid, version)
      cmd += 'taxid)'

    if self._SQL.execute(cmd):
      for id, code in self._SQL.fetchall():
        seeds.append(("Phy%s_%s") % (id, code))

    return seeds
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
