#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/26 17:17:06

import sys
sys.path.append('../../../.')
from ete_test import CodemlTree

T = CodemlTree('(Otolemur_garnettii,(((Callithrix_jacchus,Saguinus_imperator),(Ateles_sp,Alouatta_seniculus)),((Hylobates_lar,(Pongo_pygmaeus,(Gorilla_gorilla,((Pan_paniscus,Pan_troglodytes),Homo_sapiens)))),(((Macaca_fascicularis,Macaca_mulatta),Papio_cynocephalus),((Nasalis_larvatus,((Trachypithecus_obscurus,Trachypithecus_cristatus),(Trachypithecus_geei,((Trachypithecus_johnii,Trachypithecus_vetulus),Semnopithecus_entellus)))),(Procolobus_badius,Colobus_guereza))))));')

T.link_to_alignment('measuring_protein.fasta')

T.link_to_evol_model('paml_dir/fb/fb.out','fb')

T.show()

