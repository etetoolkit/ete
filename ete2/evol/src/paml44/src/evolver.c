/* evolver.c
   Copyright, Ziheng Yang, April 1995.

     cl -Ot -O2 evolver.c tools.c
     cl -Ot -O2 -DCodonNSbranches    -FeevolverNSbranches.exe    evolver.c tools.c
     cl -Ot -O2 -DCodonNSsites       -FeevolverNSsites.exe   evolver.c tools.c
     cl -Ot -O2 -DCodonNSbranchsites -FeevolverNSbranchsites.exe evolver.c tools.c

     cc -fast -o evolver evolver.c tools.c -lm
     cc -O4 -DCodonNSbranches -o evolverNSbranches evolver.c tools.c -lm
     cc -O4 -DCodonNSsites -o evolverNSsites evolver.c tools.c -lm
     cc -O4 -DCodonNSbranchsites -o evolverNSbranchsites evolver.c tools.c -lm

     evolver
     evolver 5 MCbase.dat
     evolver 6 MCcodon.dat
     evolver 7 MCaa.dat
     evolver 9 <MasterTreeFile> <TreesFile>
*/

/*
#define CodonNSbranches
#define CodonNSsites
#define CodonNSbranchsites
*/

#include "paml.h"

#define NS            7000
#define NBRANCH       (NS*2-2)
#define MAXNSONS      100
#define LSPNAME       50
#define NCODE         64
#define NCATG         40

struct CommonInfo {
   char *z[2*NS-1], spname[NS][LSPNAME+1], daafile[96], cleandata, readpattern;
   int ns, ls, npatt, np, ntime, ncode, clock, rooted, model, icode;
   int seqtype, *pose, ncatG, NSsites;
   double *fpatt, kappa, omega, alpha, pi[64], *conP, daa[20*20];
   double freqK[NCATG], rK[NCATG];
   char *siteID;    /* used if ncatG>1 */
   double *siterates;   /* rates for gamma or omega for site or branch-site models */
   double *omegaBS, *QfactorBS;     /* omega IDs for branch-site models */
}  com;
struct TREEB {
   int nbranch, nnode, root, branches[NBRANCH][2];
}  tree;
struct TREEN {
   int father, nson, sons[MAXNSONS], ibranch;
   double branch, age, omega, label, *conP;
   char *nodeStr, fossil;
}  *nodes;

extern char BASEs[];
extern int GeneticCode[][64], noisy;
int LASTROUND=0; /* not used */

#define EVOLVER
#define NODESTRUCTURE
#define BIRTHDEATH
#include "treesub.c"
#include "treespace.c"

void TreeDistances(FILE* fout);
void Simulate(char*ctlf);
void MakeSeq(char*z, int ls);
int EigenQbase(double rates[], double pi[], 
    double Root[],double U[],double V[],double Q[]);
int EigenQcodon (int getstats, double kappa,double omega,double pi[],
    double Root[], double U[], double V[], double Q[]);
int EigenQaa(double pi[],double Root[], double U[], double V[],double Q[]);
void CladeProbabilities (char treefile[]);
void CladeSupport (char tree1f[], char treesf[], int burnin);
int between_f_and_x(void);
void LabelClades(FILE *fout);

void Rell2MLtree(int argc, char *argv[]);



char *MCctlf0[]={"MCbase.dat","MCcodon.dat","MCaa.dat"};
char *seqf[3]={"mc.paml", "mc.paml", "mc.nex"};

enum {JC69, K80, F81, F84, HKY85, T92, TN93, REV} BaseModels;
char *basemodels[]={"JC69","K80","F81","F84","HKY85","T92","TN93","REV"};
enum {Poisson, EqualInput, Empirical, Empirical_F} AAModels;
char *aamodels[]={"Poisson", "EqualInput", "Empirical", "Empirical_F"};


double PMat[NCODE*NCODE], U[NCODE*NCODE], V[NCODE*NCODE], Root[NCODE];
static double Qfactor=-1, Qrates[5];  /* Qrates[] hold kappa's for nucleotides */


int main (int argc, char*argv[])
{
   char *MCctlf=NULL, outf[96]="evolver.out", file1[96]="truetree",file2[96]="rst1";
   int i, option=6, ntree=1,rooted, BD=0, burnin=0;
   double bfactor=1, birth=-1,death=-1,sample=-1,mut=-1, *space;
   FILE *fout=gfopen(outf,"w");

   /* Rell2MLtree(argc, argv); */

   printf("EVOLVER in %s\n",  VerStr);
   com.alpha=0; com.cleandata=1; com.model=0; com.NSsites=0;

   if(argc==1) printf("Results for options 1-4 & 8 go into %s\n",outf);
   else if(argc!=3 && argc!=4 && argc!=5) {
      puts("Usage: \n\tevolver \n\tevolver option# MyDataFile"); exit(-1); 
   }
   if(argc==3) {
      sscanf(argv[1],"%d",&option);
      MCctlf=argv[2];
      if(option<5 || option>7) error2("command line option not right.");
   }
   else if(argc>=4) {
      sscanf(argv[1],"%d",&option);
      if(option!=9) error2("option not good?");
      strcpy(file1, argv[2]);
      strcpy(file2, argv[3]);
      if(argc>4) sscanf(argv[4],"%d",&burnin);
   }
   else {
      for(; ;) {
         fflush(fout);
         printf("\n\t(1) Get random UNROOTED trees?\n"); 
         printf("\t(2) Get random ROOTED trees?\n"); 
         printf("\t(3) List all UNROOTED trees?\n");
         printf("\t(4) List all ROOTED trees?\n");
         printf("\t(5) Simulate nucleotide data sets (use %s)?\n",MCctlf0[0]);
         printf("\t(6) Simulate codon data sets      (use %s)?\n",MCctlf0[1]);
         printf("\t(7) Simulate amino acid data sets (use %s)?\n",MCctlf0[2]);
         printf("\t(8) Calculate identical bi-partitions between trees?\n");
         printf("\t(9) Calculate clade support values (read 2 treefiles)?\n");
         printf("\t(11) Label clades?\n");
         printf("\t(0) Quit?\n");
#if defined (CodonNSbranches)
         option=6;  com.model=1; 
         MCctlf = (argc==3 ? argv[2] : "MCcodonNSbranches.dat");
#elif defined (CodonNSsites)
         option=6;  com.NSsites=3; 
         MCctlf = (argc==3 ? argv[2] : "MCcodonNSsites.dat");
#elif defined (CodonNSbranchsites)
         option=6;  com.model=1; com.NSsites=3; 
         MCctlf = (argc==3 ? argv[2] : "MCcodonNSbranchsites.dat");
#else

         option = 4;
         scanf("%d", &option);
#endif
         if(option==0) exit(0);
         if(option>=5 && option<=7) break;
         if(option<5)  { 
            printf ("No. of species: ");
            scanf ("%d", &com.ns);
         }
         if(com.ns>NS) error2 ("Too many species.  Raise NS.");
         if((space=(double*)malloc(10000*sizeof(double)))==NULL) error2("oom");
         rooted = !(option%2);
         if (option<3) {
            printf("\nnumber of trees & random number seed? ");
            scanf("%d%d",&ntree,&i);  
            SetSeed(i==-1?(int)time(NULL):i);
            printf ("Want branch lengths from the birth-death process (0/1)? ");
            scanf ("%d", &BD);
         }
         if(option<=4) {
            if(com.ns<3) error2("no need to do this?");
            i = (com.ns*2-1)*sizeof(struct TREEN);
            if((nodes=(struct TREEN*)malloc(i)) == NULL) 
               error2("oom");
         }
         switch (option) {
         case(1):
         case(2):
            for(i=0; i<com.ns; i++)          /* default spname */
               sprintf(com.spname[i],"S%d",i+1);
            if(BD) {
               printf ("\nbirth rate, death rate, sampling fraction, and ");
               printf ("mutation rate (tree height)?\n");
               scanf ("%lf%lf%lf%lf", &birth, &death, &sample, &mut);
            }
            for(i=0;i<ntree;i++) {
               RandomLHistory (rooted, space);
               if(BD)  BranchLengthBD (1, birth, death, sample, mut);
               if(com.ns<20&&ntree<10) { OutTreeN(F0,0,BD); puts("\n"); }
               OutTreeN(fout,1,BD);  FPN(fout);
            }
            /* for (i=0; i<com.ns-2-!rooted; i++) Ib[i]=(int)((3.+i)*rndu());
               MakeTreeIb (com.ns, Ib, rooted);
            */
            break;
         case(3):
         case(4): 
            ListTrees(fout, com.ns, rooted);
            break;
         case(8):  TreeDistances(fout);  break;

         case(9):  CladeSupport(file1, file2, burnin);  break;
         /*
         case(9):  CladeProbabilities("/papers/BPPJC3sB/Karol.trees");    break;
         */
         case(10): between_f_and_x();    break;
         case(11): LabelClades(fout);    break;
         default:  exit(0);
         }
      }
   }
   com.seqtype=option-5;  /* 0, 1, 2 for bases, codons, & amino acids */
   Simulate(MCctlf?MCctlf:MCctlf0[option-5]);
   return(0);
}


int between_f_and_x (void)
{
/* this helps with the exponential transform for frequency parameters */
   int i,n,fromf=0;
   double x[100];

   for(;;) {
      printf("\ndirection (0:x=>f; 1:f=>x; -1:end)  &  #classes? ");
      scanf("%d",&fromf);    
      if(fromf==-1) return(0);
      scanf("%d", &n);  if(n>100) error2("too many classes");
      printf("input the first %d values for %s? ",n-1,(fromf?"f":"x"));
      FOR(i,n-1) scanf("%lf",&x[i]);
      x[n-1]=(fromf?1-sum(x,n-1):0);
      f_and_x(x, x, n, fromf, 1);
      matout(F0,x,1,n);
   }
}


void LabelClades(FILE *fout)
{
/* This reads in a tree and scan species names to check whether they form a 
   paraphyletic group and then label the clade.
   It assumes that the tree is unrooted, and so goes through two rounds to check
   whether the remaining seqs form a monophyletic clade.
*/
   FILE *ftree;
   int unrooted=1,iclade, sizeclade, mrca, paraphyl, is, imrca, i,j,k, lasts, haslength;
   char key[96]="A", treef[64]="/A/F/flu/HA.all.prankcodon.tre", *p,chosen[NS], *endstr="end";
   int *anc[NS-1], loc, bitmask, SI=sizeof(int)*8;
   int debug;

   printf("Tree file name? ");
   scanf ("%s", treef);
   printf("Treat tree as unrooted (0 no, 1 yes)? ");
   scanf ("%d", &unrooted);

   ftree = gfopen (treef,"r");
   fscanf (ftree, "%d%d", &com.ns, &j);
   if(com.ns<=0) error2("need ns in tree file");
   debug = (com.ns<20);

   i = (com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");
   for(i=0; i<com.ns*2-1; i++)  nodes[i].nodeStr = NULL;
   for(i=0; i<com.ns-1; i++) {
      anc[i] = (int*)malloc((com.ns/SI+1)*sizeof(int));
      if(anc[i]==NULL)  error2("oom");
   }
   ReadTreeN(ftree, &haslength, &j, 1, 0);
   fclose(ftree);
   if(debug) { OutTreeN(F0, 1, PrNodeNum);  FPN(F0); }

   for(iclade=0; iclade<com.ns-1; iclade++) {
      printf("\nString for selecting sequences (followed by non-digit) (end to end)? ");
      scanf("%s", key);
      if(strcmp(endstr, key) == 0)
         break;
      for(i=0; i<com.ns; i++) 
         chosen[i] = '\0';


      k = strlen(key);
      for(i=0; i<com.ns; i++) {
         if( (p=strstr(com.spname[i], key)) 
            && !isdigit(p[k]) )
               chosen[i] = 1;
      }

      /*
      for(i=0; i<com.ns; i++) 
         if(strstr(com.spname[i], key)) chosen[i] = 1;
      */

      /* look for MRCA, going through two rounds, assuming unrooted tree */
      for(imrca=0; imrca<1+unrooted; imrca++) {
         if(imrca) 
            for(i=0; i<com.ns; i++) chosen[i] = 1 - chosen[i]; 

         for(i=0,sizeclade=0; i<com.ns; i++) 
            if(chosen[i]) {
               sizeclade ++;
               lasts = i;
            }

         if(sizeclade <= 1 || sizeclade >= com.ns-1) {
            puts("unable to form a clade.  <2 seqs.");
            break;
         }
         for(i=0; i<com.ns-1; i++) for(j=0; j<com.ns/SI+1; j++) 
            anc[i][j] = 0;
         for(is=0; is<com.ns; is++) {
            if(chosen[is]==0) continue;
            loc = is/SI;  bitmask = 1 << (is%SI);
            for(j=nodes[is].father; j!=-1; j=nodes[j].father) {
               anc[j-com.ns][loc] |= bitmask;
               if(is==lasts) {
                  for(i=0,k=0; i<com.ns; i++)
                     if(anc[j-com.ns][i/SI] & (1<<(i%SI)))
                        k ++;
                  if(k==sizeclade) {
                     mrca = j;  break;
                  }
               }
            }
         }
         if(imrca==0 && mrca!=tree.root) /* 1st round is enough */
            break;
      }

      if(sizeclade <= 1 || sizeclade >= com.ns-1 || mrca==tree.root) {
         printf("Unable to label.  Ignored.");
         continue;
      }

      if(debug) 
         for(is=0; is<com.ns-1; is++) {
            printf("\nnode %4d: ", is+com.ns);
            for(j=0; j<com.ns; j++) {
               loc = j/SI;  bitmask = 1 << (j%SI);
               printf(" %d", (anc[is][loc] & bitmask) != 0);
            }
         }

      printf("\nClade #%d (%s): %d seqs selected, MRCA is %d\n", iclade+1, key, sizeclade, mrca+1);
      for(is=0,paraphyl=0; is<com.ns; is++) {
         if(chosen[is] == 0)
            for(j=nodes[is].father; j!=-1; j=nodes[j].father)
               if(j==mrca) { paraphyl++;  break; }
      }
      if(paraphyl) 
         printf("\nThis clade is paraphyletic, & includes %d other sequences\n", paraphyl);

      nodes[mrca].label = iclade+1;
      if(debug) OutTreeN(F0, 1, haslength|PrLabel);
   }

   for(i=0; i<com.ns-1; i++)  free(anc[i]);
   OutTreeN(fout, 1, haslength|PrLabel);  FPN(fout);
   printf("Printed final tree with labels in evolver.out\n");
   exit(0);
}

void TreeDistanceDistribution (FILE* fout)
{
/* This calculates figure 3.7 of Yang (2006).
   This reads the file of all trees (such as 7s.all.trees), and calculates the 
   distribution of partition distance in all pairwise comparisons.
*/
   int i,j,ntree, k,*nib, parti2B[NS], nsame, IBsame[NS], lenpart=0;
   char treef[64]="5s.all.trees", *partition;
   FILE *ftree;
   double mPD[NS], PD1[NS];  /* distribution of partition distances */

   puts("Tree file name?");
   scanf ("%s", treef);

   ftree=gfopen (treef,"r");
   fscanf (ftree, "%d%d", &com.ns, &ntree);
   printf("%2d sequences %2d trees.\n", com.ns, ntree);
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");

   lenpart = (com.ns-1)*com.ns*sizeof(char);
   i = ntree*lenpart;
   printf("\n%d bytes of space requested.\n", i);
   partition = (char*)malloc(i);
   nib = (int*)malloc(ntree*sizeof(int));
   if (partition==NULL || nib==NULL) error2("out of memory");

   puts("\ntree #: mean prop of tree pairs with 0 1 2 ... shared bipartitions\n");
   fputs("\ntree #: prop of tree pairs with 0 1 2 ... shared bipartitions\n",fout);
   for (i=0; i<ntree; i++) {
      ReadTreeN (ftree, &j, &k, 0, 1); 
      nib[i]=tree.nbranch-com.ns;
      BranchPartition(partition+i*lenpart, parti2B);
   }
   for(k=0; k<com.ns-3; k++) mPD[k]=0;
   for (i=0; i<ntree; i++,FPN(fout)) {
      for(k=0; k<com.ns-3; k++) PD1[k]=0;
      for (j=0; j<ntree; j++) {
         if(j==i) continue;
         nsame=NSameBranch(partition+i*lenpart,partition+j*lenpart, nib[i],nib[j],IBsame);
         PD1[nsame] ++;
      }
      for(k=0; k<com.ns-3; k++) PD1[k] /= (ntree-1.);
      for(k=0; k<com.ns-3; k++) mPD[k] = (mPD[k]*i+PD1[k])/(i+1.);
      printf("%8d (%5.1f%%):", i+1,(i+1.)/ntree*100);
      for(k=0; k<com.ns-3; k++) printf(" %7.4f", mPD[k]);
      fprintf(fout, "%8d:", i+1);  for(k=0; k<com.ns-3; k++) fprintf(fout, " %7.4f", PD1[k]);
      printf("%s", (com.ns<8||(i+1)%100==0 ? "\n" : "\r"));
   }
   free(partition); free(nodes); free(nib); fclose(ftree);
   exit(0);
}


void TreeDistances (FILE* fout)
{
   int i,j,ntree, k,*nib, parti2B[NS], nsame, IBsame[NS],nIBsame[NS], lenpart=0;
   char treef[64]="5s.all.trees", *partition;
   FILE *ftree;
   double psame, mp, vp;

   /*
   TreeDistanceDistribution(fout);
   */

   puts("\nNumber of identical bi-partitions between trees.\nTree file name?");
   scanf ("%s", treef);

   ftree=gfopen (treef,"r");
   fscanf (ftree, "%d%d", &com.ns, &ntree);
   printf("%2d sequences %2d trees.\n", com.ns, ntree);
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");

   if(ntree<2) error2("ntree");
   printf ("\n%d species, %d trees\n", com.ns, ntree);
   puts("\n\t1: first vs. rest?\n\t2: all pairwise comparisons?\n");
   k=2;
   scanf("%d", &k);

   lenpart=(com.ns-1)*com.ns*sizeof(char);
   i=(k==1?2:ntree)*lenpart;
   printf("\n%d bytes of space requested.\n", i);
   partition=(char*)malloc(i);
   nib=(int*)malloc(ntree*sizeof(int));
   if (partition==NULL || nib==NULL) error2("out of memory");

   if(k==2) {    /* pairwise comparisons */
      fputs("Number of identical bi-partitions in pairwise comparisons\n",fout);
      for (i=0; i<ntree; i++) {
         ReadTreeN (ftree, &j, &k, 0, 1); 
         nib[i]=tree.nbranch-com.ns;
         BranchPartition(partition+i*lenpart, parti2B);
      }
      for (i=0; i<ntree; i++,FPN(F0),FPN(fout)) {
         printf("%2d (%2d):", i+1,nib[i]);
         fprintf(fout,"%2d (%2d):", i+1,nib[i]);
         for (j=0; j<i; j++) {
            nsame=NSameBranch(partition+i*lenpart,partition+j*lenpart, nib[i],nib[j],IBsame);
            printf(" %2d", nsame);
            fprintf(fout," %2d", nsame);
         }
      }
   }
   else {  /* first vs. others */
      ReadTreeN (ftree, &j, &k, 0, 1);
      nib[0]=tree.nbranch-com.ns;
      if (nib[0]==0) error2("1st tree is a star tree..");
      BranchPartition (partition, parti2B);
      fputs ("Comparing the first tree with the others\nFirst tree:\n",fout);
      OutTreeN(fout,0,0);  FPN(fout);  OutTreeB(fout);  FPN(fout); 
      fputs ("\nInternal branches in the first tree:\n",fout);
      FOR(i,nib[0]) { 
         k=parti2B[i];
         fprintf(fout,"%3d (%2d..%-2d): ( ",
            i+1,tree.branches[k][0]+1,tree.branches[k][1]+1);
         FOR(j,com.ns) if(partition[i*com.ns+j]) fprintf(fout,"%d ",j+1);
         fputs(")\n",fout);
      }
      if(nodes[tree.root].nson<=2) 
         fputs("\nRooted tree, results may not be correct.\n",fout);
      fputs("\nCorrect internal branches compared with the 1st tree:\n",fout);
      FOR(k,nib[0]) nIBsame[k]=0;
      for (i=1,mp=vp=0; i<ntree; i++,FPN(fout)) {
         ReadTreeN (ftree, &j, &k, 0, 1); 
         nib[1]=tree.nbranch-com.ns;
         BranchPartition (partition+lenpart, parti2B);
         nsame=NSameBranch (partition,partition+lenpart, nib[0],nib[1],IBsame);

         psame=nsame/(double)nib[0];
         FOR(k,nib[0]) nIBsame[k]+=IBsame[k];
         fprintf(fout,"1 vs. %3d: %4d: ", i+1,nsame);
         FOR(k,nib[0]) if(IBsame[k]) fprintf(fout," %2d", k+1);
         printf("1 vs. %5d: %6d/%d  %10.4f\n", i+1,nsame,nib[0],psame);
         vp += square(psame - mp)*(i-1.)/i;
         mp=(mp*(i-1.) + psame)/i;
      }
      vp=(ntree<=2 ? 0 : sqrt(vp/((ntree-1-1)*(ntree-1.))));
      fprintf(fout,"\nmean and S.E. of proportion of identical partitions\n");
      fprintf(fout,"between the 1st and all the other %d trees ", ntree-1);
      fprintf(fout,"(ignore these if not revelant):\n %.4f +- %.4f\n", mp, vp);
      fprintf(fout,"\nNumbers of times, out of %d, ", ntree-1);
      fprintf(fout,"interior branches of tree 1 are present");
      fputs("\n(This may be bootstrap support for nodes in tree 1)\n",fout);
      FOR(k,nib[0]) { 
         i=tree.branches[parti2B[k]][0]+1;  j=tree.branches[parti2B[k]][1]+1; 
         fprintf(fout,"%3d (%2d..%-2d): %6d (%5.1f%%)\n",
            k+1,i,j,nIBsame[k],nIBsame[k]*100./(ntree-1.));
      }
   }
   free(partition);  free(nodes); free(nib);  fclose(ftree);
}




int EigenQbase(double rates[], double pi[], 
    double Root[],double U[],double V[],double Q[])
{
/* Construct the rate matrix Q[] for nucleotide model REV.
*/
   int i,j,k;
   double mr, space[4];

   zero (Q, 16);
   for (i=0,k=0; i<3; i++) for (j=i+1; j<4; j++)
      if (i*4+j!=11) Q[i*4+j]=Q[j*4+i]=rates[k++];
   for (i=0,Q[3*4+2]=Q[2*4+3]=1; i<4; i++) FOR (j,4) Q[i*4+j] *= pi[j];
   for (i=0,mr=0; i<4; i++) 
      { Q[i*4+i]=0; Q[i*4+i]=-sum(Q+i*4, 4); mr-=pi[i]*Q[i*4+i]; }
   abyx (1/mr, Q, 16);

   eigenQREV(Q, com.pi, 4, Root, U, V, space);
   return (0);
}


static double freqK_NS=-1;

int EigenQcodon (int getstats, double kappa, double omega, double pi[],
    double Root[], double U[], double V[], double Q[])
{
/* Construct the rate matrix Q[].
   64 codons are used, and stop codons have 0 freqs.
*/
   int n=com.ncode, i,j,k, c[2],ndiff,pos=0,from[3],to[3];
   double mr, space[64];
   
   for(i=0; i<n*n; i++) Q[i] = 0;
   for (i=0; i<n; i++) FOR (j,i) {
      from[0]=i/16; from[1]=(i/4)%4; from[2]=i%4;
      to[0]=j/16;   to[1]=(j/4)%4;   to[2]=j%4;
      c[0]=GeneticCode[com.icode][i];   c[1]=GeneticCode[com.icode][j];
      if (c[0]==-1 || c[1]==-1)  continue;
      for (k=0,ndiff=0; k<3; k++)  if (from[k]!=to[k]) { ndiff++; pos=k; }
      if (ndiff!=1)  continue;
      Q[i*n+j]=1;
      if ((from[pos]+to[pos]-1)*(from[pos]+to[pos]-5)==0)  Q[i*n+j]*=kappa;
      if(c[0]!=c[1])  Q[i*n+j]*=omega;
      Q[j*n+i]=Q[i*n+j];
   }
   for(i=0; i<n; i++) for(j=0; j<n; j++)
      Q[i*n+j] *= com.pi[j];
   for(i=0,mr=0;i<n;i++) { 
      Q[i*n+i] = -sum(Q+i*n,n);
      mr -= pi[i]*Q[i*n+i]; 
   }

   if(getstats)
      Qfactor += freqK_NS * mr;
   else {
      if(com.ncatG==0) FOR(i,n*n) Q[i]*=1/mr;
      else             FOR(i,n*n) Q[i]*=Qfactor;  /* NSsites models */
      eigenQREV(Q, com.pi, n, Root, U, V, space);
   }
   return (0);
}



int EigenQaa (double pi[], double Root[], double U[], double V[], double Q[])
{
/* Construct the rate matrix Q[]
*/
   int n=20, i,j;
   double mr, space[20];

   FOR (i,n*n) Q[i]=0;
   switch (com.model) {
   case (Poisson)   : case (EqualInput) : 
      fillxc (Q, 1., n*n);  break;
   case (Empirical)   : case (Empirical_F):
      FOR(i,n) FOR(j,i) Q[i*n+j]=Q[j*n+i]=com.daa[i*n+j]/100;
      break;
   }
   FOR (i,n) FOR (j,n) Q[i*n+j]*=com.pi[j];
   for (i=0,mr=0; i<n; i++) {
      Q[i*n+i]=0; Q[i*n+i]=-sum(Q+i*n,n);  mr-=com.pi[i]*Q[i*n+i]; 
   }

   eigenQREV(Q, com.pi, n, Root, U, V, space);
   FOR(i,n)  Root[i]=Root[i]/mr;

   return (0);
}


int GetDaa (FILE* fout, double daa[])
{
/* Get the amino acid substitution rate matrix (grantham, dayhoff, jones, etc).
*/
   FILE * fdaa;
   char aa3[4]="";
   int i,j, n=20;

   fdaa=gfopen(com.daafile, "r");
   printf("\nReading rate matrix from %s\n", com.daafile);

   for (i=0; i<n; i++)  for (j=0,daa[i*n+i]=0; j<i; j++)  {
      fscanf(fdaa, "%lf", &daa[i*n+j]);
      daa[j*n+i]=daa[i*n+j];
   }
   if (com.model==Empirical) {
      FOR(i,n) if(fscanf(fdaa,"%lf",&com.pi[i])!=1) error2("err aaRatefile");
      if (fabs(1-sum(com.pi,20))>1e-4) error2("\nSum of aa freq. != 1\n");
   }
   fclose (fdaa);

   if (fout) {
      fprintf (fout, "\n%s\n", com.daafile);
      FOR (i,n) {
         fprintf (fout, "\n%4s", getAAstr(aa3,i));
         FOR (j,i)  fprintf (fout, "%5.0f", daa[i*n+j]); 
      }
      FPN (fout);
   }

   return (0);
}




void MakeSeq(char*z, int ls)
{
/* generate a random sequence of nucleotides, codons, or amino acids by 
   sampling com.pi[], or read the ancestral sequence from the file RootSeq.txt
   if the file exists.
*/
   int i,j,h, n=com.ncode, ch, n31=(com.seqtype==1?3:1), lst;
   double p[64],r, small=1e-5;
   char *pch=(com.seqtype==2?AAs:BASEs);
   char rootseqf[]="RootSeq.txt", codon[4]="   ";
   FILE *fseq=(FILE*)fopen(rootseqf,"r");
   static int times=0;

   if(fseq) {
      if(times++==0) printf("Reading sequence at the root from file.\n\n");
      if(com.siterates && com.ncatG>1) 
         error2("sequence for root doesn't work for site-class models");

      for(lst=0; ; ) {
         for(i=0; i<n31; i++) {
            while((ch=fgetc(fseq)) !=EOF && !isalpha(ch)) ;
            if(ch==EOF) error2("EOF when reading root sequence.");
            if(isalpha(ch))
               codon[i]=(char)(ch=CodeChara((char)ch, com.seqtype));
         }
         if(com.seqtype==1) ch = codon[0]*16 + codon[1]*4 + codon[2];
         if(ch<0 || ch>n-1) 
            printf("error when reading site %d\n", lst+1);
         if(com.seqtype==1 && com.pi[ch]==0)
            printf("you seem to have a stop codon in the root sequence\n");

         z[lst++] = (char)ch;
         if(lst==com.ls) break;
      }
      fclose(fseq);
   }
   else {
      for(j=0; j<n; j++)  p[j] = com.pi[j];
      for(j=1; j<n; j++)  p[j] += p[j-1];
      if(fabs(p[n-1]-1) > small)
         { printf("\nsum pi = %.6f != 1!\n", p[n-1]); exit(-1); }
      for(h=0; h<com.ls; h++) {
         for(j=0,r=rndu();j<n-1;j++) 
            if(r<p[j]) break;
         z[h] = (char)j;
      }
   }
}



void Evolve1 (int inode)
{
/* evolve sequence com.z[tree.root] along the tree to generate com.z[], 
   using nodes[].branch, nodes[].omega, & com.model
   Needs com.z[0,1,...,nnode-1], while com.z[0] -- com.z[ns-1] constitute
   the data.
   For codon sequences, com.siterates[] has w's for NSsites and NSbranchsite models.
*/
   int is, h,i,j, ison, from, n=com.ncode, longseq=100000;
   double t, rw;
   
   for (is=0; is<nodes[inode].nson; is++) {
      ison=nodes[inode].sons[is];
      memcpy(com.z[ison],com.z[inode],com.ls*sizeof(char));
      t=nodes[ison].branch;
      
      if(com.seqtype==1 && com.model && com.NSsites) { /* branch-site models */
         Qfactor=com.QfactorBS[ison];
         for(h=0; h<com.ls; h++) 
            com.siterates[h] = com.omegaBS[ison*com.ncatG+com.siteID[h]];
      }

      for(h=0; h<com.ls; h++) {
         /* decide whether to recalcualte PMat[]. */
         if (h==0 || (com.siterates && com.siterates[h]!=com.siterates[h-1])) {
            rw = (com.siterates?com.siterates[h]:1);

            switch(com.seqtype) {
            case (BASEseq):
               if(com.model<=TN93)
                  PMatTN93(PMat, t*Qfactor*rw*Qrates[0], 
                                 t*Qfactor*rw*Qrates[1], t*Qfactor*rw, com.pi);
               else if(com.model==REV)
                  PMatUVRoot(PMat, t*rw, com.ncode, U,V,Root);
               break;

            case (CODONseq): /* Watch out for NSsites model */
               if(com.model || com.NSsites) { /* no need to update UVRoot if M0 */
                  if(com.model && com.NSsites==0) /* branch */
                     rw = nodes[ison].omega;  /* should be equal to com.rK[nodes[].label] */

                  EigenQcodon(0, com.kappa, rw, com.pi, Root,U,V, PMat);
               }
               PMatUVRoot(PMat, t, com.ncode, U, V, Root); 
               break;

            case (AAseq):
               PMatUVRoot(PMat, t*rw, com.ncode, U, V, Root);
               break;
            }
            for(i=0; i<n; i++)
               for(j=1;j<n;j++)
                  PMat[i*n+j] += PMat[i*n+j-1];
         }
         for(j=0,from=com.z[ison][h],rw=rndu(); j<n-1; j++)
            if(rw < PMat[from*n+j]) break;
         com.z[ison][h] = j;
      }

      if(com.ls>longseq) printf("\r   nodes %2d -> %2d, evolving . .   ", inode+1, ison+1);

      if(nodes[ison].nson) Evolve1(ison); 
   }  /* for (is) */

   if(inode==tree.root && com.ls>longseq)  printf("\r%s", strc(50,' '));
}


int PatternWeightSimple (int CollapsJC)
{
/* This is modified from PatternWeight() and collaps sites into patterns, 
   for nucleotide, amino acid, or codon sequences.
   This relies on \0 being the end of the string so that sequences should not be 
   encoded before this routine is called.
   com.pose[i] has labels for genes as input and maps sites to patterns in return.
   com.fpatt, a vector of doubles, wastes space as site pattern counts are integers.
   Sequences z[ns*ls] are copied into patterns zt[ls*lpatt], and bsearch is used 
   twice to avoid excessive copying, to count npatt first & to generate fpatt etc.
*/
   int maxnpatt=com.ls, h, ip,l,u, j, k, same;
   /* int n31 = (com.seqtype==CODONseq ? 3 : 1); */
   int n31 = 1;
   int lpatt = com.ns*n31+1;   /* extra 0 used for easy debugging, can be voided */
   int *p2s;  /* point patterns to sites in zt */
   char *zt, *p;
   double nc = (com.seqtype == 1 ? 64 : com.ncode) + !com.cleandata+1;
   int debug=0;
   char DS[]="DS";

   /* (A) Collect and sort patterns.  Get com.npatt.
      Move sequences com.z[ns][ls] into sites zt[ls*lpatt].  
      Use p2s to map patterns to sites in zt to avoid copying.
   */

   if((com.seqtype==1 && com.ns<5) || (com.seqtype!=1 && com.ns<7))
      maxnpatt = (int)(pow(nc, (double)com.ns) + 0.5);
   if(maxnpatt>com.ls) maxnpatt = com.ls;
   p2s  = (int*)malloc(maxnpatt*sizeof(int));
   zt = (char*)malloc((com.ns+1)*com.ls*n31*sizeof(char));
   if(p2s==NULL || zt==NULL)  error2("oom p2s or zt");
   memset(zt, 0, (com.ns+1)*com.ls*n31*sizeof(char));
   for(j=0; j<com.ns; j++) 
      for(h=0; h<com.ls; h++) 
         for(k=0; k<n31; k++)
            zt[h*lpatt+j*n31+k] = com.z[j][h*n31+k];

   com.npatt = l = u = ip = 0;
   for(h=0; h<com.ls; h++) {
      if(debug) printf("\nh %3d %s", h, zt+h*lpatt);
      /* bsearch in existing patterns.  Knuth 1998 Vol3 Ed2 p.410 
         ip is the loc for match or insertion.  [l,u] is the search interval.
      */
      same = 0;
      if(h != 0) {  /* not 1st pattern? */
         for(l=0, u=com.npatt-1; ; ) {
            if(u<l) break;
            ip = (l+u)/2;
            k = strcmp(zt+h*lpatt, zt+p2s[ip]*lpatt);
            if(k<0)        u = ip - 1;
            else if(k>0)   l = ip + 1;
            else         { same = 1;  break; }
         }
      }
      if(!same) {
         if(com.npatt>maxnpatt) 
            error2("npatt > maxnpatt");
         if(l > ip) ip++;        /* last comparison in bsearch had k > 0. */
         /* Insert new pattern at ip.  This is the expensive step. */

         if(ip<com.npatt)
            memmove(p2s+ip+1, p2s+ip, (com.npatt-ip)*sizeof(int));

         /*
         for(j=com.npatt; j>ip; j--) 
            p2s[j] = p2s[j-1];
         */
         p2s[ip] = h;
         com.npatt ++;
      }

      if(debug) {
         printf(": %3d (%c ilu %3d%3d%3d) ", com.npatt, DS[same], ip, l, u);
         for(j=0; j<com.npatt; j++)
            printf(" %s", zt+p2s[j]*lpatt);
      }

   }     /* for (h)  */

   /* (B) count pattern frequencies */
   com.fpatt = (double*)realloc(com.fpatt, com.npatt*sizeof(double));
   if(com.fpatt==NULL) error2("oom fpatt");
   for(ip=0; ip<com.npatt; ip++) com.fpatt[ip] = 0;
   for(h=0; h<com.ls; h++) {
      for(same=0, l=0, u=com.npatt-1; ; ) {
         if(u<l) break;
         ip = (l+u)/2;
         k = strcmp(zt+h*lpatt, zt+p2s[ip]*lpatt);
         if(k<0)        u = ip - 1;
         else if(k>0)   l = ip + 1;
         else         { same = 1;  break; }
      }
      if(!same)
         error2("ghost pattern?");
      com.fpatt[ip]++;
   }     /* for (h)  */

   for(j=0; j<com.ns; j++) {
      /* 
      com.z[j] = (char*)realloc(com.z[j], com.npatt*n31*sizeof(char)); 
      */
      for(ip=0,p=com.z[j]; ip<com.npatt; ip++) 
         for(k=0; k<n31; k++)
            *p++ = zt[p2s[ip]*lpatt+j*n31+k];
   }
   free(p2s);  free(zt);

   return (0);
}


void Simulate (char*ctlf)
{
/* simulate nr data sets of nucleotide, codon, or AA sequences.
   ls: number of nucleotides, codons, or AAs in each sequence.
   All 64 codons are used for codon sequences.
   When com.alpha or com.ncatG>1, sites are randomized after sequences are 
   generated.
   space[com.ls] is used to hold site marks.
   format (0: paml sites; 1: paml patterns; 2: paup nex)
 */
   char *ancf="ancestral.txt", *siteIDf="siterates.txt";
   FILE *fin, *fseq, *ftree=NULL, *fanc=NULL, *fsiteID=NULL;
   char *paupstart="paupstart",*paupblock="paupblock",*paupend="paupend";
   char line[32000];
   int lline=32000, i,j,k, ir,n,nr, fixtree=1, sspace=10000, rooted=1;
   int h=0,format=0, b[3]={0}, nrate=1, counts[NCATG];
   int *siteorder=NULL;
   char *tmpseq=NULL, *pc;
   double birth=0, death=0, sample=1, mut=1, tlength, *space, *blengthBS;
   double T,C,A,G,Y,R, Falias[NCATG];
   int    Lalias[NCATG];

   noisy=1;
   printf("\nReading options from data file %s\n", ctlf);
   com.ncode=n=(com.seqtype==0 ? 4 : (com.seqtype==1?64:20));
   fin=(FILE*)gfopen(ctlf,"r");
   fscanf(fin, "%d", &format);  fgets(line, lline, fin);
   printf("\nSimulated data will go into %s.\n", seqf[format]);
   if(format==2) printf("%s, %s, & %s will be appended if existent.\n",
                       paupstart,paupblock,paupend);

   fscanf (fin, "%d", &i);
   fgets(line, lline, fin);
   SetSeed(i<=0?(int)time(NULL)*2+1:i);
   fscanf (fin, "%d%d%d", &com.ns, &com.ls, &nr);
   fgets(line, lline, fin);
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");

   if(com.ns>NS) error2("too many seqs?");
   printf ("\n%d seqs, %d sites, %d replicate(s)\n", com.ns, com.ls, nr);
   k=(com.ns*com.ls* (com.seqtype==CODONseq?4:1) *nr)/1000+1;
   printf ("Seq file will be about %dK bytes.\n",k);
   for(i=0; i<com.ns; i++)          /* default spname */
      sprintf(com.spname[i],"S%d",i+1);

   if(fixtree) {
      fscanf(fin,"%lf",&tlength);   fgets(line, lline, fin);
      if(ReadTreeN(fin,&i,&j, 1, 1))  /* might overwrite spname */
         error2("err tree..");

      if(i==0) error2("use : to specify branch lengths in tree");
      for(i=0,T=0; i<tree.nnode; i++) 
         if(i!=tree.root) T += nodes[i].branch;
      if(tlength>0) {
         for(i=0; i<tree.nnode; i++) 
            if(i!=tree.root) nodes[i].branch *= tlength/T;
      }
      printf("tree length = %.3f\n", (tlength>0?tlength:T));
      if(com.ns<100) {
         printf("\nModel tree & branch lengths:\n"); 
         /* OutTreeN(F0,1,1); FPN(F0); */
         OutTreeN(F0,0,1); FPN(F0);
      }
      if(com.seqtype==CODONseq && com.model && !com.NSsites) { /* branch model */
         FOR(i,tree.nnode) nodes[i].omega=nodes[i].label;
         FPN(F0);  OutTreeN(F0, 1, PrBranch&PrLabel);  FPN(F0);
      }
   }
   else {   /* random trees, broken or need testing? */
      printf ("\nbirth rate, death rate, sampling fraction, mutation rate (tree height)?\n");
      fscanf (fin, "%lf%lf%lf%lf", &birth, &death, &sample, &mut);
      fgets(line, lline, fin);
      printf("%9.4f %9.4f %9.4f %9.4f\n", birth, death, sample, mut);
   }

   if(com.seqtype==BASEseq) {
      fscanf(fin,"%d",&com.model);  
      fgets(line, lline, fin);
      if(com.model<0 || com.model>REV) error2("model err");
      if(com.model==T92) error2("T92: please use HKY85 with T=A and C=G.");

      printf("\nModel: %s\n", basemodels[com.model]);
      if(com.model==REV)        nrate=5;
      else if(com.model==TN93)  nrate=2;
      FOR(i,nrate) fscanf(fin,"%lf",&Qrates[i]);
      fgets(line, lline, fin);
      if(nrate<=2) FOR(i,nrate) printf("kappa %9.5f\n",Qrates[i]); FPN(F0);
      if(nrate==5) {
         printf("a & b & c & d & e: ");
         FOR(i,nrate) printf("%9.5f",Qrates[i]); FPN(F0);
      }
      if((com.model==JC69 || com.model==F81)&&Qrates[0]!=1) 
         error2("kappa should be 1 for this model");
   }
   else if(com.seqtype==CODONseq) {
      for(i=0; i<64; i++) 
         getcodon(CODONs[i], i);
      if(com.model==0 && com.NSsites) {  /* site model */
         fscanf(fin,"%d",&com.ncatG);   fgets(line, lline, fin);
         if(com.ncatG>NCATG) error2("ncatG>NCATG");
         FOR(i,com.ncatG) fscanf(fin,"%lf",&com.freqK[i]);  fgets(line, lline, fin);
         FOR(i,com.ncatG) fscanf(fin,"%lf",&com.rK[i]);     fgets(line, lline, fin);
         printf("\n\ndN/dS (w) for site classes (K=%d)", com.ncatG);
         printf("\nf: ");  FOR(i,com.ncatG) printf("%9.5f",com.freqK[i]);
         printf("\nw: ");  FOR(i,com.ncatG) printf("%9.5f",com.rK[i]);  FPN(F0);
      }
      else if(com.model && com.NSsites) {  /* branchsite model */
         fscanf(fin,"%d",&com.ncatG);   fgets(line, lline, fin);
         if(com.ncatG>min2(NCATG,127)) error2("ncatG too large");
         FOR(i,com.ncatG) fscanf(fin,"%lf",&com.freqK[i]);  fgets(line,lline,fin);
         printf("\n%d site classes.\nFreqs: ", com.ncatG);
         FOR(i,com.ncatG) printf("%9.5f",com.freqK[i]);

         if((com.omegaBS=(double*)malloc((com.ncatG+2)*tree.nnode*sizeof(double)))==NULL)
            error2("oom");
         com.QfactorBS = com.omegaBS + com.ncatG*tree.nnode;
         blengthBS = com.QfactorBS + tree.nnode;

         for(i=0; i<tree.nnode; i++)
            blengthBS[i] = nodes[i].branch;
         for(k=0; k<com.ncatG; k++) {
            ReadTreeN(fin, &i, &j, 0, 1);
            if(i) error2("do not include branch lengths except in the first tree.");
            if(!j) error2("Use # to specify omega's for branches");
            for(i=0; i<tree.nnode; i++)  com.omegaBS[i*com.ncatG+k]=nodes[i].label;
         }
         for(i=0; i<tree.nnode; i++)
            { nodes[i].branch=blengthBS[i];  nodes[i].label=nodes[i].omega=0; }
         for(i=0; i<tree.nnode; i++) {  /* print out omega as node labels. */
            nodes[i].nodeStr=pc=(char*)malloc(20*com.ncatG*sizeof(char));
            sprintf(pc, "'[%.2f", com.omegaBS[i*com.ncatG+0]);
            for(k=1,pc+=strlen(pc); k<com.ncatG; k++,pc+=strlen(pc)) 
               sprintf(pc, ", %.2f", com.omegaBS[i*com.ncatG+k]);
            sprintf(pc, "]'");
         }
         FPN(F0);  OutTreeN(F0,1,PrBranch|PrLabel);  FPN(F0);
      }
      else if(!com.model) {  /* M0 */
         fscanf(fin,"%lf",&com.omega);
         fgets(line, lline, fin);
         printf("omega = %9.5f\n",com.omega);
         for(i=0; i<tree.nbranch; i++) 
            nodes[tree.branches[i][1]].omega = com.omega;
      }

      fscanf(fin,"%lf",&com.kappa);   fgets(line, lline, fin);
      printf("kappa = %9.5f\n",com.kappa);
   }

   if(com.seqtype==BASEseq || com.seqtype==AAseq) {
      fscanf(fin,"%lf%d", &com.alpha, &com.ncatG);
      fgets(line, lline, fin);
      if(com.alpha) 
        printf("Gamma rates, alpha =%.4f (K=%d)\n",com.alpha,com.ncatG);
      else { 
         com.ncatG=0; 
         puts("Rates are constant over sites."); 
      }
   }
   if(com.alpha || com.ncatG) { /* this is used for codon NSsites as well. */
      k=com.ls;
      if(com.seqtype==1 && com.model && com.NSsites) k*=tree.nnode;
      if((com.siterates=(double*)malloc(k*sizeof(double)))==NULL) error2("oom1");
      if((siteorder=(int*)malloc(com.ls*sizeof(int)))==NULL) error2("oom2");
   }

   
   if(com.seqtype==AAseq) { /* get aa substitution model and rate matrix */
      fscanf(fin,"%d",&com.model);
      printf("\nmodel: %s",aamodels[com.model]); 
      if(com.model>=2)  { fscanf(fin,"%s",com.daafile); GetDaa(NULL,com.daa); }
      fgets(line, lline, fin);
   }
   /* get freqs com.pi[] */
   if((com.seqtype==BASEseq && com.model>K80) ||
       com.seqtype==CODONseq ||
      (com.seqtype==AAseq && (com.model==1 || com.model==3)))
         FOR(k,com.ncode) fscanf(fin,"%lf",&com.pi[k]);
   else if(com.model==0 || (com.seqtype==BASEseq && com.model<=K80)) 
      fillxc(com.pi,1./com.ncode,com.ncode);

   printf("sum pi = 1 = %.6f:", sum(com.pi,com.ncode));
   matout2(F0, com.pi, 1, com.ncode, 7, 4);
   if(com.seqtype==BASEseq) {
      if(com.model<REV) {
         T=com.pi[0]; C=com.pi[1]; A=com.pi[2]; G=com.pi[3]; Y=T+C; R=A+G;
         if (com.model==F84) { 
            Qrates[1]=1+Qrates[0]/R;   /* kappa2 */
            Qrates[0]=1+Qrates[0]/Y;   /* kappa1 */
         }
         else if (com.model<=HKY85) Qrates[1]=Qrates[0];
         Qfactor = 1/(2*T*C*Qrates[0] + 2*A*G*Qrates[1] + 2*Y*R);
      }
      else
         if(com.model==REV) EigenQbase(Qrates, com.pi, Root,U,V,PMat);
   }

   /* get Qfactor for NSsites & NSbranchsite models */
   if(com.seqtype==CODONseq && com.NSsites) {
      if(!com.model) {  /* site models */
         for(k=0,Qfactor=0; k<com.ncatG; k++) {
            freqK_NS=com.freqK[k];
            EigenQcodon(1, com.kappa,com.rK[k],com.pi, NULL,NULL,NULL, PMat);
         }
         Qfactor=1/Qfactor;
         printf("Qfactor for NSsites model = %9.5f\n", Qfactor);
      }
      else {            /* branch-site models */
         for(i=0; i<tree.nnode; i++) {
            if(i==tree.root) { com.QfactorBS[i]=-1; continue; }
            for(k=0,Qfactor=0; k<com.ncatG; k++) {
               freqK_NS=com.freqK[k];
               EigenQcodon(1, com.kappa,com.omegaBS[i*com.ncatG+k],com.pi, NULL,NULL,NULL, PMat);
            }
            com.QfactorBS[i]=1/Qfactor;  Qfactor=0;
            printf("node %2d: Qfactor = %9.5f\n", i+1, com.QfactorBS[i]);
         }
      }
   }
   if(com.seqtype==CODONseq && com.ncatG<=1 && com.model==0)
      EigenQcodon(0, com.kappa,com.omega, com.pi, Root, U, V, PMat);
   else if(com.seqtype==AAseq)
      EigenQaa(com.pi, Root, U, V,PMat);

   puts("\nAll parameters are read.  Ready to simulate\n");
   for(j=0; j<com.ns*2-1; j++)
      com.z[j] = (char*)malloc(com.ls*sizeof(char));
   sspace = max2(sspace, com.ls*(int)sizeof(double));
   space  = (double*)malloc(sspace);
   if(com.alpha || com.ncatG) tmpseq=(char*)space;
   if (com.z[com.ns*2-1-1]==NULL) error2("oom for seqs");
   if (space==NULL) {
      printf("oom for space, %d bytes needed.", sspace);
      exit(-1);
   }

   fseq = gfopen(seqf[format],"w");
   if(format==2) appendfile(fseq,paupstart);
   
   fanc = (FILE*)gfopen(ancf,"w");
   if(fixtree) {
      fputs("\nAncestral sequences generated during simulation ",fanc);
      fprintf(fanc,"(check against %s)\n",seqf[format]);
      OutTreeN(fanc,0,0); FPN(fanc); OutTreeB(fanc); FPN(fanc);
   }
   if(com.alpha || com.NSsites) {
      fsiteID=(FILE*)gfopen(siteIDf,"w");
      if(com.seqtype==1) fprintf(fsiteID, "\nSite class IDs\n");
      else               fprintf(fsiteID, "\nRates for sites\n");
      if(com.seqtype==CODONseq && com.NSsites) {
         if(!com.model) matout(fsiteID,com.rK, 1,com.ncatG);
         if((com.siteID=(char*)malloc(com.ls*sizeof(char)))==NULL) 
            error2("oom siteID");
      }
   }

   for (ir=0; ir<nr; ir++) {
      if (!fixtree) {    /* right now tree is fixed */
         RandomLHistory (rooted, space);
         if (rooted && com.ns<10) j = GetIofLHistory ();
         BranchLengthBD (1, birth, death, sample, mut);
         if(com.ns<20) { 
            printf ("\ntree used: "); 
            OutTreeN(F0,1,1);
            FPN(F0); 
         }
      }
      MakeSeq(com.z[tree.root], com.ls);

      if (com.alpha)
         Rates4Sites(com.siterates,com.alpha,com.ncatG,com.ls, 0,space);
      else if(com.seqtype==1 && com.NSsites) { /* for NSsites */
         /* the table for the alias algorithm is the same, but ncatG is small. */
         MultiNomialAliasSetTable(com.ncatG, com.freqK, Falias, Lalias, space);
         MultiNomialAlias(com.ls, com.ncatG, Falias, Lalias, counts);

         for (i=0,h=0; i<com.ncatG; i++)
            for (j=0; j<counts[i]; j++) {
               com.siteID[h]=(char)i;
               com.siterates[h++]=com.rK[i]; /* overwritten later for branchsite */
            }
      }

      Evolve1(tree.root);

      /* randomize sites for site-class model */
      if(com.siterates && com.ncatG>1) {
         if(format==1 && ir==0) 
            puts("\nrequested site pattern counts as output for site-class model.\n");
         randorder(siteorder, com.ls, (int*)space);
         for(j=0; j<tree.nnode; j++) {
            memcpy(tmpseq,com.z[j],com.ls*sizeof(char));
            for(h=0; h<com.ls; h++) com.z[j][h]=tmpseq[siteorder[h]];
         }
         if(com.alpha || com.ncatG>1) {
            memcpy(space,com.siterates,com.ls*sizeof(double));
            for(h=0; h<com.ls; h++) com.siterates[h]=space[siteorder[h]];
         }
         if(com.siteID) {
            memcpy((char*)space,com.siteID,com.ls*sizeof(char));
            for(h=0; h<com.ls; h++) com.siteID[h]=*((char*)space+siteorder[h]);
         }
      }

      /* print sequences*/
      if(format==1) {
         for(i=0; i<com.ns; i++) for(h=0; h<com.ls; h++) com.z[i][h] ++;
         PatternWeightSimple(0);
         for(i=0; i<com.ns; i++) for(h=0; h<com.npatt; h++) com.z[i][h] --;
      }
      if(format==2) fprintf(fseq,"\n\n[Replicate # %d]\n", ir+1);
      printSeqs(fseq, NULL, NULL, format); /* printsma not usable as it codes into 0,1,...,60. */
      if(format==2 && !fixtree) {
         fprintf(fseq,"\nbegin tree;\n   tree true_tree = [&U] "); 
         OutTreeN(fseq,1,1); fputs(";\n",fseq);
         fprintf(fseq,"end;\n\n");
      }
      if(format==2) appendfile(fseq,paupblock);

      /* print ancestral seqs, rates for sites. */
      if(format!=1) {
         j = (com.seqtype==CODONseq?3*com.ls:com.ls);
         fprintf(fanc,"[replicate %d]\n",ir+1);

         if(!fixtree) {
            if(format<2)
               { OutTreeN(fanc,1,1); FPN(fanc); FPN(fanc); }
         }
         else {
            fprintf(fanc,"%6d %6d\n",tree.nnode-com.ns,j);
            for(j=com.ns; j<tree.nnode; j++,FPN(fanc)) {
               fprintf(fanc,"node%-26d  ", j+1);
               print1seq(fanc, com.z[j], com.ls, NULL);
            }
            FPN(fanc);

            if(fsiteID) {
               if(com.seqtype==CODONseq && com.NSsites && com.model==0) { /* site model */
                  k=0;
                  if(com.rK[com.ncatG-1]>1)
                     FOR(h,com.ls) if(com.rK[com.siteID[h]]>1) k++;
                  fprintf(fsiteID, "\n[replicate %d: %2d]\n",ir+1, k);
                  if(k)  for(h=0,k=0; h<com.ls; h++) {
                     if(com.rK[com.siteID[h]]>1) { 
                        fprintf(fsiteID,"%4d ",h+1); 
                        if(++k%15==0) FPN(fsiteID);
                     }
                  }
                  FPN(fsiteID);
               }
               else if(com.seqtype==CODONseq && com.NSsites && com.model) { /* branchsite */
                  fprintf(fsiteID, "\n[replicate %d]\n",ir+1);
                  for(h=0; h<com.ls; h++) {
                     fprintf(fsiteID," %4d ", com.siteID[h]+1);
                     if(h==com.ls-1 || (h+1)%15==0) FPN(fsiteID);
                  }
               }
               else {       /* gamma rates */
                  fprintf(fsiteID,"\n[replicate %d]\n",ir+1);
                  for(h=0; h<com.ls; h++) {
                     fprintf(fsiteID,"%7.4f ",com.siterates[h]);
                     if(h==com.ls-1 || (h+1)%10==0) FPN(fsiteID);
                  }
               }
            }
         }
      }

      printf ("\rdid data set %d %s", ir+1, (com.ls>100000||nr<100? "\n" : ""));
   }   /* for (ir) */
   if(format==2) appendfile(fseq,paupend);

   fclose(fseq);  if(!fixtree) fclose(fanc);  
   if(com.alpha || com.NSsites) fclose(fsiteID);
   for(j=0; j<com.ns*2-1; j++) free(com.z[j]);
   free(space);
   if(com.model && com.NSsites) /* branch-site model */
      for(i=0; i<tree.nnode; i++)  free(nodes[i].nodeStr);
   free(nodes);
   if(com.alpha || com.ncatG) { 
      free(com.siterates);  com.siterates=NULL;
      free(siteorder);
      if(com.siteID) free(com.siteID);  com.siteID=NULL;
   }
   if(com.seqtype==1 && com.model && com.NSsites) free(com.omegaBS); 
   com.omegaBS = NULL;

   exit (0);
}


int GetSpnamesFromMB (FILE *fmb, char line[], int lline)
{
/* This reads species names from MrBayes output file fmb, like the following.

      Taxon  1 -> 1_Arabidopsis_thaliana
      Taxon  2 -> 2_Taxus_baccata
*/
   int j, ispecies;
   char *p=NULL, *mbstr1="Taxon ", *mbstr2="->";

   puts("Reading species names from mb output file.\n");
   rewind(fmb);
   for(ispecies=0; ; ) {
      if(fgets(line, lline, fmb)==NULL) return(-1);
      if(strstr(line, mbstr1) && strstr(line, mbstr2)) {
         p=strstr(line, mbstr1)+5;
         sscanf(p, "%d", &ispecies);
         p=strstr(line, mbstr2)+3;
         if(com.spname[ispecies-1][0]) 
            error2("species name already read?");

         for(j=0; isgraph(*p)&&j<lline; ) com.spname[ispecies-1][j++] = *p++;
         com.spname[ispecies-1][j]=0;

         printf("\tTaxon %2d:  %s\n", ispecies, com.spname[ispecies-1]);
      }
      else if (ispecies)
         break;
   }
   com.ns=ispecies;
   rewind(fmb);

   return(0);
}

char *GrepLine (FILE*fin, char*query, char* line, int lline)
{
/* This greps infile to search for query[], and returns NULL or line[].
*/
   char *p=NULL;

   rewind(fin);
   for( ; ; ) {
      if(fgets(line, lline, fin)==NULL) return(NULL);
      if(strstr(line, query)) return(line);
   }
   return(NULL);
}


void CladeProbabilities (char treefile[])
{
/* This reads a tree from treefile and then scans a set of MrBayes output files
   (mbfiles) to retrieve posterior probabilities for every clade in that tree.
   It first scans the first mb output file to get the species names.

   Sample mb output:
   6 -- ...........................*************   8001 1.000 0.005 (0.000)
   7 -- ....................********************   8001 1.000 0.006 (0.000)

*/
   int lline=100000, i,j,k, nib, inode, parti2B[NS];
   char line[100000], *partition, *p;
   char symbol[2]=".*", cladestr[NS+1]={0};
   FILE *ftree, *fmb[20];
   double *Pclade, t;
/*
   int nmbfiles=15;
   char *mbfiles[]={"mb-1e-5.out", "mb-2e-5.out", "mb-3e-5.out", "mb-4e-5.out",
"mb-5e-5.out", "mb-6e-5.out", "mb-7e-5.out", "mb-8e-5.out",
"mb-9e-5.out", "mb-1e-4.out", "mb-2e-4.out", "mb-3e-4.out",
"mb-5e-4.out", "mb-1e-3.out", "mb-1e-2.out"};
*/
   int nmbfiles=2;
   char *mbfiles[]={"mb-1e-4.out", "mb-1e-1.out"};

   printf("tree file is %s\nmb output files:\n", treefile);
   ftree=gfopen(treefile,"r");
   for(k=0; k<nmbfiles; k++)
      fmb[k]=gfopen(mbfiles[k],"r");
   for(k=0; k<nmbfiles; k++) printf("\t%s\n", mbfiles[k]);

   GetSpnamesFromMB(fmb[0], line, lline);  /* read species names from mb output */

   fscanf (ftree, "%d%d", &i, &k);
   if(i && i!=com.ns) error2("do you mean to specify ns in the tree file?");
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");
   ReadTreeN (ftree, &i, &j, 0, 1);

   FPN(F0);  OutTreeN(F0, 0, 0);  FPN(F0);  FPN(F0);
   nib=tree.nbranch-com.ns;
   for(i=0;i<tree.nnode;i++) {
      nodes[i].nodeStr = NULL;
      if(i>com.ns) nodes[i].nodeStr=(char*)malloc(100*sizeof(char));
   }

   partition=(char*)malloc(nib*com.ns*sizeof(char));
   if (partition==NULL) error2("oom");
   if((Pclade=(double*)malloc(nib*nmbfiles*sizeof(double)))==NULL)
      error2("oom");
   for(i=0;i<nib*nmbfiles; i++) Pclade[i]=0;

   BranchPartition(partition, parti2B);

   for(i=0; i<nib; i++) {
      inode=tree.branches[parti2B[i]][1];
      if(partition[i*com.ns+0])
         for(j=0; j<com.ns; j++) cladestr[j]=symbol[1-partition[i*com.ns+j]];
      else
         for(j=0; j<com.ns; j++) cladestr[j]=symbol[partition[i*com.ns+j]];
      printf("#%2d branch %2d node %2d  %s", i+1, parti2B[i], inode, cladestr);

      for(k=0; k<nmbfiles; k++) {
         if(GrepLine(fmb[k], cladestr, line, lline)) {
            p=strstr(line,cladestr);
            sscanf(p+com.ns, "%lf%lf\0", &t, &Pclade[i*nmbfiles+k]);
         }
      }
      for(k=0; k<nmbfiles; k++) printf("%6.2f", Pclade[i*nmbfiles+k]);
      FPN(F0);
      for(k=0,p=nodes[inode].nodeStr; k<nmbfiles; k++) {
         sprintf(p, "%3.0f%s", Pclade[i*nmbfiles+k]*100,(k<nmbfiles-1?"/":""));
         p+=4;
      }
   }
   FPN(F0);  OutTreeN(F0,1,PrLabel);  FPN(F0);

   for(i=0; i<tree.nnode; i++) free(nodes[i].nodeStr);
   free(nodes); free(partition);  free(Pclade);
   fclose(ftree);   
   for(k=0; k<nmbfiles; k++) fclose(fmb[k]);
   exit(0);
}


void CladeSupport(char tree1f[], char tree2f[], int burnin)
{
/* This reads one tree from tree1f and then scans many trees in tree2f to 
   calculate (bootstrap and Bayesian) support values.
*/
   int i,j,k, ntree, nib1,nib2, intree;
   char *partition1, *partition2;
   double Pclade[NS]={0};
   FILE *f1, *f2;

   printf("Calculate support values for clades on the master tree\n");
   if(!isgraph(tree1f[0])) {
      printf("input two tree file names\n");
      scanf("%s%s", tree1f, tree2f);
   }
   f1=gfopen(tree1f,"r");
   f2=gfopen(tree2f,"r");

   fscanf(f1, "%d%d", &com.ns, &k);
   if(k>1) puts("only the first tree in the master tree file is used.");
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");
   for(i=0; i<com.ns*2-1; i++) nodes[i].nodeStr=NULL;

   ReadTreeN (f1, &i, &j, 1, 1);
   printf("master tree\n"); OutTreeN(F0,0,0);  FPN(F0);  FPN(F0);

   nib1=tree.nbranch-com.ns;
   partition1=(char*)malloc(2*(com.ns-1)*com.ns*sizeof(char));
   if(partition1==NULL) error2("oom");
   partition2=partition1+(com.ns-1)*com.ns;

   BranchPartition(partition1, NULL);

   for(ntree=-burnin;  ; ntree++) {
      fscanf(f2, "%d%d", &i, &j);
      if(ReadTreeN (f2, &i, &j, 0, 1)) break;
      printf("\nreading tree %5d  ", ntree+1);
      if(com.ns<15) OutTreeN(F0, 0, 0);
      if(ntree<0) continue;
      nib2=tree.nbranch-com.ns;
      BranchPartition(partition2, NULL);
      for(i=0; i<nib1; i++) {
         for(j=0,intree=0; j<nib2; j++) {
            for(k=0; k<com.ns; k++)
               if(partition1[i*com.ns+k]!=partition2[j*com.ns+k]) break;
            if(k==com.ns)  { intree=1; break; }
         }
         if(intree) Pclade[i]++;
      }
   }

   /* for(i=0; i<nib1; i++) Pclade[i]/=ntree; */
   rewind(f1);
   fscanf(f1, "%d%d", &com.ns, &k);
   ReadTreeN (f1, &i, &j, 1, 1);
   for(i=0,nib1=0; i<tree.nbranch; i++)
      if(tree.branches[i][1] >= com.ns) 
         nodes[tree.branches[i][1]].label = Pclade[nib1++];

   if(burnin) printf("\n\n%d burn in, %d trees used\n", burnin, ntree);
   else       printf("\n\n%d trees used\n", ntree);
   matout2(F0, Pclade, 1, nib1, 6, 2);
   FPN(F0);  OutTreeN(F0,0,PrLabel);  FPN(F0);
   OutTreeN(F0,1,PrLabel);  FPN(F0);

   free(nodes);  free(partition1);  fclose(f1);  fclose(f2);
   exit(0);
}


void Rell2MLtree(int argc, char *argv[])
{
/* for CodonTree project.  This retrieves the ML tree by examining the RELL 
   results for the 51 trees.
*/
   int ngene=106, ntree=51, ig,i,j,itree,MLtree, lline=10000;
   char line[10000];
   FILE *fr, *ft, *fo;

   if(argc!=3) error2("Usage Rell2MLtree treefile rellfile");
   printf("extracting ML tree from rell output\n");
   ft=gfopen(argv[1],"r");
   fr=gfopen(argv[2],"r");
   fo=gfopen("t2.trees","w");

   com.ns=8;
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");

   for(ig=0; ig<ngene; ig++) {
      fscanf(fr, "%d", &MLtree);
      fgets(line, lline, fr);
      rewind(ft);
      fscanf(ft, "%d%d", &i, &j);
      if(i!=com.ns) error2("tree file error.");
      for(itree=0;  itree<ntree; itree++) {
         if(ReadTreeN (ft, &i, &j, 0, 1)) break;
         if(itree==MLtree-1) break;
      }
      OutTreeN(F0, 0, 0); FPN(F0);
      OutTreeN(fo, 0, 0); FPN(fo);
   }
   exit(0);
}
