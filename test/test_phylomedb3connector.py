#!/usr/bin/python
### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
import sys, getopt, os, unittest
from getpass import getpass

sys.path.append(os.path.join(os.getcwd(), "../ete2/phylomedb/"))
from phylomeDB3 import PhylomeDB3Connector

host, dbase, user, port, pasw = "", "", "", "", ""

### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
class TestPhylomeDB3Connector(unittest.TestCase):

  def setUp(self):
    """ Prepare the object for the test. In this case, a db object is created
    """
    self.connection = PhylomeDB3Connector(host, dbase, user, pasw, port)


  def test_get_conversion_ids(self):
    """ Make sure that the conversion between old and current phylomeDB codes is
        working well
    """

    ## Normal Cases
    value, expected = "Hsa0000001", "Phy0007XA1_HUMAN"
    self.assertEqual(self.connection.get_conversion_protein(value), expected)

    value, expected = "Hsa1", "Phy0007XA1_HUMAN"
    self.assertEqual(self.connection.get_conversion_protein(value), expected)

    value, expected = "Sce0000301", "Phy000CVQN_YEAST"
    self.assertEqual(self.connection.get_conversion_protein(value), expected)

    ## Extreme cases: Wrong format
    value, expected = "Hsa10AFGe", None
    self.assertEqual(self.connection.get_conversion_protein(value), expected)

    value = ["Phy0008B02", "Phy0008B01"]
    self.assertRaises(NameError, self.connection.get_conversion_protein, value)

    ## Extreme cases: Managing empty parameters
    self.assertRaises(NameError, self.connection.get_conversion_protein, "")
    self.assertRaises(NameError, self.connection.get_conversion_protein, [])
    self.assertRaises(NameError, self.connection.get_conversion_protein, None)
    self.assertRaises(NameError, self.connection.get_conversion_protein, {})
    self.assertRaises(NameError, self.connection.get_conversion_protein, -125e5)

  def test_parser_ids(self):
    """ Make sure that ids are being well-parsed
    """

    ## Normal Cases
    value, expected = "Phy0008B02", '"0008B02"'
    self.assertEqual(self.connection.parser_ids(value), expected)

    value, expected = "Phy0008B02_HUMAN", '"0008B02"'
    self.assertEqual(self.connection.parser_ids(value), expected)

    value = ["Phy0008B02", "Phy0008B03", "Phy0008B01_HUMAN"]
    expected = '"0008B02", "0008B03", "0008B01"'
    self.assertEqual(self.connection.parser_ids(value), expected)

    ## Unadmitted format cases
    value, expected = "0008B02", None
    self.assertEqual(self.connection.parser_ids(value), expected)

    value, expected = ["Cas0008B02"], None
    self.assertEqual(self.connection.parser_ids(value), expected)

    ## Empty/non-compatible data cases
    self.assertRaises(NameError, self.connection.parser_ids, [])
    self.assertRaises(NameError, self.connection.parser_ids, "")
    self.assertRaises(NameError, self.connection.parser_ids, None)
    self.assertRaises(NameError, self.connection.parser_ids, ())
    self.assertRaises(NameError, self.connection.parser_ids, {})
    self.assertRaises(NameError, self.connection.parser_ids, 125.212)

  def test_get_longest_isoforms(self):
    """ Check the API is recovering correctly the longest isoforms for each
        protid
    """

    ## Normal Cases
    value = "Phy0008BO2"
    expected = {1: 'Phy0008BO3_HUMAN', 2: 'Phy0008BO2_HUMAN',
                3: 'Phy0026IBT_HUMAN'}
    self.assertEqual(self.connection.get_longest_isoform(value), expected)

    value = "Phy0008B01_HUMAN"
    expected = {1: 'Phy0008AZZ_HUMAN', 3: 'Phy002498Q_HUMAN'}
    self.assertEqual(self.connection.get_longest_isoform(value), expected)

    ## Unadmitted format cases
    value = ["Phy0008B02", "Phy0008B03", "Phy0008B01_HUMAN"]
    self.assertRaises(NameError, self.connection.get_longest_isoform, value)

    value = "0008B02"
    self.assertRaises(NameError, self.connection.get_longest_isoform, value)

    value = ["Ccs8921929"]
    self.assertRaises(NameError, self.connection.get_longest_isoform, value)

    ## Empty/non-compatible data cases
    self.assertRaises(NameError, self.connection.get_longest_isoform, [])
    self.assertRaises(NameError, self.connection.get_longest_isoform, None)
    self.assertRaises(NameError, self.connection.get_longest_isoform, "")
    self.assertRaises(NameError, self.connection.get_longest_isoform, 145)

  def test_search_id(self):
    """ Make sure that search_id function is working well. Critical function for
        the API
    """

    ## Normal Cases
    value = "Phy0008B02"
    expected = {1: 'Phy0008B02_HUMAN', 2: 'Phy0008B02_HUMAN',
                3: 'Phy0008B02_HUMAN'}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "Phy00085K5_HUMAN"
    expected = {1: 'Phy00085K5_HUMAN'}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "hola"
    expected = {1: 'Phy00350UN_436113', 2: 'Phy001FEVB_ONYPE',
                3: 'Phy001FEVB_ONYPE'}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "YBL058W"
    expected = {1: 'Phy000CVNF_YEAST', 2: 'Phy000CVNF_YEAST',
                3: 'Phy000CVNF_YEAST'}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "Sce0000029"
    expected = {1: 'Phy000CVJ3_YEAST', 2: 'Phy000CVJ3_YEAST',
                3: 'Phy000CVJ3_YEAST'}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "Hsa1"
    expected = {1: 'Phy0007XA1_HUMAN'}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "0008B0"
    expected = {}
    self.assertEqual(self.connection.search_id(value), expected)

    ## Unadmitted format cases
    value = "Phy0008B02 Phy0008B03"
    expected = {}
    self.assertEqual(self.connection.search_id(value), expected)

    value = ["Phy0008B02", "Phy0008B03", "Phy0008B01_HUMAN"]
    self.assertRaises(NameError, self.connection.search_id, value)

    ## Empty/non-compatible data cases
    self.assertRaises(NameError, self.connection.search_id, "")
    self.assertRaises(NameError, self.connection.search_id, None)
    self.assertRaises(NameError, self.connection.search_id, [])
    self.assertRaises(NameError, self.connection.search_id, -1)

  def test_external_id(self):
    """ Check if the conversion between external db ids and internal phylomeDB
        ids is working properly
    """

    ## Normal Cases
    value = "YBL058W"
    expected = {1: 'Phy000CVNF_YEAST', 2: 'Phy000CVNF_YEAST',
                3: 'Phy000CVNF_YEAST'}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "ENSACAP00000000001"
    expected = {1: 'Phy002IKCU_ANOCA'}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "O00084"
    expected = {1L: 'Phy000D234_SCHPO', 2L: 'Phy000D234_SCHPO'}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "F01D5.1"
    expected = {1L: 'Phy00033LN_CAEEL', 2L: 'Phy00033LN_CAEEL',
                3L: 'Phy00033LN_CAEEL', 4L: 'Phy00033LN_CAEEL'}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "ACYPI001241-PA"
    expected = {1L: 'Phy000XPAO_ACYPI'}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    ## Unexpected cases
    value = "Phy00033LN_CAEEL"
    expected = {}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "Phy0008B02 Phy0008B03"
    expected = {}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "TestDB1202_1201.1'"
    expected = {}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    ## Empty/non-compatible data cases
    self.assertRaises(NameError, self.connection.get_id_by_external, "")
    self.assertRaises(NameError, self.connection.get_id_by_external, None)
    self.assertRaises(NameError, self.connection.get_id_by_external, [])
    self.assertRaises(NameError, self.connection.get_id_by_external, -1)

  def test_internal_translations(self):
    """ Check if the conversion between internal phylomeDB ids and external ones
        is working well
    """

    ## Normal Cases
    value = 'Phy000CVNF_YEAST'
    expected = {'Ensembl.v59': ['YBL058W'], 'TrEMBL.2010.09': ['Q6Q5U0'],
                'protein_name': ['YBL058W', 'UBX1_YEAST'], 'gene_name':
                ['YBL058W'], 'Swiss-Prot.2010.09': ['P34223']}
    self.assertEqual(self.connection.get_id_translations(value), expected)


    value = 'Phy002IKCU_ANOCA'
    expected = {'Ensembl.v59': ['ENSACAG00000000001', 'ENSACAP00000000001',
                'ENSACAT00000000001'], 'protein_name': ['ENSACAP00000000001'],
                'gene_name': ['ENSACAP00000000001']}
    self.assertEqual(self.connection.get_id_translations(value), expected)

    value = "Phy00033LN"
    expected = {'Ensembl.v59': ['F01D5.1'], 'TrEMBL.2010.09': ['Q9XVB1'],
                'protein_name': ['F01D5.1', 'Q9XVB1_CAEEL'], 'gene_name':
                ['F01D5.1']}
    self.assertEqual(self.connection.get_id_translations(value), expected)

    value = "Phy000XPAO_ACYPI"
    expected = {'protein_name': ['ACYPI001241-PA'], 'gene_name': []}
    self.assertEqual(self.connection.get_id_translations(value), expected)

    ## Unexpected cases
    value = "Phy0008B02 Phy0008B03"
    self.assertRaises(NameError, self.connection.get_id_translations, value)

    value = "O00084"
    self.assertRaises(NameError, self.connection.get_id_translations, value)

    ## Empty/non-compatible data cases
    self.assertRaises(NameError, self.connection.get_id_translations, "")
    self.assertRaises(NameError, self.connection.get_id_translations, None)
    self.assertRaises(NameError, self.connection.get_id_translations, ())
    self.assertRaises(NameError, self.connection.get_id_translations, [])
### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****

## ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** *****
def main(argv):

  global host, dbase, user, port, pasw
  # ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
  try: opts, args = getopt.getopt(argv, "h:d:u:p:s:")
  except getopt.GetoptError: sys.exit("ERROR: Check the input parameters")

  for opt, arg in opts:
    if   opt in ("-h"):  host  = str(arg)
    elif opt in ("-d"):  dbase = str(arg)
    elif opt in ("-u"):  user  = str(arg)
    elif opt in ("-p"):  port  = str(arg)
    elif opt in ("-s"):  pasw  = str(arg)
    else: sys.exit("ERROR: Parameter not available")

  # ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
  if host and dbase and user and port:
    if not pasw:
      pasw = getpass("\nPhylomeDB Password: ")

  while True:
    try:
      suite = unittest.TestLoader().loadTestsFromTestCase(TestPhylomeDB3Connector)
    except:
      print("\nPlease, fullfill this information:")
    else:
      break

    host  = raw_input(" PhylomeDB Host: ")
    dbase = raw_input(" PhylomeDB DB: ")
    port  = raw_input(" PhylomeDB Port: ")
    user  = raw_input(" PhylomeDB User: ")
    pasw  = getpass(" PhylomeDB Password: ")
  # ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****

  unittest.TextTestRunner(verbosity = 3).run(suite)

  # ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****

### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
