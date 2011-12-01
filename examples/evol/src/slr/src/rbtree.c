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

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "rbtree.h"

void * insertelt_rbtree_sub ( RBTREE tree, RBNODE node, int (*compfun)(const void *,const void *), void * key, void * value);
void balance_rbtree ( RBNODE node, RBTREE tree);
RBNODE search_rbtree (RBTREE tree, const void * key);
enum rbcolour colour_rbnode ( const RBNODE node);

int check_rbnode ( const RBNODE node, const RBNODE parent, const RBTREE tree){
	assert(NULL!=node);
	assert(NULL!=node->key);
	assert(NULL!=node->value);

	/*  node->parent is parent*/
	assert(node->parent==parent);
	/* Both children of a red node must be black 
         * (NULL children are black)
	 */
	if ( red == node->colour){
		assert(NULL==node->left  || black==node->left->colour);
		assert(NULL==node->right || black==node->right->colour); 
	}
	if ( NULL!=node->left){ assert(tree->compfun(node->left->key,node->key)<0);}
	if ( NULL!=node->right){ assert(tree->compfun(node->right->key,node->key)>0);}

	int nblack_left = (NULL!=node->left)?check_rbnode(node->left,node,tree):0;
	int nblack_right = (NULL!=node->right)?check_rbnode(node->right,node,tree):0;
	assert(nblack_left==nblack_right);

	return nblack_left + ((black==node->colour)?1:0);
}

	
	
int check_rbtree ( const RBTREE tree ){
	#ifdef NDEBUG
		return 0;
	#endif
	assert(NULL!=tree);
	assert(NULL!=tree->compfun);
	assert(NULL!=tree->copykey);
	assert(NULL!=tree->freekey);
	if (NULL==tree->root){ return 0;}

	/*  Root must be black  */
	assert(black==tree->root->colour);
	return check_rbnode(tree->root,NULL,tree);
}


	

RBTREE create_rbtree ( int (*compfun)(const void *, const void *), void * (*copykey)(const void *), void (*freekey)(void *) ){
	assert(NULL!=compfun);
	assert(NULL!=copykey);
	assert(NULL!=freekey);

	RBTREE tree = malloc(sizeof(struct __rbtree));
	if ( NULL==tree){ return NULL;}
	tree->root = NULL;
	tree->compfun = compfun;
	tree->copykey = copykey;
	tree->freekey = freekey;

	return tree;
}

RBNODE create_rbnode ( enum rbcolour colour ){
	RBNODE node = calloc(1,sizeof(struct __rbnode));
	node->colour = colour;
	return node;
}

void free_rbnode ( RBNODE node, void (*freekey)(void *), void (*freevalue)(void *) ){
	assert(NULL!=node);

	freekey(node->key);
	if(NULL!=freevalue){freevalue(node->value);}
	free(node);
}

void free_rbnode_sub ( RBNODE node, void (*freekey)(void *), void (*freevalue)(void *) ){
	assert(NULL!=node);
	assert(NULL!=freekey);
	if(NULL!=node->left) free_rbnode_sub(node->left,freekey,freevalue);
	if(NULL!=node->right) free_rbnode_sub(node->right,freekey,freevalue);
	free_rbnode(node,freekey,freevalue);
}

void free_rbtree ( RBTREE tree, void (*freevalue)(void *) ){
	assert(NULL!=tree);
	if ( NULL!=tree->root) free_rbnode_sub(tree->root, tree->freekey, freevalue);
	free(tree);
}

RBNODE copy_rbnode_sub ( const RBNODE node, void * (*copykey)(const void *), void * (*copyvalue)(const void *) ){
	assert(NULL!=node);
	assert(NULL!=copykey);

	RBNODE newnode = create_rbnode(black);
	newnode->colour = node->colour;
	newnode->key = copykey(node->key);
	newnode->value = (NULL!=copyvalue)?copyvalue(node->value):node->value;
	if (NULL!=node->left){
		newnode->left = copy_rbnode_sub(node->left,copykey,copyvalue);
		newnode->left->parent = newnode;
	}
	if (NULL!=node->right){
		newnode->right = copy_rbnode_sub(node->right,copykey,copyvalue);
		newnode->right->parent = newnode;
	}
	return newnode;
}

RBTREE copy_rbtree ( const RBTREE tree, void * (*copyvalue)(const void *) ){
	assert(NULL!=tree);
	RBTREE newtree = create_rbtree(tree->compfun,tree->copykey,tree->freekey);
	if (NULL!=tree->root){
		newtree->root = copy_rbnode_sub(tree->root,tree->copykey,copyvalue);
		newtree->root->parent = NULL;
	}
	return newtree;
}


void * getelt_rbtree ( const RBTREE tree, const void * key){
	assert(NULL!=tree);
	assert(NULL!=key);

	RBNODE node = search_rbtree(tree,key);
	if (NULL!=node){ return node->value;}
	return NULL;
}


bool member_rbtree ( const RBTREE tree, const void * key){
	RBNODE node = search_rbtree (tree,key);
	if ( NULL==node) return false;
	return true;
}



void map_rbtree_sub ( RBNODE node, void * (*mapfun)(const void *, void *) ){
	if (NULL!=node){
		node->value = mapfun(node->key,node->value);
		map_rbtree_sub(node->left,mapfun);
		map_rbtree_sub(node->right,mapfun);
	}
}

void map_rbtree ( RBTREE tree, void * (*mapfun)(const void *, void *) ){
	map_rbtree_sub (tree->root,mapfun);
}

void unsafemap_rbtree_sub ( RBNODE node, void (*mapfun)(RBNODE) ){
	if (NULL!=node){
		mapfun(node);
		unsafemap_rbtree_sub(node->left,mapfun);
		unsafemap_rbtree_sub(node->right,mapfun);
	}
}

void unsafemap_rbtree ( RBTREE tree, void (*mapfun)(RBNODE) ){
	unsafemap_rbtree_sub(tree->root,mapfun);
}

unsigned int nmemb_rbtree_sub( const RBNODE node){
	if(NULL==node) return 0;
	return 1 + nmemb_rbtree_sub(node->left) + nmemb_rbtree_sub(node->right);
}

unsigned int nmemb_rbtree (const RBTREE tree){
	assert(NULL!=tree);

	return (NULL!=tree->root)?nmemb_rbtree_sub(tree->root):0;
}

void * insertelt_rbtree ( RBTREE tree, void * key, void * value){
	assert(NULL!=tree);
	assert(NULL!=key);
	assert(NULL!=value);
	if ( NULL==tree->root){
		/*  Tree empty, root must be black */
		tree->root = create_rbnode (black);
		tree->root->key = tree->copykey(key);
		tree->root->value = value;
		tree->root->parent = NULL;
		return NULL;
	}

	/*  Find location to add  */
	return insertelt_rbtree_sub (tree, tree->root, tree->compfun, key, value);
}

RBNODE sibling_rbnode ( const RBNODE node){
	assert(NULL!=node);
	const RBNODE parent = node->parent;
	if (NULL==parent) return NULL;
	return (node==parent->left)?parent->right:parent->left;
}

void * insertelt_rbtree_sub ( RBTREE tree, RBNODE node, int (*compfun)(const void *,const void *), void * key, void * value){
	assert(NULL!=node);
	assert(NULL!=compfun);
	assert(NULL!=key);
	assert(NULL!=value);

	int comparison = compfun(key,node->key);
	if ( comparison == 0){
		/*  key already in tree. Balancing not affected */
		void * oldvalue = node->value;
		node->value = value;
		return oldvalue;
	}

	RBNODE * childnodep = NULL;
	if ( comparison<0 ){
		childnodep = &(node->left);
	} else if ( comparison>0 ){
		childnodep = &(node->right);
	}

	/*  Continue down tree */	
	if (NULL != *childnodep){return insertelt_rbtree_sub(tree,*childnodep,compfun,key,value);}

	*childnodep = create_rbnode(red);
	(*childnodep)->key = tree->copykey(key);
	(*childnodep)->value = value;
	(*childnodep)->parent = node;
	balance_rbtree (*childnodep,tree);
	return NULL;
}

void rotate_left_rbtree ( RBNODE node, RBTREE tree){
	assert(NULL!=node);
	node->right->parent = node->parent;
	if(NULL!=node->parent){
		if (node->parent->left==node) node->parent->left = node->right;
		else if (node->parent->right==node) node->parent->right = node->right;
		else abort();
	} else {
		tree->root = node->right;
	}
	node->parent = node->right;
	RBNODE tmp = node->right->left;
	node->right->left = node;
	node->right = tmp;
	if ( NULL!=tmp){ tmp->parent = node;}
}

void rotate_right_rbtree ( RBNODE node, RBTREE tree){
	assert(NULL!=node);
	node->left->parent = node->parent;
	if(NULL!=node->parent){ 
		if (node->parent->right==node) node->parent->right = node->left;
		else if (node->parent->left==node) node->parent->left = node->left;
		else abort();
	} else {
		tree->root = node->left;
	}
	node->parent = node->left;
	RBNODE tmp = node->left->right;
	node->left->right = node;
	node->left = tmp;
	if ( NULL!=tmp){ tmp->parent = node;}
}
	
	

void balance_rbtree ( RBNODE node, RBTREE tree){
	assert(NULL!=node);
	/*  Simple cases: 
	 *    node is root (parent is null);
	 *    or, added red node to black parent  */
	RBNODE parent = node->parent;
	if ( NULL==parent){ node->colour = black; return;}
	if ( black == parent->colour){ return;}

	RBNODE gparent = parent->parent;
	assert(NULL!=gparent); /* Is this condition correct? */
	/*  Parent's colour is red from here on */

	/*  Case 3. NULL uncles are black */
	RBNODE uncle = sibling_rbnode(parent);
	if ( red==colour_rbnode(uncle)){
		parent->colour = black;
		uncle->colour = black;
		gparent->colour = red;
		balance_rbtree(gparent, tree);
		return;
	}

	/*  Case 4. Drops through to case 5*/
	if ( node == parent->right && parent == gparent->left ){
		rotate_left_rbtree(parent, tree);
		node = node->left;
	} else if ( node == parent->left && parent == gparent->right ){
		rotate_right_rbtree(parent, tree);
		node = node->right;
	}
	
	parent = node->parent;
	gparent = parent->parent;
	parent->colour = black;
	gparent->colour = red;
	if ( node == parent->left && parent==gparent->left){
		rotate_right_rbtree(gparent, tree);
	} else if ( node==parent->right && parent==gparent->right){
		rotate_left_rbtree(gparent, tree);
	} else {
		abort();
	}
}


void print_node(RBNODE node){
	printf("Node: %d\t%s:%s\n",node->colour,(const char *)node->key,(const char *)node->value);
}

int lexo ( const void * pt1, const void * pt2){
	assert(NULL!=pt1 && NULL!=pt2);
	return strcmp((const char *)pt1,(const char *)pt2);
}

RBNODE search_rbtree_sub (RBNODE node, int (*compfun)(const void *,const void *),const void * key){
	assert(NULL!=compfun);
	assert(NULL!=key);
	if (NULL==node) return NULL;

	int comparison = compfun(key,node->key);
	if ( comparison<0 ){return search_rbtree_sub(node->left,compfun,key);}
	if ( comparison>0 ){return search_rbtree_sub(node->right,compfun,key);}
	
	return node;
}

RBNODE search_rbtree (RBTREE tree, const void * key){
	assert(NULL!=tree);
	assert(NULL!=key);
	return search_rbtree_sub(tree->root,tree->compfun,key);
}

RBNODE minnode_rbtree_sub ( const RBNODE node){
	assert(NULL!=node);
	if (NULL==node->left){ return node;}
	return minnode_rbtree_sub(node->left);
}

RBNODE maxnode_rbtree_sub ( const RBNODE node){
	assert(NULL!=node);
	if (NULL==node->right){ return node;}
	return maxnode_rbtree_sub(node->right);
}

void * minelt_rbtree ( const RBTREE tree){
	assert(NULL!=tree);
	if(NULL==tree->root){return NULL;}
	RBNODE minnode = minnode_rbtree_sub(tree->root);
	return minnode->value;
}

void * maxelt_rbtree ( const RBTREE tree){
	assert(NULL!=tree);
	if(NULL==tree->root){return NULL;}
	RBNODE maxnode = maxnode_rbtree_sub(tree->root);
	return maxnode->value;
}



enum rbcolour colour_rbnode ( const RBNODE node){
	if ( NULL==node) return black;
	return node->colour;
}


/*  Need to decide what to do about memory for keys.
 * Possible memory leak at moment.  */
void * removeelt_rbtree (RBTREE tree, const void * key){
	RBNODE phantom = NULL;
	void * retval = NULL;
	assert(NULL!=tree);
	assert(NULL!=key);

	RBNODE delnode = search_rbtree(tree,key);
	if (NULL==delnode){ return retval;} /*  Nothing to delete  */
	retval = delnode->value;
	tree->freekey(delnode->key);

	/*  Node has two non-null children. Transform so not case */
	if (NULL!=delnode->right && NULL!=delnode->left){
		RBNODE leftmost = minnode_rbtree_sub(delnode->right);
		delnode->key = leftmost->key;
		delnode->value = leftmost->value;
		delnode = leftmost;
	}

	/* delnode now has at most one child  */
	enum rbcolour delcol = delnode->colour;
	RBNODE child = (NULL==delnode->right)?delnode->left:delnode->right;
	if ( NULL==child){
		child = create_rbnode(black); /* "Phantom node" */
		phantom = child;
	}
	/*  Replace node with child  */
	if (NULL!=delnode->parent){
		if   (delnode->parent->left==delnode) delnode->parent->left = child;
		else if (delnode->parent->right==delnode) delnode->parent->right = child;
		else abort();
	} else {
		tree->root = child;
	}
	child->parent = delnode->parent;
	free(delnode);

	if(red==delcol){ goto remove_end;}
	/*  Deleted node was black  */
	if (red==colour_rbnode(child)){ child->colour = black; goto remove_end;}

case1:
	/* Case 1 */
	if ( NULL==child->parent){ /* New root */
		tree->root = child;
		goto remove_end;
	}
	
	/* Case 2 */
	RBNODE sibling = sibling_rbnode(child);
	if ( red==colour_rbnode(sibling)){
		child->parent->colour = red;
		sibling->colour = black;
		if ( child == child->parent->left) rotate_left_rbtree (child->parent,tree);
		else rotate_right_rbtree(child->parent,tree);
	}
	sibling = sibling_rbnode(child);
	assert(sibling->colour==black);

	/*  Case 3 */
	if ( black== child->parent->colour
	  && black==colour_rbnode(sibling->left) && black==colour_rbnode(sibling->right)){
		sibling->colour = red;
		child = child->parent;
		goto case1;
	}
	assert(sibling->colour==black);

	/*  Case 4 */
	if ( red == child->parent->colour
	  && black==colour_rbnode(sibling->left) && black==colour_rbnode(sibling->right)){
		sibling->colour = red;
		child->parent->colour = black;
		goto remove_end;
	}
	assert(sibling->colour == black);

	/*  Case 5 */
	if ( child==child->parent->left
	  && red==colour_rbnode(sibling->left) && black==colour_rbnode(sibling->right)){
		sibling->colour = red;
		sibling->left->colour = black;
		rotate_right_rbtree(sibling,tree);
	} else if ( child==child->parent->right
	  && black==colour_rbnode(sibling->left) && red==colour_rbnode(sibling->right)){
		sibling->colour = red;
		sibling->right->colour = black;
		rotate_left_rbtree(sibling,tree);
	}
	sibling = sibling_rbnode(child);


	/*  Case 6 */
	sibling->colour = child->parent->colour;
	child->parent->colour = black;
	if ( child == child->parent->left){
		sibling->right->colour = black;
		rotate_left_rbtree(child->parent,tree);
	} else {
		sibling->left->colour = black;
		rotate_right_rbtree(child->parent,tree);
	}

remove_end:
	/*  Delelte phantom node */
	if ( phantom ){
		if ( NULL!=phantom->parent){
			if      (phantom->parent->left == phantom) phantom->parent->left = NULL;
			else if (phantom->parent->right == phantom) phantom->parent->right = NULL;
			else abort();
		}
		if(tree->root==phantom){tree->root = NULL;}
		free(phantom);
	}
	return retval;
}

void * strcopykey(const void * key){
	char * newkey = calloc(strlen((const char *)key)+1,sizeof(char));
	strcpy(newkey,(const char *)key); /* Automatically null terminated since calloc'd */
	return (void *)newkey;
}

void strfreekey (void * key){
	free(key);
}

RBITER iter_rbtree (const RBTREE tree){
	assert(NULL!=tree);
	RBITER iter = malloc(sizeof(struct __rbiter));
	iter->current = tree->root;
	iter->last = NULL;
	return iter;
}

void freeiter_rbtree( RBITER iter){
	assert(NULL!=iter);
	free(iter);
}

RBNODE iteratedown_rbtree( RBNODE node){
	while(NULL!=node->left) node = node->left;
	return (NULL==node->right)?node:iteratedown_rbtree(node->right);
}

bool next_rbtree ( RBITER rbit ){
	assert(NULL!=rbit);

	if ( rbit->current == rbit->last){
		/* Asscending tree */
		rbit->current = rbit->current->parent;
	}
	/*  No tree or passed root  */
	if ( NULL==rbit->current){
                goto rbtree_next_ret;
        }


	if ( NULL!=rbit->current->left && rbit->last==rbit->current->parent){
		/*  Come from parent and have left node  */
		rbit->current = iteratedown_rbtree(rbit->current->left);
		rbit->last = rbit->current;
	} else if (NULL!=rbit->current->right && rbit->last!=rbit->current->right) {
		/*  Have right node and have not come from right  */
		rbit->current = iteratedown_rbtree(rbit->current->right);
		rbit->last = rbit->current;
	} else {
		/* No more leaves to descent */
		rbit->last = rbit->current;
		//rbit->current = rbit->current->parent;
		goto rbtree_next_ret;
	}

	
rbtree_next_ret:
	if ( NULL==rbit->current){
		free(rbit);
		return false;
	}
	return true;
}

const void * itervalue_rbtree ( const RBITER iter){
	return iter->current->value;
}

const void * iterkey_rbtree ( const RBITER iter){
	return iter->current->key;
}

	

#ifdef TEST
#include <limits.h>

unsigned int * random_permutation (const unsigned int nelt){
	unsigned int * rperm = calloc(nelt,sizeof(unsigned int));
	
	for ( int j=0 ; j<nelt ; j++){
		unsigned int k = (int)(j*((double)random()/LONG_MAX));
		rperm[j] = rperm[k];
		rperm[k] = j;
	}
	return rperm;
}

void print_rperm ( const unsigned int * rperm, const unsigned int nelt){
	printf("%d",rperm[0]);
	for ( int i=1 ; i<nelt ; i++){
		printf(" %d",rperm[i]);
	}
	fputc('\n',stdout);
}

char random_char(void){
	return 65+(int)(26*((double)random()/LONG_MAX));
}
	
char * random_key (const unsigned int keylen){
	char * key = calloc(keylen+1,sizeof(char));
	for ( int i=0 ; i<keylen ; i++){
		key[i] = random_char();
	}
	return key;
}

char ** random_keys ( const unsigned int nelt, const unsigned int keylen){
	char ** keys = calloc(nelt,sizeof(char *));
	for ( int i=0 ; i<nelt ; i++){
		keys[i] = random_key(keylen);
	}
	return keys;
}

int main ( int argc, char * argv[]) {
	unsigned int seed,nelt,keylen;
	if ( argc!=4){
		printf ("Usage: rbtree seed nelt keylen\n");
		return EXIT_FAILURE;
	}
	sscanf(argv[1],"%u",&seed); srandom(seed);
	sscanf(argv[2],"%u",&nelt);
	sscanf(argv[3],"%u",&keylen);

	RBTREE tree = create_rbtree(lexo,strcopykey,strfreekey);
	char ** keys = random_keys(nelt,keylen);
	printf ("Inserting elements\n");
	for ( int i=0 ; i<nelt ; i++){
		printf ("\tinserting %s\n",keys[i]);
		insertelt_rbtree(tree,keys[i],"a");
		check_rbtree(tree);
	}
	unsigned int ntree_elt = nmemb_rbtree(tree);
	printf ("Tree contains %u elements in total\n",ntree_elt);
	assert(ntree_elt<=nelt);


	printf ("Copying tree\n");
	RBTREE tree2 = copy_rbtree(tree,strcopykey);
	check_rbtree(tree2);
	printf("Freeing copied tree\n");
	free_rbtree(tree2,free);

	printf("Printing tree\n");
	unsafemap_rbtree (tree,print_node);

	printf("Iterating through tree\n");
	unsigned int iter_count = 0;
	for ( RBITER iter = iter_rbtree(tree) ; next_rbtree(iter) ; ){
		const char * key = (const char *) iterkey_rbtree(iter);
		printf("\tfound %s\n",key);
		iter_count++;
	}
	assert(iter_count==ntree_elt);  

	printf ("Removing elements\n");
	unsigned int * rperm = random_permutation(nelt);
	fputs("Permutation: ",stdout);
	print_rperm(rperm,nelt);
	for ( int i=0 ; i<nelt ; i++){
		printf("\tremoving %s\n",keys[rperm[i]]);
		removeelt_rbtree(tree,keys[rperm[i]]);
		check_rbtree(tree);
	}
	assert(nmemb_rbtree(tree)==0);
	free_rbtree(tree,free);
}
#endif
