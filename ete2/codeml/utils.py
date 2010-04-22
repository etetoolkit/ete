#!/usr/bin/python
#        Author: Francois-Jose Serra
# Creation Date: 2010/04/22 16:05:46

from stats import chisqprob

def test_models(lnl1, np1, lnl2, np2):
    '''
    to test if one model is more likeli than the second
    chi square test
    '''
    return chisqprob(2*(float(lnl2)-float(lnl1)), df=(int (np2)-int(np1)))


def alg2paml(tree, alg, outdir='', align = False, formats = \
             ['fasta', 'phylip', 'iphylip']):
    '''
    convert alignment file (phylip iphylip fasta) into paml
    format stored in algn file in outdir returns phyloTree object
    '''
    for form in formats:
        try:
            phylot = PhyloTree(tree, alignment=alg, alg_format=form)
            break
        except Exception:
            continue
        sys.exit('\nERROR: Problem with inputs.\n'+tree)
    if not outdir == '':
        os.system('mkdir -p '+outdir)
        alg_file = open(outdir+'/algn','w')
        alg_file.write(' '+str(len(phylot))+' '+\
                       str (len(phylot.get_leaves()[0].sequence))+'\n')
        for node in phylot.iter_leaves():
            alg_file.write('>'+node.name+'\n')
            alg_file.write(node.sequence+'\n')
        alg_file.close()
    return phylot
