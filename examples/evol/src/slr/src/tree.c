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

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <assert.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <limits.h>
#include "model.h"
#include "bases.h"
#include "data.h"
#include "tree.h"
#include "utility.h"
#include "mystring.h"

#define TEST(A) { if (! (A) ) return 0; }
#define Free(A) if(*A != NULL){ free(*A); *A=NULL;}

char GetTreeElt (const char **tree_str);
int GetLeafNo (const char **tree_str);
char * GetLeafName ( const char **tree_str);
double GetLength (const char **tree_str);
NODE *create_tree_sub (const char **tree_str, NODE * parent, TREE * tree);
int add_lengths_to_tree (TREE * tree, double *lengths);
NODE *CreateNode (void);
void FreeNode (NODE * node, NODE * parent);
unsigned s_hash(const unsigned char *p);

static void ExtendNode ( NODE * node);
static NODE *CloneTree_sub (const NODE * node, const NODE * parent,
			    const TREE * tree, TREE * tree_new);
static void CheckIsConnected (const NODE * node1, const NODE * node2);
static void CheckIsTree_sub (const NODE * code, const NODE * parent,
			     const TREE * tree);
static void Recurse_forward_sub (const NODE * node, const NODE * parent,
				 void (*fun) (void *, int, int), void *info);
static void Recurse_backward_sub (const NODE * node, const NODE * parent,
				  void (*fun) (void *, int, int), void *info);

void * isleaf_rbmap(const void * key, void * value){
	const NODE * leaf = (NODE *) value;
	assert(NULL!=leaf);
	assert(ISLEAF(leaf));
	return value;
}

void CheckIsTree (const TREE * tree)
{
	int branch;
#ifdef NDEBUG
  return;
#endif

  assert (NULL != tree);
  assert (tree->n_sp > 0);
  assert (tree->n_br > 0);
  assert (tree->n_br >= tree->n_sp);
  //assert(tree->n_br==2*tree->n_sp-3);  // Only holds for binary trees.
  assert (NULL != tree->tstring);
  assert (NULL != tree->tree);
  assert (NULL != tree->branches);
  assert (NULL != tree->leaves);

  assert(nmemb_rbtree(tree->leaves)==tree->n_sp);
  map_rbtree(tree->leaves,isleaf_rbmap);
  
  for ( branch = 0; branch < tree->n_br; branch++) {
    assert (NULL != tree->branches[branch]);
  }

  CheckIsTree_sub (tree->tree, NULL, tree);
}

static void CheckIsConnected (const NODE * node1, const NODE * node2)
{
	int n1_to_n2;
	int n2_to_n1;
#ifdef NDEBUG
  return;
#endif

  n1_to_n2 = find_connection (node1, node2);
  n2_to_n1 = find_connection (node2, node1);

  assert (n1_to_n2 >= 0);
  assert (n2_to_n1 >= 0);

  assert (DBL_EQUALS (node1->blength[n1_to_n2], node2->blength[n2_to_n1]));
}

static void CheckIsTree_sub (const NODE * node, const NODE * parent,
			     const TREE * tree)
{
	int child, bran_num;
#ifdef NDEBUG
  return;
#endif

  child = 0;
  while (child < node->nbran && node->branch[child] != NULL) {
    CheckIsConnected (node, node->branch[child]);
    if (node->branch[child] != parent) {
      CheckIsTree_sub (node->branch[child], node, tree);
    }
    child++;
  }

  assert ((node->bnumber >= 0 && node->bnumber < tree->n_br)
	  || parent == NULL);
  bran_num = find_branch_number (node, tree);
  assert (parent == NULL || (bran_num >= 0 && bran_num < tree->n_br));
  assert (parent == NULL || node->bnumber == bran_num);
}



void create_tree (TREE * tree)
{
  const char *tmp;
  int old_sp;

  assert(NULL==tree->tree);

  tmp = tree->tstring;
  old_sp = tree->n_sp;
  tree->n_sp = 0;
  tree->leaves = create_rbtree(lexo,strcopykey,strfreekey);
  //  Bifurcating tree is upper bound on number of branches
  tree->branches = calloc(2*old_sp-3,sizeof(NODE *));
  tree->tree = create_tree_sub (&tmp, NULL, tree);
  tree->tree->bnumber = tree->n_br;

  assert(old_sp == tree->n_sp);
  CheckIsTree (tree);
}


void print_tree (FILE * out, const NODE * node, const NODE * parent,
		 const TREE * tree)
{
  int a, leaf_flag = 0;

  if (NULL == out)
    out = stdout;
  if (parent == NULL)
    CheckIsTree (tree);

  fprintf (out, "(");

  if (parent == NULL)
    a = -1;
  else
    a = 0;

  while (node->branch[++a] != NULL) {
    if (ISLEAF (CHILD (node, a))) {
      if (leaf_flag == 1){
	fprintf (out, ", ");
      }
      fprintf (out, "%s", CHILD(node,a)->name);
      leaf_flag = 1;
    }
    else {
      if (leaf_flag == 1)
	fprintf (out, ", ");
      print_tree (out, CHILD (node, a), node, tree);
      leaf_flag = 1;
    }
    if (node->blength[a]>=0.){
      fprintf (out, ":%f", node->blength[a]);
    }
  }
  fprintf (out, " )");

  if (parent == NULL)
    fprintf (out, "\n");
}

NODE *CreateNode (void)
{
  NODE *node;
  int i;
  
  node = malloc (sizeof (NODE));
  OOM (node);
  node->plik = NULL;
  node->seq = NULL;
  node->name = NULL;
  node->mat = NULL;
  node->back = NULL;
  node->mid = NULL;
  node->bmat = NULL;
  node->dback = NULL;
  node->bnumber = -1;
  node->nbran = 0;
  node->maxbran = 3;
  node->blength = calloc(3,sizeof(double));
  node->branch  = calloc(3,sizeof(NODE *));
  for ( i=0 ; i<node->maxbran ; i++){
    node->blength[i] = -1.;
    node->branch[i] = NULL;
  }

  return node;
}

static void ExtendNode ( NODE * node){
   NODE ** new_branch;
   double * new_blength;
   int bran;

   assert(NULL!=node);
   assert(node->maxbran>0);
   new_branch  = calloc(2*node->maxbran,sizeof(NODE *));   OOM(new_branch);
   new_blength = calloc(2*node->maxbran,sizeof(double));   OOM(new_blength);

   assert(node->nbran>=0);
   assert(node->nbran<=node->maxbran);
   for ( bran=0 ; bran<node->nbran ; bran++){
      new_branch[bran]  = node->branch[bran];
      new_blength[bran] = node->blength[bran];
   }
   for ( ; bran<2*node->maxbran ; bran++){
      new_branch[bran] = NULL;
      new_blength[bran] = -1.;
   }

   node->maxbran *= 2;
   free(node->branch);
   free(node->blength);
   node->branch  = new_branch;
   node->blength = new_blength;
}






NODE *create_tree_sub (const char **tree_str, NODE * parent, TREE * tree)
{
  NODE *node,*node_new;
  char c;
  int bufflen;
  double l;
  char * name;

  node = CreateNode ();
  if (parent != NULL) {
    node->nbran++;
    node->branch[0] = parent;
  }
  else{
      (*tree_str)++;
  }

  while ( (c = GetTreeElt (tree_str)) != EOF) {
    if (c == '(') {
      node->branch[node->nbran]
	= create_tree_sub (tree_str, node, tree);
      (node->branch[node->nbran])->bnumber = tree->n_br;
      tree->branches[tree->n_br++] = node->branch[node->nbran++];
      if ( node->nbran >= node->maxbran - 1 ){ ExtendNode(node); }
    }
    else if (c == ')') {
      node->branch[node->nbran] = NULL;
      return node;
    }
    else if (c == ',') {
      node_new = CreateNode();
      node->branch[node->nbran] = node_new;
      node_new->bnumber = tree->n_br;
      tree->branches[tree->n_br++] = node->branch[node->nbran];
      CHILD (node, node->nbran)->branch[0] = node;
      CHILD (node, node->nbran)->branch[1] = NULL;
      CHILD (node, node->nbran)->nbran = 1;
      name = GetLeafName(tree_str);
      bufflen = 1+strlen(name);
      node_new->name = malloc (bufflen*sizeof(char));
      strncpy(node_new->name,name,bufflen);
      if ( insertelt_rbtree(tree->leaves,name,node_new) ){
         fprintf(stderr,"Species name %s already used in tree. Please make unique and rerun program.\n",name);
         exit(EXIT_FAILURE);
      }

      tree->n_sp++; node->nbran++;
      if ( node->nbran >= node->maxbran - 1){ ExtendNode(node); }
    }
    else if (c == ':') {
      l = GetLength (tree_str);
      node->blength[node->nbran - 1] = l;
      CHILD (node, node->nbran - 1)->blength[0] = l;
    }

  }

  fprintf (stderr,"Error creating tree.\n");
  fprintf (stderr,"Tree string is %s.\n",*tree_str);
  fprintf (stderr,"This is probably a bug. Please report to tim.massingham@ebi.ac.uk\n");
  print_tree(stderr, parent,parent,tree);
  exit(EXIT_FAILURE);

  return node;
}


char GetTreeElt (const char **tree_str)
{
  char c;

  while (isspace (c = *(*tree_str)++));
  if (c == ')' || c == '(' || c == EOF || c == ':')
    return c;
  /* Two possible cases if read comma. Either next is a leaf, which
   * is indicated by comma-whitespace-char or next is a node, 
   * indicated by comma-whitespace-bracket
   */
  if (',' == c) {
    while (isspace (c = *(*tree_str)++));
    switch(c){
       case '(':	return '('; /*  new node */
       case ':':
       case ',':	fprintf(stderr,"Error reading tree. Found \",%c\".\n",c);
			exit(EXIT_FAILURE);
       default:		*(*tree_str)--;  /*  new leaf */
			return ',';
    }
  }


  /* Case: just created a new node and encountered leaf */
  (*tree_str)--;
  c = ',';

  return c;
}

int GetLeafNo (const char **tree_str)
{
  char no[3];
  int a = 0;

  while (isspace (*(*tree_str))) {
    *(*tree_str)++;
  }
  while (isdigit ((unsigned char) *(*tree_str)) != 0)
    no[a++] = *(*tree_str)++;
  no[a] = '\0';

  (void) sscanf (no, "%d", &a);

  return (a - 1);
}

char * GetLeafName ( const char ** tree_str){
   Mystring string;
   char * ret;

   string = new_mystring(10);

   while(isspace (*(*tree_str))) {
      *(*tree_str)++;
   }

   const char ** tree_str_old = tree_str;
   while ( *(*tree_str) != '\0' ){
      if ( ! isspace(*(*tree_str)) ){
         switch( *(*tree_str) ){
         case '(': case ')': case ';': case ':': case ',':
	        ret = cstring_of_mystring(string);
	        free_mystring(string);
	        return ret;
         default:
            append_char_to_mystring ( *(*tree_str),string);
         }
      }
      *(*tree_str)++;
   }
   fprintf (stderr,"Read past end of tree string trying to read leaf name. %s\n",*tree_str_old);
   exit(EXIT_FAILURE);
   return NULL;
}


double GetLength (const char **tree_str)
{
  char no[25];
  unsigned char c;
  double l;
  int a = 0;
  int maxlen = 24;

  do {
    no[a++] = *(*tree_str)++;
    c = (unsigned char) *(*tree_str);
  } while (a < maxlen
	   && (isdigit (c) != 0 || c == 'e' || c == '-' || c == '.'
	       || c == '+'));
  no[a] = '\0';
  while (isdigit (c) != 0 || c == 'e' || c == '-' || c == '.' || c == '+') {
    (*tree_str)++;
    c = (unsigned char) *(*tree_str);
  }

  (void) sscanf (no, "%le", &l);

  return l;
}

int add_lengths_to_tree (TREE * tree, double *lengths)
{
  int a, b;

  CheckIsTree (tree);
  assert (NULL != lengths);

  for (a = 0; a < tree->n_br; a++) {
    (tree->branches[a])->blength[0] = lengths[a];
    b = find_connection (CHILD (tree->branches[a], 0), tree->branches[a]);

    CHILD (tree->branches[a], 0)->blength[b] = lengths[a];
  }

  CheckIsTree (tree);

  return 0;
}


int find_connection (const NODE * from, const NODE * to)
{
  int a = -1;

  while (from->branch[++a] != NULL && from->branch[a] != to);

  if (from->branch[a] == NULL)
    return -1;

  return a;
}


int find_branch_number (const NODE * branch, const TREE * tree)
{
  int a = -1;

  while (++a < tree->n_br && tree->branches[a] != branch);
  assert (a == branch->bnumber || a == tree->n_br);

  return a;
}


void PrintBranchLengths (FILE * fp, const TREE * tree)
{
  int a;

  CheckIsTree (tree);

  for (a = 0; a < tree->n_br; a++)
    fprintf (fp,"Branch %d = %e\n", a, (tree->branches[a])->blength[0]);
}


void ScaleTree (TREE * tree, const double f)
{
  int i, j;
  NODE *node;

  CheckIsTree (tree);

  /* Cycle though all nodes */
  for (i = 0; i < tree->n_br; i++) {
    node = tree->branches[i];
    j = 0;
    while (j < node->nbran && node->branch[j] != NULL) {
      node->blength[j] *= f;
      j++;
    }
  }
  /* Do root */
  node = tree->tree;
  j = 0;
  while (j < node->nbran && node->branch[j] != NULL) {
    node->blength[j] *= f;
    j++;
  }

  CheckIsTree (tree);
}


TREE *CopyTree (const TREE * tree)
{
  TREE *tree_new;

  CheckIsTree (tree);

  tree_new = copy_tree_strings (tree);
  create_tree (tree_new);

  CheckIsTree (tree_new);
  return tree_new;
}

void * intpcopy(const void * intp){
	assert(NULL!=intp);
	int * new_intp = malloc(sizeof(int));
	*new_intp = *(int *)intp;
	return new_intp;
}

TREE *CloneTree (TREE * tree)
{
  TREE *tree_new;

  CheckIsTree (tree);

  tree_new = calloc (1, sizeof (TREE));
  if (NULL == tree_new)
    return NULL;

  tree_new->n_sp = tree->n_sp;
  tree_new->n_br = tree->n_br;
  tree_new->tstring = malloc ((1 + strlen (tree->tstring)) * sizeof (char));
  strcpy (tree_new->tstring, tree->tstring);
  tree_new->leaves = create_rbtree(lexo,strcopykey,strfreekey);
  tree_new->branches = calloc(tree->n_br,sizeof(NODE *));
  tree_new->tree = CloneTree_sub (tree->tree, NULL, tree, tree_new);

  CheckIsTree (tree_new);
  return tree_new;
}

static NODE *CloneTree_sub (const NODE * node, const NODE * parent,
			    const TREE * tree, TREE * tree_new)
{
  NODE *node_new;
  int ln, n;
  int bufflen;

  node_new = CreateNode ();
  OOM (node_new);
  node_new->bnumber = node->bnumber;

  n = 0;
  while (node->branch[n] != NULL) {
    if (node->branch[n] != parent) {
      node_new->branch[n] =
	CloneTree_sub (node->branch[n], node, tree, tree_new);
      // Connect all children to parent
      (node_new->branch[n])->branch[0] = node_new;
    }
    node_new->blength[n] = node->blength[n];
    n++;
  }
  node_new->branch[n] = NULL;


  // If on a leaf, then update leaves index
  if (ISLEAF (node)) {
    bufflen = 1 + strlen(node->name);
    node_new->name = malloc(bufflen*sizeof(char));
    strncpy(node_new->name,node->name,bufflen);
    insertelt_rbtree(tree_new->leaves,node_new->name,node_new);
  }
  // If not at root node, then in branch index
  if (NULL != parent) {
    ln = find_branch_number (node, tree);
    assert (node_new->bnumber == ln);
    tree_new->branches[ln] = node_new;
  }

  return node_new;
}


void FreeTree (TREE * tree)
{

  CheckIsTree (tree);

  FreeNode (tree->tree, NULL);
  Free (&tree->tstring);
  Free (&tree->branches);
  free_rbtree(tree->leaves,free);
  Free (&tree);
}

void FreeNode (NODE * node, NODE * parent)
{
  int i = 0;

  while (i < node->nbran && node->branch[i] != NULL) {
    if (node->branch[i] != parent) {
      FreeNode (node->branch[i], node);
    }
    i++;
  }

  Free (&node->branch);
  Free (&node->blength);
  Free (&node->seq);
  Free (&node->name);
  Free (&node->plik);
  Free (&node->mid);
  Free (&node->back);
  Free (&node->dback);
  Free (&node->mat);
  Free (&node->bmat);
  Free (&node);
}



void Recurse_forward (const TREE * tree, void (*fun) (void *, int, int),
		      void *info)
{
  NODE *node;
  int i;

  assert (NULL != tree);
  assert (NULL != fun);
  assert (NULL != info);

  node = tree->tree;
  i = 0;
  while (i < node->nbran && node->branch[i] != NULL) {
    Recurse_forward_sub (node->branch[i], node, fun, info);
    i++;
  }
}

static void Recurse_forward_sub (const NODE * node, const NODE * parent,
				 void (*fun) (void *, int, int), void *info)
{
  int i;

  assert (NULL != node && NULL != parent);
  assert (NULL != fun && NULL != info);

  /*  Recurse through all children of node */
  i = 0;
  while (i < node->nbran && node->branch[i] != NULL) {
    if (node->branch[i] != parent) {
      Recurse_forward_sub (node->branch[i], node, fun, info);
    }
    i++;
  }

  /*  Finished recursion, run function on this branch */
  fun (info, node->bnumber, parent->bnumber);
}

void Recurse_backward (const TREE * tree, void (*fun) (void *, int, int),
		       void *info)
{
  NODE *node;
  int i;

  assert (NULL != tree);
  assert (NULL != fun);
  assert (NULL != info);

  node = tree->tree;
  i = 0;
  while (i < node->nbran && node->branch[i] != NULL) {
    fun (info, node->branch[i]->bnumber, node->bnumber);
    Recurse_backward_sub (node->branch[i], node, fun, info);
    i++;
  }
}

static void Recurse_backward_sub (const NODE * node, const NODE * parent,
				  void (*fun) (void *, int, int), void *info)
{
  int i;

  assert (NULL != node && NULL != parent);
  assert (NULL != fun && NULL != info);

  /*  Recurse through all children of node */
  i = 0;
  while (i < node->nbran && node->branch[i] != NULL) {
    if (node->branch[i] != parent) {
      fun (info, node->branch[i]->bnumber, node->bnumber);
      Recurse_backward_sub (node->branch[i], node, fun, info);
    }
    i++;
  }
}



TREE **read_tree_strings (char *filename)
{
  FILE *fp;
  int n_sp, n_tree;
  TREE **set;
  int a;

  fp = fopen (filename, "r");
  if (fp == NULL) {
    printf ("Could not open tree file \"%s\"\n", filename);
    exit (EXIT_FAILURE);
  }

  fscanf (fp, "%d %d", &n_sp, &n_tree);
  set = calloc ((size_t) (n_tree + 1), sizeof (TREE *));
  OOM (set);
  set[n_tree] = NULL;
  if (n_sp < 0 || n_tree < 0) {
    printf ("Problems reading tree from file");
    fclose (fp);
    return NULL;
  }

  for (a = 0; a < n_tree; a++) {
    set[a] = malloc (sizeof (TREE));
    OOM (set[a]);
    set[a]->tstring = ReadString (fp);
    set[a]->n_sp = n_sp;
    set[a]->n_br = 0;
    set[a]->tree = NULL;
  }

  fclose (fp);

  return set;
}

TREE *copy_tree_strings (const TREE * tree)
{
  TREE *new_tree;
  int a;

  if (tree == NULL)
    return NULL;
  new_tree = malloc (sizeof (TREE));
  new_tree->n_sp = tree->n_sp;
  new_tree->n_br = 0;
  a = strlen (tree->tstring) + 1;
  new_tree->tstring = malloc (a * sizeof (char));
  strncpy (new_tree->tstring, tree->tstring, a);
  new_tree->tree = NULL;

  return new_tree;
}


int save_tree_strings (char *filename, TREE ** trees)
{
  FILE *fp;
  int a;
  int n_tree;

  fp = fopen (filename, "w");
  if (fp == NULL)
    return -1;

  n_tree = 0;
  while (trees[n_tree] != NULL)
    n_tree++;
  fprintf (fp, "%d %d\n", trees[0]->n_sp, n_tree);

  for (a = 0; a < n_tree; a++)
    fprintf (fp, "%s\n", trees[a]->tstring);

  fclose (fp);

  return 0;
}


NODE * find_leaf_by_name ( const char * name, const TREE * tree){
   CheckIsTree(tree);
   assert(NULL!=name);

   NODE * leaf = (NODE *) getelt_rbtree(tree->leaves,name);
   return leaf;
}



VEC branchlengths_from_tree ( const TREE * tree){
	assert(NULL!=tree);
	
	VEC branlength = create_vec(tree->n_br);
	assert(NULL!=branlength);
	for (unsigned int bran=0 ; bran<tree->n_br ; bran++){
		vset(branlength,bran,tree->branches[bran]->blength[0]);
	}
	return branlength;
}


