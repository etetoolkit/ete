#!/usr/bin/python
### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
import sys, getopt, os, unittest
from getpass import getpass

sys.path.append(os.path.join(os.getcwd(), "../ete2/phylomedb/"))
from phylomeDB3 import PhylomeDB3Connector

host, dbase, user, port, pasw = "", "", "", "", ""

### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****
tree_1 = {'WAG': {'tree': '(((((((Phy0004PJ7_CRYNE:0.764739,Phy000EWDU_YARLI:0.796761)0.867000:0.138011,(Phy0007S7S_GIBZE:0.436611,Phy000AW9E_NEUCR:0.446933)0.999850:0.389361)0.731000:0.076737,(((((Phy00057S0_DICDI:0.560334,(Phy000B3RA_PLAFA:0.208866,Phy000C5A9_PLAYO:0.320387)0.999850:1.039263)0.872000:0.194674,((Phy0001H3K_ARATH:1.073939,(Phy00014K1_ARATH:0.041448,Phy00017N5_ARATH:0.010695)0.980000:0.237843)0.908000:0.152943,(Phy00015YL_ARATH:0.087938,Phy0001SFG_ARATH:0.169291)0.999000:0.305849)0.999850:0.469297)0.213000:0.048819,Phy0008TSZ_LEIMA:1.700022)0.490000:0.082001,(((((Phy00000DT_ANOGA:0.423273,Phy0005XAP_DROME:0.626117)0.909000:0.157770,Phy0000P6F_APIME:0.551249)0.842000:0.095758,Phy0005ZK6_DROME:1.369223)0.924000:0.130245,((((((((Phy000AACP_MACMU:0.005049,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.928000:0.011797,(Phy0003QBK_CANFA:0.004803,(Phy00022Q2_BOVIN:0.006368,(((Phy000CGZG_RAT:0.252911,Phy0009LMB_MOUSE:0.035141)0.365746:0.002195,Phy000A62H_MOUSE:0.003603)0.027000:0.000034,Phy000CLXL_RAT:0.001436)0.974000:0.016713)0.468000:0.006206)0.792000:0.008472)0.971000:0.037932,Phy00098SP_MONDO:0.052782)0.515000:0.023175,Phy0007DAU_CHICK:0.069170)0.988000:0.097265,(Phy0006CSG_DANRE:0.126699,(Phy000D9JL_TETNG:0.010249,Phy0006ZSN_TAKRU:0.073435)0.999850:0.198965)0.892000:0.066872)0.982000:0.123649,((((Phy000CO1I_RAT:0.026050,Phy000A35T_MOUSE:0.061791)0.999850:0.058648,((((Phy000ASI0_MACMU:0.011440,(Phy000BUTW_PANTR:0.018323,Phy0008J14_HUMAN:0.000000)0.999850:0.059770)0.460000:0.003619,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.770000:0.003106)0.982000:0.023214,Phy0003SSX_CANFA:0.016193)0.288000:0.012134,Phy0002BMQ_BOVIN:0.050012)0.625000:0.006330)0.968000:0.068411,Phy0008ZAA_MONDO:0.088010)0.974000:0.102663,Phy0007CQ6_CHICK:0.087112)0.999850:0.487832)0.972000:0.117309,Phy0004H5V_CIOIN:0.548974)0.524000:0.024198,((((((((Phy0008A3X_HUMAN:0.003726,Phy000AJXF_MACMU:0.015197)0.152528:0.000358,Phy000BD05_PANTR:0.008154)0.994000:0.052312,((Phy000A0DO_MOUSE:0.007421,Phy0009U78_MOUSE:0.040419)0.944000:0.024547,Phy000CPNE_RAT:0.016885)0.999850:0.076406)0.880000:0.019001,Phy0003L1L_CANFA:0.049133)0.847000:0.017766,Phy00029HZ_BOVIN:0.003484)0.962000:0.108542,Phy0009GEH_MONDO:0.533937)0.979000:0.228955,Phy0007FZD_CHICK:0.181892)0.979000:0.340482,(Phy0006QQY_TAKRU:0.273894,Phy000692N_DANRE:0.255238)0.976000:0.247235)0.999000:0.600529)0.898000:0.083309)0.812000:0.072951,(Phy00036IS_CAEEL:0.291792,Phy0002S9O_CAEBR:0.206941)0.999850:0.861829)0.953000:0.159395)0.983000:0.209727,Phy000D22G_SCHPO:0.982238)0.855000:0.106908)0.999850:0.369274,((Phy000CVNF_YEAST:0.400542,Phy000467C_CANGA:0.320157)0.633000:0.058488,(Phy0000F1K_ASHGO:0.403569,Phy0008N76_KLULA:0.388617)0.545000:0.086135)0.999000:0.275963)0.999850:0.363936,(Phy0005KKR_DEBHA:0.147391,Phy0005KKQ_DEBHA:0.087226)0.989000:0.180504)0.999000:0.218984,Phy0002JCH_CANAL:0.000000)0.974000:0.020314,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24451.799999999999}, 'JTT': {'tree': '(((((((Phy000D22G_SCHPO:0.998857,Phy0004PJ7_CRYNE:0.788235)0.486000:0.127258,((((Phy00057S0_DICDI:0.593594,(Phy000B3RA_PLAFA:0.234012,Phy000C5A9_PLAYO:0.356383)0.999850:1.184190)0.864000:0.213265,((Phy0001H3K_ARATH:1.163301,(Phy00014K1_ARATH:0.041030,Phy00017N5_ARATH:0.009697)0.977000:0.235741)0.899000:0.162192,(Phy00015YL_ARATH:0.086894,Phy0001SFG_ARATH:0.165512)0.999850:0.322508)0.999850:0.517152)0.501000:0.143990,(((((Phy00000DT_ANOGA:0.473443,Phy0005XAP_DROME:0.663322)0.896000:0.163476,Phy0000P6F_APIME:0.612124)0.735000:0.100547,Phy0005ZK6_DROME:1.521321)0.893000:0.132818,((Phy0004H5V_CIOIN:0.580561,((((((((Phy0008A3X_HUMAN:0.003951,Phy000AJXF_MACMU:0.015636)0.147017:0.000306,Phy000BD05_PANTR:0.008460)0.994000:0.055454,((Phy000A0DO_MOUSE:0.007711,Phy0009U78_MOUSE:0.041190)0.956000:0.025421,Phy000CPNE_RAT:0.016948)0.999000:0.080391)0.867000:0.018436,Phy0003L1L_CANFA:0.051270)0.859000:0.021096,Phy00029HZ_BOVIN:0.001801)0.943000:0.116294,Phy0009GEH_MONDO:0.559427)0.976000:0.242652,Phy0007FZD_CHICK:0.181770)0.973000:0.366340,(Phy0006QQY_TAKRU:0.282120,Phy000692N_DANRE:0.279568)0.969000:0.271678)0.999850:0.677672)0.378667:0.027348,((((((Phy0003QBK_CANFA:0.004923,(Phy00022Q2_BOVIN:0.006082,((Phy000A62H_MOUSE:0.003147,(Phy000CGZG_RAT:0.249021,Phy0009LMB_MOUSE:0.034391)0.423935:0.002235)0.110000:0.000812,Phy000CLXL_RAT:0.000993)0.972000:0.016475)0.413000:0.006090)0.793000:0.007811,(Phy000AACP_MACMU:0.004952,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.936000:0.011763)0.982000:0.037209,Phy00098SP_MONDO:0.051791)0.545000:0.023993,Phy0007DAU_CHICK:0.066820)0.987000:0.095218,(Phy0006CSG_DANRE:0.122531,(Phy000D9JL_TETNG:0.011419,Phy0006ZSN_TAKRU:0.072270)0.999850:0.198140)0.955000:0.077623)0.952000:0.115041,((((Phy000CO1I_RAT:0.025459,Phy000A35T_MOUSE:0.061831)0.998000:0.060550,((((Phy000ASI0_MACMU:0.011671,(Phy000BUTW_PANTR:0.018519,Phy0008J14_HUMAN:0.000000)0.999850:0.060536)0.246000:0.003415,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.753000:0.003169)0.982000:0.023453,Phy0003SSX_CANFA:0.016117)0.227000:0.011521,Phy0002BMQ_BOVIN:0.050716)0.291000:0.005696)0.974000:0.069531,Phy0008ZAA_MONDO:0.090519)0.967000:0.105266,Phy0007CQ6_CHICK:0.085692)0.999850:0.526413)0.971000:0.134615)0.873000:0.116707)0.681000:0.073578,(Phy00036IS_CAEEL:0.324714,Phy0002S9O_CAEBR:0.196466)0.999850:1.013328)0.939000:0.167803)0.015000:0.145597,Phy0008TSZ_LEIMA:1.936822)0.751000:0.160994)0.685000:0.107045,(Phy000EWDU_YARLI:0.926945,(Phy0007S7S_GIBZE:0.450888,Phy000AW9E_NEUCR:0.443056)0.999850:0.405269)0.258000:0.065433)0.999850:0.426765,((Phy000CVNF_YEAST:0.433504,Phy000467C_CANGA:0.328907)0.791000:0.077120,(Phy0000F1K_ASHGO:0.431968,Phy0008N76_KLULA:0.416001)0.534000:0.082005)0.997000:0.291294)0.999850:0.423195,(Phy0005KKR_DEBHA:0.158081,Phy0005KKQ_DEBHA:0.084606)0.985000:0.179583)0.997000:0.241633,Phy0002JCH_CANAL:0.000000)0.968000:0.020276,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24493.099999999999}, 'Blosum62': {'tree': '(((((((Phy0004PJ7_CRYNE:0.748069,Phy000EWDU_YARLI:0.774169)0.886000:0.130830,(Phy0007S7S_GIBZE:0.430663,Phy000AW9E_NEUCR:0.439396)0.999850:0.376435)0.838000:0.081726,(((((Phy00057S0_DICDI:0.545879,(Phy000B3RA_PLAFA:0.210477,Phy000C5A9_PLAYO:0.336658)0.999850:1.008064)0.882000:0.165750,((Phy0001H3K_ARATH:0.997109,(Phy00014K1_ARATH:0.041773,Phy00017N5_ARATH:0.011407)0.984000:0.250222)0.901000:0.145910,(Phy00015YL_ARATH:0.090015,Phy0001SFG_ARATH:0.175984)0.999850:0.290460)0.999850:0.416681)0.127000:0.055163,Phy0008TSZ_LEIMA:1.548281)0.570000:0.083687,(((((Phy00000DT_ANOGA:0.414017,Phy0005XAP_DROME:0.607783)0.884000:0.146314,Phy0000P6F_APIME:0.545686)0.754000:0.075701,Phy0005ZK6_DROME:1.254874)0.936000:0.136983,((((((((Phy000AACP_MACMU:0.005233,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.920000:0.011473,(Phy0003QBK_CANFA:0.004782,(Phy00022Q2_BOVIN:0.006726,((Phy000A62H_MOUSE:0.003269,(Phy000CGZG_RAT:0.258214,Phy0009LMB_MOUSE:0.034201)0.695617:0.004688)0.042000:0.000687,Phy000CLXL_RAT:0.001328)0.973000:0.017320)0.416000:0.006328)0.846000:0.009884)0.986000:0.039479,Phy00098SP_MONDO:0.054621)0.018000:0.020662,Phy0007DAU_CHICK:0.074659)0.990000:0.100070,(Phy0006CSG_DANRE:0.129331,(Phy000D9JL_TETNG:0.012534,Phy0006ZSN_TAKRU:0.073241)0.999850:0.201368)0.876000:0.065736)0.988000:0.130366,((((Phy000CO1I_RAT:0.027672,Phy000A35T_MOUSE:0.064005)0.999000:0.058797,((((Phy000ASI0_MACMU:0.011805,(Phy000BUTW_PANTR:0.019045,Phy0008J14_HUMAN:0.000000)0.999850:0.062794)0.396000:0.003808,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.766000:0.003199)0.974000:0.024241,Phy0003SSX_CANFA:0.016562)0.455000:0.012431,Phy0002BMQ_BOVIN:0.051413)0.738000:0.007884)0.974000:0.070722,Phy0008ZAA_MONDO:0.089106)0.971000:0.098997,Phy0007CQ6_CHICK:0.093972)0.999850:0.484601)0.973000:0.116038,Phy0004H5V_CIOIN:0.527687)0.332000:0.027795,((((((((Phy0008A3X_HUMAN:0.004050,Phy000AJXF_MACMU:0.015839)0.143625:0.000254,Phy000BD05_PANTR:0.008554)0.997000:0.054493,((Phy000A0DO_MOUSE:0.007577,Phy0009U78_MOUSE:0.043960)0.924000:0.023491,Phy000CPNE_RAT:0.018241)0.999850:0.078903)0.892000:0.021644,Phy0003L1L_CANFA:0.050957)0.696000:0.019458,Phy00029HZ_BOVIN:0.002106)0.972000:0.121611,Phy0009GEH_MONDO:0.521687)0.983000:0.221239,Phy0007FZD_CHICK:0.195348)0.984000:0.340177,(Phy0006QQY_TAKRU:0.276818,Phy000692N_DANRE:0.251518)0.977000:0.230645)0.999850:0.548967)0.912000:0.080761)0.821000:0.066559,(Phy00036IS_CAEEL:0.277003,Phy0002S9O_CAEBR:0.225597)0.999850:0.805706)0.952000:0.140788)0.987000:0.195004,Phy000D22G_SCHPO:0.919244)0.852000:0.095263)0.999850:0.339395,((Phy000CVNF_YEAST:0.397957,Phy000467C_CANGA:0.333970)0.589000:0.049233,(Phy0000F1K_ASHGO:0.403358,Phy0008N76_KLULA:0.382255)0.390000:0.090115)0.998000:0.277647)0.999000:0.336982,(Phy0005KKR_DEBHA:0.148256,Phy0005KKQ_DEBHA:0.092523)0.996000:0.192444)0.999000:0.207493,Phy0002JCH_CANAL:0.000000)0.983000:0.021586,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24777.5}, 'VT': {'tree': '(((((((Phy0004PJ7_CRYNE:0.844473,Phy000EWDU_YARLI:0.878349)0.820000:0.131753,(Phy0007S7S_GIBZE:0.466848,Phy000AW9E_NEUCR:0.485558)0.999850:0.422281)0.822000:0.096765,(((((Phy00057S0_DICDI:0.607213,(Phy000B3RA_PLAFA:0.242761,Phy000C5A9_PLAYO:0.366222)0.999850:1.234553)0.890000:0.212396,((Phy0001H3K_ARATH:1.169490,(Phy00014K1_ARATH:0.043357,Phy00017N5_ARATH:0.010597)0.973000:0.286896)0.858000:0.147276,(Phy00015YL_ARATH:0.087686,Phy0001SFG_ARATH:0.183279)0.999000:0.327561)0.999000:0.519295)0.861000:0.122802,(((((Phy00000DT_ANOGA:0.462429,Phy0005XAP_DROME:0.704665)0.890000:0.176542,Phy0000P6F_APIME:0.622938)0.816000:0.102155,Phy0005ZK6_DROME:1.552412)0.896000:0.112341,((Phy0004H5V_CIOIN:0.583775,((((((((Phy0008A3X_HUMAN:0.004169,Phy000AJXF_MACMU:0.016203)0.144247:0.000266,Phy000BD05_PANTR:0.008689)0.991000:0.056357,((Phy000A0DO_MOUSE:0.008431,Phy0009U78_MOUSE:0.043438)0.924000:0.024716,Phy000CPNE_RAT:0.018227)0.998000:0.083189)0.865000:0.022112,Phy0003L1L_CANFA:0.053513)0.840000:0.016655,Phy00029HZ_BOVIN:0.004918)0.954000:0.122528,Phy0009GEH_MONDO:0.562883)0.983000:0.249483,Phy0007FZD_CHICK:0.208065)0.984000:0.366035,(Phy0006QQY_TAKRU:0.292639,Phy000692N_DANRE:0.277838)0.972000:0.261608)0.998000:0.647437)0.170000:0.045274,((((((Phy0003QBK_CANFA:0.005031,(Phy00022Q2_BOVIN:0.006437,((Phy000A62H_MOUSE:0.003400,(Phy000CGZG_RAT:0.261587,Phy0009LMB_MOUSE:0.035335)0.640106:0.003730)0.026000:0.000554,Phy000CLXL_RAT:0.001281)0.976000:0.017328)0.428000:0.006332)0.842000:0.009254,(Phy000AACP_MACMU:0.005163,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.926000:0.011579)0.980000:0.039207,Phy00098SP_MONDO:0.055156)0.233000:0.021708,Phy0007DAU_CHICK:0.074253)0.985000:0.098874,(Phy0006CSG_DANRE:0.130505,(Phy000D9JL_TETNG:0.013533,Phy0006ZSN_TAKRU:0.074270)0.999850:0.210952)0.894000:0.070241)0.980000:0.129239,((((Phy000CO1I_RAT:0.026397,Phy000A35T_MOUSE:0.066389)0.993000:0.059532,((((Phy000ASI0_MACMU:0.011879,(Phy000BUTW_PANTR:0.019171,Phy0008J14_HUMAN:0.000000)0.999850:0.063156)0.214000:0.003704,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.767000:0.003217)0.975000:0.024725,Phy0003SSX_CANFA:0.016227)0.402000:0.012807,Phy0002BMQ_BOVIN:0.051587)0.801000:0.008826)0.975000:0.069040,Phy0008ZAA_MONDO:0.094586)0.980000:0.102888,Phy0007CQ6_CHICK:0.097018)0.999850:0.520684)0.945000:0.113379)0.858000:0.119633)0.801000:0.085029,(Phy00036IS_CAEEL:0.320920,Phy0002S9O_CAEBR:0.241136)0.999850:0.994632)0.940000:0.149164)0.218000:0.112628,Phy0008TSZ_LEIMA:1.926060)0.831000:0.119723,Phy000D22G_SCHPO:1.108053)0.903000:0.135897)0.998000:0.365699,((Phy000CVNF_YEAST:0.443713,Phy000467C_CANGA:0.354185)0.605000:0.062898,(Phy0000F1K_ASHGO:0.451066,Phy0008N76_KLULA:0.414468)0.841000:0.105805)0.996000:0.305732)0.999850:0.394010,(Phy0005KKR_DEBHA:0.166384,Phy0005KKQ_DEBHA:0.095165)0.997000:0.207078)0.997000:0.234664,Phy0002JCH_CANAL:0.000000)0.968000:0.022076,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);', 'lk': -24754.299999999999}}

tree_2 = {'WAG': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108966,(Phy000CVLS_YEAST:0.209734,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025782,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.964000:0.107553)0.648000:0.118969)0.756000:0.023454)0.125038:0.000000);', 'lk': -234.922}, 'JTT': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108342,(Phy000CVLS_YEAST:0.212821,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025083,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.950000:0.104729)0.620000:0.117294)0.693659:0.022298)0.125038:0.000000);', 'lk': -231.99600000000001}, 'Blosum62': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.109694,(Phy000CVLS_YEAST:0.207014,(Phy000CVIE_YEAST:0.000047,(Phy000CYBL_YEAST:0.025515,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.951000:0.106396)0.648000:0.117220)0.719000:0.023232)0.125038:0.000000);', 'lk': -238.006}, 'VT': {'tree': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.110159,(Phy000CVLS_YEAST:0.217995,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025534,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.960000:0.106863)0.491000:0.126230)0.566848:0.020087)0.125038:0.000000);', 'lk': -240.708}, 'NJ': {'tree': '(Phy000CZQW_YEAST:0.163164,Phy000CY0I_YEAST:0.000000,(Phy000CY0I_YEAST:0.000000,(Phy000CVLS_YEAST:0.141465,(Phy000CVIE_YEAST:0.029137,(Phy000CWXJ_YEAST:0.000000,(Phy000CXBC_YEAST:0.000000,Phy000CYBL_YEAST:0.026158)1.000000:0.001052)1.000000:0.076182)1.000000:0.090556)1.000000:0.118308)1.000000:0.032708);', 'lk': 0.0}}

tree_entry_1 = {1: [[True, 'Phy0008BO3_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']], [False, 'Phy0008JFW_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']], [False, 'Phy0008J14_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']], [False, 'Phy0008A3X_HUMAN', ['Blosum62', 'JTT', 'VT', 'WAG']]], 3: [[False, 'Phy000CVNF_YEAST', ['Blosum62', 'JTT', 'NJ', 'VT', 'WAG']]], 6: [[False, 'Phy000467C_CANGA', ['Blosum62', 'JTT', 'NJ', 'VT', 'WAG']]], 10: [[False, 'Phy0000F1K_ASHGO', ['Blosum62', 'JTT', 'VT', 'WAG']]], 16: [[False, 'Phy0010CMS_ACYPI', ['JTT', 'NJ']]], 19: [[False, 'Phy000CVNF_YEAST', ['JTT', 'NJ', 'RtREV', 'VT']]], 22: [[False, 'Phy000V3G9_SCHMA', ['Blosum62', 'JTT', 'VT', 'WAG']]], 23: [[False, 'Phy0002JCG_CANAL', ['Blosum62', 'JTT', 'NJ', 'VT', 'WAG']]]}

complete_tree_1 = {'tree': {'lk': -24451.799999999999, 'method': 'WAG', 'best': True, 'newick': '(((((((Phy0004PJ7_CRYNE:0.764739,Phy000EWDU_YARLI:0.796761)0.867000:0.138011,(Phy0007S7S_GIBZE:0.436611,Phy000AW9E_NEUCR:0.446933)0.999850:0.389361)0.731000:0.076737,(((((Phy00057S0_DICDI:0.560334,(Phy000B3RA_PLAFA:0.208866,Phy000C5A9_PLAYO:0.320387)0.999850:1.039263)0.872000:0.194674,((Phy0001H3K_ARATH:1.073939,(Phy00014K1_ARATH:0.041448,Phy00017N5_ARATH:0.010695)0.980000:0.237843)0.908000:0.152943,(Phy00015YL_ARATH:0.087938,Phy0001SFG_ARATH:0.169291)0.999000:0.305849)0.999850:0.469297)0.213000:0.048819,Phy0008TSZ_LEIMA:1.700022)0.490000:0.082001,(((((Phy00000DT_ANOGA:0.423273,Phy0005XAP_DROME:0.626117)0.909000:0.157770,Phy0000P6F_APIME:0.551249)0.842000:0.095758,Phy0005ZK6_DROME:1.369223)0.924000:0.130245,((((((((Phy000AACP_MACMU:0.005049,(Phy000BO0I_PANTR:0.000000,Phy0008BO3_HUMAN:0.000000)0.125038:0.000000)0.928000:0.011797,(Phy0003QBK_CANFA:0.004803,(Phy00022Q2_BOVIN:0.006368,(((Phy000CGZG_RAT:0.252911,Phy0009LMB_MOUSE:0.035141)0.365746:0.002195,Phy000A62H_MOUSE:0.003603)0.027000:0.000034,Phy000CLXL_RAT:0.001436)0.974000:0.016713)0.468000:0.006206)0.792000:0.008472)0.971000:0.037932,Phy00098SP_MONDO:0.052782)0.515000:0.023175,Phy0007DAU_CHICK:0.069170)0.988000:0.097265,(Phy0006CSG_DANRE:0.126699,(Phy000D9JL_TETNG:0.010249,Phy0006ZSN_TAKRU:0.073435)0.999850:0.198965)0.892000:0.066872)0.982000:0.123649,((((Phy000CO1I_RAT:0.026050,Phy000A35T_MOUSE:0.061791)0.999850:0.058648,((((Phy000ASI0_MACMU:0.011440,(Phy000BUTW_PANTR:0.018323,Phy0008J14_HUMAN:0.000000)0.999850:0.059770)0.460000:0.003619,(Phy0008JFW_HUMAN:0.000000,Phy000BVFY_PANTR:0.000000)0.770000:0.003106)0.982000:0.023214,Phy0003SSX_CANFA:0.016193)0.288000:0.012134,Phy0002BMQ_BOVIN:0.050012)0.625000:0.006330)0.968000:0.068411,Phy0008ZAA_MONDO:0.088010)0.974000:0.102663,Phy0007CQ6_CHICK:0.087112)0.999850:0.487832)0.972000:0.117309,Phy0004H5V_CIOIN:0.548974)0.524000:0.024198,((((((((Phy0008A3X_HUMAN:0.003726,Phy000AJXF_MACMU:0.015197)0.152528:0.000358,Phy000BD05_PANTR:0.008154)0.994000:0.052312,((Phy000A0DO_MOUSE:0.007421,Phy0009U78_MOUSE:0.040419)0.944000:0.024547,Phy000CPNE_RAT:0.016885)0.999850:0.076406)0.880000:0.019001,Phy0003L1L_CANFA:0.049133)0.847000:0.017766,Phy00029HZ_BOVIN:0.003484)0.962000:0.108542,Phy0009GEH_MONDO:0.533937)0.979000:0.228955,Phy0007FZD_CHICK:0.181892)0.979000:0.340482,(Phy0006QQY_TAKRU:0.273894,Phy000692N_DANRE:0.255238)0.976000:0.247235)0.999000:0.600529)0.898000:0.083309)0.812000:0.072951,(Phy00036IS_CAEEL:0.291792,Phy0002S9O_CAEBR:0.206941)0.999850:0.861829)0.953000:0.159395)0.983000:0.209727,Phy000D22G_SCHPO:0.982238)0.855000:0.106908)0.999850:0.369274,((Phy000CVNF_YEAST:0.400542,Phy000467C_CANGA:0.320157)0.633000:0.058488,(Phy0000F1K_ASHGO:0.403569,Phy0008N76_KLULA:0.388617)0.545000:0.086135)0.999000:0.275963)0.999850:0.363936,(Phy0005KKR_DEBHA:0.147391,Phy0005KKQ_DEBHA:0.087226)0.989000:0.180504)0.999000:0.218984,Phy0002JCH_CANAL:0.000000)0.974000:0.020314,Phy0002JCG_CANAL:0.000000,Phy0002JCJ_CANAL:0.000000);'}, 'seq': {'Phy000ASI0_MACMU': {'collateral': 4L, 'copy': 1L, 'taxid': 9544L, 'trees': 0L, 'proteome': 'MACMU.1', 'sps_name': 'Macaca mulatta', 'gene': 'ENSMMUG00000001100', 'species': 'MACMU', 'protein': 'ENSMMUP00000001465', 'external': {}}, 'Phy00029HZ_BOVIN': {'collateral': 4L, 'copy': 1L, 'taxid': 9913L, 'trees': 0L, 'proteome': 'BOVIN.1', 'sps_name': 'Bos taurus', 'gene': 'ENSBTAG00000002033', 'species': 'BOVIN', 'protein': 'ENSBTAP00000002634', 'external': {'Ensembl.v59': ['ENSBTAG00000002033', 'ENSBTAP00000002634', 'ENSBTAT00000002634']}}, 'Phy0002BMQ_BOVIN': {'collateral': 4L, 'copy': 1L, 'taxid': 9913L, 'trees': 0L, 'proteome': 'BOVIN.1', 'sps_name': 'Bos taurus', 'gene': 'ENSBTAG00000009138', 'species': 'BOVIN', 'protein': 'ENSBTAP00000012043', 'external': {}}, 'Phy0000F1K_ASHGO': {'collateral': 12L, 'copy': 1L, 'taxid': 284811L, 'trees': 4L, 'proteome': 'ASHGO.1', 'sps_name': 'Ashbya gossypii ATCC 10895', 'gene': '', 'species': 'ASHGO', 'protein': 'Q75D11', 'external': {}}, 'Phy000467C_CANGA': {'collateral': 11L, 'copy': 1L, 'taxid': 5478L, 'trees': 5L, 'proteome': 'CANGA.1', 'sps_name': 'Candida glabrata', 'gene': '', 'species': 'CANGA', 'protein': 'Q6FXT3', 'external': {'TrEMBL.2010.09': ['Q6FXT3']}}, 'Phy000A62H_MOUSE': {'collateral': 5L, 'copy': 1L, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': 'ENSMUSG00000027455', 'species': 'MOUSE', 'protein': 'ENSMUSP00000028949', 'external': {'TrEMBL.2010.09': ['Q3UVN5']}}, 'Phy00000DT_ANOGA': {'collateral': 5L, 'copy': 1L, 'taxid': 7165L, 'trees': 0L, 'proteome': 'ANOGA.1', 'sps_name': 'Anopheles gambiae', 'gene': 'ENSANGG00000007495', 'species': 'ANOGA', 'protein': 'ENSANGP00000009984', 'external': {}}, 'Phy000D22G_SCHPO': {'collateral': 10L, 'copy': 1L, 'taxid': 4896L, 'trees': 0L, 'proteome': 'SCHPO.1', 'sps_name': 'Schizosaccharomyces pombe', 'gene': '', 'species': 'SCHPO', 'protein': 'Q9UT81', 'external': {'Swiss-Prot.2010.09': ['Q9UT81']}}, 'Phy0008BO3_HUMAN': {'collateral': 10L, 'copy': 1L, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': 'ENSG00000088833', 'species': 'HUMAN', 'protein': 'ENSP00000216879', 'external': {'Ensembl.v59': ['ENSG00000088833', 'ENSP00000216879', 'ENST00000216879'], 'TrEMBL.2010.09': ['Q53FE8', 'Q53FF5'], 'Swiss-Prot.2010.09': ['Q9UNZ2']}}, 'Phy0007S7S_GIBZE': {'collateral': 9L, 'copy': 1L, 'taxid': 5518L, 'trees': 0L, 'proteome': 'GIBZE.1', 'sps_name': 'Gibberella zeae', 'gene': '', 'species': 'GIBZE', 'protein': 'Q4IA94', 'external': {}}, 'Phy0002S9O_CAEBR': {'collateral': 5L, 'copy': 1L, 'taxid': 6238L, 'trees': 0L, 'proteome': 'CAEBR.1', 'sps_name': 'Caenorhabditis briggsae', 'gene': '', 'species': 'CAEBR', 'protein': 'Q61A62', 'external': {}}, 'Phy00014K1_ARATH': {'collateral': 22L, 'copy': 1L, 'taxid': 3702L, 'trees': 0L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': '', 'species': 'ARATH', 'protein': 'O23394', 'external': {}}, 'Phy000A35T_MOUSE': {'collateral': 5L, 'copy': 1L, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': 'ENSMUSG00000028243', 'species': 'MOUSE', 'protein': 'ENSMUSP00000029907', 'external': {'Ensembl.v59': ['ENSMUSG00000028243', 'ENSMUSP00000029907', 'ENSMUST00000029907'], 'Swiss-Prot.2010.09': ['Q0KL01']}}, 'Phy00015YL_ARATH': {'collateral': 14L, 'copy': 1L, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': '', 'species': 'ARATH', 'protein': 'O81456', 'external': {'TrEMBL.2010.09': ['O81456']}}, 'Phy000AJXF_MACMU': {'collateral': 4L, 'copy': 1L, 'taxid': 9544L, 'trees': 0L, 'proteome': 'MACMU.1', 'sps_name': 'Macaca mulatta', 'gene': 'ENSMMUG00000006487', 'species': 'MACMU', 'protein': 'ENSMMUP00000008545', 'external': {}}, 'Phy000C5A9_PLAYO': {'collateral': 4L, 'copy': 1L, 'taxid': 73239L, 'trees': 0L, 'proteome': 'PLAYO.1', 'sps_name': 'Plasmodium yoelii yoelii', 'gene': '', 'species': 'PLAYO', 'protein': 'Q7RNC9', 'external': {'TrEMBL.2010.09': ['Q7RNC9']}}, 'Phy0008A3X_HUMAN': {'collateral': 15L, 'copy': 1L, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': 'ENSG00000173960', 'species': 'HUMAN', 'protein': 'ENSP00000312107', 'external': {'Ensembl.v59': ['ENSP00000312107', 'ENSP00000385525', 'ENST00000309033', 'ENST00000404924'], 'Swiss-Prot.2010.09': ['P68543']}}, 'Phy000AW9E_NEUCR': {'collateral': 11L, 'copy': 1L, 'taxid': 5141L, 'trees': 0L, 'proteome': 'NEUCR.1', 'sps_name': 'Neurospora crassa', 'gene': '', 'species': 'NEUCR', 'protein': '(NCU01100.2)', 'external': {'TrEMBL.2010.09': ['Q8X0G7']}}, 'Phy0005XAP_DROME': {'collateral': 14L, 'copy': 1L, 'taxid': 7227L, 'trees': 4L, 'proteome': 'DROME.1', 'sps_name': 'Drosophila melanogaster', 'gene': 'CG11139', 'species': 'DROME', 'protein': 'CG11139-PA', 'external': {'Ensembl.v59': ['FBgn0033179', 'FBpp0088069', 'FBtr0088997'], 'TrEMBL.2010.09': ['Q7K3Z3']}}, 'Phy0009GEH_MONDO': {'collateral': 4L, 'copy': 1L, 'taxid': 13616L, 'trees': 0L, 'proteome': 'MONDO.1', 'sps_name': 'Monodelphis domestica', 'gene': 'ENSMODG00000002133', 'species': 'MONDO', 'protein': 'ENSMODP00000002593', 'external': {}}, 'Phy0006CSG_DANRE': {'collateral': 5L, 'copy': 1L, 'taxid': 7955L, 'trees': 0L, 'proteome': 'DANRE.1', 'sps_name': 'Danio rerio', 'gene': 'ENSDARG00000006375', 'species': 'DANRE', 'protein': 'ENSDARP00000026327', 'external': {}}, 'Phy0009LMB_MOUSE': {'collateral': 5L, 'copy': 1L, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': 'ENSMUSG00000039833', 'species': 'MOUSE', 'protein': 'ENSMUSP00000041730', 'external': {}}, 'Phy00022Q2_BOVIN': {'collateral': 5L, 'copy': 1L, 'taxid': 9913L, 'trees': 0L, 'proteome': 'BOVIN.1', 'sps_name': 'Bos taurus', 'gene': 'ENSBTAG00000006533', 'species': 'BOVIN', 'protein': 'ENSBTAP00000008580', 'external': {'Swiss-Prot.2010.09': ['Q3SZC4']}}, 'Phy0009U78_MOUSE': {'collateral': 5L, 'copy': 1L, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': 'ENSMUSG00000050416', 'species': 'MOUSE', 'protein': 'ENSMUSP00000058557', 'external': {}}, 'Phy000CGZG_RAT': {'collateral': 4L, 'copy': 1L, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': 'ENSRNOG00000022378', 'species': 'RAT', 'protein': 'ENSRNOP00000034835', 'external': {}}, 'Phy0007CQ6_CHICK': {'collateral': 4L, 'copy': 1L, 'taxid': 9031L, 'trees': 0L, 'proteome': 'CHICK.1', 'sps_name': 'Gallus gallus', 'gene': 'ENSGALG00000015431', 'species': 'CHICK', 'protein': 'ENSGALP00000024843', 'external': {'Ensembl.v59': ['ENSGALG00000015431', 'ENSGALP00000035955', 'ENSGALT00000036743']}}, 'Phy000CVNF_YEAST': {'collateral': 13L, 'copy': 1L, 'taxid': 4932L, 'trees': 6L, 'proteome': 'YEAST.1', 'sps_name': 'Saccharomyces cerevisiae', 'gene': 'YBL058W', 'species': 'YEAST', 'protein': 'YBL058W', 'external': {'Ensembl.v59': ['YBL058W'], 'TrEMBL.2010.09': ['Q6Q5U0'], 'Swiss-Prot.2010.09': ['P34223']}}, 'Phy0008N76_KLULA': {'collateral': 11L, 'copy': 1L, 'taxid': 28985L, 'trees': 3L, 'proteome': 'KLULA.1', 'sps_name': 'Kluyveromyces lactis', 'gene': '', 'species': 'KLULA', 'protein': 'Q6CMI1', 'external': {'TrEMBL.2010.09': ['Q6CMI1']}}, 'Phy0003SSX_CANFA': {'collateral': 4L, 'copy': 1L, 'taxid': 9615L, 'trees': 0L, 'proteome': 'CANFA.1', 'sps_name': 'Canis familiaris', 'gene': 'ENSCAFG00000007088', 'species': 'CANFA', 'protein': 'ENSCAFP00000010519', 'external': {'Ensembl.v59': ['ENSCAFG00000007088', 'ENSCAFP00000010519', 'ENSCAFT00000011356']}}, 'Phy000D9JL_TETNG': {'collateral': 5L, 'copy': 1L, 'taxid': 99883L, 'trees': 0L, 'proteome': 'TETNG.1', 'sps_name': 'Tetraodon nigroviridis', 'gene': 'GSTENG00003875001', 'species': 'TETNG', 'protein': 'GSTENP00003875001', 'external': {'TrEMBL.2010.09': ['Q4TB74']}}, 'Phy0003QBK_CANFA': {'collateral': 4L, 'copy': 1L, 'taxid': 9615L, 'trees': 0L, 'proteome': 'CANFA.1', 'sps_name': 'Canis familiaris', 'gene': 'ENSCAFG00000006789', 'species': 'CANFA', 'protein': 'ENSCAFP00000010130', 'external': {'Ensembl.v59': ['ENSCAFP00000010130', 'ENSCAFT00000010930']}}, 'Phy000BO0I_PANTR': {'collateral': 4L, 'copy': 1L, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': 'ENSPTRG00000013164', 'species': 'PANTR', 'protein': 'ENSPTRP00000022532', 'external': {'Ensembl.v59': ['ENSPTRP00000052472', 'ENSPTRT00000059341']}}, 'Phy00017N5_ARATH': {'collateral': 13L, 'copy': 1L, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': '', 'species': 'ARATH', 'protein': 'Q7Y175', 'external': {'Swiss-Prot.2010.09': ['Q7Y175']}}, 'Phy0007DAU_CHICK': {'collateral': 4L, 'copy': 1L, 'taxid': 9031L, 'trees': 0L, 'proteome': 'CHICK.1', 'sps_name': 'Gallus gallus', 'gene': 'ENSGALG00000006182', 'species': 'CHICK', 'protein': 'ENSGALP00000009964', 'external': {}}, 'Phy000B3RA_PLAFA': {'collateral': 8L, 'copy': 1L, 'taxid': 5833L, 'trees': 0L, 'proteome': 'PLAFA.1', 'sps_name': 'Plasmodium falciparum', 'gene': '', 'species': 'PLAFA', 'protein': 'Q8IAS1', 'external': {}}, 'Phy0005ZK6_DROME': {'collateral': 13L, 'copy': 1L, 'taxid': 7227L, 'trees': 0L, 'proteome': 'DROME.1', 'sps_name': 'Drosophila melanogaster', 'gene': 'CG4556', 'species': 'DROME', 'protein': 'CG4556-PA', 'external': {'Ensembl.v59': ['FBgn0259729', 'FBpp0289272', 'FBtr0299995'], 'TrEMBL.2010.09': ['Q8T4C3', 'Q9U9C9', 'Q9W175']}}, 'Phy000BD05_PANTR': {'collateral': 4L, 'copy': 1L, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': 'ENSPTRG00000011705', 'species': 'PANTR', 'protein': 'ENSPTRP00000020106', 'external': {'Ensembl.v59': ['ENSPTRG00000011705', 'ENSPTRP00000020106', 'ENSPTRT00000021798']}}, 'Phy0005KKQ_DEBHA': {'collateral': 10L, 'copy': 1L, 'taxid': 4959L, 'trees': 0L, 'proteome': 'DEBHA.1', 'sps_name': 'Debaryomyces hansenii', 'gene': '', 'species': 'DEBHA', 'protein': 'Q6BYR9', 'external': {}}, 'Phy00036IS_CAEEL': {'collateral': 12L, 'copy': 1L, 'taxid': 6239L, 'trees': 0L, 'proteome': 'CAEEL.1', 'sps_name': 'Caenorhabditis elegans', 'gene': 'Y94H6A.9', 'species': 'CAEEL', 'protein': 'Y94H6A.9a', 'external': {'Ensembl.v59': ['Y94H6A.9a'], 'TrEMBL.2010.09': ['Q9N2W5']}}, 'Phy0008J14_HUMAN': {'collateral': 9L, 'copy': 1L, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': 'ENSG00000178166', 'species': 'HUMAN', 'protein': 'ENSP00000319187', 'external': {}}, 'Phy0002JCG_CANAL': {'collateral': 11L, 'copy': 1L, 'taxid': 5476L, 'trees': 5L, 'proteome': 'CANAL.1', 'sps_name': 'Candida albicans', 'gene': '', 'species': 'CANAL', 'protein': 'orf19.2549', 'external': {}}, 'Phy0002JCJ_CANAL': {'collateral': 1L, 'copy': 1L, 'taxid': 5476L, 'trees': 0L, 'proteome': 'CANAL.1', 'sps_name': 'Candida albicans', 'gene': '', 'species': 'CANAL', 'protein': 'orf19.2550', 'external': {'TrEMBL.2010.09': ['Q5A9B5']}}, 'Phy0004H5V_CIOIN': {'collateral': 6L, 'copy': 1L, 'taxid': 7719L, 'trees': 0L, 'proteome': 'CIOIN.1', 'sps_name': 'Ciona intestinalis', 'gene': 'ENSCING00000001500', 'species': 'CIOIN', 'protein': 'ENSCINP00000002962', 'external': {}}, 'Phy000CO1I_RAT': {'collateral': 4L, 'copy': 1L, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': 'ENSRNOG00000009137', 'species': 'RAT', 'protein': 'ENSRNOP00000012551', 'external': {'Ensembl.v59': ['ENSRNOG00000009137', 'ENSRNOP00000012551', 'ENSRNOT00000012551'], 'Swiss-Prot.2010.09': ['P0C627']}}, 'Phy000BVFY_PANTR': {'collateral': 4L, 'copy': 1L, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': 'ENSPTRG00000020274', 'species': 'PANTR', 'protein': 'ENSPTRP00000034710', 'external': {'Ensembl.v59': ['ENSPTRG00000033886', 'ENSPTRP00000055380', 'ENSPTRT00000063836']}}, 'Phy0007FZD_CHICK': {'collateral': 4L, 'copy': 1L, 'taxid': 9031L, 'trees': 0L, 'proteome': 'CHICK.1', 'sps_name': 'Gallus gallus', 'gene': 'ENSGALG00000016497', 'species': 'CHICK', 'protein': 'ENSGALP00000026563', 'external': {'Ensembl.v59': ['ENSGALG00000016497', 'ENSGALP00000026563', 'ENSGALT00000026614'], 'TrEMBL.2010.09': ['Q5ZKL4']}}, 'Phy0006ZSN_TAKRU': {'collateral': 4L, 'copy': 1L, 'taxid': 31033L, 'trees': 0L, 'proteome': 'TAKRU.1', 'sps_name': 'Takifugu rubripes', 'gene': 'NEWSINFRUG00000121537', 'species': 'TAKRU', 'protein': 'NEWSINFRUP00000128304', 'external': {}}, 'Phy0008ZAA_MONDO': {'collateral': 4L, 'copy': 1L, 'taxid': 13616L, 'trees': 0L, 'proteome': 'MONDO.1', 'sps_name': 'Monodelphis domestica', 'gene': 'ENSMODG00000008866', 'species': 'MONDO', 'protein': 'ENSMODP00000011040', 'external': {'Ensembl.v59': ['ENSMODG00000008866', 'ENSMODP00000011040', 'ENSMODT00000011257']}}, 'Phy0001SFG_ARATH': {'collateral': 14L, 'copy': 1L, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': '', 'species': 'ARATH', 'protein': 'Q9SUG6', 'external': {'TrEMBL.2010.09': ['Q9SUG6']}}, 'Phy0002JCH_CANAL': {'collateral': 4L, 'copy': 1L, 'taxid': 5476L, 'trees': 0L, 'proteome': 'CANAL.1', 'sps_name': 'Candida albicans', 'gene': '', 'species': 'CANAL', 'protein': 'orf19.10082', 'external': {'TrEMBL.2010.09': ['C4YKZ7', 'Q5A9L6']}}, 'Phy000CPNE_RAT': {'collateral': 4L, 'copy': 1L, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': 'ENSRNOG00000004950', 'species': 'RAT', 'protein': 'ENSRNOP00000006668', 'external': {'Ensembl.v59': ['ENSRNOG00000004950', 'ENSRNOP00000006668', 'ENSRNOT00000006668'], 'TrEMBL.2010.09': ['D3ZID8']}}, 'Phy0003L1L_CANFA': {'collateral': 4L, 'copy': 1L, 'taxid': 9615L, 'trees': 0L, 'proteome': 'CANFA.1', 'sps_name': 'Canis familiaris', 'gene': 'ENSCAFG00000003944', 'species': 'CANFA', 'protein': 'ENSCAFP00000005869', 'external': {}}, 'Phy000CLXL_RAT': {'collateral': 4L, 'copy': 1L, 'taxid': 10116L, 'trees': 0L, 'proteome': 'RAT.1', 'sps_name': 'Rattus norvegicus', 'gene': 'ENSRNOG00000008604', 'species': 'RAT', 'protein': 'ENSRNOP00000011654', 'external': {'TrEMBL.2010.09': ['D3ZEG3']}}, 'Phy0005KKR_DEBHA': {'collateral': 7L, 'copy': 1L, 'taxid': 4959L, 'trees': 0L, 'proteome': 'DEBHA.1', 'sps_name': 'Debaryomyces hansenii', 'gene': '', 'species': 'DEBHA', 'protein': 'Q6BYS0', 'external': {}}, 'Phy0000P6F_APIME': {'collateral': 6L, 'copy': 1L, 'taxid': 7460L, 'trees': 1L, 'proteome': 'APIME.1', 'sps_name': 'Apis mellifera', 'gene': 'ENSAPMG00000005963', 'species': 'APIME', 'protein': 'ENSAPMP00000010305', 'external': {}}, 'Phy00098SP_MONDO': {'collateral': 4L, 'copy': 1L, 'taxid': 13616L, 'trees': 0L, 'proteome': 'MONDO.1', 'sps_name': 'Monodelphis domestica', 'gene': 'ENSMODG00000019559', 'species': 'MONDO', 'protein': 'ENSMODP00000024398', 'external': {'Ensembl.v59': ['ENSMODG00000019559', 'ENSMODP00000024398', 'ENSMODT00000024831']}}, 'Phy00057S0_DICDI': {'collateral': 5L, 'copy': 1L, 'taxid': 44689L, 'trees': 0L, 'proteome': 'DICDI.1', 'sps_name': 'Dictyostelium discoideum', 'gene': '', 'species': 'DICDI', 'protein': 'Q54BQ5', 'external': {'Swiss-Prot.2010.09': ['Q54BQ5']}}, 'Phy0001H3K_ARATH': {'collateral': 6L, 'copy': 1L, 'taxid': 3702L, 'trees': 1L, 'proteome': 'ARATH.1', 'sps_name': 'Arabidopsis thaliana', 'gene': '', 'species': 'ARATH', 'protein': 'Q9LVE1', 'external': {'TrEMBL.2010.09': ['Q9LVE1']}}, 'Phy000AACP_MACMU': {'collateral': 4L, 'copy': 1L, 'taxid': 9544L, 'trees': 0L, 'proteome': 'MACMU.1', 'sps_name': 'Macaca mulatta', 'gene': 'ENSMMUG00000015994', 'species': 'MACMU', 'protein': 'ENSMMUP00000021035', 'external': {}}, 'Phy0008TSZ_LEIMA': {'collateral': 1L, 'copy': 1L, 'taxid': 5664L, 'trees': 0L, 'proteome': 'LEIMA.1', 'sps_name': 'Leishmania major', 'gene': '', 'species': 'LEIMA', 'protein': 'Q4QBW3', 'external': {'TrEMBL.2010.09': ['Q4QBW3']}}, 'Phy0004PJ7_CRYNE': {'collateral': 9L, 'copy': 1L, 'taxid': 5207L, 'trees': 0L, 'proteome': 'CRYNE.1', 'sps_name': 'Cryptococcus neoformans', 'gene': '', 'species': 'CRYNE', 'protein': 'Q55RA0', 'external': {'TrEMBL.2010.09': ['Q5KEX0']}}, 'Phy000BUTW_PANTR': {'collateral': 4L, 'copy': 1L, 'taxid': 9598L, 'trees': 0L, 'proteome': 'PANTR.1', 'sps_name': 'Pan troglodytes', 'gene': 'ENSPTRG00000019921', 'species': 'PANTR', 'protein': 'ENSPTRP00000034120', 'external': {}}, 'Phy000A0DO_MOUSE': {'collateral': 5L, 'copy': 1L, 'taxid': 10090L, 'trees': 0L, 'proteome': 'MOUSE.1', 'sps_name': 'Mus musculus', 'gene': 'ENSMUSG00000020634', 'species': 'MOUSE', 'protein': 'ENSMUSP00000020962', 'external': {'Ensembl.v59': ['ENSMUSG00000020634', 'ENSMUSP00000020962', 'ENSMUSP00000118834', 'ENSMUST00000020962', 'ENSMUST00000142867'], 'TrEMBL.2010.09': ['B8JK44'], 'Swiss-Prot.2010.09': ['Q99KJ0']}}, 'Phy000EWDU_YARLI': {'collateral': 12L, 'copy': 1L, 'taxid': 4952L, 'trees': 0L, 'proteome': 'YARLI.1', 'sps_name': 'Yarrowia lipolytica', 'gene': '', 'species': 'YARLI', 'protein': 'Q6C5V3', 'external': {'TrEMBL.2010.09': ['Q6C5V3']}}, 'Phy0006QQY_TAKRU': {'collateral': 4L, 'copy': 1L, 'taxid': 31033L, 'trees': 0L, 'proteome': 'TAKRU.1', 'sps_name': 'Takifugu rubripes', 'gene': 'NEWSINFRUG00000151706', 'species': 'TAKRU', 'protein': 'NEWSINFRUP00000161354', 'external': {}}, 'Phy0008JFW_HUMAN': {'collateral': 17L, 'copy': 1L, 'taxid': 9606L, 'trees': 4L, 'proteome': 'HUMAN.1', 'sps_name': 'Homo sapiens', 'gene': 'ENSG00000172659', 'species': 'HUMAN', 'protein': 'ENSP00000327891', 'external': {'Ensembl.v59': ['ENSG00000215114', 'ENSP00000382507', 'ENST00000399598'], 'Swiss-Prot.2010.09': ['Q14CS0']}}, 'Phy000692N_DANRE': {'collateral': 5L, 'copy': 1L, 'taxid': 7955L, 'trees': 0L, 'proteome': 'DANRE.1', 'sps_name': 'Danio rerio', 'gene': 'ENSDARG00000041144', 'species': 'DANRE', 'protein': 'ENSDARP00000060308', 'external': {}}}}

complete_tree_2 = {'tree': {'lk': -231.99600000000001, 'method': 'JTT', 'best': True, 'newick': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108342,(Phy000CVLS_YEAST:0.212821,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025083,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.950000:0.104729)0.620000:0.117294)0.693659:0.022298)0.125038:0.000000);'}, 'seq': {'Phy000CWXJ_YEAST': {'collateral': 36L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YIR040C', 'external': {'Ensembl.v59': ['YIR040C'], 'Swiss-Prot.2010.09': ['P40584']}}, 'Phy000CXBC_YEAST': {'collateral': 36L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YGL260W', 'external': {'Ensembl.v59': ['YGL260W'], 'Swiss-Prot.2010.09': ['P53056']}}, 'Phy000CVIE_YEAST': {'collateral': 23L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YAL067W-A', 'external': {'Ensembl.v59': ['YAL067W-A'], 'Swiss-Prot.2010.09': ['Q8TGK6']}}, 'Phy000CVLS_YEAST': {'collateral': 37L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YBL108W', 'external': {'Ensembl.v59': ['YBL108W'], 'Swiss-Prot.2010.09': ['P38161']}}, 'Phy000CYBL_YEAST': {'collateral': 36L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YKL223W', 'external': {'Ensembl.v59': ['YKL223W'], 'Swiss-Prot.2010.09': ['P36031']}}, 'Phy000CY0I_YEAST': {'collateral': 24L, 'copy': 2L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YJL222W-A', 'external': {'Ensembl.v59': ['YJL222W-A'], 'Swiss-Prot.2010.09': ['P40437']}}, 'Phy000CZQW_YEAST': {'collateral': 7L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YNR075C-A', 'external': {'Ensembl.v59': ['YNR075C-A'], 'Swiss-Prot.2010.09': ['Q8TGJ2']}}}}

complete_tree_3 = {'tree': {'lk': -234.922, 'method': 'WAG', 'best': False, 'newick': '(Phy000CY0I_YEAST:0.000000,Phy000CY0I_YEAST:0.000000,(Phy000CZQW_YEAST:0.108966,(Phy000CVLS_YEAST:0.209734,(Phy000CVIE_YEAST:0.000028,(Phy000CYBL_YEAST:0.025782,(Phy000CWXJ_YEAST:0.000000,Phy000CXBC_YEAST:0.000000)0.125038:0.000000)0.964000:0.107553)0.648000:0.118969)0.756000:0.023454)0.125038:0.000000);'}, 'seq': {'Phy000CWXJ_YEAST': {'collateral': 36L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YIR040C', 'external': {'Ensembl.v59': ['YIR040C'], 'Swiss-Prot.2010.09': ['P40584']}}, 'Phy000CXBC_YEAST': {'collateral': 36L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YGL260W', 'external': {'Ensembl.v59': ['YGL260W'], 'Swiss-Prot.2010.09': ['P53056']}}, 'Phy000CVIE_YEAST': {'collateral': 23L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YAL067W-A', 'external': {'Ensembl.v59': ['YAL067W-A'], 'Swiss-Prot.2010.09': ['Q8TGK6']}}, 'Phy000CVLS_YEAST': {'collateral': 37L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YBL108W', 'external': {'Ensembl.v59': ['YBL108W'], 'Swiss-Prot.2010.09': ['P38161']}}, 'Phy000CYBL_YEAST': {'collateral': 36L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YKL223W', 'external': {'Ensembl.v59': ['YKL223W'], 'Swiss-Prot.2010.09': ['P36031']}}, 'Phy000CY0I_YEAST': {'collateral': 24L, 'copy': 2L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YJL222W-A', 'external': {'Ensembl.v59': ['YJL222W-A'], 'Swiss-Prot.2010.09': ['P40437']}}, 'Phy000CZQW_YEAST': {'collateral': 7L, 'copy': 1L, 'taxid': 4932L, 'trees': 5L, 'proteome': 'YEAST.2', 'sps_name': 'Saccharomyces cerevisiae', 'gene': '', 'species': 'YEAST', 'protein': 'YNR075C-A', 'external': {'Ensembl.v59': ['YNR075C-A'], 'Swiss-Prot.2010.09': ['Q8TGJ2']}}}}
### ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ***** ****


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

  def test_collateral_trees(self):
    """ Make sure API is getting the collateral trees for all the cases
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
    """ Check if the phylogenetic trees are being recorevy with normality
    """

    ## Normal Cases
    val_1, val_2, val_3 = "Phy0008BO2", 1, None
    expected = {}
    self.assertEqual(self.connection.get_tree(val_1, val_2, val_3), expected)

    val_1, val_2, val_3 = "Phy0008BO3_HUMAN", 1, None
    expected = tree_1
    self.assertEqual(self.connection.get_tree(val_1, val_2, val_3), expected)

    val_1, val_2, val_3 = "Phy0008BO3_HUMAN", 1, "NJ"
    expected = {}
    self.assertEqual(self.connection.get_tree(val_1, val_2, val_3), expected)

    val_1, val_2, val_3 = "Phy000CVIE", 7, "WAG"
    expected = {}
    expected.setdefault("WAG", tree_2["WAG"])
    self.assertEqual(self.connection.get_tree(val_1, val_2, val_3), expected)

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
    """ Test if the API is returning correctly the associated information, in
        terms of available trees, to a given protein identifier.
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
    """ Make sure that the API is able to recover and return together all the
        information associated to a given seed protein in a given phylome.
    """

    ## Normal Cases
    val_1, val_2, val_3 = "Phy0008BO2", 1, None
    expected = {}
    self.assertEqual(self.connection.get_seq_info_in_tree(val_1, val_2, val_3),\
      expected)

    val_1, val_2, val_3 = "Phy0008BO3_HUMAN", 1, None
    expected = complete_tree_1
    self.assertEqual(self.connection.get_seq_info_in_tree(val_1, val_2, val_3),\
      expected)

    val_1, val_2, val_3 = "Phy000CVIE", 7, None
    expected = complete_tree_2
    self.assertEqual(self.connection.get_seq_info_in_tree(val_1, val_2, val_3),\
      expected)

    val_1, val_2, val_3 = "Phy000CVIE", 7, "WAG"
    expected = complete_tree_3
    self.assertEqual(self.connection.get_seq_info_in_tree(val_1, val_2, val_3),\
      expected)

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
    """ Get how many trees are per phylome
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
    """ Get all the available trees for a given phylome
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
