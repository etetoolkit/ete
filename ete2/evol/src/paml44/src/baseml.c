/* baseml.c
     Maximum likelihood parameter estimation for aligned DNA (RNA) sequences,
                 combined with phylogenetic tree estimation.
                    Copyright, Ziheng YANG, July 1992 onwards

                  cc -o baseml -fast baseml.c tools.c -lm
                  cl -O2 baseml.c tools.c
                          baseml <ControlFileName>
*/

#include "paml.h"

#define NS            5000
#define NBRANCH       (NS*2-2)
#define NNODE         (NS*2-1)
#define MAXNSONS      100
#define NGENE         500
#define LSPNAME       50
#define NCODE         4
#define NCATG         40

#define NP            (NBRANCH+NGENE+11)
/*
#define NP            (NBRANCH+3*NNODE+NGENE+11+NCATG*NCATG-1)
*/
extern int noisy, NFunCall, NEigenQ, NPMatUVRoot, *ancestor, GeneticCode[][64];
extern double Small_Diff, *SeqDistance;
extern char AAs[];


int Forestry (FILE *fout);
void DetailOutput(FILE *fout, double x[], double var[]);
int GetOptions(char *ctlf);
int GetInitials(double x[], int *fromfile);
int GetInitialsTime(double x[]);
int SetxInitials(int np, double x[], double xb[][2]);
int SetParameters(double x[]);
int SetPGene(int igene, int _pi, int _UVRoot, int _alpha, double x[]);
int SetPSiteClass(int iclass, double x[]);
int testx(double x[], int np);
double GetBranchRate(int igene, int ibrate, double x[], int *ix);
int GetPMatBranch (double Pt[], double x[], double t, int inode);
int ConditionalPNode (int inode, int igene, double x[]);

int TransformxBack(double x[]);
int AdHocRateSmoothing (FILE*fout, double x[NS*3], double xb[NS*3][2], double space[]);
void DatingHeteroData(FILE* fout);

int TestModel (FILE *fout, double x[], int nsep, double space[]);
int OldDistributions (int inode, double oldfreq[]);
int SubData(int argc, char *argv[]);
int GroupDistances();


struct CommonInfo {
   unsigned char *z[NS], *spname[NS], seqf[256],outf[256],treef[256], cleandata;
   char oldconP[NNODE];  /* update conP for nodes to save computation (0 yes; 1 no) */
   int seqtype, ns, ls, ngene, posG[NGENE+1], lgene[NGENE], *pose, npatt, readpattern;
   int np, ntime, nrgene, nrate, nalpha, npi, nhomo, ncatG, ncode, Mgene;
   size_t sspace, sconP;
   int fix_kappa, fix_rgene, fix_alpha, fix_rho, nparK, fix_blength;
   int clock, model, getSE, runmode, print,verbose, ndata, bootstrap;
   int icode,coding, method;
   int nbtype;
   double *fpatt, kappa, alpha, rho, rgene[NGENE], pi[4],piG[NGENE][4];
   double freqK[NCATG], rK[NCATG], MK[NCATG*NCATG];
   double (*plfun)(double x[],int np), *conP, *fhK, *space;
   int conPSiteClass;        /* is conP memory allocated for each class? */
   int NnodeScale;
   char *nodeScale;          /* nScale[ns-1] for interior nodes */
   double *nodeScaleF;       /* nScaleF[npatt] for scale factors */
   int fix_omega;
   double omega;
}  com;
struct TREEB {
   int  nbranch, nnode, root, branches[NBRANCH][2];
   double lnL;
}  tree;
struct TREEN {
   int father, nson, sons[MAXNSONS], ibranch, ipop;
   double branch, age, kappa, pi[4], *conP, label;
   char *nodeStr, fossil;
}  *nodes, **gnodes, nodes_t[2*NS-1];


/* for sptree.nodes[].fossil: lower, upper, bounds, gamma, inverse-gamma */
enum {LOWER_F=1, UPPER_F, BOUND_F} FOSSIL_FLAGS;
char *fossils[]={" ", "L", "U", "B"}; 

struct SPECIESTREE {
   int nbranch, nnode, root, nspecies, nfossil;
   struct TREESPN {
      char name[LSPNAME+1], fossil, usefossil;  /* fossil: 0, 1, 2, 3 */
      int father, nson, sons[2];
      double age, pfossil[7];   /* lower and upper bounds or alpha & beta */
      double *lnrates;          /* log rates for loci */
   } nodes[2*NS-1];
}  sptree;
/* all trees are binary & rooted, with ancestors unknown. */

struct DATA { /* locus-specific data and tree information */
   int ns[NGENE], ls[NGENE], npatt[NGENE], ngene, lgene[NGENE];
   int root[NGENE+1], BlengthMethod, fix_nu, nbrate[NGENE];
   char *z[NGENE][NS], cleandata[NGENE];
   double *fpatt[NGENE], lnpT, lnpR, lnpDi[NGENE];
   double Qfactor[NGENE], pi[NGENE][NCODE], nu[NGENE];
   double rgene[NGENE], kappa[NGENE], alpha[NGENE], omega[1];
   int NnodeScale[NGENE];
   char *nodeScale[NGENE];    /* nScale[data.ns[locus]-1] for interior nodes */
}  data;

int nR=4, LASTROUND, BayesEB;
double PMat[16], Cijk[64], Root[4];
int StepMatrix[16];


FILE *frub, *flnf, *frst, *frst1, *frst2=NULL, *finitials=NULL;
char *ratef="rates";
char *models[]={"JC69","K80","F81","F84","HKY85","T92","TN93","REV","UNREST", "REVu","UNRESTu"};
enum {JC69, K80, F81, F84, HKY85, T92, TN93, REV, UNREST, REVu, UNRESTu} MODELS;
char *clockstr[]={"", "Global clock", "Local clock", "ClockCombined"};
enum {GlobalClock=1, LocalClock, ClockCombined} ClockModels;

double _rateSite=1; /* rate for a site */
int N_PMatUVRoot=0;


#define BASEML 1
#include "treesub.c"
#include "treespace.c"

int main (int argc, char *argv[])
{
   FILE *fout, *fseq=NULL, *fpair[6];
   char pairfs[1][32]={"2base.t"};
   char rstf[96]="rst", ctlf[96]="baseml.ctl", timestr[64];
   char *Mgenestr[]={"diff. rate", "separate data", "diff. rate & pi", 
                     "diff. rate & kappa", "diff. rate & pi & kappa"};
   int getdistance=1, i, idata, seed;
   size_t s2=0;

   starttimer();
   seed = 4*(int)time(NULL)+1;
   SetSeed(seed);

   com.ndata = 1;
   com.cleandata = 0;  noisy = 0;  com.runmode = 0;

   com.clock = 0;
   com.fix_rgene = 0;  /* 0: estimate rate factors for genes */
   com.nhomo = 0;
   com.getSE = 0;      /* 1: want S.E.s of estimates;  0: don't want them */

   com.seqtype = 0;   com.model = 0;
   com.fix_kappa = 0; com.kappa = 5;
   com.fix_alpha = 1; com.alpha = 0.;  com.ncatG = 4;    /* alpha=0 := inf */
   com.fix_rho = 1;   com.rho = 0;     com.nparK = 0;
   com.ncode = 4;     com.icode = 0;
   com.print = 0;     com.verbose = 1;  com.fix_blength = 0;
   com.method = 0;    com.space = NULL;

   printf("BASEML in %s\n",  VerStr);
   frub=gfopen("rub","w");  frst=gfopen(rstf,"w"); frst1=gfopen("rst1","w");

   if (argc>1)  strcpy(ctlf, argv[1]); 
   GetOptions(ctlf);
   if(com.runmode != -2) finitials=fopen("in.baseml","r");
   if(com.getSE == 2)    frst2 = fopen("rst2","w");

   fprintf(frst, "Supplemental results for BASEML\n\nseqf:  %s\ntreef: %s\n",
      com.seqf, com.treef);
   fout=gfopen(com.outf, "w"); 
#if(!RELEASE)
   fprintf(fout, "\nseed used = %d\n", seed);
#endif

   fpair[0]=(FILE*)gfopen(pairfs[0],"w");

   /* for stepwise addition, com.sspace should be calculated using com.ns. */
   com.sspace = 1000000*sizeof(double);
   if((com.space = (double*)malloc(com.sspace)) == NULL) 
      error2("oom space");

   if(com.clock==5 || com.clock==6)
      DatingHeteroData(fout);

   if((fseq=fopen (com.seqf,"r"))==NULL)  {
      printf ("\n\nSequence file %s not found!\n", com.seqf);
      exit (-1);
   }

   for (idata=0; idata<com.ndata; idata++) {
      if (com.ndata>1) {
         printf("\nData set %4d\n", idata+1);
         fprintf(fout, "\n\nData set %4d\n", idata+1);

         fprintf(frst1, "%4d", idata+1);
      }
      if(idata)  GetOptions(ctlf); /* com.cleandata is read from here again. */
      ReadSeq ((com.verbose?fout:NULL), fseq, com.cleandata);
      SetMapAmbiguity();
      if (com.rho && com.readpattern) error2("rho doesn't work with readpattern.");
      if(com.ndata==1) fclose(fseq);
      i=(com.ns*2-1)*sizeof(struct TREEN);
      if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");

      if(com.coding) {
         if(com.ls%3!=0 || (com.ngene!=1 && com.ngene!=3))
            error2("this is not a coding sequence.  Remove icode?");
      }

      if(com.Mgene && com.ngene==1)  error2 ("option Mgene for 1 gene?");
      if(com.ngene>1 && com.nhomo) error2("nhomo for mutliple genes?");
      if(com.nalpha && (!com.alpha || com.ngene==1 || com.fix_alpha))
         error2("Malpha");
      if(com.nalpha>1 && com.rho) error2("Malpha or rho");
      if(com.alpha==0)  com.nalpha = 0;
      else              com.nalpha = (com.nalpha?com.ngene:!com.fix_alpha);
      if(com.Mgene==1)  com.nalpha = !com.fix_alpha;

      if(com.ngene==1) com.Mgene = 0;
      if((com.nhomo==1 && com.ngene>1) || (com.Mgene>1 && com.nhomo>=1))
         error2("nhomo does not work with Mgene options");

      if((com.Mgene>=2 && com.model==JC69) || (com.Mgene>=3 && com.model==F81) 
        || ((com.Mgene==2 || com.Mgene==4) && com.model==K80)
        || (com.Mgene>1 && com.nhomo>1) 
        || (com.Mgene>=2 && (com.model==UNREST||com.model==UNRESTu)))
         error2 ("model || Mgene");
      fprintf(fout,"\nBASEML (in %s)  %s  %s ", VerStr,com.seqf,models[com.model]);
      if(com.clock) fprintf(fout," %s ",clockstr[com.clock]);
      if (!com.nparK && com.alpha && com.rho) fprintf (fout, "  Auto-");
      if (com.alpha) fprintf (fout,"dGamma (ncatG=%d)", com.ncatG);
      if (com.nalpha>1) fprintf (fout,"(%d gamma)", com.nalpha);
      if (com.ngene>1) 
         fprintf (fout, " (%d genes: %s)  ", com.ngene, Mgenestr[com.Mgene]);
      if (com.nhomo>1)
         fprintf(fout,"\nNonhomo:%2d  fix_kappa%2d\n",com.nhomo,com.fix_kappa);
      if (com.nparK && com.ncatG>3)
         printf("\a\n%d rate categories for nonparametric model?\n", com.ncatG);
      if (com.nparK) fprintf(fout,"\nnparK:%4d  K:%4d\n",com.nparK,com.ncatG);

      if(getdistance) {
         i = com.ns*(com.ns-1)/2;
         SeqDistance = (double*)realloc(SeqDistance,i*sizeof(double));
         ancestor = (int*)realloc(ancestor, i*sizeof(int));
         if(SeqDistance==NULL||ancestor==NULL) error2("oom distance&ancestor");
      }
      InitializeBaseAA(fout);
      if (com.Mgene==3) 
         for(i=0; i<com.ngene; i++) xtoy(com.pi,com.piG[i],4);

      if (com.model==JC69 && !com.readpattern && !com.print) 
         PatternWeightJC69like(fout);

      com.sconP = (com.ns-1)*com.ncode*(size_t)com.npatt*sizeof(double);
      if((com.conP = (double*)realloc(com.conP, com.sconP))==NULL) 
         error2("oom conP");
      if (com.alpha || com.nparK) {
         s2 = com.npatt*com.ncatG*sizeof(double);
         if((com.fhK=(double*)realloc(com.fhK,s2))==NULL) error2("oom");
      }

      printf ("\n%9ld bytes for distance ",
         com.ns*(com.ns-1)/2*(sizeof(double)+sizeof(int)));
      printf("\n%9lu bytes for conP\n", com.sconP);
      printf("%9lu bytes for fhK\n%9lu bytes for space\n", s2, com.sspace);

      /* FOR(i,com.ns*2-1) xtoy(com.pi,nodes[i].pi, 4);  check this? */

      if(getdistance)
         DistanceMatNuc(fout,fpair[0],com.model,com.alpha);

      if (com.Mgene==1)        MultipleGenes (fout, fpair, com.space);
      else if (com.runmode==0) Forestry (fout);
      else if (com.runmode==2) fprintf(frst,"%2d",StarDecomposition(fout,com.space));
      else if (com.runmode==3) StepwiseAddition (fout, com.space);
      else if (com.runmode>=4) Perturbation(fout, (com.runmode==4), com.space);

      FPN(frst);  if((idata+1)%10==0) fflush(frst);
      if(com.ndata>1 && com.runmode) {
         fprintf(frst1, "\t"); 
         OutTreeN(frst1, 1, 0);
      }
      FPN(frst1); fflush(frst1);
      free(nodes);
      printf("\nTime used: %s\n", printtime(timestr));

   }   /* for(idata) */
   if(com.ndata>1 && fseq) fclose(fseq);
   free(com.space);
   fclose(fout);  fclose(frst);   fclose(fpair[0]);
   if(finitials) { fclose(finitials);  finitials=NULL; }

   return (0);
}


/* x[]: t[ntime], rgene[ngene-1], kappa[nbranch], pi[nnode*3], 
        { alpha, rho || rK[], fK[] || rK[], MK[] }
*/

FILE *ftree;
void PrintBestTree(FILE *fout, FILE *ftree, int btree);

int Forestry (FILE *fout)
{
   static int times=0;
   int status=0, inbasemlg=0, i,j=0, itree=0,ntree, np,np0,iteration=1;
   int pauptree=0, btree=0, haslength;
   double x[NP], xcom[NP-NBRANCH], lnL,lnL0=0,lnLbest=0, e=1e-8, nchange=-1;
   double xb[NP][2], tl=0, *g=NULL, *H=NULL;
   FILE *finbasemlg=NULL, *frate=NULL;

   ftree = gfopen(com.treef,"r");
   GetTreeFileType(ftree,&ntree,&pauptree,0);
   if(com.alpha) frate=gfopen(ratef,"w");
   if (com.alpha && com.rho==0 && com.nhomo==0 && com.nparK==0 && com.ns<15) {
      inbasemlg=1;  finbasemlg=gfopen("in.basemlg","w");
   }
   flnf=gfopen("lnf","w+");
   fprintf(flnf,"%6d %6d %6d\n", ntree, com.ls, com.npatt);

   for(itree=0; ntree==-1||itree<ntree; itree++,iteration=1) {
      if(ReadTreeN(ftree,&haslength,&i,0,1)) 
         { puts("\nend of tree file."); break; }
      if(noisy) printf("\nTREE # %2d: ", itree+1);
      fprintf (fout,"\nTREE # %2d:  ", itree+1);
      fprintf (frub,"\n\nTREE # %2d\n", itree+1);
      if(com.print) fprintf (frst,"\n\nTREE # %2d\n", itree+1);
      fprintf (flnf,"\n\n%2d\n", itree+1);

      LASTROUND=0;
      if (com.fix_blength==2 && !haslength) error2("no branch lengths in tree");
      if (com.fix_blength>0 && !haslength) com.fix_blength=0;
      if (times++==0 && com.fix_blength>0 && haslength) {
         if(com.clock) puts("\nBranch lengths in tree are ignored");
         else {
            if(com.fix_blength==2) puts("\nBranch lengths in tree are fixed.");
            else if(com.fix_blength==1) 
               puts("\nBranch lengths in tree used as initials.");
            if(com.fix_blength==1) {
               FOR(i,tree.nnode) 
                  if((x[nodes[i].ibranch]=nodes[i].branch)<0) 
                     x[nodes[i].ibranch]=1e-5;
            }
         }
      }

      if(com.cleandata) 
         nchange=MPScore (com.space);
      if(noisy&&com.ns<99) 
         { OutTreeN(F0,0,0); printf(" MP score: %.2f\n",nchange);}
      OutTreeN(fout,0,0);  fprintf(fout,"  MP score: %.2f",nchange);
      if(!com.clock && com.model<=REV && com.nhomo<=2 
         && nodes[tree.root].nson<=2 && com.ns>2){
         puts("\nThis is a rooted tree, without clock.  Check.");
         if(com.verbose) fputs("\nThis is a rooted tree.  Please check!",fout);
      }

      fflush(fout);  fflush(flnf);

      GetInitials(x, &i);
      if(i==-1) iteration=0;

      if((np=com.np)>NP) error2("raise NP and recompile");

      if(com.sspace < spaceming2(np)) {
         com.sspace = spaceming2(np);
         if((com.space=(double*)realloc(com.space,com.sspace))==NULL)
            error2("oom space");
      }

      if(itree) { np0 = np; }
      if(itree && !finitials && (com.nhomo==0 || com.nhomo==2))
         for (i=0; i<np-com.ntime; i++) x[com.ntime+i]=max2(xcom[i],0.001);

      PointconPnodes ();

      lnL = com.plfun (x, np);
      if(noisy) {
         printf("\nntime & nrate & np:%6d%6d%6d\n",com.ntime,com.nrate,com.np);
         if(noisy>2 && com.ns<50) { OutTreeB(F0); FPN(F0); matout(F0,x,1,np); }
         printf("\nlnL0 = %12.6f\n",-lnL);
      }

      if (iteration && np) {
         SetxBound (np, xb);
         SetxInitials (np, x, xb); /* start within the feasible region */
         if(com.method==1)
            j=minB(noisy>2?frub:NULL, &lnL,x,xb, e, com.space);
         else if(com.method==3)
            j=minB2(noisy>2?frub:NULL, &lnL,x,xb, e, com.space);
         else
            j=ming2(noisy>2?frub:NULL,&lnL,com.plfun,NULL,x,xb, com.space,e,np);

         if (j==-1 || lnL<=0 || lnL>1e7) status = -1;
         else                            status = 0;
      }

      if (itree==0) { lnL0=lnLbest=lnL; btree=0; }
      else if (lnL<lnLbest) {
         lnLbest=lnL;  btree=itree; 
      }
      if (noisy) printf ("Out...\nlnL  = %12.6f\n", -lnL);
      fprintf(fout,"\nlnL(ntime:%3d  np:%3d): %13.6f %+12.6f\n",
          com.ntime, np, -lnL, -lnL+lnL0);
      if(com.fix_blength<2) { OutTreeB (fout);  FPN (fout); }
      if(LASTROUND==0) {
         LASTROUND=1;
         if((com.npi && com.model!=T92) || com.nparK>=2) TransformxBack(x);
      }
      if(com.clock) { /* move times into x[] */
         for(i=0,j=!nodes[tree.root].fossil; i<tree.nnode; i++) 
            if(i!=tree.root && nodes[i].nson && !nodes[i].fossil) 
               x[j++]=nodes[i].age;
      }
      for(i=0; i<np; i++) 
         fprintf(fout," %8.6f", x[i]);  
      FPN(fout); fflush(fout);
      if(inbasemlg) matout(finbasemlg, x, 1, np);

/*
for(i=0;i<np;i++) fprintf(frst1,"\t%.6f", x[i]); 
fprintf(frst1,"\t%.4f", -lnL);
*/
      if (com.getSE) {
         puts("Calculating SE's");
         if(com.sspace < np*(np+1)*sizeof(double)) {
            com.sspace = np*(np+1)*sizeof(double);
            if((com.space=(double*)realloc(com.space,com.sspace))==NULL)
               error2("oom space for SE");
         }

         g = com.space;
         H = g + com.np;
         HessianSKT2004 (x, lnL, g, H);
         if(com.getSE>=2 && com.clock==0 && nodes[tree.root].nson==3) {  /* g & H */
            fprintf(frst2,"\n %d\n\n", com.ns);
            OutTreeN(frst2, 1, 1);  fprintf(frst2,"\n\n");
            for(i=0; i<com.ntime; i++)
               if(x[i]>0.0004 && fabs(g[i])<0.005) g[i] = 0;
            for(i=0; i<com.ntime; i++) fprintf(frst2," %9.6f", x[i]);  fprintf(frst2, "\n\n");
            for(i=0; i<com.ntime; i++) fprintf(frst2," %9.6f", g[i]);  fprintf(frst2, "\n\n");
            fprintf(frst2, "\nHessian\n\n");
            for(i=0; i<com.ntime; i++,FPN(frst2))
               for(j=0; j<com.ntime; j++) 
                  fprintf(frst2," %9.2f", H[i*np+j]);
            fflush(frst2);
         }

         for(i=0; i<np*np; i++)  H[i] *= -1;
         matinv(H, np, np, H+np*np);
         fprintf(fout,"SEs for parameters:\n");
         for(i=0; i<np; i++) 
            fprintf(fout," %8.6f", (H[i*np+i]>0. ? sqrt(H[i*np+i]) : -1));
         FPN(fout);
      }

      /* if(com.clock) SetBranch(x); */
      /* GroupDistances(); */

      if(com.nbtype>1)
         fprintf(fout,"\nWarning: branch rates are not yet applied in tree length and branch lengths");
      if(AbsoluteRate) {
         fprintf(fout,"\nNote: mutation rate is not applied to tree length.  Tree has times, for TreeView\n");
         for(i=0;i<tree.nnode;i++)  nodes[i].branch*=ScaleTimes_TipDate;
      }

      if(!AbsoluteRate) {
         for(i=0,tl=0;i<tree.nnode;i++) 
            if(i!=tree.root) tl+=nodes[i].branch;
         fprintf(fout,"\ntree length = %9.5f%s\n",tl,com.ngene>1?" (1st gene)":"");
      }
      FPN(fout); OutTreeN(fout,1,0); FPN(fout);
      FPN(fout); OutTreeN(fout,1,1); FPN(fout);

      if(TipDate) {  /* scale back the times in nodes[].branch */
         for(i=0;i<tree.nnode;i++)  nodes[i].branch/=ScaleTimes_TipDate;
      }

      if(com.np-com.ntime || com.clock)
         DetailOutput(fout,x,H);
      if(status) {
         printf ("convergence?\n");  fprintf (fout,"check convergence..\n");
      }
      if (itree==0)
         for (i=0; i<np-com.ntime; i++) xcom[i]=x[com.ntime+i];
      else if (!j)
         for (i=0; i<np-com.ntime; i++) xcom[i]=xcom[i]*.8+x[com.ntime+i]*0.2;
/*
      TestModel(fout,x,1,com.space);
      fprintf(fout,"\n\n# of lfun calls:%10d\n", NFunCall);
*/


      if(com.coding && com.Mgene!=1 && !AbsoluteRate) {
         fputs("\nTree with branch lengths for codon models:\n",fout);
         FOR(i,tree.nnode) nodes[i].branch *= (1+com.rgene[1]+com.rgene[2]);
         FPN(fout); OutTreeN(fout,1,1); FPN(fout);
         FOR(i,tree.nnode) nodes[i].branch /= (1+com.rgene[1]+com.rgene[2]);
      }

      com.print-=9;  com.plfun(x, np);  com.print+=9;
      if (com.print) {
         if (com.plfun != lfun)
            lfunRates(frate, x, np);

         /** think about more-general models **/
         if (com.nhomo==0 && com.nparK==0 && com.model<=REV && com.rho==0
            /* && com.clock<=1 */)  /* clock to be fixed */
            AncestralSeqs(frst, x);
      }
   }         /* for (itree) */

   if(ntree>1) {
      fprintf(frst1, "\t%d\t", btree+1);
      PrintBestTree(frst1, ftree, btree);
   }
   if(finbasemlg) fclose(finbasemlg);   if (frate) fclose(frate);
   fclose(ftree); 

   if(ntree==-1)  ntree=itree;
   if(ntree>1) { rewind(flnf);  rell(flnf,fout,ntree); }   
   fclose(flnf);

   return(0);
}


void PrintBestTree(FILE *fout, FILE *ftree, int btree)
{
   int itree, ntree, i,j;

   rewind(ftree);
   GetTreeFileType(ftree,&ntree,&i,0);
   for(itree=0; ntree==-1||itree<ntree; itree++) {
      if(ReadTreeN(ftree,&i,&j,0,1)) 
         { puts("\nend of tree file."); break; }
      if(itree==btree)
         OutTreeN(fout, 1, 0);
   }
}


int TransformxBack(double x[])
{
/* transform variables x[] back to their original definition after iteration,
   for output and for calculating SEs.
*/ 
   int i,k, K=com.ncatG;

   k=com.ntime+com.nrgene+com.nrate;
   for (i=0; i<com.npi; i++)  
      f_and_x(x+k+3*i,x+k+3*i,4,0,0);
   
   k+=com.npi*3 + K-1;        /* K-1 for rK */
   if (com.nparK==2)          /* rK & fK */
      f_and_x(x+k,x+k,K,0,0);
   else if (com.nparK==3)     /* rK & MK (double stochastic matrix) */
      for (i=0; i<K-1; k+=K-1,i++)  f_and_x(x+k,x+k,K,0,0);
   else if (com.nparK==4)     /* rK & MK */
      for (i=0; i<K;   k+=K-1,i++)  f_and_x(x+k,x+k,K,0,0);
   return(0);
}


void DetailOutput (FILE *fout, double x[], double var[])
{
   int i,j,k=com.ntime, nr[]={0, 1, 0, 1, 1, 1, 2, 5, 11};
   int n31pi=(com.model==T92?1:3);
   double Qfactor,*p=com.pi, t=0, k1,k2, S,V, Y=p[0]+p[1],R=p[2]+p[3];
   double *Qrate=x+com.ntime+com.nrgene, *oldfreq=NULL;

   fprintf(fout,"\nDetailed output identifying parameters\n");
   if(com.clock) OutputTimesRates(fout, x, var);
   k=com.ntime;
   if (com.nrgene && !com.clock) {
      fprintf (fout, "\nrates for %d genes:%6.0f", com.ngene, 1.);
      FOR (i,com.nrgene) fprintf (fout, " %8.5f", x[k+i]);  FPN(fout);
   }
   k+=com.nrgene;
   
   if(com.nhomo==1) {
      if(com.nrate) fprintf (fout, "kappa under %s:", models[com.model]);
      for(i=0; i<com.nrate; i++) fprintf (fout, " %8.5f", x[k++]);  FPN(fout);
      fprintf (fout, "Base frequencies:\n");
      for(j=0; j<4; j++) fprintf (fout, " %8.5f", com.pi[j]);
      k += n31pi;
   }
   else if(com.nhomo>=3) {
      fprintf (fout, "kappa under %s (in order of branches):", models[com.model]);
      for(i=0; i<com.nrate; i++) fprintf(fout," %8.5f", x[k++]);  FPN(fout);
      SetParameters(x);
      if(com.alpha==0) {
         if((oldfreq=(double*)malloc(tree.nnode*4*sizeof(double)))==NULL) 
            error2("out of memory for OldDistributions()");
         OldDistributions (tree.root, oldfreq);
      }
      fputs("\n(frequency parameters for branches)  [frequencies at nodes] (see Yang & Roberts 1995 fig 1)\n\n",fout);
      for(i=0; i<tree.nnode; i++,FPN(fout)) {
         fprintf (fout, "Node #%d  (", i+1);
         for(j=0; j<4; j++) fprintf (fout, " %7.5f ", nodes[i].pi[j]);
         fprintf(fout,")");
         if(com.alpha==0) {
            fprintf(fout,"  [");
            for(j=0; j<4; j++) fprintf(fout," %7.5f",oldfreq[i*4+j]);
            fprintf(fout," ]");
         }
      }
      fprintf(fout,"\nNote: node %d is root.\n",tree.root+1);
      k += com.npi*n31pi;
      if(com.alpha==0) free(oldfreq);
   }
   else if (!com.fix_kappa) {
      fprintf(fout,"\nParameters %s in the rate matrix", (com.model<=TN93?"(kappa)":""));
      fprintf(fout," (%s) (Yang 1994 J Mol Evol 39:105-111):\n", models[com.model]);

      if (com.nhomo==2) {
         fprintf (fout, "\nbranch         t    kappa      TS     TV\n");
         for(i=0; i<tree.nbranch; i++) {
            if (com.model==F84)  { k1 = 1+x[k+i]/R;  k2 = 1+x[k+i]/R; }
            else                   k1 = k2=x[k+i];
            S = 2*p[0]*p[1]*k1+2*p[2]*p[3]*k2; 
            V = 2*Y*R;
            Qfactor = 1/(S+V);
            /* t=(com.clock ? nodes[tree.branches[i][1]].branch : x[i]); */
            t = nodes[tree.branches[i][1]].branch; 
            fprintf(fout,"%2d..%-2d %9.5f %8.5f %9.5f %8.5f\n",
               tree.branches[i][0]+1,tree.branches[i][1]+1, t,x[k+i],
               t*S/(S+V), t*V/(S+V));
         }
      }
      /* Mgene = 0:rates, 1:separate; 2:diff pi, 3:diff kapa, 4:all diff*/
      else if (com.Mgene>=2) {
         for(i=0; i<com.ngene; i++) {
            fprintf (fout, "\nGene #%d: ", i+1);
            p = (com.Mgene==3 ? com.pi : com.piG[i]);
            Qrate = (com.Mgene==2 ? x+k : x+k+i*nr[com.model]);
            if (com.model<=TN93)
               FOR (j,nr[com.model]) fprintf(fout," %8.5f", Qrate[j]);
            else if (com.model==REV || com.model==REVu) 
               /* output Q matrix, no eigen calculation */
               EigenQREVbase(fout, Qrate, p, &nR, Root, Cijk);
         }
         if (com.Mgene>=3) k+=com.ngene*nr[com.model];
         else              k+=nr[com.model];
      }
      else {
         if (com.model<REV) FOR (i,com.nrate) fprintf (fout, " %8.5f", x[k++]);
         else k+=com.nrate;
      }
      FPN(fout);
   }

   if (com.Mgene<2) {
      if (com.model==REV || com.model==REVu) /* output Q, no eigen calculation */
         EigenQREVbase(fout, Qrate, com.pi, &nR, Root, Cijk);
      else if (com.model==UNREST || com.model==UNRESTu)
         QUNREST (fout, PMat, x+com.ntime+com.nrgene, com.pi);
   }

   for(j=0; j<com.nalpha; j++) {
      if (!com.fix_alpha)  
         fprintf(fout,"\nalpha (gamma, K=%d) = %8.5f", com.ncatG,(com.alpha=x[k++]));
      if(com.nalpha>1) 
         DiscreteGamma(com.freqK,com.rK,com.alpha,com.alpha,com.ncatG,DGammaMean);
      fprintf(fout, "\nrate: "); FOR(i,com.ncatG) fprintf(fout," %8.5f",com.rK[i]);
      fprintf(fout, "\nfreq: "); FOR(i,com.ncatG) fprintf(fout," %8.5f",com.freqK[i]);
      FPN(fout);
   }
   if (!com.fix_rho) {
      fprintf (fout, "rho for the auto-discrete-gamma model: %9.5f",x[k]);
      FPN(fout);
   }
   if (com.nparK>=1 && com.nalpha<=1) {
      fprintf(fout, "\nrate:");  FOR(i,com.ncatG) fprintf(fout," %8.5f",com.rK[i]);
      fprintf(fout, "\nfreq:");  FOR(i,com.ncatG) fprintf(fout," %8.5f",com.freqK[i]);
      FPN(fout);
   }
   if (com.rho || (com.nparK>=3 && com.nalpha<=1)) {
      fprintf (fout, "transition probabilities between rate categories:\n");
      for(i=0;i<com.ncatG;i++,FPN(fout))  FOR(j,com.ncatG) 
         fprintf (fout, " %8.5f", com.MK[i*com.ncatG+j]);
   }
   FPN(fout);
}

int GetStepMatrix(char*line)
{
/* read user definitions of the REV and UNREST models
   StepMatrix[4*4]:
      -1 at diagonals, 0 for default rate, and positive values for rates
*/
   char *p,*errstr="StepMatrix specification in the control file";
   int i,k, b1=-1,b2;

   p=strchr(line,'[');
   if(p==NULL) error2("model specification.  Expecting '['.");
   sscanf(++p,"%d", &com.nrate);
   if(com.nrate<0 || (com.model==REVu&&com.nrate>5) 
                  || (com.model==UNRESTu&&com.nrate>11)) error2(errstr);
   for(i=0; i<4; i++) for(k=0; k<4; k++) StepMatrix[i*4+k] = (i==k?-1:0);
   for(i=0; i<com.nrate; i++) { 
      while(*p && *p!='(') p++;
      if(*p++ !='(') error2( "expecting (" );
      for(k=0; k<12; k++) {
         while (isspace(*p)) p++;
         if(*p==')') break;
         b1=CodeChara(*p++,0);  b2=CodeChara(*p++,0);
         if(b1<0||b1>3||b2<0||b2>3) error2("bases out of range.");
         if(b1==b2||StepMatrix[b1*4+b2]>0) {
            printf("pair %c%c already specified.\n", BASEs[b1],BASEs[b2]);
         }
         if(com.model==REVu) StepMatrix[b1*4+b2]=StepMatrix[b2*4+b1]=i+1;
         else                StepMatrix[b1*4+b2]=i+1;
      }
      printf("rate %d: %d pairs\n", i+1,k);
   }
   for(i=0; i<16; i++) { printf("%3d", StepMatrix[i]); if((i+1)%4==0) FPN(F0); }

   return(0);
}

int GetOptions (char *ctlf)
{
   int iopt, i, j, nopt=30, lline=4096; 
   char line[4096], *pline, opt[32], *comment="*#";
   char *optstr[]={"seqfile","outfile","treefile","noisy", "cleandata", 
        "verbose","runmode", "method", "clock","fix_rgene","Mgene","nhomo",
        "getSE","RateAncestor", "model","fix_kappa","kappa",
        "fix_alpha","alpha","Malpha","ncatG", "fix_rho","rho",
        "nparK", "ndata", "bootstrap", "Small_Diff","icode", "fix_blength", "seqtype"};
   double t;
   FILE *fctl;
   int ng=-1, markgenes[NGENE];

   fctl = gfopen(ctlf,"r");
   if(noisy) printf ("Reading options from %s..\n", ctlf);
   for ( ; ; ) {
      if (fgets(line, lline, fctl) == NULL) break;
      for (i=0,t=0,pline=line; i<lline&&line[i]; i++)
         if (isalnum(line[i]))  { t=1; break; }
         else if (strchr(comment,line[i])) break;
      if (t==0) continue;
      sscanf (line, "%s%*s%lf", opt, &t);
      if ((pline=strstr(line, "="))==NULL)
         error2("option file.");

      for (iopt=0; iopt<nopt; iopt++) {
         if (strncmp(opt, optstr[iopt], 8)==0)  {
            if (noisy>=9)
               printf ("\n%3d %15s | %-20s %6.2f", iopt+1,optstr[iopt],opt,t);
            switch (iopt) {
               case ( 0): sscanf(pline+1, "%s", com.seqf);    break;
               case ( 1): sscanf(pline+1, "%s", com.outf);    break;
               case ( 2): sscanf(pline+1, "%s", com.treef);    break;
               case ( 3): noisy=(int)t;           break;
               case ( 4): com.cleandata=(char)t;  break;
               case ( 5): com.verbose=(int)t;     break;
               case ( 6): com.runmode=(int)t;     break;
               case ( 7): com.method=(int)t;      break;
               case ( 8): com.clock=(int)t;       break;
               case ( 9): com.fix_rgene=(int)t;   break;
               case (10): com.Mgene=(int)t;       break;
               case (11): com.nhomo=(int)t;       break;
               case (12): com.getSE=(int)t;       break;
               case (13): com.print=(int)t;       break;
               case (14): com.model=(int)t; 
                  if(com.model>UNREST) GetStepMatrix(line);  break;
               case (15): com.fix_kappa=(int)t;   break;
               case (16): 
                  com.kappa=t;
                  if(com.fix_kappa && (com.clock==5 || com.clock==6) 
                     && com.model!=0 && com.model!=2) {
                     ng = splitline (++pline, markgenes);
                     for(j=0; j<min2(ng,com.ndata); j++) 
                        if(!sscanf(pline+markgenes[j],"%lf",&data.kappa[j])) break;
                        /* 
                        matout(F0, data.kappa, 1, min2(ng,com.ndata));
                        */
                  }
                  break;
               case (17): com.fix_alpha=(int)t;   break;
               case (18): 
                  com.alpha=t;
                  if(com.fix_alpha && t && (com.clock==5 || com.clock==6)) {
                     ng = splitline (++pline, markgenes);
                     for(j=0; j<min2(ng,com.ndata); j++) 
                        if(!sscanf(pline+markgenes[j],"%lf",&data.alpha[j])) break;
                        /*
                        matout(F0, data.alpha, 1, min2(ng,com.ndata));
                        */
                  }
                  break;
               case (19): com.nalpha=(int)t;      break;
               case (20): com.ncatG=(int)t;       break;
               case (21): com.fix_rho=(int)t;     break;
               case (22): com.rho=t;              break;
               case (23): com.nparK=(int)t;       break;
               case (24): com.ndata=(int)t;       break;
               case (25): com.bootstrap=(int)t;   break;
               case (26): Small_Diff=t;           break;
               case (27): com.icode=(int)t; com.coding=1; break;
               case (28): com.fix_blength=(int)t; break;
               case (29): com.seqtype=(int)t;     break;
            }
            break;
         }
      }
      if (iopt==nopt)
        { printf ("\noption %s in %s not recognised\n", opt,ctlf); exit(-1); }
   }
   fclose (fctl);

   if((com.fix_kappa || (com.fix_alpha&&com.alpha)) && (com.clock==5 || com.clock==6))
      printf("Using parameters from the control file.");


   if(com.seqtype!=0) error2("seqtype = 0?");
   if (com.fix_alpha==1 && com.alpha==0) {
      if (!com.fix_rho || com.rho) error2("fix rho to 0 if alpha=0.");
   }
   if (com.nparK>=1) { 
      com.fix_alpha=com.fix_rho=1; 
      if(com.alpha==0) com.alpha=0.5;
      if(com.nparK<=2) com.rho=0; else com.rho=0.4;
      if(com.nhomo>=1) error2("nhomo & nparK");
   }
   if(com.model!=F84 && com.kappa<=0)  error2("init kappa..");
   if(!com.fix_alpha && com.alpha<=0)  error2("init alpha..");
   if(!com.fix_rho && com.rho==0) { com.rho=0.001;  puts("init rho reset"); }

   if (com.alpha) 
      { if (com.ncatG<2 || com.ncatG>NCATG) error2 ("ncatG"); }
   else if (com.ncatG>1) com.ncatG=1;

   if(com.method &&(com.clock||com.rho)) 
      { com.method=0; puts("Iteration method reset: method = 0"); }
   if(com.method && (com.model==UNREST||com.model==UNRESTu))
      error2("I did not implemented method = 1 for UNREST.  Use method = 0");

   if(com.model>UNREST && com.Mgene>2)
      error2("u models don't work with Mgene");

   if (com.nhomo==2) {
      if (com.model!=K80 && com.model!=F84 && com.model!=HKY85) error2("nhomo");
   }
   else if (com.nhomo>2 && !(com.model>=F84 && com.model<=T92)) error2("nhomo");
   else if (com.nhomo>2 && com.method) error2("nhomo & method.");
   else
      if (com.nhomo==1 && !(com.model>=F81 && com.model<=REV) && com.model!=REVu)
         error2("nhomo=1 and model");

   if(com.nhomo>=2 && com.clock==2) error2("clock=2 & nhomo imcompatible");

   if(com.clock>=5 && com.model>=TN93) error2("model & clock imcompatible");

   if (com.nhomo>1 && com.runmode>0)  error2("nhomo incompatible with runmode");
   if (com.runmode==-2) error2("runmode = -2 not implemented in baseml.");
   if (com.clock && com.runmode>2)  error2("runmode & clock?");
   if (com.runmode)  com.fix_blength=0;
   if (com.runmode==3 && (com.npi || com.nparK))
      error2("runmode incompatible with nparK or nhomo.");

   if (com.model==JC69 || com.model==K80 || com.model==UNREST)
      if (com.nhomo!=2)  com.nhomo=0;
   if (com.model==JC69 || com.model==F81) { com.fix_kappa=1; com.kappa=1; }
   if (com.model==TN93 || com.model==REV || com.model==REVu)  com.fix_kappa=0;
   if (com.nparK==3) {
      puts("\n\nnparK==3, double stochastic, may not work.  Use nparK=4?\n");
      getchar();
   }
   com.fix_omega=1; com.omega=0;
   if(com.ndata<=0) com.ndata=1;
   if(com.bootstrap && com.ndata!=1) error2("ndata=1 for bootstrap.");

   return (0);
}


int GetInitials (double x[], int *fromfile)
{
/* This calculates com.np, com.ntime, com.npi, com.nrate etc., and gets 
   initial values for ML iteration.  It also calculates some of the 
   statistics (such as eigen values and vectors) that won't change during 
   the likelihood iteration.  However, think about whether this is worthwhile. 
   The readfile option defeats this effort right now as the x[] is read in 
   after such calculations.  Some of the effort is duplicated in 
   SetParameters().  Needs more careful thinking.
*/
   int i,j,k, K=com.ncatG, n31pi=(com.model==T92?1:3);
   size_t sconP_new=(size_t)(tree.nnode-com.ns)*com.ncode*com.npatt*com.ncatG*sizeof(double);
   double t=-1;

   NFunCall=NPMatUVRoot=NEigenQ=0;
   if(com.clock==ClockCombined && com.ngene<=1) 
      error2("Combined clock model requires mutliple genes.");
   GetInitialsTimes (x);

   com.plfun=lfunAdG;
   if (com.alpha==0 && com.nparK==0)  com.plfun=lfun;
   else if ((com.alpha && com.rho==0) || com.nparK==1 || com.nparK==2)
      com.plfun=lfundG;

   if(com.clock && com.fix_blength==-1) com.fix_blength=0;

   if(com.method && com.fix_blength!=2 && com.plfun==lfundG) {
      com.conPSiteClass = 1;
      if(com.sconP < sconP_new) {
         com.sconP = sconP_new;
         printf("\n%9lu bytes for conP, adjusted\n", com.sconP);
         if((com.conP = (double*)realloc(com.conP, com.sconP))==NULL)
            error2("oom conP");
      }
   }
   InitializeNodeScale();

   com.nrgene = (!com.fix_rgene)*(com.ngene-1);
   FOR (j,com.nrgene) x[com.ntime+j]=1;
   if (com.fix_kappa && (com.Mgene==3 || com.Mgene==4)) error2("Mgene options");

   if(com.model<=UNREST) {
      com.nrate=0;
      if (!com.fix_kappa) {
         if (com.model<=T92)        com.nrate=1;
         else if (com.model==TN93)  com.nrate=2;
         else                       com.nrate=(com.model==REV?5:11);
         if (com.Mgene>=3)          com.nrate*=com.ngene;
      }
   }
   switch (com.nhomo) {
   case (0): com.npi=0;           break;   /* given 1 pi */
   case (1): com.npi=1;           break;   /* solve 1 pi */
   case (2): com.npi=0;  com.nrate=tree.nbranch;  break;  /* b kappa's */
   case (3): com.npi=com.ns+(tree.root>=com.ns)+(tree.nnode>com.ns+1);
             com.nrate=(com.fix_kappa?1:tree.nbranch);  
             for(i=0; i<tree.nnode; i++)  nodes[i].label = (i<com.ns?i:com.ns);
             if(tree.root>=com.ns) nodes[tree.root].label = com.ns+1;
             break;   /* ns+2 pi */
   case (4): com.npi=tree.nnode;  com.nrate=(com.fix_kappa?1:tree.nbranch);
                                  break;   /* nnode pi   */
   case (5): com.nrate=(com.fix_kappa?1:tree.nbranch);
      for(i=0,com.npi=0; i<tree.nnode; i++) {
         j=(int)nodes[i].label;
         if(j+1>com.npi)  com.npi=j+1;
         if(j<0||j>tree.nnode-1) error2("node label in tree.");
      }
      printf("%d sets of frequency parameters\n",com.npi);
      break;   /* user-specified pi   */
   }

   if (com.model<=TN93 && com.Mgene<=1)  
      EigenTN93 (com.model,com.kappa,com.kappa,com.pi,&nR,Root,Cijk);
   if (com.model==REV || com.model==UNREST)
      FOR (j, (com.Mgene>=3?com.ngene:1)) {
         k=com.ntime+com.nrgene+j*(com.model==REV?5:11);
         FOR (i,com.nrate) x[k+i]=0.2+0.1*rndu();
         if (com.model==REV)  x[k]=1;
         else x[k]=x[k+3]=x[k+8]=1;
      }
   else 
      FOR(i,com.nrate) x[com.ntime+com.nrgene+i]=com.kappa;

   FOR(i,com.npi*n31pi) x[com.ntime+com.nrgene+com.nrate+i]=rndu()*.2;
   com.np = k = com.ntime+com.nrgene+com.nrate+com.npi*n31pi;

   if (com.alpha || com.nparK) {
      for (i=0; i<com.nalpha; i++) 
         x[k++]=com.alpha=0.01+com.alpha*(.5+rndu());
      if (!com.fix_rho)   x[k++]=com.rho=com.rho*(.5+rndu());

      if (com.rho)
         AutodGamma(com.MK, com.freqK, com.rK, &t, com.alpha,com.rho,K);
      else
         DiscreteGamma (com.freqK, com.rK, com.alpha, com.alpha, K, DGammaMean);


      if (com.nparK) { xtoy(com.rK, x+k, K-1);  k+=K-1; }
      switch (com.nparK) {
      case (2):                            /* rK & fK */
         zero(x+k, K-1);          k+=K-1;          break;
      case (3):                            /* rK & MK (double stochastic) */
         zero(x+k, (K-1)*(K-1));  k+=(K-1)*(K-1);  break;
      case (4):                            /* rK & MK */
         zero(x+k, K*(K-1));      k+=K*(K-1);      break;
      }
      com.np=k;
   }

   if(com.fix_blength==-1)
      for(i=0; i<com.np; i++)  x[i] = (i<com.ntime ? .1+rndu() : .5+rndu());

   if(finitials) readx(x,fromfile);
   else    *fromfile=0;

   return (0);
}




int SetParameters(double x[])
{
/* This sets parameters in com., nodes[], etc and is called before lfun() etc.
   Iinitialize U, V, Root etc, if necessary.
   For nhomo models (nhomo=1,3,4) 
      x[] has frequencies if (LASTROUND==1) or exp(pi)/(1+SUM(exp[pi])) if otherwise
*/
   int i, j, k, K=com.ncatG, status=0, n31pi=(com.model==T92?1:3);
   double k1=com.kappa, k2=com.kappa, t, space[NCATG*(NCATG+1)];

   if(com.clock>=5) return(0);
   if(com.fix_blength<2) SetBranch(x);

   for(i=0; i<com.nrgene; i++) com.rgene[i+1]=x[com.ntime+i];
   if(com.clock && com.clock<5 && AbsoluteRate) 
      com.rgene[0]=x[0]; /* so that rgene are absolute rates */

   if (!com.fix_kappa && com.model<=TN93 && com.clock<5) {
       com.kappa=k1=k2=x[com.ntime+com.nrgene];
       if (com.model==TN93) k2=x[com.ntime+com.nrgene+1];
   }
   if (com.nhomo==1) {
      k = com.ntime+com.nrgene+com.nrate;
      if(com.model==T92)
         { com.pi[0]=com.pi[2]=(1-x[k])/2;  com.pi[1]=com.pi[3]=x[k]/2; }
      else {
         if (!LASTROUND) f_and_x(x+k,com.pi,4,0,0);
         else            xtoy (x+k, com.pi, 3);
         com.pi[3]=1-sum(com.pi,3);
      }
      if (com.model<=TN93)
         EigenTN93(com.model,k1,k2,com.pi,&nR,Root,Cijk);
   }
   else if (com.nhomo==2)
      for (i=0,k=com.ntime+com.nrgene; i<tree.nbranch; i++)
         nodes[tree.branches[i][1]].kappa=x[k+i];
 
   if (com.model<=TN93 && com.nhomo==0 && com.Mgene<=1)
      RootTN93 (com.model, k1, k2, com.pi, &t, Root);
   else if (com.nhomo>=3) {
      for (i=0,k=com.ntime+com.nrgene; i<tree.nbranch; i++)
         nodes[tree.branches[i][1]].kappa=(com.fix_kappa?x[k]:x[k+i]); /* ?? */
      k+=com.nrate;

      FOR (i,tree.nnode) {
         j = (com.nhomo==4 ? i : (int)nodes[i].label);
         if(com.model==T92) {
            nodes[i].pi[0]=nodes[i].pi[2] = (1-x[k+j])/2;
            nodes[i].pi[1]=nodes[i].pi[3] = x[k+j]/2;
         }
         else {
            if (!LASTROUND) f_and_x(x+k+j*3, nodes[i].pi, 4,0,0);
            else            xtoy   (x+k+j*3, nodes[i].pi, 3);
            nodes[i].pi[3]=1-sum(nodes[i].pi,3);
         }
      }
      xtoy(nodes[tree.root].pi, com.pi, 4);

/*
FOR (i,tree.nnode) {
printf("node %d (%2.0f ): ", i,nodes[i].label);
FOR(j,4) printf("%8.5f", nodes[i].pi[j]);
FPN(F0);
}
getchar();
*/
   }
   else if ((com.model==REV || com.model==REVu) && com.Mgene<=1)
      EigenQREVbase (NULL, x+com.ntime+com.nrgene, com.pi, &nR, Root, Cijk);
   /*
   else if ((com.model==UNREST || com.model==UNRESTu) && com.Mgene<=1)
      EigenQunrest (NULL, x+com.ntime+com.nrgene,com.pi,&nR,cRoot,cU,cV);
   */

   if (com.nparK==0 && (com.alpha==0 || com.fix_alpha*com.fix_rho==1))
      return(status);
   if (com.nalpha>1) return (status);
   k = com.ntime+com.nrate+com.nrgene+com.npi*n31pi;
   if (!com.fix_alpha) {
      com.alpha=x[k++];
      if (com.fix_rho)
         DiscreteGamma (com.freqK,com.rK,com.alpha,com.alpha,K,DGammaMean);
   }
   if (!com.fix_rho) {
      com.rho=x[k++];
      AutodGamma (com.MK, com.freqK, com.rK, &t,com.alpha,com.rho,K);
   }
   if (com.nparK==0) return(status);

   /* nparK models */
   xtoy (x+k, com.rK, K-1);

   if (com.nparK==2) {
      if (!LASTROUND)  f_and_x(x+k+K-1, com.freqK, K,0,0);
      else             xtoy  (x+k+K-1, com.freqK, K-1);
      com.freqK[K-1]=1-sum(com.freqK, K-1);
   }
   else if (com.nparK==3) {   /* rK & MK (double stochastic matrix) */
      for (i=0,k+=K-1; i<K-1; k+=K-1,i++) {
         if (!LASTROUND) f_and_x(x+k, com.MK+i*K, K,0,0);
         else            xtoy  (x+k, com.MK+i*K, K-1);
         com.MK[i*K+K-1]=1-sum(com.MK+i*K,K-1);
      }
      FOR(j, K) {
         for(i=0,com.MK[(K-1)*K+j]=1;i<K-1; i++)
            com.MK[(K-1)*K+j]-=com.MK[i*K+j];
         if (com.MK[(K-1)*K+j]<0)
            printf("SetPar: MK[K-1][j]=%.5f<0\n",com.MK[(K-1)*K+j]);
      }
   }
   else if (com.nparK==4) { /* rK & MK */
      for (i=0, k+=K-1; i<K; k+=K-1, i++) {
         if (!LASTROUND) f_and_x(x+k, com.MK+i*K, K,0,0);
         else            xtoy  (x+k, com.MK+i*K, K-1);
         com.MK[i*K+K-1]=1-sum(com.MK+i*K,K-1);
      }
      PtoPi(com.MK, com.freqK, K, space);
   }
   com.rK[K-1]=(1-innerp(com.freqK, com.rK, K-1))/com.freqK[K-1];
   return (status);
}


int SetPGene(int igene, int _pi, int _UVRoot, int _alpha, double x[])
{
/* xcom[] does not contain time parameters
   Note that com.piG[][] have been homogeneized if (com.Mgene==3)
*/
   int nr[]={0, 1, 0, 1, 1, 1, 2, 5, 11};
   int k=com.nrgene+(com.Mgene>=3)*igene*nr[com.model];
   double *xcom=x+com.ntime;
   double ka1=xcom[k], ka2=(com.model==TN93?xcom[k+1]:-1);

   if(com.Mgene==2 && com.fix_kappa) ka1=ka2=com.kappa;

   if (_pi) {
      xtoy(com.piG[igene], com.pi, 4);
   }
   if (_UVRoot) {
      if (com.model==K80) com.kappa=ka1;
      else if (com.model<=TN93) 
         EigenTN93(com.model,ka1,ka2,com.pi,&nR,Root,Cijk);
      else if (com.model==REV || com.model==REVu)
         EigenQREVbase(NULL,xcom+k,com.pi, &nR, Root, Cijk);
   }
   if (_alpha) {
      com.alpha=xcom[com.nrgene+com.nrate+com.npi+igene]; /* check?? */
      DiscreteGamma(com.freqK,com.rK,com.alpha,com.alpha,com.ncatG,DGammaMean);
   }
   return(0);
}


int SetxBound (int np, double xb[][2])
{
/* sets lower and upper bounds for variables during iteration
*/
   int i, j, k=0, nf=0, n31pi=(com.model==T92?1:3);
   double tb[]={.4e-6, 9999}, tb0=.4e-6, rgeneb[]={1e-4,999}, rateb[]={1e-5,999};
   double alphab[]={.005, 999}, rhob[]={-0.2, 0.99}, pb[]={.00001,.99999};
   double fb[]={-19,9}; /* transformed freqs.*/

   SetxBoundTimes (xb);
   for(i=com.ntime;i<np;i++) FOR (j,2) xb[i][j]=rateb[j];

   FOR (i,com.nrgene) FOR (j,2) xb[com.ntime+i][j]=rgeneb[j];
   FOR (i,com.nrate)  FOR (j,2) xb[com.ntime+com.nrgene+i][j]=rateb[j];
   k=com.ntime+com.nrgene+com.nrate;
   for(i=0; i<com.npi*n31pi; i++) {
      xb[k][0]  =(com.model==T92?pb[0]:fb[0]);
      xb[k++][1]=(com.model==T92?pb[1]:fb[1]);
   }
   for (i=0;i<com.nalpha;i++,k++)  FOR (j,2) xb[k][j]=alphab[j];
   if (!com.fix_rho)   FOR (j,2) xb[np-1][j]=rhob[j];
   if (com.nparK) {
      FOR (i,com.ncatG-1) { xb[k][0]=rateb[0]; xb[k++][1]=rateb[1]; }
      if     (com.nparK==2) nf=com.ncatG-1;
      else if(com.nparK==3) nf=(com.ncatG-1)*(com.ncatG-1);
      else if(com.nparK==4) nf=(com.ncatG-1)*com.ncatG;
      FOR(i,nf) { xb[k][0]=fb[0]; xb[k++][1]=fb[1]; }
   }
   if(noisy>2 && np<50) {
      printf("\nBounds (np=%d):\n",np);
      FOR(i,np) printf(" %10.6f", xb[i][0]);  FPN(F0);
      FOR(i,np) printf(" %10.6f", xb[i][1]);  FPN(F0);
   }
   return(0);
}

int testx (double x[], int np)
{
/* This is used for LS branch length estimation by nls2, called only if(clock==0)
*/
   int i;
   double tb[]={.4e-6, 99};

   FOR (i,com.ntime)  
      if (x[i]<tb[0] || x[i]>tb[1]) 
         return (-1);
   return (0);
}



int ConditionalPNode (int inode, int igene, double x[])
{
   int n=4, i,j,k,h, ison, pos0=com.posG[igene],pos1=com.posG[igene+1];
   double t;

   for (i=0; i<nodes[inode].nson; i++)
      if (nodes[nodes[inode].sons[i]].nson>0 && !com.oldconP[nodes[inode].sons[i]])
         ConditionalPNode (nodes[inode].sons[i], igene, x);
   if(inode<com.ns) {  /* young ancestor */
      for(h=pos0*n; h<pos1*n; h++) 
         nodes[inode].conP[h] = 0;
   }
   else
      for(h=pos0*n; h<pos1*n; h++)
         nodes[inode].conP[h] = 1;
   if (com.cleandata && inode<com.ns) /* young ancestor */
      for(h=pos0; h<pos1; h++)
         nodes[inode].conP[h*n+com.z[inode][h]] = 1;

   for (i=0; i<nodes[inode].nson; i++) {
      ison = nodes[inode].sons[i];
      t = nodes[ison].branch*_rateSite;

      if(com.clock<5) {
         if(com.clock)  t *= GetBranchRate(igene,(int)nodes[ison].label,x,NULL);
         else           t *= com.rgene[igene];
      }
      GetPMatBranch(PMat, x, t, ison);

      if (nodes[ison].nson<1 && com.cleandata) {        /* tip && clean */
         for(h=pos0; h<pos1; h++)
            for(j=0; j<n; j++)
               nodes[inode].conP[h*n+j] *= PMat[j*n+com.z[ison][h]];
      }
      else if (nodes[ison].nson<1 && !com.cleandata) {  /* tip & unclean */
         for(h=pos0; h<pos1; h++)
            for(j=0; j<n; j++) {
               for(k=0,t=0; k<nChara[com.z[ison][h]]; k++)
                  t += PMat[j*n+CharaMap[com.z[ison][h]][k]];
               nodes[inode].conP[h*n+j] *= t;
            }
      }
      else {
         for(h=pos0; h<pos1; h++)
            for(j=0; j<n; j++) {
               for(k=0,t=0; k<n; k++)
                  t += PMat[j*n+k]*nodes[ison].conP[h*n+k];
               nodes[inode].conP[h*n+j] *= t;
            }
      }

   }        /*  for (ison)  */
   if(com.NnodeScale && com.nodeScale[inode])  NodeScale(inode, pos0, pos1);
   return (0);
}


int PMatCijk (double P[], double t)
{
/* P(t)ij = SUM Cijk * exp{Root*t}
*/
   int i,j,k, n=4, nr=nR;
   double expt[4], pij;

   if (t<-.001 && noisy>3) 
      printf ("\nt = %.5f in PMatCijk", t);
   if (t<1e-200) { identity (P, n); return(0); }

   for (k=1; k<nr; k++) expt[k]=exp(t*Root[k]);
   FOR (i,n) FOR (j,n) {
      for (k=1,pij=Cijk[i*n*nr+j*nr+0]; k<nr; k++)
         pij+=Cijk[i*n*nr+j*nr+k]*expt[k];
      P[i*n+j] = (pij>0?pij:0);
   }
   return (0);
}


#ifdef UNDEFINED

int CollapsSite (FILE *fout, int nsep, int ns, int *ncat, int SiteCat[])
{
   int j,k, it, h, b[NS], ndiff, n1, bit1;
/* n1: # of 1's   ...  bit1: the 1st nonzero bit */
   
   *ncat = 5 + (1<<(ns-1))-1 + nsep*11;
   if (fout) fprintf (fout, "\n# cat:%5d  # sep:%5d\n\n", *ncat, nsep);
 
   FOR (h, 1<<2*ns) {
      for (j=0,it=h; j<ns; b[ns-1-j]=it%4,it/=4,j++) ;
      for (j=1,ndiff=0; j<ns; j++)  {
         FOR (k,j) if (b[j]==b[k]) break;
         if (k==j) ndiff++;
      }
      switch (ndiff) {
      default  : SiteCat[h]=0;      break;
      case (0) : SiteCat[h]=b[0]+1; break;
      case (1) :
         for (j=1,it=0,n1=0,bit1=0; j<ns; j++) {
            k = (b[j]!=b[0]);
            it = it*2 + k;
            n1 += k;
            if (bit1==0 && k) bit1=ns-1-j;
         }
         it = 5 + it-1;
         if (nsep==0) { SiteCat[h]=it; break; }

         SiteCat[h]=it+min2(bit1+1,nsep)*11;
         if (n1==1 && bit1<nsep) {
            SiteCat[h]-=11;
            SiteCat[h]+=(b[0]*4+b[ns-1-bit1]-b[0]-(b[0]<=b[ns-1-bit1]));
         }
         break;
      }
      if (fout) {
         FOR (j, ns) fprintf (fout, "%1c", BASEs[b[j]]);
         fprintf (fout, "%5d    ", SiteCat[h]);
         if (h%4==3) FPN (fout);
      }
   }
   return (0);
}

int GetPexpML (double x[], int ncat, int SiteCat[], double pexp[])
{
   int  j, it, h, nodeb[NNODE]; 
   int  isum, nsum=1<<(2*(tree.nbranch-com.ns+1));
   double fh, y, Pt[NBRANCH][16];

   if (com.ngene>1 || com.nhomo || com.alpha || com.nparK || com.model>REV)
      error2 ("Pexp()");
   SetParameters (x);
   FOR (j, tree.nbranch) 
      PMatCijk (Pt[j], nodes[tree.branches[j][1]].branch);

   for (h=0; h<(1<<2*com.ns); h++) {
      if (SiteCat[h] == 0) continue;
      for (j=0,it=h; j<com.ns; nodeb[com.ns-1-j]=it&3,it>>=2,j++) ;
      for (isum=0,fh=0; isum<nsum; isum++) {
         for (j=0,it=isum; j<tree.nbranch-com.ns+1; j++)
            { nodeb[com.ns+j]=it%4; it/=4; }
         for (j=0,y=com.pi[nodeb[tree.root]]; j<tree.nbranch; j++) 
            y*=Pt[j][nodeb[tree.branches[j][0]]*4+nodeb[tree.branches[j][1]]];
         fh += y;
      }
      pexp[SiteCat[h]] += fh;
   }    
   pexp[0] = 1-sum(pexp+1,ncat-1);
   return (0);
}


int TestModel (FILE *fout, double x[], int nsep, double space[])
{
/* test of models, using com.
*/
   int j,h, it, ls=com.ls, ncat, *SiteCat;
   double *pexp=space, *nobs, lmax0, lnL0, X2, ef, de;

   SiteCat=(int*)malloc((1<<2*com.ns)* sizeof(int));
   if (SiteCat == NULL)  error2 ("oom");
   CollapsSite (F0, nsep, com.ns, &ncat, SiteCat);
   fprintf (fout, "\n\nAppr. test of model.. ncat%6d  nsep%6d\n", ncat,nsep);

   nobs = pexp+ncat;
   zero (pexp, 2*ncat);
    /* nobs */
   FOR (h, com.npatt) {
      for (j=0,it=0; j<com.ns; j++) it = it*4+(com.z[j][h]-1);
      nobs[SiteCat[it]] += com.fpatt[h];
   }
   GetPexpML (x, ncat, SiteCat, pexp);

   for (h=0,lnL0=0,X2=0,lmax0=-(double)ls*log((double)ls); h<ncat; h++) {
      if (nobs[h]>1) {
         lmax0 += nobs[h]*log(nobs[h]);
         lnL0 += nobs[h]*log(pexp[h]);
      }
      ef = com.ls*pexp[h];
      de = square(nobs[h]-ef)/ef;
      X2 += de;
      fprintf (fout, "\nCat #%3d%9.0f%9.2f%9.2f", h, nobs[h], ef,de);
   }
   fprintf (fout, "\n\nlmax0:%12.4f  D2:%12.4f   X2:%12.4f\n",
       lmax0, 2*(lmax0-lnL0), X2);
   free (SiteCat);

   return (0);
}


#endif


int OldDistributions (int inode, double oldfreq[])
{
/* reconstruct nucleotide frequencies at and down inode
   for nonhomogeneous models com.nhomo==3 or 4.
   oldfreq[tree.nnode*4]
*/
   int i, n=4;
   double kappa=com.kappa;

   if (com.alpha || com.model>REV) {
      puts("OldDistributions() does not run when alpha > 0 or model >= TN93");
      return(-1);
   }
   if (inode==tree.root) {
      xtoy (nodes[inode].pi, oldfreq+inode*n, n);
   }
   else {
      if(!com.fix_kappa) kappa=nodes[inode].kappa;
      EigenTN93 (com.model, kappa, kappa, nodes[inode].pi, &nR, Root, Cijk);
      PMatCijk (PMat, nodes[inode].branch);
      matby (oldfreq+nodes[inode].father*n, PMat, oldfreq+inode*n, 1, n,n);
   }
   FOR (i,nodes[inode].nson)
      OldDistributions (nodes[inode].sons[i], oldfreq);
   return (0);
}



/* problems and notes

   (1) AdG model: generation of com.MK[K*K] is not independent
       of com.alpha or DiscreteGamma().

non-homogeneous process models:
  nhomo            fix_kappa         models
 
  0 (1 pi given)   0 (solve 1 kappa)   JC69, K80, F81, F84, HKY85,
                                       REV(5), UNREST(11)
                   1 (1 kappa given)   K80, F84, HKY85
 
  1 (solve 1 pi)   0 (as above)        F84, HKY85, REV(5)
                   1                   F81(0), F84, HKY85        
 
  2 (b kappa's)    ?                   K80, F84, HKY85

  3 (ns+2 pi)      0 (solve 1 kappa)   F84 & HKY85  
                   1 (nbranch kappa)   F84 & HKY85  
 
  4 (nnode pi)     0,1  (as above)


space-time process models:
  nparK     fix_alpha       fix_rho        parameters 
  0         (0,1)          (0,1)           alpha & rho for AdG

  1         set to 1       set to 1        rK[]        (freqK=1/K) (K-1)
  2         set to 1       set to 1        rK[] & freqK[]          2(K-1)
  3         set to 1       set to 1        rK[] & MK[] (freqK=1/K) K(K-1)
  4         set to 1       set to 1        rK[] & MK[]             K*K-1


Local clock models
   parameters under local clock (com.clock=2)
      com.ntime = (#ancestral nodes) - 1 + (#rates) - 1
   Parameters include (ns-1) node times t[] and rates for branches.
      x[0]: t0*r0
      x[1..(nid-1)]: ti/t0 ancestral node times expressed as ratios
      x[ns-1 .. ntime-1]: rates for branches

*/
