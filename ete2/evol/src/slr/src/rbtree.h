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

#ifndef _RBTREE_H_
#define _RBTREE_H_

#ifndef _STDBOOL_H_
#include <stdbool.h>
#endif

enum rbcolour { red,black};

struct __rbnode {
        enum rbcolour colour;
        struct __rbnode *left, *right, *parent;
        void *key,*value;
};
typedef struct __rbnode * RBNODE;

struct __rbtree {
        RBNODE root;
        int (*compfun)(const void *, const void *);
        void * (*copykey)(const void *);
        void (*freekey)(void *);
};
typedef struct __rbtree * RBTREE;

struct __rbiter {
	RBNODE last;
	RBNODE current;
};
typedef struct __rbiter * RBITER;


RBTREE create_rbtree ( int (*compfun)(const void *, const void *), void * (*copykey)(const void *), void (*freekey)(void *) );
void free_rbtree (RBTREE tree, void (*freevalue)(void *));
RBTREE copy_rbtree ( const RBTREE tree, void * (*copyvalue)(const void *) );

void * getelt_rbtree ( const RBTREE tree, const void * key);
bool member_rbtree ( const RBTREE tree, const void * key);
void * insertelt_rbtree ( RBTREE tree, void * key, void * value);
void * removeelt_rbtree (RBTREE tree, const void * key);
RBITER iter_rbtree (const RBTREE tree);
const void * itervalue_rbtree (const RBITER iter);
const void * iterkey_rbtree ( const RBITER iter);
void freeiter_rbtree( RBITER iter);
bool next_rbtree ( RBITER rbit );


void map_rbtree ( RBTREE tree, void * (*mapfun)(const void *, void *) );
void * minelt_rbtree ( const RBTREE tree);
void * maxelt_rbtree ( const RBTREE tree);
unsigned int nmemb_rbtree (const RBTREE tree);


int lexo ( const void * pt1, const void * pt2);
void * strcopykey(const void * key);
void strfreekey (void * key);

#endif
