/* TreeTimeJeff.c
   Copyright, Ziheng Yang, June 2003.

     cc -O3 -o TreeTimeJeff TreeTimeJeff.c tools.c -lm
     cl -Ot -O2 TreeTimeJeff.c tools.c

     TreeTimeJeff <MultidivtimeOutputFile>

   This reads the output from Jeff Thorne's multidivtime to print out
   a tree with branch lengthes calculated using the posterior means of
   divergence times.  The output tree can then be read in from Rod
   Page's TreeView.  This is for making a tree like Figure 1 of Yang &
   Yoder (2003 Syst Biol), the cute-looking paper on mouse lemurs.
   Suppose the output from multidivtime is o.md.  Run the program by

   TreeTimeJeff o.md
   TreeTimeJeff o.md > z.trees

   Then edit out everything except the tree in z.trees.  Read the tree
   from TreeView, change fonts etc., save it as a picture file and
   import it into powerpoint.  Use excel to make up an x-axis, of
   reasonable length, to be used as the time scale.  Delete everything
   else and copy the x-axis into powerpoint.  Resize the tree to match
   up with the time axis.

*/

#include "paml.h"
#define NS            1000
#define NBRANCH       (NS*2-2)
#define MAXNSONS      100

struct CommonInfo {
   char *z[2*NS-1], spname[NS][20], cleandata;
   int ns, ls, npatt, np, ntime, ncode, clock, model, icode;
   int seqtype, *pose;
   double *conP, *fpatt;
}  com;
struct TREEB {
   int nbranch, nnode, root, branches[NBRANCH][2];
}  tree;
struct TREEN {
   int father, nson, sons[NS], ibranch;
   double branch, age, label, *conP;
  char *nodeStr;
}  nodes[2*NS-1];

#define NODESTRUCTURE
#include "treesub.c"

void main (int argc, char*argv[])
{
   int  lline=32000, i,j, ch, jeffnode, inode;
   char line[32000], mcmcf[96]="o.multidivtime";
   FILE *fmcmc;
   double t;

   puts("Usage:\n\tTreeTimeJeff <MultidivtimeOutputFile>\n");
   if(argc>1) strcpy(mcmcf, argv[1]);
   fmcmc=gfopen(mcmcf, "r");

   /* Read root node number */
   for( ; ; ) {
	   if(fgets(line, lline, fmcmc) == NULL) error2("EOF mcmc file");
      if(strstr(line, "Root node number of master tree is")==NULL) continue;
      sscanf(line+35, "%d", &j);
      com.ns=j/2+1;
      break;
   }
   printf("Tree has %d taxa.\n\n", com.ns);

   /* read tree.  JeffNode read into [].branch */
   for(; ; ) {
	   ch=fgetc(fmcmc);
	   if(ch==EOF) error2("EOF treefile");
	   if(ch=='(') 
         { ungetc(ch,fmcmc); break; }
   }
   ReadTreeN(fmcmc, &i, &j, 2, 0);
   OutTreeN(F0,1,0);  FPN(F0);  FPN(F0);

   /* read posterior time estimates */
   for(i=0; i<tree.nnode; i++) nodes[i].age=0;
   for( ; ; ) {
	   if(fgets(line, lline, fmcmc) == NULL) error2("EOF mcmc file");
      if(strstr(line, "Actual time node")==NULL) continue;
      sscanf(line+17, "%d =%lf", &jeffnode, &t);
      if(jeffnode<com.ns) {
         if(t>0) nodes[inode].age=t;
      }
      else {
         inode=tree.nnode-1+com.ns-jeffnode;
         printf("JeffNode %3d ZihengNode %3d time %9.6f\n", jeffnode,inode+1,t);
         nodes[inode].age=t;
         if(inode==com.ns) break;
         if(jeffnode-nodes[inode].branch != 0)
            printf(" node number error. ");
      }
   }
   for(i=0; i<tree.nnode; i++) 
      if(i!=tree.root) nodes[i].branch=nodes[nodes[i].father].age-nodes[i].age;

   FPN(F0);  OutTreeN(F0,1,1);  FPN(F0);
   fclose(fmcmc);
   exit(0);
}
