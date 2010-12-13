#!/usr/bin/python
"""
11 Nov 2010

test module
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"



from ete_dev.evol import EvolTree
from ete_dev.evol.treeview.layout import evol_clean_layout
from ete_dev      import faces, TreeImageProperties
from random       import random as rnd
from model        import Model
from copy         import deepcopy

WRKDIR = 'examples/data/protamine/PRM1/'

def main():
    """
    main function
    """

    print 'link to already runned data.'
    tree = EvolTree (WRKDIR + 'tree.nw')
    tree.workdir = 'examples/data/protamine/PRM1/paml/'

    random_swap(tree)
    tree.link_to_evol_model (WRKDIR + 'paml/fb/fb.out', 'fb')
    check_annotation (tree)
    tree.link_to_evol_model (WRKDIR + 'paml/M1/M1.out', 'M1')
    tree.link_to_evol_model (WRKDIR + 'paml/M2/M2.out', 'M2')
    tree.link_to_evol_model (WRKDIR + 'paml/M7/M7.out', 'M7')
    tree.link_to_evol_model (WRKDIR + 'paml/M8/M8.out', 'M8')
    tree.link_to_alignment  (WRKDIR + 'alignments.fasta_ali')
    print 'vars of fb model:'
    print vars (tree.get_evol_model('fb'))
    print 'pv of LRT M2 vs M1: ',
    print tree.get_most_likely ('M2','M1')
    print 'pv of LRT M8 vs M7: ',
    print tree.get_most_likely ('M8','M7')
    M2a = deepcopy (tree.get_evol_model('M2'))
    M2b = deepcopy (tree.get_evol_model('M2'))
    M2c = deepcopy (tree.get_evol_model('M2'))
    M2d = deepcopy (tree.get_evol_model('M2'))
    tree._models['M2.a'] = M2a
    tree._models['M2.b'] = M2b
    tree._models['M2.c'] = M2c
    tree._models['M2.d'] = M2d
    col =  {'NS' : 'grey', 'RX' : 'black',
            'RX+': 'grey', 'CN' : 'black',
            'CN+': 'grey', 'PS' : 'black', 'PS+': 'black'}
    col2 = {'NS' : 'white', 'RX' : 'white',
            'RX+': 'white', 'CN' : 'white',
            'CN+': 'white', 'PS' : 'white', 'PS+': 'white'}
    print tree._models
    M2a.set_histface (up=False, typ='line', lines = [1.0,0.3], col_lines=['red','grey'], header='ugliest face')
    M2b.set_histface (up=False, typ='error', col=col2, lines = [2.5, 1.0, 4.0, 0.5], header = 'Many lines, error boxes, background black',
                      col_lines=['orange', 'yellow', 'red', 'cyan'])
    M2c.set_histface (up=False, typ='protamine', lines = [1.0,0.3], col_lines=['black','grey'],
                      extras=['+','-',' ',' ',' ',':P', ' ',' ']*2+[' ']*(len(tree.get_leaves()[0].sequence)-16))
    M2d.set_histface (up=False, typ='hist', col=col, lines = [1.0,0.3], col_lines=['black','grey'])
    print 'Test histogram faces, in clean layout, (omega in dark red, 100*(dN)/100*(dS), in grey)'
    tree.show (histfaces=['M2','M2.a', 'M2.b', 'M2.c', 'M2.d'], layout=evol_clean_layout)

    # run codeml
    TREE_PATH    = "examples/data/S_example/measuring_S_tree.nw"
    ALG_PATH     = "examples/data/S_example/alignment_S_measuring_evol.fasta"
    WORKING_PATH = "/tmp/ete2-codeml_example/"
    
    tree = EvolTree (TREE_PATH)
    tree.link_to_alignment (ALG_PATH)
    tree.workdir = (WORKING_PATH)
    tree.run_model ('fb_anc')

    I = TreeImageProperties()
    I.force_topology             = False
    I.tree_width                 = 200
    I.draw_aligned_faces_as_grid = True
    I.draw_guidelines            = True
    I.guideline_type             = 2
    I.guideline_color            = "#CCCCCC"
    I.complete_branch_lines      = True
    for n in sorted (tree.get_descendants()+[tree],
                     key=lambda x: x.paml_id):
        if n.is_leaf(): continue
        anc_face = faces.SequenceFace (n.sequence, 'aa', fsize=11, aabg={})
        I.aligned_foot.add_face(anc_face, 1)
        I.aligned_foot.add_face(faces.TextFace('paml_id: #%d '%(n.paml_id)), 0)
    print 'display result of bs_anc model, with ancestral amino acid sequences.'
    tree.show(img_properties=I)

    tree.run_model ('M1')
    tree.run_model ('M2')
    tree.run_model ('M7')
    tree.run_model ('M8')
    print 'pv of LRT M2 vs M1: ',
    print tree.get_most_likely ('M2','M1')
    print 'pv of LRT M8 vs M7: ',
    print tree.get_most_likely ('M8','M7')
    tree.get_evol_model('M8').set_histface (up=False, typ='hist',
                                            lines = [2.0,0.3],
                                            col_lines=['black','grey'])
    tree.show(histfaces=['M2', 'M8'])
    tree.mark_tree ([2])
    print tree.write()
    tree.run_model ('bsA.2')
    tree.run_model ('bsA1.2')
    print 'pv of LRT bsA vs bsA1: ',
    print tree.get_most_likely ('bsA.2','bsA1.2')
    # clean marks:
    print tree.write()
    tree.mark_tree (map (lambda x: x._nid, tree.get_descendants()),
                    marks=[''] * len (tree.get_descendants()), verbose=True)
    print tree.write()
    tree.mark_tree ([2, 3, 4] + [1, 5], marks=['#1']*3 + ['#2']*2)
    print tree.write()
    tree.run_model ('bsC.2-3-4_1-5')
    tree.run_model ('bsA1.2')
    print 'pv of LRT bsC vs M1, marking 2 3 4 versus 1 5: ',
    print tree.get_most_likely ('bsC.2-3-4_1-5','M1')
    tree.run_model ('b_free.2-3-4_1-5')
    tree.run_model ('b_neut.2-3-4_1-5')
    print 'pv of LRT b_free 2 3 4, 1 5 amd outgroup vs 1 5 with omega = 1: ',
    print tree.get_most_likely ('b_free.2-3-4_1-5','b_neut.2-3-4_1-5')


    print '\n\n Now testing Models according to Yang papers:'
    print '----------------------------------------------\n'
    print 'Lysosyme:'
    tree = EvolTree ()

    print '''Yang, Z. 1998
    Likelihood ratio tests for detecting positive selection and application to primate lysozyme evolution
    Molecular biology and evolution 15: 568-73
    Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/9580986'''
    
    tree = EvolTree ('(((Hylobates_EDN,(Orang_EDN,(Gorilla_EDN,(Chimp_EDN,Human_EDN)))),(Macaq_EDN,(Cercopith_EDN,(Macaq2_EDN,Papio_EDN)))),(Orang_ECP,((Macaq_ECP,Macaq2_ECP),(Goril_ECP,Chimp_ECP,Human_ECP))));')
    print 'Working with tree -> no outgroup:'
    print tree

    print 'mark EDN duplicate:'
    for node in tree.traverse():
        tomark=False
        for leaf in node.get_leaf_names():
            if 'EDN' in leaf:
                tomark=True
                break
        if tomark:
            tree.mark_tree([node._nid], ['#1'])
    print tree.write()
    tree.link_to_alignment ('examples/data/CladeModelNoOG/ECP_EDN_15.nuc',
                            alg_format='paml')
    # run free branch just to lose time
    tree.run_model ('fb')
    print 'running branch sit model C and D for different omega values...'
    for omega in ['0.1', '0.5', '0.75', '2']:
        print 'running model bsD with starting omega = ' + omega
        tree.run_model ('bsD.' + omega, omega=omega)
        #                -------------  -----------
        #                      |             |
        #  ref name for this run             value of parameter "omega"
        print 'running model bsC with starting omega = ' + omega
        tree.run_model ('bsC.' + omega, omega=omega)


    tree = EvolTree ('((((Hylobates_EDN,(Orang_EDN,(Gorilla_EDN,(Chimp_EDN,Human_EDN)))),(Macaq_EDN,(Cercopith_EDN,(Macaq2_EDN,Papio_EDN)))),(Orang_ECP,((Macaq_ECP,Macaq2_ECP),(Goril_ECP,Chimp_ECP,Human_ECP)))),OwlMonkey_EDN,Tamarin_EDN);')
    tree.run_model ('fb.17spe')

    print "The End."


def random_swap(tree):
    '''
    swap randomly tree, to make sure labelling as paml is well done
    '''
    for node in tree.iter_descendants():
        if int (rnd()*100)%3:
            node.swap_childs()
    
def check_annotation (tree):
    '''
    check each node is labelled with a paml_id
    '''
    for node in tree.iter_descendants():
        if not hasattr (node, 'paml_id'):
            print 'Error, unable to label with paml ids'
            break
    print 'Labelling ok!'


if __name__ == "__main__":
    exit(main())
