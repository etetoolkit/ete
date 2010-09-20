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

    cmd  = 'SELECT distinct protein.protid, code, phylome_id FROM seed_friend, '
    cmd += 'species, protein WHERE (friend_id IN (%s) ' %self.parser_ids(protid)
    cmd += 'AND seed_friend.protid = protein.protid AND protein.taxid = '
    cmd += 'species.taxid)'

    if self._SQL.execute(cmd):
      return self._SQL.fetchall()
    return []
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_tree(self, protid, phylome_id, method = None):
    """ Returns the tree associated with a given method for a the tuple protid,
        phylome_id. If method is not defined then the functions returns all
        available trees for the protid in the given phylome_id
    """

    cmd = 'SELECT newick, method, lk FROM %s WHERE (phylome' % self._trees_table
    cmd += '_id = %s AND protid = %s' % (phylome_id, self.parser_ids(protid))
    cmd += ' AND method = "%s")' % method if method else ')'

    trees = {}
    if self._SQL.execute(cmd):
      for tree, method, lk in self._SQL.fetchall():
        trees.setdefault(method, {})["lk"] = lk
        trees.setdefault(method, {})["tree"] = tree
    return trees
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
