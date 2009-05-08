#! /usr/bin/env python
import os 
import sys
import re
from optparse import OptionParser
_VERSION = "1.0"
_DESCRIPTION = '''

Calculates the dN and dS substitution rates of a given set of protein
pairs.

Prot pairs can be passed as a list of two-field lines within a text
file. Protein and DNA seqs are read from the the especified FASTA
files.

MUSCLE is used for protein sequence alignments and CODEML is used for
dN/dS calculation.

You can select the method used for the test: ML, YN or ALL.
''' 

import algIO

BASE_PATH = "./"

# Option Parser 
OPTPARSER = OptionParser(_DESCRIPTION, version=_VERSION)

OPTPARSER.add_option('-p', '--proteins', action='store', dest='proteins_fasta_file',
                      help='')
OPTPARSER.add_option('-g', '--genes', action='store', dest='dna_fasta_file',

                      help='')
OPTPARSER.add_option('-m', '--mode', action='store', dest='method',
                      help='')

OPTPARSER.add_option('-i', '--idpairs', action='store', dest='ids',
                      help='')

OPTPARSER.add_option('-f', '--idsfile', action='store', dest='idsfile',
                      help='')

OPTPARSER.add_option('-b', '--basepath', action='store', dest='base_path',
                      help='')

OPTPARSER.add_option('-C', '--collect', action='store_true', dest='collect',
                      help='Does not perform calculations, Just collect data.')


OPTIONS, ARGS = OPTPARSER.parse_args()

# CONFIG
CODEML_PATH = "codeml"
YN00_PATH   = "yn00"
MUSCLE_PATH = "muscle"

def main():
    global BASE_PATH
    if not OPTIONS.proteins_fasta_file or\
	    not OPTIONS.dna_fasta_file or\
	    not OPTIONS.method or not (OPTIONS.ids or OPTIONS.idsfile):
	OPTPARSER.print_help()
	sys.exit()


    if OPTIONS.base_path:
	BASE_PATH = OPTIONS.base_path

    ids_to_process = []
    if OPTIONS.ids:
	try:
	    id1, id2 = OPTIONS.ids.split(",")
	except ValueError:
	    print >>sys.stderr, "Id pair is not in the format: [-i id1,id2]"
	    sys.exit(-1)
	else:
	    ids_to_process.append([id1,id2])

    elif OPTIONS.idsfile:
	try:
	    for line in open(OPTIONS.idsfile):
		line = line.strip()
		if line==''  or  line.startswith("#"):
		    continue
		else:
		    fields = line.split("\t")
		    id1, id2 = fields[0], fields[1]
		    ids_to_process.append([id1,id2])
	except IndexError, IOError:
	    print >>sys.stderr, "Id file not in the format: 'id1 [TAB] id2 [newline]'\n", line
	    sys.exit(-1)

    prots = read_fasta(OPTIONS.proteins_fasta_file)
    dna = read_fasta(OPTIONS.dna_fasta_file)

    # check that all ids are in prots and dna
    not_found = None
    errors = 0
    for id1,id2 in ids_to_process:
	if id1 not in prots or id1 not in dna:
	    print >>sys.stderr, "%s could not be found in the proteins or genes file." %id1
	    errors += 1

	if id2 not in prots or id2 not in dna:
	    print >>sys.stderr, "%s could not be found in the proteins or genes file." %id2
	    errors += 1


    if errors>0:
	raw_input("Sequences of %d ids could not be found. Press (Ctrl+C> to abort or ENTER to start." %errors)


    # COmpute pairs
    os.system("mkdir -p %s" %BASE_PATH)
    OUT = open(os.path.join(BASE_PATH,"result_summary.txt"),"w")
    key_values  = [ "2ML.dS","2YN.dS","2NG.dS","2ML.dN","2YN.dN", "2NG.dN" ]
    print >>OUT, '\t'.join(["#ID_pairs"]+key_values)
    for id1, id2 in ids_to_process:
	if OPTIONS.collect:
	    results = collect_results(id1, id2)
	else:
	    get_pairwise(id1, id2, prots[id1], prots[id2], dna[id1], dna[id2], OPTIONS.method)
	    results = collect_results(id1, id2)

	values = [id1+"_"+id2] + [results.get(key, None) for key in key_values ]
	print '\t'.join(map(str,values))
	print >>OUT, '\t'.join(map(str,values))
	OUT.flush()
    OUT.close()


def collect_results(id_1, id_2):
    results = {}
    id_1st, id_2nd = sorted([id_1, id_2])
    pair_path = os.path.join(BASE_PATH, id_1st, id_2nd)
    rfiles  = [ "2ML.dS","2YN.dS","2NG.dS","2ML.dN","2YN.dN", "2NG.dN" ]
    for f in rfiles:
	try:
	    results[f] = float(re.search("\s+([+-]?\d+\.\d+)", open(os.path.join(pair_path, f)).read(), re.MULTILINE).groups()[0])
	except:
	    print >>sys.stderr, "Could not process result file:", os.path.join(pair_path, f)
    return results


def get_pairwise(id_1, id_2, aa_1, aa_2, nt_1, nt_2, method):

    results = {}
    
    id_1st, id_2nd = sorted([id_1, id_2])
    pair_name = "_".join(([id_1st, id_2nd]))

    pair_path = os.path.join(BASE_PATH, id_1st, id_2nd)
    os.system("mkdir -p %s" %pair_path)

    prots_msf_file   = pair_path +"/"+pair_name+".pep.fasta"
    genes_msf_file   = pair_path +"/"+pair_name+".dna.fasta"
    fasta_aln_file   = pair_path +"/"+pair_name+".pep.alg"
    phylip_aln_file  = pair_path +"/"+pair_name+".pep.phylip"
    dna_aln_file     = pair_path +"/"+pair_name+".dna.phylip"
    codeml_out_file  = pair_path +"/"+pair_name+".codeml"
    codeml_conf_file = pair_path +"/"+pair_name+".codeml.config"
    yn_out_file      = pair_path +"/"+pair_name+".yn"
    yn_conf_file     = pair_path +"/"+pair_name+".yn.config"

    open(prots_msf_file, "w").write( ">%s\n%s\n>%s\n%s\n" %(id_1, aa_1, id_2, aa_2))
    open(genes_msf_file, "w").write( ">%s\n%s\n>%s\n%s\n" %(id_1, nt_1, id_2, nt_2))

    # RUN MUSCLE alignments
    os.system("%s -in %s -out %s" % (MUSCLE_PATH, \
					 prots_msf_file, \
					 fasta_aln_file) 
	      )

    # Read peptide alignment
    pep_alg = algIO.read_fasta(fasta_aln_file)

    # Creates an empty alignment to store clean dna alg
    dna_alg = algIO.alignment()
    dna_alg.seqs[id_1] = ""
    dna_alg.seqs[id_2] = ""
    dna_alg.seq_order= [id_1,id_2]
    # Initialize  aa counters  
    aa_counter_1 = -1
    aa_counter_2 = -1
    # Look every aligned aa
    for pos in xrange(len(pep_alg.seqs[id_1])):
	# When gaps, position is incremented in aligned seq, but not
	# in its coding seq
        if pep_alg.seqs[id_1][pos] != "-":
            aa_counter_1 +=1
        if pep_alg.seqs[id_2][pos] != "-":
            aa_counter_2 +=1
        # If no gap in aa alignment, take dna codons
        if pep_alg.seqs[id_1][pos] != "-" and pep_alg.seqs[id_2][pos] != "-":
            codon_1 = get_codon(aa_counter_1, nt_1)
            codon_2 = get_codon(aa_counter_2, nt_2)
            dna_alg.seqs[id_1]+=  codon_1
            dna_alg.seqs[id_2]+=  codon_2
            dna_alg.length+=3
            print "Aligned aa: %c%c, codons:" %(pep_alg.seqs[id_2][pos],pep_alg.seqs[id_1][pos]),codon_1,codon_2
    algIO.write_phylip(dna_alg, dna_aln_file, interleaved=False)

    if OPTIONS.method=="ML" or OPTIONS.method=="ALL":
	# Run ML test
	write_codeml_config_file(codeml_conf_file, dna_aln_file, codeml_out_file)
	print "cd %s; %s %s" %(pair_path, CODEML_PATH, codeml_conf_file)
	os.system("cd %s; %s %s" %(pair_path, CODEML_PATH, codeml_conf_file))

    if OPTIONS.method=="YN" or OPTIONS.method=="ALL":
	# Run YN test
	write_yn_config_file(yn_conf_file, dna_aln_file, yn_out_file)
	os.system("cd %s; %s %s" %(pair_path, YN00_PATH, yn_conf_file))

    return

def get_codon(codon_pos,seq):
    """ given a dna seq, returns the codon at position = codon_pos""" 
    pos = 3*codon_pos
    return seq[pos:pos+3]

def write_yn_config_file(configFile,algFile,outFile):
    conf = """
seqfile = %s     * sequence data filename
outfile = %s     * main result file name
icode = 0        * 0:universal code; 1:mammalian mt; 2-10:see below
weighting = 0    * weighting pathways between codons (0/1)?
commonf3x4 = 0   * use one set of codon freqs for all pairs (0/1)?
""" % (algFile,outFile)

    CONFIG = open(configFile,"w")
    CONFIG.write(conf)
    CONFIG.close()
    return 


def write_codeml_config_file(configFile,algFile,outFile):
    conf = """
      seqfile = %s                            * sequence data filename
*    treefile = ctls/trees/fb.tree            * tree structure file name
      outfile = %s                            * main result file name

        noisy = 9      * 0,1,2,3,9: how much rubbish on the screen
      verbose = 0      * 0: concise; 1: detailed, 2: too much
      runmode = -2     * 0: user tree;  1: semi-automatic;  2: automatic
                       * 3: StepwiseAddition; (4,5):PerturbationNNI; -2: pairwise

      seqtype = 1  * 1:codons; 2:AAs; 3:codons-->AAs
    CodonFreq = 2  * 0:1/61 each, 1:F1X4, 2:F3X4, 3:codon table
*       ndata = 1
        clock = 0  * 0:no clock, 1:clock; 2:local clock; 3:CombinedAnalysis
       aaDist = 0  * 0:equal, +:geometric; -:linear, 1-6:G1974,Miyata,c,p,v,a
   aaRatefile = dat/jones.dat  * only used for aa seqs with model=empirical(_F)
                   * dayhoff.dat, jones.dat, wag.dat, mtmam.dat, or your own

        model = 1
                   * models for codons:
                       * 0:one, 1:b, 2:2 or more dN/dS ratios for branches
                   * models for AAs or codon-translated AAs:
                       * 0:poisson, 1:proportional, 2:Empirical, 3:Empirical+F
                       * 6:FromCodon, 7:AAClasses, 8:REVaa_0, 9:REVaa(nr=189)

      NSsites = 0  * 0:one w;1:neutral;2:selection; 3:discrete;4:freqs;
                   * 5:gamma;6:2gamma;7:beta;8:beta&w;9:beta&gamma;
                   * 10:beta&gamma+1; 11:beta&normal>1; 12:0&2normal>1;
                   * 13:3normal>0

        icode = 0  * 0:universal code; 1:mammalian mt; 2-10:see below
        Mgene = 0
                   * codon: 0:rates, 1:separate; 2:diff pi, 3:diff kapa, 4:all diff
                   * AA: 0:rates, 1:separate

    fix_kappa = 0  * 1: kappa fixed, 0: kappa to be estimated
        kappa = 2  * initial or fixed kappa
    fix_omega = 0  * 1: omega or omega_1 fixed, 0: estimate
        omega = .4 * initial or fixed omega, for codons or codon-based AAs

    fix_alpha = 1  * 0: estimate gamma shape parameter; 1: fix it at alpha
        alpha = 0  * initial or fixed alpha, 0:infinity (constant rate)
       Malpha = 0  * different alphas for genes
        ncatG = 8  * # of categories in dG of NSsites models

        getSE = 1  * 0: don't want them, 1: want S.E.s of estimates
 RateAncestor = 0  * (0,1,2): rates (alpha>0) or ancestral states (1 or 2)

    Small_Diff = .5e-6
     cleandata = 1  * remove sites with ambiguity data (1:yes, 0:no)?
*  fix_blength = -1  * 0: ignore, -1: random, 1: initial, 2: fixed
        method = 0   * 0: simultaneous; 1: one branch at a time

* Genetic codes: 0:universal, 1:mammalian mt., 2:yeast mt., 3:mold mt.,
* 4: invertebrate mt., 5: ciliate nuclear, 6: echinoderm mt.,
* 7: euplotid mt., 8: alternative yeast nu. 9: ascidian mt.,
* 10: blepharisma nu.
* These codes correspond to transl_table 1 to 11 of GENEBANK.
""" % (algFile,outFile)

    CONFIG = open(configFile,"w")
    CONFIG.write(conf)
    CONFIG.close()
    return 


def read_fasta(fname):
    seqs = {}
    active_name = None
    for line in open(fname):
	line = line.strip()
	if line.startswith(">"):
	    name = line[1:].split()[0]
	    seqs[name] = ""
	    active_name = name
	else:
	    seqs[active_name] += line.upper()
    return seqs





if __name__ == "__main__":
    main()
