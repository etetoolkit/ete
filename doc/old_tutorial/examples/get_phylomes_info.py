from ete3 import PhylomeDBConnector
# This connects to the main phylomeDB server (default parameters)
p = PhylomeDBConnector()
# Obtains a list of available phylomes
phylomes_list = p.get_phylomes()
# Obtains the list of proteomes used in phylome 1 (the human phylome)
phylomes_list = p.get_proteomes_in_phylome(1)
# all seeds (potentially, trees) in the human phylome
all_seed_sequences = p.get_seed_ids(1)
# Gets species info from associated to the  "Hsa" code
print p.get_species_info("Hsa")
# {'code': 'Hsa', 'taxid': 9606L, 'name': 'Homo_sapiens'}
#
# You can also use the same method to find the species code given a ncbi taxid
print p.get_species_info(9606)
# {'code': 'Hsa', 'taxid': 9606L, 'name': 'Homo_sapiens'}
#
# Get phylomeDB IDs matching a given Ensembl protein ID. Always
# returns the code of the longest isoform.
idmatches = p.search_id("ENSG00000146556")
# You can also use the search_id method to find the longest isoform of
# the gene associated to a given phylomeID. Note that phylomeDB trees
# are always reconstructed using the longest isoform associated to a
# gene.
#
print p.search_id("Hsa0000125")
# ['Hsa0000122']
