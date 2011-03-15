/*
 *  Copyright 2003-2008 Tim Massingham (tim.massingham@ebi.ac.uk)
 *  Funded by EMBL - European Bioinformatics Institute
 */
/*
 *  This file is part of SLR ("Sitewise Likelihood Ratio")
 *
 *  SLR is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  SLR is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with SLR.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef _TREE_H_
#define _TREE_H_

#ifndef _STDIO_H_
#include <stdio.h>
#endif

#define ISLEAF(A)       ( A->branch[1] == NULL )
#define CHILD(A,B)      A->branch[B]
#define CHILDP(A,B)     ((A->branch[B])->plik);
#define LENGTH(A)       A->length[B]

#define DBL_EQUALS(A,B) ( fabs((A)-(B))<=2*DBL_EPSILON*(fabs(A)+fabs(B)) )
#ifndef OOM
#define OOM(A) if ( A == NULL){ \
                  printf ("Out of Memory!\n"); \
                  exit (EXIT_FAILURE); }
#endif

#ifndef _RBTREE_H_
#include "rbtree.h"
#endif

#ifndef _VEC_H_
#include "vec.h"
#endif



struct node {
        struct node **   branch;
        double          * blength;
        int             bnumber;
	int		nbran;
	int 		maxbran;
        int             *seq;
	char 		*name;
        /*  Part_lik is array, length N_BASES*N_PTS, indexed by a*N_BASES+b*/
        double          *plik;
        double          *mid,*back,*dback;
        double          *mat, *bmat;
        double          scalefactor,bscalefactor;
        int scale,bscale;
};

typedef struct node NODE;

typedef struct {
        int n_sp;
        int n_br;
        char * tstring;
        NODE * tree;
        NODE ** branches;
        RBTREE leaves;
} TREE;


void Recurse_forward ( const TREE * tree, void (*fun)(void *, int,int), void * info);
void Recurse_backward ( const TREE * tree, void (*fun)(void *, int,int), void *info);
void CheckIsTree ( const TREE * tree);
void create_tree (TREE * tree);
void print_tree ( FILE * out, const NODE * node, const NODE * parent, const TREE * tree);
int find_branch_number ( const NODE * branch, const TREE * tree);
int find_connection ( const NODE * from, const NODE * to);
int add_lengths_to_tree ( TREE * tree, double *lengths);
void PrintBranchLengths (FILE * fp, const TREE * tree);
void ScaleTree ( TREE * tree, const double f);
TREE * CopyTree ( const TREE * tree);
TREE * CloneTree ( TREE * tree);
void FreeTree ( TREE * tree);
void FreeNode( NODE * node, NODE * parent);

TREE ** read_tree_strings ( char * filename);
TREE * copy_tree_strings ( const TREE * tree );
int save_tree_strings ( char * filename, TREE ** trees);
int add_lengths_to_tree ( TREE * tree, double *lengths);

NODE *  find_leaf_by_name ( const char * name, const TREE * tree);
VEC branchlengths_from_tree ( const TREE * tree);

#endif

