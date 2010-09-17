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
  def __init__(self, host = "84.88.66.245", db = "phylomeDB", user = "public", \
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
    if user == "phyAdmin":
      self._trees_table    = "tree"
      self._algs_table     = "alignment"
      self._phylomes_table = "phylome"
    else:
      self._trees_table    = "tree_" + user
      self._algs_table     = "alignment_" + user
      self._phylomes_table = "phylome_" + user
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def parser_ids(self, ids):
    """ Returns a string with the input id/s ready to be used in any MySQL query
    """

    parser = lambda id: id[3:10] if ID_PATTERN.match(id) else id
    if type(ids) == str: ids = [ids]

    if type(ids) in ITERABLE_TYPES:
      return ', ' .join(['"%s"' % parser(n) for n in ids])

    return None
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_conversion_protein(self, code):
    """ Returns the conversion between old phylome id codes and the new ones
    """

    # Look if the given code can be mapped into the phylomeDB dabatase
    cmd =  'SELECT protid, code FROM old_protein, species WHERE (species.taxid '
    cmd += '= old_protein.taxid AND old_code = "%s" AND old_protid =' % code[:3]
    cmd += ' %s)' % code[3:]

    # If everything is fine, return the new id
    if self._SQL.execute (cmd):
      code = self._SQL.fetchone()
      if code: return ("Phy%s_%s") % (code[0], code[1])
    return None
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **
  def get_longest_isoform(self, id):
    """ Returns the longest isoform for a given id
    """

    # Look for different isoforms asocciated to the same gene/protein
    cmd = 'SELECT p.protid, s.code, p.version FROM protein AS p, species AS s, '
    cmd += 'isoform AS i WHERE (i.longest = p.protid AND i.version = p.version '
    cmd += 'AND p.taxid = s.taxid AND i.isoform = %s)' % self.parser_ids(id)

    isoforms = {}
    if self._SQL.execute(cmd):
      for protid, code, version in self._SQL.fetchall():
        isoforms[version] = ("Phy%s_%s") % (protid, code)
    return isoforms
  ### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** **

