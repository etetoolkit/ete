/* treespace.c
   collection of tree perturbation routines
*/

#include "paml.h"

int MakeTreeIb (int ns, int Ib[], int rooted)
{
/* construct tree from Ib[] using the algorithm of adding species
   Ib[k] marks the branch to which the (k+3)_th species (or the root) 
   is added.  Ib[k] should be in the range [0,k+3]
*/
   int i,j,k, is,it;

   tree.nbranch=3;
   for (i=0; i<3; i++)  { tree.branches[i][0]=3;  tree.branches[i][1]=i; }
   for (k=0; k<ns-3; k++) {
      is=k+3;       /* add species (is) to branch Ib[k] */

      for (i=0; i<tree.nbranch; i++)  for (j=0; j<2; j++)
         if (tree.branches[i][j]>=is) tree.branches[i][j]+=2;
      it=tree.branches[Ib[k]][1];
      tree.branches[Ib[k]][1]=is+1;
      tree.branches[tree.nbranch][0]=is+1;
      tree.branches[tree.nbranch++][1]=it;
      tree.branches[tree.nbranch][0]=is+1;
      tree.branches[tree.nbranch++][1]=is;
   }
   tree.root=tree.branches[0][0];
   BranchToNode ();
   
   if (rooted) {
      it=tree.branches[Ib[k]][0];
      tree.branches[Ib[k]][0]=tree.branches[tree.nbranch][0]=2*com.ns-2;
      tree.branches[tree.nbranch][1]=it;
      for (; it!=tree.root;  it=nodes[it].father) {
         tree.branches[nodes[it].ibranch][0]=it;
         tree.branches[nodes[it].ibranch][1]=nodes[it].father;
      }
      tree.root=2*com.ns-2;  tree.nbranch++;
      BranchToNode ();
   }
   return (0);
}

int GetTreeI (int itree, int ns, int rooted)
{
/* get the i_th tree.  Trees are ordered according to the algorithm of 
   adding species.
   returns a random tree if itree==-1, in which case ns can be large
*/
   int i, M[NS-2], nM=ns-3+rooted, Ib[NS-2];

   for (i=0; i<nM-1; i++) M[i]=2*i+5;
   for (i=0,M[nM-1]=1; i<nM-2; i++) M[nM-1-i-2]*=M[nM-1-i-1];

   if (itree==-1)  for (i=0; i<nM; i++) Ib[i]=(int)((2*i+3)*rndu());
   else            for (i=0; i<nM; i++) {Ib[i]=itree/M[i]; itree%=M[i]; } 
/*
   if (noisy>3) {
      FOR (i, nM) printf ("%5d ", M[i]);   FPN (F0);
      FOR (i, nM) printf ("%5d ", Ib[i]);  FPN (F0);
   }
*/
   MakeTreeIb (ns, Ib, rooted);
   return (0);
}


/*
int NumberofTrees (int ns, int rooted)
{
   int i, ntree=1;

   if (ns>15) error2 ("ns too large in NumberofTrees().");
   for (i=4; i<=ns; i++)  ntree *= 2*i-5;
   if (rooted) ntree *= 2*i-3;
   return (ntree);
}
*/


int CountLHistories (void)
{
/* This counts the number of labeled histories for a given rooted tree.
*/
   int i,k, nLH, nLR[NS-1][2], change, *sons, j;
   double y=0;

   for(i=com.ns; i<tree.nnode; i++) 
     if(nodes[i].nson!=2) error2("this works for rooted trees only");
   for(i=com.ns; i<tree.nnode; i++) 
      nLR[i-com.ns][0] = nLR[i-com.ns][1] = -1;
   for(k=0; k<com.ns; k++) {
      for(i=com.ns,change=0; i<tree.nnode; i++) {
         sons = nodes[i].sons;
         for(j=0; j<2; j++) {
            if(nLR[i-com.ns][j] != -1) continue;
            if(sons[j] < com.ns) {
               nLR[i-com.ns][j] = 0;
               change = 1;
            }
            else if(nLR[sons[j]-com.ns][0] != -1 && nLR[sons[j]-com.ns][1] != -1) {
               nLR[i-com.ns][j] = nLR[sons[j]-com.ns][0] + nLR[sons[j]-com.ns][1] + 1;
               change = 1;
            }
         }
      }
      if(!change) break;
   }
   for(i=0,nLH=1; i<tree.nnode-com.ns; i++) {
      /*
      printf("\nnode %2d (%2d %2d): %2d %2d ", i+com.ns, nodes[i+com.ns].sons[0], nodes[i+com.ns].sons[1], nLR[i][0], nLR[i][1]);
      */
      if(nLR[i][0]==-1 || nLR[i][1]==-1)
         error2("nLR = -1");
      if(nLR[i][0] && nLR[i][1]) {
         nLH *= (int)Binomial((double)(nLR[i][0]+nLR[i][1]), min2(nLR[i][0], nLR[i][1]), &y);
         if(y) error2("y!=0 not considered");
      }
   }
   return(nLH);   
}



int ListTrees (FILE* fout, int ns, int rooted)
{
/* list trees by adding species, works fine with large ns
*/
   int NTrees, NTreeRoot=3;
   int i, Ib[NS-2], ns1=ns+rooted, nM=ns1-3, finish;

   if(com.ns<=12) {
      printf ("%20s%20s%20s\n", "Taxa", "Unrooted trees", "Rooted trees");
      for (i=4,NTrees=1; i<=com.ns; i++)  
         printf ("%20d%20d%20d\n", i, (NTrees*=2*i-5), (NTreeRoot*=2*i-3));
      fprintf (fout, "%10d %10d\n", com.ns, (!rooted?NTrees:NTreeRoot));
   }

   if(com.ns<=26) {
      for (i=0; i<com.ns; i++)
         sprintf(com.spname[i], "%d", i+1);
   }

   for (i=0;i<nM;i++) Ib[i]=0;
   for (NTrees=0; ; ) {
      MakeTreeIb(ns, Ib, rooted);
      OutTreeN(fout, (com.ns<=26), 0);

      if(rooted) fprintf(fout, " [%7d %6d LHs]\n", NTrees++, CountLHistories());
      else fprintf(fout, " [%7d]\n", NTrees++);

      for (i=nM-1,Ib[nM-1]++,finish=0; i>=0; i--) {
         if (Ib[i]<2*i+3) break;
         if (i==0) { 
            finish=1; 
            break;
         }
         Ib[i]=0; Ib[i-1]++; 
      }
      if (finish) break;
   }
   FPN(fout);

   return (0);
}

int GetIofTree (int rooted, int keeptree, double space[])
{
/* Get the index of tree.
   tree.branches[] are destroyed for reconstruction, 
   and some branches are reversed which may affect nodes[] also.
   Both are restored before return if keeptree=1.
   Works with binary trees only.
   bA[nbranch*(ns-2)]
*/
   int M[NS-2], nM=com.ns-3+rooted;
   int i,j,k,is,it, b=0,a1,a2,Ib[NS-1], nid=tree.nnode-com.ns;
   char ns2=(char)(com.ns-2), *bA=(char*)space;  /* bA[b*ns2+j]: ancestors on branch b */
   struct TREEB tree0=tree;

   if (tree.nnode-com.ns!=com.ns-1-!rooted) error2 ("GetIofTree");
   if (com.ns>15) error2("ns too large in GetIofTree");

   /* find new root. 
      Ib[]: No. of times inner nodes are visited on paths 1-2, 1-3, 2-3 */
   for (i=0; i<nid; i++) Ib[i]=0;
   for (i=0; i<2; i++)  for (j=i+1; j<3; j++)  {
      for (a1=i; a1!=-1; a1=nodes[a1].father) {
         for (a2=j; a2!=-1; a2=nodes[a2].father)  if (a1==a2) break;
         if (a1==a2) break;
      }
      for (k=0,Ib[a1-com.ns]++; k<2; k++) {  /* a1 is ancestor of i and j */
         a2=k?nodes[i].father:nodes[j].father;
         for (; a2!=a1; a2=nodes[a2].father)  Ib[a2-com.ns]++; 
      }
   }
   /* reset root of tree at it */
   for (it=com.ns; it<com.ns+nid; it++) if (Ib[it-com.ns]==3) break;
   ReRootTree (it);
   for (i=0,tree.nbranch=3; i<3; i++)  {
      tree.branches[i][0]=tree.root;  tree.branches[i][1]=i;
      for (it=nodes[i].father,k=0; it!=tree.root; it=nodes[it].father)
         bA[i*ns2+k++]=(char)it;
      bA[i*ns2+k]=0;
   }
   
   for (is=3; is<com.ns; is++) { /* add species (is) on branch b at node it */
      for (it=nodes[is].father; it!=tree.root; it=nodes[it].father) {
    for (b=0; b<tree.nbranch; b++) if (strchr(bA+b*ns2,it)) break;
    if (b<tree.nbranch) break;
      }
      Ib[is-3]=b;
      tree.branches[tree.nbranch][0]=it;
      tree.branches[tree.nbranch++][1]=tree.branches[b][1];
      tree.branches[tree.nbranch][0]=it;
      tree.branches[tree.nbranch++][1]=is;
      tree.branches[b][1]=it;

      if (is==com.ns-1) break;
      for (i=0; i<3; i++) {  /* modify bA[] for the 3 affected branches */
         if (i) b=tree.nbranch-3+i;
         it=nodes[tree.branches[b][1]].father; 
         for (k=0; it!=tree.branches[b][0]; it=nodes[it].father) 
            bA[b*ns2+k++]=(char)it;
         bA[b*ns2+k]=0;
      }
   }  /* for (is) */
   if (rooted) {
      a1=nodes[k=tree0.root].sons[0];  a2=nodes[tree0.root].sons[1];
      if (nodes[a1].father==k)      k=a1;
      else if (nodes[a2].father==k) k=a2;
      else error2 ("rooooot");
      for (b=0; b<tree.nbranch; b++) if (tree.branches[b][1]==k) break;
      Ib[nM-1]=b;
   }
   if (keeptree)  { tree=tree0;  BranchToNode (); }

   for (i=0; i<nM-1; i++) M[i]=2*i+5;
   for (i=0,M[nM-1]=1; i<nM-2; i++) M[nM-1-i-2]*=M[nM-1-i-1];
   for (i=0,it=0; i<nM; i++) it+=Ib[i]*M[i];
   return (it);
}


void ReRootTree (int newroot)
{
/* reroot tree at newroot.  oldroot forgotten
   The order of branches is not changed.  
   Branch lengths, and other parameters for branches are updated.
   Note that node inode needs to be updated if com.oldconP[inode] == 0.
*/
   int oldroot=tree.root, a,b;  /* a->b becomes b->a */

   if (newroot==oldroot) return;
   for (b=newroot,a=nodes[b].father; b!=oldroot; b=a,a=nodes[b].father) {
      tree.branches[nodes[b].ibranch][0]=b;
      tree.branches[nodes[b].ibranch][1]=a;
#if (BASEML || CODEML)
      if(a>=com.ns /* && com.method==1 */) com.oldconP[a]=0;  /* update the node */
#endif
   }

   tree.root=newroot;
   BranchToNode ();
   for (b=oldroot,a=nodes[b].father; b!=newroot; b=a,a=nodes[b].father)
      { nodes[b].branch=nodes[a].branch; nodes[b].label=nodes[a].label; }
   nodes[newroot].branch=-1;  nodes[newroot].label=-1;

#if (CODEML)
   /* omega's are moved in updateconP for NSbranchsites models */
   if(com.model && com.NSsites==0) { 
      for (b=oldroot,a=nodes[b].father; b!=newroot; b=a,a=nodes[b].father)
         nodes[b].omega=nodes[a].omega;
      nodes[newroot].omega=-1;
   }
#endif
#if (BASEML)
   if(com.nhomo==2) { 
      for (b=oldroot,a=nodes[b].father; b!=newroot; b=a,a=nodes[b].father)
         nodes[b].kappa=nodes[a].kappa;
      nodes[newroot].kappa=-1;
   }
#endif

}



int NeighborNNI (int i_tree)
{
/* get the i_tree'th neighboring tree of tree by the nearest neighbor 
   interchange (NNI), each tree has 2*(# internal branches) neighbors.
   works with rooted and unrooted binary trees.

   Gives the ip_th neighbor for interior branch ib. 
   Involved branches are a..b, a..c, b..d,
   with a..b to be the internal branch.
   swap c with d, with d to be the ip_th son of b
*/ 
   int i, a,b,c,d, ib=i_tree/2, ip=i_tree%2;

   if (tree.nbranch!=com.ns*2-2-(nodes[tree.root].nson==3)) 
      error2 ("err NeighborNNI: multificating tree.");

   /* locate a,b,c,d */
   for (i=0,a=0; i<tree.nbranch; i++)
      if (tree.branches[i][1]>=com.ns && a++==ib) break;
   ib=i;
   a=tree.branches[ib][0];  b=tree.branches[ib][1];
   c=nodes[a].sons[0];      if(c==b) c=nodes[a].sons[1];
   d=nodes[b].sons[ip];

   /* swap nodes c and d */
   tree.branches[nodes[c].ibranch][1]=d;
   tree.branches[nodes[d].ibranch][1]=c;
   BranchToNode ();
   return (0);
}

int GetLHistoryI (int iLH)
{
/* Get the ILH_th labelled history.  This function is rather similar to 
   GetTreeI which returns the I_th rooted or unrooted tree topology.
   The labeled history is recorded in the numbering of nodes: 
   node # increases as the node gets older: 
   node d corresponds to time 2*ns-2-d; tree.root=ns*2-2;
   t0=1 > t1 > t2 > ... > t[ns-2]
   k ranges from 0 to i(i-1)/2 and indexes the pair (s1 & s2, with s1<s2),
   out of i lineages, that coalesce.
*/
   int i,k, inode, nodea[NS], s1, s2, it;

   tree.nnode=com.ns*2-1;
   for (i=0; i<tree.nnode; i++)  {
      nodes[i].father=nodes[i].nson=-1;  FOR (k,com.ns) nodes[i].sons[k]=-1;
   }
   for (i=0,inode=com.ns; i<com.ns; i++) nodea[i]=i;
   for (i=com.ns,it=iLH; i>=2; i--)  {
      k=it%(i*(i-1)/2);  it/=(i*(i-1)/2); 
      s2=(int)(sqrt(1.+8*k)-1)/2+1;  s1=k-s2*(s2-1)/2; /* s1<s2, k=s2*(s2-1)/2+s1 */

      if (s1>=s2 || s1<0)  printf("\nijk%6d%6d%6d", s1, s2, k);

      nodes[nodea[s1]].father=nodes[nodea[s2]].father=inode;
      nodes[inode].nson=2;
      nodes[inode].sons[0]=nodea[s1];
      nodes[inode].sons[1]=nodea[s2];
      nodea[s1]=inode;  nodea[s2]=nodea[i-1]; 
      inode++;
   }
   tree.root=inode-1;
   NodeToBranch();
   return (0);
}

int GetIofLHistory (void)
{
/* Get the index of the labelled history (rooted tree with nodes ordered
   according to time).  
   Numbering of nodes: node # increases as the node gets older:
   node d corresponds to time 2*ns-2-d; tree.root=ns*2-2;
   t0=1 > t1 > t2 > ... > t[ns-2]
*/
   int index, i,j,k[NS+1], inode,nnode, nodea[NS], s[2];

   if (nodes[tree.root].nson!=2 || tree.nnode!=com.ns*2-1
     || tree.root!=com.ns*2-2)  error2("IofLH");
   for (i=0; i<com.ns; i++) nodea[i]=i;
   for (inode=nnode=com.ns,index=0; inode<com.ns*2-1; inode++,nnode--) {
      FOR (i,2) FOR (j,nnode)  
         if (nodes[inode].sons[i]==nodea[j]) { s[i]=j; break; }
      k[nnode]=max2(s[0],s[1]); s[0]=min2(s[0],s[1]); s[1]=k[nnode];
      k[nnode]=s[1]*(s[1]-1)/2+s[0];
      nodea[s[0]]=inode; nodea[s[1]]=nodea[nnode-1];
   }
   for (nnode=2,index=0; nnode<=com.ns; nnode++)
      index=nnode*(nnode-1)/2*index+k[nnode];
   return (index);
}


int ReorderNodes (char LHistory[])
{
/* changes interior node numbers so that the topology represent a labeled
   history.  LHistory recordes the order of interior nodes with [0] to be 
   root, and [ns-2] the youngest node.   
   Changes node LHistory[k] to com.ns*2-3-k.  
   Uses only tree but not nodes[] but transforms both tree and nodes into 
   the labeled history.
*/
   int i, j, k;

   if (tree.root!=com.ns*2-2 || LHistory[0]!=com.ns*2-2) {
      tree.root=com.ns*2-2;
/*      printf("\nRoot changed to %d in ReorderNodes..\n", com.ns*2-2+1); */
   }
   FOR (i, tree.nbranch) FOR (j,2) 
      if (tree.branches[i][j]>=com.ns) 
         FOR (k, com.ns-1)
            if (tree.branches[i][j]==LHistory[k]) 
               { tree.branches[i][j]=com.ns*2-2-k;  break; }
   BranchToNode();

   return (0);
}
