NCBI taxonomy tree made easy
=============================

This is a simple program that I use to query the NCBI taxonomy
tree. It requires the ETE python library (ete.cgenomics.org) and
sqlite3 to work.  Features are still very rudimentary. Please,
refer/cite this repository if you use the program.

Change log
***************
 **April 17th 2012**
 * Name searches are not case sensitive 
 * Added synonym support for name translation
 * Added fuzzy search

Requirements: 
***************

 * ETE (ete.cgenomics.org)
 * sqlite3

 * Fuzzy search (optional) requires:

   python 2.7 or pysqlite2 compiled with load_extension capabilities.
   For instance, download pysqlite2 from PyPi, comment the following line in setup.cfg: 
  
      define=SQLITE_OMIT_LOAD_EXTENSION
  
   and run "sudo python setup.py install". 

   Also, the sqlite3 extension "levenshtein.sqlext" should be present,
   so you will need to compile the SQLite extension included in this
   package.
   
   $ cd SQLite-Levenshtein
   $ make
   

Usage:
*********

update taxonomy tree (download and parse the latest NCBI taxonomy DB): 
-----------------------------------------------------------------------
  $ wget  ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz

  $ tar zxf taxdump.tar.gz 

  $ python update_taxadb.py # This may take a while

get help:
------------
  $ python ./ncbi_query.py -h 

get name-to-taxid translation: 
------------------------------------
  $ python ./ncbi_query.py -n Bos taurus, Gallus gallus, Homo sapiens 

get NCBI topology from species names:
------------------------------------------------
  $ python ./ncbi_query.py -n Bos taurus, Gallus gallus, Homo sapiens -x

get NCBI lineage and info from species names: 
------------------------------------------------
  $ python ./ncbi_query.py -n Bos taurus, Gallus gallus, Homo sapiens -i

get the same as above using taxids: 
------------------------------------
  $ python ./ncbi_query.py -t 9913 9031 9606 -x

translate names using fuzzy search queries:
------------------------------------------------

  fuzzy factor indicates the allowed level of similarity to report
  matches. i.e: 0.8 would mean that only matches changing 80% of the
  characters in the original string will be considered (case
  sensitive).

  $ python ./ncbi_query.py -n Bos tauras, gallus, Homo sapien --fuzzy 0.8


Contact: jhcepas[at]gmail.com
