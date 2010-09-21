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
from ete2 import PhyloTree

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
    self._trees_table    = "tree"
    self._phylomes_table = "phylome"
    self._algs_table     = "alignment"
    self._phylomes_content_table = "phylome_content"
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
  def get_conversion_protein(self, code):
    """ Returns the conversion between old phylome id codes and the new ones
    """

    # Check if the code is well-constructed
    if not code or type(code) != str:
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

    protid = self.parser_ids(id)
    # Check if it is an unique code that follow the phylomeDB code structure
    if not type(id) == str or not protid:
      raise NameError("Check your input data")

    # Look for different isoforms asocciated to the same gene/protein
    cmd = 'SELECT p.protid, s.code, p.version FROM protein AS p, species AS s, '
    cmd += 'isoform AS i WHERE (i.longest = p.protid AND i.version = p.version '
    cmd += 'AND p.taxid = s.taxid AND i.isoform = %s)' % protid

    # Return the longest available isoforms for each proteome where the id is
    # already register
    isoforms = {}
    if self._SQL.execute(cmd):
      for protid, code, version in self._SQL.fetchall():
        isoforms[version] = ("Phy%s_%s") % (protid, code)
    return isoforms
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def search_id(self, id):
    """ Returns a list of the longest isoforms for each proteome where the id is
        already registered. The id can be a current id version, former phylomeDB
        id or an external id.
    """

    # Check if id is valid to be searched.
    if not id or type(id) != str:
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
        if currentID: phylomeDB_matches.update(self.get_longest_isoform(currentID))

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

    # Check if the code is well-constructed
    if not external or type(external) != str:
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

    protid = self.parser_ids(id)
    # Check if the code is well-constructed
    if not protid or type(id) != str:
      raise NameError("Check your input data")

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

    protid = self.parser_ids(protid)
    ## Check if the code is well-constructed
    if not protid:
      raise NameError("Check your input data")

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

    protid = self.parser_ids(id)
    ## Check if the code is well-constructed
    if not protid or type(id) != str:
      raise NameError("Check your input protid code")

    ## Check if the phylome_id code is an integer greater than 0
    try:
      int(phylome_id)
    except:
      raise NameError("Check your input phylome id")
    if int(phylome_id) < 1:
      raise NameError("Check your input phylome id")

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
        trees.setdefault(method, {})["tree"] = tree
    return trees
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_seq_info_in_tree(self, id, phylome_id, method = None):
    """ Returns all the available information for each sequence from tree/s
        asociated to a tuple (protein, phylome) identifiers.
    """

    protid = self.parser_ids(id)
    ## Check if the code is well-constructed
    if not protid or type(id) != str:
      raise NameError("Check your input protid code")

    ## Check if the phylome_id code is an integer greater than 0
    try:
      int(phylome_id)
    except:
      raise NameError("Check your input phylome id")
    if int(phylome_id) < 1:
      raise NameError("Check your input phylome id")

    if method != None and type(method) != str:
      raise NameError("Check your input method selection")

    ## Look for the protid in the given phylome and recover, if the method is
    ## not defined, the best tree for that protein id in that phylome
    cmd =  'SELECT newick, method, lk FROM %s AS t WHERE ' % (self._trees_table)
    cmd += '(protid = %s AND phylome_id = %s AND method ' % (protid, phylome_id)
    cmd += '= "%s"' % (method) if method else '!= "NJ"'
    cmd += ') ORDER BY lk DESC LIMIT 1'

    info = {}
    if self._SQL.execute(cmd):
      newick, tree_method, lk = self._SQL.fetchone()
      info.setdefault("tree", {})["newick"] = newick
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
    ids = '%s' % protid
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

    ## Store the information
    if self._SQL.execute(cmd):
      for entry in self._SQL.fetchall():

        code = ("Phy%s_%s") % (entry[0], entry[3])
        proteome = ("%s.%s") % (entry[3], entry[2])
        info.setdefault("seq", {}).setdefault(code, {})

        info["seq"][code].setdefault("species", entry[3])
        info["seq"][code].setdefault("taxid", entry[1])
        info["seq"][code].setdefault("proteome", proteome)
        info["seq"][code].setdefault("sps_name", entry[4])
        info["seq"][code].setdefault("protein", entry[5] if entry[5] else "")
        info["seq"][code].setdefault("gene", entry[6] if entry[6] else "")
        info["seq"][code].setdefault("copy", entry[7]  if entry[7] else "")
        info["seq"][code].setdefault("trees", entry[8])
        info["seq"][code].setdefault("collateral", entry[9])
        info["seq"][code].setdefault("external", {})

    ## Get the external ids associated to each sequence in the tree.
    cmd = 'SELECT distinct p.protid, s.code, e.external_db, e.external_id FROM '
    cmd += 'protein AS p, external_id AS e, species AS s WHERE (e.protid = p.'
    cmd += 'protid AND p.protid IN (%s) AND p.taxid = s.taxid)' % (ids)

    if self._SQL.execute(cmd):
      for protid, code, db, id in self._SQL.fetchall():
        code = ("Phy%s_%s") % (protid, code)
        info["seq"][code]["external"].setdefault(db, []).append(id)
    return info
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_available_trees_by_phylome(self, id, collateral = True):
    """ Returns all available tress for a given protid grouped by phylomes
    """

    protid = self.parser_ids(id)
    ## Check if the code is well-constructed
    if not protid:
      raise NameError("Check your input protid code")

    if type(collateral) != bool:
      raise NameError("Check your input collateral flag parameter")

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

    ## Check if the phylome_id code is an integer greater than 0
    try:
      int(phylome_id)
    except:
      raise NameError("Check your input phylome id")
    if int(phylome_id) < 1:
      raise NameError("Check your input phylome id")

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

    ## Check if the phylome_id code is an integer greater than 0
    try:
      int(phylome_id)
    except:
      raise NameError("Check your input phylome id")
    if int(phylome_id) < 1:
      raise NameError("Check your input phylome id")

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
        trees.setdefault(id, {}).setdefault(method, [lk, newick])
    return trees
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

