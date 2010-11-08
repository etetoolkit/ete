#!/usr/bin/python
### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
import sys, getopt, os, unittest, datetime
from getpass import getpass

sys.path.append(os.path.join(os.getcwd(), "../ete2/phylomedb/"))
from phylomeDB3 import PhylomeDB3Connector

host = "phylomedb.org"
dbase = "phylomedb_3"
user = "public"
port = 3306
pasw = "public"

### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
searched_1 = {'SYNPW': {1: ['Phy0025Y50_SYNPW']}, 'ACAM1': {1: ['Phy00255BN_ACAM1']}, 'PROMS': {1: ['Phy001GXRH_PROMS'], 2: ['Phy001GXRH_PROMS']}, 'SYNS3': {2: ['Phy0032Y3K_SYNS3']}, 'SYNJA': {1: ['Phy001YFR0_SYNJA'], 2: ['Phy001YFR0_SYNJA']}, 'SYNJB': {1: ['Phy001ML5W_SYNJB'], 2: ['Phy001ML5W_SYNJB'], 3: ['Phy001ML5W_SYNJB']}, 'PROM5': {1: ['Phy0032TSR_PROM5']}, 'PROM4': {1: ['Phy0032PYP_PROM4']}, 'PROM3': {1: ['Phy0025VSW_PROM3']}, 'PROM2': {1: ['Phy0032RRI_PROM2']}, 'PROM1': {1: ['Phy0032VGD_PROM1']}, 'PROM0': {1: ['Phy0025VGZ_PROM0']}, '167539': {1: ['Phy001W7DU_167539'], 2: ['Phy001W7DU_167539']}, 'SYNP2': {1: ['Phy0032ZT8_SYNP2']}, 'SYNP6': {1: ['Phy001NTRH_SYNP6'], 2: ['Phy001NTRH_SYNP6'], 3: ['Phy001NTRH_SYNP6']}, 'SYNR3': {1: ['Phy002602V_SYNR3']}}

tree_1 = {'WAG': {'tree': '(((((((Phy0004PJ7_CRYNE:0.764739,Phy000EWDU_YARLI:0.796761)0.867000:0.138011,(Phy0007S7S_GIBZE:0.436611,Phy000AW9E_NEUCR:0.446933)0.999850:0.389361)0.731000:0.076737,(((((Phy00057S0_DICDI:0.560334,(Phy000B3RA_PLAFA:0.208866,Phy000C5A9_PLAYO:0.320387)0.999850:1.039263)0.872000:0.194674,((Phy0001H3K_ARATH:1.073939,(Phy00014K1_ARATH:0.041448,Phy00017N5_ARATH:0.010695)0.980000:0.237843)0.908000:0.152943,(Phy00015YL_ARATH:0.087938,Phy0001SFG_ARATH:0.169291)0.999000:0.305849)0.999850:0.469297)0.213000:0.048819,Phy0008TSZ_LEIMA:1.700022)0.490000:0.082001,(((((Phy00000DT_ANOGA:0.423273,Phy0005XAP_DROME:0.626117)0.909000:0.157770,Phy0000P6F_APIME:0.551249)0.842000:0.095758,Phy0005ZK6_DROME:1.369223)0.924000:0.130245,((((((((Phy000AACP_MACMU:0.005049,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.928000:0.011797,(Phy0003QBK_CANFA:0.004803,(Phy00022Q2_BOVIN:0.006368,(((Phy000CGZG_RAT:0.252911,Phy0009LMB_MOUSE:0.035141)0.365746:0.002195,Phy000A62H_MOUSE:0.003603)0.027000:0.000034,Phy000CLXL_RAT:0.001436)0.974000:0.016713)0.468000:0.006206)0.792000:0.008472)0.971000:0.037932,Phy00098SP_MONDO:0.052782)0.515000:0.023175,Phy0007DAU_CHICK:0.069170)0.988000:0.097265,(Phy0006CSG_DANRE:0.126699,(Phy000D9JL_TETNG:0.010249,Phy0006ZSN_TAKRU:0.073435)0.999850:0.198965)0.892000:0.066872)0.982000:0.123649,((((Phy000CO1I_RAT:0.026050,Phy000A35T_MOUSE:0.061791)0.999850:0.058648,((((Phy000ASI0_MACMU:0.011440,(Phy000BUTW_PANTR:0.018323,Phy0008J14_HUMAN:0.000000)0.999850:0.059770)0.460000:0.003619,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.770000:0.003106)0.982000:0.023214,Phy0003SSX_CANFA:0.016193)0.288000:0.012134,Phy0002BMQ_BOVIN:0.050012)0.625000:0.006330)0.968000:0.068411,Phy0008ZAA_MONDO:0.088010)0.974000:0.102663,Phy0007CQ6_CHICK:0.087112)0.999850:0.487832)0.972000:0.117309,Phy0004H5V_CIOIN:0.548974)0.524000:0.024198,((((((((Phy0008A3X_HUMAN:0.003726,Phy000AJXF_MACMU:0.015197)0.152528:0.000358,Phy000BD05_PANTR:0.008154)0.994000:0.052312,((Phy000A0DO_MOUSE:0.007421,Phy0009U78_MOUSE:0.040419)0.944000:0.024547,Phy000CPNE_RAT:0.016885)0.999850:0.076406)0.880000:0.019001,Phy0003L1L_CANFA:0.049133)0.847000:0.017766,Phy00029HZ_BOVIN:0.003484)0.962000:0.108542,Phy0009GEH_MONDO:0.533937)0.979000:0.228955,Phy0007FZD_CHICK:0.181892)0.979000:0.340482,(Phy0006QQY_TAKRU:0.273894,Phy000692N_DANRE:0.255238)0.976000:0.247235)0.999000:0.600529)0.898000:0.083309)0.812000:0.072951,(Phy00036IS_CAEEL:0.291792,Phy0002S9O_CAEBR:0.206941)0.999850:0.861829)0.953000:0.159395)0.983000:0.209727,Phy000D22G_SCHPO:0.982238)0.855000:0.106908)0.999850:0.369274,((Phy000CVNF_YEAST:0.400542,Phy000467C_CANGA:0.320157)0.633000:0.058488,(Phy0000F1K_ASHGO:0.403569,Phy0008N76_KLULA:0.388617)0.545000:0.086135)0.999000:0.275963)0.999850:0.363936,(Phy0005KKR_DEBHA:0.147391,Phy0005KKQ_DEBHA:0.087226)0.989000:0.180504)0.999000:0.218984,Phy0002JCH_CANAL:0.000000)0.974000:0.020314,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24451.799999999999}, 'JTT': {'tree': '(((((((Phy000D22G_SCHPO:0.998857,Phy0004PJ7_CRYNE:0.788235)0.486000:0.127258,((((Phy00057S0_DICDI:0.593594,(Phy000B3RA_PLAFA:0.234012,Phy000C5A9_PLAYO:0.356383)0.999850:1.184190)0.864000:0.213265,((Phy0001H3K_ARATH:1.163301,(Phy00014K1_ARATH:0.041030,Phy00017N5_ARATH:0.009697)0.977000:0.235741)0.899000:0.162192,(Phy00015YL_ARATH:0.086894,Phy0001SFG_ARATH:0.165512)0.999850:0.322508)0.999850:0.517152)0.501000:0.143990,(((((Phy00000DT_ANOGA:0.473443,Phy0005XAP_DROME:0.663322)0.896000:0.163476,Phy0000P6F_APIME:0.612124)0.735000:0.100547,Phy0005ZK6_DROME:1.521321)0.893000:0.132818,((Phy0004H5V_CIOIN:0.580561,((((((((Phy0008A3X_HUMAN:0.003951,Phy000AJXF_MACMU:0.015636)0.147017:0.000306,Phy000BD05_PANTR:0.008460)0.994000:0.055454,((Phy000A0DO_MOUSE:0.007711,Phy0009U78_MOUSE:0.041190)0.956000:0.025421,Phy000CPNE_RAT:0.016948)0.999000:0.080391)0.867000:0.018436,Phy0003L1L_CANFA:0.051270)0.859000:0.021096,Phy00029HZ_BOVIN:0.001801)0.943000:0.116294,Phy0009GEH_MONDO:0.559427)0.976000:0.242652,Phy0007FZD_CHICK:0.181770)0.973000:0.366340,(Phy0006QQY_TAKRU:0.282120,Phy000692N_DANRE:0.279568)0.969000:0.271678)0.999850:0.677672)0.378667:0.027348,((((((Phy0003QBK_CANFA:0.004923,(Phy00022Q2_BOVIN:0.006082,((Phy000A62H_MOUSE:0.003147,(Phy000CGZG_RAT:0.249021,Phy0009LMB_MOUSE:0.034391)0.423935:0.002235)0.110000:0.000812,Phy000CLXL_RAT:0.000993)0.972000:0.016475)0.413000:0.006090)0.793000:0.007811,(Phy000AACP_MACMU:0.004952,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.936000:0.011763)0.982000:0.037209,Phy00098SP_MONDO:0.051791)0.545000:0.023993,Phy0007DAU_CHICK:0.066820)0.987000:0.095218,(Phy0006CSG_DANRE:0.122531,(Phy000D9JL_TETNG:0.011419,Phy0006ZSN_TAKRU:0.072270)0.999850:0.198140)0.955000:0.077623)0.952000:0.115041,((((Phy000CO1I_RAT:0.025459,Phy000A35T_MOUSE:0.061831)0.998000:0.060550,((((Phy000ASI0_MACMU:0.011671,(Phy000BUTW_PANTR:0.018519,Phy0008J14_HUMAN:0.000000)0.999850:0.060536)0.246000:0.003415,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.753000:0.003169)0.982000:0.023453,Phy0003SSX_CANFA:0.016117)0.227000:0.011521,Phy0002BMQ_BOVIN:0.050716)0.291000:0.005696)0.974000:0.069531,Phy0008ZAA_MONDO:0.090519)0.967000:0.105266,Phy0007CQ6_CHICK:0.085692)0.999850:0.526413)0.971000:0.134615)0.873000:0.116707)0.681000:0.073578,(Phy00036IS_CAEEL:0.324714,Phy0002S9O_CAEBR:0.196466)0.999850:1.013328)0.939000:0.167803)0.015000:0.145597,Phy0008TSZ_LEIMA:1.936822)0.751000:0.160994)0.685000:0.107045,(Phy000EWDU_YARLI:0.926945,(Phy0007S7S_GIBZE:0.450888,Phy000AW9E_NEUCR:0.443056)0.999850:0.405269)0.258000:0.065433)0.999850:0.426765,((Phy000CVNF_YEAST:0.433504,Phy000467C_CANGA:0.328907)0.791000:0.077120,(Phy0000F1K_ASHGO:0.431968,Phy0008N76_KLULA:0.416001)0.534000:0.082005)0.997000:0.291294)0.999850:0.423195,(Phy0005KKR_DEBHA:0.158081,Phy0005KKQ_DEBHA:0.084606)0.985000:0.179583)0.997000:0.241633,Phy0002JCH_CANAL:0.000000)0.968000:0.020276,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24493.099999999999}, 'Blosum62': {'tree': '(((((((Phy0004PJ7_CRYNE:0.748069,Phy000EWDU_YARLI:0.774169)0.886000:0.130830,(Phy0007S7S_GIBZE:0.430663,Phy000AW9E_NEUCR:0.439396)0.999850:0.376435)0.838000:0.081726,(((((Phy00057S0_DICDI:0.545879,(Phy000B3RA_PLAFA:0.210477,Phy000C5A9_PLAYO:0.336658)0.999850:1.008064)0.882000:0.165750,((Phy0001H3K_ARATH:0.997109,(Phy00014K1_ARATH:0.041773,Phy00017N5_ARATH:0.011407)0.984000:0.250222)0.901000:0.145910,(Phy00015YL_ARATH:0.090015,Phy0001SFG_ARATH:0.175984)0.999850:0.290460)0.999850:0.416681)0.127000:0.055163,Phy0008TSZ_LEIMA:1.548281)0.570000:0.083687,(((((Phy00000DT_ANOGA:0.414017,Phy0005XAP_DROME:0.607783)0.884000:0.146314,Phy0000P6F_APIME:0.545686)0.754000:0.075701,Phy0005ZK6_DROME:1.254874)0.936000:0.136983,((((((((Phy000AACP_MACMU:0.005233,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.920000:0.011473,(Phy0003QBK_CANFA:0.004782,(Phy00022Q2_BOVIN:0.006726,((Phy000A62H_MOUSE:0.003269,(Phy000CGZG_RAT:0.258214,Phy0009LMB_MOUSE:0.034201)0.695617:0.004688)0.042000:0.000687,Phy000CLXL_RAT:0.001328)0.973000:0.017320)0.416000:0.006328)0.846000:0.009884)0.986000:0.039479,Phy00098SP_MONDO:0.054621)0.018000:0.020662,Phy0007DAU_CHICK:0.074659)0.990000:0.100070,(Phy0006CSG_DANRE:0.129331,(Phy000D9JL_TETNG:0.012534,Phy0006ZSN_TAKRU:0.073241)0.999850:0.201368)0.876000:0.065736)0.988000:0.130366,((((Phy000CO1I_RAT:0.027672,Phy000A35T_MOUSE:0.064005)0.999000:0.058797,((((Phy000ASI0_MACMU:0.011805,(Phy000BUTW_PANTR:0.019045,Phy0008J14_HUMAN:0.000000)0.999850:0.062794)0.396000:0.003808,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.766000:0.003199)0.974000:0.024241,Phy0003SSX_CANFA:0.016562)0.455000:0.012431,Phy0002BMQ_BOVIN:0.051413)0.738000:0.007884)0.974000:0.070722,Phy0008ZAA_MONDO:0.089106)0.971000:0.098997,Phy0007CQ6_CHICK:0.093972)0.999850:0.484601)0.973000:0.116038,Phy0004H5V_CIOIN:0.527687)0.332000:0.027795,((((((((Phy0008A3X_HUMAN:0.004050,Phy000AJXF_MACMU:0.015839)0.143625:0.000254,Phy000BD05_PANTR:0.008554)0.997000:0.054493,((Phy000A0DO_MOUSE:0.007577,Phy0009U78_MOUSE:0.043960)0.924000:0.023491,Phy000CPNE_RAT:0.018241)0.999850:0.078903)0.892000:0.021644,Phy0003L1L_CANFA:0.050957)0.696000:0.019458,Phy00029HZ_BOVIN:0.002106)0.972000:0.121611,Phy0009GEH_MONDO:0.521687)0.983000:0.221239,Phy0007FZD_CHICK:0.195348)0.984000:0.340177,(Phy0006QQY_TAKRU:0.276818,Phy000692N_DANRE:0.251518)0.977000:0.230645)0.999850:0.548967)0.912000:0.080761)0.821000:0.066559,(Phy00036IS_CAEEL:0.277003,Phy0002S9O_CAEBR:0.225597)0.999850:0.805706)0.952000:0.140788)0.987000:0.195004,Phy000D22G_SCHPO:0.919244)0.852000:0.095263)0.999850:0.339395,((Phy000CVNF_YEAST:0.397957,Phy000467C_CANGA:0.333970)0.589000:0.049233,(Phy0000F1K_ASHGO:0.403358,Phy0008N76_KLULA:0.382255)0.390000:0.090115)0.998000:0.277647)0.999000:0.336982,(Phy0005KKR_DEBHA:0.148256,Phy0005KKQ_DEBHA:0.092523)0.996000:0.192444)0.999000:0.207493,Phy0002JCH_CANAL:0.000000)0.983000:0.021586,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24777.5}, 'VT': {'tree': '(((((((Phy0004PJ7_CRYNE:0.844473,Phy000EWDU_YARLI:0.878349)0.820000:0.131753,(Phy0007S7S_GIBZE:0.466848,Phy000AW9E_NEUCR:0.485558)0.999850:0.422281)0.822000:0.096765,(((((Phy00057S0_DICDI:0.607213,(Phy000B3RA_PLAFA:0.242761,Phy000C5A9_PLAYO:0.366222)0.999850:1.234553)0.890000:0.212396,((Phy0001H3K_ARATH:1.169490,(Phy00014K1_ARATH:0.043357,Phy00017N5_ARATH:0.010597)0.973000:0.286896)0.858000:0.147276,(Phy00015YL_ARATH:0.087686,Phy0001SFG_ARATH:0.183279)0.999000:0.327561)0.999000:0.519295)0.861000:0.122802,(((((Phy00000DT_ANOGA:0.462429,Phy0005XAP_DROME:0.704665)0.890000:0.176542,Phy0000P6F_APIME:0.622938)0.816000:0.102155,Phy0005ZK6_DROME:1.552412)0.896000:0.112341,((Phy0004H5V_CIOIN:0.583775,((((((((Phy0008A3X_HUMAN:0.004169,Phy000AJXF_MACMU:0.016203)0.144247:0.000266,Phy000BD05_PANTR:0.008689)0.991000:0.056357,((Phy000A0DO_MOUSE:0.008431,Phy0009U78_MOUSE:0.043438)0.924000:0.024716,Phy000CPNE_RAT:0.018227)0.998000:0.083189)0.865000:0.022112,Phy0003L1L_CANFA:0.053513)0.840000:0.016655,Phy00029HZ_BOVIN:0.004918)0.954000:0.122528,Phy0009GEH_MONDO:0.562883)0.983000:0.249483,Phy0007FZD_CHICK:0.208065)0.984000:0.366035,(Phy0006QQY_TAKRU:0.292639,Phy000692N_DANRE:0.277838)0.972000:0.261608)0.998000:0.647437)0.170000:0.045274,((((((Phy0003QBK_CANFA:0.005031,(Phy00022Q2_BOVIN:0.006437,((Phy000A62H_MOUSE:0.003400,(Phy000CGZG_RAT:0.261587,Phy0009LMB_MOUSE:0.035335)0.640106:0.003730)0.026000:0.000554,Phy000CLXL_RAT:0.001281)0.976000:0.017328)0.428000:0.006332)0.842000:0.009254,(Phy000AACP_MACMU:0.005163,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.926000:0.011579)0.980000:0.039207,Phy00098SP_MONDO:0.055156)0.233000:0.021708,Phy0007DAU_CHICK:0.074253)0.985000:0.098874,(Phy0006CSG_DANRE:0.130505,(Phy000D9JL_TETNG:0.013533,Phy0006ZSN_TAKRU:0.074270)0.999850:0.210952)0.894000:0.070241)0.980000:0.129239,((((Phy000CO1I_RAT:0.026397,Phy000A35T_MOUSE:0.066389)0.993000:0.059532,((((Phy000ASI0_MACMU:0.011879,(Phy000BUTW_PANTR:0.019171,Phy0008J14_HUMAN:0.000000)0.999850:0.063156)0.214000:0.003704,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.767000:0.003217)0.975000:0.024725,Phy0003SSX_CANFA:0.016227)0.402000:0.012807,Phy0002BMQ_BOVIN:0.051587)0.801000:0.008826)0.975000:0.069040,Phy0008ZAA_MONDO:0.094586)0.980000:0.102888,Phy0007CQ6_CHICK:0.097018)0.999850:0.520684)0.945000:0.113379)0.858000:0.119633)0.801000:0.085029,(Phy00036IS_CAEEL:0.320920,Phy0002S9O_CAEBR:0.241136)0.999850:0.994632)0.940000:0.149164)0.218000:0.112628,Phy0008TSZ_LEIMA:1.926060)0.831000:0.119723,Phy000D22G_SCHPO:1.108053)0.903000:0.135897)0.998000:0.365699,((Phy000CVNF_YEAST:0.443713,Phy000467C_CANGA:0.354185)0.605000:0.062898,(Phy0000F1K_ASHGO:0.451066,Phy0008N76_KLULA:0.414468)0.841000:0.105805)0.996000:0.305732)0.999850:0.394010,(Phy0005KKR_DEBHA:0.166384,Phy0005KKQ_DEBHA:0.095165)0.997000:0.207078)0.997000:0.234664,Phy0002JCH_CANAL:0.000000)0.968000:0.022076,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24754.299999999999}}

tree_2 = {'WAG': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108966,(Phy000CVLS_YEAST:0.209734,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025782,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.964000:0.107553)0.648000:0.118969)0.756000:0.023454)0.125038:0.000000);', 'lk': -234.922}, 'JTT': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108342,(Phy000CVLS_YEAST:0.212821,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025083,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.950000:0.104729)0.620000:0.117294)0.693659:0.022298)0.125038:0.000000);', 'lk': -231.99600000000001}, 'Blosum62': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.109694,(Phy000CVLS_YEAST:0.207014,(Phy000CVIE_YEAST:0.000047,(Phy000CYBL_YEAST:0.025515,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.951000:0.106396)0.648000:0.117220)0.719000:0.023232)0.125038:0.000000);', 'lk': -238.006}, 'VT': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.110159,(Phy000CVLS_YEAST:0.217995,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025534,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.960000:0.106863)0.491000:0.126230)0.566848:0.020087)0.125038:0.000000);', 'lk': -240.708}, 'NJ': {'tree': '(Phy000CZQW_YEAST:0.163164,Phy000CY0I_YEAST:0.000000,(Phy000CY0I_YEAST:0.000000,(Phy000CVLS_YEAST:0.141465,(Phy000CVIE_YEAST:0.029137,(Phy000CWXJ_YEAST:0.000000,(Phy000CXBC_YEAST:0.000000,Phy000CYBL_YEAST:0.026158)1.000000:0.001052)1.000000:0.076182)1.000000:0.090556)1.000000:0.118308)1.000000:0.032708);', 'lk': 0.0}}

tree_entry_1 = {1: [[True, 'Phy0008BO3_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']], [False, 'Phy0008JFW_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']], [False, 'Phy0008J14_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']], [False, 'Phy0008A3X_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']]], 3: [[False, 'Phy000CVNF_YEAST', ['Blosum62', 'JTT', 'NJ', 'VT', 'WAG']]], 6: [[False, 'Phy000467C_CANGA', ['Blosum62', 'JTT', 'NJ', 'VT', 'WAG']]], 10: [[False, 'Phy0000F1K_ASHGO', ['Blosum62', 'JTT', 'VT', 'WAG']]], 16: [[False, 'Phy0010CMS_ACYPI', ['JTT', 'NJ']]], 19: [[False, 'Phy000CVNF_YEAST', ['JTT', 'NJ', 'RtREV', 'VT']]], 22: [[False, 'Phy000V3G9_SCHMA', ['Blosum62', 'JTT', 'VT', 'WAG']]], 23: [[False, 'Phy0002JCG_CANAL', ['Blosum62', 'JTT', 'NJ', 'VT', 'WAG']]]}

complete_tree_1 =  {'tree': {'lk': -24451.799999999999, 'method': 'WAG', 'best': True, 'tree': '(((((((Phy0004PJ7_CRYNE:0.764739,Phy000EWDU_YARLI:0.796761)0.867000:0.138011,(Phy0007S7S_GIBZE:0.436611,Phy000AW9E_NEUCR:0.446933)0.999850:0.389361)0.731000:0.076737,(((((Phy00057S0_DICDI:0.560334,(Phy000B3RA_PLAFA:0.208866,Phy000C5A9_PLAYO:0.320387)0.999850:1.039263)0.872000:0.194674,((Phy0001H3K_ARATH:1.073939,(Phy00014K1_ARATH:0.041448,Phy00017N5_ARATH:0.010695)0.980000:0.237843)0.908000:0.152943,(Phy00015YL_ARATH:0.087938,Phy0001SFG_ARATH:0.169291)0.999000:0.305849)0.999850:0.469297)0.213000:0.048819,Phy0008TSZ_LEIMA:1.700022)0.490000:0.082001,(((((Phy00000DT_ANOGA:0.423273,Phy0005XAP_DROME:0.626117)0.909000:0.157770,Phy0000P6F_APIME:0.551249)0.842000:0.095758,Phy0005ZK6_DROME:1.369223)0.924000:0.130245,((((((((Phy000AACP_MACMU:0.005049,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.928000:0.011797,(Phy0003QBK_CANFA:0.004803,(Phy00022Q2_BOVIN:0.006368,(((Phy000CGZG_RAT:0.252911,Phy0009LMB_MOUSE:0.035141)0.365746:0.002195,Phy000A62H_MOUSE:0.003603)0.027000:0.000034,Phy000CLXL_RAT:0.001436)0.974000:0.016713)0.468000:0.006206)0.792000:0.008472)0.971000:0.037932,Phy00098SP_MONDO:0.052782)0.515000:0.023175,Phy0007DAU_CHICK:0.069170)0.988000:0.097265,(Phy0006CSG_DANRE:0.126699,(Phy000D9JL_TETNG:0.010249,Phy0006ZSN_TAKRU:0.073435)0.999850:0.198965)0.892000:0.066872)0.982000:0.123649,((((Phy000CO1I_RAT:0.026050,Phy000A35T_MOUSE:0.061791)0.999850:0.058648,((((Phy000ASI0_MACMU:0.011440,(Phy000BUTW_PANTR:0.018323,Phy0008J14_HUMAN:0.000000)0.999850:0.059770)0.460000:0.003619,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.770000:0.003106)0.982000:0.023214,Phy0003SSX_CANFA:0.016193)0.288000:0.012134,Phy0002BMQ_BOVIN:0.050012)0.625000:0.006330)0.968000:0.068411,Phy0008ZAA_MONDO:0.088010)0.974000:0.102663,Phy0007CQ6_CHICK:0.087112)0.999850:0.487832)0.972000:0.117309,Phy0004H5V_CIOIN:0.548974)0.524000:0.024198,((((((((Phy0008A3X_HUMAN:0.003726,Phy000AJXF_MACMU:0.015197)0.152528:0.000358,Phy000BD05_PANTR:0.008154)0.994000:0.052312,((Phy000A0DO_MOUSE:0.007421,Phy0009U78_MOUSE:0.040419)0.944000:0.024547,Phy000CPNE_RAT:0.016885)0.999850:0.076406)0.880000:0.019001,Phy0003L1L_CANFA:0.049133)0.847000:0.017766,Phy00029HZ_BOVIN:0.003484)0.962000:0.108542,Phy0009GEH_MONDO:0.533937)0.979000:0.228955,Phy0007FZD_CHICK:0.181892)0.979000:0.340482,(Phy0006QQY_TAKRU:0.273894,Phy000692N_DANRE:0.255238)0.976000:0.247235)0.999000:0.600529)0.898000:0.083309)0.812000:0.072951,(Phy00036IS_CAEEL:0.291792,Phy0002S9O_CAEBR:0.206941)0.999850:0.861829)0.953000:0.159395)0.983000:0.209727,Phy000D22G_SCHPO:0.982238)0.855000:0.106908)0.999850:0.369274,((Phy000CVNF_YEAST:0.400542,Phy000467C_CANGA:0.320157)0.633000:0.058488,(Phy0000F1K_ASHGO:0.403569,Phy0008N76_KLULA:0.388617)0.545000:0.086135)0.999000:0.275963)0.999850:0.363936,(Phy0005KKR_DEBHA:0.147391,Phy0005KKQ_DEBHA:0.087226)0.989000:0.180504)0.999000:0.218984,Phy0002JCH_CANAL:0.000000)0.974000:0.020314,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);'}, 'seq': {'Phy000ASI0_MACMU': {'collateral': 4L, 'copy': 1, 'taxid': 9544L, 'trees': 0L, 'proteome': 'MACMU.1', 'sps_name': 'Macaca mulatta', 'gene': set(['ENSMMUP00000001465']), 'species': 'MACMU', 'protein': set(['ENSMMUP00000001465']), 'external': {}}, 'Phy00029HZ_BOVIN': {'collateral': 4L, 'copy': 1, 'taxid': 9913L, 'trees': 0L, 'proteome': 'BOVIN.1', 'sps_name': 'Bos taurus', 'gene': set(['ENSBTAP00000002634']), 'species': 'BOVIN', 'protein': set(['ENSBTAP00000002634']), 'external': {'Ensembl.v59': ['ENSBTAG00000002033', 'ENSBTAP00000002634', 'ENSBTAT00000002634']}}, 'Phy0002BMQ_BOVIN': {'collateral': 4L, 'copy': 1, 'taxid': 9913L, 'trees': 0L, 'proteome': 'BOVIN.1', 'sps_name': 'Bos taurus', 'gene': set(['ENSBTAP00000012043']), 'species': 'BOVIN', 'protein': set(['ENSBTAP00000012043']), 'external': {}}, 'Phy0000F1K_ASHGO': {'collateral': 12L, 'copy': 1, 'taxid': 284811L, 'trees': 4L, 'proteome': 'ASHGO.1', 'sps_name': 'Ashbya gossypii ATCC 10895', 'gene': set([]), 'species': 'ASHGO', 'protein': set(['Q75D11']), 'external': {}}, 'Phy000467C_CANGA': {'collateral': 11L, 'copy': 1, 'taxid': 5478L, 'trees': 5L, 'proteome': 'CANGA.1', 'sps_name': 'Candida glabrata', 'gene': set([]), 'species': 'CANGA', 'protein': set(['Q6FXT3']), 'external': {'TrEMBL.2010.09': ['Q6FXT3']}}, 'Phy000A62H_MOUSE': {'collateral': 5L, 'copy': 1, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': set(['ENSMUSP00000028949']), 'species': 'MOUSE', 'protein': set(['ENSMUSP00000028949']), 'external': {'TrEMBL.2010.09': ['Q3UVN5']}}, 'Phy00000DT_ANOGA': {'collateral': 5L, 'copy': 1, 'taxid': 7165L, 'trees': 0L, 'proteome': 'ANOGA.1', 'sps_name': 'Anopheles gambiae', 'gene': set(['ENSANGP00000009984']), 'species': 'ANOGA', 'protein': set(['ENSANGP00000009984']), 'external': {}}, 'Phy000D22G_SCHPO': {'collateral': 10L, 'copy': 1, 'taxid': 4896L, 'trees': 0L, 'proteome': 'SCHPO.1', 'sps_name': 'Schizosaccharomyces pombe', 'gene': set([]), 'species': 'SCHPO', 'protein': set(['Q9UT81']), 'external': {'Swiss-Prot.2010.09': ['Q9UT81']}}, 'Phy0008BO3_HUMAN': {'collateral': 10L, 'copy': 1, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': set(['ENSP00000216879']), 'species': 'HUMAN', 'protein': set(['ENSP00000216879']), 'external': {'Ensembl.v59': ['ENSG00000088833', 'ENSP00000216879', 'ENST00000216879'], 'TrEMBL.2010.09': ['Q53FE8', 'Q53FF5'], 'Swiss-Prot.2010.09': ['Q9UNZ2']}}, 'Phy0007S7S_GIBZE': {'collateral': 9L, 'copy': 1, 'taxid': 5518L, 'trees': 0L, 'proteome': 'GIBZE.1', 'sps_name': 'Gibberella zeae', 'gene': set([]), 'species': 'GIBZE', 'protein': set(['Q4IA94']), 'external': {}}, 'Phy0002S9O_CAEBR': {'collateral': 5L, 'copy': 1, 'taxid': 6238L, 'trees': 0L, 'proteome': 'CAEBR.1', 'sps_name': 'Caenorhabditis briggsae', 'gene': set([]), 'species': 'CAEBR', 'protein': set(['Q61A62']), 'external': {}}, 'Phy00014K1_ARATH': {'collateral': 22L, 'copy': 1, 'taxid': 3702L, 'trees': 0L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': set([]), 'species': 'ARATH', 'protein': set(['O23394']), 'external': {}}, 'Phy000A35T_MOUSE': {'collateral': 5L, 'copy': 1, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': set(['ENSMUSP00000029907']), 'species': 'MOUSE', 'protein': set(['ENSMUSP00000029907']), 'external': {'Ensembl.v59': ['ENSMUSG00000028243', 'ENSMUSP00000029907', 'ENSMUST00000029907'], 'Swiss-Prot.2010.09': ['Q0KL01']}}, 'Phy00015YL_ARATH': {'collateral': 14L, 'copy': 1, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': set([]), 'species': 'ARATH', 'protein': set(['O81456']), 'external': {'TrEMBL.2010.09': ['O81456']}}, 'Phy000AJXF_MACMU': {'collateral': 4L, 'copy': 1, 'taxid': 9544L, 'trees': 0L, 'proteome': 'MACMU.1', 'sps_name': 'Macaca mulatta', 'gene': set(['ENSMMUP00000008545']), 'species': 'MACMU', 'protein': set(['ENSMMUP00000008545']), 'external': {}}, 'Phy000C5A9_PLAYO': {'collateral': 4L, 'copy': 1, 'taxid': 73239L, 'trees': 0L, 'proteome': 'PLAYO.1', 'sps_name': 'Plasmodium yoelii yoelii', 'gene': set([]), 'species': 'PLAYO', 'protein': set(['Q7RNC9']), 'external': {'TrEMBL.2010.09': ['Q7RNC9']}}, 'Phy0008A3X_HUMAN': {'collateral': 15L, 'copy': 1, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': set(['ENSP00000312107']), 'species': 'HUMAN', 'protein': set(['ENSP00000312107']), 'external': {'Ensembl.v59': ['ENSP00000312107', 'ENSP00000385525', 'ENST00000309033', 'ENST00000404924'], 'Swiss-Prot.2010.09': ['P68543']}}, 'Phy000AW9E_NEUCR': {'collateral': 11L, 'copy': 1, 'taxid': 5141L, 'trees': 0L, 'proteome': 'NEUCR.1', 'sps_name': 'Neurospora crassa', 'gene': set([]), 'species': 'NEUCR', 'protein': set(['(NCU01100.2)']), 'external': {'TrEMBL.2010.09': ['Q8X0G7']}}, 'Phy0005XAP_DROME': {'collateral': 14L, 'copy': 1, 'taxid': 7227L, 'trees': 4L, 'proteome': 'DROME.1', 'sps_name': 'Drosophila melanogaster', 'gene': set(['CG11139-PA']), 'species': 'DROME', 'protein': set(['CG11139-PA']), 'external': {'Ensembl.v59': ['FBgn0033179', 'FBpp0088069', 'FBtr0088997'], 'TrEMBL.2010.09': ['Q7K3Z3']}}, 'Phy0009GEH_MONDO': {'collateral': 4L, 'copy': 1, 'taxid': 13616L, 'trees': 0L, 'proteome': 'MONDO.1', 'sps_name': 'Monodelphis domestica', 'gene': set(['ENSMODP00000002593']), 'species': 'MONDO', 'protein': set(['ENSMODP00000002593']), 'external': {}}, 'Phy0006CSG_DANRE': {'collateral': 5L, 'copy': 1, 'taxid': 7955L, 'trees': 0L, 'proteome': 'DANRE.1', 'sps_name': 'Danio rerio', 'gene': set(['ENSDARP00000026327']), 'species': 'DANRE', 'protein': set(['ENSDARP00000026327']), 'external': {}}, 'Phy0009LMB_MOUSE': {'collateral': 5L, 'copy': 1, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': set(['ENSMUSP00000041730']), 'species': 'MOUSE', 'protein': set(['ENSMUSP00000041730']), 'external': {}}, 'Phy00022Q2_BOVIN': {'collateral': 5L, 'copy': 1, 'taxid': 9913L, 'trees': 0L, 'proteome': 'BOVIN.1', 'sps_name': 'Bos taurus', 'gene': set(['ENSBTAP00000008580']), 'species': 'BOVIN', 'protein': set(['ENSBTAP00000008580']), 'external': {'Swiss-Prot.2010.09': ['Q3SZC4']}}, 'Phy0009U78_MOUSE': {'collateral': 5L, 'copy': 1, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': set(['ENSMUSP00000058557']), 'species': 'MOUSE', 'protein': set(['ENSMUSP00000058557']), 'external': {}}, 'Phy000CGZG_RAT': {'collateral': 4L, 'copy': 1, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': set(['ENSRNOP00000034835']), 'species': 'RAT', 'protein': set(['ENSRNOP00000034835']), 'external': {}}, 'Phy0007CQ6_CHICK': {'collateral': 4L, 'copy': 1, 'taxid': 9031L, 'trees': 0L, 'proteome': 'CHICK.1', 'sps_name': 'Gallus gallus', 'gene': set(['ENSGALP00000024843']), 'species': 'CHICK', 'protein': set(['ENSGALP00000024843']), 'external': {'Ensembl.v59': ['ENSGALG00000015431', 'ENSGALP00000035955', 'ENSGALT00000036743']}}, 'Phy000CVNF_YEAST': {'collateral': 13L, 'copy': 1, 'taxid': 4932L, 'trees': 6L, 'proteome': 'YEAST.1', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set(['YBL058W']), 'species': 'YEAST', 'protein': set(['YBL058W']), 'external': {'Ensembl.v59': ['YBL058W'], 'TrEMBL.2010.09': ['Q6Q5U0'], 'Swiss-Prot.2010.09': ['P34223']}}, 'Phy0008N76_KLULA': {'collateral': 11L, 'copy': 1, 'taxid': 28985L, 'trees': 3L, 'proteome': 'KLULA.1', 'sps_name': 'Kluyveromyces lactis', 'gene': set([]), 'species': 'KLULA', 'protein': set(['Q6CMI1']), 'external': {'TrEMBL.2010.09': ['Q6CMI1']}}, 'Phy0003SSX_CANFA': {'collateral': 4L, 'copy': 1, 'taxid': 9615L, 'trees': 0L, 'proteome': 'CANFA.1', 'sps_name': 'Canis familiaris', 'gene': set(['ENSCAFP00000010519']), 'species': 'CANFA', 'protein': set(['ENSCAFP00000010519']), 'external': {'Ensembl.v59': ['ENSCAFG00000007088', 'ENSCAFP00000010519', 'ENSCAFT00000011356']}}, 'Phy000D9JL_TETNG': {'collateral': 5L, 'copy': 1, 'taxid': 99883L, 'trees': 0L, 'proteome': 'TETNG.1', 'sps_name': 'Tetraodon nigroviridis', 'gene': set(['GSTENP00003875001']), 'species': 'TETNG', 'protein': set(['GSTENP00003875001']), 'external': {'TrEMBL.2010.09': ['Q4TB74']}}, 'Phy0003QBK_CANFA': {'collateral': 4L, 'copy': 1, 'taxid': 9615L, 'trees': 0L, 'proteome': 'CANFA.1', 'sps_name': 'Canis familiaris', 'gene': set(['ENSCAFP00000010130']), 'species': 'CANFA', 'protein': set(['ENSCAFP00000010130']), 'external': {'Ensembl.v59': ['ENSCAFP00000010130', 'ENSCAFT00000010930']}}, 'Phy000BO0I_PANTR': {'collateral': 4L, 'copy': 1, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': set(['ENSPTRP00000022532']), 'species': 'PANTR', 'protein': set(['ENSPTRP00000022532']), 'external': {'Ensembl.v59': ['ENSPTRP00000052472', 'ENSPTRT00000059341']}}, 'Phy00017N5_ARATH': {'collateral': 13L, 'copy': 1, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': set([]), 'species': 'ARATH', 'protein': set(['Q7Y175']), 'external': {'Swiss-Prot.2010.09': ['Q7Y175']}}, 'Phy0007DAU_CHICK': {'collateral': 4L, 'copy': 1, 'taxid': 9031L, 'trees': 0L, 'proteome': 'CHICK.1', 'sps_name': 'Gallus gallus', 'gene': set(['ENSGALP00000009964']), 'species': 'CHICK', 'protein': set(['ENSGALP00000009964']), 'external': {}}, 'Phy000B3RA_PLAFA': {'collateral': 8L, 'copy': 1, 'taxid': 5833L, 'trees': 0L, 'proteome': 'PLAFA.1', 'sps_name': 'Plasmodium falciparum', 'gene': set([]), 'species': 'PLAFA', 'protein': set(['Q8IAS1']), 'external': {}}, 'Phy0005ZK6_DROME': {'collateral': 13L, 'copy': 1, 'taxid': 7227L, 'trees': 0L, 'proteome': 'DROME.1', 'sps_name': 'Drosophila melanogaster', 'gene': set(['CG4556-PA']), 'species': 'DROME', 'protein': set(['CG4556-PA']), 'external': {'Ensembl.v59': ['FBgn0259729', 'FBpp0289272', 'FBtr0299995'], 'TrEMBL.2010.09': ['Q8T4C3', 'Q9U9C9', 'Q9W175']}}, 'Phy000BD05_PANTR': {'collateral': 4L, 'copy': 1, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': set(['ENSPTRP00000020106']), 'species': 'PANTR', 'protein': set(['ENSPTRP00000020106']), 'external': {'Ensembl.v59': ['ENSPTRG00000011705', 'ENSPTRP00000020106', 'ENSPTRT00000021798']}}, 'Phy0005KKQ_DEBHA': {'collateral': 10L, 'copy': 1, 'taxid': 4959L, 'trees': 0L, 'proteome': 'DEBHA.1', 'sps_name': 'Debaryomyces hansenii', 'gene': set([]), 'species': 'DEBHA', 'protein': set(['Q6BYR9']), 'external': {}}, 'Phy00036IS_CAEEL': {'collateral': 12L, 'copy': 1, 'taxid': 6239L, 'trees': 0L, 'proteome': 'CAEEL.1', 'sps_name': 'Caenorhabditis elegans', 'gene': set(['Y94H6A.9a']), 'species': 'CAEEL', 'protein': set(['Y94H6A.9a']), 'external': {'Ensembl.v59': ['Y94H6A.9a'], 'TrEMBL.2010.09': ['Q9N2W5']}}, 'Phy0008J14_HUMAN': {'collateral': 9L, 'copy': 1, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': set(['ENSP00000319187']), 'species': 'HUMAN', 'protein': set(['ENSP00000319187']), 'external': {}}, 'Phy0002JCG_CANAL': {'collateral': 11L, 'copy': 1, 'taxid': 5476L, 'trees': 5L, 'proteome': 'CANAL.1', 'sps_name': 'Candida albicans', 'gene': set([]), 'species': 'CANAL', 'protein': set(['orf19.2549']), 'external': {}}, 'Phy0002JCJ_CANAL': {'collateral': 1L, 'copy': 1, 'taxid': 5476L, 'trees': 0L, 'proteome': 'CANAL.1', 'sps_name': 'Candida albicans', 'gene': set([]), 'species': 'CANAL', 'protein': set(['orf19.2550']), 'external': {'TrEMBL.2010.09': ['Q5A9B5']}}, 'Phy0004H5V_CIOIN': {'collateral': 6L, 'copy': 1, 'taxid': 7719L, 'trees': 0L, 'proteome': 'CIOIN.1', 'sps_name': 'Ciona intestinalis', 'gene': set(['ENSCINP00000002962']), 'species': 'CIOIN', 'protein': set(['ENSCINP00000002962']), 'external': {}}, 'Phy000CO1I_RAT': {'collateral': 4L, 'copy': 1, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': set(['ENSRNOP00000012551']), 'species': 'RAT', 'protein': set(['ENSRNOP00000012551']), 'external': {'Ensembl.v59': ['ENSRNOG00000009137', 'ENSRNOP00000012551', 'ENSRNOT00000012551'], 'Swiss-Prot.2010.09': ['P0C627']}}, 'Phy000BVFY_PANTR': {'collateral': 4L, 'copy': 1, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': set(['ENSPTRP00000034710']), 'species': 'PANTR', 'protein': set(['ENSPTRP00000034710']), 'external': {'Ensembl.v59': ['ENSPTRG00000033886', 'ENSPTRP00000055380', 'ENSPTRT00000063836']}}, 'Phy0007FZD_CHICK': {'collateral': 4L, 'copy': 1, 'taxid': 9031L, 'trees': 0L, 'proteome': 'CHICK.1', 'sps_name': 'Gallus gallus', 'gene': set(['ENSGALP00000026563']), 'species': 'CHICK', 'protein': set(['ENSGALP00000026563']), 'external': {'Ensembl.v59': ['ENSGALG00000016497', 'ENSGALP00000026563', 'ENSGALT00000026614'], 'TrEMBL.2010.09': ['Q5ZKL4']}}, 'Phy0006ZSN_TAKRU': {'collateral': 4L, 'copy': 1, 'taxid': 31033L, 'trees': 0L, 'proteome': 'TAKRU.1', 'sps_name': 'Takifugu rubripes', 'gene': set(['NEWSINFRUP00000128304']), 'species': 'TAKRU', 'protein': set(['NEWSINFRUP00000128304']), 'external': {}}, 'Phy0008ZAA_MONDO': {'collateral': 4L, 'copy': 1, 'taxid': 13616L, 'trees': 0L, 'proteome': 'MONDO.1', 'sps_name': 'Monodelphis domestica', 'gene': set(['ENSMODP00000011040']), 'species': 'MONDO', 'protein': set(['ENSMODP00000011040']), 'external': {'Ensembl.v59': ['ENSMODG00000008866', 'ENSMODP00000011040', 'ENSMODT00000011257']}}, 'Phy0001SFG_ARATH': {'collateral': 14L, 'copy': 1, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': set([]), 'species': 'ARATH', 'protein': set(['Q9SUG6']), 'external': {'TrEMBL.2010.09': ['Q9SUG6']}}, 'Phy0002JCH_CANAL': {'collateral': 4L, 'copy': 1, 'taxid': 5476L, 'trees': 0L, 'proteome': 'CANAL.1', 'sps_name': 'Candida albicans', 'gene': set([]), 'species': 'CANAL', 'protein': set(['orf19.10082']), 'external': {'TrEMBL.2010.09': ['C4YKZ7', 'Q5A9L6']}}, 'Phy000CPNE_RAT': {'collateral': 4L, 'copy': 1, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': set(['ENSRNOP00000006668']), 'species': 'RAT', 'protein': set(['ENSRNOP00000006668']), 'external': {'Ensembl.v59': ['ENSRNOG00000004950', 'ENSRNOP00000006668', 'ENSRNOT00000006668'], 'TrEMBL.2010.09': ['D3ZID8']}}, 'Phy0003L1L_CANFA': {'collateral': 4L, 'copy': 1, 'taxid': 9615L, 'trees': 0L, 'proteome': 'CANFA.1', 'sps_name': 'Canis familiaris', 'gene': set(['ENSCAFP00000005869']), 'species': 'CANFA', 'protein': set(['ENSCAFP00000005869']), 'external': {}}, 'Phy000CLXL_RAT': {'collateral': 4L, 'copy': 1, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': set(['ENSRNOP00000011654']), 'species': 'RAT', 'protein': set(['ENSRNOP00000011654']), 'external': {'TrEMBL.2010.09': ['D3ZEG3']}}, 'Phy0005KKR_DEBHA': {'collateral': 7L, 'copy': 1, 'taxid': 4959L, 'trees': 0L, 'proteome': 'DEBHA.1', 'sps_name': 'Debaryomyces hansenii', 'gene': set([]), 'species': 'DEBHA', 'protein': set(['Q6BYS0']), 'external': {}}, 'Phy0000P6F_APIME': {'collateral': 6L, 'copy': 1, 'taxid': 7460L, 'trees': 1L, 'proteome': 'APIME.1', 'sps_name': 'Apis mellifera', 'gene': set(['ENSAPMP00000010305']), 'species': 'APIME', 'protein': set(['ENSAPMP00000010305']), 'external': {}}, 'Phy00098SP_MONDO': {'collateral': 4L, 'copy': 1, 'taxid': 13616L, 'trees': 0L, 'proteome': 'MONDO.1', 'sps_name': 'Monodelphis domestica', 'gene': set(['ENSMODP00000024398']), 'species': 'MONDO', 'protein': set(['ENSMODP00000024398']), 'external': {'Ensembl.v59': ['ENSMODG00000019559', 'ENSMODP00000024398', 'ENSMODT00000024831']}}, 'Phy00057S0_DICDI': {'collateral': 5L, 'copy': 1, 'taxid': 44689L, 'trees': 0L, 'proteome': 'DICDI.1', 'sps_name': 'Dictyostelium discoideum', 'gene': set([]), 'species': 'DICDI', 'protein': set(['Q54BQ5']), 'external': {'Swiss-Prot.2010.09': ['Q54BQ5']}}, 'Phy0001H3K_ARATH': {'collateral': 6L, 'copy': 1, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': set([]), 'species': 'ARATH', 'protein': set(['Q9LVE1']), 'external': {'TrEMBL.2010.09': ['Q9LVE1']}}, 'Phy000AACP_MACMU': {'collateral': 4L, 'copy': 1, 'taxid': 9544L, 'trees': 0L, 'proteome': 'MACMU.1', 'sps_name': 'Macaca mulatta', 'gene': set(['ENSMMUP00000021035']), 'species': 'MACMU', 'protein': set(['ENSMMUP00000021035']), 'external': {}}, 'Phy0008TSZ_LEIMA': {'collateral': 1L, 'copy': 1, 'taxid': 5664L, 'trees': 0L, 'proteome': 'LEIMA.1', 'sps_name': 'Leishmania major', 'gene': set([]), 'species': 'LEIMA', 'protein': set(['Q4QBW3']), 'external': {'TrEMBL.2010.09': ['Q4QBW3']}}, 'Phy0004PJ7_CRYNE': {'collateral': 9L, 'copy': 1, 'taxid': 5207L, 'trees': 0L, 'proteome': 'CRYNE.1', 'sps_name': 'Cryptococcus neoformans', 'gene': set([]), 'species': 'CRYNE', 'protein': set(['Q55RA0']), 'external': {'TrEMBL.2010.09': ['Q5KEX0']}}, 'Phy000BUTW_PANTR': {'collateral': 4L, 'copy': 1, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': set(['ENSPTRP00000034120']), 'species': 'PANTR', 'protein': set(['ENSPTRP00000034120']), 'external': {}}, 'Phy000A0DO_MOUSE': {'collateral': 5L, 'copy': 1, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': set(['ENSMUSP00000020962']), 'species': 'MOUSE', 'protein': set(['ENSMUSP00000020962']), 'external': {'Ensembl.v59': ['ENSMUSG00000020634', 'ENSMUSP00000020962', 'ENSMUSP00000118834', 'ENSMUST00000020962', 'ENSMUST00000142867'], 'TrEMBL.2010.09': ['B8JK44'], 'Swiss-Prot.2010.09': ['Q99KJ0']}}, 'Phy000EWDU_YARLI': {'collateral': 12L, 'copy': 1, 'taxid': 4952L, 'trees': 0L, 'proteome': 'YARLI.1', 'sps_name': 'Yarrowia lipolytica', 'gene': set([]), 'species': 'YARLI', 'protein': set(['Q6C5V3']), 'external': {'TrEMBL.2010.09': ['Q6C5V3']}}, 'Phy0006QQY_TAKRU': {'collateral': 4L, 'copy': 1, 'taxid': 31033L, 'trees': 0L, 'proteome': 'TAKRU.1', 'sps_name': 'Takifugu rubripes', 'gene': set(['NEWSINFRUP00000161354']), 'species': 'TAKRU', 'protein': set(['NEWSINFRUP00000161354']), 'external': {}}, 'Phy0008JFW_HUMAN': {'collateral': 17L, 'copy': 1, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': set(['ENSP00000327891']), 'species': 'HUMAN', 'protein': set(['ENSP00000327891']), 'external': {'Ensembl.v59': ['ENSG00000215114', 'ENSP00000382507', 'ENST00000399598'], 'Swiss-Prot.2010.09': ['Q14CS0']}}, 'Phy000692N_DANRE': {'collateral': 5L, 'copy': 1, 'taxid': 7955L, 'trees': 0L, 'proteome': 'DANRE.1', 'sps_name': 'Danio rerio', 'gene': set(['ENSDARP00000060308']), 'species': 'DANRE', 'protein': set(['ENSDARP00000060308']), 'external': {}}}}

complete_tree_2 = {'tree': {'lk': -231.99600000000001, 'method': 'JTT', 'best': True, 'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108342,(Phy000CVLS_YEAST:0.212821,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025083,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.950000:0.104729)0.620000:0.117294)0.693659:0.022298)0.125038:0.000000);'}, 'seq': {'Phy000CWXJ_YEAST': {'collateral': 36L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YIR040C']), 'external': {'Ensembl.v59': ['YIR040C'], 'Swiss-Prot.2010.09': ['P40584']}}, 'Phy000CXBC_YEAST': {'collateral': 36L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YGL260W']), 'external': {'Ensembl.v59': ['YGL260W'], 'Swiss-Prot.2010.09': ['P53056']}}, 'Phy000CVIE_YEAST': {'collateral': 23L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YAL067W-A']), 'external': {'Ensembl.v59': ['YAL067W-A'], 'Swiss-Prot.2010.09': ['Q8TGK6']}}, 'Phy000CVLS_YEAST': {'collateral': 37L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YBL108W']), 'external': {'Ensembl.v59': ['YBL108W'], 'Swiss-Prot.2010.09': ['P38161']}}, 'Phy000CYBL_YEAST': {'collateral': 36L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YKL223W']), 'external': {'Ensembl.v59': ['YKL223W'], 'Swiss-Prot.2010.09': ['P36031']}}, 'Phy000CY0I_YEAST': {'collateral': 24L, 'copy': 2, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YJL222W-A', 'YIL174W']), 'external': {'Ensembl.v59': ['YJL222W-A'], 'Swiss-Prot.2010.09': ['P40437']}}, 'Phy000CZQW_YEAST': {'collateral': 7L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YNR075C-A']), 'external': {'Ensembl.v59': ['YNR075C-A'], 'Swiss-Prot.2010.09': ['Q8TGJ2']}}}}

complete_tree_3 = {'tree': {'lk': -234.922, 'method': 'WAG', 'best': False, 'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108966,(Phy000CVLS_YEAST:0.209734,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025782,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.964000:0.107553)0.648000:0.118969)0.756000:0.023454)0.125038:0.000000);'}, 'seq': {'Phy000CWXJ_YEAST': {'collateral': 36L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YIR040C']), 'external': {'Ensembl.v59': ['YIR040C'], 'Swiss-Prot.2010.09': ['P40584']}}, 'Phy000CXBC_YEAST': {'collateral': 36L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YGL260W']), 'external': {'Ensembl.v59': ['YGL260W'], 'Swiss-Prot.2010.09': ['P53056']}}, 'Phy000CVIE_YEAST': {'collateral': 23L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YAL067W-A']), 'external': {'Ensembl.v59': ['YAL067W-A'], 'Swiss-Prot.2010.09': ['Q8TGK6']}}, 'Phy000CVLS_YEAST': {'collateral': 37L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YBL108W']), 'external': {'Ensembl.v59': ['YBL108W'], 'Swiss-Prot.2010.09': ['P38161']}}, 'Phy000CYBL_YEAST': {'collateral': 36L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YKL223W']), 'external': {'Ensembl.v59': ['YKL223W'], 'Swiss-Prot.2010.09': ['P36031']}}, 'Phy000CY0I_YEAST': {'collateral': 24L, 'copy': 2, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YJL222W-A', 'YIL174W']), 'external': {'Ensembl.v59': ['YJL222W-A'], 'Swiss-Prot.2010.09': ['P40437']}}, 'Phy000CZQW_YEAST': {'collateral': 7L, 'copy': 1, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': set([]), 'species': 'YEAST', 'protein': set(['YNR075C-A']), 'external': {'Ensembl.v59': ['YNR075C-A'], 'Swiss-Prot.2010.09': ['Q8TGJ2']}}}}

msf_1 = {'Phy000ASI0_MACMU': {'gene': set(['ENSMMUG00000001100']), 'seq': 'MAEGGGPDPSEKERRSSGPRPPSARDLQLALAELYEDEVKCKSSKSNRPKAAVFKSPRTPPQRFYSSEHEYSGLNIVRPSTGKIVNELFREAREHGAVPLNEATRASGDDKSKSFTGGGYRLGNSFCKRSEYIYGENQLQDVQILLKLWSNGFSLDDGELRPYNEPTNAQFLESVKRGEIPLELQRLVHGGQVNLDMEDHQDQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSILNAVVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRNFIVQSRPEFAALDFILVTSFPNKELTDESLTLLEADILNTVLLQQLK', 'comments': set(['genescaffold_MMUL_0_1_GeneScaffold_4999_43610_75983_1 gene_ENSMMUG00000001100 transcript_ENSMMUT00000001558 Oldphy_#Mmu0027363#']), 'external': {}, 'seq_leng': 331, 'protein': set(['ENSMMUP00000001465']), 'copy': 1L}, 'Phy00029HZ_BOVIN': {'gene': set(['ENSBTAG00000002033']), 'seq': 'MKEVDNLESIKEEWVCETGSDHQPLSDSQQKNCEYFVDSLFEEAQKVGAKCLSPTEQKKQVDVSIKLWKNGFTVNDDFRSYSDGASQQFLNSIKKGELPLELQGVFDKEEVDVKVEDKKNEVCMSTKPVFQPFSGQGHRLGSATPKIVSKAKNIEVENKNKLSAVPLNNLEPITNIQIWLANGKRIVQKFNISHRISHIKDFIEKYQGSQRSPPFSLATALPFLKLLDETLTLEEADLQNAVIIQRLKKTAEPFKELS', 'comments': set(['chromosome_Btau_2.0_11_56385357_56404666_-1 gene_ENSBTAG00000002033 transcript_ENSBTAT00000002634 Oldphy_#Bta0022038#']), 'external': {'Ensembl.v59': ['ENSBTAG00000002033', 'ENSBTAP00000002634', 'ENSBTAT00000002634']}, 'seq_leng': 258, 'protein': set(['ENSBTAP00000002634']), 'copy': 1L}, 'Phy0002BMQ_BOVIN': {'gene': set(['ENSBTAG00000009138']), 'seq': 'LALAELYEDEVKCKASKSDRPKATAFKSPQTAPQRFYSSEHECSGLHIVQPSTGKIVNELFREARQHGAVPLNEATRASGDDKSKSFTGGGYRLGNSFCKQSEYIYGENQLQDVQILLKLWSNGFSLDDGELRPYSDPTNAQFLESVKRGEIPLELQRLVHGGHLNLDMEDHQDQEYVKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEEKSLFNAVVLIDDSMPTTKIQIRLADGSRLIQRFNSTHRILDVRDFIVQSRPEFATLDFILVTSFPNKVLTDESLTLQEADILNTVILQQLK', 'comments': set(['scaffold_Btau_2.0_ChrUn.9906_287_18463_1 gene_ENSBTAG00000009138 transcript_ENSBTAT00000012043 Oldphy_#Bta0024801#']), 'external': {}, 'seq_leng': 303, 'protein': set(['ENSBTAP00000012043']), 'copy': 1L}, 'Phy0000F1K_ASHGO': {'gene': set([]), 'seq': 'MSDEQIQQFMMLTNSSAEVARKYLGEHEDDLEDALNGFYANQQRPGSVEGQRNSYSDPNSSQEPRSSSPQLPSQASAKSGGSSGRSKKEKPWFRTFSQIMKESQEEDDDDEARHTFAGGETSGLEVTDPNDSNSLIRDLLEKARKGGERGDNGQGRSVAAHNFFKGRGYRLGSSAEAEPEVVTQPEEPERPRKVTREITFWKEGFQVGEDGPLYRYDDPANSYYLNELNQGRAPLRLLNVEFGQEVDVNVYKKLDESYKPPKKKHGGFGGSGRRLGSPIPGDIARAEEAVEQESSATSPAPEAKQESPKPAEQQGNTSVQIRYANGKREVLRCNSFDKVGFLYDHVKQNTSEARPFTLNQVCPVQPLEDFECTIGEQNLCNSVVVQRWV', 'comments': set(['ABR211Cp Oldphy_#Ago0003873#']), 'external': {}, 'seq_leng': 389, 'protein': set(['Q75D11']), 'copy': 1L}, 'Phy000467C_CANGA': {'gene': set([]), 'seq': 'MSDSDKVIQQFMTLTDRSIDVAREYLEQYDNDLGGALNAYYASQMESEEEQRENDERWGPTRESPRPSSAEGTSSRALSQSSEPVKYDSKKNSKFMSFSQMVKSNGGSGDDDDDDDKRNTFAGGEVSGLEVTDPNDSNNIIKDLLEKAKRGGESLSQEESENKRSAQHFIGKGYRLGSSVGETNQVVEDNTESGRRTPERVTRDITFWKEGFQVGEGELYRYDDPANSFYLNELNQGRAPLKLLNVEFGQEVDVNVHKKLDESYKPPKRKIEGFHGRGQRLGSPVPGDAPEPAVATATQAVPKTETKAEKTEEVPKGDSSIQIRYASGKREIFRCNATDSVRSLYEYVSSNTTDKSRQFTLNHAFPVKPIENSDISVEEAGLVNAVVVQRWK', 'comments': set(['Similar to sp|P34223 Saccharomyces cerevisiae YBL058w SHP1 Oldphy_#Cgl0004426#']), 'external': {'TrEMBL.2010.09': ['Q6FXT3']}, 'seq_leng': 392, 'protein': set(['Q6FXT3']), 'copy': 1L}, 'Phy000A62H_MOUSE': {'gene': set(['ENSMUSG00000027455']), 'seq': 'MAEERQDALREFVAVTGTEEDRARFFLESAGWDLQIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEEEEEEEGQRTWFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGERRRHSGQDVHVVLKLWKTGFSLDNGDLRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLNTSSPAQQAENEAKASSSILINEAEPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFVLMTTFPNKELADENQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_NCBIM34_2_150951232_150968236_1 gene_ENSMUSG00000027455 transcript_ENSMUST00000028949 Oldphy_#Mms0032479#']), 'external': {'TrEMBL.2010.09': ['Q3UVN5']}, 'seq_leng': 372, 'protein': set(['ENSMUSP00000028949']), 'copy': 1L}, 'Phy00000DT_ANOGA': {'gene': set(['ENSANGG00000007495']), 'seq': 'IATLHTLHSSSSEDEEEQGQAFYAGGSERSGQQVLGPPRKNPIKDYVSEIFRSAQQGNLETFDPSEESGGSSWSLYAGTGYRLGQTEDDHQEVTPRGARTAASSSSQNLEVVTLTLWRQGFVINDGELRLYEDPANREFFESITRGEIPEELRSKGQTMFRVDLKDNRHEEYVKRSKPFKAFGGSGQTLGSPVPPMANEENEKRAAEELALDSAQPTTMLQIRLIDGSRLSARFNQAHTVEHVRRYIVNARPQYGAQNFALMTTFPSKELSDGAQTLKDAGLLNAAILQRLN', 'comments': set(['chromosome_MOZ2a_2L_9684401_9685339_-1 gene_ENSANGG00000007495 transcript_ENSANGT00000009984 Oldphy_#Aga0000497#']), 'external': {}, 'seq_leng': 292, 'protein': set(['ENSANGP00000009984']), 'copy': 1L}, 'Phy000D22G_SCHPO': {'gene': set([]), 'seq': 'MDREDILKEFCNRNNIDVSQGRFFLESTNWNYELATALLHEVIPPEEDHGLQPSSDVSKVPEVTGSSSGISGGDQQPPRPLQRQQNTQGQGMKSGTASKKFATLRDLEGNDESAEEKSHLFTGGEKSGLSVEDGDPDPKKQLVRDILEKARQHTISPLDEQDSGPSSLASSWASVGQRLGTENEASGSTTPVTQSGPPRENPPTESQPEKPLRRTLYFWRNGFSVDDGPIYTYDDPANQEMLRYINSGRAPLHLLGVSMNQPIDVVVQHRMDEDYVAPFKPFSGKGQRLGSTYMQPRMSQMPGGLYTDTSTSSSVPINVKPNSTTPHASLQIDENKPTTRIQVRLSNGGRTVLTVNLSHTLHDIYEAVRAVSPGNFILSVPFPAKTLEDDPSVTVEAASLKNASLVQKSL', 'comments': set(['UBX domain protein 3 Oldphy_#Spb0001902#']), 'external': {'Swiss-Prot.2010.09': ['Q9UT81']}, 'seq_leng': 410, 'protein': set(['Q9UT81']), 'copy': 1L}, 'Phy0008BO3_HUMAN': {'gene': set(['ENSG00000088833']), 'seq': 'MAAERQEALREFVAVTGAEEDRARFFLESAGWDLQIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEDEEEEEGQRFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGEKRQHSSQDVHVVLKLWKSGFSLDNGELRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLSTSSPAQQAENEAKASSSILIDESEPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFILMTTFPNKELADESQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_NCBI35_20_1370811_1396417_-1 gene_ENSG00000088833 transcript_ENST00000216879 CCDS13015.1 Oldphy_#Hsa0018651#']), 'external': {'Ensembl.v59': ['ENSG00000088833', 'ENSP00000216879', 'ENST00000216879'], 'TrEMBL.2010.09': ['Q53FE8', 'Q53FF5'], 'Swiss-Prot.2010.09': ['Q9UNZ2']}, 'seq_leng': 370, 'protein': set(['ENSP00000216879']), 'copy': 1L}, 'Phy0007S7S_GIBZE': {'gene': set([]), 'seq': 'MADQEGQIVEFAGLSGASPEEARQYLEAHNWNLAEASNAWFRDAEDDGRDTSTAPAPVPDNYTGPRTLDGRPAPEAARSSSQATRKSAPSQQRKTGIATLGSIGSSSHQHDHGDDDDDDSDPEDDDGRGNLFAGGEKSGLAVQDPNQQEAGPKKIISDILAKARANAARPEAENEAGPSEPSRFRGTGQTLGGDGVESRSIPDPLGPVRASNAESQERVLHIWQDGFSIDDGDLRRFDDPANQADLALIRSGRAPLHLMNVQHDQPIDVKLHQHDTPYQPQPKQYRPFGGSGQRLGAVVPGASEGSSSTTAAPAAASSSSNAPSVDDSQPTVMIRIQMPDGTRLPARFNTNHTVGDIYGFVQGASAETRSRSWVLSTTFPNKDHTNHSLVLGEMSEFKKGGTAVVKWT', 'comments': set(['Hypothetical protein Oldphy_#Gze0005078#']), 'external': {}, 'seq_leng': 408, 'protein': set(['Q4IA94']), 'copy': 1L}, 'Phy0002S9O_CAEBR': {'gene': set([]), 'seq': 'FSCSIRTFRDIGGDNDGPDSDDSGADAERGEPQEFYAGSGQAVQGPRGPRNNEDHIRRILQAAQVENPEELAAAVGGGRGGRDNKDKVTLTLHLWTDGLSIEDGPLMARNDPATIEFLEIVGRGGIPPSLHQQYQGKDIDFNIDRRHEAYQPPKMKPFGGSGVRLGNVVPTVIGVDVSTASSSAAGAATMPSGPTSAEEEAKQLEDAKKELKTDMGQPTTNIQIRLPSGQRIVAVFNHTHTLEAVRCFICTARPDIIYSPFELMSAYPPKVLIDETQTLKEANLLNSVIAVKISP', 'comments': set(['Hypothetical protein CBG13914 _Fragment_ Oldphy_#Cbr0005435#']), 'external': {}, 'seq_leng': 295, 'protein': set(['Q61A62']), 'copy': 1L}, 'Phy00014K1_ARATH': {'gene': set([]), 'seq': 'MATETNENLINSFIEITSSSREEANFFLESHTWNLDAAVSTFLDNDAAAAAEPNPTGPPPPSSTIAGAQSPSQSHSPDYTPSETSPSPSRSRSASPSSRAAPYGLRSRGGAGENKETENPSGIRSSRSRQHAGNIRTFADLNRSPADGEGSDSDEANEYYTGGQKSGMMVQDPKKVKDVDELFDQARQSAVDRPVEPSRSASTSFTGAARLLSGEAVSSSPQQQQQEQPQRIMHTITFWLNGFTVNDGPLRGFSDPENAAFMNSISRSECPSELEPADKKIPVHVDLVRRGENFTEPPKPKNPFQGVGRTLGASGSGSSSAPQASSAPMNVAPAPSRGLVVDPAAPTTSIQLRLADGTRLVSRFNNHHTVRDVRGFIDASRPGGSKEYQLLTMGFPPKQLTELDQTIEQAGFITKILPFLLEARHFLRVSLDFIHLQCPDLSLYSSAICKLLFFLLSPKVSVIMIKQIFGKLPRKPSKSSHNDSNPNGEGGPSSKSSASNSNGANGTVIAPSSTSSNRTNQVNGVYEALPSFRDVPTSEKPNLFIKKLSMCCVVFDFNDPSKNLREKEIKRQTLLELVDYIATVSTKLSDAAMQEIAKVAVVNLFRTFPSANHESKILETLDVDDEEPALEPAWPHLQVVYELLLRFVASPMTDAKLAKRYIDHSFVLKLLDLFDSEDQREREYLKTILHRIYGKFMVHRPFIRKAINNIFYRFIFETEKHNGIAELLEILGSIINGFALPLKEEHKLFLIRALIPLHRPKCASAYHQQLSYCIVQFVEKDFKLADTVIRGLLKYWPVTNSSKEVMFLGELEEVLEATQAAEFQRCMVPLFRQIARCLNSSHFQVAERALFLWNNDHIRNLITQNHKVIMPIVFPAMERNTRGHWNQAVQSLTLNVRKVMAETDQILFDECLAKFQEDEANETEVVAKREATWKLLEELAASKSVSNEAVLVPRFSSSVTLATGKTSGS', 'comments': set(['Phosphatase like protein Oldphy_#Ath0004528#']), 'external': {}, 'seq_leng': 969, 'protein': set(['O23394']), 'copy': 1L}, 'Phy000A35T_MOUSE': {'gene': set(['ENSMUSG00000028243']), 'seq': 'MAEGGRAEPEEQERGSSRPRPPSARDLQLALAELYEDEMKCKSSKPDRSTPATCRSPRTPPHRLYSGDHKYDGLHIVQPPTGKIVNELFKEAREHGAVPLNEATRSSREDKTKSFTGGGYRLGNSFYKRSEYIYGENQLQDVQVLLKLWRNGFSLDDGELRPYSDPTNAQFLESVKRGETPLELQRLVHGAQVNLDMEDHQDQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSILNAAVLIDDSMPTTKIQIRLADGSRLVQRFNSTHRILDVRDFIVRSRPEFATTDFILVTSFPSKELTDETVTLQEADILNTVILQQLK', 'comments': set(['chromosome_NCBIM34_4_6118252_6146610_1 gene_ENSMUSG00000028243 transcript_ENSMUST00000029907 Oldphy_#Mms0028711#']), 'external': {'Ensembl.v59': ['ENSMUSG00000028243', 'ENSMUSP00000029907', 'ENSMUST00000029907'], 'Swiss-Prot.2010.09': ['Q0KL01']}, 'seq_leng': 331, 'protein': set(['ENSMUSP00000029907']), 'copy': 1L}, 'Phy00015YL_ARATH': {'gene': set([]), 'seq': 'MSSKDKKPSKPSSSRGGIRTLSDLNRRSGPDSDSDSDGPQEYYTGGEKSGMLVQDPSKKDDVDEIFNQARQLGAVEGPLEPPPSSRSFTGTGRLLSGENVPTGNQQPEPVVHNIVFWSNGFTIDDGPLRKLDDPENASFLEVNDFHSIRKSECPKELEPADRRAPVHVNLMRKEEKCPERQKRRVSFQGVGRTLGGSNEGSGSSSPVAPDSAPIPIQTEPAPSQSLVIDETVPTTSIQLRLADGTRLVAKFNHHHTVNDIRGFIDSSRPGASLNYQLQTMGFPPKPLTDLTQTIEEAGLANSVVLQKF', 'comments': set(['T27D20.10 protein _Putative membrane trafficking factor_ Oldphy_#Ath0006348#']), 'external': {'TrEMBL.2010.09': ['O81456']}, 'seq_leng': 308, 'protein': set(['O81456']), 'copy': 1L}, 'Phy000AJXF_MACMU': {'gene': set(['ENSMMUG00000006487']), 'seq': 'MKDVDNLKSVKQEXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXVDVNIKLWKNGFTVNDDFRSYSDGASQQFLNSIKKGELPSELQGIFDKEEVDVKVEDKKNEICLSTKPVFQPFSGQGHRLGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXVSHIKDFIEKYQGSQRSPPFSLATALPVLRLLDETLTLEEADLQNAVIIQRLQKTAAPFRELSEH', 'comments': set(['genescaffold_MMUL_0_1_GeneScaffold_5091_5892_33121_1 gene_ENSMMUG00000006487 transcript_ENSMMUT00000009096 Oldphy_#Mmu0016254#']), 'external': {}, 'seq_leng': 260, 'protein': set(['ENSMMUP00000008545']), 'copy': 1L}, 'Phy000C5A9_PLAYO': {'gene': set([]), 'seq': 'QKSGLEVENSDSDDMAQSYYTSKLPENCRRITLYKNGFTIDEGEFRDFEVEENKKFMENIEAGILPKELQGKDKSIMNVAIKDKSSQIYTKNKSQEEKTLYKGQGVKLGSSNSNLNEEEINKIIASNPTDIKEIKIDDNNPITTIQIRLYNGKKIIQKFNYNHTVEDLFQFVYGHTPINFSLFFDFPLKKIERNNKTLQEENLLGLIIFFFFLPNLILFGIYICIILCVQV', 'comments': set(['UBX domain, putative _Fragment_ Oldphy_#Pyo0005951#']), 'external': {'TrEMBL.2010.09': ['Q7RNC9']}, 'seq_leng': 231, 'protein': set(['Q7RNC9']), 'copy': 1L}, 'Phy0008A3X_HUMAN': {'gene': set(['ENSG00000173960']), 'seq': 'MKDVDNLKSIKEEWVCETGSDNQPLGNNQQSNCEYFVDSLFEEAQKVSSKCVSPAEQKKQVDVNIKLWKNGFTVNDDFRSYSDGASQQFLNSIKKGELPSELQGIFDKEEVDVKVEDKKNEICLSTKPVFQPFSGQGHRLGSATPKIVSKAKNIEVENKNNLSAVPLNNLEPITNIQIWLANGKRIVQKFNITHRVSHIKDFIEKYQGSQRSPPFSLATALPVLRLLDETLTLEEADLQNAVIIQRLQKTASFRELSEH', 'comments': set(['chromosome_NCBI35_2_24075027_24135342_1 gene_ENSG00000173960 transcript_ENST00000309033 CCDS1704.1 Oldphy_#Hsa0016629#']), 'external': {'Ensembl.v59': ['ENSP00000312107', 'ENSP00000385525', 'ENST00000309033', 'ENST00000404924'], 'Swiss-Prot.2010.09': ['P68543']}, 'seq_leng': 259, 'protein': set(['ENSP00000312107']), 'copy': 1L}, 'Phy000AW9E_NEUCR': {'gene': set([]), 'seq': 'MTDHDDKISSFCELTGVATDAATEYLNNYDWDMDAAVAAYYTDQDNSASNTGAAPASARASAAAPPEYIGPRTLDGRPAPQYAQSSSSAPKKTQKRTGLATLSSIGGRRDEDDDEDEDDEEDEGRGPRDLFAGGEKSGLAVQDPSQREPNSDTRRLLQDILAKARENSRAGGNSSDDEETGAETGAGTARPTRFRGTGMTLGGDGVESRQIPNVDSNTSAAPRQLEGPTQERTLHIWSNGFSVEEGPLYRFDDPANQADLAMIRAGRAPLRLMNVRPDQRVNVKLEQHQEEWRQLPKKYVPFSGEGRRLGSPVPGDGSGFVPPAAAAAASTAVASASATSGSAQAPTTGVDESQPTVMLRIQLPDGSRLPARFNTSQTIGDVYDFVQRSSTSLSARPWVLSTTFPNKDHTDKSLVLGDTPEFKRGAAAVVKWV', 'comments': set(['hypothetical protein Oldphy_#Ncr0001064#']), 'external': {'TrEMBL.2010.09': ['Q8X0G7']}, 'seq_leng': 433, 'protein': set(['(NCU01100.2)']), 'copy': 1L}, 'Phy0005XAP_DROME': {'gene': set(['CG11139']), 'seq': 'MAARGDLIAQFIEITGTDENVARFYLSSCDWDIEHALGNYWSTQADLPVPVPTVGHADNPKPKPTSSSGASASASAAGATKSADSAVATSSASVDIAPAATKAKPKFATLSDMSKESSSDDDQQAFYAGGSDRSGQQVLGPPKRKNFREQLTDMMRSAQEQNIAEVGPSTSSGSASGGSGGAVWGQGMRLGMTDNDHTAVGTKKPAATIENKPVVVLKLWSQGFSIDGGELRHYDDPQNKEFLETVMRGEIPQELLEMGRMVNVDVEDHRHEDFKRQPVPQTFKGSGQKLGSPVANLVTEAPTVPVALSPGEAANQEASARDAINLNSEAPSTTLQIRLADGSRLAAQFNLSHTVSDIRRFIQTARPQYSTSNFILVSSFPTRELSDDNSTIEKAGLKNAALMQRLK', 'comments': set(['chromosome_BDGP4_2R_2976828_2978544_-1 gene_CG11139 transcript_CG11139-RA Oldphy_#Dme0013780#']), 'external': {'Ensembl.v59': ['FBgn0033179', 'FBpp0088069', 'FBtr0088997'], 'TrEMBL.2010.09': ['Q7K3Z3']}, 'seq_leng': 407, 'protein': set(['CG11139-PA']), 'copy': 1L}, 'Phy0009GEH_MONDO': {'gene': set(['ENSMODG00000002133']), 'seq': 'MKEVEKLESLREDWLCESGAEGQSHRGSQAGSCELFFDSLLEEAQRGGSEHLPSAAAVTQADVSIKLWQNGFTVNGEFRSYGDGASQQFLNAIRKGELPSELRGRFSQEEVAVRVEDKKEQVFVPRKPAFAPFSGRGHRLGSATPRIVSKASGGEAGPPKPLAAPAVPLNPWEPVTSIQIWLADGRRLVQRFNVSHRVSHVRDFIRSCEGSPRSAPFSLVTALPGLRPLDDALTLEEAGLRNAVVIQR', 'comments': set(['scaffold_BROADO2_scaffold_281_1727_4937_1 gene_ENSMODG00000002133 transcript_ENSMODT00000002647 Oldphy_#Mdo0026119#']), 'external': {}, 'seq_leng': 248, 'protein': set(['ENSMODP00000002593']), 'copy': 1L}, 'Phy0006CSG_DANRE': {'gene': set(['ENSDARG00000006375']), 'seq': 'MAEREEAVRGFVAVTDVDEERARFFLESAGWDLQLALANFFEDGGEDDIATLPQPESGSVTRPTGPSEHRVTSFRDLMHEDDDDSGDEEGQRFFAGGSERSGQQIVGPPKKKNSNELIEDLFKGAKEHGAVPVDKAGKGLGESSKSKPFGGGGYRLGAAPEEESTYVAGARRQPGSSQDQVHVVLKLWKTGFSLDEGELRTYSDPENALFLESIRRGEIPLELRQRFRGGQVNLDMEDHRDEDFSKPRLAFKAFTGEGQKLGSATPELVSLQRPQDQAASEAEASASISVDTSQPITSIQIRLADGGRLVQKFNHTHRVSDVRQFVASARPALAATEFVLMTTFPNKELTDESLTLKEANLLNAVIVQRLK', 'comments': set(['chromosome_ZFISH5_19_12266333_12276172_1 gene_ENSDARG00000006375 transcript_ENSDART00000019111 Oldphy_#Dre0016991#']), 'external': {}, 'seq_leng': 371, 'protein': set(['ENSDARP00000026327']), 'copy': 1L}, 'Phy0009LMB_MOUSE': {'gene': set(['ENSMUSG00000039833']), 'seq': 'IKIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLFHDQDEEEEEEEGQRFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAALEEESAYVAGERRWHSGQDVHVVLKLWKTGFSLDNGDLRSYQDPSNAPFLESIRRGEVPAELQRLAHGGQVNLDMEDHRDEDFMKPKGAFKAFTGKGQKLSSMAPQVLNTSSPAQQAENEAKASSSILINEAEPTTDIQIRLADGERLVQKFNHSHRISDIRLFIVDARPAMAATSFVLMTTFPNKELADENQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_NCBIM34_5_48316229_48317242_1 gene_ENSMUSG00000039833 transcript_ENSMUST00000049098 Oldphy_#Mms0005977#']), 'external': {}, 'seq_leng': 337, 'protein': set(['ENSMUSP00000041730']), 'copy': 1L}, 'Phy00022Q2_BOVIN': {'gene': set(['ENSBTAG00000006533']), 'seq': 'MAAERQDALREFVAVTGAEEDRARFFLESAGWDLQIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEDEEEEEGQRFYAGGSERSGQQIVGPPRKRSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGERRRHSGQDVHVVLKLWKTGFSLDNGELRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQILNTSSPAQQAENEAKASSSISIDESQPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFVLMTTFPNKELADENQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_Btau_2.0_13_41209692_41229859_1 gene_ENSBTAG00000006533 transcript_ENSBTAT00000008580 Oldphy_#Bta0013257#']), 'external': {'Swiss-Prot.2010.09': ['Q3SZC4']}, 'seq_leng': 370, 'protein': set(['ENSBTAP00000008580']), 'copy': 1L}, 'Phy0009U78_MOUSE': {'gene': set(['ENSMUSG00000050416']), 'seq': 'MKEVDNIREEWVCETGPPDSQPLNDNQQKDCEYYVDSLFEEAGKAGAKCLSPTEQKKQVDVNIKLWKNGFTVNDDFRSYSDGASQHFLNSIKKGELPSELRGIFDKEEVDVKVENKKNEVCMSTKPVFHPFSGQGHRLASATPRIVSKAKSVEVDNKSTLSAVSLNILEPITRIQIWLANGERTVQRFNVSHRVSHIKDFNEKYQGSQRSPPFALSTALPFLRFLDETLTLEEADLKNAVIIQRLQKTAKPFRKL', 'comments': set(['chromosome_NCBIM34_13_40339138_40339905_1 gene_ENSMUSG00000050416 transcript_ENSMUST00000054853 Oldphy_#Mms0017098#']), 'external': {}, 'seq_leng': 255, 'protein': set(['ENSMUSP00000058557']), 'copy': 1L}, 'Phy000CGZG_RAT': {'gene': set(['ENSRNOG00000022378']), 'seq': 'DLQIVLASFYEDAGAEDIVTISQANPSLMSRGTAPRQRFYAEGSERSRQQIVDLPRKKSPNKLVDDLFKGTKEHGTVAVKSPGETSKLRPFAEGGYRLGAAPEERSAYVAGERIQDVHVVLKPWKTRFSLDNDNLRSGRDPANAQFLESIRRAEVSVELWRLVYTGQVALDMEDHRDEDFVKPKGAFKAFTGEGQKVDSTPLLNTSSPNQQAENETKANLSILINEAESTMDIQIWLVDGGRLVQKFNHSHRISDNGLFIMYARPAMAATSFVLITTPNKKLADENQTLKEANLLCTVIAVIIW', 'comments': set(['chromosome_RGSC3.4_17_65701314_65702397_1 gene_ENSRNOG00000022378 transcript_ENSRNOT00000028942 Oldphy_#Rno0013357#']), 'external': {}, 'seq_leng': 304, 'protein': set(['ENSRNOP00000034835']), 'copy': 1L}, 'Phy0007CQ6_CHICK': {'gene': set(['ENSGALG00000015431']), 'seq': 'MADGGASPAQQEGEMSAAGPGLRRERQHRGSGRPPSARDLQLALAELYEDEAKRQSLRSDKPTTTKMSNSKGLKIDSFRSLRKPERSMSDDKENQRFYSGDSEYRGLQISGASNNPSKIVAELFKEAKEHGAVPLDEASRTSGDFSKAKSFSGGGYRLGDSSQKHSEYIYGENQDVQILLKLWRNGFSLDDGELRSYSDPINAQFLESVKRGEIPVELQRLVHGGQVNLDMEDHQEQEYVKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSILNAPVLIDDSVPATKIQIRLADGSRLIQRFNQTHRIKDIRDFIIQSRPAFATTDFVLVTTFPNKELTDESLTLREADILNTVILQQLK', 'comments': set(['chromosome_WASHUC1_2_111235822_111254908_1 gene_ENSGALG00000015431 transcript_ENSGALT00000024889 Oldphy_#Gga0009296#']), 'external': {'Ensembl.v59': ['ENSGALG00000015431', 'ENSGALP00000035955', 'ENSGALT00000036743']}, 'seq_leng': 365, 'protein': set(['ENSGALP00000024843']), 'copy': 1L}, 'Phy000CVNF_YEAST': {'gene': set(['YBL058W']), 'seq': 'MAEIPDETIQQFMALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQKDRREEAHWNRQQEKALKQEAFSTNSSNKAINTEHVGGLCPKPGSSQGSNEYLKRKGSTSPEPTKGSSRSGSGNNSRFMSFSDMVRGQADDDDEDQPRNTFAGGETSGLEVTDPSDPNSLLKDLLEKARRGGQMGAENGFRDDEDHEMGANRFTGRGFRLGSTIDAADEVVEDNTSQSQRRPEKVTREITFWKEGFQVADGPLYRYDDPANSFYLSELNQGRAPLKLLDVQFGQEVEVNVYKKLDESYKAPTRKLGGFSGQGQRLGSPIPGESSPAEVPKNETPAAQEQPMPDNEPKQGDTSIQIRYANGKREVLHCNSTDTVKFLYEHVTSNANTDPSRNFTLNYAFPIKPISNDETTLKDADLLNSVVVQRWA', 'comments': set(['chromosome_SGD1_II_111439_112710_1 gene_YBL058W transcript_YBL058W Oldphy_#Sce0000185#']), 'external': {'Ensembl.v59': ['YBL058W'], 'TrEMBL.2010.09': ['Q6Q5U0'], 'Swiss-Prot.2010.09': ['P34223']}, 'seq_leng': 423, 'protein': set(['YBL058W']), 'copy': 1L}, 'Phy0008N76_KLULA': {'gene': set([]), 'seq': 'MSDEQIQQFVALTNTSVNVASDYLNQFGDLGEALNAFYATQQDEQEPKTKASFEQPIPKAASQGELSNSSAKDDVTYARTLSGQKIALPRSTPSPSQKPKSKSKFQSFSDILKGGDDEDEDRNTFAGGETSGLEITDPHANDSNSLIRDLLQKARRGGERAEQEEEENEEAESKKHHFVGKGYRLGSDVSAPPTVVEDDTPVVSKPKKVTREITFWKDGFQVGDGKLYRYDDPENSFYLKELNQGRAPLQLLDVEFGQEVDVTVYKKLEEPYVPPKRKVSGFQGTGKRLGSPIPGDAVNSQSASPAESTPVGTEIKEKSPDDELKGDTSVQIRYASGKREVLRCNSTDTIRFLYQHVKANTAEMRPFTLSHAFPVKPIDEFDSTLKDQDLCNAVVVQRWV', 'comments': set(['Kluyveromyces lactis strain NRRL Y-1140 chromosome E of strain NRRL Y-1140 of Kluyveromyces lactis Oldphy_#Kla0001584#']), 'external': {'TrEMBL.2010.09': ['Q6CMI1']}, 'seq_leng': 400, 'protein': set(['Q6CMI1']), 'copy': 1L}, 'Phy0003SSX_CANFA': {'gene': set(['ENSCAFG00000007088']), 'seq': 'MAEGGGADPGEQERSSGPRPPSARDLQLALAELYEDEVKCKSSKSDRPKATVFKSPRTPPQRFYSSEHEYSGLHIVRPSTGKIVNELFKEAREHGAVPLNEATRASGDNKSKSFTGGGYRLGNSFCKRSEYIYGENQLQDVQILLKLWSNGFSLDDGELRPYNDPPNAQFLESVKRGEIPLELQRLVHGGHVNLDMEDHQDQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSIFNAVVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRNFIIQSRPEFATLDFILVTSFPNKELTDESLTLQEADILNTVILQQLK', 'comments': set(['chromosome_BROADD1_29_12239706_12264718_1 gene_ENSCAFG00000007088 transcript_ENSCAFT00000011356 Oldphy_#Cfa0017323#']), 'external': {'Ensembl.v59': ['ENSCAFG00000007088', 'ENSCAFP00000010519', 'ENSCAFT00000011356']}, 'seq_leng': 330, 'protein': set(['ENSCAFP00000010519']), 'copy': 1L}, 'Phy000D9JL_TETNG': {'gene': set(['GSTENG00003875001']), 'seq': 'ASQEQSVREFVAVTGVDEERARFFLESAGWSLHLALGSFFEDEGDEDIVTLPQPESGSSGSWSGGPSSSQPRVTSFRDLMHEAKEESDEEEGQRFFAGGSERSGQQIVGPPKKKSSNEVVEDLFKGAREHGAVPLDRSGKGPSDSRKPHAFFGGGYRLGTAPEESAYVAGERQASSTQQDVHVVLKLWKTGFSLDNGDLRNYNDPGNAGFLEAIRRGEIPLELREQSRGGQVNLDMEDHRDEDFVKPRVSFKAFGGEGQKLGSATPELTSPAASTHNQTANEAEARTSVTLDPSQPLTNIQIRLADGTKLIQKFNHTHRVSDLRLFVVAARPSMAAADFVLMTTFPNQELSDESQTLQQANLLNAVIVQRL', 'comments': set(['chromosome_TETRAODON7_Un_random_84312282_84315999_-1 gene_GSTENG00003875001 transcript_GSTENT00003875001 Oldphy_#Tni0006626#']), 'external': {'TrEMBL.2010.09': ['Q4TB74']}, 'seq_leng': 371, 'protein': set(['GSTENP00003875001']), 'copy': 1L}, 'Phy0003QBK_CANFA': {'gene': set(['ENSCAFG00000006789']), 'seq': 'QIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEEEEEEEGQRFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGERRRHSGQDVHVVLKLWKSGFSLDNGELRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLNTSSPAQQAENEAKASSSVSIDESQPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFVLMTTFPNKELADESQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_BROADD1_24_22498010_22517318_1 gene_ENSCAFG00000006789 transcript_ENSCAFT00000010930 Oldphy_#Cfa0014106#']), 'external': {'Ensembl.v59': ['ENSCAFP00000010130', 'ENSCAFT00000010930']}, 'seq_leng': 336, 'protein': set(['ENSCAFP00000010130']), 'copy': 1L}, 'Phy000BO0I_PANTR': {'gene': set(['ENSPTRG00000013164']), 'seq': 'MAAERQEALREFVAVTGAEEDRARFFLESAGWDLQIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEDEEEEEGQRFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGEKRQHSSQDVHVVLKLWKSGFSLDNGELRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLSTSSPAQQAENEAKASSSILIDESEPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFILMTTFPNKELADESQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_CHIMP1A_20_1402637_1428312_-1 gene_ENSPTRG00000013164 transcript_ENSPTRT00000024426 Oldphy_#Ptr0020671#']), 'external': {'Ensembl.v59': ['ENSPTRP00000052472', 'ENSPTRT00000059341']}, 'seq_leng': 370, 'protein': set(['ENSPTRP00000022532']), 'copy': 1L}, 'Phy00017N5_ARATH': {'gene': set([]), 'seq': 'MATETNENLINSFIEITSSSREEANFFLESHTWNLDAAVSTFLDNDAAAAAEPNPTGPPPPSSTIAGAQSPSQSHSPDYTPSETSPSPSRSRSASPSSRAAPYGLRSRGGAGENKETENPSGIRSSRSRQHAGNIRTFADLNRSPADGEGSDSDEANEYYTGGQKSGMMVQDPKKVKDVDELFDQARQSAVDRPVEPSRSASTSFTGAARLLSGEAVSSSPQQQQQEQPQRIMHTITFWLNGFTVNDGPLRGFSDPENAAFMNSISRSECPSELEPADKKIPVHVDLVRRGENFTEPPKPKNPFQGVGRTLGASGSGSSSAPQASSAPMNVAPAPSRGLVVDPAAPTTSIQLRLADGTRLVSRFNNHHTVRDVRGFIDASRPGGSKEYQLLTMGFPPKQLTELDQTIEQAGIANAVVIQKF', 'comments': set(['Putative phosphatase Oldphy_#Ath0008528#']), 'external': {'Swiss-Prot.2010.09': ['Q7Y175']}, 'seq_leng': 421, 'protein': set(['Q7Y175']), 'copy': 1L}, 'Phy0007DAU_CHICK': {'gene': set(['ENSGALG00000006182']), 'seq': 'GFPFQIALASFYEDGGDEDILTLPQPTPSSVSRGTAASDHRVTSFRDLVHAQEDDDEEEEGQRFYAGGSERSGQQIVGPPRKKSPNELVEDLFKGAKEHGAVAVDRTAKSSGESSKPKPFAGGGYRLGATPEEESAYVAGERRHNSVQDVHVVLKLWKTGFSLDSGELRSYQDPSNAQFLDDIRRGEVPAELRRLARGGQVNLDMEDHRDEEYVKPKSVFKAFTGEGQKLGSTAPQVLSTSSPAQQAENEAKASSAIAIDESEPVTNIQIRLADGGRLVQKFNHNHRIRDIRLFIVDARPAMAATSFVLMTTFPNKELTDENQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_WASHUC1_20_9445267_9450956_1 gene_ENSGALG00000006182 transcript_ENSGALT00000009978 Oldphy_#Gga0010040#']), 'external': {}, 'seq_leng': 340, 'protein': set(['ENSGALP00000009964']), 'copy': 1L}, 'Phy000B3RA_PLAFA': {'gene': set([]), 'seq': 'MSNIRSLSDLKKDDKKNNERVAHYTGGQKSGLEVQNSDDDFVQNLFKSKLPENCRHITLYKNGFIVDDGEFRDLEIEENKKFMANIEAGILPKEFASKDKTMNVAIKDKSNQIYTKKKTKEQELYKGQGVKLGGTISSISEEEMNKISTDPNNIKEIKIDDKKPITTLHIRLYNGKKITQKFNYDHTVEDLFQFVFSYTPVNFSLSYDYPLKLINRNEHQTLESAKLLDLLITQKLIP', 'comments': set(['Hypothetical protein MAL8P1.122 Oldphy_#Pfa0000135#']), 'external': {}, 'seq_leng': 238, 'protein': set(['Q8IAS1']), 'copy': 1L}, 'Phy0005ZK6_DROME': {'gene': set(['CG4556']), 'seq': 'MTDEQKLSTFMKRHGVREEVARQYLSSNNWSLEVASSTYESEAVSKKQEPEKSSEHSQANESNRDLHSLLSEISRRKEGDHDGYQACASDSSTDHDTPAGKRVNINSSTPAITNNDSDRSLRVWGHGNRLGSAHPINPPPRSATEDSDTEPADDEHTIVVLHLWSEGFSLDDGSLRLYALPENERFLRAILRGDFPEEMLRVPRVQLSVQDHTNESYRHLSRKQFMGPGRPLNSPSPQILVVGPMPVEAQGLQLNERADTTTVQLRMADGSRVAGRFNLTHNVGDLYQYARLARPEFSDRSFVLMTAFPRQELVESDTRTLVQANLCNVVVIQHLNEEQVEPLSSDASEPIVQ', 'comments': set(['chromosome_BDGP4_2R_19931526_19932702_-1 gene_CG4556 transcript_CG4556-RA Oldphy_#Dme0016713#']), 'external': {'Ensembl.v59': ['FBgn0259729', 'FBpp0289272', 'FBtr0299995'], 'TrEMBL.2010.09': ['Q8T4C3', 'Q9U9C9', 'Q9W175']}, 'seq_leng': 353, 'protein': set(['CG4556-PA']), 'copy': 1L}, 'Phy000BD05_PANTR': {'gene': set(['ENSPTRG00000011705']), 'seq': 'MKDVDNLKSIKEEWVCETGSDNQPLGNNQQSNCEYFVDSLFEEAQKVSSKCVSPAEQKKQVDVNIKLWKNGFTVNNDFRSYSDGASQQFLNSIKKGELPSELQGIFDKEEVDVKVEDKKNEICLSTKPVFQPFSGQGHRLGSATPKIVSKAKNIEIENKNNLSAVPLNNLEPITNIQIWLANGKRIVQKFNISHRVSHIKDFIEKYQGSQRSPPFSLATALPVLRLLDETLTLEEADLQNAVIIQRLQKTASFRELSEH', 'comments': set(['chromosome_CHIMP1A_2A_24954086_25012968_1 gene_ENSPTRG00000011705 transcript_ENSPTRT00000021798 Oldphy_#Ptr0006402#']), 'external': {'Ensembl.v59': ['ENSPTRG00000011705', 'ENSPTRP00000020106', 'ENSPTRT00000021798']}, 'seq_leng': 259, 'protein': set(['ENSPTRP00000020106']), 'copy': 1L}, 'Phy0005KKQ_DEBHA': {'gene': set([]), 'seq': 'GGVRKIRDLNKKEEEDEEDKKDKNFFTGGEKSALQVEDPNKRGDKKKEKSIIDKIFQRAKEQMDQPDERPSSNQDQPEEVRKFTGTGFKLGGENEPSEQVADMNSRLPKKPSKVTREITFWKQGFTVGEGALHRYDDPNNASLLQELNAGRVPMSLLDVEFGQDVDVSLFKKTDEDWVPPKTKVGGFSGQGQRLGSPVPGESCGASPAPEAQPEPTKETKPEDKGEGDSLVQIRFANGKKTSHKFNSTDSITKVYDFVRTHPFTESDKSFILTHAFPVKPIEESNDLTVGDAKLKNAVIVQRWI', 'comments': set(['Debaryomyces hansenii chromosome A of strain CBS767 of Debaryomyces hansenii _Fragment_ Oldphy_#Dha0003604#']), 'external': {}, 'seq_leng': 304, 'protein': set(['Q6BYR9']), 'copy': 1L}, 'Phy00036IS_CAEEL': {'gene': set(['Y94H6A.9']), 'seq': 'MSRNIRTFRDIGNNDDGGPDSDDSGADAAERGAPQEFYAGSGQAVQGPRGAAARGPDSEAHIRRILQAAEVVQPEGGEAPRGRPSGRETISLTLHLWSDGLSIEDGPLMSRQDPRTIEFLESVGKGEIPPSLVQQYPGKEIDFKVNRHHEEYVAPKMKPFGGSGVRLGNVVPTVLGQSSSSATTAGTSSATTDHNPDHTAENEAKQLEDAKKELSTNMNEPTTNIQIRLPNNQRLVGIFNHSHTLEAVRTFICTARPDMIYAPFQMMAAYPPKPFEDESQTLKDANVLNSVVAVKILPTTN', 'comments': set(['chromosome_CEL140_IV_2720562_2725816_-1 gene_Y94H6A.9 transcript_Y94H6A.9a Oldphy_#Cel0010715#']), 'external': {'Ensembl.v59': ['Y94H6A.9a'], 'TrEMBL.2010.09': ['Q9N2W5']}, 'seq_leng': 301, 'protein': set(['Y94H6A.9a']), 'copy': 1L}, 'Phy0008J14_HUMAN': {'gene': set(['ENSG00000178166']), 'seq': 'EGGGPELGEQERRSSRLWPPSAQDLQNLINKLALEELYEDEVKRKSSKSDRPKAAVFKSPRTPPQSFTGGGYRLGNSFCKRSEYMHGENQLQDVQILLKLWSNGFSLDDGELRPYNEPTNAQFLEFVKRGEIPLELQCLVHGGQVNWDMEDHQDQEYIKPRLRFKAFSGEGQKLGRLTPEIVSTPSSPEEEDKSILNAVVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRNFIVQSCPEFAALDFILVTSFPNKELTDESLTLLEADILNTVLLHQLK', 'comments': set(['chromosome_NCBI35_7_156489770_156490675_-1 gene_ENSG00000178166 transcript_ENST00000314451 Oldphy_#Hsa0028192#']), 'external': {}, 'seq_leng': 283, 'protein': set(['ENSP00000319187']), 'copy': 1L}, 'Phy0002JCG_CANAL': {'gene': set([]), 'seq': 'MSENTPDSQLIAEFVSITNSSTYLAEQYLSRNSNDLVEAVEDFYANNEPSQKSETKKSSSSNAKGSGVRTFRDLNDEDDDEEDDKTNTNFFTGGEKSGLQVEDPNKDKDNDRSIIDQIFQKAREQMQQPDDRPSASQNDQPSPIKFSGKGFKLGDGNEPSQVVEDPNASAKKFRPSKVTREITFWKQGFTVGDGPLHRYDDPRNAMFCKNLNQGRVPMSILDVEFGQDVDVSVYKKTDEDWTPPKRKIGGYHGAGHRLGSPVPGEVLVNNEASSQPDIKTETEISKPKDGGEGDSTVQIRFANGKRTSHKFNSSDSILKVYEFVKNHEYNSEPTRPFTLSHAFPVKPIEESSDITISDAKLKNAVIVQRWK', 'comments': set(['orf19.2549 CGDID_CAL0002468 Contig19-10151 _46431, 45317_ CDS, reverse complemented, translated using codon table 12  _371 residues_ Oldphy_#Cal0001948#']), 'external': {}, 'seq_leng': 371, 'protein': set(['orf19.2549']), 'copy': 1L}, 'Phy0002JCJ_CANAL': {'gene': set([]), 'seq': 'MSENTPDSQLIAEFVSITNSSTYLAEQYLSRNSNDLVEAVEDFYANNEPSQKSETKKSSSSNAKGSGVRTFRDLNDEDDDEEDDKTNTNFFTGGEKSGLQVEDPNKDKDNDRSIIDQIFQKAREQMQQPDDRPSASQNDQPSPIKFSGKGFKLGDGNEPSQVVEDPNASAKKFRPSKVTREITFWKQGFTVGDGPLHRYDDPRNAMFCKN', 'comments': set(['orf19.2550 CGDID_CAL0002473 Contig19-10151 _46431, 45799_ CDS, reverse complemented, translated using codon table 12  _210 residues_ Oldphy_#Cal0001951#']), 'external': {'TrEMBL.2010.09': ['Q5A9B5']}, 'seq_leng': 210, 'protein': set(['orf19.2550']), 'copy': 1L}, 'Phy0004H5V_CIOIN': {'gene': set(['ENSCING00000001500']), 'seq': 'MSSQDEMVTEFRGITDASEERARFFLESSGWQLQVIYTSTHHPDEVDEEYVPEEDPEPPKNKPGVSTRSSKVEPKRTTRSSKFASVHDYKNNKNDDSSEEEGQRYYAGGSEHSGELIVGPPRKKNTNQQIKDLFKEAKEHGAEVVDEPRKHGKEKEKKKYFTGAGYKLGDGGEDSPSVFVPGEVEQQRPGPVNVVLKLWSNGFTVDDGPLRDFNDPQNQEFLQSVKKGQIPQELIRNAKGGEVHVDMEDHREEDYKPQKKKLKPFSGQGQMLGSEAHLRPGIPTPQVETSPAPSISSSVDPPISIDQSKPSTNIQIRLLDGTRIRQQFNHDHRVSDIRSFILNSQPNMGSRPFVLMTTFPNKELTNENETIAGAQLLNSQVVQKLK', 'comments': set(['scaffold_CINT1.95_scaffold_276_60319_66740_-1 gene_ENSCING00000001500 transcript_ENSCINT00000002962 Oldphy_#Cin0013449#']), 'external': {}, 'seq_leng': 386, 'protein': set(['ENSCINP00000002962']), 'copy': 1L}, 'Phy000CO1I_RAT': {'gene': set(['ENSRNOG00000009137']), 'seq': 'MAEGGGAEPEEQERRSSRPRPPSARDLQLALAELYEDEMKCKSSKPDRSTATAFKSPRTPPLRLYSGDQEYGGLHIAQPPTGKIVNELFKEAREHGAVPLNEATRSSSDDKAKSFTGGGYRLGSSFYKRSEYIYGENQLQDVQILLRLWSNGFSLDDGELRPYSDPTNAQFLESVKRGEIPLELQRLVHGSQVSLDMEDHQDQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSILNAAVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRDFIVQSRPEFATTDFILVTSFPSKELTDESVTLQDADILNTVILQQLK', 'comments': set(['chromosome_RGSC3.4_5_19631872_19654541_1 gene_ENSRNOG00000009137 transcript_ENSRNOT00000012551 Oldphy_#Rno0022503#']), 'external': {'Ensembl.v59': ['ENSRNOG00000009137', 'ENSRNOP00000012551', 'ENSRNOT00000012551'], 'Swiss-Prot.2010.09': ['P0C627']}, 'seq_leng': 331, 'protein': set(['ENSRNOP00000012551']), 'copy': 1L}, 'Phy000BVFY_PANTR': {'gene': set(['ENSPTRG00000020274']), 'seq': 'MAEGGGPEPGEQERRSSGPRPPSARDLQLALAELYEDEVKCKSSKSNRPKATVFKSPRTPPQRFYSSEHEYSGLNIVRPSTGKIVNELFKEAREHGAVPLNEATRASGDDKSKSFTGGGYRLGSSFCKRSEYIYGENQLQDVQILLKLWSNGFSLDDGELRPYNEPTNAQFLESVKRGEIPLELQRLVHGGQVNLDMEDHQDQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSILNAVVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRNFIVQSRPEFAALDFILVTSFPNKELTDESLTLLEADILNTVLLQQLK', 'comments': set(['chromosome_CHIMP1A_8_61236696_61276533_1 gene_ENSPTRG00000020274 transcript_ENSPTRT00000037556 Oldphy_#Ptr0030299#']), 'external': {'Ensembl.v59': ['ENSPTRG00000033886', 'ENSPTRP00000055380', 'ENSPTRT00000063836']}, 'seq_leng': 331, 'protein': set(['ENSPTRP00000034710']), 'copy': 1L}, 'Phy0007FZD_CHICK': {'gene': set(['ENSGALG00000016497']), 'seq': 'MDNIKTVKEEWMCKSRTGDQILNGTEQNHDYFVDNLFEEAQKIGAICMSPTTVKNQVDVIIKLWKNGFTVNDGELRSYTDVGNQQFLDSVKKGELPFELQKVFEKEEVDVKVEDKKDELYLSSKKPIFHPFSGHGYRLGSATPRIISKAREDHQGAADKRRLPVVPLNDLEPITNIQIWLADGERIIQKFNVSHRISHVRDFITKYQGSEGGVPFMLTTSLPFRELQDETLTLQEAKLQNAVVVQRLRKTTEPFRLLAMKAPDDDCKTAATPNGRLKNEQKNAMKSTSSN', 'comments': set(['chromosome_WASHUC1_3_102264124_102281158_1 gene_ENSGALG00000016497 transcript_ENSGALT00000026614 Oldphy_#Gga0013515#']), 'external': {'Ensembl.v59': ['ENSGALG00000016497', 'ENSGALP00000026563', 'ENSGALT00000026614'], 'TrEMBL.2010.09': ['Q5ZKL4']}, 'seq_leng': 290, 'protein': set(['ENSGALP00000026563']), 'copy': 1L}, 'Phy0006ZSN_TAKRU': {'gene': set(['NEWSINFRUG00000121537']), 'seq': 'MASQEQSVKEFVAVTGVDEERARFFLESAGWSLHLALGSFFEDEGDEDIVTLPPPDSGSSGSWSGGPSSQPRVTSFRDLMHEAKEESDEEEGQRFFAGGSERSGQQIVGPPKKKSSNEVVEDLFKGAREHGAVPLDRSGKGPVDSRKHHAFFGGGYRLGTAPEESAYVAGEKQASNNQQDVHVVLKLWKTGFSLDNGDLRNYNDPGNAGFLEAIRRGEIPLELREQSRGGQVNLDMEDHRDEDFAKPKVSFKAFGGEGQKLGSATPELASPAATSTQNQAANEASTSVTLDYDQPLTSIQIRLADGTKLIQKFNHTHRVSDLRHFVIAAQPSMAAMEFVLMTTFPNKELSDESKTLQQANLLNAVIVQRLK', 'comments': set(['scaffold_FUGU4_scaffold_220_276304_280560_1 gene_NEWSINFRUG00000121537 transcript_NEWSINFRUT00000128304 Oldphy_#Fru0014548#']), 'external': {}, 'seq_leng': 371, 'protein': set(['NEWSINFRUP00000128304']), 'copy': 1L}, 'Phy0008ZAA_MONDO': {'gene': set(['ENSMODG00000008866']), 'seq': 'PTPGGHRQEKRHSGSRAGPRPPTARDLQLALAELYEDEVKCRSSFQSEKPKAKVFKSPRTPPQRLYSGEHEYSGLHISGPSKTTGKIVDELFKEAKEHGAVPLNETTRASGDGNKSKSFLGGGYRLGDSSRKRSEYVYGENQLQDVQILLKLWSNGFSLDDGELRSYTDPTNAQFLESVKRGEIPLELQRLVHGGQVNLDMEDHQEQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEEKSIINAVVLIDDSVPTTKIQIRLADGSRLIQRFNHTHRIMDVREFIIQSRPEFATLGFVLVTTFPNKELTDESLTLQEADILNTVILQQLK', 'comments': set(['scaffold_BROADO2_scaffold_4_105290513_105321030_-1 gene_ENSMODG00000008866 transcript_ENSMODT00000011257 Oldphy_#Mdo0003936#']), 'external': {'Ensembl.v59': ['ENSMODG00000008866', 'ENSMODP00000011040', 'ENSMODT00000011257']}, 'seq_leng': 335, 'protein': set(['ENSMODP00000011040']), 'copy': 1L}, 'Phy0001SFG_ARATH': {'gene': set([]), 'seq': 'MSSKDKKLSKPTSGRTGGIRTLSDLNRRSEPDSDSDSDGPQEYFTGGEKSGMLVQDPTKEPKHDDVDEIFNQARQLGAVEGPLEHPSSSRSFTGTGRLLSGESVPTALQQPEPVIHNIIFWSNGFTVDDGPLRKLDDPENASFLDSIRKSECPKELEPVDKRAPVHVNLMRRDEKCPEKEKLKVSFQGVGRTLGGASSSTASSQSNLTDVAAVQSPLQSLVVDETLPSTSIQLRLADGTRMVAKFNNHHTVNDIRGFIEFSRPGNPNNYTLQVMGFPPKPLTDPSQTIEQAGLASSVVIQKF', 'comments': set(['Hypothetical protein AT4g22150 _CDC48-interacting UBX-domain protein_ Oldphy_#Ath0035467#']), 'external': {'TrEMBL.2010.09': ['Q9SUG6']}, 'seq_leng': 302, 'protein': set(['Q9SUG6']), 'copy': 1L}, 'Phy0002JCH_CANAL': {'gene': set([]), 'seq': 'MSENTPDSQLIAEFVSITNSSTYLAEQYLSRNSNDLVEAVEDFYANNEPSQKSETKKSSSSNAKGSGVKTFRDLNDEDDDEEDDKTNTNFFTGGEKSGLQVEDPNKDKDNDRSIIDQIFQKAREQMQQPDDRPSASQDDQPSPIKFSGKGFKLGDGNEPSQVVEDPNASAKKFRPSKVTREITFWKQGFTVGDGPLHRYDDPRNASVLQELNQGRVPMSILDVEFGQDVDVSVYKKTDEDWTPPKRKIGGYHGAGHRLGSPVPGEVLVNNEASSQPDIKTETEISKPKDEGEGDSTVQIRFANGKRTSHKFNSSDSILKVYEFVKNHEYNSEPTRPFTLSHAFPVKPIEESSDITISDAKLKNAVIVQRWK', 'comments': set(['orf19.2549 CGDID_CAL0002468 Contig19-20151 _46449, 45334_ CDS, reverse complemented, translated using codon table 12  _371 residues_ Oldphy_#Cal0001949#']), 'external': {'TrEMBL.2010.09': ['C4YKZ7', 'Q5A9L6']}, 'seq_leng': 371, 'protein': set(['orf19.10082']), 'copy': 1L}, 'Phy000CPNE_RAT': {'gene': set(['ENSRNOG00000004950']), 'seq': 'MKEVDNLDSIKEEWVCETGPPDNQPLNDNPQKDCEYFVDSLFEEAEKAGAKCLSPTEQKKQVDVNIKLWKNGFTVNDDFRSYSDGASQQFLNSIKKGELPSELQGVFDKDEVDVKVEDKKNEVCMSTKPVFQPFSGQGHRLGSATPRIVSKAKSIEVDNKSTLSAVSLNNLEPITRIQIWLANGERTVQRFNISHRVSHIKDFIEKYQGTQRSPPFALATALPFLRFLDETLTLEEADLQNAVIIQRLQKTAEPFRKL', 'comments': set(['chromosome_RGSC3.4_6_28188233_28209727_-1 gene_ENSRNOG00000004950 transcript_ENSRNOT00000006668 Oldphy_#Rno0024587#']), 'external': {'Ensembl.v59': ['ENSRNOG00000004950', 'ENSRNOP00000006668', 'ENSRNOT00000006668'], 'TrEMBL.2010.09': ['D3ZID8']}, 'seq_leng': 258, 'protein': set(['ENSRNOP00000006668']), 'copy': 1L}, 'Phy0003L1L_CANFA': {'gene': set(['ENSCAFG00000003944']), 'seq': 'MKEVDNLESIKEEWVCETGSDNQPLSDDRQRNCEYFVDSLFEEAEKVGAKCMSPTEQKKQVDVSIKLWKNGFTVNDDFRSYTDGASQQFLNSVKKGELPLELQGIFDKEEVDVKVEDKKNEVCMSTKPVFQPFSGQGHRLGSATPKIVSKSKSIEVENKNNLSVVQLNNLEPITNVQIWLANGKRIVQKFNISHRISHIKDFIEKYQGSQRSPPFSLATALPFLKLLDETLTLEEADLQNAVIIQRLQKTAEPFREL', 'comments': set(['chromosome_BROADD1_17_21431502_21461427_1 gene_ENSCAFG00000003944 transcript_ENSCAFT00000006336 Oldphy_#Cfa0007267#']), 'external': {}, 'seq_leng': 257, 'protein': set(['ENSCAFP00000005869']), 'copy': 1L}, 'Phy000CLXL_RAT': {'gene': set(['ENSRNOG00000008604']), 'seq': 'MAEERQDALREFVAVTGAEEDRARFFLESAGWDLQIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEEEEEEEGQRIRFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGERRRHSGQDVHVVLKLWKTGFSLDNGDLRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLNTSSPAQQAENEAKASSSILINEAEPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFVLMTTFPNKELADENQTLKEANLLNAVIVQRLT', 'comments': set(['chromosome_RGSC3.4_3_141799286_141823762_1 gene_ENSRNOG00000008604 transcript_ENSRNOT00000011654 Oldphy_#Rno0019770#']), 'external': {'TrEMBL.2010.09': ['D3ZEG3']}, 'seq_leng': 372, 'protein': set(['ENSRNOP00000011654']), 'copy': 1L}, 'Phy0005KKR_DEBHA': {'gene': set([]), 'seq': 'MSNQEQDQLIDQFVTVTNSSKSLAEQYLARNENDLINAIEDYYATSSNTENSGIDNTKPKQPKASGGVRTFRDLNNNEDDDEEDKTDTNFFTGGEKSALQVEDPNKRGDKKKEKSIIDQIFQRAKEQMDQPDERPSSNQDQPEEVRKFTGTGFKLGGENEPSEQVADMNSRLPKKPSKVTREITFWKQGFTVGEGALHRYDDPNNASVLQELNAGRVPMSLLDVEFGQDVDVSVFKKTDEDWVPPKRKVGGFSGQGQRLGSLYQENRVVRLQLQKLNQSLQRKQNQRIRVKVTL', 'comments': set(['Debaryomyces hansenii chromosome A of strain CBS767 of Debaryomyces hansenii Oldphy_#Dha0003605#']), 'external': {}, 'seq_leng': 294, 'protein': set(['Q6BYS0']), 'copy': 1L}, 'Phy0000P6F_APIME': {'gene': set(['ENSAPMG00000005963']), 'seq': 'MENHDELVSQFIDTTGVEPEEARFYLELSNWQLEVALDTFYYPLALPSLSNEPTEGTSEEERTDISDKNAGSVKSSEMEGKSSKEKIKPKSKFAMLSDLKDRESSPEDEEGQAFYAGGSEHTGQQILGPGKKKDIVSDMFKSCQRQSIAVESKPSGQQRPNTFSGTGIFFTVVTATTSNNQQTNSGLITLKLWKDGFTINDSELRLYSDPENREFLETIKRGEIPAEIRQEIQGTEARLDMEDHHHETYVPPKVKVKAFSGKGHMLGSPSPATVGMTIPTDLADQAANESQAKQKLNLDESKPVTTLQIRLADGTSVKAQFNLTHTINDLRQYIITMRPQYAMREFNLLTMYPTKELTEDKTIEEAGLQNTTIIQRLK', 'comments': set(['group_AMEL2.0_Group5_4355307_4357175_1 gene_ENSAPMG00000005963 transcript_ENSAPMT00000010305 Oldphy_#Ame0012288#']), 'external': {}, 'seq_leng': 378, 'protein': set(['ENSAPMP00000010305']), 'copy': 1L}, 'Phy00098SP_MONDO': {'gene': set(['ENSMODG00000019559']), 'seq': 'KMAERQEALREFVAVTGAEEDRARFFLESAGWDLQIALASFYEDGGDEDLVSLSQPAPSSVSRGTAPSDNRVTSFRDLVHAQEDDEDDEEGQRFYAGGSERSGQQIVGPPRKKSPNELVEDLFKGAKEHGAVAVDRMAKSPGETSKPKPFAGGGYRLGAAPEEESAYVAGERRSYSGQDVHIVLKLWKSGFSLDSGELRSYQDPSNAQFLESIRRGEVPTELRRLSRGGQVNLDMEDHRDEDFVKPKGTFKAFTGEGQKLGSTTPQLLNTSSPAQQAENEAKASSSITIDESEPTTNIQIRLADGGRLVQKFNHRHRISDVRLFIVDARPAMAAMSFVLMTTFPNKELADESQTLKEANLLNAVIVQRLI', 'comments': set(['scaffold_BROADO2_scaffold_38_3811058_3902759_-1 gene_ENSMODG00000019559 transcript_ENSMODT00000024831 Oldphy_#Mdo0016263#']), 'external': {'Ensembl.v59': ['ENSMODG00000019559', 'ENSMODP00000024398', 'ENSMODT00000024831']}, 'seq_leng': 370, 'protein': set(['ENSMODP00000024398']), 'copy': 1L}, 'Phy00057S0_DICDI': {'gene': set([]), 'seq': 'MSDHSEAIATFQSITGASKEESTFYLESHDWDLEKAAQTFTTLQEEENQRNDQPQIEEDYEDEEEEDDHRDPMPASRPVYSKPVAKTVSKKAPAGGRVGGIRTLSDFNNDDHDDHDHSDGDDDEDDRSQQYFTGGEKSGLVVESAPKKGKNGGSGDIVNDVFDSAKRHGAVASNEKKVEKPDSFDSVGYQLGATDQGNRNVSKPKEKDPNSQVVEVKVTFWNQGFTIDDGPLRKYDNPENKELLDDIQRGIVPRELQKKATTPNGLSVTLINNHNQDYVEPAKPKYVAFSGGGQTLGSSSTSTNNNNNNNNNNNNRATTTSTTTTSTPNVSSINVDQSQPTTTVQIRLANGSRLSTTFNHSHTLQDVINYINSSSGSNQSFDLLTGFPQKPVTNPTSTTLKDAGLLNALLIQKLK', 'comments': set(['Hypothetical protein Oldphy_#Ddi0000107#']), 'external': {'Swiss-Prot.2010.09': ['Q54BQ5']}, 'seq_leng': 415, 'protein': set(['Q54BQ5']), 'copy': 1L}, 'Phy0001H3K_ARATH': {'gene': set([]), 'seq': 'MSEETVSSELEEEPQKVFTHTVTSWSNGFTVDDSSLKTLDDPENATFLEIISSMESPRELGQVRVQVKIISREEENYTVYLSPSLFSDSNKPESQAGSDSASTKPPPALAMRAKESAIERSEQSSKVLSGETDSAELQEQQQEDQPYEVVTYTVTIWRNGFTVDDDPFKSLDDPENAAFLEELQTLAGSESTSTEPPLTTTQPPSMSSLVVDPAAPTTSIQLILADSTRIVTQFNTHHTIRDIRCFIDTSRPDGSKDYQLLIMGSPPTPLSDFDQTIEKAGIANSVLVQKF', 'comments': set(['Emb|CAB10320.1 Oldphy_#Ath0020783#']), 'external': {'TrEMBL.2010.09': ['Q9LVE1']}, 'seq_leng': 291, 'protein': set(['Q9LVE1']), 'copy': 1L}, 'Phy000AACP_MACMU': {'gene': set(['ENSMMUG00000015994']), 'seq': 'MAAERQEALREFVAVTGAEEERARFFLESAGWDLQIALASFYEDGGDEDIVTISQATPSSVSRGTAPSDNRVTSFRDLIHDQDEDEEEEEGQRFYAGGSERSGQQIVGPPRKKSPNELVDDLFKGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGEKRQHSSQDVHVVLKLWKSGFSLDNGELRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLSTSSPAQQAENEAKASSSILIDESEPTTNIQIRLADGGRLVQKFYHSHRISDIRLFIVDARPAMAATSFILMTTFPNKELADESQTLKEANLLNAVIVQRLT', 'comments': set(['scaffold_MMUL_0_1_SCAFFOLD95141_54735_80021_1 gene_ENSMMUG00000015994 transcript_ENSMMUT00000022486 Oldphy_#Mmu0003844#']), 'external': {}, 'seq_leng': 370, 'protein': set(['ENSMMUP00000021035']), 'copy': 1L}, 'Phy0008TSZ_LEIMA': {'gene': set([]), 'seq': 'MEARGNVDGEKFRSINTLRTRFPALTVSDARALLERHNWNVAIAGAEAERGERQRTKADSANYFVGGGDKGSGQQVMAPSGESVSDRSGEIASGSGVHSMIDRIFRKAEVEGAKASGGDGGSGVEDNEPRAFYGRGQRLGYTANPSPYVASTLRAERSVCITVYRDGFEVDSNGFVPLNSDEGRQFVEAMDKGYVPPSLAAKYPNTDLTVNLRDCLQVDYVPPSYIAFQGDGHRLAAPSSTAASSAAPANAQASPATAGRSGTPAYDPSRTVEVRSDEATSFVVLLNTRGERRQVQVNPERHTVDDLYSLAHAYQPELQNFILVERGMPPRRLEASTRSQTIAQAKLSRAVVALQQM', 'comments': set(['Hypothetical protein Oldphy_#Lma0004833#']), 'external': {'TrEMBL.2010.09': ['Q4QBW3']}, 'seq_leng': 357, 'protein': set(['Q4QBW3']), 'copy': 1L}, 'Phy0004PJ7_CRYNE': {'gene': set([]), 'seq': 'MAPSSQDISQFTAITQASEDEAVHWLESSGSLEAAVQDYLTAQDAAGTAGAGDDLPGNEAPSLATTGGASGARTLSGAPVQDTVPAGWGQPQRSQFGRIQHNDNDRGDDDKDPEELFAGGGKNSGLAVQNPDDAPGSGNSLVDKILKAASRNGAPPPRSNEPAAPPGRSAFFGGAGNTLGSDETPSTSVASEQPSQSPGPSVQTGGMPGGFGGLGAIPPGLMEQLMNQMSGRSGAPPSALSPGPSNIDHIDPSRISTDENGETVVHRSLTFWRNGFSIEDGPLLAYDEPQNRHLLQALEEGRAPSAAFGVPFDQRVNVEVHQRRREDYVAPKKKMKAFVGGGQRLGDAVPEVASGSASPMPGSLPTSSSNIGENTGRGTSGETKFEVDPSKPTTNIQLRFGDGSRQVARVNLDHTIADLRSYVTAARSDSRPFVLQTTFPSKELSDMNETVEGAKLQNAVVVQRFV', 'comments': set(['Hypothetical protein Oldphy_#Cne0002749#']), 'external': {'TrEMBL.2010.09': ['Q5KEX0']}, 'seq_leng': 466, 'protein': set(['Q55RA0']), 'copy': 1L}, 'Phy000BUTW_PANTR': {'gene': set(['ENSPTRG00000019921']), 'seq': 'EGGGPELGEQERRSSRLWPPSAQDLQNLINKLALEELYEDEVKRKPSKSDRPKAAVFKSPRTPPQSFTGGGYRLGNSFCKRSEYMHGENQLQDVQILLKLWSNGFSLDDGELRPYNEPTNAQFLEFKRGEIPLELQCFVHGGQVNWDMEDHQDQEYIKPRLRFKAFSGEGQKLGRLTPEIVSAPSSPEEEDKSILNAVVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRNFIVQSCPEFAALDFIPVTSFPNKELTDESLTLLEADILNTVLLHQLK', 'comments': set(['chromosome_CHIMP1A_7_159310366_159311274_-1 gene_ENSPTRG00000019921 transcript_ENSPTRT00000036914 Oldphy_#Ptr0029505#']), 'external': {}, 'seq_leng': 282, 'protein': set(['ENSPTRP00000034120']), 'copy': 1L}, 'Phy000A0DO_MOUSE': {'gene': set(['ENSMUSG00000020634']), 'seq': 'MKEVDNLDSIKEEWACETGPPDSQPLNDNQQKDCEYFVDSLFEEAGKAGAKCLSPTEQKKQVDVNIKLWKNGFTVNDDFRSYSDGASQQFLNSIKKGELPSELWGIFDKEEVDVKVEDKKNEVCMSTKPVFQPFSGQGHRLGSATPRIVSKAKSVEVDNKSTLSAVSLNNLEPITRIQIWLANGERTVQRFNVSHRVSHIKDFIEKYQGSQRSPPFALATALPFLRFLDETLTLEEADLKNAVIIQRLQKTAEPFRKL', 'comments': set(['chromosome_NCBIM34_12_4054764_4083225_-1 gene_ENSMUSG00000020634 transcript_ENSMUST00000020962 Oldphy_#Mms0025106#']), 'external': {'Ensembl.v59': ['ENSMUSG00000020634', 'ENSMUSP00000020962', 'ENSMUSP00000118834', 'ENSMUST00000020962', 'ENSMUST00000142867'], 'TrEMBL.2010.09': ['B8JK44'], 'Swiss-Prot.2010.09': ['Q99KJ0']}, 'seq_leng': 258, 'protein': set(['ENSMUSP00000020962']), 'copy': 1L}, 'Phy000EWDU_YARLI': {'gene': set([]), 'seq': 'MVSEEEKTERIAQFVGITQSSPEDAQDCLLHTDWDVAQAVDLFLSANDDPEENEEDAENDDAEDIDVEEDSDAYANPSGLAPSGIAAGIQGFLSGLAGRDDPAAAASEPQGILSNPQPSGYRLGDGTGSSTPVSGASSSTTPAPSAPAPAPAPRRGVAGVRTLGDLSRDNAPPKRQDLFTGGEKSALAVQNPNRPGQPGNQGGNPLVNDIIRRAEANPARPRGENDDESEDEEQVGSFHGTGFTLGSDEVQSRPVESALPTSLPKVSRSITFWQNGFTVEDGPLYRYDDPRNQRYLETLNQGRAPLALLDVQHNQAVDINVTDRSEEAYVEKKPVYGGSGNRLGSPVPGEPTPSSSATPPPSAPTPAATSSGPSNSSSGAGGSRIQIRLGDGTRLTPSFSPDLTVQSLYDFVDEHNPSGREYVLQTTFPNKELRDKSLTLKDAKVIGAAIVQRYE', 'comments': set(['Similar to KLLA0E20141g Kluyveromyces lactis Oldphy_#Yli0002312#']), 'external': {'TrEMBL.2010.09': ['Q6C5V3']}, 'seq_leng': 455, 'protein': set(['Q6C5V3']), 'copy': 1L}, 'Phy0006QQY_TAKRU': {'gene': set(['NEWSINFRUG00000151706']), 'seq': 'VEMVVRLWKDGFTVNDEEFRSYSVPENQDFLDAIKRGELPGEWESRAEKEELEISVEDLTEENYLPKKKVFHPFSGRGYRLGSVAPRVVARSPSVHEDGESPPIPMVTLDHALPVTSLQIWLADGRRLVQRFNLSHRIIDVQDFVARSQRSCPPFILTTSLPFRELSDKDLSLEEADLANAVIVQR', 'comments': set(['scaffold_FUGU4_scaffold_16_146037_147934_-1 gene_NEWSINFRUG00000151706 transcript_NEWSINFRUT00000161354 Oldphy_#Fru0002823#']), 'external': {}, 'seq_leng': 186, 'protein': set(['NEWSINFRUP00000161354']), 'copy': 1L}, 'Phy0008JFW_HUMAN': {'gene': set(['ENSG00000172659']), 'seq': 'MAEGGGPEPGEQERRSSGPRPPSARDLQLALAELYEDEVKCKSSKSNRPKATVFKSPRTPPQRFYSSEHEYSGLNIVRPSTGKIVNELFKEAREHGAVPLNEATRASGDDKSKSFTGGGYRLGSSFCKRSEYIYGENQLQDVQILLKLWSNGFSLDDGELRPYNEPTNAQFLESVKRGEIPLELQRLVHGGQVNLDMEDHQDQEYIKPRLRFKAFSGEGQKLGSLTPEIVSTPSSPEEEDKSILNAVVLIDDSVPTTKIQIRLADGSRLIQRFNSTHRILDVRNFIVQSRPEFAALDFILVTSFPNKELTDESLTLLEADILNTVLLQQLK', 'comments': set(['chromosome_NCBI35_8_59486474_59526607_1 gene_ENSG00000172659 transcript_ENST00000331398 Oldphy_#Hsa0028724#']), 'external': {'Ensembl.v59': ['ENSG00000215114', 'ENSP00000382507', 'ENST00000399598'], 'Swiss-Prot.2010.09': ['Q14CS0']}, 'seq_leng': 331, 'protein': set(['ENSP00000327891']), 'copy': 1L}, 'Phy000692N_DANRE': {'gene': set(['ENSDARG00000041144']), 'seq': 'QVEIVVRLWKNGFTLNDEDLRSYTQEENQEFLEAIKKGELPLELEGRAEDEELEVNVEDMKDEVYVPKKKIFHPFTGRGYRLGRKVMLAVLKPVTSLQIWLADGRRTQRFNLCHRISDVQRFVEQAQITDTPFILTTSLPFRELTDEAQSLEEADLANAVIVQRPVNTHAPFGHS', 'comments': set(['chromosome_ZFISH5_22_37796510_37803631_-1 gene_ENSDARG00000041144 transcript_ENSDART00000060309 Oldphy_#Dre0012174#']), 'external': {}, 'seq_leng': 175, 'protein': set(['ENSDARP00000060308']), 'copy': 1L}}

msf_2 = {'Phy000CWXJ_YEAST': {'gene': set([]), 'seq': 'MEMTLFLNESYIFHRLRMWSIVLWHSCVFVCAECGNANYRVPRCLIKPFSVPVTFPFSVKKNIRILDLDPRTEAYCLSPYSVCSKRLPCKKYFYLLNSYNIKRVLGVVYC', 'comments': set(['YIR040C YIR040C SGDID_S000001479 Chr IX from 433717-433385, reverse complement, Dubious ORF, _Dubious open reading frame unlikely to encode a protein, based on experimental and comparative sequence data_']), 'external': {'Ensembl.v59': ['YIR040C'], 'Swiss-Prot.2010.09': ['P40584']}, 'seq_leng': 110, 'protein': set(['YIR040C']), 'copy': 1L}, 'Phy000CXBC_YEAST': {'gene': set([]), 'seq': 'MEMLLFLNESYIFHRLRMWSIVLWHSCVFVCAECGNANYRVPRCLIKPFSVPVTFPFSVKKNIRILDLDPRTEAYC', 'comments': set(['YGL260W YGL260W SGDID_S000003229 Chr VII from 6860-7090, Uncharacterized ORF, _Putative protein of unknown function_ transcription is significantly increased in a NAP1 deletion background_ deletion mutant has increased accumulation of nickel and selenium_']), 'external': {'Ensembl.v59': ['YGL260W'], 'Swiss-Prot.2010.09': ['P53056']}, 'seq_leng': 76, 'protein': set(['YGL260W']), 'copy': 1L}, 'Phy000CVIE_YEAST': {'gene': set([]), 'seq': 'MPIIGVPRCLIKPFSVPVTFPFSVKKNIRILDLDPRTEAYCLSLNSVCFKRLPRRKYFHLLNSYNIKRVLGVVYC', 'comments': set(['YAL067W-A YAL067W-A SGDID_S000028593 Chr I from 2480-2707, Uncharacterized ORF, _Putative protein of unknown function_ identified by gene-trapping, microarray-based expression analysis, and genome-wide homology searching_']), 'external': {'Ensembl.v59': ['YAL067W-A'], 'Swiss-Prot.2010.09': ['Q8TGK6']}, 'seq_leng': 75, 'protein': set(['YAL067W-A']), 'copy': 1L}, 'Phy000CVLS_YEAST': {'gene': set([]), 'seq': 'MEMLLFLNESYIFHRFRMWSIVLWHSCVFVCAECGNAYYRGAGGCLEKPFCAPVKFPFSVKKNIRILDLDPRSEAYCLSHHLVCPKRFPCKATSLLLIPEG', 'comments': set(['YBL108W YBL108W SGDID_S000000204 Chr II from 8177-8482, Dubious ORF, _Dubious open reading frame unlikely to encode a protein, based on available experimental and comparative sequence data_']), 'external': {'Ensembl.v59': ['YBL108W'], 'Swiss-Prot.2010.09': ['P38161']}, 'seq_leng': 101, 'protein': set(['YBL108W']), 'copy': 1L}, 'Phy000CYBL_YEAST': {'gene': set([]), 'seq': 'MEMLLFLNESYIFHRLRMWSTVLWHSCVFVCVECENANYRVPRCLIKPFSVPVTFPFSVKKNIRILDLDPRTEAYCLSPYSVCSKRLPCKKYFYLLNSYNIKRVLGVVYC', 'comments': set(['YKL223W YKL223W SGDID_S000001706 Chr XI from 2390-2722, Dubious ORF, _Dubious open reading frame unlikely to encode a protein, based on available experimental and comparative sequence data_']), 'external': {'Ensembl.v59': ['YKL223W'], 'Swiss-Prot.2010.09': ['P36031']}, 'seq_leng': 110, 'protein': set(['YKL223W']), 'copy': 1L}, 'Phy000CY0I_YEAST': {'gene': set([]), 'seq': 'MPIIGVPRCLEKPFCAPAKFPFSVKKNIRILDLDPRTEAYCLSLNSVCSKRLPCKKYFYLLNSYNIKRVLGVVYC', 'comments': set(['YIL174W YIL174W SGDID_S000001436 Chr IX from 9469-9696, pseudogene, _Hypothetical protein_', 'YJL222W-A YJL222W-A SGDID_S000028663 Chr X from 9452-9679, Dubious ORF, _Dubious open reading frame unlikely to encode a protein, based on available experimental and comparative sequence data_']), 'external': {'Ensembl.v59': ['YJL222W-A'], 'Swiss-Prot.2010.09': ['P40437']}, 'seq_leng': 75, 'protein': set(['YJL222W-A', 'YIL174W']), 'copy': 2L}, 'Phy000CZQW_YEAST': {'gene': set([]), 'seq': 'MPIIGVPRCLENPFCAPAKFPLSVKKKIRI', 'comments': set(['YNR075C-A YNR075C-A SGDID_S000028706 Chr XIV from 781603-781511, reverse complement, Uncharacterized ORF, _Identified by gene-trapping, microarray-based expression analysis, and genome-wide homology searching_']), 'external': {'Ensembl.v59': ['YNR075C-A'], 'Swiss-Prot.2010.09': ['Q8TGJ2']}, 'seq_leng': 30, 'protein': set(['YNR075C-A']), 'copy': 1L}}

alg_1 = {'clean_alg': '>Phy0008NXA_KLULA\nMPNVVLSSRLTNNDSVFLQEWIKPSVRPYYLPEQRVTDLLEHDIISAFQTALNPAPQRFV\nRIVKFHRVNDYTVYATIRDSTALILCFVIGNVTLQFWNHRECKLWFDFPGLRMVPVLKIE\nKARMFDRDQISSNVQFEWVYDT\n\n>Phy0000EEO_ASHGO\nMPKVVLASRAHKADSIFLREWLVDAVVPALEAGVEIPALPPATATLSLEPTVIQNPKRFL\nRIVRFTRVHDFAVCAVARDAGCCILVFVIGNTSLLFYARSDAAAAFEVPALSTLPVLRVG\nDCAIFDQDQVESHRRFPLVSRY\n\n>Phy00045YQ_CANGA\nMPPFIPKSRSNAVESVYLHGWVRDMLLESKTSQNIIPRVDPDEASPLLSRRIYANRRHFV\nKITKFFQVHNYSVYASVKDSQHQILSFMIGDAKLGIMVVDELRHYFKIVSLDMIPYLIIN\nQAFILDYDQVEAFKMTPFVYQY\n\n>Phy000JOHZ_VANPO\nMPKIILPSNKSSVDSTYLQEWIDLIIDRNYDTGEVIPILDEYGFNSSVINLIIKKPYHFA\nKVTNFFNVVDYSVYASIRDRKFQVLSFLIGDCKLKFMTYWEIKELYDLSSISLYPVLSIN\nQARMFDWSQIKSFEKFDWIYNK\n\n>Phy000NR7A_SACCA\nMPRVILSSKLSQTDSIFLQPWIEGLLRESLQGNQQVPSLNEADLRPQCSPKVLTNHCHFT\nKVTKFFKINNYAISASIRDSRFQLLSLVIGDAAIIYKSRDQITTQFDFIISPLVPILQIN\nQASLFDGDQVQHLRSFPFVYST\n\n>Phy000NNS9_SACBA\n------------------------------------------------------------\n--------------------------MIIGDADLAYVTSTQALARFIRLSSETVPILIIN\nQATIFDIDQVGSLNNFPFVYKY\n\n>Phy000CWVX_YEAST\nMPKVILESHSKPTDSVFLQPWIKALIEDNSESGHVIPSLTKQDLAPHMSPTILTNPCHFA\nKITKFYNVCDYKVYASIRDSSHQILVMIIGDADLVYVTNSRAMSHFICLSNEIVPVLNVN\nQATIFDIDQVGSLSTFPFVYKY\n\n>Phy000NNS8_SACBA\nMPRVFLESNSRQVDSIFLQPWIKLLIDDNSESDHVIPALAQQDLAPHMCPQILTNPFHFA\nRITRFYNVCDYRVYASVRDSTHQILS----------------------------------\n----------------------\n\n', 'seqnumber': 8L, 'raw_alg': '>Phy0008NXA_KLULA\nMPNVVLSSRLTN-NDSVFLQEWIKPSVRPYYLKNEKTKFWPEQRELVTDLLEHDII----\n-ESAFQTALNPAPQRFVRIVKFHRVNDYTVYATIRDSTALILCYFTVDCVLDYETINNDR\nITLNTLNTLFVIGNVTLQFWNHRECKLWF-NQDFPGL----RM--VPVLKIEKARMFDRD\nQISSNVQFEWV-------------------YDTLHG\n\n>Phy0000EEO_ASHGO\nMPKVVLASRAHK-ADSIFLREWLVDAVVPALERSGACAPWAGVECFIPALPPATAT----\n--LSLEPTVIQNPKRFLRIVRFTRVHDFAVCAVARDAGCCILVEFTPHCVSNFERRYHQR\nITSSTVNSLFVIGNTSLLFYARSDAAAAF---EVPALMNGSST--LPVLRVGDCAIFDQD\nQVESHRRFPLVQEHPRFVQSLDMAMQGSVLSRYT--\n\n>Phy00045YQ_CANGA\nMPPFIPKSRSNA-VESVYLHGWVRDMLLESKT--------SQNIAVIPRVDPDEAS----\n-IPLLSRRIYANRRHFVKITKFFQVHNYSVYASVKDSQHQILSQFTPKCVSEFESRNRSR\nITSDTVNTLFMIGDAKLGIMVVDELRHYF-GEKIVSLFNGLDMPYIPYLIINQAFILDYD\nQVEAFKMTPFV-------------------YQYI--\n\n>Phy000JOHZ_VANPO\nMPKIILPSNKSSCVDSTYLQEWIDLIIDRNYDN-------TGEV--IPILDEYGFNDSQS\nYMSSVINLIIKKPYHFAKVTNFFNVVDYSVYASIRDRKFQVLSEFTSNCVSSFERLYNSR\nITENTINCLFLIGDCKLKFMTYWEIKELY-KLDLSSICNKNSL--YPVLSINQARMFDWS\nQIKSFEKFDWI-------------------YNK---\n\n>Phy000NR7A_SACCA\nMPRVILSSKLSQ-TDSIFLQPWIEGLLRESLQKKTYLP--GNQQREVPSLNEADLR----\n-APQCSPKVLTNHCHFTKVTKFFKINNYAISASIRDSRFQLLSEFTPKCVSNFERRHHRR\nLTSETLNCLLVIGDAAIIYKSRDQITTQFGNIDFIISKNVSPL--VPILQINQASLFDGD\nQVQHLRSFPFV-------------------YSTL--\n\n>Phy000NNS9_SACBA\n------------------------------------------------------------\n------------------------------------------------------------\n---------MIIGDADLAYVTSTQALARF--MIRLSSISTSET--VPILIINQATIFDID\nQVGSLNNFPFV-------------------YKYL--\n\n>Phy000CWVX_YEAST\nMPKVILESHSKP-TDSVFLQPWIKALIEDNSEHDQYHP--SGHV--IPSLTKQDLA----\n-LPHMSPTILTNPCHFAKITKFYNVCDYKVYASIRDSSHQILVEFSQECVSNFERTHNCR\nITSETTNCLMIIGDADLVYVTNSRAMSHF--KICLSNISSKEI--VPVLNVNQATIFDID\nQVGSLSTFPFV-------------------YKYL--\n\n>Phy000NNS8_SACBA\nMPRVFLESNSRQ-VDSIFLQPWIKLLIDDNSEH-HHIP--SDHV--IPALAQQDLA----\n-LPHMCPQILTNPFHFARITRFYNVCDYRVYASVRDSTHQILS-----------------\n------------------------------------------------------------\n------------------------------------\n\n'}

alg_2 = {'clean_alg': '>Phy0007XAB_HUMAN\nRIGPSSAQPVAEASSLGLSGAGQMLHPNSSIGFQSVPVMPLSL\n\n>Phy000B82E_PANTR\nRIGPSSAQPVAEASSLGLSGAGQMLHPNSSIGFQSVPVMPLSL\n\n', 'seqnumber': 2L, 'raw_alg': '>Phy0007XAB_HUMAN\nRIGPSSAQPVAEASSLGLSGAGQMLHPNSSIGFQSVPVMPLSL\n\n>Phy000B82E_PANTR\nRIGPSSAQPVAEASSLGLSGAGQMLHPNSSIGFQSVPVMPLSL\n\n'}

phylome_1 = {'seed_species': 'Homo sapiens', 'name': 'Human phylome (1)', 'seed_taxid': 9606L, 'comments': 'Human phylome in the context of 38 eukaryotic species', 'seed_proteome': 'HUMAN.1', 'date': datetime.date(2007, 1, 6), 'seed_version': 1L, 'id': 1}

phylome_content_1 = [['3055', 'CHLRE', '1', 'Chlamydomonas reinhardtii', 'other', '2006-06-01'], ['3702', 'ARATH', '1', 'Arabidopsis thaliana', 'integr8', '2006-06-01'], ['4896', 'SCHPO', '1', 'Schizosaccharomyces pombe', 'integr8', '2006-06-01'], ['4932', 'YEAST', '1', 'Saccharomyces cerevisiae', 'ensembl', '2006-06-01'], ['4952', 'YARLI', '1', 'Yarrowia lipolytica', 'integr8', '2006-06-01'], ['4959', 'DEBHA', '1', 'Debaryomyces hansenii', 'integr8', '2006-06-01'], ['5141', 'NEUCR', '1', 'Neurospora crassa', 'other', '2006-06-01'], ['5207', 'CRYNE', '1', 'Cryptococcus neoformans', 'integr8', '2006-06-01'], ['5476', 'CANAL', '1', 'Candida albicans', 'other', '2006-06-01'], ['5478', 'CANGA', '1', 'Candida glabrata', 'integr8', '2006-06-01'], ['5518', 'GIBZE', '1', 'Gibberella zeae', 'integr8', '2006-06-01'], ['5664', 'LEIMA', '1', 'Leishmania major', 'integr8', '2006-06-01'], ['5833', 'PLAFA', '1', 'Plasmodium falciparum', 'integr8', '2006-06-01'], ['5888', 'PARTE', '1', 'Paramecium tetraurelia', 'integr8', '2006-06-01'], ['6035', 'ENCCU', '1', 'Encephalitozoon cuniculi', 'integr8', '2006-06-01'], ['6238', 'CAEBR', '1', 'Caenorhabditis briggsae', 'integr8', '2006-06-01'], ['6239', 'CAEEL', '1', 'Caenorhabditis elegans', 'ensembl', '2006-06-01'], ['7165', 'ANOGA', '1', 'Anopheles gambiae', 'ensembl', '2006-06-01'], ['7227', 'DROME', '1', 'Drosophila melanogaster', 'ensembl', '2006-06-01'], ['7460', 'APIME', '1', 'Apis mellifera', 'ensembl', '2006-06-01'], ['7719', 'CIOIN', '1', 'Ciona intestinalis', 'ensembl', '2006-06-01'], ['7955', 'DANRE', '1', 'Danio rerio', 'ensembl', '2006-06-01'], ['8364', 'XENTR', '1', 'Xenopus tropicalis', 'ensembl', '2006-06-01'], ['9031', 'CHICK', '1', 'Gallus gallus', 'ensembl', '2006-06-01'], ['9544', 'MACMU', '1', 'Macaca mulatta', 'ensembl', '2006-06-01'], ['9598', 'PANTR', '1', 'Pan troglodytes', 'ensembl', '2006-06-01'], ['9606', 'HUMAN', '1', 'Homo sapiens', 'ensembl', '2006-06-01'], ['9615', 'CANFA', '1', 'Canis familiaris', 'ensembl', '2006-06-01'], ['9913', 'BOVIN', '1', 'Bos taurus', 'ensembl', '2006-06-01'], ['10090', 'MOUSE', '1', 'Mus musculus', 'ensembl', '2006-06-01'], ['10116', 'RAT', '1', 'Rattus norvegicus', 'ensembl', '2006-06-01'], ['13616', 'MONDO', '1', 'Monodelphis domestica', 'ensembl', '2006-06-01'], ['28985', 'KLULA', '1', 'Kluyveromyces lactis', 'integr8', '2006-06-01'], ['31033', 'TAKRU', '1', 'Takifugu rubripes', 'ensembl', '2006-06-01'], ['44689', 'DICDI', '1', 'Dictyostelium discoideum', 'integr8', '2006-06-01'], ['55529', 'GUITH', '1', 'Guillardia theta', 'integr8', '2006-06-01'], ['73239', 'PLAYO', '1', 'Plasmodium yoelii yoelii', 'integr8', '2006-06-01'], ['99883', 'TETNG', '1', 'Tetraodon nigroviridis', 'ensembl', '2006-06-01'], ['284811', 'ASHGO', '1', 'Ashbya gossypii ATCC 10895', 'integr8', '2006-06-01']]

sequence_1 = {'name': {'HUMAN.2': set(['A2A2L1_HUMAN']), 'HUMAN.3': set(['ENST00000350991', 'ENST00000381658']), 'HUMAN.1': set(['ENSP00000202584'])}, 'seq': 'MTKMKMRRKRKARGAKEHGAVAVERVTKSPGETSKPRPFAGGGYRLGAAPEEESAYVAGEKRQHSSQDVHVVLKLWKSGFSLDNGELRSYQDPSNAQFLESIRRGEVPAELRRLAHGGQVNLDMEDHRDEDFVKPKGAFKAFTGEGQKLGSTAPQVLSTSSPAQQAENEAKASSSILIDESEPTTNIQIRLADGGRLVQKFNHSHRISDIRLFIVDARPAMAATSFILMTTFPNKELADESQTLKEANLLNAVIVQRLT', 'copy_number': 2L, 'comments': {'HUMAN.2': set(['NSFL1 _P97_ cofactor _P47_ - Homo sapiens _Human_']), 'HUMAN.1': set(['chromosome_NCBI35_20_1370811_1396417_-1 gene_ENSG00000088833 transcript_ENST00000350991 CCDS13017.1 Oldphy_#Hsa0018650#'])}, 'taxid': 9606L, 'protid': 'Phy0008BO2_HUMAN', 'external': {'Ensembl.v59': ['ENSP00000202584', 'ENSP00000371074', 'ENST00000350991', 'ENST00000381658'], 'TrEMBL.2010.09': ['A2A2L1']}, 'gene': {'HUMAN.3': set(['ENSG00000088833']), 'HUMAN.1': set(['ENSG00000088833'])}, 'isoforms': {'Phy0026IBT_HUMAN': 372L, 'Phy0008BO2_HUMAN': 259L, 'Phy0008BO3_HUMAN': 370L}, 'species': 'Homo sapiens', 'proteome': set(['HUMAN.2', 'HUMAN.3', 'HUMAN.1'])}

sequence_2 = {'name': {'YEAST.3': set(['YA067_YEAST']), 'YEAST.2': set(['YAL067W-A']), 'YEAST.1': set(['YAL067W-A'])}, 'seq': 'MPIIGVPRCLIKPFSVPVTFPFSVKKNIRILDLDPRTEAYCLSLNSVCFKRLPRRKYFHLLNSYNIKRVLGVVYC', 'copy_number': 1L, 'comments': {'YEAST.3': set(['Putative UPF0377 family protein YAL067W-A - Saccharomyces cerevisiae _Baker_s yeast_']), 'YEAST.2': set(['YAL067W-A YAL067W-A SGDID_S000028593 Chr I from 2480-2707, Uncharacterized ORF, _Putative protein of unknown function_ identified by gene-trapping, microarray-based expression analysis, and genome-wide homology searching_']), 'YEAST.1': set(['chromosome_SGD1_I_2480_2707_1 gene_YAL067W-A transcript_YAL067W-A Oldphy_#Sce0000004#'])}, 'taxid': 4932L, 'protid': 'Phy000CVIE_YEAST', 'external': {'Ensembl.v59': ['YAL067W-A'], 'Swiss-Prot.2010.09': ['Q8TGK6']}, 'gene': {'YEAST.1': set(['YAL067W-A'])}, 'isoforms': {'Phy000CVIE_YEAST': 75L}, 'species': 'Saccharomyces cerevisiae', 'proteome': set(['YEAST.3', 'YEAST.2', 'YEAST.1'])}

range_1 = ({'Phy0008052_HUMAN': {'algs': 0, 'copy_number': 1L, 'seq_length': 413L, 'trees': 0, 'prot_name': set(['ENSP00000354829']), 'gene_name': set(['ENSG00000198964']), 'comments': set(['chromosome_NCBI35_10_51735352_52053743_-1 gene_ENSG00000198964 transcript_ENST00000361781 CCDS7240.1 Oldphy_#Hsa0003710#'])}, 'Phy0008051_HUMAN': {'algs': 2, 'copy_number': 1L, 'seq_length': 419L, 'trees': 4, 'prot_name': set(['ENSP00000355235']), 'gene_name': set(['ENSG00000198964']), 'comments': set(['chromosome_NCBI35_10_51735352_52053743_-1 gene_ENSG00000198964 transcript_ENST00000361543 Oldphy_#Hsa0003709#'])}, 'Phy0008CHE_HUMAN': {'algs': 2, 'copy_number': 1L, 'seq_length': 51L, 'trees': 4, 'prot_name': set(['ENSP00000355389']), 'gene_name': set(['ENSG00000198966']), 'comments': set(['chromosome_NCBI35_21_29488348_29488767_1 gene_ENSG00000198966 transcript_ENST00000361202 Oldphy_#Hsa0019706#'])}, 'Phy0007Z06_HUMAN': {'algs': 2, 'copy_number': 1L, 'seq_length': 313L, 'trees': 4, 'prot_name': set(['ENSP00000354707']), 'gene_name': set(['ENSG00000198967']), 'comments': set(['chromosome_NCBI35_1_155389302_155390243_1 gene_ENSG00000198967 transcript_ENST00000361284 Oldphy_#Hsa0002238#'])}, 'Phy0007Z01_HUMAN': {'algs': 2, 'copy_number': 1L, 'seq_length': 324L, 'trees': 4, 'prot_name': set(['ENSP00000354706']), 'gene_name': set(['ENSG00000198965']), 'comments': set(['chromosome_NCBI35_1_155262774_155263748_1 gene_ENSG00000198965 transcript_ENST00000362060 Oldphy_#Hsa0002233#'])}}, 32010)
### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****

### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
class TestPhylomeDB3Connector(unittest.TestCase):

  def setUp(self):
    """ Prepare the object for the test. In this case, a db object is created
    """
    self.connection = PhylomeDB3Connector(host, dbase, user, pasw, port)

  def test_get_conversion_ids(self):
    """ TREES: Make sure that the conversion between old and current phylomeDB
        codes is working well
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


  def test_check_parameters(self):
    """ OTHER: Make sure all input parameters are valid for the API functions
    """

    ## Normal Cases
    self.assertEqual(self.connection.check_input_parameter(str_number = 7, \
      single_id = "Phy0007XA1_HUMAN"), True)

    self.assertEqual(self.connection.check_input_parameter(str_number = 7, \
      list_id = "Phy0007XA1_HUMAN"), True)

    self.assertEqual(self.connection.check_input_parameter(code = "test_api", \
      list_id = ["Phy0007XA1_HUMAN", "Phy0129129"]), True)

    self.assertEqual(self.connection.check_input_parameter(code = "test_api", \
      single_id = ["Phy0007XA1_HUMAN", "Phy0129129"]), False)

    self.assertEqual(self.connection.check_input_parameter(code = "test_api", \
      string = None), True)

    self.assertEqual(self.connection.check_input_parameter(code = "test_api", \
      boolean = None), False)

    self.assertEqual(self.connection.check_input_parameter(boolean = True), True)

    self.assertEqual(self.connection.check_input_parameter(string = []), False)

    ## Non-compatible cases
    self.assertRaises(NameError, self.connection.check_input_parameter, \
      bool = True)


  def test_parser_ids(self):
    """ TREES: Make sure that ids are being well-parsed
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
    """ TREES: Check the API is recovering correctly the longest isoforms for
        each protid
    """

    ## Normal Cases
    value = "Phy0008BO2"
    expected = {'HUMAN': {1: ['Phy0008BO3_HUMAN'], 2: ['Phy0008BO2_HUMAN'],
                3: ['Phy0026IBT_HUMAN']}}
    self.assertEqual(self.connection.get_longest_isoform(value), expected)

    value = "Phy0008B01_HUMAN"
    expected = {'HUMAN': {1: ['Phy0008AZZ_HUMAN'], 3: ['Phy002498Q_HUMAN']}}
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
    """ TREES: Make sure that search_id function is working well. Critical
        function for the API
    """

    ## Normal Cases
    value = "Phy0008B02"
    expected = {'HUMAN': {1: ['Phy0008B02_HUMAN'], 2: ['Phy0008B02_HUMAN'],
                3: ['Phy0008B02_HUMAN']}}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "Phy00085K5_HUMAN"
    expected = {'HUMAN': {1: ['Phy00085K5_HUMAN']}}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "hola"
    expected = searched_1
    self.assertEqual(self.connection.search_id(value), expected)

    value = "YBL058W"
    expected = {'YEAST': {1: ['Phy000CVNF_YEAST'], 2: ['Phy000CVNF_YEAST'],
                3: ['Phy000CVNF_YEAST']}}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "Sce0000029"
    expected = {'YEAST': {1: ['Phy000CVJ3_YEAST'], 2: ['Phy000CVJ3_YEAST'],
                3: ['Phy000CVJ3_YEAST']}}
    self.assertEqual(self.connection.search_id(value), expected)

    value = "Hsa1"
    expected = {'HUMAN': {1: ['Phy0007XA1_HUMAN']}}
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
    """ TREES: Check if the conversion between external db ids and internal
        phylomeDB ids is working properly
    """

    ## Normal Cases
    value = "YBL058W"
    expected = {'YEAST': {1: ['Phy000CVNF_YEAST'], 2: ['Phy000CVNF_YEAST'],
                3: ['Phy000CVNF_YEAST']}}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "ENSACAP00000000001"
    expected = {'ANOCA': {1: ['Phy002IKCU_ANOCA']}}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "O00084"
    expected = {'SCHPO': {1: ['Phy000D234_SCHPO'], 2: ['Phy000D234_SCHPO']}}
    # {1L: 'Phy000D234_SCHPO', 2L: 'Phy000D234_SCHPO'}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "F01D5.1"
    expected = {'CAEEL': {1: ['Phy00033LN_CAEEL'], 2: ['Phy00033LN_CAEEL'],
                3: ['Phy00033LN_CAEEL'], 4: ['Phy00033LN_CAEEL']}}
    self.assertEqual(self.connection.get_id_by_external(value), expected)

    value = "ACYPI001241-PA"
    expected = {'ACYPI': {1L: ['Phy000XPAO_ACYPI']}}
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
    """ TREES: Check if the conversion between internal phylomeDB ids and
        external ones is working well
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


  def test_collateral_trees(self):
    """ TREES: Make sure API is getting the collateral trees for all the cases
    """

    ## Normal Cases
    value, expected = 'Phy0008BO2', (('Phy000CVNF_YEAST', 19L),)
    self.assertEqual(self.connection.get_collateral_seeds(value), expected)

    value = 'Phy000XPAO_ACYPI'
    expected = (('Phy0000JH1_APIME', 29), ('Phy000YCXA_NASVI', 27), \
               ('Phy000Z43T_TRICA', 26), ('Phy000XPLZ_ACYPI', 16))
    self.assertEqual(self.connection.get_collateral_seeds(value), expected)

    value, expected = 'Phy002IKCU_ANOCA', tuple()
    self.assertEqual(self.connection.get_collateral_seeds(value), expected)

    value, expected = ["Phy0008B02", "Phy0008B03"], tuple()
    self.assertEqual(self.connection.get_collateral_seeds(value), expected)

    value = ["Phy00043J2", "Phy0008NDH"]
    expected = (('Phy000HL76_CANGA', 6),  ('Phy000D0FT_YEAST', 19),
                ('Phy000D0FT_YEAST', 3),  ('Phy000D0FT_YEAST', 5),
                ('Phy000D0FT_YEAST', 7),  ('Phy0000C20_ASHGO', 10),
                ('Phy0018F8T_ECOL5', 18), ('Phy0002N75_CANAL', 23),
                ('Phy000CX32_YEAST', 19), ('Phy000CX32_YEAST', 3),
                ('Phy000CX32_YEAST', 5),  ('Phy000CX32_YEAST', 7),
                ('Phy0000CNT_ASHGO', 10), ('Phy0008NDH_KLULA', 24),
                ('Phy0008LZ7_KLULA', 24), ('Phy00043J2_CANGA', 6))
    self.assertEqual(self.connection.get_collateral_seeds(value), expected)


    ## Unexpected cases
    value = "Phy0008B02 Phy0008B03"
    self.assertRaises(NameError, self.connection.get_collateral_seeds, value)

    value = "O00084"
    self.assertRaises(NameError, self.connection.get_collateral_seeds, value)

    ## Empty/non-compatible data cases
    self.assertRaises(NameError, self.connection.get_collateral_seeds, None)
    self.assertRaises(NameError, self.connection.get_collateral_seeds, "")
    self.assertRaises(NameError, self.connection.get_collateral_seeds, [])
    self.assertRaises(NameError, self.connection.get_collateral_seeds, {})
    self.assertRaises(NameError, self.connection.get_collateral_seeds, ())


  def test_get_trees(self):
    """ TREES: Check if the phylogenetic trees are being recorevy with normality
    """

    ## Normal Cases
    val_1, val_2, val_3 = "Phy0008BO2", 1, None
    expected = {}
    self.assertEqual(self.connection.get_tree(val_1, val_2, val_3), expected)

    val_1, val_2, val_3 = "Phy0008BO3_HUMAN", 1, None
    expected = tree_1

    returned = self.connection.get_tree(val_1, val_2, val_3)
    for method in returned:
      returned[method]["tree"] = returned[method]["tree"].write()
    self.assertEqual(returned, expected)

    val_1, val_2, val_3 = "Phy0008BO3_HUMAN", 1, "NJ"
    expected = {}
    self.assertEqual(self.connection.get_tree(val_1, val_2, val_3), expected)

    val_1, val_2, val_3 = "Phy000CVIE", 7, "WAG"
    expected = {}
    expected.setdefault("WAG", tree_2["WAG"])

    returned = self.connection.get_tree(val_1, val_2, val_3)
    for method in returned:
      returned[method]["tree"] = returned[method]["tree"].write()
    self.assertEqual(returned, expected)

    ## Unexpected cases
    val_1, val_2, val_3 = "Phy000CVIE", "-1", "WAG"
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))

    val_1, val_2, val_3 = "Phy000CVIE", None, "WAG"
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))

    val_1, val_2, val_3 = "Phy000CVIE Phy000CVIE", "7", "WAG"
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))

    ## Empty/non-compatible cases
    val_1, val_2, val_3 = None, None, None
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))

    val_1, val_2, val_3 = [], "1", None
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))

    val_1, val_2, val_3 = {}, 1, None
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))

    val_1, val_2, val_3 = ["Phy0008BO3"], 1, "Blosum62"
    self.assertRaises(NameError, self.connection.get_tree, *(val_1, val_2, val_3))


  def test_get_available_trees(self):
    """ TREES: Test if the API is returning correctly the associated
        information, in terms of available trees, to a given protein identifier.
    """

    ## Normal Cases
    value_1, value_2 = "Phy0008BO3_HUMAN", False
    expected = {1: [[True, 'Phy0008BO3_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']]]}
    self.assertEqual(self.connection.get_available_trees_by_phylome(value_1, \
      value_2), expected)

    value_1, value_2 = "Phy0008BO3_HUMAN", True
    expected = tree_entry_1
    self.assertEqual(self.connection.get_available_trees_by_phylome(value_1, \
      value_2), expected)

    value_1, value_2 = ["Phy0008BO3_HUMAN", "Phy0008BO2"], True
    expected = tree_entry_1
    self.assertEqual(self.connection.get_available_trees_by_phylome(value_1, \
      value_2), expected)

    value_1, value_2 = "Phy0008BO2", True
    expected = {19: [[False, 'Phy000CVNF_YEAST', ['JTT', 'NJ', 'RtREV', 'VT']]]}
    self.assertEqual(self.connection.get_available_trees_by_phylome(value_1, \
      value_2), expected)

    value_1, value_2 = "Phy0008BO1", False
    expected = {}
    self.assertEqual(self.connection.get_available_trees_by_phylome(value_1, \
      value_2), expected)

    ## Unexpected cases
    value_1, value_2 = "0008BO2", False
    self.assertRaises(NameError, self.connection.get_available_trees_by_phylome,
      *(value_1, value_2))

    value_1, value_2 = "Phy0008BO2", None
    self.assertRaises(NameError, self.connection.get_available_trees_by_phylome,
      *(value_1, value_2))

    ## Empty/non-compatible values
    value_1, value_2 = None, None
    self.assertRaises(NameError, self.connection.get_available_trees_by_phylome,
      *(value_1, value_2))

    value_1, value_2 = [], None
    self.assertRaises(NameError, self.connection.get_available_trees_by_phylome,
      *(value_1, value_2))

    value_1, value_2 = "", False
    self.assertRaises(NameError, self.connection.get_available_trees_by_phylome,
      *(value_1, value_2))


  def test_get_info_in_tree(self):
    """ TREES: Make sure that the API is able to recover and return together all
        the information associated to a given seed protein in a given phylome.
    """

    ## Normal Cases
    val_1, val_2, val_3 = "Phy0008BO2", 1, None
    expected = {}
    self.assertEqual(self.connection.get_seq_info_in_tree(val_1, val_2, val_3),\
      expected)

    val_1, val_2, val_3 = "Phy0008BO3_HUMAN", 1, None
    returned = self.connection.get_seq_info_in_tree(val_1, val_2, val_3)
    returned["tree"]["tree"] = returned["tree"]["tree"].write()
    self.assertEqual(returned, complete_tree_1)

    val_1, val_2, val_3 = "Phy000CVIE", 7, None
    returned = self.connection.get_seq_info_in_tree(val_1, val_2, val_3)
    returned["tree"]["tree"] = returned["tree"]["tree"].write()
    self.assertEqual(returned, complete_tree_2)

    val_1, val_2, val_3 = "Phy000CVIE", 7, "WAG"
    returned = self.connection.get_seq_info_in_tree(val_1, val_2, val_3)
    returned["tree"]["tree"] = returned["tree"]["tree"].write()
    self.assertEqual(returned, complete_tree_3)

    ## Unexpected cases
    val_1, val_2, val_3 = "0008BO2", -1, False
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    val_1, val_2, val_3 = "Phy0008BO2", 10, False
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    val_1, val_2, val_3 = "Phy0008BO2 Phy0008BO2", 10, None
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    val_1, val_2, val_3 = ["Phy0008BO3", "Phy0008BO3_HUMAN"], 10, None
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    ## Empty/non-compatible cases
    val_1, val_2, val_3 = [], -1, False
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    val_1, val_2, val_3 = "", -1, False
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    val_1, val_2, val_3 = None, -1, False
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))

    val_1, val_2, val_3 = "Phy0000001", None, False
    self.assertRaises(NameError, self.connection.get_seq_info_in_tree, *(val_1,\
      val_2, val_3))


  def test_count_trees(self):
    """ TREES: Get how many trees are per phylome
    """

    ## Normal Cases
    value = 1
    expected = {'WAG': 19578, 'JTT': 19585, 'Blosum62': 19578, 'VT': 19577}
    self.assertEqual(self.connection.count_trees(value), expected)

    value = "7"
    expected = {'WAG': 5719,'JTT': 5719,'Blosum62': 5719,'VT': 5719,'NJ': 5719}
    self.assertEqual(self.connection.count_trees(value), expected)

    value = "2"
    expected = {}
    self.assertEqual(self.connection.count_trees(value), expected)

    ## Unexpected cases
    value = -3
    self.assertRaises(NameError, self.connection.count_trees, value)

    value = "Four"
    self.assertRaises(NameError, self.connection.count_trees, value)

    # Other illegal cases
    self.assertRaises(NameError, self.connection.count_trees, [])
    self.assertRaises(NameError, self.connection.count_trees, None)


  def test_get_trees_in_phylome(self):
    """ TREES: Get all the available trees for a given phylome
    """

    ## Normal Cases
    #~ The normal cases are not performed in order of avoiding to recover big
    #~ data sets.
    #~ value = 7
    #~ expected = {}
    #~ self.assertEqual(self.connection.get_phylome_trees(value), expected)

    ## Unexpected cases
    value = -3
    self.assertRaises(NameError, self.connection.get_phylome_trees, value)

    value = "Four"
    self.assertRaises(NameError, self.connection.get_phylome_trees, value)

    # Other illegal cases
    self.assertRaises(NameError, self.connection.get_phylome_trees, [])
    self.assertRaises(NameError, self.connection.get_phylome_trees, None)


  def test_get_msf_info(self):
    """ MSF:   Get all available information for the homologs sequence of a
        given seed protein in a given phylome
    """

    ## Normal Cases
    val_1, val_2 = "Phy0008BO2", 1
    expected = {}
    self.assertEqual(self.connection.get_seq_info_msf(val_1, val_2), expected)

    val_1, val_2 = "Phy0008BO3_HUMAN", 1
    expected = msf_1
    self.assertEqual(self.connection.get_seq_info_msf(val_1, val_2), expected)

    val_1, val_2 = "Phy000CVIE", 7
    expected = msf_2
    self.assertEqual(self.connection.get_seq_info_msf(val_1, val_2), expected)

    ## Unexpected cases
    val_1, val_2 = "0008BO2", -1
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *(val_1, \
      val_2))

    val_1, val_2 = "Phy0008BO2", -1
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *(val_1, \
      val_2))

    val_1, val_2 = "Phy0008BO2 Phy0008BO2", 10
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *(val_1, \
      val_2))

    val_1, val_2 = "Phy0008BO2", None
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *(val_1, \
      val_2))

    val_1, val_2 = ["Phy0008BO3", "Phy0008BO3_HUMAN"], 1
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *(val_1, \
      val_2))

    ## Empty/non-compatible cases
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *([], 10))
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *(None, 10))
    self.assertRaises(NameError, self.connection.get_seq_info_msf, *("", 1))


  def test_get_algs(self):
    """ ALGS:  Check if the are being recovery with normality
    """

    ## Normal Cases
    value_1, value_2 = "Phy000CWVX", 7
    expected = alg_1
    self.assertEqual(self.connection.get_algs(value_1, value_2), expected)

    expected = alg_1["raw_alg"]
    self.assertEqual(self.connection.get_raw_alg(value_1, value_2), expected)

    expected = alg_1["clean_alg"]
    self.assertEqual(self.connection.get_clean_alg(value_1, value_2), expected)

    value_1, value_2 = "Phy0007XAB_HUMAN", 1
    expected = alg_2
    self.assertEqual(self.connection.get_algs(value_1, value_2), expected)

    expected = alg_2["raw_alg"]
    self.assertEqual(self.connection.get_raw_alg(value_1, value_2), expected)

    expected = alg_2["clean_alg"]
    self.assertEqual(self.connection.get_clean_alg(value_1, value_2), expected)

    value_1, value_2 = "Phy000CWVX", 1
    expected = {}
    self.assertEqual(self.connection.get_algs(value_1, value_2), expected)

    expected = ""
    self.assertEqual(self.connection.get_raw_alg(value_1, value_2), expected)

    expected = ""
    self.assertEqual(self.connection.get_clean_alg(value_1, value_2), expected)

    ## Unexpected cases
    value_1, value_2 = "BxtTTUASAS", 1
    self.assertRaises(NameError, self.connection.get_algs, *(value_1, value_2))

    self.assertRaises(NameError, self.connection.get_raw_alg, *(value_1, \
      value_2))

    self.assertRaises(NameError, self.connection.get_clean_alg, *(value_1, \
      value_2))

    value_1, value_2 = "Phy0007XAB Phy0008BO2", 1
    self.assertRaises(NameError, self.connection.get_algs, *(value_1, value_2))

    self.assertRaises(NameError, self.connection.get_raw_alg, *(value_1, \
      value_2))

    self.assertRaises(NameError, self.connection.get_clean_alg, *(value_1, \
      value_2))

    value_1, value_2 = ["Phy0007XAB", "Phy0008BO2"], 1
    self.assertRaises(NameError, self.connection.get_algs, *(value_1, value_2))

    self.assertRaises(NameError, self.connection.get_raw_alg, *(value_1, \
      value_2))

    self.assertRaises(NameError, self.connection.get_clean_alg, *(value_1, \
      value_2))

    ## Empty/non-compatible cases
    value_1, value_2, = None, None
    self.assertRaises(NameError, self.connection.get_algs, *(value_1, value_2))

    self.assertRaises(NameError, self.connection.get_raw_alg, *(value_1, \
      value_2))

    self.assertRaises(NameError, self.connection.get_clean_alg, *(value_1, \
      value_2))

    value_1, value_2, = None, []
    self.assertRaises(NameError, self.connection.get_algs, *(value_1, value_2))

    self.assertRaises(NameError, self.connection.get_raw_alg, *(value_1, \
      value_2))

    self.assertRaises(NameError, self.connection.get_clean_alg, *(value_1, \
      value_2))

    value_1, value_2, = "Phy0008BO3", None
    self.assertRaises(NameError, self.connection.get_algs, *(value_1, value_2))

    self.assertRaises(NameError, self.connection.get_raw_alg, *(value_1, \
      value_2))

    self.assertRaises(NameError, self.connection.get_clean_alg, *(value_1, \
      value_2))


  def test_count_algs(self):
    """ ALGS:  Get how many alignments are per phylome
    """

    ## Normal Cases
    value, expected = 1, 20355
    self.assertEqual(self.connection.count_algs(value), expected)

    value, expected = "7", 5906
    self.assertEqual(self.connection.count_algs(value), expected)

    value, expected = "2", 0
    self.assertEqual(self.connection.count_algs(value), expected)

    ## Unexpected cases
    value = -3
    self.assertRaises(NameError, self.connection.count_algs, value)

    value = "Four"
    self.assertRaises(NameError, self.connection.count_algs, value)

    # Other illegal cases
    self.assertRaises(NameError, self.connection.count_algs, [])
    self.assertRaises(NameError, self.connection.count_algs, None)


  def test_get_algs_in_phylome(self):
    """ ALGS:  Get all the available alignments for a given phylome
    """

    ## Normal Cases
    #~ The normal cases are not performed in order of avoiding to recover big
    #~ data sets.
    #~ value = 7
    #~ expected = {}
    #~ self.assertEqual(self.connection.get_phylome_algs(value), expected)

    ## Unexpected cases
    value = -3
    self.assertRaises(NameError, self.connection.get_phylome_algs, value)

    value = "Four"
    self.assertRaises(NameError, self.connection.get_phylome_algs, value)

    # Other illegal cases
    self.assertRaises(NameError, self.connection.get_phylome_algs, [])
    self.assertRaises(NameError, self.connection.get_phylome_algs, None)


  def test_species_in_db(self):
    """ INFO:  Recover information about the species in the database
    """

    ## Normal Cases
    ## Impossible to test his function since the result depends on the current
    ## state of the database
    #~ expected = {}
    #~ self.assertEqual(self.connection.get_species(), expected)

    expected = {'code': 'HUMAN', 'taxid': 9606L, 'name': 'Homo sapiens'}
    self.assertEqual(self.connection.get_species_info(taxid = 9606), expected)

    expected = {'code': 'HUMAN', 'taxid': 9606L, 'name': 'Homo sapiens'}
    self.assertEqual(self.connection.get_species_info(code = "HUMAN"), expected)

    expected = {}
    self.assertEqual(self.connection.get_species_info(code = "HUMAN", taxid = \
      1292), expected)

    ## Unexpected cases
    self.assertRaises(NameError, self.connection.get_species_info, taxid = \
      "YEAST")

    self.assertRaises(NameError, self.connection.get_species_info, code = \
      "My species")

    self.assertRaises(NameError, self.connection.get_species_info, code = -3)

    self.assertRaises(NameError, self.connection.get_species_info, code = [])

    self.assertRaises(NameError, self.connection.get_species_info, code = None,\
      taxid = None)


  def test_genomes_in_db(self):
    """ INFO:  Recover information about the proteomes/genomes in the database
    """

    ## Normal Cases
    ## Impossible to test his function since the result depends on the current
    ## state of the database
    #~ expected = {}
    #~ self.assertEqual(self.connection.get_genomes(), expected)

    expected = {'taxid': 9606L, 'comments': '-', 'source': 'ensembl',
                'version': 3L, 'date': None, 'genome_id': 'HUMAN.3',
                'species': 'Homo sapiens'}
    self.assertEqual(self.connection.get_genome_info("HUMAN.3"), expected)

    expected = {}
    self.assertEqual(self.connection.get_genome_info("HUMAN.18"), expected)

    expected = {4932L: [1L, 2L, 3L]}
    self.assertEqual(self.connection.get_genomes_by_species(4932), expected)

    expected = {}
    self.assertEqual(self.connection.get_genomes_by_species(4878887), expected)

    ## Unexpected cases
    self.assertRaises(NameError, self.connection.get_genome_info, \
      "My.Test.Species")

    self.assertRaises(NameError, self.connection.get_genome_info, \
      "My Test.Species")

    self.assertRaises(NameError, self.connection.get_genomes_by_species, \
      "AnotherTest")

    self.assertRaises(NameError, self.connection.get_genomes_by_species, "Four")

    ## Non-valid cases
    self.assertRaises(NameError, self.connection.get_genome_info, [])

    self.assertRaises(NameError, self.connection.get_genome_info, "")

    self.assertRaises(NameError, self.connection.get_genomes_by_species, None)

    self.assertRaises(NameError, self.connection.get_genomes_by_species, -787)


  def test_phylomes_in_db(self):
    """ INFO:  Recover information about the phylomes in the database
    """

    ## Normal Cases
    ## Impossible to test his function since the result depends on the current
    ## state of the database
    #~ expected = {}
    #~ self.assertEqual(self.connection.get_phylomes(), expected)

    expected = phylome_1
    self.assertEqual(self.connection.get_phylome_info(1), expected)

    expected = {}
    self.assertEqual(self.connection.get_phylome_info(1200201), expected)

    expected = phylome_content_1
    self.assertEqual(self.connection.get_proteomes_in_phylome(1), expected)

    expected = []
    self.assertEqual(self.connection.get_proteomes_in_phylome(154547), expected)

    ## Unexpected cases
    self.assertRaises(NameError, self.connection.get_phylome_info, -1)

    self.assertRaises(NameError, self.connection.get_phylome_info, "Four")

    self.assertRaises(NameError, self.connection.get_proteomes_in_phylome, -781)

    self.assertRaises(NameError, self.connection.get_proteomes_in_phylome, "On")

    ## Non-valid cases
    self.assertRaises(NameError, self.connection.get_phylome_info, None)

    self.assertRaises(NameError, self.connection.get_phylome_info, [])

    self.assertRaises(NameError, self.connection.get_proteomes_in_phylome, "")

    self.assertRaises(NameError, self.connection.get_proteomes_in_phylome, None)


  def test_get_sequence_info(self):
    """ INFO:  Recover information about a specific sequence
    """

    ## Normal Cases
    value, expected = "Phy0008BO2_HUMAN", sequence_1
    self.assertEqual(self.connection.get_seqid_info(value), expected)

    expected = {'Phy0026IBT_HUMAN': 372L, 'Phy0008BO2_HUMAN': 259L,
                'Phy0008BO3_HUMAN': 370L}
    self.assertEqual(self.connection.get_all_isoforms(value), expected)

    value, expected = "Phy000CVIE", sequence_2
    self.assertEqual(self.connection.get_seqid_info(value), expected)

    expected = {'Phy000CVIE_YEAST': 75L}
    self.assertEqual(self.connection.get_all_isoforms(value), expected)

    value, expected = "Phy100CVIE", {}
    self.assertEqual(self.connection.get_seqid_info(value), expected)

    self.assertEqual(self.connection.get_all_isoforms(value), expected)

    ## Unexpected cases
    self.assertRaises(NameError, self.connection.get_seqid_info, "Ccs929291")

    self.assertRaises(NameError, self.connection.get_all_isoforms, "Ccs929291")

    self.assertRaises(NameError, self.connection.get_seqid_info, \
      "Phy000CVIE Phy0000129")

    self.assertRaises(NameError, self.connection.get_all_isoforms, \
      "Phy000CVIE Phy0000129")

    self.assertRaises(NameError, self.connection.get_seqid_info, ["Phy000CVIE",\
      "Phy0008BO3_HUMAN"])

    self.assertRaises(NameError, self.connection.get_all_isoforms, \
      ["Phy000CVIE", "Phy0008BO3_HUMAN"])

    ## Non-valid cases
    self.assertRaises(NameError, self.connection.get_seqid_info, "")

    self.assertRaises(NameError, self.connection.get_all_isoforms, "")

    self.assertRaises(NameError, self.connection.get_seqid_info, [])

    self.assertRaises(NameError, self.connection.get_all_isoforms, [])

    self.assertRaises(NameError, self.connection.get_seqid_info, None)

    self.assertRaises(NameError, self.connection.get_all_isoforms, None)

    self.assertRaises(NameError, self.connection.get_seqid_info, 82102)

    self.assertRaises(NameError, self.connection.get_all_isoforms, 8201222)

  def test_get_cross_reference_info(self):
    """ INFO:  Recover information for the resources associated to a phylome
    """

    ## Normal Cases
    ## It is not feasible to test this function since it generates the complete
    ## proteome for a given taxid species and proteome version
    #~ taxid, version = 9606, 1
    #~ self.connection.get_seqs_in_genome(taxid, version)
    #~ self.connection.get_seqs_in_genome(taxid, version, False)

    val_1, val_2, val_3, expected = 1, 0, 5, range_1
    self.assertEqual(self.connection.get_seed_ids_in_phylome(val_1, val_2, \
      val_3), expected)

    value = ["Phy000CVIE", "Phy0008BO3_HUMAN"]
    expected = {'Phy000CVIE_YEAST': [(3L, 'Yeast phylome (P60)'),
                (4L, 'Yeast phylome (T12b)'), (5L, 'Yeast phylome (P21)'),
                (7L, 'Yeast phylome (T12a)')],
                'Phy0008BO3_HUMAN': [(1L, 'Human phylome (1)')]}
    self.assertEqual(self.connection.get_phylomes_for_seed_ids(value), expected)

    ## It is not feasible to test this function since it generates the complete
    ## ids proteome for the input phylome
    #~ self.connection.get_seed_ids(1, filter_isoforms = True)

    ## Unexpected cases
    val_1, val_2, val_3 = 9606, 1, "True"
    self.assertRaises(NameError, self.connection.get_seqs_in_genome, *(val_1, \
      val_2, val_3))

    val_1, val_2, val_3 = 7, 1, "-"
    self.assertRaises(NameError, self.connection.get_seed_ids_in_phylome, \
      *(val_1, val_2, val_3))

    value = ["Ccs000C46E", "Xxz0008BO3_HUMAN"]
    self.assertRaises(NameError, self.connection.get_phylomes_for_seed_ids, \
      value)

    value = 9291291921
    self.assertRaises(NameError, self.connection.get_seed_ids, value)
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
