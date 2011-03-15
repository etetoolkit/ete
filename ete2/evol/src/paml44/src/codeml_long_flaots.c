/* codeml.c  (aaml.c & codonml.c)

   Maximum likelihood parameter estimation for codon sequences (seqtype=1) 
                    or amino-acid sequences (seqtype=2)
                Copyright, Ziheng YANG, 1993-2003

               cc -o codeml -fast codeml.c tools.o -lm
                         codeml <ControlFileName>
*/


/*
#define NSSITES_K1_K2_CLASSES
#define NSSITESBandits
#define DSDN_MC  1
#define DSDN_MC_SITES  1
*/

#include "paml.h"

#define NS            5000
#define NBRANCH       (NS*2-2)
#define NNODE         (NS*2-1)
#define MAXNSONS      100
#define NGENE         2000
#define LSPNAME       50
#define NCODE         64
#define NCATG         41
#define NBTYPE        17

#define NP            (NBRANCH*2+NGENE-1+2+NCODE+2)
/*
#define NP            (NBRANCH+NGENE-1+189+2+NCODE+2)
*/
extern char BASEs[],AAs[];
extern int noisy, NFunCall, NEigenQ, NPMatUVRoot, *ancestor, GeneticCode[][64];
extern double *SeqDistance;

int  Forestry (FILE *fout);
int  GetMemPUVR(int nc, int nUVR);
int  sortwM3(double x[]);
void DetailOutput(FILE *fout, double x[], double var[]);
int  GetOptions (char *ctlf);
int  testx (double x[], int np);
int  SetxBound (int np, double xb[][2]);
int  SetxInitials (int np, double x[], double xb[][2]);
int  GetInitials (double x[], int*fromfile);
double *PointKappa (double xcom[], int igene);
double *PointOmega (double xcom[], int igene, int inode, int isiteclass);
int  GetCodonFreqs (void);
int  SetParameters (double x[]);
int  SetParametersNSsites (double x[]);
int  Set_UVR_BranchSite (int iclass, int branchlabel);
int  SetPGene (int igene, int _pi, int _UVRoot, int _alpha, double x[]);
int  SetPSiteClass(int iclass, double x[]);
int  PMatJC69like (double P[], double t, int n);
int  printfcode (FILE *fout, double fb61[], double space[]);
int  InitializeCodon (FILE *fout, double space[]);
int  AA2Codonf (double faa[20], double fcodon[]);
int  DistanceMatAA (FILE *fout);
int  GetDaa(FILE *fout, double daa[]);
void getpcodonClass(double x[], double pcodonClass[]);
int  SelectionCoefficients (FILE* fout, double kappa[], double ppi[], double omega);
int  EigenQcodon(int getstats, double blength, double *S, double *dS, double *dN,
     double Root[], double U[], double V[], double *meanrate, double kappa[], double omega, double Q[]);
int  EigenQaa(FILE *fout, double Root[], double U[], double V[],double rate[]);
int  Qcodon2aa(double Qc[], double pic[], double Qaa[], double piaa[]);
int  SetAA1STEP(void);
int  GetOmegaAA(int OmegaAA[]);
int  TestModelQc(FILE *fout, double x[]);
double lfun2dSdN(double x[], int np);
int  VariancedSdN(double t, double omega, double vtw[2*2], double vdSdN[2*2]);
int  GetCodonFreqs2 (void);
int  PairwiseCodon(FILE *fout, FILE*fds, FILE*fdn, FILE*dt, double space[]);
int  PairwiseAA(FILE *fout, FILE *f2AA);
int  lfunNSsites_rate(FILE* fout, double x[], int np);
int  lfunNSsites_M2M8(FILE* frst, double x[], int np);
int  lfunNSsites_AC(FILE* frst, double x[], int np);
double GetBranchRate(int igene, int ibrate, double x[], int *ix);
int  GetPMatBranch(double Pt[], double x[], double t, int inode);
int  ConditionalPNode(int inode, int igene, double x[]);
double CDFdN_dS(double x,double par[]);
int  DiscreteNSsites(double par[]);
char GetAASiteSpecies(int species, int sitepatt);
void finishup(void);
int  mergeSeqs(FILE*fout);
void Get4foldSites(void);
int  AdHocRateSmoothing(FILE*fout, double x[NS*3], double xb[NS*3][2], double space[]);
void DatingHeteroData(FILE* fout);

int SlidingWindow(FILE*fout, FILE* fpair[], double space[]);

void SimulateData2s61(void);
void Ina(void);
void d4dSdN(FILE*fout);

struct common_info {
   unsigned char *z[NS], *spname[NS], seqf[96],outf[96],treef[96],daafile[96], cleandata;
   char oldconP[NNODE];       /* update conP for nodes? to save computation */
   int seqtype, ns, ls, ngene, posG[NGENE+1], lgene[NGENE], npatt,*pose, readpattern;
   int runmode,clock,verbose,print, codonf,aaDist,model,NSsites;
   int nOmega, nbtype, nOmegaType;  /* branch partition, AA pair (w) partition */
   int method, icode, ncode, Mgene, ndata, bootstrap;
   int fix_rgene,fix_kappa,fix_omega,fix_alpha,fix_rho,nparK,fix_blength,getSE;
   int np, ntime, nrgene, nkappa, npi, nrate, nalpha, ncatG, hkyREV;
   size_t sconP, sspace;
   double *fpatt, *space, kappa,omega,alpha,rho,rgene[NGENE];
   double pi[NCODE], piG[NGENE][64], fb61[64];
   double f3x4[NGENE][12], *pf3x4, piAA[20];
   double freqK[NCATG], rK[NCATG], MK[NCATG*NCATG],daa[20*20], *conP, *fhK;
   double (*plfun)(double x[],int np);
   double omega_fix;  /* fix the last w in the NSbranchB, NSbranch2 models 
          for lineages.  Useful for testing whether w>1 for some lineages. */
   int     conPSiteClass; /* conPSiteClass=0 if (method==0) and =1 if (method==1)?? */
   int     NnodeScale;
   char   *nodeScale;        /* nScale[ns-1] for interior nodes */
   double *nodeScaleF;       /* nScaleF[npatt] for scale factors */
  /* pomega & pkappa are used to communicate between SetParameters & ConditionalPNode 
     & EigenQcodon.  Try to remove them? */
   double *pomega, pkappa[5], *ppi;
}  com;
struct TREEB {
   int  nbranch, nnode, root, branches[NBRANCH][2];
   double lnL;
}  tree;
struct TREEN {
   int father, nson, sons[MAXNSONS], ibranch, ipop;
   double branch, age, omega, *conP, label;
   char *nodeStr, fossil, usefossil;
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
   int root[NGENE+1], BlengthMethod, fix_nu, nbrate[NGENE], icode[NGENE];
   char   *z[NGENE][NS], cleandata[NGENE];
   char   idaafile[NGENE], daafile[NGENE][40];
   double *fpatt[NGENE], lnpT, lnpR, lnpDi[NGENE];
   double Qfactor[NGENE], pi[NGENE][NCODE];
   double rgene[NGENE], kappa[NGENE], alpha[NGENE], omega[NGENE];
   int NnodeScale[NGENE];
   char *nodeScale[NGENE];    /* nScale[data.ns[locus]-1] for interior nodes */
}  data;

extern double Small_Diff;
int Nsensecodon, FROM61[64], FROM64[64], FourFold[4][4];
int ChangedInIteration;  /* 1: t changed, update P(t); 2: paras changed, update UVRoot */
double *PMat, *U, *V, *Root, *_UU[NBTYPE+2], *_VV[NBTYPE+2], *_Root[NBTYPE+2];
/* 5 sets for branchsite models (YN2002); 6 sets for clade models */

double pcodon0[64],paa0[20], *pcodonClass;  /* for aaDist=FIT1 or FIT2 */

int BayesEB;  /* =1 for site models M2a & M8; =2 for branch-site models A & C */
int LASTROUND;
int IClass=-1;

int OmegaAA[190], AA1STEP[190];

double _rateSite=1;
double Qfactor_NS, Qfactor_NS_branch[NBTYPE];


double AAchem[][20+1]={  /* last element is the max */
{8.1, 10.5, 11.6, 13, 5.5, 10.5, 12.3, 9, 10.4, 5.2, 
 4.9, 11.3,  5.7, 5.2,  8,  9.2,  8.6, 5.4, 6.2, 5.9,    13}, /* p */
{ 31, 124,  56,  54,   55, 85, 83,   3, 96, 111, 
 111, 119, 105, 132, 32.5, 32, 61, 170, 136, 84,        170}, /* v */
{0, 0.65, 1.33, 1.38, 2.75, 0.89, 0.92, 0.74, 0.58,
 0, 0, 0.33, 0, 0, 0.39, 1.42, 0.71, 0.13, 0.2, 0,      -999},/* c */
{-0.11, 0.079, -0.136, -0.285, -0.184, -0.067, -0.246, -0.073, 0.32, 0.001,
 -0.008, 0.049, -0.041, 0.438, -0.016, -0.153, -0.208, 0.493, 0.381, -0.155} /* a */
};   /* in the order p, v, c, a */


FILE *fout, *frub, *flnf, *frst, *frst1, *frst2=NULL, *finitials;
char *ratef="rates";
enum {Fequal, F1x4, F3x4, Fcodon, F1x4MG, F3x4MG, FMutSel0, FMutSel} CodonFreqs;
char *codonfreqs[]={"Fequal", "F1x4", "F3x4", "Fcodon", "F1x4MG", "F3x4MG", "FMutSel0", "FMutSel"};
enum {NSbranchB=1, NSbranch2, NSbranch3} NSBranchModels;
char *NSbranchmodels[]={"One dN/dS ratio", 
     "free dN/dS Ratios for branches", "several dN/dS ratios for branches",
     "NSbranch3"};
enum {Poisson, EqualInput, Empirical, Empirical_F,
     FromCodon=6, REVaa_0=8, REVaa=9} AAModel;
char *aamodels[]={"Poisson", "EqualInput", "Empirical", "Empirical_F", "",
     "", "FromCodon", "", "REVaa_0", "REVaa"};
enum {NSnneutral=1, NSpselection, NSdiscrete, NSfreqs, NSgamma, NS2gamma, 
     NSbeta, NSbetaw, NSbetagamma, NSbeta1gamma, NSbeta1normal, NS02normal, 
     NS3normal} NSsitesModels;
char *NSsitesmodels[]={"one-ratio","NearlyNeutral", "PositiveSelection","discrete","freqs", 
     "gamma","2gamma","beta","beta&w>1","beta&gamma", "beta&gamma+1", 
     "beta&normal>1", "0&2normal>0", "3normal>0"};
enum {FIT1=11, FIT2=12} SiteClassModels;
enum {AAClasses=7 } aaDistModels;
char *clockstr[]={"", "Global clock", "Local clock", "ClockCombined"};
enum {GlobalClock=1, LocalClock, ClockCombined} ClockModels;

#define CODEML 1
#include "treesub.c"
#include "treespace.c"


/* variables for batch run of site models */
int ncatG0=10, insmodel=0, nnsmodels=1, nsmodels[14]={0};
/* used for sliding windows analysis */
int windowsize0=20, offset0=1, npositive=0;
double lnLmodel;

int main (int argc, char *argv[])
{
   FILE *fseq=NULL, *fpair[6]; 
   char pairfs[6][32]={"2NG.dS","2NG.dN","2NG.t", "2ML.dS","2ML.dN","2ML.t"};
   char ctlf[96]="codeml.ctl", *pmodel, timestr[64];
   char *seqtypestr[3]={"CODONML", "AAML", "CODON2AAML"};
   char *Mgenestr[]={"diff. rate", "separate data", "diff. rate & pi", 
                     "diff. rate & k&w", "diff. rate & pi & k&w"};
   int getdistance=1, i, k, s2=0, idata, nc, nUVR, seed, cleandata0;


#ifdef NSSITESBandits
   atexit(finishup);
#endif
   starttimer();

   com.ndata=1;
   noisy=0;           com.runmode=0;
   com.clock=0;       com.fix_rgene=0; /* 0: estimate rate factors for genes */
   com.cleandata=0;  /* 1: delete; 0:use missing data */
   com.seqtype=AAseq;
   com.model=Empirical_F;  
   strcpy(com.daafile, "jones.dat");
   com.icode=0;       com.nrate=0;
   com.fix_kappa=0;   com.kappa=1;    com.omega=2.1;
   com.fix_alpha=1;   com.alpha=0.;   com.ncatG=4;   /* alpha=0 := inf */
   com.fix_rho=1;     com.rho=0.;
   com.getSE=0;       com.print=0;    com.verbose=1;  com.fix_blength=0;
   com.method=0;      com.space=NULL;

   frub=gfopen("rub","w");
	frst=gfopen("rst","w");
	frst1=gfopen("rst1","w");

/*
   mergeSeqs(frst);  exit(0);
   Ina();
*/
   seed = 12346789;
   seed = 4*(int)time(NULL)+1; 
   SetSeed(seed);

#if (DSDN_MC || DSDN_MC_SITES)
   SimulateData2s61();
#endif

   if(argc>1) strcpy(ctlf,argv[1]);

   GetOptions(ctlf);
   cleandata0 = com.cleandata;
   if(com.runmode!=-2) finitials=fopen("in.codeml","r");
   else                getdistance = 1;

   fprintf(frst, "Supplemental results for CODEML (seqf: %s  treef: %s)\n", 
      com.seqf, com.treef);
   if(com.getSE==2) frst2=fopen("rst2","w");

   printf("%s in %s\n", seqtypestr[com.seqtype-1], VerStr);

   fout = gfopen(com.outf, "w");

#if(!RELEASE)
   fprintf(fout, "\nseed used = %d\n", seed);
#endif

   if(noisy && com.seqtype==CODONseq) 
      { printcu(F0,NULL,com.icode); puts("Nice code, uuh?"); }

   /* space for P&U&V&Root */
   if(com.clock==5 || com.clock==6)
      DatingHeteroData(fout);

   nUVR=1; nc=20;
   if(com.seqtype==CODONseq) { nc=64; if(com.model>=1) nUVR=NBTYPE+2; }
   else if (com.seqtype==CODONseq||com.model==FromCodon) nc=64;

   GetMemPUVR(nc, nUVR);

   if((fseq=fopen(com.seqf,"r"))==NULL || com.seqf[0]=='\0') {
      printf ("\n\nSequence file %s not found!\n", com.seqf);
      exit (-1);
   }

   /* d4dSdN(fout); */
   if (com.aaDist==AAClasses) {
      SetAA1STEP();
      GetOmegaAA(OmegaAA);
   }
   else if (com.seqtype==AAseq && com.model==REVaa_0)
      SetAA1STEP();

   if(com.seqtype==1) {
      for(i=0; i<3; i++) 
         fpair[i]=(FILE*)gfopen(pairfs[i],"w");
      if(com.runmode==-2)
         for(; i<6;i++) fpair[i]=(FILE*)gfopen(pairfs[i],"w");
   }
   else if(com.runmode==-2)
      fpair[0]=(FILE*)gfopen("2AA.t","w");

   for (idata=0; idata<com.ndata; idata++) {
      if (com.ndata>1) {
         printf ("\nData set %d ", idata+1);
         fprintf(fout, "\n\nData set %d\n", idata+1);
         fprintf(frst,"\t%d",idata+1);
         fprintf(frst1, "%d", idata+1);
         fprintf(frub,"\nData set %2d\n",idata+1);
      }

      if(idata)
         GetOptions(ctlf); /* warning: ndata, cleandata etc. are read again. */
      if(nnsmodels>1) {
         if(com.seqtype!=1) error2("batch run of site models requires codon seqs.");
         if(com.fix_omega) error2("fix omega during batch run?");
         if(com.model) error2("model should be 0 in the batch run?");
         if(com.runmode) error2("runmode?");

         com.NSsites=NSbetaw;  com.ncatG=ncatG0+1;
         printf("NSsites batch run (ncatG as in YNGP2000): ");
         for(i=0; i<nnsmodels; i++)
            printf(" %2d", nsmodels[i]); 
         FPN(F0);
      }

      com.cleandata = cleandata0;

      /* ReadSeq may change seqtype*/
      ReadSeq((com.verbose?fout:NULL),fseq, com.cleandata); 
      SetMapAmbiguity();
      
      /* AllPatterns(fout); */

      fprintf(frst1,"\t%d\t%d\t%d", com.ns, com.ls, com.npatt); 

      if (com.ngene==1) 
         com.Mgene = 0;
      if(com.ngene>1) {
         if(com.seqtype==1 && com.npi)
            error2("codon models (estFreq) not implemented for ngene > 1");
         if(com.model) error2("NSbranchsites with ngene.");
         if(com.NSsites) error2("NSsites with ngene.");
         if(com.aaDist>=FIT1)  /* because of pcodon0[] */
            { error2("ngene for amino acid fitness models"); }
      }

      if(com.ndata==1) fclose(fseq);

      i = (com.ns*2-1)*sizeof(struct TREEN);
      if((nodes=(struct TREEN*)malloc(i))==NULL) 
         error2("oom nodes");

      pmodel=(com.seqtype==CODONseq?NSbranchmodels[com.model]:aamodels[com.model]);
      fprintf(fout,"%s (in %s)  %s\n",seqtypestr[com.seqtype-1], VerStr, com.seqf);
      fprintf(fout,"Model: %s for branches", pmodel);
      if(com.clock) fprintf(fout," %s ",clockstr[com.clock]);
      if(com.seqtype==CODONseq||com.model==FromCodon) {
         if(com.fix_kappa) fprintf(fout, " kappa = %.3f fixed\n", com.kappa);
         if(com.fix_omega) fprintf(fout, " omega = %.3f fixed\n", com.omega);
      }
      if(com.seqtype==AAseq && (com.model==Empirical||com.model==Empirical_F))
         fprintf (fout, " (%s) ", com.daafile);
      if(com.seqtype==AAseq&&com.nrate) fprintf(fout,"(nrate:%d) ",com.nrate);
      if(com.alpha && com.rho) fprintf (fout, "Auto-");
      if(com.alpha) fprintf (fout,"dGamma (ncatG=%d) ", com.ncatG);
      if(com.ngene>1)
         fprintf (fout, " (%d genes: %s)  ", com.ngene, Mgenestr[com.Mgene]);

      if(com.alpha==0)  com.nalpha=0;
      else              com.nalpha=(com.nalpha?com.ngene:!com.fix_alpha);
      if(com.Mgene==1) com.nalpha=!com.fix_alpha;
      if(com.nalpha>1 && (!com.alpha || com.ngene==1 || com.fix_alpha))
         error2("Malpha");
      if(com.nalpha>1 && com.rho) error2("Malpha or rho");
      if(com.nalpha>1) fprintf (fout,"(%d gamma)", com.nalpha);
     
      if(com.Mgene && com.ngene==1) error2("Mgene for one gene.");
      if(com.seqtype==CODONseq) {
         fprintf (fout, "\nCodon frequency model: %s\n", codonfreqs[com.codonf]);
         if(com.alpha) 
            fputs("Warning: Gamma model for codons.  See documentation.",fout);
      }
      if((com.seqtype==CODONseq||com.model==FromCodon) 
         && (com.aaDist && com.aaDist<10 && com.aaDist!=AAClasses))
         fprintf(fout,"%s, %s\n",com.daafile,(com.aaDist>0?"geometric":"linear"));

      if(com.NSsites) {
         fprintf(fout,"Site-class models: ");
         if (nnsmodels==1) {
            fprintf(fout," %s",NSsitesmodels[com.NSsites]);
            if(com.NSsites>=NSdiscrete)fprintf(fout," (%d categories)",com.ncatG);
         }
         if(com.nparK) fprintf(fout," & HMM");
         FPN(fout);
         if(com.aaDist)
            fprintf(fout,"\nFitness models: aaDist: %d\n",com.aaDist);
      }
      fprintf(fout,"ns = %3d  ls = %3d\n\n", com.ns, com.ls);

      com.sspace = max2(5000000,3*com.ncode*com.ncode*sizeof(double));
      if(com.NSsites) {
         if(com.sspace < 2*com.ncode*com.ncode+4*com.npatt*sizeof(double))
            com.sspace = 2*com.ncode*com.ncode+4*com.npatt*sizeof(double);
      }
      k = com.ns*(com.ns-1)/2;
/*
      com.sspace=max2(com.sspace,
        (int)sizeof(double)*((com.ns*2-2)*(com.ns*2-2+4+k)+k));
*/
      if((com.space = (double*)realloc(com.space,com.sspace))==NULL) {
         printf("\nfailed to get %9lu bytes for space", com.sspace);
         error2("oom space");
      }
      if(getdistance) {
         SeqDistance=(double*)realloc(SeqDistance, k*sizeof(double));
         ancestor=(int*)realloc(ancestor, k*sizeof(int));
         if(SeqDistance==NULL||ancestor==NULL) error2("oom distance&ancestor");
         for(i=0; i<k; i++) SeqDistance[i] = -1;
      }
      if(com.seqtype==AAseq) {
         InitializeBaseAA (fout);
         if (com.model==FromCodon /* ||com.aaDist==AAClasses */)
            AA2Codonf(com.pi, com.fb61);  /* get codon freqs from aa freqs */ 
      }
      else {  /* codon sequences */
         if(com.sspace < max2(com.ngene+1,com.ns)*(64+12+4)*sizeof(double)) {
            com.sspace = max2(com.ngene+1,com.ns)*(64+12+4)*sizeof(double);
            if((com.space = (double*)realloc(com.space,com.sspace))==NULL)
               error2("oom space for #c");
         }
         if (InitializeCodon(fout,com.space))
            error2("giving up on stop codons");

         if(com.Mgene==3)
            for(i=0; i<com.ngene; i++)
               xtoy(com.pi,com.piG[i],com.ncode);
      }

      if(getdistance) {
         if(com.seqtype==CODONseq)
            DistanceMatNG86(fout,fpair[0],fpair[1],fpair[2],0);
         else
            DistanceMatAA(fout);
      }
      fflush(fout);

      if(com.seqtype==AAseq && com.model==Poisson && !com.print) 
         PatternWeightJC69like(fout);
      if(com.alpha || com.NSsites) {
         s2=com.npatt*com.ncatG*sizeof(double);
         if((com.fhK=(double*)realloc(com.fhK,s2))==NULL) error2("oom fhK");
      }


/********/
/*
npositive += SlidingWindow(fout, fpair, com.space); 
FPN(frst1); fflush(frst1);  
continue;
*/

      if(com.runmode==-2 && com.Mgene!=1) {
         if(com.seqtype==CODONseq) 
            PairwiseCodon(fout,fpair[3],fpair[4],fpair[5],com.space);  
         else
            PairwiseAA(fout, fpair[0]);  
      }
      else {
         com.sconP = 2L *com.ncode*com.npatt*sizeof(double);
         /* to be increased later in GetInitials() */
         /* com.sconP = (com.ns-1)*com.ncode*com.npatt*sizeof(double); */
         com.conP = (double*)realloc(com.conP, com.sconP);

         printf("\n%9u bytes for distance",com.ns*(com.ns-1)/2*sizeof(double));
         printf("\n%9u bytes for conP\n", com.sconP);
         printf ("%9u bytes for fhK\n%9u bytes for space\n", s2, com.sspace);
         if(com.conP==NULL)
            error2("oom conP");

         if (nnsmodels>1) {
            for(insmodel=0; insmodel<nnsmodels; insmodel++) {
               com.NSsites=nsmodels[insmodel];
               if(com.NSsites<=NSpselection)     com.ncatG = com.NSsites+1;
               else if (com.NSsites==NSdiscrete) com.ncatG = 3;
               else if (com.NSsites==NSfreqs)    com.ncatG=5;
               else if (com.NSsites==NSbetaw||com.NSsites==NS02normal) 
                     com.ncatG = ncatG0 + 1;
               else  com.ncatG = ncatG0;

               com.nrate=com.nkappa=(com.hkyREV?5:!com.fix_kappa);
               if(com.NSsites==0 || com.NSsites==NSbetaw)  com.nrate += !com.fix_omega;
               else if(com.NSsites==NSnneutral)            com.nrate ++;
               else if(com.NSsites==NSpselection)          com.nrate += 1+!com.fix_omega;
               else if(com.NSsites==NSdiscrete)            com.nrate += com.ncatG;

               printf("\n\nModel %d: %s\n",com.NSsites, NSsitesmodels[com.NSsites]);
               fprintf(fout,"\n\nModel %d: %s",com.NSsites,NSsitesmodels[com.NSsites]);
               fprintf(frst,"\n\nModel %d: %s",com.NSsites,NSsitesmodels[com.NSsites]);
               fprintf(frub,"\n\nModel %d: %s",com.NSsites,NSsitesmodels[com.NSsites]);
               if(com.NSsites) fprintf(fout," (%d categories)",com.ncatG);
               FPN(fout);

#ifdef NSSITESBandits
               com.fix_blength = (com.NSsites>0 ? 2 : 1);
               if(com.NSsites>0) strcpy(com.treef,"M0tree");
#endif
               Forestry(fout);

               printf("\nTime used: %s\n", printtime(timestr));
               fprintf(fout,"\nTime used: %s\n", printtime(timestr));
            }
         }
         else {
            if (com.Mgene==1)        MultipleGenes(fout, fpair, com.space);
            else if (com.runmode==0) Forestry(fout);
            else if (com.runmode==3) StepwiseAddition(fout, com.space);
            else if (com.runmode>=4) Perturbation(fout,(com.runmode==4),com.space);
            else                     StarDecomposition(fout, com.space);
            printf("\nTime used: %s\n", printtime(timestr));
            fprintf(fout,"\nTime used: %s\n", printtime(timestr));
         }
      }
      FPN(frst);  fflush(frst);  
      FPN(frst1); fflush(frst1);
      free(nodes);

   }  /* for (idata) */


/**************/
/*
printf("\nfalse positive: %6d\n", npositive);
fprintf(frst1, " false positive: %6d\n", npositive);
*/

   fclose(frst);
   k=0;
   if(com.seqtype==1) k=(com.runmode==-2?6:3);
   else if (com.runmode==-2) k=1;
   FOR(i,k) fclose(fpair[i]);
   if(com.ndata>1 && fseq) fclose(fseq);  
   fclose(fout);  fclose(frub);  
   if(finitials)  fclose(finitials);
   FreeMemPUVR();
   free(com.pose);
   for(i=0; i<com.ns; i++) free(com.z[i]);

   return (0);
}


/* x[]: t[ntime]; rgene[ngene-1]; kappa; p[](NSsites); omega[]; 
        { alpha(for NSsites) !! alpha, rho || rK[], fK[] || rK[], MK[] }
*/

int Forestry (FILE *fout)
{
   static int times=0;
   FILE *ftree, *frate=NULL;
   int  status=0, i,j=0,k, itree, ntree, np, iteration=1;
   int pauptree=0, haslength;
   double x[NP],xb[NP][2], xcom[NP-NBRANCH], lnL=0,lnL0=0, e=1e-8, tl=0, nchange=-1;
   double *g=NULL, *H=NULL;
#ifdef NSSITESBandits
   FILE *fM0tree;
#endif

   if ((ftree=fopen(com.treef,"r"))==NULL) {
      printf("\ntree file %s not found.\n", com.treef);
      exit(-1);
   }
   GetTreeFileType(ftree, &ntree, &pauptree, 0);
   if (com.alpha)
      frate=(FILE*)gfopen(ratef,"w");
   if (ntree>10 && com.npatt>10000 && com.print) 
      puts("\nlnf file may be large");
   flnf=gfopen("lnf","w+");
   fprintf(flnf,"%6d %6d %6d\n", ntree, com.ls, com.npatt);

   if(com.seqtype==1 && com.aaDist>=FIT1) {
      xtoy(com.pi,pcodon0,64);
      zero(paa0,20);
      FOR(i,com.ncode) paa0[GeneticCode[com.icode][FROM61[i]]]+=pcodon0[i];
      pcodonClass=(double*)malloc(com.ncatG*64*sizeof(double));
      if(pcodonClass==NULL) error2("oom pcodonClass");
   }

   for(itree=0; ntree==-1||itree<ntree; itree++,iteration=1) {
      if(ReadTreeN(ftree,&haslength, &i,0,1))
            { puts("end of tree file."); break; }

/*
Write code for outgroup rooting

{
int ns0=com.ns, keep[]={1,1,1,1,0};
ReRootTree(com.ns);
PruneSubTreeN(com.ns, keep);
OutTreeN(F0,0,0); FPN(F0);
continue;
}
*/

      printf("\nTREE # %2d\n", itree+1);
      fprintf(fout,"\n\nTREE # %2d:  ", itree+1);
      fprintf(flnf,"\n\n%2d\n", itree+1);
      if(com.print) fprintf (frst,"\n\nTREE # %2d\n", itree+1);
      fprintf(frub,"\n\nTREE #%2d\n", itree+1);

      if (com.fix_blength==2 && !haslength) error2("no branch lengths in tree");
      if (com.fix_blength>0 && !haslength) com.fix_blength=0;
      if (times++==0 && com.fix_blength>0 && haslength) {
         if(com.clock) puts("\nBranch lengths in tree are ignored");
         else {
            if(com.fix_blength==2)
               puts("\nBranch lengths in tree are fixed.");
            else if(com.fix_blength==1) 
               puts("\nBranch lengths in tree used as initials.");
            if(com.fix_blength==1) {
               FOR(i,tree.nnode) 
                  if((x[nodes[i].ibranch]=nodes[i].branch)<0) 
                     x[nodes[i].ibranch]=1e-5;
            }
         }
      }
      LASTROUND=0;
      if(com.cleandata) 
         nchange = MPScore(com.space);
      if(com.ns<40) { OutTreeN(F0,0,0); printf("   MP score: %.0f",nchange); }
      OutTreeN(fout,0,0); fprintf(fout,"   MP score: %.0f",nchange);

      if(!com.clock && nodes[tree.root].nson<=2 && com.ns>2) {
         puts("\nThis is a rooted tree, without clock.  Check.");
         fputs("\nThis is a rooted tree.  Please check!",fout);
      }
      GetInitials(x, &i);
      
      np = com.np;
      if(noisy>=3 && np<100) matout(F0,x,1,np);
      if(i==-1) iteration = 0;
      if(np>NP || np-com.ntime>NP-NBRANCH) error2("raise NP");
      if(com.sspace < spaceming2(np)) {
         com.sspace = spaceming2(np);
         printf ("\nspace adjusted to %9u bytes\n",com.sspace);
         if((com.space=(double*)realloc(com.space,com.sspace))==NULL) {
            printf("\ntrying to get %d bytes for ming2", com.sspace);
            error2("oom space");
         }
      }
      printf("\nntime & nrate & np:%6d%6d%6d\n",com.ntime,com.nrate,com.np);

/*
      if(itree && !finitials)  for(i=0;i<np-com.ntime;i++) x[com.ntime+i] = xcom[i];
*/
      if(iteration && np) {
         SetxBound(np, xb);
         SetxInitials (np, x, xb); /* start within the feasible region */
      }
      PointconPnodes ();

      lnL = com.plfun (x,np);
      if(noisy) {
         printf("\nnp =%6d", np);
         printf("\nlnL0 = %12.6f\n",-lnL);
      }

      if(iteration && np) {
         if(com.method == 1)
            j = minB (noisy>2?frub:NULL, &lnL,x,xb, e, com.space);
         else if (com.method==3)
            j = minB2(noisy>2?frub:NULL, &lnL,x,xb, e, com.space);
         else
            j = ming2(noisy>2?frub:NULL,&lnL,com.plfun,NULL,x,xb, com.space,e,np);

         if (j==-1 || lnL<=0 || lnL>1e7) status=-1;  else status=0;
         if(status) fprintf(fout,"\ncheck convergence..");

      }
      printf("Out..\nlnL  = %12.6f\n",-lnL);

      printf("%d lfun, %d EigenQcodon, %d P(t)\n",NFunCall, NEigenQ, NPMatUVRoot);
      if (itree==0)
         { lnL0=lnL;  FOR(i,np-com.ntime) xcom[i]=x[com.ntime+i]; }
      else if (!j)
         for (i=0; i<np-com.ntime; i++) xcom[i]=xcom[i]*.2+x[com.ntime+i]*0.8;

      if(!LASTROUND && (com.NSsites==NSpselection||com.NSsites==NSdiscrete
        ||com.NSsites==NSfreqs||com.NSsites==NS3normal)) {
         /* transform back to p0, p1,... */
         k=com.ntime+com.nrgene+com.nkappa+com.npi;

         if(com.nparK) {   /* HMM model for w */
            k += com.ncatG;
            for(i=0; i<com.ncatG; i++,k+=com.ncatG-1) 
               f_and_x(x+k,x+k,com.ncatG,0,0);
         }
         else {
            j = (com.NSsites==NS3normal ? 3 : com.ncatG);
            if(com.model && com.model<=NSbranch2) j=3;
            f_and_x(x+k,x+k,j,0,0);
         }
      }
      LASTROUND=1;
      if(com.NSsites==NSdiscrete && com.aaDist==0 && com.model==0)
         sortwM3(x);
      if(com.clock) { /* move times into x[] */
         for(i=0,j=!nodes[tree.root].fossil; i<tree.nnode; i++) 
            if(i!=tree.root && nodes[i].nson && !nodes[i].fossil) 
               x[j++] = nodes[i].age;
      }

      fprintf (fout,"\nlnL(ntime:%3d  np:%3d): %13.6f %+14.6f\n",
         com.ntime, np, -lnL, -lnL+lnL0);

      if(com.fix_blength<2) {
         OutTreeB(fout);  FPN(fout);
      }
/*
      OutTreeB(fout);  FPN(fout);
      if(com.fix_blength==2) {
         for(i=0; i<tree.nbranch; i++) fprintf(fout, " %8.5f", nodes[tree.branches[i][1]].branch);
         FPN(fout);
      }
*/
      for(i=0; i<np; i++) fprintf(fout," %8.6f",x[i]); 
      FPN(fout); fflush(fout);

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

      if(com.seqtype==1 && com.ntime && com.clock==0)
         fprintf(fout,"\nNote: Branch length is defined as number of nucleotide substitutions per codon (not per neucleotide site).\n");
      if(com.Mgene>1) {
         fprintf(fout,"Note: Branch length is defined for the first gene (site partition).\n");
         fprintf(fout,"For other genes, look at \"rates for genes\".\n");
      }

      /* if (com.clock) SetBranch (x); */
      if(com.clock && com.nbtype>1)
         fputs("\nWarning: branch rates are not yet applied in tree length and branch lengths",fout);
      if(AbsoluteRate)
         fputs("\nNote: mutation rate is not applied to tree length.  Tree has times, for TreeView",fout);
      for(i=0,tl=0; i<tree.nnode; i++) 
         if(i!=tree.root) tl += nodes[i].branch;
      fprintf(fout,"\ntree length = %9.5f%s\n",tl,com.ngene>1?" (1st gene)":"");



#ifdef NSSITESBandits
      if(com.NSsites==0) {
         for(i=com.ntime; i<com.np; i++) fprintf(frst1,"\t%.3f", x[i]);
         fprintf(frst1,"\t%.2f\t%.3f", tl, -lnL);

         fM0tree=(FILE*)gfopen("M0tree", (insmodel==0?"w":"a"));
         fprintf(fM0tree, "%d  %d\n", com.ns, 1);
         OutTreeN(fM0tree,1,1);  FPN(fM0tree);
         fclose(fM0tree);
      }
      else {
         for(i=com.ntime; i<com.np; i++) fprintf(frst1,"\t%.3f",x[i]);
         fprintf(frst1,"\t%.3f",-lnL);
      }
#else

      for(i=0; i<com.np; i++) fprintf(frst1,"\t%.3f",x[i]);
      fprintf(frst1,"\t%.3f", -lnL);

/*
      fprintf(frst1,"\t%.4f", (com.ns==2 ? x[0]*2 : 0));
      for(i=0; i<com.nkappa; i++) fprintf(frst1,"\t%.3f",x[com.ntime+i]); 
      fprintf(frst1,"\t%.4f", com.omega);
      fprintf(frst1,"\t%.3f", -lnL);
*/
#endif

      FPN(fout); OutTreeN(fout,0,1);  FPN(fout);
      FPN(fout); OutTreeN(fout,1,1);  FPN(fout);

      if(com.np-com.ntime || com.clock) 
         DetailOutput(fout,x, H);

      if (com.seqtype==AAseq && com.model>=REVaa_0)
         EigenQaa(fout, Root, U, V, x+com.ntime+com.nrgene);

      if (com.NSsites)
         lfunNSsites_rate(frst,x,np);
      if (com.print) {
         if(com.rho==0 && com.nparK==0 && com.clock<=1)
            AncestralSeqs(frst,x);
         if(!com.NSsites && com.plfun!=lfun)
            lfunRates(frate,x,np);
      }
      com.print -= 9;
      lnL = com.plfun(x,np);
      com.print += 9;

      fflush(fout);  fflush(flnf);  fflush(frst);  fflush(frst1);
   }     /* for(itree) */

   fclose(ftree); 
   if(frate) fclose(frate);
   if (com.aaDist && com.aaDist<10 && com.aaDist!=AAClasses
      && (com.seqtype==CODONseq||com.model==FromCodon))
      printf("\n%s, %s.\n", com.daafile, (com.aaDist>0 ? "geometric" : "linear"));
   if(com.seqtype==1 && com.aaDist>=FIT1) free(pcodonClass);
   if(ntree==-1)  ntree=itree;

   if(ntree>1) { 
      rewind(flnf);
      rell(flnf,fout,ntree); 
   }

   fclose(flnf);
   return (0);
}




double *PointKappa (double xcom[], int igene)
{
/* This points to the kappa parameters in xcom[], by looking at com.model, 
   igene, et&c.
*/
   int k=com.nrgene;
   int nka=(com.hkyREV?5:1), nw=(com.aaDist==AAClasses?com.nOmegaType:1);

   if(com.Mgene>1 && com.Mgene>=3)
      k += igene*(nka + nw);

   if(com.fix_kappa) return(&com.kappa);

   return(xcom+k);
}

double *PointOmega (double xcom[], int igene, int inode, int isiteclass)
{
/* This points to the omega parameters in xcom[], by looking at com.model, 
   com.NSsites and igene.  This sometimes points to com.omega or com.rK[].
   This is called by SetParameters(), DetailOutput(), etc.
   
   Difficulties in using this with lfunt() etc.

   Trying to remove global variables com.pomega and com.pkappa through 
   PointOmega and PointKappa, but was unsuccessful when too many changes were 
   made at the same time.  Perhaps look at this later.  Note that some 
   variables are passed over the head from lfunt() etc. to EigenQcodon().

   Ziheng Notes: 8 August 2003.

*/
   int k = com.nrgene+com.nkappa, backfore;
   int nka=(com.hkyREV?5:1), nw=(com.aaDist==AAClasses?com.nOmegaType:1);

   if (com.seqtype!=CODONseq && com.model!=FromCodon) 
      error2("should not be here.");

   if(com.NSsites==0 && com.model==0) { /* simple case: one ratio */
      if(com.ngene<=1) {
         if(com.fix_omega) return (&com.omega_fix);  /* fix_omega */
         else              ;
      }
      else if(com.Mgene>=3) 
         k += igene*(nka + nw) + nka;
   }
   else if(com.NSsites==0 && com.model) {  /* branch model */
      if (com.aaDist==0) {
         if(com.fix_omega && nodes[inode].label==com.nbtype-1) 
            return (&com.omega_fix);
         else k += (int)nodes[inode].label;
      }
      else if(com.aaDist==AAClasses)
         k += (int)nodes[inode].label*com.nOmegaType;
   }
   else if (com.NSsites && com.model==0) { /* site model */
      if(com.aaDist<10)
         k += com.ncatG-1+2*isiteclass;
      else if(com.aaDist==FIT1)
         k += com.ncatG-1+4*isiteclass;
      else if(com.aaDist==FIT2)
         k += com.ncatG-1+5*isiteclass;
      else 
         return (&com.rK[isiteclass]);
   }
   else if (com.NSsites && com.model<=NSbranch2) { /* branch&site models A&B */
      k += 2;   /* skip the frequencies. */
      backfore = (int)nodes[inode].label;
      if(isiteclass<2)
         return(&com.rK[isiteclass]);
      else if(isiteclass==2) {
         if(com.fix_omega && backfore) 
            return(&com.omega_fix);
         else
            k += 2 + (com.NSsites==NSpselection?0:2) + backfore;
      }
   }
   else { /* NSbranch3: Clade models C and D */
      k += com.ncatG-1;   /* skip the frequencies. */
      backfore = (int)nodes[inode].label;
      if(isiteclass<com.ncatG-1)
         return(&com.rK[isiteclass]);
      else if(isiteclass == com.ncatG-1) {
         if(com.fix_omega && backfore==com.nbtype-1) 
            return(&com.omega_fix);
         else
            k += 2 + (com.NSsites==NSpselection?0:2) + backfore;
      }
   }
   return (xcom+k);
}


int sortwM3(double x[])
{
/* sort the w values for NSsites=NSdiscrete
   This assumes that com.freqK[] and com.rK[] have been initialized.
*/
   int i, k=com.ntime+com.nrgene+com.nkappa+com.npi, index[NCATG];
   double space[NCATG];

   if(com.NSsites!=NSdiscrete) error2("sortwM3");
   if(fabs(1-sum(com.freqK,com.ncatG))>1e-6) error2("sortwM3: freqK");

   if(com.nparK) { puts("\asortwM3 for HMM not implemented yet.."); return(-1); }

   indexing(com.rK, com.ncatG, index, 0, (int*)space);
   xtoy(com.rK,space,com.ncatG);
   FOR(i,com.ncatG) com.rK[i]=space[index[i]];
   xtoy(com.freqK,space,com.ncatG);
   FOR(i,com.ncatG) com.freqK[i]=space[index[i]];
   FOR(i,com.ncatG-1) x[k+i]=com.freqK[i];
   FOR(i,com.ncatG)   x[k+com.ncatG-1+i]=com.rK[i];
   return(0);
}


void printParametersNSsites (FILE* fout, double x[])
{
   int i,j, k=com.ntime+com.nrgene+com.nkappa+com.npi;
   double w[NBTYPE][3];

   if(!com.NSsites) error2("should not be here");

   fprintf(fout,"\n\ndN/dS (w) for site classes (K=%d)\n",com.ncatG);
   if(com.model==0) {
      fputs("\np: ",fout);  for(i=0; i<com.ncatG; i++) fprintf(fout,"%9.5f", com.freqK[i]);
      fputs("\nw: ",fout);  for(i=0; i<com.ncatG; i++) fprintf(fout,"%9.5f", com.rK[i]);
      i = com.ncatG-1;
      if(com.freqK[i] < 1e-5 && com.rK[i] > 1)  fprintf(fout,"\n(note that p[%d] is zero)\n", i);
   }
   else if(com.model<=NSbranch2) {
      fprintf(fout,"\nsite class             0        1       2a       2b");
      fprintf(fout,"\nproportion     ");
      for(i=0; i<com.ncatG; i++) fprintf(fout," %8.5f", com.freqK[i]);
      fprintf(fout,"\nbackground w   ");
      for(i=0; i<com.ncatG; i++) fprintf(fout," %8.5f", com.rK[i%2]);
      fprintf(fout,"\nforeground w   ");
      for(i=0; i<com.ncatG-2; i++) fprintf(fout," %8.5f", com.rK[i%2]);
      for(i=0; i<2; i++) fprintf(fout," %8.5f", (com.fix_omega?com.omega_fix:x[com.np-1]));

      if(com.freqK[2] < 1e-5 && com.rK[2] > 1)
         fprintf(fout, "\n(note that p[2] is zero)\n");

   }
   else if (com.model==NSbranch3) {
      k += com.ncatG-1 + (com.NSsites==3 && com.ncatG>2) + 1;  /* freqs & w0 & w1 */
      for(i=0; i<com.nbtype; i++) {
         for(j=0; j<com.ncatG-1; j++) 
            w[i][j] = com.rK[j];
         w[i][com.ncatG-1] = (i==com.nbtype-1 && com.fix_omega ? com.omega_fix : x[k++]);
      }

      fprintf(fout,"\nsite class    ");
      for(i=0; i<com.ncatG; i++) fprintf(fout," %9d", i);
      fprintf(fout,"\nproportion     ");
      for(i=0; i<com.ncatG; i++) fprintf(fout, " %9.5f", com.freqK[i]);
      for(i=0; i<com.nbtype; i++) {
         fprintf(fout,"\nbranch type %d: ", i);
         for(j=0; j<com.ncatG; j++) fprintf(fout," %9.5f", w[i][j]);
      }
      i = com.ncatG-1;
      if(com.freqK[i] < 1e-5)  fprintf(fout,"\n(note that p[%d] is zero)\n", i);
   }
   fprintf(fout, "\n");
}

static int ijAAref=19*20+9; 
/* reference aa pair: VI (for REVaa, REVaa_0, AAClasses to estimate Grantham)
   The rate for this pair is set to 1, and other rates are relative to it.
*/
#define E1N(m,s) (s/sqrt(PI*2)*exp(-square((1-m)/s)/2)+m*(1-CDFNormal((1-m)/s)))


void DetailOutput (FILE *fout, double x[], double var[])
{
/* var[] is used for codon models if com.getSE=1 to calculate the variances 
   of dS and dN.
*/
   int i,j,k=com.ntime, np=com.np,npclass, ibtype;
   double om=-1,N=-1,S=0,dN=0,dS=0,dSt,dNt, mr=0, vtw[4],vSN[4], omclass[NCATG];
   double phi1=0,phi2=0, t, *tdSdNb=NULL, y;
   double mu[3]={0,1,2},sig[3]={-1}; /* 3normal: mu0=0 fixed. mu2 estimated */
   double fb3x4[12];

   fprintf(fout,"\nDetailed output identifying parameters\n");

	if(com.clock) OutputTimesRates(fout, x, var);
   k = com.ntime;
   if (com.nrgene) {
      fprintf (fout, "\nrates for %d genes:%6.0f", com.ngene, 1.);
      for(i=0; i<com.nrgene; i++) 
         fprintf (fout, " %8.5f", x[k++]);
      FPN(fout);
   }

   if (com.seqtype==CODONseq || com.model==FromCodon) {
      if (com.hkyREV) {
         fprintf(fout,"a (TC) & b (TA) & c (TG) & d (CA) & e (CG): ");
         FOR(i,5) fprintf(fout,"%8.5f ", x[k++]);  FPN(fout);
      }
      else if (!com.fix_kappa && com.Mgene<=2)
         fprintf(fout,"\nkappa (ts/tv) = %8.5f\n", x[k++]);

      if(com.npi) {
         if (com.codonf==F1x4 || com.codonf==F1x4MG || com.codonf>=FMutSel0) {
            for(j=0,fb3x4[3]=1; j<3; j++) fb3x4[j] = x[k+j];
            abyx(1/sum(fb3x4,4), fb3x4, 4);
            fprintf(fout, "\nFrequency parameters:\n");
            for(j=0;j<4;j++)
               fprintf(fout, " %9.5f (%c)", fb3x4[j], BASEs[j]);

            if(com.codonf==FMutSel) 
               for(j=0;j<4;j++)
                  fprintf(frst1, "\t%.4f", fb3x4[j]);
         }
         else if (com.codonf==F3x4 || com.codonf==F3x4MG) {
            for(j=0;j<3;j++) {
               xtoy(x+k+j*3, fb3x4+j*4, 3);
               fb3x4[j*4+3] = 1;
               abyx(1/sum(fb3x4+j*4,4), fb3x4+j*4, 4);
            }
            fprintf(fout, "\nCodon frequency model: %s", codonfreqs[com.codonf]);
            fprintf(fout, "\nFrequency parameters:\n");
            for(i=0; i<3; i++,FPN(fout)) {
               fprintf(fout, "Position %d:  ", i+1);
               for(j=0;j<4;j++) 
                  fprintf(fout, " %9.5f (%c)", fb3x4[i*4+j], BASEs[j]);
            }
         }
         if(com.npi>3 || com.codonf!=FMutSel) {
            fprintf(fout, "\nEquilibrium codon frequencies (evolver-style):\n");
            for(j=0; j<64; j++) {
              fprintf(fout," %11.8f", GeneticCode[com.icode][j]==-1?0:com.pi[FROM64[j]]);
              if((j+1)%4==0) FPN(fout);
            }
         }
         if(com.npi>3 && com.codonf>=FMutSel0) {
            if(com.codonf==FMutSel0) {
               fprintf(fout, "\nEquilibrium amino acid frequencies:\n");
               for(j=0; j<20; j++) {
                 fprintf(fout," %11.8f", com.piAA[j]);
                 if((j+1)%10==0) FPN(fout);
               }
               fprintf(fout, "\nfitness for %d codons (amino acid %c has fitness 0)\n", com.ncode, AAs[19]);
               i = GeneticCode[com.icode][FROM61[com.ncode-1]];
               y = (i == 19 ? 0 : com.ppi[3+i]);
               for(j=0; j<com.ncode; j++) {
                  i = GeneticCode[com.icode][FROM61[j]];
                 fprintf(fout," %9.6f", (i == 19 ? 0 : com.ppi[3+i])-y);
               }
            }
            else {
               fprintf(fout, "\nfitness for %d codons (GGG has fitness 0)\n", com.ncode-1);
               for(j=0; j<com.ncode-1; j++)
                 fprintf(fout," %9.6f", com.ppi[3+j]);
            }
            FPN(fout);
         }

         k += com.npi;

         if(com.codonf == FMutSel) 
            SelectionCoefficients(frst, com.pkappa, com.ppi, com.omega);
      }

      /* dN/dS by averaging over site classes.  
         Qfactor_NS was calculated during ML iteration and is used here.. 
      */
      if(com.NSsites && com.model==0) {  
         for(j=0,dS=dN=0; j<com.ncatG; j++) {
            if(com.aaDist) {
               if(com.aaDist<10)
                  com.pomega = x+k+com.ncatG-1+2*j;
               else if(com.aaDist >= FIT1) {
                  com.pomega = x+k+com.ncatG-1+j*(4+(com.aaDist==FIT2));
                  xtoy(pcodonClass+j*64, com.pi, com.ncode);
               }
            }
            mr = -1;
            EigenQcodon(1,1,&S,&dSt,&dNt,NULL,NULL,NULL, &mr, com.pkappa,com.rK[j],PMat);
            /* t=1 used here, and dS & dN used later for each branch */
            dS += com.freqK[j]*dSt;
            dN += com.freqK[j]*dNt;
            omclass[j] = dNt/dSt;
         }
         om = dN/dS;
         dS *= Qfactor_NS;
         dN *= Qfactor_NS;
         N = com.ls*3 - S;
      }


      if(!com.fix_omega && com.NSsites==0 && com.model==0 && com.aaDist!=7 && com.Mgene<=2)
         fprintf(fout,"\nomega (dN/dS) = %8.5f\n", x[k++]);

      /* dN/dS rate ratios for classes */
      if (com.NSsites>=NSgamma) {
         fprintf(fout,"\nParameters in M%d (%s):\n ", com.NSsites, NSsitesmodels[com.NSsites]);
         if(com.NSsites==NSgamma) 
            fprintf(fout,"  a=%9.5f  b=%9.5f\n",x[k],x[k+1]);
         else if(com.NSsites==NS2gamma)
            fprintf(fout," p0=%9.5f  a0=%9.5f  b0=%9.5f\n(p1=%9.5f) a1=%9.5f (b1=%9.5f)\n",
            x[k],x[k+1],x[k+2], 1-x[k], x[k+3],x[k+3]);
         else if(com.NSsites==NSbeta)
            fprintf(fout,"p=%9.5f  q=%9.5f\n",x[k],x[k+1]);
         else if(com.NSsites==NSbetaw)
            fprintf(fout," p0=%9.5f  p=%9.5f q=%9.5f\n (p1=%9.5f) w=%9.5f\n",
            x[k],x[k+1],x[k+2], 1-x[k], (com.fix_omega?com.omega:x[k+3]));
         else if(com.NSsites==NSbetagamma)
            fprintf(fout," p0=%9.5f  p=%9.5f  q=%9.5f\n(p1=%9.5f) a=%9.5f  b=%9.5f\n",
            x[k],x[k+1],x[k+2], 1-x[k], x[k+3],x[k+4]);
         else if(com.NSsites==NSbeta1gamma)
            fprintf(fout," p0=%9.5f  p=%9.5f  q=%9.5f\n(p1=%9.5f) a=%9.5f  b=%9.5f\n",
            x[k],x[k+1],x[k+2], 1-x[k], x[k+3],x[k+4]);
         else if(com.NSsites==NSbeta1normal)
            fprintf(fout," p0=%9.5f  p=%9.5f  q=%9.5f\n(p1=%9.5f) u=%9.5f  s=%9.5f\n",
            x[k],x[k+1],x[k+2], 1-x[k], x[k+3],x[k+4]);
         else if(com.NSsites==NS02normal)
            fprintf(fout,"p0=%9.5f  p1=%9.5f  u2=%9.5f  s1=%9.5f  s2=%9.5f\n",
            x[k],x[k+1],x[k+2],x[k+3],x[k+4]);
         else if(com.NSsites==NS3normal)
            fprintf(fout,"p0=%9.5f  p1=%9.5f (p2=%9.5f)\n u2=%9.5f  s0=%9.5f  s1=%9.5f  s2=%9.5f\n",
            x[k],x[k+1], 1-x[k]-x[k+1], x[k+2],x[k+3],x[k+4],x[k+5]);
      }

      if (com.NSsites==NSdiscrete && com.aaDist) { /* structural site classes */
         npclass=(com.aaDist<10 ? 2 : (com.aaDist==FIT1?4:5));
         fprintf(fout,"\nParameters in each class (%d)",npclass);
         fprintf(fout,"%s:\n\n",
            (com.aaDist<10 ? "(b, a)" : "(a_p, p*, a_v, v*, b)"));
         for(j=0,k+=com.ncatG-1; j<com.ncatG; j++,FPN(fout)) {
            fprintf(fout,"%d: f=%8.5f, ",j+1,com.freqK[j]);
            FOR(i,npclass) fprintf(fout,"%9.5f",x[k++]);
            fprintf(fout," dN/dS =%8.5f", omclass[j]);
         }
      }
      else if (com.NSsites && com.aaDist==0) {
         printParametersNSsites(fout,x);
         if (com.nparK) {
            fprintf(fout,"\nTransition matrix M in HMM: M_ij=Prob(i->j):\n");
            matout(fout, com.MK, com.ncatG, com.ncatG);
         }
      }
      else if(com.aaDist && com.aaDist<=6) { /* one class (YNH98, Genetics) */
         k = com.ntime+com.nrgene+com.nkappa+com.npi;
         fprintf (fout,"\nb = %9.5f", x[k++]);
         if (com.seqtype==CODONseq)  fprintf (fout,"\na = %9.5f\n", x[k++]);
      }
      else if(com.aaDist && com.aaDist>=11) { /* fitness, one class */
         fprintf (fout,"\nfitness model (a_p, p*, a_v, v*, (and w0 for FIT2):\n");
         k = com.ntime+com.nrgene+com.nkappa+com.npi;
         FOR(i,4+(com.aaDist==FIT2)) fprintf(fout," %9.5f",x[k++]);  FPN(fout);
      }
      else if(com.model==0 && com.NSsites==0 && !com.fix_omega && com.Mgene>2) {
         if(!com.fix_kappa && !com.fix_omega) {
            for(i=0; i<com.ngene; i++,k+=2)
               fprintf(fout,"\ngene #%2d: kappa = %9.5f omega = %9.5f", i+1, x[k], x[k+1]);
         }
         else if(com.fix_kappa) {
            for(i=0; i<com.ngene; i++,k++)
               fprintf(fout,"\ngene #%2d: omega = %9.5f", i+1, x[k]);
         }
         else if(com.fix_omega) {
            for(i=0; i<com.ngene; i++,k++)
               fprintf(fout,"\ngene #%2d: kappa = %9.5f", i+1, x[k]);
         }
      }
   }
   else 
      k += com.nrate;

   for(j=0; j<com.nalpha; j++) {
      if (!com.fix_alpha)  
         fprintf(fout,"\nalpha (gamma, K = %d) = %8.5f", com.ncatG,(com.alpha=x[k++]));
      if(com.nalpha>1) 
         DiscreteGamma(com.freqK,com.rK,com.alpha,com.alpha,com.ncatG,DGammaMean);

      fprintf(fout,"\nrate: "); FOR(i,com.ncatG) fprintf(fout," %8.5f",com.rK[i]);
      fprintf(fout,"\nfreq: "); FOR(i,com.ncatG) fprintf(fout," %8.5f",com.freqK[i]);
   }

   if (com.rho) {
      if (!com.fix_rho) fprintf (fout, "rho (correlation) = %8.5f\n", x[k]);
      fprintf (fout, "transition probabilities between rate categories:\n");
      for(i=0;i<com.ncatG;i++,FPN(fout))  FOR(j,com.ncatG) 
         fprintf(fout," %8.5f",com.MK[i*com.ncatG+j]);
   }

   if (com.aaDist==AAClasses) {
      if(com.model==0) {
         fprintf (fout, "\nw (dN/dS) classes for amino acid pairs:\n");
         for(k=0; k<com.nOmegaType; k++) {
            fprintf (fout, " %9.5f: ", x[com.ntime+com.nrgene+com.nkappa+k]);
            for(i=0;i<20;i++) for(j=0;j<i;j++)
               if (OmegaAA[i*(i-1)/2+j]==k) fprintf(fout," %c%c", AAs[i],AAs[j]);
            if (k==0)  fprintf(fout, " (background ratio)");
            FPN(fout); 
         }
      }
      else {
         fprintf (fout, "\nw (dN/dS) for branch-type and amino acid class:\n");
         k = com.ntime+com.nrgene+com.nkappa+com.npi;
         for(i=0; i<com.nbtype; i++) {
            fprintf(fout, "Branch type %d: ", i);
            for(j=0; j<com.nOmegaType; j++) {
               fprintf (fout, " %9.5f", x[k++]);
            }
            FPN(fout); 
         }
      }
   }

   /* dN & dS for each branch in the tree */
   if(com.seqtype==CODONseq && com.ngene==1 && (com.model==0 || com.NSsites==0)
      /*||com.model==FromCodon||com.aaDist==AAClasses */){
      tdSdNb = (double*)malloc(tree.nnode*3*sizeof(double));
      if(tdSdNb==NULL) error2("oom DetailOutput");
      if(com.model && com.aaDist!=AAClasses ) {  /*  branch models */
         fprintf(fout, "\nw (dN/dS) for branches: ");
         k = com.ntime+com.nrgene+com.nkappa+com.npi;
         for(i=0; i<com.nOmega-1; i++)
            fprintf(fout, " %7.5f", x[k+i]);
         fprintf(fout, " %7.5f", (com.fix_omega ? com.omega : x[k+i]));
         FPN(fout);
      }
      fputs("\ndN & dS for each branch\n\n",fout);
      fprintf(fout,"%7s%11s%8s%8s%8s%8s%8s %5s %5s\n\n",
              "branch","t","N","S","dN/dS","dN","dS","N*dN","S*dS");
      for(i=0,dNt=dSt=0; i<tree.nbranch; i++) {
         fprintf(fout,"%4d..%-3d ",tree.branches[i][0]+1,tree.branches[i][1]+1);
         k = com.ntime+com.nrgene+com.nkappa+com.npi;
/*       if(com.codonf >= FMutSel0) 
            com.ppi = x+com.ntime+com.nrgene+com.nkappa;
  */
         t = nodes[tree.branches[i][1]].branch;

         if(com.NSsites==0) {
            if (com.aaDist) om=-1; /* not used in EigenQcodon() */
            else if (com.model==0 || com.model==FromCodon)
               om = (com.fix_omega?com.omega:x[k]);
            else if (com.model==NSbranchB) om = x[k+i];
            else if (com.model==NSbranch2) om = nodes[tree.branches[i][1]].omega;

            if(com.model && com.aaDist)
               com.pomega = x + com.ntime + com.nrgene + !com.fix_kappa + com.npi
                              + (int)nodes[tree.branches[i][1]].label*com.nOmegaType;

            mr = 0;
            EigenQcodon(1,t,&S,&dS,&dN, NULL,NULL,NULL, &mr, com.pkappa,om,PMat); /* PMat destroyed! */
            dNt += dN;
            dSt += dS;
            if (com.aaDist) om = dN/dS;
/*
            if(dS<.01/com.ls) om = -1;
            else if(om==-1)   om = dN/dS;
            if(com.model==0)  om = com.omega;
*/
            N = com.ls*3-S;
            if(com.model) {
               tdSdNb[i] = t;
               tdSdNb[tree.nnode+i] = dS;
               tdSdNb[tree.nnode*2+i] = dN;
            }

            fprintf(fout," %7.70f %7.4f %7.4f %7.100f %7.100f %7.100f %5.1f %5.1f", //fprintf(fout," %7.3f %7.1f %7.1f %7.4f %7.4f %7.4f %5.1f %5.1f",
                          t,N,S,om,dN,dS,N*dN,S*dS);
            /* fprintf(frst,"%8.1f%8.1f %9.5f%9.4f%9.4f",N,S,om,dN,dS); */

            /* om not used in AAClasses model */
            if(com.getSE>1&&com.fix_blength<2&&!com.clock&&com.aaDist!=AAClasses){
               vtw[0] = var[i*np+i];  
               vtw[3] = var[k*np+k]; 
               vtw[1] = vtw[2] = var[i*np+k]; 
               VariancedSdN(t, om, vtw, vSN);
               fprintf(fout,"  dN = %7.100f +- %.100f dS = %7.100f +- %.100f",//fprintf(fout,"  dN = %7.4f +- %.4f dS = %7.4f +- %.4f",
                  dN,(vSN[3]>0?sqrt(vSN[3]):-0),dS,(vSN[0]>0?sqrt(vSN[0]):-0));
               fprintf(fout," (method 2)");
            }
            FPN(fout);
         }
         else if(com.model==0) {  /* NSsites & other site-class models */
	   fprintf(fout,"%9.70f %8.4f %8.4f %8.100f %8.100f %8.100f %6.1f %6.1f\n", //fprintf(fout,"%9.3f %8.1f %8.1f %8.4f %8.4f %8.4f %6.1f %6.1f\n",
                          t,N,S,om,dN*t,dS*t, N*dN*t,S*dS*t);
         }
         else {  /* NSbranchsites models */
            ;
         }
      }  /* for (i) */
      if(com.NSsites==0) {
         fprintf(fout,"\ntree length for dN: %12.4f\ntree length for dS: %12.4f\n", dNt,dSt);  

         fprintf(frst1,"\t%.4f\t%.4f", dNt, dSt);

      }
      if(com.model && com.NSsites==0) {
         fprintf(fout,"\ndS tree:\n");  
         for(i=0; i<tree.nbranch; i++)  
            nodes[tree.branches[i][1]].branch = tdSdNb[tree.nnode+i];
         OutTreeN(fout,1,1);
         fprintf(fout,"\ndN tree:\n");
         for(i=0; i<tree.nbranch; i++)
            nodes[tree.branches[i][1]].branch = tdSdNb[tree.nnode*2+i];
         OutTreeN(fout,1,1);  FPN(fout);
         /* revert branch lengths to the original values */
         for(i=0; i<tree.nbranch; i++)
            nodes[tree.branches[i][1]].branch = tdSdNb[i];
         free(tdSdNb);

         /* the first label is the label assigned in the tree file.  The second is w ratio */
         if(com.aaDist==0) {
            fprintf(fout,"\nw ratios as labels for TreeView:\n");  
            OutTreeN(fout, 1, PrOmega);  FPN(fout);
         }
      }
   }  /* if codonseqs */

   FPN(fout); fflush(fout);
}



void ReadNSsitesModels(char *line)
{
/* This reads the line  NSsites = 0 1 2 3 7 8  in codeml.ctl.
*/
   char *pline;
   int pop_digit, nNSsitesModels=16;

   if ((pline=strstr(line, "="))==NULL) error2(".ctl file error NSsites");
   pline++;
   for (nnsmodels=0; nnsmodels<nNSsitesModels; nnsmodels++) {
      if(sscanf(pline, "%d", &nsmodels[nnsmodels]) != 1) break;
      for(pop_digit=0; ; ) {
         if(isdigit(*pline)) { pline++; pop_digit=1; }
         else if(isspace(*pline)) {
            pline++;
            if(pop_digit) break;
         }
         else  error2(".ctl file NSsites line strange.");
      }
      if(nsmodels[nnsmodels]<0 || nsmodels[nnsmodels]>=nNSsitesModels)
         error2("NSsites model");
   }
   com.NSsites=nsmodels[0];
}


int ReadDaafiles(char *line)
{
/* This reads the daa files and set up the eigen matrices U,V,Root for combined 
   clock analyses of multiple protein data sets (clock = 5 or 6).
*/
   int  i, ng=(com.ndata>1?com.ndata:NGENE), markgenes[NGENE];

   splitline(line, markgenes);
   for(i=0; i<ng; i++) {
      if(!isalnum(line[markgenes[i]])) break;
      sscanf(line+markgenes[i], "%s", data.daafile[i]);
      printf("protein %2d uses %s\n", i+1, data.daafile[i]);
   }
   return(0);
}


int GetOptions (char *ctlf)
{
   int iopt, i,j, nopt=36, lline=255;
   char line[255], *pline, opt[99], *comment="*#";
   char *optstr[] = {"seqfile", "outfile", "treefile", "seqtype", "noisy", 
        "cleandata", "runmode", "method", 
        "clock", "getSE", "RateAncestor", "CodonFreq", "estFreq", "verbose",
        "model", "hkyREV", "aaDist","aaRatefile",
        "NSsites", "NShmm", "icode", "Mgene", "fix_kappa", "kappa",
        "fix_omega", "omega", "fix_alpha", "alpha","Malpha", "ncatG", 
        "fix_rho", "rho", "ndata", "bootstrap", "Small_Diff", "fix_blength"};
   double t;
   FILE  *fctl;
   int ng=-1, markgenes[NGENE+99];
   char *daafiles[]={"", "grantham.dat", "miyata.dat", 
                     "g1974c.dat","g1974p.dat","g1974v.dat","g1974a.dat"};

   fctl=gfopen(ctlf,"r");
   if (noisy) printf ("\n\nReading options from %s..\n", ctlf);
   for (;;) {
      if (fgets(line, lline, fctl) == NULL) break;
      for (i=0,t=0,pline=line; i<lline&&line[i]; i++)
         if (isalnum(line[i]))  { t=1; break; }
         else if (strchr(comment,line[i])) break;
      if (t==0) continue;
      sscanf (line, "%s%*s%lf", opt,&t);
      if ((pline=strstr(line, "="))==NULL) 
         error2("err: option file. add space around the equal sign?");
      for (iopt=0; iopt<nopt; iopt++) {
         if (strncmp(opt, optstr[iopt], 8)==0)  {
            if (noisy>=9)
               printf ("\n%3d %15s | %-20s %6.2f", iopt+1,optstr[iopt],opt,t);
            switch (iopt) {
               case ( 0): sscanf(pline+1, "%s", com.seqf);    break;
               case ( 1): sscanf(pline+1, "%s", com.outf);    break;
               case ( 2): sscanf(pline+1, "%s", com.treef);   break;
               case ( 3): com.seqtype=(int)t;     break;
               case ( 4): noisy=(int)t;           break;
               case ( 5): com.cleandata=(char)t;  break;
               case ( 6): com.runmode=(int)t;     break;
               case ( 7): com.method=(int)t;      break;
               case ( 8): com.clock=(int)t;       break;
               case ( 9): com.getSE=(int)t;       break;
               case (10): com.print=(int)t;       break;
               case (11): com.codonf=(int)t;      break;
               case (12): com.npi=(int)t;         break;
               case (13): com.verbose=(int)t;     break;
               case (14): com.model=(int)t;       break;
               case (15): com.hkyREV=(int)t;      break;
               case (16): com.aaDist=(int)t;      break;
               case (17): 
                  sscanf(pline+2,"%s",com.daafile); 
                  if(com.seqtype==2 && com.ndata>1 && (com.clock==5 || com.clock==6)) {
                     ReadDaafiles(pline+2);
                     break;
                  }
                  break;
               case (18): ReadNSsitesModels(line); break;
               case (19): com.nparK=(int)t;       break;
               case (20): 
                  com.icode=(int)t;
                  if(com.seqtype==1 && (com.clock==5 || com.clock==6)) {
                     ng = splitline (++pline, markgenes);
                     for(j=0; j<min2(ng,com.ndata); j++) 
                        if(!sscanf(pline+markgenes[j],"%d",&data.icode[j])) break;

for(j=0; j<min2(ng,com.ndata); j++) printf("%4d", data.icode[j]);  FPN(F0);


                  }
                  break;
               case (21): com.Mgene=(int)t;       break;
               case (22): com.fix_kappa=(int)t;   break;
               case (23): 
                  com.kappa=t;            
                  if(com.seqtype==1 && com.fix_kappa && (com.clock==5 || com.clock==6)) {
                     ng = splitline (++pline, markgenes);
                     for(j=0; j<min2(ng,com.ndata); j++) 
                        if(!sscanf(pline+markgenes[j],"%lf",&data.kappa[j])) break;

matout(F0, data.kappa, 1, min2(ng,com.ndata));
                  }
                  break;
               case (24): com.fix_omega=(int)t;   break;
               case (25): 
                  com.omega=t;            
                  if(com.seqtype==1 && com.fix_omega && (com.clock==5 || com.clock==6)) {
                     ng = splitline (++pline, markgenes);
                     for(j=0; j<min2(ng,com.ndata); j++) 
                        if(!sscanf(pline+markgenes[j],"%lf",&data.omega[j])) break;

matout(F0, data.omega, 1, min2(ng,com.ndata));
                  }

                  break;
               case (26): com.fix_alpha=(int)t;   break;
               case (27): 
                  com.alpha=t;
                  if(com.fix_alpha && t && (com.clock==5 || com.clock==6)) {
                     ng = splitline (++pline, markgenes);
                     for(j=0; j<min2(ng,com.ndata); j++) 
                        if(!sscanf(pline+markgenes[j], "%lf", &data.alpha[j])) break;

matout(F0, data.alpha, 1, min2(ng,com.ndata));
                  }
                  break;
               case (28): com.nalpha=(int)t;      break;
               case (29): com.ncatG=(int)t;       break;
               case (30): com.fix_rho=(int)t;     break;
               case (31): com.rho=t;              break;
               case (32): com.ndata=(int)t;       break;
               case (33): com.bootstrap=(int)t;   break;
               case (34): Small_Diff=t;           break;
               case (35): com.fix_blength=(int)t; break;
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

   if (noisy) FPN(F0);
   if(com.seqtype==1 || com.model==FromCodon)
      setmark_61_64 ();
   if (com.seqtype==AAseq || com.seqtype==CODON2AAseq) {
      if(com.NSsites) error2("use NSsites=0 for amino acids?");
      if(com.hkyREV && com.model!=FromCodon)  /*  REV & FromCodon not well-tested. */
         error2("use hkyREV=0 for amino acids?");
      com.ncode = 20;
      if(com.aaDist==AAClasses) 
         com.nrate = com.nkappa=(com.hkyREV ? 5 : !com.fix_kappa); 

      switch (com.model) {
      case (Poisson):  case (EqualInput): case (Empirical): case (Empirical_F):
         com.fix_kappa=1; com.kappa=0; com.nrate=0;   break;
      case (FromCodon): 
         com.nrate=com.nkappa = (com.hkyREV ? 5 : !com.fix_kappa);
         if(com.aaDist) com.nrate++;
         if(com.fix_omega) error2("fix_omega = 1");
         if(com.codonf) {
            com.codonf=0;  puts("CodonFreq=0 reset for model=6.");
         }
         break;
      case (REVaa_0): com.fix_kappa=0; com.kappa=0; break; 
      case (REVaa):   com.fix_kappa=0; com.kappa=0; com.nrate=189; break;
      default: error2("model unavailable");
      }
      if(com.Mgene>2 || (com.Mgene==2 && (com.model==Fequal||com.model==2))) 
         error2 ("Mgene && model");
      if(com.seqtype==2 && com.model!=FromCodon && com.model!=AAClasses) 
         { com.fix_kappa=com.fix_omega=1; com.kappa=com.omega=0; }
   }
   else if(com.seqtype==CODONseq) {
      if(com.nparK)
         if (com.model||com.aaDist||com.NSsites!=NSdiscrete||com.alpha||com.rho)
            error2("HMM model option");
      if(com.Mgene>1 && com.model) error2("Mgene & model?");
      if(com.fix_kappa) {
         if(com.hkyREV)
            error2("can't fix kappa for the codon model you selected.");
         else 
            com.pkappa[0] = com.kappa;
      }
      if(com.codonf>=FMutSel0 && com.Mgene>=2)
         error2("model FMutSel + Mgene not implemented");
      if(com.runmode==-2 && com.seqtype==1 && com.npi)
         error2("runmode = -2 not implemented for codon models with frequencies");
      if(com.hkyREV && (com.aaDist || com.Mgene>1))
         error2("hkyREV with aaDist or Mgene: check options?\a");
      if(com.NSsites<0 || com.NSsites>13) error2("option NSsites.");
      if(com.aaDist && com.NSsites) 
         error2("aaDist & NSsites don't work together");
      if((com.model && com.aaDist)
         && (com.model>NSbranch2 || com.aaDist!=AAClasses))
            error2("model & aaDist");
      if(com.model==NSbranch3 && com.NSsites!=2 && com.NSsites!=3)
            error2("clade model should have model = 3 NSsites = 2 or 3.");

      if(com.aaDist && com.fix_omega) 
         error2("can't fix_omega for aaDist models");
      
      com.nrate=com.nkappa = (com.hkyREV ? 5 : !com.fix_kappa);

      /* pi_T, pi_C, pi_A are counted as frequency parameters pi. */
      if(com.codonf==0)
         com.npi = 0;
      if(com.codonf==FMutSel0)     /* FMutSel0: pi_TCA plus 20 AA freqs. */
         com.npi = 3 + (com.npi ? 20-1 : 0);
      else if(com.codonf==FMutSel) /* FMutSel:  pi_TCA plus 60 codon freqs. */
         com.npi = 3 + (com.npi ? com.ncode-1 : 0);
      else if(com.npi) {
         if      (com.codonf==F1x4 || com.codonf==F1x4MG)  com.npi = 3;
         else if (com.codonf==F3x4 || com.codonf==F3x4MG)  com.npi = 9;
         else if (com.codonf==Fcodon)                      com.npi = com.ncode-1;
      }
      com.nrate += com.npi;

      if (com.aaDist!=AAClasses) {
         if(com.fix_kappa>1) error2("fix_kappa>1, not tested.");  /** ???? */
         if (com.model>0 && (com.alpha || !com.fix_alpha)) 
            error2("dN/dS ratios among branches not implemented for gamma");
         if (com.model>0 && com.clock) 
            error2("model and clock don't work together");
         if (com.fix_omega) {
            com.omega_fix=com.omega;
            if((com.model==0 && com.NSsites==NSdiscrete)
               || (com.model && com.NSsites && com.NSsites!=NSpselection
                   &&com.NSsites!=NSdiscrete && com.NSsites!=NSbetaw))
               error2("\afix_omega?");
         }
         if (com.model>NSbranch3) error2("seqtype or model.");
/*
         if (com.model==NSbranch2 && com.clock==2) 
            error2("NSbranch & local clock.");
*/
         if (com.model==NSbranch3 && com.NSsites==2 && com.ncatG!=3) 
            { com.ncatG=3; puts("ncatG=3 reset."); }
         if(com.kappa<0)  error2("kappa..");
         if (com.runmode)  com.fix_blength=0;
         if(com.runmode==-2 && (com.NSsites||com.alpha||com.aaDist))
            error2("err: incorrect model for pairwise comparison.\ncheck NSsites, alpha, aaDist.");
         if(com.runmode>0 && com.model==2) error2("tree search & model");
         if(com.aaDist && com.NSsites!=0 && com.NSsites!=NSdiscrete)
            error2("NSsites && aaDist.");

         if(com.aaDist==0) {
            if((!com.fix_omega || (com.Mgene && com.Mgene>=3)) && !com.NSsites)
               com.nrate++;
         }
         else {
            if(com.aaDist<=6)          com.nrate+=2;   /* a & b, PSB2000 */
            else if(com.aaDist==FIT1)  com.nrate+=4;   /* fitness models: */
            else if(com.aaDist==FIT2)  com.nrate+=5;   /* ap, p*, av, v*, b */
            if(com.aaDist>=FIT1) 
               for(i=0; i<2; i++) 
                  for(j=0;j<20;j++) AAchem[i][j] /= AAchem[i][20];
         }
         if (com.Mgene>=3 && com.nrate==0)  error2("Mgene");

         if(com.NSsites) {
            if(com.NSsites==NSfreqs && com.ncatG!=5)
               { puts("\nncatG changed to 5."); com.ncatG=5; }
            if(com.model && com.NSsites)
               if((com.model!=2  && com.model!=3) 
                  || (com.NSsites!=NSpselection && com.NSsites!=NSdiscrete))
               error2("only NSsites=2,3 & model=2,3 are compatible.");
            if(com.alpha || com.fix_alpha==0) error2("NSsites & gamma");
            switch(com.NSsites) {
               case (NSnneutral):   com.ncatG=2;  break;
               case (NSpselection): com.ncatG=3;  break;
               case (NSbetaw):      com.ncatG++;  break;
               case (NS02normal):   com.ncatG++;  break;
            }

            if(com.model==2) { /* branchsite models A & B */
               if(com.ncatG!=3) puts("\abranch-site model: use ncatG=3 only.");
               com.ncatG=4; 
               com.nrate += (com.NSsites==2?2:3);
            }
            else if(com.model==3) { /* Clade models C & D */
               if(com.NSsites==NSpselection) {
                  com.ncatG=3;  com.nrate+=3;
               }
               if(com.NSsites==NSdiscrete) {
                  if(com.ncatG!=2  && com.ncatG!=3) 
                     error2("use 2 or 3 for ncatG for model=3?");
                  com.nrate += com.ncatG+1;
               }
            }
            else if(com.NSsites==NSnneutral) {
               if(!com.fix_omega) com.nrate++; 
               else             { com.nrate++; com.omega_fix=com.omega; }
            }
            else if(com.NSsites==NSpselection) {
               if(!com.fix_omega) com.nrate+=2; 
               else             { com.nrate++; com.omega_fix=com.omega; }
            }
            else if(com.NSsites==NSbetaw)
               { if(!com.fix_omega) com.nrate++; else com.omega_fix=com.omega; }
            else if(com.NSsites==NSdiscrete && com.aaDist) {
               if (com.aaDist<=6) com.nrate+=com.ncatG;  /* a&b PSB2000 */
               else {  /* fitness models */
                  com.nrate=!com.fix_kappa+4*com.ncatG;
                  if(com.aaDist==FIT2) com.nrate+=com.ncatG;
               }
            }
            else if(com.NSsites==NSdiscrete) 
               com.nrate+=com.ncatG;    /* omega's */
         }
      }
   }
   else
      error2 ("seqtype..");

   if(com.runmode==-2 && com.cleandata==0) {
      com.cleandata=1; 
      if(noisy) puts("gaps are removed for pairwise comparison.");
   }
   if(com.method &&(com.clock||com.rho)) 
      { com.method=0; puts("Iteration method reset: method = 0"); }
   if(com.method && com.seqtype==2 && com.model==FromCodon) 
      { com.method=0; puts("\awork on method = 1 for model = 6"); }

   if (com.clock && com.fix_blength==2) 
      error2("can't fix branch lengths under clock model.");
   if (com.runmode==3 && (com.clock)) error2("runmode+clock");
   if (com.aaDist<=6 && (com.seqtype==CODONseq || com.model==FromCodon))
      strcpy(com.daafile, daafiles[abs(com.aaDist)]);

   if (com.fix_alpha && com.alpha==0) {
      if (com.rho) puts("rho set to 0.");  com.fix_rho=1; com.rho=0; 
   }
   if(!com.fix_alpha && com.alpha<=0) { com.alpha=0.5; puts("alpha reset"); }
   if(!com.fix_rho && com.rho==0) { com.rho=0.001;  puts("init rho reset"); }
   if(com.alpha||com.NSsites) 
      { if(com.ncatG<2 || com.ncatG>NCATG) error2("ncatG"); }
   else if (com.ncatG>1) com.ncatG=1;

#ifdef NSSITES_K1_K2_CLASSES
   if((com.NSsites==NSgamma||com.NSsites==NS2gamma||com.NSsites>=NSbetagamma)
      && com.ncatG<10) error2("need more categories for NSsites");
#endif

   if(com.ndata<=0) com.ndata=1;
   if(com.bootstrap && com.ndata!=1) error2("ndata=1 for bootstrap.");

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



int SetxBound (int np, double xb[][2])
{
   int i=-1,j,k, K=com.ncatG;
   double tb[]={4e-6,50}, tb0=1e-8, rgeneb[]={0.01,99}, rateb[]={1e-4,999};
   double alphab[]={0.002,99}, betab[]={0.005,99}, omegab[]={0.0001,999};
   double rhob[]={0.01,0.99}, pb[]={.00001,.99999};

   SetxBoundTimes (xb);
   for(i=com.ntime;i<np;i++) FOR (j,2) xb[i][j]=rateb[j];

   for(i=com.ntime;i<np;i++) { xb[i][0]=rateb[0]; xb[i][1]=rateb[1]; }
   for(i=0; i<com.nrgene; i++) for(j=0;j<2;j++) xb[com.ntime+i][j]=rgeneb[j]; 
   for(i=0; i<com.nrate; i++)  for(j=0;j<2;j++) xb[com.ntime+com.nrgene+i][j]=rateb[j];
   k = com.ntime+com.nrgene+com.nkappa; 

   /* codon frequency parameters */
   
   k += j = (com.seqtype==CODONseq && com.codonf>=FMutSel0 ? 3 : 0);
   if(com.seqtype==CODONseq && com.npi>3 
      && (com.codonf==Fcodon || com.codonf==FMutSel0 ||com.codonf==FMutSel)) {
      for( ; j<com.npi; j++) {
         xb[k][0] = -29; xb[k++][1] = 29; 
      }
   }

   /* omega parameters or those in the w distribution */
   if (com.NSsites) { /* p's before w's in xb[] */
      omegab[0] *= 0.01;

      switch(com.NSsites) {
      case(NSnneutral):  
         xb[k][0]=pb[0]; xb[k++][1]=pb[1];    /* p0 */
         xb[k][0]=omegab[0]; xb[k++][1]=1;    /* w0 < 1 */
         break;
      case(NSpselection): /* for p0, p1, w2 */
         FOR(j,2) { xb[k][0]=-99; xb[k++][1]=99; }  /* transformed p */
         xb[k][0]=omegab[0]; xb[k++][1]=1;          /* w0 < 1 */
         if(!com.fix_omega && (com.model==0 || com.model==2))  /* w2 > 1 */   
            { xb[k][0]=1; xb[k++][1]=omegab[1];  }
         else if (com.model==3) 
            FOR(j,1+!com.fix_omega) { xb[k][0]=omegab[0];  xb[k++][1]=omegab[1]; }
         break;
      case(NSdiscrete):  /* pK[] & rK[] */
         if(com.model==3) { /* Clade model D */
            if(com.nparK) error2("model & NSsites & nparK");
            FOR(j,K-1) { xb[k][0]=-99; xb[k++][1]=99; }
            FOR(j,K+1) { xb[k][0]=omegab[0];  xb[k++][1]=omegab[1]; }
         }
         else if(com.model==2) {  /* branch-site model B */
            K=3;
            if(com.nparK==0) 
               FOR(j,K-1) { xb[k][0]=-99; xb[k++][1]=99; }
            FOR(j,K) { xb[k][0]=omegab[0];  xb[k++][1]=omegab[1]; }
            if(com.nparK) 
               FOR(j,K*(K-1)) { xb[k][0]=-99; xb[k++][1]=99; }
         }
         else  {                 /* NSsites models M3 */
            FOR(j,K-1) { xb[k][0]=-99; xb[k++][1]=99; }
            FOR(j,K) { xb[k][0]=omegab[0];  xb[k++][1]=omegab[1]; }
         }

         if(com.seqtype==CODONseq && com.aaDist)
            FOR(j,K) { xb[k][0]=omegab[0];  xb[k++][1]=omegab[1]; }
         break; 
      case(NSfreqs):     /* p0...pK */
         FOR(j,K-1) { xb[k][0]=-99; xb[k++][1]=99; }
         break; 
      case(NSgamma):
         FOR(j,2) { xb[k][0]=alphab[0]; xb[k++][1]=alphab[1]; } break;
      case(NS2gamma):    /* p0, alpha1,beta1,alpha2=beta2 */
         xb[k][0]=pb[0]; xb[k++][1]=pb[1];
         FOR(j,3) { xb[k][0]=alphab[0]; xb[k++][1]=alphab[1]; }
         break;
      case(NSbeta):       /* p_beta,q_beta */
         FOR(j,2) { xb[k][0]=betab[0]; xb[k++][1]=betab[1]; } 
         break;
      case(NSbetaw):
         /* p0, p_beta, q_beta, w */
         xb[k][0]=pb[0]; xb[k++][1]=pb[1]; /* p0 */
         FOR(j,2) { xb[k][0]=betab[0]; xb[k++][1]=betab[1]; }  /* p & q */
         if(!com.fix_omega) { xb[k][0]=1;  xb[k++][1]=omegab[1]; }
         break;
      case(NSbetagamma):  /* p0, p_beta, q_beta, alpha, beta */
         xb[k][0]=pb[0]; xb[k++][1]=pb[1]; /* p0 */
         FOR(j,4) { xb[k][0]=betab[0]; xb[k++][1]=betab[1]; }  /* p&q, a&b */
         break;
      case(NSbeta1gamma):  /* p0, p_beta, q_beta, alpha, beta */
         xb[k][0]=pb[0]; xb[k++][1]=pb[1]; /* p0 */
         FOR(j,4) { xb[k][0]=betab[0]; xb[k++][1]=betab[1]; }  /* p&q, a&b */
         break;
      case(NSbeta1normal):  /* p0, p_beta, q_beta, mu, s */
         xb[k][0]=pb[0]; xb[k++][1]=pb[1]; /* p0 */
         FOR(j,4) { xb[k][0]=betab[0]; xb[k++][1]=betab[1]; }  /* p&q, mu&s */
         xb[k-2][0]=1;  xb[k-2][1]=9;  /* mu */
         break;
      case(NS02normal):   /* p0, p1, mu2, s1, s2 */
         FOR(j,2) { xb[k][0]=pb[0];  xb[k++][1]=pb[1]; }  /* p0 & p1, */
         FOR(j,3) { xb[k][0]=.0001; xb[k++][1]=29; }  /* mu2,s1,s2 */
         break;
      case(NS3normal):    /* p0, p1, mu2, s0, s1, s2 */
         FOR(j,2) { xb[k][0]=-49;  xb[k++][1]=49; }  /* p0 & p1, tranformed */
         FOR(j,4) { xb[k][0]=.0001; xb[k++][1]=29; }  /* mu2,s0,s1,s2 */
         break;
      }
   }
   else if((com.seqtype==CODONseq||com.model==FromCodon)&&com.aaDist!=AAClasses)
     { if(!com.fix_omega) { xb[k][0]=omegab[0]; xb[k][1]=omegab[1]; } }

   if(com.seqtype==CODONseq && com.model)
      for(j=0; j<com.nOmega-com.fix_omega; j++) 
         { xb[k+j][0]=omegab[0]; xb[k+j][1]=omegab[1]; }

   if (com.aaDist<0 && (com.seqtype==1||com.model==FromCodon)) {
      /* linear relationship between d_ij and w_ij */
      if(com.nrate != !com.fix_kappa+1+(com.seqtype==1)) error2("in Setxbound");
      xb[com.ntime+com.nrgene+!com.fix_kappa][1]=1; /* 0<b<1 */
   }

   k=com.ntime+com.nrgene+com.nrate;
   for (i=0;i<com.nalpha;i++,k++)  FOR (j,2) xb[k][j]=alphab[j];
   if (!com.fix_rho)   FOR (j,2) xb[np-1][j]=rhob[j];

   if(noisy>=3 && np<100) {
      printf("\nBounds (np=%d):\n",np);
      for(i=0;i<np;i++) printf(" %10.6f", xb[i][0]);  FPN(F0);
      for(i=0;i<np;i++) printf(" %10.6f", xb[i][1]);  FPN(F0);
   }

   return(0);
}

void getpcodonClass(double x[], double pcodonClass[])
{
/* This uses pcodon0[], paa0[], and x[] to calculate pcodonclass[] and
   com.pi[] for the fitness models.
   pcodon0[] has the codon frequencies observed (codonFreq=3) or expected 
   (codonFreq=2 or 1 or 0) rootally.  Under the fitness models, the expected 
   codon frequencies pcodonClass[] differs among site classes and from the 
   rootal pi[] (pcodon0[]).
   This is called by SetParameters().
*/
   int i,iclass,iaa, k, nclass=(com.NSsites==0?1:com.ncatG);
   double paaClass[20], *w,fit;

   if(com.seqtype!=1 || com.aaDist<FIT1) error2("getpcodonClass");
   k=com.ntime+com.nrgene+!com.fix_kappa+nclass-1;
   FOR(iclass, nclass) {
      w=x+k+iclass*(4+(com.aaDist==FIT2));
      FOR(iaa,20) {
         fit = -w[0]*square(AAchem[0][iaa]-w[1])
               -w[2]*square(AAchem[1][iaa]-w[3]);
         paaClass[iaa]=exp(2*fit);
      }
      abyx(1/sum(paaClass,20), paaClass, 20);
      FOR(i,com.ncode) {
         iaa=GeneticCode[com.icode][FROM61[i]];
         pcodonClass[iclass*64+i]=pcodon0[i]/paa0[iaa]*paaClass[iaa];
      }

if(fabs(1-sum(pcodonClass+iclass*64,com.ncode))>1e-5) error2("pcodon!=1");
/*
fprintf(frst,"\nSite class %d: ",iclass+1);
matout (frst,paaClass,2, 10);
matout (frst,pcodonClass+iclass*64,16,4);
*/
   }
   if(nclass==1) FOR(i,com.ncode) com.pi[i]=pcodonClass[i];
}



int GetInitialsCodon (double x[])
{
/* This sets the initials and count com.np for codon models.
*/
   int k=com.ntime+com.nrgene, i,j, K=com.ncatG, nsyncodon[20];
   double mr=0;

   if(com.nrate) { /* either kappa, omega, or both for each gene */
      if(com.Mgene<=2) {
         if(com.hkyREV) {
            x[k++]=.5+rndu(); 
            for(i=0; i<4; i++) x[k++]=.1+rndu(); 
         }
         else if (!com.fix_kappa) 
            x[k++] = com.kappa;
         if(com.codonf==FMutSel0 || com.codonf==FMutSel) {
            for(i=0;i<3;i++)   /* pi_TCA */
               x[k++] = com.pf3x4[i]/(com.pf3x4[3]+.02*rndu());

            if(com.npi>3 && com.codonf==FMutSel0) {
               for(i=0; i<20; i++) nsyncodon[i]=0;
               for(i=0; i<com.ncode; i++)
                  nsyncodon[GeneticCode[com.icode][FROM61[i]]] ++;
               for(i=0; i<20-1; i++)   /* amino acid fitness, ignoring nsyncodon */
                  x[k++] = log((com.piAA[i]/nsyncodon[i]+.001)/(com.piAA[19]/nsyncodon[19]+.002*rndu()));
            }
            else if(com.npi>3 && com.codonf==FMutSel) {
               for(i=0;i<com.ncode-1;i++)   /* codon fitness */
                  x[k++] = log((com.pi[i]+.001)/(com.pi[com.ncode-1]+.002*rndu()));
            }
         }
         else if(com.npi) {
            if(com.codonf==Fcodon) 
               for(i=0;i<com.ncode-1;i++)   /* codon fitness */
                  x[k++] = log((com.pi[i]+.001)/(com.pi[com.ncode-1]+.002*rndu()));
            else if(com.codonf==F1x4 || com.codonf==F1x4MG) 
               for(i=0;i<3;i++)   /* pi_TCA */
                  x[k++] = com.pf3x4[i]/(com.pf3x4[3]+.02*rndu());
            else if(com.codonf==F3x4 || com.codonf==F3x4MG) 
               for(j=0; j<3; j++)
                  for(i=0;i<3;i++)   /* pi_TCA */
                     x[k++] = com.pf3x4[j*4+i]/(com.pf3x4[j*4+3]+.02*rndu());
         }
         if (com.NSsites==0 && com.model==0) {
            if (!com.aaDist)
               { if(!com.fix_omega)    x[k++]=com.omega; }
            else
               { x[k++]=0.11; x[k++]=0.22; }
         }
      }
      else { /* com.Mgene==3,4 */
         if(com.Mgene>=3) {
            com.nrate *= com.ngene;
            if(com.fix_omega) com.nrate--;
         }
         for(i=0; i<com.ngene; i++) {
            if(com.hkyREV) 
               error2("hkyREV for ngene>1.  Fix me.");
            if(!com.fix_kappa && !com.fix_omega)
               { x[k++] = com.kappa;  x[k++] = com.omega; }
            else if (com.fix_kappa) 
               x[k++] = com.omega;
            else if (com.fix_omega) {
               x[k++] = com.kappa;  
               if(i!=com.ngene-1) x[k++] = com.omega;
            }
         }
      }
   }

   if(com.model && com.model<=NSbranch3) {  /* branch models */
      if (com.model==NSbranchB) {
         com.nbtype = tree.nbranch;
         for(i=0; i<tree.nbranch; i++) 
            nodes[(int)tree.branches[i][1]].label = i;
      }
      if(com.NSsites==0) {
         com.nOmega = com.nbtype;
         if(com.aaDist==0)
            com.nrate = com.nkappa+!com.fix_omega+com.nbtype-1;
         else if (com.aaDist==AAClasses) 
            com.nrate = com.nkappa + com.nOmegaType*com.nbtype;
   
         else if (com.model==NSbranchB || com.model==NSbranch2)
            com.nrate += (com.model==NSbranchB ? tree.nbranch : com.nOmega-1+!com.fix_omega);

         k = com.ntime+com.nrgene;
         for(i=0; i<com.nrate; i++)
            x[k++] = com.omega * (0.8+0.4*rndu());
      }
   }


   if (com.NSsites==0 && com.nrate==0)
      EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr, (com.nkappa>1?x+com.ntime+com.nrgene:&com.kappa), com.omega,PMat);


   /* branch-site and clade models 
      com.nOmega=2 different w's at a site (three w's in the model: w0,w1,w2) */
   if(com.model && com.NSsites) {
      if(com.model==NSbranch2) { /* branch-site models A & B */
         com.ncatG=4;  K=3;
         if(com.NSsites==NSdiscrete) 
            com.nrate = com.nkappa +com.npi + 2 +!com.fix_omega+com.nbtype-1-1; /* add w0 and w1 */
         else 
            com.nrate = com.nkappa +com.npi +1+!com.fix_omega+com.nbtype-1-1;
      }

      /* add p0 and p1.  check that this works for NSbranch2 */
      k = com.ntime+com.nrgene+com.nkappa+com.npi;

      if(com.model<=NSbranch2) { /* branch-site models A & B */
         /* p0 and p1:  x[0,1]=1,0, for p[]=0.6 0.2 */
         x[k++] = 1+0.2*rndu();
         if(K==3) x[k++] = 0.2*rndu();
         if(com.NSsites == 2)        /* w0<1, w1=1 (if present) */
            x[k++] = 0.2+0.1*rndu();
         else if(com.NSsites == NSdiscrete) {   /* w0 and w1 for model B */
            x[k++] = 0.2*rndu();
            if(K==3) x[k++] = 0.4+.8*rndu();
         }
         if(!com.fix_omega)  
            x[k++] = 1+0.5*rndu();  /* w2 */
      }
      else { /* NSbranch3: clade models C and D */
         x[k++] = 1 + rndu();
         if(com.ncatG == 3) x[k++] = .5+rndu();   /* p0 and p1 */
         if(com.NSsites == NSpselection)        /* w0<1, w1=1 (if present) */
            x[k++] = 0.4*rndu();
         else if(com.NSsites == NSdiscrete) {   /* w0 and w1 */
            x[k++] = 0.4*rndu();
            if(com.ncatG==3) x[k++] = 0.5+.5*rndu();
         }
         for(i=0; i<com.nbtype-1; i++)    /* additional w's */
            x[k++] = com.omega*(1+0.5*rndu());
         if(!com.fix_omega) 
            x[k++] = com.omega*(1+0.5*rndu());
      }
   }
   else if (com.NSsites) {        /* w's are counted in com.nrate */
      switch(com.NSsites) {
      case(NSnneutral):
         x[k++]=0.5+0.4*rndu();   /* p0 for w0<1 */
         x[k++]=0.1+0.5*rndu();             /* w0<1 */
         break;
      case(NSpselection): /* for p0, p1.  w is counted in nrate.  */
         x[k++]=.8+rndu(); x[k++]=.1+.5*rndu();   /* p0, p1 */
         x[k++]=0.1+0.4*rndu();             /* w0<1 */
         if(!com.fix_omega) { 
            x[k++]=com.omega;    /* w2 */
            if(com.omega<1) {
               puts("\ninitial w for M2:NSpselection reset.");
               x[k-1]=2+rndu();
            }
         }
         break;  
      case(NSdiscrete):
         if(com.aaDist) {
            for(i=0; i<com.ncatG-1; i++) x[k++]=0.;
            if(com.aaDist<=6) 
               for(i=0;i<com.ncatG;i++) { x[k++]=1.1; x[k++]=1.2; }
            for(i=0;i<com.ncatG;i++) /* ap,p*,av,v*, and b for each site class */
               FOR(j,4+(com.aaDist==FIT2)) x[k++]=rndu();
         }
         else if(com.nparK) { /* K*(K-1) paras in HMM of dN/dS over sites */
            zero(x+k,com.ncatG*(com.ncatG-1)); 
            k += com.ncatG*(com.ncatG-1);
         }
         else  {   /* p0...pK.  Note that w's are counted in nrate  */
            for(i=0;i<com.ncatG-1;i++) x[k++]=rndu();
            for(i=0;i<com.ncatG;i++)
               x[k++]=com.omega * (.5+i*2./com.ncatG*(0.8+0.4*rndu()));
         }
         break;
      case(NSfreqs):    /* p0...pK.  w's are fixed  */
         for(i=0;i<com.ncatG-1;i++) x[k++]=(com.ncatG-j)/2.;
         break;
      case(NSgamma):  x[k++]=1.1; x[k++]=1.1; break;
      case(NS2gamma):    /* p0, alpha1,beta1,alpha2=beta2 */
         x[k++]=0.5; FOR(j,3) x[k++]=2*rndu()+j*0.1; break;
      case(NSbeta):       /* p_beta,q_beta */
         x[k++]=.2+rndu(); x[k++]=1+rndu(); break; 
      case(NSbetaw):
         /* p0, p_beta, q_beta.  w is counted in nrate. */
         x[k++]=.9; x[k++]=.2+rndu(); x[k++]=1+rndu();
         if(!com.fix_omega) {
            x[k++]=com.omega;
            if(com.omega<1) {
               puts("\ninitial w for M8:NSbetaw>1 reset.");
               x[k-1]=2+rndu();
            }
         }
         break;
      case(NSbetagamma):  /* p0, p_beta, q_beta, alpha, beta */
         x[k++]=.9; x[k++]=.4; x[k++]=1.2; x[k++]=1.1; x[k++]=1.1;
         break;
      case(NSbeta1gamma):  /* p0, p_beta, q_beta, alpha, beta */
         x[k++]=.9; x[k++]=.4; x[k++]=1.2; x[k++]=.1; x[k++]=1.1;
         break;
      case(NSbeta1normal):  /* p0, p_beta, q_beta, alpha, beta */
         x[k++]=.95; x[k++]=.4; x[k++]=1.2; x[k++]=1.1; x[k++]=1.1;
         break;
      case(NS02normal):    /* p0, p1, mu2, s1, s2 */
         x[k++]=.8; x[k++]=0.3;   /* p0 & p1, not transformed */
         x[k++]=.2; /* mu2 */ 
         x[k++]=5; x[k++]=1.1;  /* s1,s2 */
         break;
      case(NS3normal):    /* p0, p1, mu2, s0, s1, s2 */
         x[k++]=.77; x[k++]=0.22;   /* p0 & p1, transformed */
         x[k++]=.2; /* mu2 */ 
         x[k++]=0.5; x[k++]=5; x[k++]=1.1;  /* s0,s1,s2 */
         break;
      }
   }     /* if(com.NSsites) */

   com.np = k;
   return(0);
}


int GetInitials (double x[], int* fromfile)
{
/* This caculates the number of parameters (com.np) and get initial values.
   This routine is too messy.  Perhaps try to restruct the code and make 
   two sections for amino acids and codons?
   com.nrate is initialised in getoptions().
*/
   static int times=0;
   int i, j,k=0, naa=20;
   int K=(com.model==2&&com.NSsites?com.ncatG-1:com.ncatG);
   size_t sconP_new = (size_t)(tree.nnode-com.ns)*com.ncode*com.npatt*sizeof(double);
   double t;

   NFunCall = NPMatUVRoot = NEigenQ = 0;
   if(com.clock==ClockCombined && com.ngene<=1) 
      error2("Combined clock model requires mutliple genes.");
   GetInitialsTimes(x);

   com.plfun = (com.alpha==0 ? lfun : (com.rho==0?lfundG:lfunAdG));
   if(com.NSsites) com.plfun=lfundG;
   if(com.nparK) com.plfun=lfunAdG;

   if(com.plfun==lfun) com.conPSiteClass=0;
   if(com.method && com.fix_blength!=2 && com.plfun==lfundG) {
      com.conPSiteClass=1;
      sconP_new *= com.ncatG;
   }
   if(com.sconP<0 || sconP_new<0) error2("data set too large.");
   if(com.sconP<sconP_new) {
      com.sconP = sconP_new;
      printf("\n%9lu bytes for conP, adjusted\n", com.sconP);
      if((com.conP=(double*)realloc(com.conP, com.sconP))==NULL) 
         error2("oom conP");
   }

   InitializeNodeScale();

   if(times++==0) {
      if((com.aaDist && com.aaDist<10 && com.aaDist!=AAClasses &&
          (com.seqtype==CODONseq||com.model==FromCodon)) ||
          (com.seqtype==AAseq &&
          (com.model==Empirical||com.model==Empirical_F||com.model>=REVaa_0))){
         GetDaa(NULL,com.daa);
      }
   }
   com.nrgene = (!com.fix_rgene)*(com.ngene-1);
   for(j=0; j<com.nrgene; j++) x[com.ntime+j] = 1;


   if(com.seqtype==CODONseq) 
      GetInitialsCodon(x);
   else {
      com.np = com.ntime+com.nrgene+com.nrate;

      k=com.ntime+com.nrgene;
      if (com.aaDist==AAClasses) { 
         if (!com.fix_kappa) x[k++]=com.kappa;
         FOR (i,com.nrate-!com.fix_kappa) x[k++]=com.omega;
         if (com.nOmegaType>65) 
            puts("\a\nget better initial values for AAclasses?");
      }
      else {
         if (com.seqtype==AAseq) {   /* AAseq */
            if (com.nrate==0)
               EigenQaa(NULL, Root, U, V, &t); /* once for all */
            if (com.model==REVaa_0) {
               for(i=0;i<naa;i++) for(j=0;j<i;j++) 
                  if (AA1STEP[i*(i-1)/2+j] && i*naa+j!=ijAAref)
                     x[k++]=com.daa[i*naa+j];
            }
            else if (com.model==REVaa) { 
               for (i=1; i<naa; i++)  FOR(j,i)
                  if(i*naa+j!=ijAAref) x[k++]=com.daa[i*naa+j];
            }
            else if (com.model==FromCodon) {
               FOR(j,com.nkappa)  x[k++]=com.kappa;
               FOR(j,com.nrate-com.nkappa)  x[k++]=com.omega; 
            }
         }
      }
   }

   for (i=0; i<com.nalpha; i++) x[com.np++] = com.alpha;

   if (!com.fix_rho) x[com.np++]=com.rho;
   if (com.rho)
      AutodGamma (com.MK, com.freqK, com.rK, &t, com.alpha, com.rho,com.ncatG);
   else if (com.alpha && com.fix_alpha && !com.NSsites)
      DiscreteGamma(com.freqK,com.rK,com.alpha,com.alpha,com.ncatG,DGammaMean);

   if(com.fix_blength==-1)
      for(i=0; i<com.np; i++)  x[i] = (i<com.ntime ? .1+0.5*rndu() : 0.5+rndu());

   *fromfile=0;
   if(finitials) {
      readx(x,fromfile);
      if(com.runmode>0 && fromfile && com.NSsites)  LASTROUND=1;
   }

   return (0);
}



int SetPGene (int igene, int _pi, int _UVRoot, int _alpha, double x[])
{
/* xcom[] does not contain time parameters
   Note that com.piG[][] have been homogeneized if (com.Mgene==3)
   Note calculation of nr1 for (com.Mgene>=3 && com.fix_omega), as only the 
   w for the last partition is fixed.
*/
   int nr1=(com.nrate+1)/com.ngene, k=com.nrgene+(com.Mgene>=3)*igene*nr1;
   double *xcom=x+com.ntime, mr=0;

   if (_pi) {
      xtoy (com.piG[igene],com.pi,com.ncode);
#if(defined(CODEML))
      if(com.codonf==F1x4MG || com.codonf==F3x4MG)
         com.pf3x4 = com.f3x4[igene];
#endif
   }
   if (_UVRoot) {
      if (com.seqtype==CODONseq) {
         if(!com.fix_kappa) com.kappa=xcom[k++];
         if(!com.fix_omega) com.omega=xcom[k++];
         else
            com.omega = (com.Mgene>2&&igene<com.ngene-1?xcom[k++]:com.omega_fix);
         if (!com.NSsites)
            EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr,
               (com.hkyREV||com.codonf==FMutSel?&xcom[com.nrgene]:&com.kappa),com.omega,PMat);
      }
      else
         EigenQaa(NULL, Root, U, V, xcom+k);
   }
   if (_alpha) {
      com.alpha=xcom[com.nrgene+com.nrate+igene];
      DiscreteGamma (com.freqK, com.rK, com.alpha, com.alpha, com.ncatG, DGammaMean);
   }
   return (0);
}


int SetParametersNSsites (double x[])
{
/* for NSsites and NSbranchsite models including HMM, NSclade models
   p's are before w's in x[].
   w[2][3] holds omegas; w[i][j] for fore (i=0) or back (i=1) branches 
   in site class j.

   A & B: branch-site models:  (model=2, NSsites=2 or 3)

                       iclass
                    0    1    2    3
         back      w0   w1   w0   w1
         fore      w0   w1   w2   w2

   C & D: clade-site models:   (model=3, NSsites=2 or 3)  
   (D: nbtype = 2)

                       iclass
                    0    1    2
         b0        w0   w1   w2
         b1        w0   w1   w3
         b2        w0   w1   w4
         ......
*/
   int k0=com.ntime+com.nrgene+com.nkappa+com.npi, k=k0;
   int K=com.ncatG, i,j;
   double w[NBTYPE][3], t, S,dS,dN, spaceP2PI[NCATG*(NCATG+1)], small=1e-4;
   double mr, f;

   if(com.NSsites==0) error2("SetParametersNSsites : strange.");

   switch(com.NSsites) {
   case(NSnneutral):
      com.freqK[0] = x[k++];
      com.freqK[1] = 1-com.freqK[0]; 
      com.rK[0] = x[k++];
      com.rK[1] = 1; 
      break;
   case(NSpselection): 
   case(NSdiscrete):
      if(com.model == NSbranch2)   /* branch-site A&B (Y&N2002) */
         K = com.ncatG-1;
      if(com.nparK) {      /* HMM models, setting up p[] & w[] */
         for(j=0; j<K; j++)   /* w's for site classes */
            com.rK[j] = x[k++];
         for (i=0; i<K; i++, k+=K-1) {
            if (!LASTROUND) f_and_x(x+k,com.MK+i*K,K,0,0);   /* x->f */
            else            xtoy  (x+k,com.MK+i*K,K-1);
            com.MK[i*K+K-1] = 1-sum(com.MK+i*K,K-1);
         }
         PtoPi(com.MK, com.freqK, K, spaceP2PI);
         break;
      }

   /* *** Note: Falling through.  
      This sets up p[] for NSpselection, NSdiscrete, NSfreqs
   */
   case(NSfreqs): 
      if (!LASTROUND) {
         f_and_x(x+k,com.freqK,K,0,1);   /* x->f */
         k += K-1;
      }
      else {
         for(j=0,com.freqK[K-1]=1; j<K-1; j++) 
            com.freqK[K-1] -= (com.freqK[j] = x[k++]);
         if(com.freqK[K-1]<-small || com.freqK[K-1]>1+small) {
            matout(F0, com.freqK, 1, K);
            error2("freqK[]");
         }
      }

      /* setting up w[] */
      if(com.NSsites == NSfreqs) {
         if(com.ncatG!=5) error2("NSfreqs, ncatG?");
         com.rK[0] = 0;
         com.rK[1] = 1./3; 
         com.rK[2] = 2./3; 
         com.rK[3] = 1; 
         com.rK[4] = 3;
      }
      else if(com.NSsites == NSpselection) {
         com.rK[0] = x[k++];
         com.rK[1] = 1; 
         com.rK[2] = (com.fix_omega && com.model<=2 ? com.omega_fix : x[k++]);
      }
      else if(com.NSsites == NSdiscrete && com.aaDist == 0) {
         for(j=0; j<K; j++)
            com.rK[j] = x[k++];
      }
      if(com.model) {  /* branch-site and clade models */
         if(com.model == NSbranch2) { /* branch-site models */
            w[0][0] = w[1][0] = com.rK[0];  /* site class 0 */
            w[0][1] = w[1][1] = com.rK[1];  /* site class 1 */
            w[0][2] = -1;
            w[1][2] = com.rK[2];
         }
         else {                       /* clade models */
            k--;
            for(i=0; i<com.nbtype; i++) {
               for(j=0; j<K-1; j++) 
                  w[i][j] = com.rK[j];
               w[i][K-1] = (i==com.nbtype-1 && com.fix_omega ? com.omega_fix : x[k++]);
            }
         }
      }
      break;

   case(NSgamma):
   case(NS2gamma):
   case(NSbeta):
   case(NSbetaw): 
   case(NSbetagamma):
   case(NSbeta1gamma):
   case(NSbeta1normal):
   case(NS02normal):
   case(NS3normal):
      DiscreteNSsites(x+k);  break;
   }

   /* For NSsites models, calculates Qfactor_NS, to be used in EigenQcodon().
      For branch-site and clade models, calculate Qfactor_NS[] and also 
      UVRoot for different omega's.
   */
   k = k0;
   if(com.model == 0) {  /* NSsites models */
      for(j=0,Qfactor_NS=0; j<com.ncatG; j++) {
         if(com.aaDist) {
            if(com.aaDist<10)         com.pomega = x+k+com.ncatG-1+2*j;
            else if(com.aaDist >= FIT1) {
               com.pomega = x+k+com.ncatG-1+j*(4+(com.aaDist==FIT2));
               xtoy(pcodonClass+j*64, com.pi, com.ncode);
            }
         }
         mr = -1;
         EigenQcodon(1,-1,&S,&dS,&dN,NULL,NULL,NULL, &mr, com.pkappa, com.rK[j], PMat);
         Qfactor_NS += com.freqK[j]*mr;
      }
      Qfactor_NS = 1/Qfactor_NS;
   }
   else if (com.model == NSbranch2) { /* branch&site models */
      t = com.freqK[0] + com.freqK[1];
      com.freqK[2] = (1-t)*com.freqK[0]/t;
      com.freqK[3] = (1-t)*com.freqK[1]/t;
      /* calculates scale factors: background branches has two site classes
         while foreground branches has 3 site classes */

      for(i=0; i<2; i++) {  /* i=0 back (2 site classes); i=1 fore (3 classes) */
         Qfactor_NS_branch[i] = 0;
         for(j=0; j<(i==0?2:3); j++) {
            com.omega = w[i][j];
            f = com.freqK[j];
            if(i==0)       f = com.freqK[j]/t;
            else if(j==2)  f = 1-t;

            if(NFunCall==1) printf("branch=%d  freq=%.6f w%d = %.6f\n", i,f,j,com.omega);
            mr = -1;
            EigenQcodon(1,-1,&S,&dS,&dN,NULL,NULL,NULL, &mr, com.pkappa, com.omega, PMat);
            Qfactor_NS_branch[i] += f * mr;
         }
         Qfactor_NS_branch[i] = 1/Qfactor_NS_branch[i];
         if(NFunCall==1) printf("\t\t\tQfactor for branch %d = %.6f\n", i,Qfactor_NS_branch[i]);
      }
      /* calculates 3 sets of U&V&Root vectors (w0,w1,w2), for GetPMatBranch().  
         No EigenQcodon() calls are needed in ConditionalPNode() or minbranches().
      */
      for(i=0; i<3; i++) {  /* (w0,w1,w2) */
         if(NFunCall==1) printf("w[%d] = %.6f\n", i, w[1][i]);
         mr = 1;
         EigenQcodon(0,-1,NULL,NULL,NULL,_Root[i],_UU[i],_VV[i], &mr, com.pkappa,w[1][i],PMat);
      }
   }
   else { /* NSbranch3: Clade models C and D */
      /* calculates Qfactor_NS_branch[nbtype]: each branch has K=com.ncatG site classes */
      for(i=0; i<com.nbtype; i++) {
         Qfactor_NS_branch[i] = 0;
         for(j=0; j<K; j++) {
            mr = -1;
            EigenQcodon(1,-1,&S,&dS,&dN,NULL,NULL,NULL, &mr, com.pkappa,w[i][j],PMat);
            Qfactor_NS_branch[i] += com.freqK[j] * mr;
         }
         Qfactor_NS_branch[i] = 1/Qfactor_NS_branch[i];

         if(NFunCall==1) printf("\t\t\tQfactor for branch=%d  = %.6f\n", i,Qfactor_NS_branch[i]);
      }
      /* calculates K-1+nbtype sets of U&V&Root vectors (w0,w1,w2, w3,...), for GetPMatBranch().
      */
      for(i=0; i<K-1+com.nbtype; i++) {
         mr = 1;
         com.omega = (i < K-1 ? w[0][i] : w[i-K+1][K-1]);
         EigenQcodon(0,-1,NULL,NULL,NULL,_Root[i],_UU[i],_VV[i], &mr, com.pkappa,com.omega,PMat);
      }
   }
   return(0);
}


int Set_UVR_BranchSite (int iclass, int branchlabel)
{
/* There are 3 different w's in the branch-site models A & B, and nbtype+2 
   different w's in the clade models C & B, so there are the same number of 
   sets of U&V&Root.  This routine points out the right set.
*/
   int iUVR=0;

   if(com.model==0 || com.NSsites==0) error2("should not be here.");

   if(com.model<=NSbranch2) { /* branch-site models A & B */
      if(branchlabel==0) iUVR = iclass%2;                  /* back, w0 w1 */
      else               iUVR = (iclass<=1 ? iclass : 2);  /* fore, w0 w1 w2 */
   }
   else   {                   /* clade models C & D */
      if(iclass<com.ncatG-1) iUVR = iclass;
      else                   iUVR = com.ncatG-1 + branchlabel;
   }
   U = _UU[iUVR];
   V = _VV[iUVR];
   Root = _Root[iUVR];

   return (iUVR);
}


int GetCodonFreqs (void)
{
/* This is called by SetParameters() and calculates the expected base or codon frequencies 
   (com.pf3x4[] & com.pi[]) using the parameters under the model com.codonf.  
   This is used for models in which codon frequency parameters are estimated from 
   the data by ML.  Modified from GetCodonFreqs2().
   com.pi[] is modified.
   The routine does not work if com.ngene>1.
*/
   int n=com.ncode, i,j,k, ic,iaa,b[3];
   double *ppi=com.ppi, mutbias[20], y;

   if (com.codonf==Fcodon) {
      for(i=0; i<n; i++)
         com.pi[i] = (i==n-1 ? 1 : exp(com.ppi[i]));
      abyx (1./sum(com.pi,n), com.pi, n);
      return(0);
   }

   for(j=0;j<3;j++) {
      xtoy(ppi, com.pf3x4+j*4, 3);
      com.pf3x4[j*4+3] = 1;
      abyx (1./sum(com.pf3x4+j*4,4), com.pf3x4+j*4, 4);
      if(com.codonf==F3x4 || com.codonf==F3x4MG)
         ppi += 3;
   }
   if(com.codonf==FMutSel && com.npi==3)  return(0);

   if ((com.codonf>=F1x4 && com.codonf<=F3x4MG) || com.npi>3) {
      for (i=0; i<n; i++) {
         ic=FROM61[i];  b[0]=ic/16; b[1]=(ic/4)%4; b[2]=ic%4;
         com.pi[i] = com.pf3x4[b[0]]*com.pf3x4[4+b[1]]*com.pf3x4[8+b[2]];
      }
   }

   if (com.codonf==FMutSel && com.npi>3) {
      for(i=0; i<n-1; i++)  /* last codon has fitness 0 */
         com.pi[i] *= exp(com.ppi[3+i]);
   }
   else if (com.codonf==FMutSel0 && com.npi>3) {
      for(i=0; i<n; i++) {  /* last amino acid has fitness 0 */
         iaa = GeneticCode[com.icode][FROM61[i]];
         if(iaa<19) com.pi[i] *= exp(com.ppi[3+iaa]);
      }
      for(i=0,zero(com.piAA,20); i<n; i++)
         com.piAA[GeneticCode[com.icode][FROM61[i]]] += com.pi[i];
      abyx (1./sum(com.piAA,20), com.piAA, 20);
   }
   else if (com.codonf==FMutSel0 && com.npi==3) {
      for (i=0,zero(mutbias,20); i<n; i++) {
         ic=FROM61[i];  iaa = GeneticCode[com.icode][ic];
         b[0]=ic/16; b[1]=(ic/4)%4; b[2]=ic%4;
         mutbias[iaa] += com.pf3x4[b[0]]*com.pf3x4[b[1]]*com.pf3x4[b[2]];
      }
      for(i=0; i<n; i++) {
         ic=FROM61[i];  iaa = GeneticCode[com.icode][ic];
         b[0]=ic/16; b[1]=(ic/4)%4; b[2]=ic%4;
         y = com.pf3x4[b[0]]*com.pf3x4[b[1]]*com.pf3x4[b[2]];
         com.pi[i] = y/mutbias[iaa] * com.piAA[iaa];
      }
      y = sum(com.pi, n);
   }
   abyx (1./sum(com.pi,n), com.pi, n);
   return (0);
}


int SetParameters (double x[])
{
/* Set com. variables and initialize U, V, Root etc. before each calculation 
   of the likelihood function.
   Is it a good idea to restruct this and/or Getinitials into two parts,
   one for aa's and another for codons?
   When (com.NSsites==NS02normal || NS3normal), p's are before w's in x[]; 
   see CDFdN_dS().
*/
   int i,j,k, ik=0, nUVR=NBTYPE+2;
   double t,w0=-1, mr=0;

   if(com.clock>=5) return(0);
   if(com.fix_blength<2) SetBranch(x);
   if(com.np<=com.ntime) return(0);

   if(com.seqtype==1 || com.model==FromCodon || com.aaDist==AAClasses) {
      k = com.ntime+com.nrgene;
      if(com.hkyREV==0) {
         if(com.fix_kappa==1) { com.pkappa[0]=com.kappa; ik=1; }
         else                   com.kappa=x[k];
      }
      for(i=0; i<com.nkappa; i++) 
         com.pkappa[ik++] = x[k++];

      if(com.npi) {
         com.ppi = x+com.ntime+com.nrgene+com.nkappa;
         GetCodonFreqs ();
      }
      com.pomega = x+com.ntime+com.nrgene+com.nkappa+com.npi;
   }
   for(j=0;j<com.nrgene;j++) 
      com.rgene[j+1] = x[com.ntime+j];
   if(com.clock && AbsoluteRate) com.rgene[0] = x[0]; /* so that rgene are abs rates */

   if(com.seqtype==1 && com.aaDist>=FIT1) 
      getpcodonClass(x, pcodonClass);

   k=com.ntime+com.nrgene+com.nkappa+com.npi;

   if (com.nrate) {
      if(!com.model && !com.aaDist && !com.fix_omega && !com.NSsites) 
         com.omega=x[k];
      if(com.seqtype==AAseq)
         EigenQaa(NULL, Root, U, V, x+com.ntime+com.nrgene);
      else if(com.model==0 && com.NSsites==0 && com.Mgene<=1)
         EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr, com.pkappa, com.omega,PMat);
      else if((com.model==NSbranchB || com.model==NSbranch2) 
            && com.NSsites==0 && com.nbtype<=nUVR) {
         for(i=0; i<com.nbtype; i++) {
            if(com.aaDist == AAClasses)
               com.pomega = x+com.ntime+com.nrgene+com.nkappa+com.npi+i*com.nOmegaType;
            else
               w0 = (i==com.nOmega-1&&com.fix_omega?com.omega_fix:com.pomega[i]);
            EigenQcodon(0,-1,NULL,NULL,NULL,_Root[i],_UU[i],_VV[i], &mr, com.pkappa,w0,PMat);
         }
      }
      k = com.ntime+com.nrgene+com.nrate;
   }
   if (com.seqtype==CODONseq && com.NSsites)
      SetParametersNSsites(x);

   /* to force crash in case or error */
   /* 
   if(com.model) com.omega=-1;
   */

   /* branch models */
   if(com.seqtype==CODONseq && com.model && com.NSsites==0 && com.aaDist==0) {
      FOR(j,tree.nnode) {
         if (j==tree.root) continue;
         if (com.fix_omega && (int)nodes[j].label==com.nOmega-1)
            nodes[j].omega = com.omega_fix;
         else
            nodes[j].omega = com.pomega[(int)nodes[j].label];
      }
   }
   if (!com.fix_alpha && com.NSsites==0) {
      com.alpha=x[k++];
      if (com.fix_rho)
         DiscreteGamma(com.freqK,com.rK,com.alpha,com.alpha,com.ncatG,DGammaMean);
   }
   if (!com.fix_rho) {
      com.rho=x[k++];
      AutodGamma(com.MK, com.freqK, com.rK, &t, com.alpha, com.rho, com.ncatG);
   }
   return (0);
}


int DiscreteNSsites(double par[])
{
/* This discretizes the continuous distribution for dN/dS ratios among sites
   and calculates freqK[] and rK[], using the median method.
   par[] contains all paras in the w distribution.  par[0] is the 
   proportion of beta if (com.NSsites==betaw), or the proportion of w=0 if 
   (com.NSsites=NS02normal).
   This routine uses com.NSsites, com.ncatG, com.freqK, com.rK.
   betaw has com.ncatG-1 site classes in the beta distribution, and 02normal 
   has com.ncatG-1 site classes in the mixed normal distribution.
   See the function CDFdN_dS() for definitions of parameters.
*/
   int status=0, j,off, K=com.ncatG-(com.NSsites==NSbetaw || com.NSsites==NS02normal);
   double xb[2]={1e-7,99};  /* bounds for omega.  */
   int K1=6, K2=4, UseK1K2=0;
   double p01=0, p,w0, lnbeta;

   if(com.NSsites==NSbeta || com.NSsites==NSbetaw) xb[1]=1;

#ifdef NSSITES_K1_K2_CLASSES
   if((com.NSsites==NSgamma||com.NSsites==NS2gamma||com.NSsites>=NSbetagamma)){
      K2=max2(K2,K/3);  K1=K-K2;  UseK1K2=1;
      p01=CDFdN_dS(1.,par);

      /* printf("\nK:%3d%3d\t p01=%9.5f\n",K1,K2,p01); */
      FOR(j,K) {
         if(j<K1) { p=p01*(j*2.+1)/(2.*K1); w0=p; }
         else     { p=p01+(1-p01)*((j-K1)*2.+1)/(2.*K2); w0=1.01+(j-K1)/K2; }
         com.rK[j] = InverseCDF(CDFdN_dS,p,w0,par,xb);
         com.freqK[j] = (j<K1 ? p01/K1 : (1-p01)/K2); thread
      }
   }
#endif

   if(!UseK1K2) { /* this is currently used */
      if(com.NSsites==NSbeta || com.NSsites==NSbetaw) {
         off=(com.NSsites==NSbetaw);  /* par[0] is proportion for beta for M8 */
         lnbeta=LnGamma(par[off])+LnGamma(par[off+1])-LnGamma(par[off]+par[off+1]);
         for(j=0; j<K; j++) {
            p=(j*2.+1)/(2.*K);
            com.rK[j] = QuantileBeta(p, par[off], par[off+1], lnbeta);
         }
      }
      else {
         FOR(j,K) {
            p = (j*2.+1)/(2.*K);
            w0 = .01+j/K; if(com.rK[j]) w0=(w0+com.rK[j])/2;
            com.rK[j] = Quantile(CDFdN_dS,p,w0,par,xb);
         }
      }
      FOR(j,K) com.freqK[j]=1./K;
   }

   if(com.NSsites==NSbetaw) {
      if(!com.fix_omega) com.rK[com.ncatG-1]=par[3];
      else               com.rK[com.ncatG-1]=com.omega_fix;
      com.freqK[K]=1-par[0]; FOR(j,K) com.freqK[j]*=par[0];
   }
   if(com.NSsites==NS02normal) {
      for(j=K-1;j>=0;j--) /* shift to right by 1 to make room for spike at 0*/
         { com.rK[j+1]=com.rK[j]; com.freqK[j+1]=com.freqK[j];  }
      com.rK[0]=0;  com.freqK[0]=par[0];
      for(j=1;j<K+1;j++) com.freqK[j]*=(1-par[0]);
   }

   if(com.NSsites>=NSgamma){
      if(!status && com.NSsites==NSbeta) 
         for(j=1;j<com.ncatG;j++) if(com.rK[j]+1e-7<com.rK[j-1]) status=1;

      if(status) {
         printf("\nwarning: DiscreteNSsites\nparameters: ");
         FOR(j,(com.NSsites==7?2:4)) printf(" %12.6f", par[j]);  FPN(F0);
         FOR(j,com.ncatG)            printf("%13.5f", com.freqK[j]);  FPN(F0);
         FOR(j,com.ncatG)            printf("%13.5e", com.rK[j]);  FPN(F0);
      }
   }
   return(0);
}


double CDFdN_dS(double x,double p[])
{
/* This calculates the CDF of the continuous dN/dS distribution over sites, 
   to be used as argument to the routine Quantile().  When the distribution
   has spikes, the spikes are ignored in this routine, and the scaling
   is done outside this routine, for example, in DiscreteNSsites().
   All parameters (par) for the w distribution are passed to this routine, 
   although some (p0 for the spike at 0) are not used in this routine.  
   Parameters are arranged in the following order:

      NSgamma (2):       alpha, beta
      NS2gamma (4):      p0, alpha1, beta1, alpha2 (=beta2)
      NSbeta (2):        p_beta, q_beta
      NSbetaw (4):       p0, p_beta, q_beta, w (if !com.fix_omega, not used here)
      NSbetagamma (5):   p0, p_beta, q_beta, alpha, beta
      NSbeta1gamma (5):  p0, p_beta, q_beta, alpha, beta (1+gamma)
      NSbeta1normal (5): p0, p_beta, q_beta, mu, s (normal>1)
      NS02normal (5):    p0, p1, mu2, s1, s2 (s are sigma's)
      NS3normal (6):     p0, p1, mu2, s0, s1, s2 (s are sigma's)

   Parameters p0 & p1 are transformed if (!LASTROUND)

*/
   double cdf=-1;
   double z, f[3],mu[3]={0,1,2},sig[3]; /* 3normal: mu0=0 fixed. mu2 estimated */

   switch(com.NSsites) {
   case(NSgamma):  cdf=CDFGamma(x,p[0],p[1]);   break;
   case(NS2gamma): 
      cdf=p[0] *CDFGamma(x,p[1],p[2])+(1-p[0])*CDFGamma(x,p[3],p[3]);  break;
   case(NSbeta):   cdf=CDFBeta(x,p[0],p[1],0);  break;
   case(NSbetaw):  cdf=CDFBeta(x,p[1],p[2],0);  break;
   case(NSbetagamma):
      cdf=p[0]*CDFBeta(x,p[1],p[2],0)+(1-p[0])*CDFGamma(x,p[3],p[4]);  break;

   case(NSbeta1gamma):
      if(x<=1) cdf=p[0]*CDFBeta(x,p[1],p[2],0);
      else     cdf=p[0]+(1-p[0])*CDFGamma(x-1,p[3],p[4]);
      break;
   case(NSbeta1normal):
      if(x<=1) cdf=p[0]*CDFBeta(x,p[1],p[2],0);
      else {
         cdf=CDFNormal((p[3]-1)/p[4]);
         if(cdf<1e-9) {
            matout(F0,p,1,5);;
            printf("PHI(%.6f)=%.6f\n",(p[3]-1)/p[4],cdf);  getchar();
         }
         cdf=p[0]+(1-p[0])*(1- CDFNormal((p[3]-x)/p[4])/cdf);
      }
      break;
   case(NS02normal):
      mu[2]=p[2]; sig[1]=p[3]; sig[2]=p[4];
      f[1]=p[1];  f[2]=1-f[1];
      cdf = 1 - f[1]* CDFNormal(-(x-mu[1])/sig[1])/CDFNormal(mu[1]/sig[1])
              - f[2]* CDFNormal(-(x-mu[2])/sig[2])/CDFNormal(mu[2]/sig[2]);
      break;
   case(NS3normal):
      mu[2]=p[2]; sig[0]=p[3]; sig[1]=p[4]; sig[2]=p[5];

      if(LASTROUND) { f[0]=p[0]; f[1]=p[1]; }
      else          { z=(f[0]=exp(p[0]))+(f[1]=exp(p[1]))+1; f[0]/=z; f[1]/=z;}
      f[2]=1-f[0]-f[1];
      cdf = 1 - f[0]* 2*CDFNormal(-x/sig[0])
              - f[1]* CDFNormal(-(x-mu[1])/sig[1])/CDFNormal(mu[1]/sig[1])
              - f[2]* CDFNormal(-(x-mu[2])/sig[2])/CDFNormal(mu[2]/sig[2]);
      break;
   }
   return(cdf);
}


void GetSNphysical(double pi[], double *Sphysical, double *Nphysical, double *S4)
{
/* this calculates the synonymous and nonsynonymous sites according to the 
   physical-site definition (Yang 2006 Computational Molecular Evolution, Section 2.5.4).
   S and N are sites per codon.
   It is not clear how to deal with stop codons.
*/
   int i,j,k, ic,b[3], aa0,aa1, *code=GeneticCode[com.icode];
   int by[3]={16,4,1}, nstop,s,n;
   double y;

   for(i=0,*Sphysical=*Nphysical=*S4=0; i<com.ncode; i++) {
      ic=FROM61[i]; b[0]=ic/16; b[1]=(ic/4)%4; b[2]=ic%4;
      /* no need to check the first and second positions here */
      if(FourFold[b[0]][b[1]]) *S4 += pi[i];
      aa0=code[ic];

      for(j=0,s=n=nstop=0; j<3; j++) FOR(k,3) {
         aa1 = code[ic + ((b[j]+k+1)%4 - b[j])*by[j]];
         if(aa1==-1)        nstop++;
         else if(aa0==aa1)  s++;
         else               n++;
      }
      /* s + n ~= 9 */
      *Sphysical += pi[i]*s/9.*3.;
      *Nphysical += pi[i]*n/9.*3.;
   }
   y = (*Sphysical + *Nphysical)/3;
   *Sphysical /= y;  *Nphysical /= y;
}


double GetOmega (int aa1, int aa2, double omega, double pomega[])
{
/* this gets the omega (w) value under different models for EigenQcodon().
*/
   double w=1, fit1,fit2;
   int k;

   if (com.aaDist==AAClasses) {
      if (aa1<aa2)  { k=aa2; aa2=aa1; aa1=k; }
      k=aa1*(aa1-1)/2+aa2;
      if (pomega[OmegaAA[k]]<0) {
         if (noisy)  printf("aa1 & aa2 & iw & w: %d %d %d %.5f\n", 
                        aa1,aa2,OmegaAA[k],pomega[OmegaAA[k]]);
         pomega[OmegaAA[k]]=0;
      }
      if (com.seqtype==AAseq && com.nrate>65 && aa1*20+aa2==ijAAref)
          ;     /* if estimating grantham's matrix with aa sequences */
      else  w = pomega[OmegaAA[k]];
   }
   else if (com.aaDist==0)  w = omega; /* NSsites==0 or >0 */
   else if (com.aaDist<=6)  {          /* chemical properties: a & b */
      w = pomega[0]*com.daa[aa1*20+aa2];
      if(com.aaDist>0)           w = exp(-w);  /* geometric */
      else                       w = 1-w;      /* linear */
      if (com.seqtype==CODONseq) w *= pomega[1];
   }
   else if (com.aaDist>=FIT1) {   /* ap,p*,av,v* (and w0 for FIT2) */
      fit1 = -pomega[0]*square(AAchem[0][aa1]-pomega[1])
             -pomega[2]*square(AAchem[1][aa1]-pomega[3]);
      fit2 = -pomega[0]*square(AAchem[0][aa2]-pomega[1])
             -pomega[2]*square(AAchem[1][aa2]-pomega[3]);

      w = exp(-fit1-fit2);
      if(com.aaDist==FIT2) w *= pomega[4];
   }

   return(w);
}


double GetMutationMultiplier (int i, int j, int pos, int from[3], int to[3])
{
/* This sets the mutation-bias multipliers for F1x4MG, F3x4MG, FMutSel0, FMutSel.
   com.pi[], com.pf3x4[], and com.piAA[] are set correctly before this routine is called.
*/
   int n=com.ncode, b1,b2;
   double q, eFit1, eFit2, small=min2(1e-6, 1./com.ls);

   /* b1 and b2 are the 2 unchanged positions */
   if     (pos==0) { b1=1; b2=2; }
   else if(pos==1) { b1=2; b2=0; }
   else            { b1=0; b2=1; }   
   q = 1 / (com.pf3x4[b1*4+to[b1]] * com.pf3x4[b2*4+to[b2]]);

   if(com.npi && (com.codonf==FMutSel || com.codonf==FMutSel0)) {
      eFit1 = max2(com.pi[i], small);
      eFit2 = max2(com.pi[j], small);

      eFit1 /= com.pf3x4[from[0]] * com.pf3x4[from[1]] * com.pf3x4[from[2]];
      eFit2 /= com.pf3x4[  to[0]] * com.pf3x4[  to[1]] * com.pf3x4[to[2]];

      if(fabs(eFit2-eFit1)>1e-10)
         q *= (log(eFit2)-log(eFit1))/(eFit2-eFit1);
      else
         q /= eFit2;
   }
   return(q);
}


int SelectionCoefficients (FILE* fout, double kappa[], double ppi[], double omega)
{
/* This calculates the distribution of S or 2Ns under the FMutSel or FMutSel0 models.
   Qsubw[] is not correct if (com.NSsites) and the results are not printed.
*/
   int n=Nsensecodon, i,j,k, ic1,ic2,b1,b2;
   int ndiff,pos=0,from[3],to[3];
   double q, summut=0, summutp=0, sumsub=0, sumsubw=0, eF1,eF2, fb[4];
   double bigS=2, sumbadmut=0,sumgoodmut=0;
   double Qmut[NCODE*NCODE], Qsub[NCODE*NCODE], Qsubw[NCODE*NCODE], Ns[NCODE*NCODE], mNs=0,mNsp=0,mNsn=0;
   double maxNs=0, fNsMut[50]={0}, fNsSub[50]={0}, fNsSubw[50]={0}, small=min2(1e-6, 1./com.ls);
   int ncat=21;

   if(com.codonf<FMutSel0)
      error2("codonf incorrect");

   fprintf(fout, "\nI\tJ\tij\t2Ns_IJ\tpMut_IJ\tpSub_IJ\t2Ns_JI\tpMut_JI\tpSub_JI\n\n");
   fb[0]=ppi[0]; fb[1]=ppi[1]; fb[2]=ppi[2]; fb[3]=1;
   for (i=0;i<n*n;i++) Qmut[i]=Qsub[i]=Qsubw[i]=0;
   for (i=1; i<n; i++) {
      ic1=FROM61[i]; from[0]=ic1/16; from[1]=(ic1/4)%4; from[2]=ic1%4;
      for(j=0; j<i; j++) {
         ic2=FROM61[j]; to[0]=ic2/16; to[1]=(ic2/4)%4; to[2]=ic2%4;
         for(k=0,ndiff=0; k<3; k++)
            if(from[k]!=to[k]) { ndiff++; pos=k; }
         if(ndiff!=1)  continue;
         q = 1;
         if(com.hkyREV) { /* REV-GTR model */
            b1 = min2(from[pos],to[pos]); /* b1 and b2 are changed nucleotides */
            b2 = max2(from[pos],to[pos]);
            if      (b1==0 && b2==1)  q = kappa[0]; /* TC or CT, relative to AG */
            else if (b1==0 && b2==2)  q = kappa[1]; /* TA or AT */
            else if (b1==0 && b2==3)  q = kappa[2]; /* TG or GT */
            else if (b1==1 && b2==2)  q = kappa[3]; /* CA or AC */
            else if (b1==1 && b2==3)  q = kappa[4]; /* CG or GC */
         }
         else {           /* HKY model */
            if(from[pos]+to[pos]==1 || from[pos]+to[pos]==5)
               q = kappa[0];
         }

         eF1 = max2(com.pi[i], small) / (fb[from[0]] * fb[from[1]] * fb[from[2]]);
         eF2 = max2(com.pi[j], small) / (fb[  to[0]] * fb[  to[1]] * fb[to[2]]);

         Ns[i*n+j] = log(eF2/eF1);
         Ns[j*n+i] = -Ns[i*n+j];

         if(maxNs < fabs(Ns[i*n+j])) maxNs = fabs(Ns[i*n+j]);
         
         Qmut[i*n+j] = Qsub[i*n+j] = com.pi[i] * q * fb[  to[pos]];
         Qmut[j*n+i] = Qsub[j*n+i] = com.pi[j] * q * fb[from[pos]];

         if(fabs(Ns[i*n+j]) > 1e-20) {  /* non-neutral mutations */
            Qsub[i*n+j] *= Ns[i*n+j]/(1 - exp(-Ns[i*n+j]));
            Qsub[j*n+i] *= Ns[j*n+i]/(1 - exp(-Ns[j*n+i]));
         }
         Qsubw[i*n+j] = Qsub[i*n+j];
         Qsubw[j*n+i] = Qsub[j*n+i];
         if(!com.NSsites && GeneticCode[com.icode][ic1] != GeneticCode[com.icode][ic2]) {
            Qsubw[i*n+j] *= com.omega;
            Qsubw[j*n+i] *= com.omega;
         }

         summut  += Qmut[i*n+j] + Qmut[j*n+i];
         sumsub  += Qsub[i*n+j] + Qsub[j*n+i];
         sumsubw += Qsubw[i*n+j] + Qsubw[j*n+i];

         if(fabs(Ns[i*n+j]) > 1e-20) {  /* non-neutral mutations */
            summutp += (Ns[i*n+j]>0 ? Qmut[i*n+j] : Qmut[j*n+i]);
            mNsp += (Ns[i*n+j]>0 ? Qmut[i*n+j]*Ns[i*n+j] : Qmut[j*n+i]*Ns[j*n+i]);
            mNsn += (Ns[i*n+j]<0 ? Qmut[i*n+j]*Ns[i*n+j] : Qmut[j*n+i]*Ns[j*n+i]);
         }
         else {  /* neutral mutation.  Ns = 0 makes no contribution to mNsp & mNsn */
            summutp += (Qmut[i*n+j] + Qmut[j*n+i])/2;
         }
         mNs  += (Qmut[i*n+j]+Qmut[j*n+i])*fabs(Ns[i*n+j]);

         if (fabs(Ns[i*n+j])>bigS) {
            if (Ns[i*n+j]>0) {
               sumgoodmut += Qmut[i*n+j];
               sumbadmut  += Qmut[j*n+i];
            }
            else {
               sumgoodmut += Qmut[j*n+i];
               sumbadmut  += Qmut[i*n+j];
            }
         }

         fprintf(fout, "%c%c%c\t", BASEs[from[0]],BASEs[from[1]],BASEs[from[2]]);
         fprintf(fout, "%c%c%c\t", BASEs[  to[0]],BASEs[  to[1]],BASEs[  to[2]]);
         fprintf(fout, "%c%c", BASEs[from[pos]],BASEs[to[pos]]);
         fprintf(fout, "\t%.5f\t%.5f\t%.5f", Ns[i*n+j], Qmut[i*n+j], Qsub[i*n+j]);
         fprintf(fout, "\t%.5f\t%.5f\t%.5f", Ns[j*n+i], Qmut[j*n+i], Qsub[j*n+i]);

         if(!com.NSsites)
            fprintf(fout, "\t%.5f\t%.5f", Qsubw[i*n+j], Qsubw[j*n+i]);

         FPN(fout);

      } /* for (j) */
   }    /* for (i) */

   sumgoodmut /= summut;
   sumbadmut /= summut;
   mNs /= summut;
   mNsp /= summutp;
   mNsn /= summut-summutp;

   fprintf(fout, "\n\nHistograms\n2Ns\tFMut\tFSub(CodonUsage)\tFSubw(after w)\n\n");

   for(i=0; i<n; i++) {
      for(j=0; j<n; j++) {
         if(Qmut[i*n+j] == 0) continue;
         for(k=0; k<ncat-1; k++)  {
            if(Ns[i*n+j] < (-1 + (k+1.)*2/ncat)*maxNs) break;
         }
         fNsMut[k]  += Qmut[i*n+j]/summut;
         fNsSub[k]  += Qsub[i*n+j]/sumsub;
         fNsSubw[k] += Qsubw[i*n+j]/sumsubw;
      }
   }
   for(k=0; k<ncat; k++) {
      fprintf(fout, "%.5f\t%.5f\t%.5f", (-1 + (k+0.5)*2/ncat)*maxNs, fNsMut[k], fNsSub[k]);
      if(!com.NSsites) 
         fprintf(fout, "\t%.5f", fNsSubw[k]);
      FPN(fout);
   }

   fprintf(fout, "\nProportion of advantageous (S > 0) mutations:\n %.5f\n", summutp/summut);
   fprintf(fout, "\nProportions of good & bad mutations (|S| > %.4f) among mutations:\n%.5f  %.5f\n", 
      bigS, sumgoodmut, sumbadmut);
   fprintf(fout, "\nmean |Ns| = %.5f\tmean Ns+ = %.5f\tmean Ns- = %.5f\n", mNs,mNsp,mNsn);

   fprintf(frst1, "\t%.4f\t%.4f\t%.4f", mNs, mNsp, mNsn);
        
   return(0);
}


int EigenQcodon (int getstats, double blength, double *S, double *dS, double *dN,
    double Root[], double U[], double V[], double *meanrate, double kappa[], double omega, double Q[])
{
/* This contructs the rate matrix Q for codon substitution and gets the eigen
   values and vectors if getstats==0, or get statistics (dS & dN etc.) if 
   getstats==1.
   The routine is also called by Qcodon2aa for mechanistic amino acid 
   substitution models.
   Input parameters are kappa, omega and com.pi (or com.fb61).

   Statistics calculated include S, dS & dN.
   c0[0,1,2] and c[0,1,2] are rates for the 3 codon positions before and after 
   selection.  c4 is for 4-fold rates.  ts[3] and tv[3] are transition/
   transversion rates for the three codon positions, not calculated.

   *Qfactor or *meanrate:
      =0 means that Q is scaled as usual;
      <0 means that the scale factor will be calculated and returned 
      >0 the given scale factor is applied (1 means no scaling).
   
   Note that under NSsites or branch&site models, scaling is done for all Q
   matrices for the whole branch.

   aaDist=FIT1 & FIT2:  ap,p*,av,v*, (and w0 for FIT2)
   The argument omega is used only if the model assumes one omega.  For 
   AAClasses, com.pomega is used instead.
*/
   int n=Nsensecodon, i,j,k, ic1,ic2,aa1,aa2, b1,b2;
   int ndiff,pos=0,from[3],to[3];
   double q, mr, rs0,ra0,rs,ra, y;
   double Sphysical, Nphysical, S4, dSnew, dNnew;
   double d4=0, d0[3], d[3], ts[3], tv[3];  /* rates at positions and 4-fold sites */
   double *pi=(com.seqtype==AAseq?com.fb61:com.pi), w=-1, piQij;
   double space[NCODE*(NCODE+1)];

/* Delete this after the MutSel project. */
   static int times=0;
   if(!getstats) times=0;
   else times++;

   NEigenQ++;
   if(blength>=0 && (S==NULL||dS==NULL||dN==NULL)) error2("EigenQcodon");
   for (i=0;i<n*n;i++) Q[i]=0;
   for (i=1; i<n; i++) {
      ic1=FROM61[i]; from[0]=ic1/16; from[1]=(ic1/4)%4; from[2]=ic1%4;
      for(j=0; j<i; j++) {

         ic2=FROM61[j]; to[0]=ic2/16; to[1]=(ic2/4)%4; to[2]=ic2%4;
         for(k=0,ndiff=0; k<3; k++)
            if(from[k]!=to[k]) { ndiff++; pos=k; }
         if(ndiff!=1)  continue;
         q = 1;
         if(com.hkyREV) { /* REV-GTR model */
            b1 = min2(from[pos],to[pos]); /* b1 and b2 are changed nucleotides */
            b2 = max2(from[pos],to[pos]);
            if      (b1==0 && b2==1)  q = kappa[0]; /* TC or CT, relative to AG */
            else if (b1==0 && b2==2)  q = kappa[1]; /* TA or AT */
            else if (b1==0 && b2==3)  q = kappa[2]; /* TG or GT */
            else if (b1==1 && b2==2)  q = kappa[3]; /* CA or AC */
            else if (b1==1 && b2==3)  q = kappa[4]; /* CG or GC */
         }
         else {            /* HKY model */
            if(from[pos]+to[pos]==1 || from[pos]+to[pos]==5)
               q = kappa[0];
         }
         if (com.codonf>=F1x4MG && com.codonf<=FMutSel && com.codonf!=Fcodon)
            q *= GetMutationMultiplier (i, j, pos, from, to);

         aa1 = GeneticCode[com.icode][ic1];  
         aa2 = GeneticCode[com.icode][ic2];
         if(aa1 != aa2)
            q *= GetOmega(aa1, aa2, omega, com.pomega);
         Q[i*n+j] = q*pi[j];
         Q[j*n+i] = q*pi[i];

      } /* for (j) */
   }    /* for (i) */

   for (i=0; i<n; i++)
      Q[i*n+i] = -sum(Q+i*n,n);
   for (i=0,mr=0; i<n; i++)
      mr -= pi[i]*Q[i*n+i];

   if(getstats==0) {  /* get Root, U, & V */
      if (com.seqtype==AAseq) return (0);
      eigenQREV(Q, pi, n, Root, U, V, space);
      if(*meanrate>= 0) {    /* apply scaling if meanrate>0 */
         if(*meanrate>0)
            mr = *meanrate;
         for (i=0; i<n; i++) 
            Root[i] /= mr;
      }
   }
   else {
      for(i=0;i<3;i++) d[i] = d0[i] = ts[i] = tv[i]=0;
      rs0 = ra0 = rs = ra = 0;
      for (i=0; i<n; i++) {
         ic1=FROM61[i]; from[0]=ic1/16; from[1]=(ic1/4)%4; from[2]=ic1%4;
         for(j=0; j<n; j++) {
            if(i==j || Q[i*n+j]==0) continue;
            ic2=FROM61[j]; to[0]=ic2/16; to[1]=(ic2/4)%4; to[2]=ic2%4;
            aa1 = GeneticCode[com.icode][ic1];  
            aa2 = GeneticCode[com.icode][ic2];
            for(k=0,ndiff=0; k<3; k++)
               if(from[k] != to[k]) { ndiff++; pos=k; }
            if(ndiff!=1) error2("jgl");

            piQij = pi[i]*Q[i*n+j];
            if(pos==2 && FourFold[to[0]][to[1]]) 
               d4 += piQij;

            if(aa1==aa2) {
               rs += piQij;
               d0[pos] += piQij;
            }
            else {
               ra += piQij;
               w = GetOmega(aa1, aa2, omega, com.pomega);
               ra0 += piQij/w;
               d0[pos] += piQij/w;
            }
            d[pos] += piQij;
         } /* for (j) */
      }    /* for (i) */

      if(fabs(mr-(rs+ra)) > 1e-6) 
         error2("mr should be = rs+ra");

      rs0 = rs;
      w = (rs0+ra0);  rs0 /= w;  ra0 /= w;   *S = rs0*3*com.ls;
      if(com.NSsites==0 && blength>=0) {  /* calculates dS & dN */
         if(blength==0) *dS = *dN = 0;
         rs /= mr;
         ra /= mr;
         *dS = blength*rs/(3*rs0);
         *dN = blength*ra/(3*ra0);
         w = (*dS>0 ? *dN/ *dS : -1);
         GetSNphysical(com.pi, &Sphysical, &Nphysical, &S4);
         for(i=0;i<3;i++) {
            d[i]  *= blength/mr;
            d0[i] *= blength/mr;
         }
         d4 *= blength/mr/S4;
         dNnew = blength*ra/Nphysical;
         dSnew = blength*rs/Sphysical;

         if(noisy>=9) {
            printf("\nd123[*] =%9.5f%9.5f%9.5f  average%9.5f\n", d[0],d[1],d[2], (d[0]+d[1]+d[2])/3);
            printf(  "    [B] =%9.5f%9.5f%9.5f  average%9.5f\n", d0[0],d0[1],d0[2], (d0[0]+d0[1]+d0[2])/3);
            printf("accept  =%9.5f%9.5f%9.5f\n\n", d[0]/d0[0],d[1]/d0[1],d[2]/d0[2]);
            printf("w =%9.5f dN =%9.5f dS =%9.5f d4 =%9.5f (%.1f four-fold sites)\n", w, *dN,*dS, d4, S4*com.ls);
            printf("%12s dN*=%9.5f dS*=%9.5f S* =%7.2f N* =%7.2f\n", "", dNnew, dSnew, Sphysical*com.ls, Nphysical*com.ls);
         }

         /* print out dN* dS* d4 d3B */
         if(com.verbose && times==1 && com.ns==2)
            fprintf(frst1, "\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f", 
                           *dN*2, *dS*2, dNnew*2, dSnew*2, d0[2]*2, d4*2);
      }
      else if (com.NSsites) {
         *dS = rs/(rs0*3);
         *dN = ra/(ra0*3);
      }
   }

   if(*meanrate<0) *meanrate = mr;
   return(0);
}


int EigenQaa (FILE *fout, double Root[], double U[], double V[], double rate[])
{
/*  Codon-based AA model must use FromCodon, even if com.aaDist==AAClasses.
*/
   int naa=20, i,j,k;
   double Q[20*20], mr=0, t=0;
   double space[NCODE*NCODE*2+NCODE],*Qc=space+NCODE*NCODE, *space_pisqrt=Qc+NCODE*NCODE;
   char aa3[4]="", AAratefile[96]="AAratefile.dat";
   FILE *fAArate;

   for(i=0; i<naa*naa; i++) Q[i]=0;
   switch (com.model) {
   case (Poisson)   : case (EqualInput) : 
      fillxc (Q, 1., naa*naa);  break;
   case (Empirical) : case (Empirical_F):
      for(i=0; i<naa; i++) for(j=0; j<i; j++)
         Q[i*naa+j]=Q[j*naa+i]=com.daa[i*naa+j];
      break;
   case (FromCodon):
      EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr,
         (com.hkyREV||com.codonf==FMutSel?rate:&com.kappa),com.omega,Qc);
      Qcodon2aa(Qc, com.fb61, Q, space);
      break;
   case (REVaa_0)  :
      for (i=1,k=0; i<naa; i++) for (j=0; j<i; j++)
         if (AA1STEP[i*(i-1)/2+j] && i*naa+j!=ijAAref)
            Q[i*naa+j]=Q[j*naa+i]=rate[k++];
      k=ijAAref;  Q[(k/naa)*naa+k%naa]=Q[(k%naa)*naa+k/naa]=1;
      break;
   case (REVaa)  : 
      for (i=0,k=0; i<naa; i++) for (j=0; j<i; j++)
         if (i*naa+j!=ijAAref) Q[i*naa+j]=Q[j*naa+i]=rate[k++];
      Q[ijAAref]=Q[(ijAAref%naa)*naa+(ijAAref/naa)]=1; 
      break;
   }
   for(i=0; i<naa; i++) for(j=0; j<naa; j++)
      Q[i*naa+j] *= com.pi[j];
   for (i=0,mr=0; i<naa; i++) {
      Q[i*naa+i] = 0;
      Q[i*naa+i] = -sum(Q+i*naa,naa);
      mr -= com.pi[i]*Q[i*naa+i]; 
   }

   if (fout && com.model>=REVaa_0) {
      printf("\nAA substitution rate matrix printed into %s\n", AAratefile);
      fAArate=(FILE*)gfopen(AAratefile,"w");
      fprintf (fout, "\n\nRate matrix (symmetrical part, Sij)\n");
      for(i=0,t=0;i<naa;i++) {
         if(com.pi[i]==0) error2("EigenQaa: do this now");
         for(j=0; j<i; j++)
            t += Q[i*naa+j]/com.pi[j]/(naa*(naa-1)/2.);
      }
      for(i=0; i<naa; i++) {
         fprintf (fout, "\n%-5s", getAAstr(aa3,i));
         for(j=0; j<i; j++) fprintf(fout, " %4.0f", Q[i*naa+j]/t/com.pi[j]*100);
         for(j=0; j<i; j++) fprintf(fAArate, " %5.1f", Q[i*naa+j]/t/com.pi[j]*100); 
         FPN(fAArate);
      }
      fputs("\n     ",fout);  
      for(i=0; i<naa; i++)
         fprintf(fout,"%5s", getAAstr(aa3,i));  
      FPN(fout);  
      fflush(fout);
      matout(fAArate, com.pi, 1, naa);
      for(i=0; i<naa; i++)
         fprintf(fAArate,"%12s", getAAstr(aa3,i));
      FPN(fAArate);  
      fprintf(fAArate,"\n\nNote: Amino acid rate matrix estimated from %s\n", com.seqf);
      fclose(fAArate);
   }

   if (fout && frst1 && com.model>=REVaa_0) {
      fprintf(frst1, "\nRate matrix (symmetrical part, Sij) for bubble plot\n");
      for(i=0; i<naa; i++)  for(j=0; j<i; j++) 
         fprintf(frst1, "\t%d\t%d\t%.2f\n", i+1,j+1,Q[i*naa+j]/t/com.pi[j]*100);
   }

   eigenQREV(Q, com.pi, naa, Root, U, V, space_pisqrt);
   for(i=0; i<naa; i++)
      Root[i] = Root[i]/mr;
   return (0);
}


int Qcodon2aa (double Qc[], double pic[], double Qaa[], double piaa[])
{
/* Qc -> Qaa

   This routine constructs the rate matrix for amino acid replacement from
   the rate matrix for codon substitution, by congregating states in the
   Markov chain.  Both processes are time reversible, and only the
   symmetrical part of the rate matrix are constructed.  Codon frequencies 
   pic[] are used.  They are constructed by assigning equal frequencies for 
   synonymous codons in the routine AA2Codonf().
   Qaa(aai,aaj) = SUMi SUMj (piC[i]*piC[j]]*Qc[i][j]) / (piAA[i]*piAA[j])
*/
   int i, j, aai, aaj, nc=Nsensecodon, naa=20;
   double ti, tij;

   zero(piaa,naa);
   zero(Qaa,naa*naa);
   for(i=0; i<nc; i++)
      piaa[GeneticCode[com.icode][FROM61[i]]] += pic[i];
   for(i=0; i<nc; i++) {
      aai = GeneticCode[com.icode][FROM61[i]];
      if(piaa[aai]==0)   ti = 0;
      else               ti = pic[i]/piaa[aai];
      for(j=0; j<i; j++) {
         aaj = GeneticCode[com.icode][FROM61[j]];
         if (Qc[i*nc+j]==0 || aai==aaj) continue;
         if(piaa[aaj]==0) 
            tij = 0;
         else
            tij = ti*pic[j]*Qc[i*nc+j]/piaa[aaj];
         Qaa[aai*naa+aaj] += tij;
         Qaa[aaj*naa+aai] += tij;
      }
   }

   return (0);
}



int ConditionalPNode (int inode, int igene, double x[])
{
   int n=com.ncode, i,j,k,h, ison, pos0=com.posG[igene], pos1=com.posG[igene+1];
   double t;

   FOR(i,nodes[inode].nson)
      if(nodes[nodes[inode].sons[i]].nson>0 && !com.oldconP[nodes[inode].sons[i]])
         ConditionalPNode(nodes[inode].sons[i], igene, x);

   if(inode<com.ns)
      for(h=pos0*n; h<pos1*n; h++) nodes[inode].conP[h]=0; /* young ancestor */
   else
      for(h=pos0*n; h<pos1*n; h++) nodes[inode].conP[h]=1;
   if (com.cleandata && inode<com.ns)
      for(h=pos0;h<pos1;h++) nodes[inode].conP[h*n+com.z[inode][h]]=1;

   for (i=0; i<nodes[inode].nson; i++) {
      ison = nodes[inode].sons[i];
      t = nodes[ison].branch * _rateSite;
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
      else {                                            /* internal node */
         for(h=pos0; h<pos1; h++)
            for(j=0; j<n; j++) {
               for(k=0,t=0; k<n; k++)
                  t += PMat[j*n+k]*nodes[ison].conP[h*n+k];
               nodes[inode].conP[h*n+j] *= t;
            }
      }

   }        /*  for (ison)  */
   if(com.NnodeScale && com.nodeScale[inode]) 
      NodeScale(inode, pos0, pos1);

   return (0);
}




int PMatJC69like (double P[], double t, int n)
{
   int i;
   double pii=1./n+(1.-1./n)*exp(-n/(n-1.)*t), pij=(1.-pii)/(n-1.);
   for(i=0; i<n*n; i++) P[i] = pij;
   for(i=0; i<n; i++)   P[i*n+i] = pii;
   return (0);
}




double Fcodon_3x4 (double fcodon[], double fb3x4[]);
void OutFb3x4(FILE*fout, double fb3x4[]);
void CountCodons (FILE *fout,double fcodonsg[],double fb3x4sg[],double fb4g[]);

double Fcodon_3x4(double fcodon[], double fb3x4[])
{
/* this converts the codon frequencies into a fb3x4 table. fcodon has 64 codons.
*/
   int b[3], k,j, nc=64, status=0;
   double t;

   zero(fb3x4,12);
   for(k=0; k<nc; k++) {
      b[0]=k/16; b[1]=(k%16)/4; b[2]=k%4;
      for(j=0; j<3; j++)
         fb3x4[j*4+b[j]]+=fcodon[k];
   }
   for(j=0; j<3; j++) {
      t=sum(fb3x4+j*4, 4);
      if(t<1e-15) status=-1;
      abyx(1/t, fb3x4+j*4, 4);
   }
   if(status)
      matout (F0, fcodon, 16, 4);
   return(status);
}

void OutFb3x4 (FILE*fout, double fb3x4[])
{
   int j,k;
   for(j=0; j<3; j++) {
      fprintf(fout, "\nposition %2d:", j+1);
      for(k=0;k<4;k++) 
         fprintf(fout,"%5c:%7.5f", BASEs[k],fb3x4[j*4+k]);
   }
   fprintf(fout,"\nAverage     ");
   for(k=0; k<4; k++) 
      fprintf(fout,"%5c:%7.5f", BASEs[k],(fb3x4[0*4+k]+fb3x4[1*4+k]+fb3x4[2*4+k])/3);
}


void CountCodons (FILE *fout,double fcodonsg[],double fb3x4sg[],double fb4g[])
{
/* Outputs codon counts and f3x4 tables, called from InitializeCodon(), where 
   more notes are found.
*/
   int h, j,k, nc=NCODE, ig, wname=15, nb[3], ib[3][4], ic;

   /* counts codons for output, species first, genes next */
   fputs("Codon usage in sequences\n",fout);
   zero(fcodonsg, com.ns*nc);
   for(j=0; j<com.ns; j++) {
      for(h=0; h<com.npatt; h++) {
         for(k=0; k<3; k++)
            NucListall(CODONs[com.z[j][h]][k], &nb[k], ib[k]);
         k = nb[0]*nb[1]*nb[2];
         if(k>1)  continue;
         ic = ib[0][0]*16+ib[1][0]*4+ib[2][0];
         fcodonsg[j*nc+ic] += com.fpatt[h];
      }
      Fcodon_3x4(fcodonsg+j*nc, fb3x4sg+j*12);
   }
   printcums(fout, com.ns, fcodonsg, com.icode);
   fputs("Codon position x base (3x4) table for each sequence.",fout);
   for(j=0; j<com.ns; j++) {
      fprintf (fout,"\n\n#%d: %-*s", j+1,wname,com.spname[j]);
      OutFb3x4(fout, fb3x4sg+j*12);
   }

   zero(fcodonsg, (com.ngene+1)*nc);
   zero(fb4g, (com.ngene+1)*4);
   for(ig=0; ig<com.ngene; ig++) {
      for(j=0; j<com.ns; j++) {
         for(h=com.posG[ig]; h<com.posG[ig+1]; h++) {
            for(k=0; k<3; k++)
               NucListall(CODONs[com.z[j][h]][k], &nb[k], ib[k]);

            k = nb[0]*nb[1]*nb[2];
            if(k>1) continue;
            ic = ib[0][0]*16+ib[1][0]*4+ib[2][0];
            fcodonsg[ig*nc+ic] += com.fpatt[h];
         }
      }
      if(Fcodon_3x4(fcodonsg+ig*nc, fb3x4sg+ig*12)) {
         printf("Gene %d seems empty.", ig+1);
         exit(-1);
      }
   }
   if(com.ngene>1) {
      fputs("\n\nCodon usage in genes\n",fout);
      printcums(fout, com.ngene, fcodonsg, com.icode);
      fputs("Codon position x base (3x4) table for each gene.\n",fout);
      for(ig=0; ig<com.ngene; ig++) {
         fprintf (fout,"\n\nGene #%d", ig+1);
         OutFb3x4(fout, fb3x4sg+ig*12);
      }
   }
   
   for(ig=0; ig<com.ngene; ig++)  
      for(k=0;k<nc;k++) fcodonsg[com.ngene*nc+k]+=fcodonsg[ig*nc+k];
   Fcodon_3x4(fcodonsg+com.ngene*nc, fb3x4sg+com.ngene*12);
   for(ig=0; ig<com.ngene+1; ig++)
      for(j=0;j<3;j++) for(k=0;k<4;k++) fb4g[ig*4+k]+=fb3x4sg[ig*12+j*4+k]/3;
   
   fputs("\n\nSums of codon usage counts",fout);
   printcu(fout, fcodonsg+com.ngene*nc, com.icode);
   if(!com.cleandata) fputs("\n(Ambiguity data are not used in the counts.)\n",fout);
   fputs("\n\nCodon position x base (3x4) table, overall\n",fout);
   OutFb3x4(fout, fb3x4sg+com.ngene*12);


   {
      double *fb3x4 = fb3x4sg+com.ngene*12, GC3;
      GC3 = (fb3x4[0*4+1] + fb3x4[1*4+1] + fb3x4[2*4+1])/3
          + (fb3x4[0*4+3] + fb3x4[1*4+3] + fb3x4[2*4+3])/3;
      fprintf(frst1, "\t%.4f", GC3);
   }

}


void AddCodonFreqSeqGene (int js, int ig, double fcodon0[], double fcodon[],
                    double fb3x40[], double fb3x4[], 
                    double fb40[], double fb4[]);

void AddCodonFreqSeqGene (int js, int ig, double fcodon0[], double fcodon[],
                    double fb3x40[], double fb3x4[], 
                    double fb40[], double fb4[])
{
/* This adds codon and nucleotide counts in sequence js in gene ig to fcodon,
   fb3x4, and fb4, using fcodon0, fb3x40, and fb40 to resolve ambiguities
   Similar to AddFreqSeqGene().
*/
   int h, k, i0,i1,i2, nc=NCODE;
   int nb[3],ib[3][4],ic=-1;
   double t,t1;
   char str[4]="   ", codon[4]=" ", ft[64];

   for(h=com.posG[ig]; h<com.posG[ig+1]; h++) {
      for(k=0; k<3; k++)
         NucListall(CODONs[com.z[js][h]][k], &nb[k], ib[k]);
      k = nb[0]*nb[1]*nb[2];
      for(k=0; k<3; k++) {  /* f3x4 & f1x4, no regard for stop codons */
         for(i0=0,t=t1=0; i0<nb[k]; i0++) {
            t  += fb3x40[k*4+ib[k][i0]];
            t1 += fb40[ib[k][i0]];
         }
         for(i0=0; i0<nb[k]; i0++) {
            fb3x4[k*4+ib[k][i0]] += com.fpatt[h] * fb3x40[k*4+ib[k][i0]]/t;   
            fb4[ib[k][i0]]       += com.fpatt[h]* fb40[ib[k][i0]]/t1;
         }
      }
      for(i0=0; i0<64; i0++) ft[i0]=0;
      for(i0=k=0,t=0; i0<nb[0]; i0++) FOR(i1,nb[1]) FOR(i2,nb[2]) {
         ic = ib[0][i0]*16+ib[1][i1]*4+ib[2][i2];         
         if(FROM64[ic]==-1) continue;
         ft[ic] = 1;  k++;
         t += fcodon0[ic];
      }
      if(k==0) printf("%s in seq. %d is stop (icode=%d)\n", 
         getcodon(str,ic),js+1,com.icode);
      if(t<1e-100)
         printf("difficulty in resolving codon %s.\n", codon);
      for(ic=0; ic<nc; ic++)  if(ft[ic]) 
         fcodon[ic] += (t>0 ? com.fpatt[h]*fcodon0[ic]/t : com.fpatt[h]/k);
   }
}


int InitializeCodon (FILE *fout, double space[])
{
/* Count codons for genes, calculate site patterns and fpatt.
   Sequences com.z[] are not coded and may contain ambiguity characters
   Space requirement for fcodonsg & fb3x4sg: max(ngene+1,ns)*(64+12+4).
   First we count codons for output, with ambiguity characters ignored.    
   Then we recount to resolve ambiguity characters, to be used for ML 
   calculation later on.
   set up com.pi[NCODE], com.piG[NGENE][64], according to com.codonf
   com.pi[] has freqs for all codon sites in the seqs if ngene>1.
   Space use is not economical as com.piG and fcodonsg are separate and 
   duplicated.
*/
   int j,k, nc=NCODE, ig, ic[3], wrongorder[4]={2,1,3,0};
   int irf,nrf=20;
   double *fcodonsg=space, *fb3x4sg=space+max2((com.ngene+1),com.ns)*nc;
   double *fb4g=space+(com.ngene+1)*(64+12);
   double *ppi, fcodon0[64],fb3x40[12],fb40[4], d1,d2,d3;

   /* counts codons for output, species first, genes next */
   if(noisy) puts("Counting codons..");
   CountCodons(fout, fcodonsg, fb3x4sg, fb4g);

   /* Now to count fcodonsg, fb3x4sg, fb4g, to set up pi's for ML calculation.
      Three iterations are going on at the same time.
   */
   if (com.codonf!=Fequal && !com.cleandata) { /* iteration to resolve ambiguities */
      for(ig=0; ig<com.ngene; ig++) {    /* calculate com.piG[] */
         axtoy(1/sum(fcodonsg+ig*nc,nc), fcodonsg+ig*nc, fcodon0, nc);
         xtoy(fb3x4sg+ig*12, fb3x40, 12);
         xtoy(fb4g+ig*4, fb40, 4);

         for(irf=0; irf<nrf; irf++) {
            zero(fcodonsg + ig*nc, nc);
            zero(fb3x4sg + ig*12, 12);
            zero(fb4g+ig*4, 4);
            for(j=0; j<com.ns; j++) {
               AddCodonFreqSeqGene (j, ig, fcodon0, fcodonsg+ig*nc, 
                  fb3x40, fb3x4sg+ig*12, fb40, fb4g+ig*4);
            }
            abyx(1/sum(fcodonsg+ig*nc,nc), fcodonsg + ig*nc, nc);
            for(k=0; k<3; k++) 
               abyx(1/sum(fb3x4sg+ig*12+k*4,4), fb3x4sg+ig*12+k*4, 4);
            abyx(1/sum(fb4g+ig*4,4), fb4g+ig*4, 4);
            d1 = distance(fcodonsg+ig*nc, fcodon0, nc);
            d2 = distance(fb3x4sg+ig*12, fb3x40, 12);
            d3 = distance(fb4g+ig*4, fb40, 4);
            if(d1<1e-8 && d2<1e-8 && d3<1e-8) 
               break;
            xtoy(fcodonsg+ig*nc, fcodon0, nc);
            xtoy(fb3x4sg+ig*12, fb3x40, 12);
            xtoy(fb4g+ig*4, fb40, 4);
         } /* for(irf) */
      }   /* for(ig) */

      axtoy(1/sum(fcodonsg+com.ngene*nc,nc), fcodonsg+com.ngene*nc, fcodon0, nc);
      xtoy(fb3x4sg+com.ngene*12, fb3x40, 12);
      xtoy(fb4g+com.ngene*4, fb40, 4);
      for(irf=0; irf<nrf; irf++) {  /* calculate com.pi[] */
         zero(fcodonsg + com.ngene*nc, nc);
         zero(fb3x4sg + com.ngene*12, 12);
         zero(fb4g + com.ngene*4, 4);
         for(ig=0; ig<com.ngene; ig++)
            for(j=0; j<com.ns; j++) {
               AddCodonFreqSeqGene(j, ig, fcodon0, fcodonsg+com.ngene*nc, 
                  fb3x40, fb3x4sg+com.ngene*12, fb40, fb4g+com.ngene*4);
            }
         abyx(1/sum(fcodonsg+com.ngene*nc,nc), fcodonsg+com.ngene*nc, nc);
         for(k=0;k<3;k++) 
            abyx(1/sum(fb3x4sg+com.ngene*12+k*4,4), fb3x4sg+com.ngene*12+k*4, 4);
         abyx(1/sum(fb4g+com.ngene*4,4), fb4g+com.ngene*4, 4);
         d1 = distance(fcodonsg+com.ngene*nc, fcodon0, nc);
         d2 = distance(fb3x4sg+com.ngene*12, fb3x40, 12);
         d3 = distance(fb4g+com.ngene*4, fb40, 4);
         if(d1<1e-8 && d2<1e-8 && d3<1e-8)  break;
         xtoy(fcodonsg+com.ngene*nc, fcodon0, nc);
         xtoy(fb3x4sg+com.ngene*12, fb3x40, 12);
         xtoy(fb4g+com.ngene*4, fb40, 4);
      } /* for(irf) */
   }

   /* edit com.pi & com.piG according to com.codonf */
   for(ig=0; ig<com.ngene+1; ig++) {
      ppi = (ig<com.ngene?com.piG[ig]:com.pi);
      zero(ppi, nc);
      if (com.codonf==Fequal)
         fillxc(ppi,1,com.ncode);
      else if (com.codonf==Fcodon || com.codonf==FMutSel0 || com.codonf==FMutSel) {
         for(k=0; k<nc; k++)
            if(FROM64[k]>-1)  ppi[FROM64[k]] = fcodonsg[ig*nc+k]; 
      }
      else if (com.codonf==F3x4 || com.codonf==F3x4MG) {
         for(k=0; k<nc; k++)
            if(FROM64[k]>-1)
               ppi[FROM64[k]] = fb3x4sg[ig*12+k/16]*fb3x4sg[ig*12+4+(k/4)%4]*fb3x4sg[ig*12+8+k%4];
      }
      else if (com.codonf==F1x4 || com.codonf==F1x4MG) {
         for(k=0; k<nc; k++)
            if(FROM64[k]>-1)
               ppi[FROM64[k]] = fb4g[ig*4+k/16]*fb4g[ig*4+(k/4)%4]*fb4g[ig*4+k%4];
      }
      abyx(1/sum(ppi,com.ncode), ppi, com.ncode);  /* ncode != nc */

      if(ig<com.ngene) {
         if (com.codonf>=F1x4 && com.codonf<=FMutSel)
            xtoy(fb3x4sg+ig*12, com.f3x4[ig], 12);
         /* write 1x4 tables into 3x4 tables */
         if (com.codonf==FMutSel0 || com.codonf==FMutSel || com.codonf==F1x4 || com.codonf==F1x4MG) {
            for(k=0; k<4; k++)  {
               d1 = com.f3x4[ig][0*4+k] + com.f3x4[ig][1*4+k] + com.f3x4[ig][2*4+k];
               for(j=0; j<3; j++)
                  com.f3x4[ig][j*4+k] = d1/3;
            }
         }
      }
   }

   if(com.codonf==FMutSel0) {
      for(j=0,zero(com.piAA,20); j<com.ncode; j++) 
         com.piAA[GeneticCode[com.icode][FROM61[j]]] += com.pi[j];
      matout(F0, com.piAA, 1, 20);
   }

   if(com.codonf>=F1x4 && com.codonf<=FMutSel)
      com.pf3x4 = com.f3x4[0];

   if(com.verbose && com.ngene==1) {
      fprintf(fout,"\n\nCodon frequencies under model, for use in evolver (TTT TTC TTA TTG ... GGG):\n"); 
      for(k=0; k<64; k++) {
        fprintf(fout,"%12.8f",GeneticCode[com.icode][k]==-1?0:com.pi[FROM64[k]]);
        if((k+1)%4==0) FPN(fout);
      }
/*      
      fprintf(fout, "\nWrong order: AAA AAC AAG AAT ... TTT\n");
      for(k=0; k<64; k++) {
         ic[0] = wrongorder[k/16]; 
         ic[1] = wrongorder[(k/4)%4]; 
         ic[2] = wrongorder[k%4];
         j = ic[0]*16+ic[1]*4+ic[2];
         if(GeneticCode[com.icode][j]!=-1)
            fprintf(fout,"%.8f, ", com.pi[FROM64[j]]);
      }
      exit(0);
*/
   }
   return(0);
}



int AA2Codonf(double faa[20], double fcodon[])
{
/* get codon freqs from amino acid freqs, assuming equal freq. for each syn
   codon.  Used in codon-based amino acid substitution models.
*/
   int ic, iaa, i, NCsyn[20];

   FOR(i,20) NCsyn[i]=0;
   FOR(ic,64) if((iaa=GeneticCode[com.icode][ic])!=-1) NCsyn[iaa]++;
   zero(fcodon, 64);
   for(ic=0; ic<Nsensecodon; ic++) {
      iaa=GeneticCode[com.icode][FROM61[ic]];
      fcodon[ic]+=faa[iaa]/NCsyn[iaa];
   }
   if(fabs(1-sum(fcodon,64))>1e-6) printf("\n1 == %12.7f\n", sum(fcodon,64));
   return (0);
}


int DistanceMatAA (FILE *fout)
{
   int i,j, h;
   double p, lst;

   if(fout) fprintf(fout,"\nAA distances (raw proportions of different sites)\n");
   for(h=0,lst=0; h<com.npatt; h++)  lst+=com.fpatt[h];
   FOR(i, com.ns) {
      if(fout) fprintf(fout, "\n%-15s", com.spname[i]);
      FOR(j,i) {
         for(h=0,p=0; h<com.npatt; h++)
            if (com.z[i][h] != com.z[j][h]) p += com.fpatt[h];
         p /= lst;
         SeqDistance[i*(i-1)/2+j]=p;
         if(fout) fprintf(fout, " %7.4f", p);
      }
   }
   if(fout) FPN(fout);
   return (0);
}


int GetDaa (FILE* fout, double daa[])
{
/* Get the amino acid distance (or substitution rate) matrix 
   (grantham, dayhoff, jones, etc).
*/
   FILE * fdaa;
   char aa3[4]="";
   int i,j, naa=20;
   double dmax=0,dmin=1e40;

   if(noisy>3) printf("\n\nReading matrix from %s", com.daafile);
   if (com.model==REVaa_0||com.model==REVaa) puts(", to get initial values.");
   fdaa=gfopen(com.daafile, "r");

   for (i=0; i<naa; i++)  for (j=0,daa[i*naa+i]=0; j<i; j++)  {
      fscanf(fdaa, "%lf", &daa[i*naa+j]);
      daa[j*naa+i]=daa[i*naa+j];
      if (dmax<daa[i*naa+j]) dmax=daa[i*naa+j];
      if (dmin>daa[i*naa+j]) dmin=daa[i*naa+j];
   }
   if(com.aaDist && (com.seqtype==1||com.model==FromCodon)) { /* codon model */
      if(noisy) printf("\ndistance: %.2f --- %.2f\n", dmin, dmax);
      FOR (i,naa) FOR(j,naa) com.daa[i*naa+j]/=dmax;
   }
   else if (com.seqtype==AAseq) {
      for(i=0; i<naa; i++)  for(j=0; j<i; j++)
         if(i*naa+j!=ijAAref)
            daa[j*naa+i]=daa[i*naa+j] /= com.daa[ijAAref];
      daa[ijAAref]=daa[(ijAAref%naa)*naa+(ijAAref/naa)] = 1;

      if(com.model==Empirical) {
         FOR(i,naa) if(fscanf(fdaa,"%lf",&com.pi[i])!=1) 
            error2("aaRatefile");
         if (fabs(1-sum(com.pi,20))>1e-5) {
            printf("\nSum of freq. = %.6f != 1 in aaRateFile\n",sum(com.pi,naa)); 
            exit(-1);
         }
      }
   }
   fclose(fdaa);

   if(fout) {
      fprintf (fout, "\n%s\n", com.daafile);
      FOR (i,naa) {
         fprintf (fout, "\n%4s", getAAstr(aa3,i));
         FOR (j,i)  fprintf (fout, "%5.0f", daa[i*naa+j]); 
      }
      FPN (fout);
   }

/*
SetAA1STEP();
for(i=0,FPN(frst);i<naa;i++,FPN(frst))
   FOR(j,i) fprintf(frst,"%3d",AA1STEP[i*(i-1)/2+j]);

for(i=0,k=0;i<naa;i++) 
   FOR(j,i) if(AA1STEP[i*(i-1)/2+j]) {
      fprintf(frst,"%c%c\t%.2f\n",AAs[i],AAs[j],com.daa[i*naa+j]);
      k++;
   }
fprintf(frst,"\n%d one-step amino acid pairs\n", k);
exit (0);
*/

   return (0);
}


int SetAA1STEP (void)
{
/* Sets the global variable AA1STEP[19*20/2].
   Sets com.nrate for models like AAClasses and REVaa_0.
   AA1STEP[k] marks the k_th pair of amino acids that differ at one position, 
   Q[i*naa+j] is the k_th nonzero element if AA1STEP[k]=i*naa+j;
   Lower diagonal of Q is visited, with i>j.
*/
   int ncode0=com.ncode, nc, naa=20, i,j,k, ic1,ic2, ndiff, from[3],to[3];
   int *Q=(int*)PMat;

   setmark_61_64();
   nc=Nsensecodon;  com.ncode=ncode0;
   FOR (i, naa*naa) Q[i]=0;
   for (i=0; i<nc; i++) FOR (j,i) {
      ic1=FROM61[i]; from[0]=ic1/16; from[1]=(ic1/4)%4; from[2]=ic1%4;
      ic2=FROM61[j];   to[0]=ic2/16;   to[1]=(ic2/4)%4;   to[2]=ic2%4;
      for (k=0,ndiff=0; k<3; k++)  if (from[k]!=to[k]) ndiff++; 
      if (ndiff!=1)  continue; 
      ic1=GeneticCode[com.icode][ic1];
      ic2=GeneticCode[com.icode][ic2];
      Q[ic1*naa+ic2]++; 
      Q[ic2*naa+ic1]++;
   }
/*
#if DEBUG
      for (i=0,FPN(F0); i<naa; i++,FPN(F0)) FOR(j,i)printf("%3d",Q[i*naa+j]);
#endif
*/
   for (i=0,k=0; i<naa; i++) FOR(j,i) {
      if (Q[i*naa+j]>0) { AA1STEP[i*(i-1)/2+j]=1;  k++; }
      else                AA1STEP[i*(i-1)/2+j]=0;
   }
   /*
   for(i=0,FPN(F0);i<naa;i++,FPN(F0)) FOR(j,i)printf("%3d",AA1STEP[i*(i-1)/2+j]);
   */
   com.nrate=k-1;     /* one element (ijAAref) is fixed */

   return(0);
}

int GetOmegaAA (int OmegaAA[])
{
/* This routine reads the file OmegaAA.dat to initialize the
   lower diagonal matrix OmegaAA, which specifies the aa substituion
   rate classes.  To be used with the codon substitution model
   AAClasses, which specifies several classes of the dN/dS ratio.

   OmegaAA[iaa*(iaa-1)/2+jaa]= -1 if no one-step change is possible; 
                             = 0 for the first, background, class
                             = i (1,..,nclass) if iaa and jaa are in class i 
*/
   char *OmegaAAf="OmegaAA.dat", line[1024];
   FILE *fin;
   int iomega, n1step=0, i,j,k, iaa,jaa, npair, naa=20, nline=1024;

   for(i=0,n1step=0; i<naa; i++) FOR(j,i)
      if (AA1STEP[i*(i-1)/2+j]) { OmegaAA[i*(i-1)/2+j]=0; n1step++; }
      else                        OmegaAA[i*(i-1)/2+j]=-1;
   if (noisy) {
       printf("\n\n%d one-step aa pairs.\n", n1step);
       printf("Reading omega class from %s.\n", OmegaAAf);
   }
   fin=gfopen(OmegaAAf,"r");
   fscanf(fin, "%d", &com.nOmegaType);  
   printf ("# of dN/dS classes requested: %d.\n", com.nOmegaType);
   if (com.nOmegaType<1 || com.nOmegaType>65-1) { 
      if (com.seqtype!=CODONseq) puts("\nTo be tested.\a");
      com.nOmegaType=0;
      if (com.seqtype==AAseq) {
         FOR(i,naa) FOR(j,i) if(i*naa+j!=ijAAref && AA1STEP[i*(i-1)/2+j])
             OmegaAA[i*(i-1)/2+j]=com.nOmegaType++;
      }
      else
         FOR(i,naa) FOR(j,i) 
           if(AA1STEP[i*(i-1)/2+j]) OmegaAA[i*(i-1)/2+j]=com.nOmegaType++;
      printf("%d dN/dS ratios estimated from data.\nCrtl-C if wrong. Enter to continue.",com.nOmegaType);
      getchar ();
   }
   else {
      FOR (iomega, com.nOmegaType-1) {
         fscanf(fin, "%d", &j);
         if (j!=iomega+1) { printf("err data file %s.", OmegaAAf); exit(-1); } 
         printf ("\nClass #%d: ", j);
         j=fgetc (fin);  if (j!=':') error2("err expecting :");
         fgets (line, nline, fin);
      
         printf ("%s\n", line);
         for (j=0,npair=0; j<nline-1&&line[j]&&line[j]!='\n'; j++) {
            iaa=line[j];
            if (!isalpha(iaa)) continue;
            jaa=line[++j];  if(!isalpha(jaa)) error2("err jaa");
            npair++;

            printf ("\npair %2d: |%c%c| ", npair, iaa,jaa);
            iaa=CodeChara((char)iaa,AAseq); jaa=CodeChara((char)jaa,AAseq);
            if(iaa<0||iaa>19||jaa<0||jaa>19) error2("aa not found");
            if (iaa<jaa)  { k=jaa, jaa=iaa; iaa=k; }
      
            printf ("|%c%c (%2d,%2d)| ", AAs[iaa], AAs[jaa],iaa,jaa);
            if (iaa==jaa) puts("This pair has no effect.");
            if (OmegaAA[iaa*(iaa-1)/2+jaa]==-1) {
               puts("\nThis pair cannot change in one step and is ignored!");
               continue;
            }
            else if (OmegaAA[iaa*(iaa-1)/2+jaa]) 
               error2("This pair has already been specified?");
            OmegaAA[iaa*(iaa-1)/2+jaa]=iomega+1;
            printf (" in class %d ",iomega+1);
         }
      }
   }
   fclose(fin);
   com.nrate=com.nkappa=(com.hkyREV?5:!com.fix_kappa);
   com.nrate += (com.nOmega=com.nOmegaType);
   printf ("\n%d AA substitution types (omega's)\n", com.nOmegaType);
/*
   for (i=0; i<naa; i++,FPN(F0)) 
       FOR(j,i) printf ("%3d",OmegaAA[i*(i-1)/2+j]);
*/
   return (0);
}



int GetCodonFreqs2 (void)
{
/* Recalcualte the expected codon frequencies (com.pi[]) using the control
   variable com.codonf, and the observed codon frequencies in com.pi[].
   com.pi[] is both input (observed codon frequencies) and output (expected 
   frequencies under the model codonf).
   This is used by PairwiseCodon().
*/
   int n=com.ncode, i,j, ic,b[3];
   double *pi=com.pi, fb3x4[12], fb4[4], GC[3]={0};

   if (com.codonf==Fequal)
      { fillxc(pi,1./n,n); return 0; }
   if (com.codonf!=Fcodon && com.codonf!=FMutSel) {
      for (i=0,zero(fb3x4,12),zero(fb4,4); i<n; i++) {
         ic=FROM61[i];  b[0]=ic/16; b[1]=(ic/4)%4; b[2]=ic%4;
         for(j=0;j<3;j++) 
            { fb3x4[j*4+b[j]] += pi[i];  fb4[b[j]] += pi[i]/3.; }
      }
      for (i=0; i<n; i++) {
         ic=FROM61[i];  b[0]=ic/16; b[1]=(ic/4)%4; b[2]=ic%4;
         if (com.codonf==F3x4 || com.codonf==F3x4MG)
            pi[i]=fb3x4[b[0]]*fb3x4[4+b[1]]*fb3x4[8+b[2]];
         else
            pi[i]=fb4[b[0]]*fb4[b[1]]*fb4[b[2]];
      }

      if(com.codonf==F1x4MG)
         for(j=0;j<3;j++) 
            xtoy(fb4, com.pf3x4+j*4, 4);
      else if(com.codonf==F3x4MG)
         xtoy(fb3x4, com.pf3x4, 12);

      abyx (1./sum(pi,n), pi, n);

      GC[0]=(fb3x4[0+1]+fb3x4[0+3])*100;
      GC[1]=(fb3x4[4+1]+fb3x4[4+3])*100;
      GC[2]=(fb3x4[8+1]+fb3x4[8+3])*100;
      /*  fprintf(frst1, "\tGC123\t%.1f\t%.1f\t%.1f", GC[0],GC[1],GC[2]);  */
   }
   return 0;
}


double lfun2dSdN (double x[], int np)
{
/* likelihood function for calculating dS and dN between 2 sequences,
   com.z[0] & com.z[1:
         f(i,j) = \pi_i * p_{ij}(t)
   
   Data are clean and coded.
   Transition probability pijt is calculated for observed patterns only.
*/
   int n=com.ncode, h,i,k, ik, z0,z1;
   double lnL=0, fh,expt[NCODE], mr=0;

   NFunCall++;
   k=1, ik=0;
   if(com.hkyREV==0) {
      if(com.fix_kappa==1) { com.pkappa[0]=com.kappa; ik=1; }
      else                 com.kappa=x[k]; /* Is this necessary? */
   }
   for(i=0; i<(com.hkyREV?5:!com.fix_kappa); i++)
      com.pkappa[ik++]=x[k++];
   if(com.codonf==FMutSel) 
      for(i=0; i<3; i++) 
         com.pkappa[ik++]=x[k++];

   if(!com.fix_omega) com.omega=x[1+com.nkappa];
   if(!com.fix_kappa || !com.fix_omega)
      EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr, com.pkappa, com.omega,PMat);

   for(k=0; k<n; k++) 
      expt[k]=exp(x[0]*Root[k]);
   for (h=0; h<com.npatt; h++) {
      if(com.fpatt[h]<1e-20) continue;
     z0=com.z[0][h];  z1=com.z[1][h];
      for(k=0,fh=0;k<n;k++)
         fh += U[z0*n+k]*expt[k]*V[k*n+z1];
      fh*=com.pi[z0];
      if(fh<=0) {
         matout(F0,x,1,np); printf("lfun2dSdN: fh = %.9f\n",fh);
         fh=1e-70;
      }
      lnL -= log(fh) * com.fpatt[h];
   }
   return (lnL);
}


int VariancedSdN (double t, double omega, double vtw[2*2], double vdSdN[2*2])
{
/* This calculates the covariance matrix of dS & dN, using the 
   difference approximation, from the covariance matrix of t and 
   omega (vtw).  com.kappa and com.pi are used.  Sampling errors
   in parameters other than t and omega, such as kappa and pi[], 
   are ignored.
         JacobiSN = {{dS/dt, dS/dw}, {dN/dt,dN/dw}}
*/
   int np=2;
   double JacobiSN[2*2],T1[2*3],T2[2*3], S,dS,dN, dS1,dN1,dS2,dN2, eh, mr=0;

   if(vtw[0]<=0 || vtw[3]<=0) { 
      puts("var(dS,dN) not calculable."); 
      zero(vdSdN,4); 
      return(-1); 
   }

   /* printf("\nt & w: %.5f %.5f\n", t, omega);
      matout(F0,vtw, 2,2); */
   EigenQcodon(1,t,&S,&dS,&dN,NULL,NULL,NULL, &mr, com.pkappa,omega,PMat);

   eh = (t+1)*Small_Diff;
   EigenQcodon(1,t+eh,&S,&dS1,&dN1,NULL,NULL,NULL, &mr, com.pkappa,omega,PMat);
   EigenQcodon(1,t-eh,&S,&dS2,&dN2,NULL,NULL,NULL, &mr, com.pkappa,omega,PMat);
   JacobiSN[0*np+0] = (dS1 - dS2)/(2*eh);
   JacobiSN[1*np+0] = (dN1 - dN2)/(2*eh);
  
   eh = (omega+1)*Small_Diff;
   EigenQcodon(1,t,&S,&dS1,&dN1,NULL,NULL,NULL, &mr, com.pkappa,omega+eh,PMat);
   EigenQcodon(1,t,&S,&dS2,&dN2,NULL,NULL,NULL, &mr, com.pkappa,omega-eh,PMat);
   JacobiSN[0*np+1] = (dS1 - dS2)/(2*eh);
   JacobiSN[1*np+1] = (dN1 - dN2)/(2*eh);
  
   matby(JacobiSN,vtw,T1,2,2,2);
   mattransp2 (JacobiSN, T2, 2, 2);
   matby(T1,T2,vdSdN,2,2,2);

   /* matout(F0,vdSdN, 2,2); */

   return (0);
}

double distanceHKY85 (double x[], double *kappa, double alpha);
int distance3pos(double dHKY[], double kHKY[], int *sites4, char *z1, char *z2);

int distance3pos(double dHKY[], double kHKY[], int *sites4, char *z1, char *z2)
{
/* This calculates nucleotide-based distances between two protein-coding 
   DNA sequences z1 and z2, both of which are coded.  com.cleandata = 1 is 
   assumed.
*/
   int i,j, h, k, ic1, ic2, from[3], to[3];
   double fij[4][16]={{0}}, pi4[4]={0};
   /* [0,1,2] are for 3 positions, [3] is for 4-fold */

   for (h=0; h<com.npatt; h++) {
      ic1=FROM61[(int)z1[h]]; from[0]=ic1/16; from[1]=(ic1/4)%4; from[2]=ic1%4;
      ic2=FROM61[(int)z2[h]];   to[0]=ic2/16;   to[1]=(ic2/4)%4;   to[2]=ic2%4;
      for(k=0; k<3; k++) 
         fij[k][from[k]*4+to[k]] += com.fpatt[h]/com.ls;
      if(from[0]==to[0] && from[1]==to[1] && FourFold[to[0]][to[1]]) 
         fij[3][from[2]*4+to[2]] += com.fpatt[h];
   }
   *sites4 = (int) sum(fij[3], 16);

   if(*sites4)
      FOR(k,16) fij[3][k] /= *sites4;
   FOR(i,4) FOR(j,4) pi4[i]+=fij[3][i*4+j]/2;
   FOR(i,4) FOR(j,4) pi4[j]+=fij[3][i*4+j]/2;

   for(k=0; k<4; k++)
      dHKY[k] = distanceHKY85(fij[k], &kHKY[k], 0);
   return(0);
}


int PairwiseCodon (FILE *fout, FILE*fds, FILE*fdn, FILE*ft, double space[])
{
/* Calculates ds & dn for all pairwise codon sequence comparisons.
   It uses different npatt for different pairs.
   The data com.z[] should be encoded clean data, with ambiguity characters 
   removed.  Think of what to do with raw unclean data.
   JacobiSN has two columns, the 1st are deratives of dS (dS/dt, dS/dk, dS/dw)
   and the second of dN.
*/
   char *pz0[NS],codon[2][3];   /* pz0, npatt0, & fpatt0 hold the old information */
   int npatt0=com.npatt;
   double *fpatt0, ls0=com.ls;
   float fp[NCODE*NCODE];
   int n=com.ncode, is,js,j,k,h, i0,np, wname=15;
   int nb[3],ib[3][4],ic[2], missing=0, sites4;
   double x[10]={.9,1,.5,.5,.5,.5,.3}, xb[10][2]={{1e-5,50}}, large=50;
   double kappab[2]={.01,999}, omegab[2]={.001,99};
   double lnL, e=1e-7, *var=space+NP, S,dS,dN, mr=0;
   double JacobiSN[2*3],T1[2*3],T2[2*3],vSN[2*2], dS1,dN1,dS2,dN2,y[3],eh; 
          /* for calculating SEs of dS & dN */
   double dHKY[4], kHKY[4];

   fpatt0=(double*)malloc(npatt0*3*sizeof(double));
   FOR(k,com.ns) pz0[k]=com.z[k];
   com.z[0]=(char*)(fpatt0+npatt0);  com.z[1]=com.z[0]+npatt0;
   FOR (k,npatt0) fpatt0[k]=(float)com.fpatt[k];

   if(!com.cleandata) puts("\nPairwiseCodon: pairwise deletion.");
   if (com.ngene>1 && com.Mgene==1) puts("ngene>1 to be tested.");
   if (noisy>1) printf("\npairwise comparison (Goldman & Yang 1994).\n");
   fprintf(fout,"\npairwise comparison, codon frequencies: %s.\n",
      codonfreqs[com.codonf]);

   FOR(j,com.nkappa) { xb[1+j][0]=kappab[0]; xb[1+j][1]=kappab[1]; }
   if(!com.fix_omega)  { k=1+com.nkappa; xb[k][0]=omegab[0]; xb[k][1]=omegab[1]; }

   fprintf(fds,"%6d\n", com.ns);  fprintf(fdn,"%6d\n", com.ns);
   fprintf(ft,"%6d\n", com.ns);
   fprintf(frst, "\n\npairwise comparison (Goldman & Yang 1994)");
   fprintf(frst,
      "\nseq seq        N       S       dN       dS     dN/dS   Paras.\n");

   for(is=0;is<com.ns;is++) {
      fprintf(fds,"%-*s ", wname,com.spname[is]);
      fprintf(fdn,"%-*s ", wname,com.spname[is]);
      fprintf(ft,"%-*s ", wname,com.spname[is]);
      for(js=0; js<is; js++) {
         if(noisy>9) {
            puts("\ni & j (i>j)? "); scanf("%d%d",&is,&js);  
            is--; js--;
            if(is>com.ns || js<0 || is<js) error2("invalid pair");
         }
         if(noisy>1) printf ("\n%4d vs. %3d", is+1, js+1);
         fprintf(fout,"\n\n%d (%s) ... %d (%s)",
              is+1,com.spname[is], js+1,com.spname[js]);
         fprintf (frst, "%3d %3d ", is+1, js+1);
         if(noisy>2) fprintf(frub, "\n\n%d (%s) ... %d (%s)",
                  is+1,com.spname[is], js+1,com.spname[js]);
         FOR(k,n*n) fp[k]=0;
         if(com.cleandata) {
            for(h=0; h<npatt0; h++) {
               j = max2(pz0[is][h],pz0[js][h]);
               k = min2(pz0[is][h],pz0[js][h]);
               fp[j*n+k] += (float)fpatt0[h];
            }
         }
         else {
            for(h=0,com.ls=0; h<npatt0; h++) {
               FOR(i0,2) FOR(k,3) codon[i0][k]=pz0[i0==0?is:js][h*3+k];
               for(i0=0,missing=0; i0<2; i0++) {
                  for(k=0; k<3; k++)
                     NucListall(codon[i0][k], &nb[k], ib[k]);
                  if(nb[0]*nb[1]*nb[2]!=1)  { missing=1; break; }
                  else  ic[i0]=FROM64[ ib[0][0]*16+ib[1][0]*4+ib[2][0] ];
               }
               if(missing) continue;
               com.ls+=(int)fpatt0[h];

               j=max2(ic[0],ic[1]);
               k=min2(ic[0],ic[1]);
               fp[j*n+k]+=(float)fpatt0[h];
            }
         }

         for(j=0,com.npatt=0;j<n;j++) {
            for(k=0;k<j+1;k++)
               if(fp[j*n+k]) {
                  com.z[0][com.npatt]=(char)j;
                  com.z[1][com.npatt]=(char)k;
                  com.fpatt[com.npatt++]=fp[j*n+k];
               }
         }
         if(noisy>2) printf("\n  npatt=%d ",com.npatt);
         for(j=0,zero(com.pi,n); j<com.npatt; j++) {
            com.pi[(int)com.z[0][j]]+=com.fpatt[j]/(2.*com.ls);
            com.pi[(int)com.z[1][j]]+=com.fpatt[j]/(2.*com.ls);

         }
         GetCodonFreqs2 ();

         distance3pos(dHKY, kHKY, &sites4, com.z[0], com.z[1]);

         np=com.np = (com.ntime=1)+com.nkappa+!com.fix_omega;
         NFunCall=0;

         /* initial values and bounds */
         x[0]=SeqDistance[is*(is-1)/2+js]*(0.8+0.3*rndu());
         if(x[0]>3) x[0]=1.5+rndu();
         if(x[0]<1e-6) x[0]=.5*rndu();
         if(com.nkappa==1) { /* HKY type model */
            if(is==0 && js==1)  x[1]=(com.icode==1?4:1.5)+rndu();
            else                x[1]=(x[1]*2+2+rndu())/3;
            if(x[1]>10) x[1]=5;
            xb[1][0]=0.4;
         }
         else         /* REV or FMutSel models, do something later */
            for(j=1,x[1]=.8+.4*rndu(); j<com.nkappa; j++) x[1+j]=.2+.4*rndu();

         if(!com.fix_omega) {
            k=1+com.nkappa;
            if(is==0 && js==0) x[k]=0.2+0.2*rndu();
            else               x[k]=(3*x[k]+0.6*rndu())/4;
            x[k]=max2(x[k],0.01);
            x[k]=min2(x[k],2);
         }

         if(noisy>=9) {
            FPN(F0);  FOR(k,np) printf(" %12.6f",x[k]); FPN(F0);
            FOR(k,np) printf(" %12.6f",xb[k][0]); FPN(F0);
            FOR(k,np) printf(" %12.6f",xb[k][1]); FPN(F0);
         }
         
         if(com.fix_kappa && com.fix_omega)  
            EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr, com.pkappa,com.omega,PMat);

         if(np)
            ming2(noisy>3?frub:NULL,&lnL,lfun2dSdN,NULL,x,xb, space,e,np);
         else {  x[1]=x[2]=com.kappa=com.omega=0; lnL=0; }
         
         lnLmodel = lnL;
         fprintf(fout,"\nlnL =%12.6f\n",-lnL);
         FOR(k,np) fprintf(fout," %8.5f",x[k]);  FPN(fout);

         if(noisy>2) {
            printf("\n\nt_NG = %.5f\tMLEs: ", SeqDistance[is*(is-1)/2+js]);
            for(k=0;k<np;k++) printf(" %.5f", x[k]);
         }

         if (np && com.getSE) {
            Hessian(np, x, lnL, space, var, lfun2dSdN, var+np*np);
            matinv(var, np, np, var+np*np);
            fprintf(fout,"SEs for parameters:\n");
            FOR(k,np) fprintf(fout," %8.5f",(var[k*np+k]>0.?sqrt(var[k*np+k]):-0));
            FPN(fout);
         }
         FPN(fout);
         EigenQcodon(1,x[0],&S,&dS,&dN, NULL,NULL,NULL, &mr, com.pkappa,com.omega,PMat);

         if(noisy>=3) {
            puts("\nNucleotide-based analysis (approximate MLEs; use baseml to get proper MLEs):");
            printf("\ndHKY (123-4):");  FOR (k,4) printf(" %8.5f", dHKY[k]);
            printf("\nkHKY (123-4):");  FOR (k,4) printf(" %8.5f", kHKY[k]);
            printf(" (%d four-fold sites)\n", sites4);
         }
 
         fprintf(fds," %7.4f",dS);   fprintf(fdn," %7.4f",dN);
         fprintf(ft," %7.4f",x[0]);

         fprintf (fout,
             "t=%7.4f  S=%8.1f  N=%8.1f  dN/dS=%7.4f  dN=%7.4f  dS=%7.4f\n",
              x[0],S,com.ls*3-S,com.omega,dN,dS);

         fprintf(frst,"%8.1f %8.1f %8.4f %8.4f %8.4f",com.ls*3-S,S,dN,dS,com.omega);
         for(k=0; k<np; k++) fprintf(frst," %8.4f",x[k]);  
         /*
         for(k=0; k<np; k++) fprintf(frst1," %8.4f",x[k]);  
         fprintf(frst1,"\t%.3f", -lnL);
         */
         k=np-1;
         if (com.getSE)
            fprintf(frst," +-%6.4f",(var[k*np+k]>0.?sqrt(var[k*np+k]):-1));
         fprintf(frst," %9.3f\n",-lnL);
         if(com.getSE && !com.fix_omega) {
            FOR(k, np) {
               FOR(j,np) y[j]=x[j];
               y[k] += (eh=(x[k]+1)*Small_Diff);
               if(!com.fix_kappa) com.kappa=y[1];
               com.omega=y[1+!com.fix_kappa];
               EigenQcodon(1,y[0],&S,&dS1,&dN1,NULL,NULL,NULL, &mr, com.pkappa,com.omega,PMat);
               y[k] -= 2*eh;
               if(!com.fix_kappa) com.kappa=y[1];
               com.omega=y[1+!com.fix_kappa];
               EigenQcodon(1,y[0],&S,&dS2,&dN2,NULL,NULL,NULL, &mr, com.pkappa,com.omega,PMat);

               JacobiSN[0*np+k]=(dS1-dS2)/(2*eh);
               JacobiSN[1*np+k]=(dN1-dN2)/(2*eh);
            }

            matby(JacobiSN, var, T1, 2, np, np);
            mattransp2(JacobiSN, T2, 2, np);
            matby(T1,T2,vSN,2,np,2);
/*
            fputs("\nvar(dS,dN):\n", fout);
            matout(fout,vSN,2,2);
*/
            fprintf(fout,"dN = %7.5f +- %.5f   dS = %7.5f +- %.5f",
                 dN,(vSN[3]>0?sqrt(vSN[3]):-0),dS,(vSN[0]>0?sqrt(vSN[0]):-0));
            fprintf(fout," (by method 1)\n");

            T1[0] = var[0]; 
            T1[1] = T1[2] = var[0*np+np-1];
            T1[3] = var[(np-1)*np+(np-1)];
            if(com.getSE && !com.fix_omega)
               VariancedSdN(x[0], x[np-1], T1, vSN);

            fprintf(fout,"dN = %7.5f +- %.5f   dS = %7.5f +- %.5f",
               dN,(vSN[3]>0?sqrt(vSN[3]):-0),dS,(vSN[0]>0?sqrt(vSN[0]):-0));
            fprintf(fout," (by method 2)\n");

         }
         fflush(frst);  fflush(fout);
      }  /* for (js) */
      FPN(fds); FPN(fdn); FPN(ft);   fflush(fds); fflush(fdn); fflush(ft); 
   }     /* for (is) */

   com.ls=(int)ls0;  FOR(k,com.ns) com.z[k]=pz0[k];  
   com.npatt=npatt0;  FOR(h,npatt0) com.fpatt[h]=fpatt0[h]; free(fpatt0);
   return (0);
}


double lfun2AA (double t)
{
/* likelihood function for two amino acid sequences
         prob(i,j) = PI_i * p(i,j,t)
   
   The data are clean & coded (com.z[0] & com.z[1]).  
   Transition probability pijt is calculated for observed patterns only.
*/
   int n=20, h,k, aa0,aa1;
   double lnL=0, pijt,expt[20],al=com.alpha;

   if(al==0)  FOR(k,n) expt[k]=exp(t*Root[k]);
   else       FOR(k,n) expt[k]=pow(al/(al-t*Root[k]),al);
   for(h=0; h<com.npatt; h++) {
      aa0=com.z[0][h]; aa1=com.z[1][h];
      for(k=0,pijt=0;k<n;k++) 
         pijt+=U[aa0*n+k]*expt[k]*V[k*n+aa1];
      lnL-=log(com.pi[aa0]*pijt)*com.fpatt[h];
   }
   return(lnL);
}


int _nestS=0;   /* 189= estimate the S elements, 0= use those from com.daa[] */
static double *_Fij;

double lfun2AArev (double x[], int np)
{
/* np = _nestS + 19*3 + (1 or 2);
   x[]: Q matrix, 3*pi, 1 or 2 blength
   pi[0] is for the root, pi[1] & pi[2] are for Q[1] & Q[2] for the 2 branches.
   See notes in PairwiseAArev().
*/
   int i,j,k, n=20;
   double pi[3][20], *p, Q[3][400], *T=Q[0], *Fe=Q[0], t,t1,t2, m1,m2, lnL=0;
   double space[20*20*2+20*2];

   NFunCall++;
   for(k=0; k<3; k++) {
      for(i=0,p=pi[k],p[19]=1; i<n-1; i++) p[i]=x[_nestS+k*19+i];
      for(i=0,t=0; i<n; i++) t+=p[i];
      for(i=0; i<n; i++) p[i]/=t;
   }

   if(_nestS) {
      for(i=0,k=0; i<n; i++) {
         for(j=0,Q[1][i*n+i]=0;j<i;j++)
            if(i*n+j!=ijAAref) 
               Q[1][i*n+j]=Q[1][j*n+i] = x[k++];
      }
      Q[1][ijAAref]=Q[1][(ijAAref%n)*n+(ijAAref/n)]=1; 
   }
   else {
      for(i=0; i<n; i++)
         for(j=0,Q[1][i*n+i]=0;j<=i;j++)
            Q[1][i*n+j]=Q[1][j*n+i] = com.daa[i*n+j];
   }

   for(i=0,m1=m2=0; i<n; i++) {
      for(j=0,t1=t2=0;j<n;j++) {
         Q[2][i*n+j] = Q[1][i*n+j]*pi[2][j];
         Q[1][i*n+j]*= pi[1][j];
         t1 += Q[1][i*n+j];
         t2 += Q[2][i*n+j];
      }
      Q[1][i*n+i] = -t1;
      Q[2][i*n+i] = -t2;
      m1 += pi[1][i]*t1;
      m2 += pi[2][i]*t2;
   }

   if(com.ntime==1) { t1=x[np-1]/2/m1; t2=x[np-1]/2/m2; }
   else             { t1=x[np-2]/m1;   t2=x[np-1]/m2; }
   PMatQRev(Q[1], pi[1], t1, n, space);
   PMatQRev(Q[2], pi[2], t2, n, space);

   for(i=0; i<n*n; i++)  Fe[i]=0;
   for(k=0;k<n;k++) 
      for(i=0;i<n;i++)
         for(j=0,t=pi[0][k]*Q[1][k*n+i]; j<n; j++)
            Fe[i*n+j] += t*Q[2][k*n+j];

   /* if(fabs((t=sum(Fe,n*n))-1)>1e-6) printf("Fe = %.9f != 1\n", t); */

   for(i=0; i<n*n; i++) {
      if(_Fij[i]<=1e-15) continue;
      if(Fe[i]>1e-200) 
         lnL -= _Fij[i]*log(Fe[i]);
      else 
         printf("Fij_exp = %.10f < 0\n", Fe[i]);
   }
   return(lnL);
}

double PairwiseAArev (int is, int js)
{
/* This calculates pairwise distance under a nonstationary model.  It assumes 
   three sets of amino acid frequencies: pi[0] for the root, pi[1] and pi[2]
   are for the Q matrices for branches 1 and 2.  
   It estimate the symmetrical part of the rate matrix if _nestS==189.  
   If _nestS==0, it uses the symmetrical part read from the com.daa file.
   It can estimate 1 or 2 distances depending on com.ntime=1 or 2.

   np = 189 + 19*3 + (1 or 2);
   x[]: Q matrix, 3*pi, 1 or 2 blength
*/
   int n=com.ncode, h,i,j,k, np=_nestS+ 19*3 + 1;
   double Fij[400], x[248], xb[248][2], lnL, e=1e-9, t=0, p[20];

   com.ntime=1;  /* 1: t1=t2; 2: t1 and t2 */
   if(com.ntime==2) np++;
   _Fij=Fij;
   if(com.cleandata!=1) error2("cleandata");

   if(com.sspace < spaceming2(np)) {
      com.sspace = spaceming2(np);
      printf ("\nspace adjusted to %9lu bytes\n",com.sspace);
      if((com.space=(double*)realloc(com.space,com.sspace))==NULL)
         error2("oom space");
   }

   for(h=0,zero(Fij,n*n); h<com.npatt; h++) {
      Fij[com.z[is][h]*n+com.z[js][h]] += com.fpatt[h]/com.ls;
   }

   if(_nestS) {
      for (i=1,k=0; i<n; i++)  FOR(j,i)
         if(i*n+j!=ijAAref) x[k++] = (com.daa[i*n+j]+.001)*(0.8+0.4*rndu());
   }
   for(i=0;i<np;i++) {
      x[i]=rndu();  xb[i][0]=1e-5;  xb[i][1]=100;
   }
   lnL = lfun2AArev(x,np);
   printf("\nlnL0 = %12.6f\n",-lnL);

   ming2(noisy>2?frub:NULL,&lnL,lfun2AArev,NULL,x,xb, com.space, e, np);



for(k=0; k<3; k++) {
   for(i=0,p[19]=1; i<n-1; i++) p[i]=x[_nestS+k*19+i];
   for(i=0,t=0; i<n; i++) t+=p[i];
   for(i=0; i<n; i++) p[i]/=t;
   matout2(F0, p, 1, n, 7, 4);
}

   return (x[_nestS + 19*3]);
}


int PairwiseAA (FILE *fout, FILE*f2AA)
{
/* Calculates pairwise distances using amino acid seqs.
   Data (com.z[]) are clean and coded.
   com.npatt for the whole data set is used which may be greater than 
   the number of patterns for each pair.
   SE is not calculated.
*/
   char *pz0[NS];
   int n=com.ncode, j, is,js;
   double x, xb[2]={0,19}, lnL, step;

   if (com.ngene>1 && com.Mgene==1) error2("ngene>1 to be tested.");
   if (noisy) printf("\npairwise ML distances of AA seqs.\n\n");
/*
   if(com.model>Empirical_F)  error2("PairwiseAA: model wrong");
*/
   if(com.model==0)  fillxc(com.pi,1./n, n);
   if(com.model>=Empirical)  GetDaa(NULL, com.daa);
   if(com.model==0 || com.model==Empirical)
      EigenQaa(NULL, Root, U, V, NULL);

   FOR(j,com.ns) pz0[j]=com.z[j];
   fprintf(fout,"\nML distances of aa seqs.\n");
   if(com.alpha) 
      fprintf(fout,"\nContinuous gamma with alpha = %.3f is used (ncatG is ignored).\n\n",com.alpha);

   fprintf(f2AA,"%6d\n", com.ns);
   for(is=0; is<com.ns; is++,FPN(F0),FPN(fout),FPN(f2AA)) {
      printf ("%4d vs", is+1);
      fprintf(f2AA,"%-14s ", com.spname[is]);
      fprintf(fout,"%-14s ", com.spname[is]);
      for(js=0; js<is; js++) {

         if(com.model==REVaa) {
            x=PairwiseAArev(is, js);
            fprintf(f2AA," %7.4f",x); fprintf(fout," %7.4f",x); 
            continue;
         }

         com.z[0]=pz0[is]; com.z[1]=pz0[js]; 
         printf (" %2d", js+1);
         if(com.model==1||com.model==Empirical_F) {
            for (j=0,zero(com.pi,n); j<com.npatt; j++) {
               com.pi[(int)com.z[0][j]]+=com.fpatt[j];
               com.pi[(int)com.z[1][j]]+=com.fpatt[j];
            }
            abyx(1./sum(com.pi,n), com.pi, n);
            EigenQaa(NULL,Root,U,V,NULL);
         }
         /* com.posG[1]=com.npatt; */

         xb[0]=SeqDistance[is*(is-1)/2+js];  x=xb[0]*1.5;  step=xb[0];
         LineSearch(lfun2AA, &lnL, &x, xb, step, 1e-7);
         fprintf(f2AA," %7.4f",x); fprintf(fout," %7.4f",x); 
         if (com.getSE) ;
      }  /* for (js) */
   }     /* for (is) */

   FOR(j,com.ns) com.z[j]=pz0[j];
   return (0);
}


char GetAASiteSpecies(int species, int sitepatt)
{
/* this returns the amino acid encoded by the codon at sitepatt in species.
   Returns '*' if more than two amino acids or '-' if codon is --- or ***.
*/
   int n=com.ncode, c, naa, k;
   char aa, newaa;

   if(com.seqtype!=1)
      error2("GetAASiteSpecies() right now works for codon seqs only.  Check.");
   c = com.z[species][sitepatt];
   if(c<n) {
      aa = AAs[ GeneticCode[com.icode][FROM61[c]] ];
   }
   else { /* naa is = 1 or >1, precise value being incorrect. */
      for(k=0,aa=-1; k<nChara[c]; k++) {
         newaa = GeneticCode[com.icode][FROM61[ CharaMap[c][k] ]];
         if(newaa==-1) continue;
         newaa = AAs[newaa];
         if(aa==-1) {
            naa = 1;
            aa = newaa;
         }
         else 
            if(newaa != aa) naa++;
      }
      if(nChara[c]==n)  aa = '-';
      else if(naa>1)    aa = '*';
   }   
   return (aa);
}



int PrintProbNSsites (FILE* frst, double prob[], double meanw[], double varw[], int ncat, int refsp)
{
/*  This prints out posterior probabilities that each site is from a site class
    under the NSsites mdoels (model=0).
    This is called by both the old empirical Bayes routine (NEB) and also the new 
    Bayes empirical Bayes (BEB) routine.
*/
   int h, hp, it, ir, lst=(com.readpattern?com.npatt:com.ls);
   double psel=0, wpos=1, cutoff=0.5;
   double mpostp[NCATG];
   char  *sig, aa;

   char codons[2][4];
   double St, Nt, ns, na, ndiff;

   if(com.model==0) {
      fprintf(frst," & postmean_w");
      if(!BayesEB && com.rK[ncat-1]>1)  fprintf(frst," & P(w>1)");
   }
   fprintf(frst,"\n(amino acids refer to 1st sequence: %s)\n\n", com.spname[refsp]);
   zero(mpostp, com.ncatG);
   for(h=0; h<lst; h++,FPN(frst)) {
      hp = (!com.readpattern ? com.pose[h] : h);
      aa = GetAASiteSpecies(refsp, hp);
      fprintf(frst,"%4d %c  ", h+1, aa);
      for (ir=0,it=0,psel=0; ir<ncat; ir++) {
         fprintf(frst," %5.5f", prob[ir*com.npatt+hp]);
         if(prob[ir*com.npatt+hp] > prob[it*com.npatt+hp])
            it = ir;
         if(!BayesEB && com.model==0)
            if(com.rK[ir] > 1) psel += prob[ir*com.npatt+hp];
         mpostp[ir] += prob[ir*com.npatt+hp]/com.ls;

      }
      fprintf(frst, " (%2d)", it+1);
      if(com.model==0) {
         fprintf(frst, " %6.3f", meanw[hp]);
         if(!BayesEB && psel) fprintf(frst, " %6.3f", psel);
         if(BayesEB==1 && com.model==0)
            fprintf(frst, " +- %6.3f", varw[hp]);
      }
   }

   /*
   if(!BayesEB) {
      printf("\nmean posterior probabilities for site classes");
      matout(F0, mpostp, 1, com.ncatG);
      matout(F0, com.freqK, 1, com.ncatG);
   }
   */

   /* list of positively selected sites */
   if(com.model==0) { /* NSsites models */
      if(com.NSsites!=1 && com.NSsites!=7)
         fprintf(frst,"\nPositively selected sites\n\n\tProb(w>1)  mean w\n\n");

      for(ir=0,it=0; ir<ncat; ir++) 
         if(BayesEB==1 || (com.freqK[ir]>.1/com.ls && com.rK[ir]>wpos)) it=1;
      if(!com.aaDist && it) {
         fprintf(fout,"\nPositively selected sites (*: P>95%%; **: P>99%%)\n");
         fprintf(fout,"(amino acids refer to 1st sequence: %s)\n\n", com.spname[refsp]);
         fprintf(fout,"            Pr(w>1) %25s\n\n", "post mean +- SE for w");
         for(h=0; h<lst; h++) {
            hp=(!com.readpattern ? com.pose[h] : h);
            if(BayesEB==1)
               psel = prob[(ncat-1)*com.npatt+hp];
            else
               for (ir=0,psel=0; ir<ncat; ir++)
                  if(com.rK[ir]>wpos) psel+=prob[ir*com.npatt+hp];

            if(psel>cutoff) {
               sig = "  ";
               if(psel>.95) sig = "* ";
               if(psel>.99) sig = "**";
               aa = GetAASiteSpecies(refsp, hp);
               fprintf(fout,"%6d %c %10.3f%-8s %.3f", h+1, aa, psel, sig, meanw[hp]);
               fprintf(frst,"%6d %c %10.3f%-8s %.3f", h+1, aa, psel, sig, meanw[hp]);

               if(BayesEB==1 && com.model==0) {
                  fprintf(fout, " +- %5.3f", varw[hp]);
                  fprintf(frst, " +- %5.3f", varw[hp]);
               }

               /*********** print out both codons if 2 sequences ******/
               /*
               if(com.ns==2) {
                  codons[0] = CODONs[com.z[0][hp]]);
                  codons[1] = CODONs[com.z[1][hp]]);
                  ndiff=difcodonNG(codons[0], codons[1], &St,&Nt,&ns,&na,0,com.icode);
                  fprintf(fout,"\t%3s %3s  %2.0f diff (ps pn: %5.3f %5.3f)", codons[0], codons[1], ndiff, ns/St, na/Nt);
               }
               */

               FPN(fout);  FPN(frst);
            }
         }
         FPN(fout);
         if(!BayesEB==1 && com.rK[ncat-2]>wpos)
            fputs("\nNote: more than one w>1.  Check rst for details\n",fout);
      }
   }
   return(0);
}

int lfunNSsites_rate (FILE* frst, double x[], int np)
{
/* This calculates the dN/dS rates for sites under models with variabel dN/dS 
   ratios among sites (Nielsen and Yang 1998).  Modified from lfundG() 
   com.fhK[] holds the posterior probabilities.
*/
   int  h,hp, ir, it=0, refsp=0, k=com.ntime+com.nrgene+com.nkappa;
   double lnL=0, fh;
   double w2=x[com.np-1],psel=0, *meanw, maxmw, minmw, wpos=1.1, cutoff=0.5;
   char  *sig, aa;

   FILE *fsites, *fras;
   int  continuous=0, R,G,B;
   int  lst=(com.readpattern?com.npatt:com.ls);
   int  ncolors=5;  /* continuous = 0 uses the specified colors */
   char sitelabel[96], *colors[5]={"darkblue", "lightblue", "purple", "pinkred", "red"};
   char *colorvalues[5]={"[2,2,120]", "[133,57,240]", "[186,60,200]", "[200,60,160]", "[250,5,5]"};


   NFunCall++;
   if(com.nparK) error2("lfunNSsites_rate to be done for HMM.");

   if((meanw=(double*)malloc(com.npatt*sizeof(double)))==NULL) 
      error2("oom lfunNSsites_rate");  /* meanw useful for NSsites only */
   if(com.aaDist==0)
      printParametersNSsites(frst,x);
   else  
      fputs("\nCheck main result file for parameter estimates\n",frst);

   fx_r(x,np);
   if(com.NnodeScale)
      FOR(h,com.npatt) {
         for(ir=1,fh=com.fhK[h]; ir<com.ncatG; ir++)
            if(com.fhK[ir*com.npatt+h]>fh) fh=com.fhK[ir*com.npatt+h];
         for(ir=0; ir<com.ncatG; ir++)
            com.fhK[ir*com.npatt+h]=exp(com.fhK[ir*com.npatt+h]-fh);
         lnL-=fh*com.fpatt[h];
      }

   for(h=0; h<com.npatt; h++) {
      for (ir=0,fh=meanw[h]=0; ir<com.ncatG; ir++) {
         fh += (com.fhK[ir*com.npatt+h]*=com.freqK[ir]);  /* prior=>posterior */
         meanw[h] += com.fhK[ir*com.npatt+h]*com.rK[ir];
      }
      for (ir=0,meanw[h]/=fh; ir<com.ncatG; ir++) com.fhK[ir*com.npatt+h]/=fh;
      lnL -= com.fpatt[h]*log(fh);
   }

   fprintf(frst,"\nNaive Empirical Bayes (NEB) probabilities for %d classes",com.ncatG);
   if(com.model==0 && com.NSsites && com.NSsites!=1 && com.NSsites!=7) 
      fprintf(fout,"\nNaive Empirical Bayes (NEB) analysis");
   PrintProbNSsites(frst, com.fhK, meanw, NULL, com.ncatG, refsp);

   if(com.model && com.model<=NSbranch2) {  /* branch&site models */
      if(com.rK[0]>wpos || com.rK[1]>wpos) {  /* positive sites for all lineages */
         fputs("\n\nPositive sites for all lineages Prob(w>1):\n",fout);
         for(h=0; h<lst; h++) {
            hp=(!com.readpattern ? com.pose[h] : h);
            aa = GetAASiteSpecies(refsp, hp);
            psel = 0;
            if(com.rK[0]>wpos) psel =  com.fhK[0*com.npatt+hp];
            if(com.rK[1]>wpos) psel += com.fhK[1*com.npatt+hp];
            if(psel>cutoff) {
               sig = "";
               if(psel>.95) sig = "*";
               if(psel>.99) sig = "**";
               fprintf(fout, "%6d %c %.3f%s\n", h+1, aa, psel, sig);
            }
         }
      }
      if(w2>wpos && (com.freqK[com.ncatG-1]>1e-6)) {  /* for foreground branches */
         fprintf(fout,"\nNaive Empirical Bayes (NEB) analysis (please use the BEB results.)");
         fprintf(fout,"\nPositive sites for foreground lineages Prob(w>1):\n\n");
         for(h=0; h<lst; h++) {
            hp=(!com.readpattern ? com.pose[h] : h);
            aa = GetAASiteSpecies(refsp, hp);
            psel = com.fhK[2*com.npatt+hp]+com.fhK[3*com.npatt+hp];
            if(psel>cutoff) {
               sig = "";
               if(psel>.95) sig = "*";
               if(psel>.99) sig = "**";
               fprintf(fout, "%6d %c %.3f%s\n", h+1, aa, psel, sig);
            }
         }
      }
   }
   fprintf (frst,"\n\nlnL = %12.6f\n", -lnL);

   /* RasMol script for coloring structure */
   if(com.verbose && com.model==0) {
      fsites=(FILE*)fopen("SiteNumbering.txt", "r");
      if(fsites) {
         puts("\nCollecting RasMol commands for coloring structure into RasMol.txt");

         printf("Choose color scheme (0: %d colors, 1: white->red, 2: rainbow) ",ncolors);
         scanf("%d", &continuous);

         fras=(FILE*)gfopen("RasMol.txt", "w");
         for(h=0,maxmw=0,minmw=99; h<com.npatt; h++) {
            if(maxmw<meanw[h]) maxmw = meanw[h]; 
            if(minmw>meanw[h]) minmw = meanw[h]; 
         }
         if(continuous==0)
            for (it=0; it<ncolors; it++)
               printf("\t%-10s %-20s mean_w < %7.5f\n", 
                  colors[it], colorvalues[it], (it+1)*(maxmw-minmw)/ncolors);
         fprintf(fras, "cartoon\nset background white\n");
         for(h=0; h<lst; h++) {
            fscanf(fsites, "%d%s", &it, sitelabel);
            if(it-1!=h)  { puts("Site number wrong.  Giving up."); break; }
            if(strchr(sitelabel, '?')) continue;
            hp = (!com.readpattern ? com.pose[h] : h);

            if(continuous==0) {
               for (it=0; it<ncolors; it++)
                  if(meanw[hp]<minmw+(it+1.)*(maxmw-minmw)/ncolors+1e-9) break;
               fprintf(fras,"select %s\n\t\tcolor %s\n", sitelabel, colorvalues[it]);
            }
            else if (continuous==1) {
               it = 5+(int)(245*(meanw[hp]-minmw)/(maxmw-minmw+1e-9));
               fprintf(fras,"select %s\n\t\tcolor [250, %d, %d]\n", sitelabel, 255-it,255-it);
            }
            else {
               rainbowRGB((meanw[hp]-minmw)/(maxmw-minmw+1e-9), &R, &G, &B);
               fprintf(fras, "select %s\n\t\tcolor [%d, %d, %d]\n", sitelabel, R,G,B);
            }
         }
         fclose(fsites);  fclose(fras);
      }
   }
   free(meanw);

   if(com.model==0 && (com.NSsites==2 || com.NSsites==8) 
      && (com.fix_omega!=1 || com.omega!=1))   /* BEB for M2 & M8 */
      lfunNSsites_M2M8(frst, x, com.np);
   if(!com.fix_omega && (com.model==2 || com.model==3) && com.NSsites==2)  /* BEB for branchsite A & clade C */
      lfunNSsites_AC(frst, x, com.np);

   return (0);
}


#ifdef NSSITESBandits
void finishup(void)
{
   FILE *fend=NULL;
   fend=(FILE*)gfopen("finished","w");
   fclose(fend);
}
#endif


/*

(*) Codon models for variable dN/dS ratios among sites
    (com.nrate includes kappa & omega) (see also CDFdN_dS)

    NSsites          npara

    0  one-ratio     0:    one ratio for all sites
    1  neutral       1:    p0 (w0=0, w1=1)
    2  selection     3:    p0, p1, w2 (w0=0, w1=1)
    3  discrete      2K-1: p0,p1,..., and w0,w1,...
    4  freqs         K:    p's (w's are fixed)
    5  gamma         2:    alpha, beta
    6  2gamma        4:    p0, alpha1,beta1, alpha2=beta2
    7  beta          2:    p_beta, q_beta
    8  beta&w        4:    p0, p_beta, q_beta, w estimated
    9  beta&gamma    5:    p0, p_beta, q_beta, alpha, beta
   10  beta&1+gamma  5:    p0, p_beta, q_beta, alpha, beta (1+gamma used)
   11  beta&1>normal 5:    p0, p_beta, q_beta, mu, s    (normal truncated w>1)
   12  0&2normal     5:    p0, p1, mu2, s1, s2
   13  3normal       6:    p0, p1, mu2, s0, s1, s2
   14  M8a:beta&w=1  3:    p0, p_beta, q_beta, w=1 fixed
   15  M8a:beta&w>=1 4:    p0, p_beta, q_beta, w>=1 estimated

NSsites = 14 forces change to fix_omega so we can't have 2 models in one run.
NSsites = 15 would not set omegab[0] correctly for the next tree.


(*) Codon models for variable dN/dS ratios among both branches and sites
    (model=2, NSsites=3 or 2)
    (com.nrate includes kappa & omega)
    Parameters include branchlens, kappa, p0, p1, w0, w1, w2

    method = 0: SetPSiteClass copies w's to nodes[].omega and PMat is calculated
    in ConditionalPNode().  
    method = 1: PMat for branch of interest is calulated in lfuntdd_SiteClass().
    The two types of branches have different Qfactor_NS: Qfactor_NS_branch[2].
    August 2000.


(*) Codon (perhaps aa as well) site-class models

    NSsites=3, ncatG=3 or 2 etc
  
    aaDist: 
       1-6 for G1974,Miyata,c,p,v,a
       FIT1 & FIT2 (11, 12): fitness model F_j = a_p*(p-p*)^2+a_v*(v-v*)^2
       FIT1:   w_ij = exp(F_j - F_i)
       FIT2:   w_ij = b*exp(F_j - F_i)

       FIT1 & FIT2 are also implemented for NSsites=0


(*) Amino acid models

    REVaa: The symmetrical part (S) of the rate matrix Q=S*PI are estimated, 
           making up 19*20/2-1=189 rate parameters for the matrix.  The aa 
           frequencies are estimated using the observed ones.  The Sij for 
           ijAAref=19*naa+9 (I-V) is set to one and others are relative rates;
    REVaa_0: AA1STEP[i*(i+1)+j] marks the aa pair i & j that are 
            interchangeable.  Sij for ijAAref=19*naa+9 (I-V) is set to one 
            and others are relative rates;


(*)
    Codon & amino acid models

    AAClasses: OmegaAA[i*(i-1)/2+j] marks the dN/dS ratio class for the pair 
            i & j.  Note kappa is before omega's in x[].
            OmegaAA[i*(i-1)/2+j]=-1, if AAs i & j are not interchangeable
                       =0,  for the background ratio
                       =1,...,nclass for AAs i & j specified in OmegaAA.dat.
            The total number of classes (com.nOmega) is one plus the number 
            specified in the file OmegaAAf.

   com.nOmega is the number of different dN/dS ratios in the NSbranchB, NSbranch2 models
      and in AAClasses.
   nodes[].label marks the dN/dS ratio for the node in the NSbranchB NSbranch2 models
   AA1STEP[i*(i-1)/2+j] =1 if AAs i & j differ at one codon position;
                        =0 otherwise.

(*) Codon and amino acid models

    aaDist = -5,-4,-3,-2,-1,1,2,3,4,5: 
    Geometric and linear relationships between amino acid distance and 
    substitution rate:
       wij = a*(1-b*dij/dmax)
       wij = a*exp(-b*dij/dmax)
    aaDist = 0:equal, +:geometric; -:linear, {1-5:Grantham,Miyata,c,p,v}

    aaDist = 11, 12: fitness models, see above.
*/





#if 0  /* routines for testing codon-models */

int GetCategoryQc (char z[NS])
{
/* the category ID for a codon site with z[NS], transformed
   classified into 19 categories 
*/
   int i,j, icat, ncat=19, it, b[NS][3], nbase[3], markb[4];

   puts("\nDo not work with missing data, GetCategoryQc.");
   for (j=0; j<com.ns; j++) {
      it=FROM61[(int)z[j]];  b[j][0]=it/16; b[j][1]=(it/4)%4; b[j][2]=it%4;
   }
   FOR (i,3) {
      FOR (j,4) markb[j]=0;
      FOR (j,com.ns) markb[b[j][i]]=1;
      nbase[i]=markb[0]+markb[1]+markb[2]+markb[3]-1;
   }
   if(nbase[1]>=2) icat=ncat-1;
   else {
      if(nbase[0]>2) nbase[0]=2;  if(nbase[2]>2) nbase[2]=2;
      icat = nbase[1]*9+nbase[0]*3+nbase[2];
   }
   return (icat);
}

int TestModelQc (FILE * fout, double x[])
{
/* Test the Qc model, slower than simulations
*/
   char z[NS];
   int h, npatt, it, icat, j, nodeb[NS], imposs;
   int n=Nsensecodon, isum, nsum, ncat=19;
   double  fh, y, nobs[19], pexp[19], Pt[8][NCODE*NCODE];

   puts("\nDo not work with missing data, GetCategoryQc.");
   puts("\ntest Qc..\n");
   for (h=0,zero(nobs,ncat); h<com.npatt; h++) {
      for (j=0; j<com.ns; j++) z[j]=com.z[j][h]-1;
      icat = GetCategoryQc(z);
      nobs[icat]+=com.fpatt[h];
   }
   FOR (j,ncat) 
      printf("cat #%4d: %4d%4d%4d%6.0f\n", j+1,j/9+1,(j/3)%3+1,j%3+1,nobs[j]);

   if (com.ns>5 || com.alpha || com.ngene>1)
      error2 ("TestModelQc: ns>5 || alpha>0.");
   if (SetParameters (x)) puts ("\npar err..");
   for (j=0,npatt=1; j<com.ns; j++)  npatt*=n;
   for (isum=0,nsum=1; isum<tree.nnode-com.ns; nsum*=n,isum++) ;
   printf("\nTest Qc: npatt = %d\n", npatt);
   FOR (j, tree.nbranch) 
      PMatUVRoot (Pt[j], nodes[tree.branches[j][1]].branch,n,U,V,Root);

   for (h=0,zero(pexp,ncat); h<npatt; h++) {
      for (j=0,it=h; j<com.ns; nodeb[com.ns-1-j]=it%n,it/=n,j++) ;
      for (j=0,imposs=0; j<com.ns; j++) 
         { z[j]=nodeb[j];  if (com.pi[(int)z[j]]==0) imposs=1; }
      if (imposs) continue;
      
      if ((icat=GetCategoryQc(z)) == ncat-1) continue;
      if ((h+1)%100==0) 
         printf("\rTest Qc:%9d%4d%9.2f%%", h+1, icat, 100.*(h+1.)/npatt);

      for (isum=0,fh=0; isum<nsum; isum++) {
         for (j=0,it=isum; j<tree.nbranch-com.ns+1; j++)
            { nodeb[com.ns+j]=it%n; it/=n; }
         for (j=0,y=com.pi[nodeb[tree.root]]; j<tree.nbranch; j++) 
            y*=Pt[j][nodeb[tree.branches[j][0]]*n+nodeb[tree.branches[j][1]]];
         fh += y;
      }
      if (fh<=0) {
         matout (F0, x, 1, com.np);
         printf ("\a\ntest Qc: h=%4d  fh=%9.4f \n", h, fh);
      }
      pexp[icat]+=fh;
   }    
   pexp[ncat-1]=1-sum(pexp,ncat-1);

   FOR (j,ncat) 
      fprintf(fout, "\ncat # %4d%4d%4d%4d%6.0f%10.5f%10.2f", 
         j+1, j/9+1, (j/3)%3+1, j%3+1, nobs[j], pexp[j], com.ls*pexp[j]);
   return (0);
}

#endif

#if (DSDN_MC || DSDN_MC_SITES)

void SimulateData2s61(void)
{
/* This simulates two codon sequences and analyze using ML (GY94).
   It generates site pattern freqs and then samples from them
   to generate the seq data.  Codons are coded as 0,1,...,60.  There
   is another routine of a similar name in the file dsdn.c where the
   codons are coded as 0,1,...,63.  The two routines should not be
   mixed.
   Note that com.pi[] is changed in the analysis but not reused to 
   calculate Efij[]
   Ifdef (DSDN_MC_SITES), the data will be simulated with the NSsites models
   but analysed assuming one omega for all sites, so the model is wrong.
*/
   char infile[32]="in.codon2s", seqfile[32]="codonseq.tmp",str[4]="";
   FILE *fseq, *fin;
   int ir,nr=100, ip, i,j,k,h, n=Nsensecodon;
   int npatt0=n*(n+1)/2, nobs[NCODE*NCODE];
   int il,nil, ls[50]={0,200,500};
   double y, x[6]={1,1,1},xb[6][2], S,dN,dS,dNt,dSt,om,lnL, mr=0;
   double t0,kappa0,omega0=.5,pi0[NCODE], mx[6],vx[6],mse[6]; /* t,k,w,dS,dN */
   double Efij[NCODE*(NCODE+1)/2], space[50000];

   com.icode=0; com.seqtype=1; com.ns=2;
   com.ncode=n; com.cleandata=1; setmark_61_64 ();
   for(j=0; j<com.ns; j++)
      com.z[j] = (char*) malloc(npatt0*sizeof(char));
   if(com.z[com.ns-1]==NULL) error2("oom z");
   if((com.fpatt=(double*)malloc(npatt0*sizeof(double)))==NULL)
   error2("oom fpatt");
   for(j=0; j<3; j++) { xb[j][0]=.0001; xb[j][1]=99; }

#if (DSDN_MC_SITES)
   strcpy(infile,"in.codon2sSites");
#endif
   printf("\nTwo codon seq. simulation for ML (GY94), input from %s\n",infile);
   fin=gfopen(infile,"r");
   
   fscanf (fin,"%d%d%d%d", &k,&nr, &com.codonf,&nil);  SetSeed(k);
   printf("\n%d replicates, %s model for analysis\nLc:",
      nr,codonfreqs[com.codonf]);
   for(il=0; il<nil; il++) 
      fscanf(fin, "%d", &ls[il+1]);
   matIout(F0, ls+1, 1, nil);
   for(i=0,k=0; i<NCODE; i++) {
      fscanf(fin,"%lf",&y);
      if(GeneticCode[com.icode][i]>-1) pi0[k++]=y;
      else if(y!=0)
         error2("stop codon freq !=0");
   }
   printf("sum pi = 1 = %.6f\n", sum(pi0,n));

   for(ip=0; ip<99; ip++) {
      fscanf(fin, "%lf%lf", &t0,&kappa0);
      if(t0<0) exit(0);
      printf("\n\nParameter set %d\nt0 =%.2f  kappa0 =%.2f\n",ip+1,t0,kappa0);
      fprintf(frst,"\n\nParameter set %d\nt0 =%.2f  kappa0 =%.2f\n",ip+1,t0,kappa0);

      for(j=0; j<n; j++) com.pi[j] = pi0[j];
      com.ls=1;
#if (DSDN_MC_SITES)
      com.NSsites=3;
      fscanf(fin,"%d", &com.ncatG);
      for(i=0; i<com.ncatG; i++) fscanf(fin,"%lf", &com.freqK[i]);
      for(i=0; i<com.ncatG; i++) fscanf(fin,"%lf", &com.rK[i]);

      printf("\nSite classe model (K=%d)\np: ",com.ncatG);
      for(i=0; i<com.ncatG; i++)
         printf("%7.4f",com.freqK[i]);
      printf("\nw: "); FOR(i,com.ncatG) printf("%7.4f",com.rK[i]); FPN(F0);
      fprintf(frst,"\nSite classe model (K=%d)\np: ",com.ncatG);
      for(i=0; i<com.ncatG; i++)
         fprintf(frst,"%7.4f",com.freqK[i]);
      fputs("\nw: ",frst); FOR(i,com.ncatG) fprintf(frst,"%7.4f",com.rK[i]); FPN(frst);

      if(1-sum(com.freqK,com.ncatG))
         error2("freqs do not sum to 1");
      for(j=0,Qfactor_NS=0,dS=dN=0; j<com.ncatG; j++) {
         freqK_NS = com.freqK[j];
         EigenQcodon(1,1,&S,&dSt,&dNt,NULL,NULL,NULL, &mr, &kappa0,com.rK[j],PMat);
         dS += freqK_NS*dSt;
         dN += freqK_NS*dNt;
      }
      Qfactor_NS = 1/Qfactor_NS;
      om = (dS>0?dN/dS:-1);
      dS *= t0*Qfactor_NS;
      dN *= t0*Qfactor_NS;

#else
      fscanf(fin,"%lf", &omega0);
      EigenQcodon(1,t0,&S,&dS,&dN, NULL,NULL,NULL, &mr, &kappa0,omega0,space);
      om=omega0;
#endif
      printf("\nCorrect values"); 
      printf("\nS%%=%7.4f  dS=%7.4f  dN=%7.4f  w=%7.4f\n",S/3,dS,dN,om);
      fprintf(frst,"\nCorrect values");
      fprintf(frst,"\nS%%=%7.4f  dS=%7.4f  dN=%7.4f  w=%7.4f\n",S/3,dS,dN,om);
      
      /* calculate Efij[], the site pattern probabilities */
      FOR(j,n) com.pi[j]=pi0[j];
#if (DSDN_MC_SITES)
      com.NSsites=3;
      for(k=0,zero(Efij,npatt0); k<com.ncatG; k++) {
         EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr, &kappa0,com.rK[k],PMat);
         PMatUVRoot(PMat, t0, n, U, V, Root);
         for(i=0,h=0;i<n;i++) for(j=0;j<=i;j++) {
            y=com.pi[i]*PMat[i*n+j];
            Efij[h++] += (i==j?y:2*y) * com.freqK[k];
         }
      }
      com.NSsites=0;
#else
      EigenQcodon(0,-1,NULL,NULL,NULL,Root, U, V, &mr, &kappa0, omega0, PMat);
      PMatUVRoot (PMat, t0, n, U, V, Root);
      for(i=0,h=0;i<n;i++) for(j=0;j<=i;j++) { /* why for each il? */
         y=com.pi[i]*PMat[i*n+j];
         Efij[h++]=(i==j?y:2*y);
      }
#endif
      for(i=h=0,com.ls=1,com.npatt=npatt0;i<n;i++) for(j=0;j<=i;j++) {
         com.z[0][h]=(char)i; com.z[1][h]=(char)j;
         com.fpatt[h]=Efij[h];  h++;
      }
      if(fabs(1-sum(Efij,npatt0))>1e-6) error2("sum Efij != 1");

      for(il=0; il<nil+1; il++) {
         com.ls=ls[il];
         if(com.ls==0) {
            puts("\nML estimates from infinite data"); 
            com.ls=1;
            x[0]=t0*rndu(); x[1]=kappa0; x[2]=omega0*rndu();
            GetCodonFreqs2 ();
            ming2(NULL,&lnL,lfun2dSdN,NULL,x,xb, space,1e-10,3);
            printf("lnL = %.6f\n",-lnL);
            EigenQcodon(1,x[0],&S,&dS,&dN, NULL,NULL,NULL, &mr, &x[1],x[2],space);
            printf("S%%=%7.4f  dS=%7.4f  dN=%7.4f  w=%7.4f\n",S/3,dS,dN,x[2]);
            fprintf(frst,"ML estimates from infinite data\nt=%7.4f  k=%7.4f",x[0],x[1]);
            fprintf(frst,"  S%%=%7.4f  dS=%7.4f  dN=%7.4f  w=%7.4f\n",S/3,dS,dN,x[2]);

            for(h=1;h<npatt0; h++) Efij[h]+=Efij[h-1];
            puts("\nt & k & w & dS & dN");
            fputs("\nLc & t & k & w & dS & dN\n",frst);  fflush(frst);
            continue;
         }

         printf("\nls = %d\n", com.ls);
         for(ir=0,zero(mx,6),zero(vx,6),zero(mse,6); ir<nr; ir++) {
            MultiNomial(com.ls, npatt0, Efij, nobs, NULL);
            for(i=0,com.npatt=0,zero(com.pi,n);i<n;i++) for(j=0;j<=i;j++)
               if(nobs[k=i*(i+1)/2+j]) {
                  com.z[0][com.npatt]=i; com.z[1][com.npatt]=j;
                  com.fpatt[com.npatt++]=nobs[k];
               }
            for(i=0,zero(com.pi,n); i<com.npatt; i++) {
               com.pi[com.z[0][i]]+=com.fpatt[i]/(2.*com.ls);
               com.pi[com.z[1][i]]+=com.fpatt[i]/(2.*com.ls);
            }
            GetCodonFreqs2 ();

            x[0]=t0;  x[1]=kappa0; x[2]=omega0;
            /* printf("\nlnL=%9.6f\n",-lfun2dSdN(x,3)); */
            ming2((noisy?F0:NULL),&lnL,lfun2dSdN,NULL,x,xb, space,1e-7,3);
            EigenQcodon(1,x[0],&S,&x[3],&x[4], NULL,NULL,NULL, &mr, &x[1],x[2],space);
            FOR(j,5) {
               vx[j]+=(x[j]-mx[j])*(x[j]-mx[j]);
               mx[j]=(mx[j]*ir+x[j])/(ir+1.);
            }
            mse[0]+=square(x[2]-omega0);
            printf("\r%4d%8.4f%8.4f%8.4f  %8.4f%8.4f%8.4f%8.4f%8.4f",
                   ir+1,x[0],x[1],x[2],mx[0],mx[1],mx[2],mx[3],mx[4]);
#if 0
            if(ir==9) {
               fseq=gfopen(seqfile,"w");
               fprintf(fseq,"%6d %6d\n", com.ns,com.ls*3);
               for(i=0;i<2;i++,FPN(fseq),fflush(fseq)) {
                  fprintf(fseq,"seq.%-5d  ", i+1);
                  FOR(h,com.npatt) FOR(k,(int)com.fpatt[h]) 
                     fprintf(fseq,"%s", getcodon(str,FROM61[com.z[i][h]]));
               }
               fclose(fseq); exit(0);
           }
#endif
         }
         if(nr>1) { FOR(j,5) vx[j]=sqrt(vx[j]/(nr-1.)/nr); mse[0]=sqrt(mse[0]/nr); }
         fprintf(frst,"%4d ", com.ls);
         FOR(i,5) fprintf(frst,"%7.4f +%7.4f", mx[i],vx[i]);  FPN(frst);
      }  /* for (ii) */
   }   /* for(ip) */
   exit(0);
}


void Ina(void)
{
/* This simulates two codon sequences and analyze them using Ina's method.  
   Ina's program is modified to output result in Ina1.tmp.  Consistency
   analysis is done by generating long sequences.
   Note that com.pi[] is not changed in the analysis, which is done outside
   the program.  
*/
   char seqfile[32]="codonseq.tmp",tmpfile[32]="Ina1.tmp",str[4]="";
   FILE *fseq, *ftmp;
   int ip,ir,nr=500, i,j,k,h, n=Nsensecodon;
   int npatt0=n*(n+1)/2, nobs[NCODE*NCODE];
   int il,nil=1, ls[]={500,100,200,300,400,500,600,800,1000}, fcodon=1;
   double y, t=.5,f3x4[12], x[3]={1,1,1}, S,dS,dN, mr=0;
   double t0=1,kappa0=1,omega0=1, mx[6],vx[6],mse[6]; /* t,k,w,dS,dN */
   double Efij[NCODE*NCODE], space[50000];
   double f3x4_data[][3*4]={
                            {0.25, 0.25, 0.25, 0.25,
                             0.25, 0.25, 0.25, 0.25,
                             0.25, 0.25, 0.25, 0.25},

                            {0.20517, 0.28293, 0.30784, 0.20406, /* mt pri */
                             0.40979, 0.27911, 0.18995, 0.12116,
                             0.15105, 0.43290, 0.37123, 0.04482},

                            {0.19020, 0.16201, 0.36655, 0.28124, /* hiv */
                             0.28889, 0.18805, 0.30179, 0.22127,
                             0.24875, 0.16894, 0.36822, 0.21410},

                            {0.14568, 0.24519, 0.33827, 0.27086,
                             0.35556, 0.18765, 0.24049, 0.21630, 
                             0.26444, 0.25728, 0.21012, 0.26815} /* lysinNew*/
                           };

   puts("\nThis simulates data and analyses them using Ina95.");

printf ("fcodon? ");
scanf ("%d", &fcodon);

   FOR(j,12) f3x4[j]=f3x4_data[fcodon][j];
   for(j=0,h=0,y=0; j<64; j++) {
      if (GeneticCode[com.icode][j]==-1) continue;
      com.pi[h]=f3x4[j/16]*f3x4[4+(j%16)/4]*f3x4[8+j%4];
      y+=com.pi[h++];
   }
   FOR(j,n) com.pi[j]/=y;
   printf("fcodon: %d\n",fcodon);
   matout(frst,f3x4,3,4);
   com.icode=0; com.seqtype=1; com.ns=2; com.ls=1; npatt0=n*(n+1)/2;
   com.ncode=n; setmark_61_64 ();
   FOR(j,com.ns) com.z[j]=(char*) malloc(npatt0*sizeof(char));
   if(com.z[com.ns-1]==NULL) error2 ("oom z");
   if((com.fpatt=(double*)malloc(npatt0*sizeof(double)))==NULL)
      error2("oom fpatt");

   printf("\nInfinite sequences.\nsum pi=1=%.6f\n",sum(com.pi,NCODE));
   noisy=0;  FOR(i,6) x[i]=0;

   FOR(ip,99) {
      printf("\nt0 & kappa0 & omega0? ");
      scanf("%lf%lf%lf", &t0,&kappa0,&omega0);
      if(t0<0) exit(0);
      printf("t0 =%.2f & kappa0 =%.2f & omega0 =%.2f\n",t0,kappa0,omega0);
      fprintf(frst, "\nt & k & w: %8.2f%8.2f%8.2f\n\n", t0,kappa0,omega0);
      EigenQcodon(1,t0,&S,&dS,&dN, NULL,NULL,NULL, &mr, &kappa0,omega0,space); 
      fprintf(frst,"\nS/(S+N)=%7.4f  dS=%7.4f  dN=%7.4f\n",S/3,dS,dN);
      fputs("Lc & t & k & w & dS & dN\n",frst);
   
      EigenQcodon(0,-1,NULL,NULL,NULL,Root, U, V, &mr, &kappa0, omega0, PMat);
      PMatUVRoot (PMat, t0, n, U, V, Root);
      for(i=0,h=0;i<n;i++) for(j=0;j<=i;j++) {
         y=com.pi[i]*PMat[i*n+j];
         Efij[h++]=(i==j?y:2*y);
      }
      for(i=h=0,com.ls=1,com.npatt=npatt0;i<n;i++) for(j=0;j<=i;j++) {
         com.z[0][h]=(char)i; com.z[1][h]=(char)j;
         com.fpatt[h]=Efij[h];  h++;
      }
      for(h=1;h<npatt0; h++) Efij[h]+=Efij[h-1];
      if(fabs(1-Efij[npatt0-1])>1e-6) puts("Sum p_ij != 1.");
      for(il=0; il<nil; il++) {
   
         com.ls=ls[il];
         printf("\nls = %d\n", com.ls);
         for(ir=0,zero(mx,6),zero(vx,6),zero(mse,6); ir<nr; ir++) {
            printf("\r%4d", ir+1);
            MultiNomial (com.ls, npatt0, Efij, nobs, NULL);
            for(i=0,com.npatt=0;i<n;i++) for(j=0;j<=i;j++)
               if(nobs[k=i*(i+1)/2+j]) {
                  com.z[0][com.npatt]=i; com.z[1][com.npatt]=j; 
                  com.fpatt[com.npatt++]=nobs[k];
               }
            fseq=gfopen(seqfile,"w");
            fprintf(fseq,"> %6d %6d\n", com.ns,com.ls*3);
            for(i=0;i<2;i++,FPN(fseq),fflush(fseq)) {
               fprintf(fseq,"seq.%-5d  ", i+1);
               FOR(h,com.npatt) FOR(k,(int)com.fpatt[h]) 
                  fprintf(fseq,"%s", getcodon(str,FROM61[com.z[i][h]]));
            }
            fclose(fseq);
            if(com.ls>2000) system("Ina1Large codonseq.tmp >t");
            else            system("Ina1 codonseq.tmp >t");
            ftmp=gfopen(tmpfile,"r");
            if(fscanf(ftmp,"%lf%lf%lf",&x[0],&x[1],&x[2]) !=3) 
               error2("reading tmpf");
            fclose(ftmp);
            FOR(j,5) {
               vx[j]+=(x[j]-mx[j])*(x[j]-mx[j]);
               mx[j]=(mx[j]*ir+x[j])/(ir+1.);
            }
            mse[0]+=square(x[0]-omega0);

            printf("%7.4f%7.4f%7.4f  %7.4f%7.4f%7.4f%7.4f%7.4f",
                   x[0],x[1],x[2],mx[0],mx[1],mx[2],mx[3],mx[4]);

/*            fprintf(frst1,"%7.4f%7.4f%7.4f  %7.4f%7.4f%7.4f%7.4f%7.4f\n",
                   x[0],x[1],x[2],mx[0],mx[1],mx[2],mx[3],mx[4]);
*/
         }
         if(nr>1) { FOR(j,5) vx[j]=sqrt(vx[j]/(nr-1.)/nr); mse[0]=sqrt(mse[0]/nr); }
         fprintf(frst,"%4d ", com.ls);
         FOR(i,5) fprintf(frst,"%7.3f +%7.4f", mx[i],vx[i]);
         FPN(frst); fflush(frst);

         fprintf(frst1,"%6d%6d %7.2f%7.2f%7.2f: %8.3f +%7.3f\n",
             com.ls,nr, t0,kappa0,omega0, mx[0],mse[0]);  
         fflush(frst1);
      }    /* for (il) */
   }       /* for (ip) */
   exit(0);
}

#endif

#if 0

int mergeSeqs(FILE*fout)
{
/* This concatenate multiple genes (data sets) for the same set of species
   into one file of a long gene.  Used to process Anne Yoders' alignment.
*/

   char *filenames[12]={"NADH1.fin","NADH2.fin","COI.fin","COII.fin","ATPase8.fin",
        "ATPase6.fin","COIII.fin","NADH3.fin","NADH4L.fin","NADH4.fin",
        "NADH5.fin", "Cytb.fin"};

   int ns0=32, nfile=12, ifile, ls0, lswhole=20000, i,h, lgene0[32];
   char *z0[32], *spname0[32]={"Artibeus", "B.musculus", "B.physalus", "Bos", 
      "Canis", "Cavia", "Ceratother", "Dasypus", "Didelphis", "E.asinus", 
      "E.caballus","Erinaceus", "Felis", "Glis", "Gorilla", "Halichoeru", "Homo",
      "Hylobates", "Macropus", "Mus", "Ornithorhy", "Oryctolagu", "Ovis",
      "P.paniscus", "P.troglody", "Papio", "Phoca", "P.abelii",
      "P.pygmaeus", "Rattus", "Rhinoceros", "Sus"};
   FILE *fseq;

   noisy=0;
   FOR(i,ns0) if((z0[i]=(char*)malloc(lswhole*sizeof(char)))==NULL) 
      error2("oom z");
   for(ifile=0,ls0=0; ifile<nfile; ifile++) {
      printf("Reading data set %2d/%2d (%s)", ifile+1,nfile,filenames[ifile]);
      fseq=gfopen (filenames[ifile],"r");
      ReadSeq(NULL,fseq,1);
      lgene0[ifile]=com.ls;  com.ls*=3;
      FOR(i,ns0) if(strcmp(spname0[i],com.spname[i])) error2("spname different"); 
      FOR(i,ns0)  FOR(h,com.ls) z0[i][ls0+h]=com.z[i][h];
      ls0+=com.ls;
      printf(" + %5d = %5d\n", com.ls, ls0);
   }
   fprintf(fout,"%6d %6d  G\nG %4d ", ns0,ls0,nfile);
   FOR(ifile,nfile) fprintf(fout, " %4d", lgene0[ifile]);  FPN(fout);

   for(i=0;i<ns0;i++,FPN(fout)) {
      fprintf(fout,"%-12s  ", spname0[i]);
      FOR(h,ls0) {
         fprintf(fout,"%c", z0[i][h]);
         if((h+1)%3==0) fprintf(fout," ");
      }
   }
   return(0);
}

#endif


int SlidingWindow(FILE*fout, FILE* fpair[], double space[])
{
/* sliding window analysis, clean data, 2 sequences only */
   int wlen=windowsize0, offset=offset0, wstart, n=com.ncode, j, h, positive=0;
   int ls0=com.ls, npatt0=com.npatt;
   char *z0[NS];
   double *fpatt0, pi0[NCODE], lnL0=0, lnL1=0;

   if(com.seqtype!=1) error2("implemented for codon sequences only.");
   if(com.runmode!=-2) error2("this version of sliding windows requires runmode=-2");
   if(!com.cleandata || com.ngene>1)
      error2("clean data & one gene only for sliding window analysis");   
   if(com.print)
      error2("Choose RateAncestor=0 for sliding window analysis");   
   for(j=0; j<com.ns; j++) 
      z0[j] = com.z[j];
   for(j=0; j<com.ns; j++) 
      if((com.z[j]=malloc(npatt0*sizeof(char)))==NULL) error2("oom z");
   if((fpatt0=(double*)malloc(npatt0*sizeof(double)))==NULL) error2("oom fp");
   for(h=0; h<com.npatt; h++) 
      fpatt0[h] = com.fpatt[h];
   for(j=0; j<n; j++) 
      pi0[j] = com.pi[j];

   for (wstart=0; wstart+wlen<=ls0; wstart+=offset) {
      for(h=0; h<npatt0; h++) 
         com.fpatt[h] = 0;
      for(h=wstart; h<wstart+wlen; h++)
         com.fpatt[com.pose[h]]++;

      for(h=0,com.npatt=0,zero(com.pi,n); h<npatt0;h++) if(com.fpatt[h]>0) {
         for(j=0; j<com.ns; j++)
            com.z[j][com.npatt] = z0[j][h];
         com.fpatt[com.npatt] = com.fpatt[h];
         com.npatt++;
      }
      com.ls = wlen;  
      com.posG[0] = 0; com.posG[1] = com.npatt;

      com.fix_omega = 1; com.omega = 1;
      PairwiseCodon(fout,fpair[3],fpair[4],fpair[5],com.space);
      lnL0 = -lnLmodel; /* lnLmodel passed overhead from PairwiseCodon() */

      com.fix_omega = 0; com.omega = 0.5;
      PairwiseCodon(fout,fpair[3],fpair[4],fpair[5],com.space);
      lnL1 = -lnLmodel;
      
      if(com.omega>1 && (lnL1-lnL0)>2.71/2) {
         positive = 1;
         break;
      }
      
      if(noisy) 
         printf("sites %3d -- %3d  (%d) npatt:%4d w=%.4f\n",wstart+1,wstart+wlen,ls0,com.npatt, com.omega);
      fprintf(fout,"\nsites %3d -- %3d  %4d",wstart+1,wstart+wlen,com.npatt);

      /* Forestry(fout); */
   }
   fprintf(frst1, " %2d", positive);
   printf("     %2d", positive);

   com.ls = ls0;  com.posG[1] = com.npatt = npatt0;
   for(h=0; h<com.npatt; h++) 
      com.fpatt[h] = fpatt0[h];
   xtoy(pi0, com.pi, n);
   free(fpatt0);
   for(j=0; j<com.ns; j++) { 
      free(com.z[j]); 
      com.z[j] = z0[j]; 
   }
   return(positive);
}



void Get4foldSites(void)
{
/* This collects the four-fold degerate sites into a file named 4fold.nuc.
   The data are not coded yet, and the routine is called from ReadSeq().
*/
   int ls4, j,k,h, ib[3][4], nb[3];
   char file4[12]="4fold.nuc", *mark4;
   FILE *f4;

   f4=gfopen(file4,"w");
   if ((mark4=(char*)malloc(com.ls*sizeof(char)))==NULL) error2("oom mark");
   FOR(h,com.ls) mark4[h]=0;

   for (h=0,ls4=0; h<com.ls; h++) {
      for(k=0; k<3; k++)
			NucListall(com.z[0][h*3+k], &nb[k], ib[k]);
      if(nb[0]==1 && nb[2]==1 && FourFold[ib[0][0]][ib[1][0]]) {
         for(j=1; j<com.ns; j++)
            for(k=0; k<2; k++) if(com.z[j][h*3+k]!=com.z[0][h*3+k]) goto nextsite;
         mark4[h]=1;  ls4++;
      }
      nextsite: ;
   }     /* for(h) */

   fprintf (f4, "%6d  %6d\n", com.ns, ls4);
   for (j=0; j<com.ns; j++) {
      fprintf (f4, "\n%s\n", com.spname[j]);
      for (h=0; h<com.ls; h++)
         if(mark4[h]) fprintf (f4, "%c", com.z[j][h*3+2]);
      FPN (f4);
   }
   fprintf(f4, "\n\ncodons included\n");
   for(h=0; h<com.ls; h++)
		if(mark4[h]) fprintf(f4, " %2d", h+1);
	FPN(f4);

   fclose(f4);  free(mark4);
}


double distanceHKY85 (double x[], double *kappa, double alpha);

void d4dSdN(FILE* fout)
{
/* This looks at the 4-fold degerenate sites.
*/
   char str1[4]="   ", str2[4]="   ";
   int i,j,k, n=com.ncode, b[2][3], ic1,ic2,iaa;
   double pS4,d4,kappa4fold;
   double fij, fij4f[4*4], pi4f[4], pstop,t, S,dS,dN,dN_dS, mr=0;
   double fb3x4[12]={.25, .25, .25, .25, 
                     .25, .25, .25, .25, 
                     .25, .25, .25, .25};

   int nii=18, ii;
   double t0[]={0.001, 0.01,0.05, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1, 1.2, 1.5, 2,2.5,3};


   com.ls=1; com.kappa=3; com.omega=1;

   fb3x4[0*4+0]=0.35;
   fb3x4[0*4+1]=0.15;
   fb3x4[0*4+2]=0.35;
   fb3x4[0*4+3]=0.15;
/*
   fb3x4[1*4+0]=0.35;  
   fb3x4[1*4+1]=0.15;
   fb3x4[1*4+2]=0.35;
   fb3x4[1*4+3]=0.15;
*/
   fb3x4[2*4+0]=0.35;  
   fb3x4[2*4+1]=0.15;
   fb3x4[2*4+2]=0.35;
   fb3x4[2*4+3]=0.15;


printf("\tt\tS\tdS\tdN\tdN/dS\tS4\td4\tk_4f\tpT_4f\n");

   zero(com.pi,64);
   FOR(k,64)  if(FROM64[k]>-1)
      com.pi[FROM64[k]]=fb3x4[k/16]*fb3x4[4+(k/4)%4]*fb3x4[8+k%4];
   pstop=1-sum(com.pi,n);
   abyx(1/(1-pstop),com.pi,n);

   EigenQcodon(0,-1,NULL,NULL,NULL,Root,U,V, &mr, &com.kappa,com.omega,PMat);

matout(frst,com.pi,16,4);

   FOR(ii,nii) {
      t=t0[ii];
      EigenQcodon(1,t,&S,&dS,&dN,NULL,NULL,NULL, &mr, &com.kappa,com.omega,PMat);
      PMatUVRoot (PMat, t, n, U, V, Root);
      if(testTransP(PMat,n)) error2("testP");

matout(frst,PMat,n,n);

      for(i=0,zero(fij4f,16);i<n;i++) {
         ic1=FROM61[i]; b[0][0]=ic1/16; b[0][1]=(ic1/4)%4; b[0][2]=ic1%4;
         iaa=GeneticCode[com.icode][ic1];
         ic1-=b[0][2];
         FOR(k,4)  if(GeneticCode[com.icode][ic1+k]!=iaa)  break;
         if(k<4) continue;
         FOR(j,n) {
            fij=com.pi[i]*PMat[i*n+j];
            ic2=FROM61[j]; b[1][0]=ic2/16; b[1][1]=(ic2/4)%4; b[1][2]=ic2%4;

            if(b[0][0]!=b[1][0] || b[0][1]!=b[1][1]) continue;
            fij4f[b[0][2]*4+b[1][2]] += fij;

/* printf("%c %s %s  %.8f\n",AAs[iaa],getcodon(str1,ic1+b[0][2]),getcodon(str2,ic2),fij);
*/

         }
      }

      pS4=sum(fij4f,16)/3;
      abyx(1/sum(fij4f,16),fij4f,16);
      FOR(k,4) pi4f[k]=sum(fij4f+k*4,4);

/* matout(F0,fij4f,4,4); */

      d4 = distanceHKY85 (fij4f, &kappa4fold, 0);
      dN_dS = (dS>0 ? dN/dS : -1);
printf("\t%.4f\t%.5f\t%.5f\t%.5f\t%.5f\t%.3f\t%.5f\t%.3f\t%.4f\n", 
       t,S/3,dS,dN,dN_dS, pS4,d4,kappa4fold,pi4f[0]);

   }

printf("\nproportion of stop codons: %.4f\n", pstop);

   exit(0);
}


double distanceHKY85 (double x[], double *kappa, double alpha)
{
/* This is from SeqDivergence(), copied here to avoid linking to SeqDivergence.
*/
   int i,j;
   double p[4], Y,R, a1,a2,b, P1,P2,Q,tc,ag;
   double largek=999, larged=9;

   if (testXMat(x) && noisy) {
      matout(F0,x,4,4);
      puts("X err..  Perhaps no sites to compare?");
   }
   *kappa=0;
   for (i=0,zero(p,4); i<4; i++) {
      FOR (j,4) { p[i]+=x[i*4+j]/2;  p[j]+=x[i*4+j]/2; }
   }
   P1=x[0*4+1]+x[1*4+0];
   P2=x[2*4+3]+x[3*4+2];
   Q = x[0*4+2]+x[0*4+3]+x[1*4+2]+x[1*4+3]+ x[2*4+0]+x[2*4+1]+x[3*4+0]+x[3*4+1];
   Y=p[0]+p[1];
   R=p[2]+p[3];

   if(P1+P2+Q<1e-100) {
      *kappa=-1; return(0);
   }

   tc=p[0]*p[1]; 
   ag=p[2]*p[3];

   a1=1-Y*P1/(2*tc)-Q/(2*Y);
   a2=1-R*P2/(2*ag)-Q/(2*R);
   b=1-Q/(2*Y*R);
   if (a1<=0 || a2<=0 || b<=0) return (larged);
   if (alpha<=0) { a1=-log(a1); a2=-log(a2); b=-log(b); }
   else   { a1=-gammap(a1,alpha); a2=-gammap(a2,alpha); b=-gammap(b,alpha);}
   a1 = -R/Y*b + a1/Y;
   a2 = -Y/R*b + a2/R;
   if (b>0) *kappa = min2((a1+a2)/(2*b), largek);
   return 2*(p[0]*p[1] + p[2]*p[3])*(a1+a2)/2 + 2*Y*R*b;
}




void get_pclassM_iw_M2M8(int *iw, double *pclassM, 
                         int iclassM, int ip[], double para[4][100], int n1d, int M2a, int ternary);
void get_grid_para_like_M2M8(double para[4][100], int n1d, int dim, int M2a, int ternary, 
                        double p0b[], double p1b[], double w0b[], double wsb[], 
                        double p_beta_b[], double q_beta_b[], double x[], double *S);
void GetIndexTernary(int *ix, int *iy, double *x, double *y, int itriangle, int K);



void get_grid_para_like_M2M8 (double para[4][100], int n1d, int dim, int M2a, int ternary,
     double p0b[], double p1b[], double w0b[], double wsb[],
     double p_beta_b[], double q_beta_b[], double x[], double *S)
{
/* This sets up the grid (para[][]) according to the priors.  It also copies all
   possible w values into com.rK[].
   The bounds on parameters are used to set up the uniform priors for parameters.  
*/
   int i,k,h, site=10;
   double fh;

   if(com.NSsites==NSbetaw)  /* can't control the range of w from the beta */
      { w0b[0]=0; w0b[1]=1; }

   for(i=0; i<n1d; i++) {
      para[0][i] = p0b[0]+(i+0.5)*(p0b[1]-p0b[0])/n1d;                   /* p0 */
      if(com.NSsites==2) {  /* M2 & M2a */
         para[1][i] = p1b[0]+(i+0.5)*(p1b[1]-p1b[0])/n1d;                /* p1 */
         if(ternary) para[0][i] = para[1][i] = -1;
         if(M2a) 
            para[2][i] = w0b[0]+(i+0.5)*(w0b[1]-w0b[0])/n1d;             /* w0 */
         para[2+M2a][i] = wsb[0]+(i+0.5)*(wsb[1]-wsb[0])/n1d;            /* w2 */
      }
      else {                 /* M8 */
         para[1][i] = p_beta_b[0]+(i+0.5)*(p_beta_b[1]-p_beta_b[0])/n1d; /* p */
         para[2][i] = q_beta_b[0]+(i+0.5)*(q_beta_b[1]-q_beta_b[0])/n1d; /* q */
         para[3][i] = wsb[0]+(i+0.5)*(wsb[1]-wsb[0])/n1d;                /* ws */
      }
   }

   k=0;
   if(com.NSsites==2 && M2a==0)
       com.rK[k++]=0;
   else   /* w0 in M2a or w0 from beta in M8 */
       for(i=0; i<n1d; i++)
          com.rK[k++] = w0b[0]+(i+0.5)*(w0b[1]-w0b[0])/n1d;
   if(com.NSsites==2)
      com.rK[k++]=1;  /* w1 for M2 & M2a */
   for(i=0; i<n1d; i++)
      com.rK[k++] = wsb[0]+(i+0.5)*(wsb[1]-wsb[0])/n1d; /* w2 in M2 or ws */

   /* calculates the likelihood com.fhK[] */
   printf("\nCalculating f(x_h|w): %d categories %d w sets.\n", n1d, com.ncatG);
   com.conPSiteClass=0;  *S=0;
   fx_r(x,-1);

   if(noisy>3)
      for(k=0; k<com.ncatG; k++)
         printf("S%d w log{f(x|w)}: %9.4f  %12.6f\n", 
            site,com.rK[k], (com.NnodeScale?com.fhK[k*com.npatt+site]:log(com.fhK[k*com.npatt+site])));
   
   if(com.NnodeScale)
      for(h=0; h<com.npatt; h++) {
         for(k=1,fh=com.fhK[h]; k<com.ncatG; k++)
            fh = max2(fh,com.fhK[k*com.npatt+h]);
         for(k=0; k<com.ncatG; k++) 
            com.fhK[k*com.npatt+h] = exp(com.fhK[k*com.npatt+h]-fh);
         *S += fh*com.fpatt[h];
      }
   else 
      for(h=0; h<com.npatt; h++) {
         for(k=1,fh=com.fhK[h]; k<com.ncatG; k++)
            fh = max2(fh,com.fhK[k*com.npatt+h]);
         for(k=0; k<com.ncatG; k++) 
            com.fhK[k*com.npatt+h] /= fh;
         *S += log(fh)*com.fpatt[h];
      }

}


void get_pclassM_iw_M2M8(int *iw, double *pclassM, 
     int iclassM, int ip[], double para[][100], int n1d, int M2a, int ternary)
{
/* Given the point on the grid (ip[]), this returns iw and pclassM, where iw 
   locates the w ratio in com.rK[] and f(x_h|w) stored in com.fhK[], 
   and pclassM is the proportion of the site class under the model.
   Look at get_grid_para_like() for more info about the setup of com.rK[], which 
   accounts for the setup of iw here in this function.

   M8 used to use 10 categories to approximate the beta, each of probability 
   10%.  Here we use n1d categories, equally spaced, and the 
   probabilities for categories are calculated using CDFBeta.  

   Parameters for grid integration:

                   Parameters         Parameter dependence
      Model     0    1    2    3          iw            pclassM
   -------------------------------------------------------------------
      M2       p0   p1   w2          iclassM w0 w2     iclassM p0 p1
      M2a      p0   p1   w0   w2     iclassM w2        iclassM p0 p1
      M8       p0    p    q   ws     iclassM p q ws    iclassM p0 p q
   -------------------------------------------------------------------

   If M2 or M2a and ternary, the n1d*n1d grid for p0-p1 is mapped onto the 
   triangle specified by p0-p1-p2.  First the index i and j are retrieved 
   from the label for the point (ip[0]*n1d+ip[1]).  Then the coordinates 
   p0 and p1 at the point is worked out.  With this scheme, p0 and p1 each 
   takes on 2*n1d-1 possible values.
*/
   int i,j;
   double p0,p1, p,q, cdf0=0,cdf1=1;

   if(com.NSsites==NSpselection) {    /* M2 & M2a */
      if(ternary) {
         GetIndexTernary(&i, &j, &p0, &p1, ip[0]*n1d+ip[1], n1d);
         *pclassM = (iclassM==0 ? p0 : (iclassM==1 ? p1 : 1-p0-p1));
      }
      else {
         if(iclassM<2) *pclassM = para[iclassM][ip[iclassM]];  /* p0 or p1 */
         else          *pclassM = 1-para[0][ip[0]]-para[1][ip[1]];   /* p2 */
         *pclassM = max2(*pclassM,0);
      }

      if(M2a==0) {     /*M2 */
         if(iclassM<2) *iw = iclassM;           /* w0 or w1 */
         else          *iw = 2+ip[2];           /* w2 */
      }
      else {  /* M2a */
         if(iclassM==0)      *iw = ip[2];       /* w0 */
         else if(iclassM==1) *iw = n1d;         /* w1 */
         else                *iw = n1d+1+ip[3]; /* w2 */
      }
   }
   else {   /* M8 */
      p0 = para[0][ip[0]];
      if(iclassM<n1d) {  /* w from beta */
         p = para[1][ip[1]];
         q = para[2][ip[2]];
         if(iclassM>0)     cdf0 = CDFBeta(iclassM/(double)n1d, p, q, 0);
         if(iclassM<n1d-1) cdf1 = CDFBeta((iclassM+1.0)/n1d, p, q, 0);
         *pclassM = p0*(cdf1-cdf0);
         *iw = iclassM;
      }
      else {             /* ws */
         *pclassM = 1-p0;
         *iw = n1d+ip[3];
      }
   }
}



int lfunNSsites_M2M8 (FILE* frst, double x[], int np)
{
/* Bayes empirical Bayes (BEB) correction for the posterior of w for each site 
   under M2 or M8.  The integral is 3-d for M2, and 4-d for M2a or M8, 
   approximated using n1d=10 categories in each dimension.  The ngrid=n1d^dim
   points make up the grid.

   com.ncatG is the number of all possible w's ever needed.  They are copied 
   into com.rK[], to be used to calculate f(x_h|w), stored in com.fhK[], before
   entering the grid of 4-d integration.  iw[ngrid*nclassM] identifies the 
   position of w in com.rK[], and pclassM[ngrid*nclassM] is the proportion 
   of sites under the model.  Those are set up in get_pclassM_iw().

   The priors are set up in get_grid_para_like().  See notes there.
   Some control variables:  
      M2a=1 for M2a=0 for M2.
      ternary=1: use ternary triangles to specify prior for p0-p1 under M2 or M2a
             =0: break p0 and p1 into 10 bins and skip the unfeasible points

   Parameters and their priors are as follows:
      M2 (p0 p1 w2)   : p0,p1~U(0,1),              w2~U(1,11)
      M2a(p0 p1 w0 w2): p0,p1~U(0,1), w0~U(0,1),   w2~U(1,11)
      M8 (p0 p  q  ws): p0~U(0,1),    p,q~U(0,2),  ws~U(1,11)

   Ziheng, Copenhagen, 17 May 2004.
*/
   int n1d=10, M2a=1, ternary=1, trianglePriorM8=0;
   double p0b[]={0,1}, p1b[]={0,1}, w0b[]={0,1};  /* w0b for M2a only. */
   double wsb[]={1,11};           /* for w2 in M2 & M2a, or for ws in M8 */
   double p_beta_b[]={0,2}, q_beta_b[]={0,2};

   int dim=(com.NSsites==8||M2a?4:3), ngrid,igrid, ip[4]={0}, j,k,h, it;
   int refsp=0, ncatG0=com.ncatG;
   /* # of site classes under model and index for site class */
   int nclassM = (com.NSsites==NSpselection?3:n1d+1), iclassM, *iw;
   double para[4][100]={{0}}, postpara[4][100];  /* paras on grid for 4-d integral: n1d<=100! */
   /* lnfXs is log of term in equation 5 in YWN05, which sums over those terms. */
   double fh, fX, *lnfXs,S1,S2, *lnprior, *pclassM, *meanw, *varw, *postSite, *postp0p1=NULL;
   double fh1site, t,v;
   char timestr[32], *paras[4];

   printf("\nBEBing (dim = %d).  This may take several minutes.", dim);

   if(com.NSsites==8) { paras[0]="p0"; paras[1]="p"; paras[2]="q"; paras[3]="ws"; }
   else if(!M2a)      { paras[0]="p0"; paras[1]="p1";  paras[2]="w2"; }
   else               { paras[0]="p0"; paras[1]="p1";  paras[2]="w0"; paras[3]="w2"; }

   ngrid=n1d*n1d*n1d*(dim==4?n1d:1);
   if(com.NSsites==8) com.ncatG = n1d+n1d;  /* w from beta & ws */
   else               com.ncatG = (M2a ? n1d+1+n1d : 2+n1d);  /* w0, w1=1, w2 */
   if((meanw=(double*)malloc(com.npatt*(2+nclassM)*sizeof(double)))==NULL)
      error2("oom meanw");
   varw=meanw+com.npatt;  postSite=varw+com.npatt;
   ternary=(com.NSsites==2 && ternary);

   if(ternary && (postp0p1=(double*)malloc(n1d*n1d*sizeof(double)))==NULL)
      error2("oom postp0p1");
   if((lnfXs=(double*)malloc(ngrid*sizeof(double)))==NULL)
      error2("oom lnfXs");
   if((pclassM=(double*)malloc(ngrid*nclassM*(sizeof(double)+sizeof(int))))==NULL)
      error2("oom pclassM");  /* this wastes space */
   iw = (int*)(pclassM+ngrid*nclassM);
   if((lnprior=(double*)malloc(n1d*n1d*sizeof(double)))==NULL)
      error2("oom lnprior");  /* this wastes space */

   k=com.npatt*com.ncatG*sizeof(double);
   if((com.fhK=(double*)realloc(com.fhK,k))==NULL) error2("oom fhK");

   for(j=0; j<n1d*n1d; j++) lnprior[j]=0;
   if(com.NSsites==8 && trianglePriorM8) {
      /* for(j=0; j<n1d; j++) lnprior[j]=(2-1./n1d-j*2./n1d)/n1d; */
      for(j=0; j<n1d; j++) lnprior[j]=(2*j+1.)/(n1d*n1d);
      printf("triangular prior for p0 under M8\n");
      for(j=0; j<n1d; j++) printf("%9.4f", (2*j+1.)/(2*n1d));  FPN(F0);
      for(j=0; j<n1d; j++) printf("%9.4f", lnprior[j]);  FPN(F0);
   }

   BayesEB=1;
   get_grid_para_like_M2M8(para, n1d, dim, M2a, ternary, p0b, p1b, w0b, wsb, p_beta_b, q_beta_b, x, &S1);

   /* Set up im and pclassM, for each igrid and iclassM. */
   for(igrid=0; igrid<ngrid; igrid++) {
      for(j=dim-1,it=igrid; j>=0; j--) { ip[j]=it%n1d; it/=n1d; }
      if(com.NSsites==2 && !ternary && para[0][ip[0]]+para[1][ip[1]]>1) continue;
      for(k=0; k<nclassM; k++) {
         get_pclassM_iw_M2M8(&iw[igrid*nclassM+k], &pclassM[igrid*nclassM+k],k,ip,para,n1d,M2a,ternary);
      }
   }

   /* calculate log{fX}, where fX is the marginal probability of data,
      and posterior of parameters postpara[].  S2 is the scale factor. */
   printf("Calculating f(X), the marginal probability of data.\n");
   fX=1;  S2=-1e300;
   FOR(j,dim) FOR(k,n1d) postpara[j][k]=1;
   if(ternary) FOR(k,n1d*n1d) postp0p1[k]=1;
   for(igrid=0; igrid<ngrid; igrid++) {
      for(j=dim-1,it=igrid; j>=0; j--) { ip[j]=it%n1d; it/=n1d; }
      if(com.NSsites==2 && !ternary && para[0][ip[0]]+para[1][ip[1]]>1) 
         continue;
      for(h=0,lnfXs[igrid]=0; h<com.npatt; h++) {
         for(k=0,fh=0; k<nclassM; k++)
            fh += pclassM[igrid*nclassM+k]*com.fhK[iw[igrid*nclassM+k]*com.npatt+h];

         if(fh<1e-300) {
            printf("strange: f[%3d] = %12.6g very small.\n",h,fh);
            continue;
         }

         lnfXs[igrid] += log(fh)*com.fpatt[h];
      }
      lnfXs[igrid] += (com.NSsites==8 ? lnprior[ip[0]] : lnprior[ip[0]*n1d+ip[1]]);
      t=lnfXs[igrid]-S2;
      if(t>0) {    /* change scale factor S2 */
         t = (t<200 ? exp(-t) : 0);
         fX=fX*t+1;
         FOR(j,dim) FOR(k,n1d)
            postpara[j][k] *= t;
         FOR(j,dim)
            postpara[j][ip[j]] ++;

         if(ternary) {
            FOR(k,n1d*n1d) postp0p1[k] *= t;
            postp0p1[ip[0]*n1d+ip[1]] ++;
         }

         S2 = lnfXs[igrid];
      }
      else if(t>-200) {
         t = exp(t);
         fX += t;
         for(j=0; j<dim; j++)
            postpara[j][ip[j]] += t;
         if(ternary) postp0p1[ip[0]*n1d+ip[1]] += t;
      }
   }
   for(j=0; j<dim; j++)
      for(k=0; k<n1d; k++)
         postpara[j][k]/=fX;
   if(ternary) 
      for(k=0; k<n1d*n1d; k++) 
         postp0p1[k] /=fX;

   fX = log(fX)+S2;
   printf("\tlog(fX) = %12.6f  S = %12.6f %12.6f\n", fX+S1-dim*log(n1d*1.),S1,S2);

   /* calculate posterior probabilities and mean w for each site pattern.
      S1 and S2 are scale factors for probabilities and for w. */
   printf("Calculating f(w|X), posterior probabilities of site classes.\n");
   for(h=0; h<com.npatt; h++) {
      S1=-1e300;  FOR(j,nclassM) postSite[j*com.npatt+h]=1;
      S2=-1e300;  meanw[h]=varw[h]=1;
      for(iclassM=0; iclassM<nclassM; iclassM++) {
         for(igrid=0; igrid<ngrid; igrid++) {
            for(j=dim-1,it=igrid; j>=0; j--) { ip[j]=it%n1d; it/=n1d; }
            if(com.NSsites==2 && !ternary && para[0][ip[0]]+para[1][ip[1]]>1) 
               continue;

            for(k=0,fh=0; k<nclassM; k++) /* duplicated calculation */
               fh += pclassM[igrid*nclassM+k]*com.fhK[iw[igrid*nclassM+k]*com.npatt+h];

            it = igrid*nclassM+iclassM;
            fh1site = pclassM[it]*com.fhK[iw[it]*com.npatt+h];

            if(fh1site<1e-300) continue;

            fh1site /= fh;
            t = log(fh1site)+lnfXs[igrid]; /* t is log of term on grid */
            if(t>S1) {  /* change scale factor S1 */
               for(j=0; j<nclassM; j++) 
                  postSite[j*com.npatt+h] = postSite[j*com.npatt+h]*exp(S1-t);
               S1 = t;
            }
            postSite[iclassM*com.npatt+h] += exp(t-S1);

            t = fh1site*com.rK[iw[it]];
            v = fh1site*square(com.rK[iw[it]]);
            if(t<1e-300) continue;
            t = log(t)+lnfXs[igrid]; /* t is log of mean */
            v = log(v)+lnfXs[igrid];
            if(t>S2) {  /* change scale factor S2 */
               meanw[h] = meanw[h]*exp(S2-t);
               varw[h]  = varw[h]*exp(S2-t);
               S2 = t;
            }
            meanw[h] += exp(t-S2);
            varw[h]  += exp(v-S2);
         }
      }

      for(j=0; j<nclassM; j++) 
         postSite[j*com.npatt+h] *= exp(S1-fX);
      meanw[h] *= exp(S2-fX);
      varw[h]  *= exp(S2-fX);
      varw[h] -= meanw[h]*meanw[h];
      varw[h] = (varw[h]>0?sqrt(varw[h]):0);

      if((h+1)%10==0 || h==com.npatt-1)
         printf("\r\tdid %3d / %3d patterns  %s", h+1,com.npatt,printtime(timestr));
   }  /* for(h) */

   /* print out posterior probabilities */
   fprintf(frst,"\nBayes Empirical Bayes (BEB) probabilities for %d classes (class)", nclassM);
   fprintf(fout,"\nBayes Empirical Bayes (BEB) analysis");
   fprintf(fout," (Yang, Wong & Nielsen 2005. Mol. Biol. Evol. 22:1107-1118)");

   com.ncatG = ncatG0;
   PrintProbNSsites(frst, postSite, meanw, varw, nclassM, refsp);

   fprintf(fout, "\n\nThe grid %s\n\n", (ternary?"(see ternary graph for p0-p1)":""));
   for(j=(ternary?2:0); j<dim; j++,FPN(fout)) {
      fprintf(fout, "%-2s: ", paras[j]);
      for(k=0; k<n1d; k++)
         fprintf(fout, " %6.3f", para[j][k]);
   }
   if(ternary)  for(k=0; k<n1d; k++) postpara[0][k]=postpara[1][k]=-1;
   fprintf(fout, "\n\nPosterior on the grid\n\n");
   for(j=(ternary?2:0); j<dim; j++,FPN(fout)) {
      fprintf(fout, "%-2s: ", paras[j]);
      for(k=0;k<n1d;k++)
         fprintf(fout, " %6.3f", postpara[j][k]);
   }
   if(ternary) {
      fprintf(fout,"\nPosterior for p0-p1 (see the ternary graph)\n\n");
      for(k=0;k<n1d*n1d;k++) {
         fprintf(fout," %5.3f", postp0p1[k]);
         if(fabs(square((int)sqrt(k+1.))-(k+1))<1e-5) FPN(fout);
      }
      fprintf(fout,"\nsum of density on p0-p1 = %10.6f\n", sum(postp0p1,n1d*n1d));
   }

   BayesEB = 0;
   free(meanw);  free(lnfXs);  free(pclassM);  free(lnprior);
   if(ternary) free(postp0p1);
   return(0);
}



/********************************************************************/
void get_grid_para_like_AC(double para[][100], int n1d, int dim, 
     double w0b[], double w2b[], double x[], double *S);

void get_pclassM_iw_AC(int *iw, double *pclassM, int iclassM, int ip[], double para[][100], int n1d);


void get_grid_para_like_AC(double para[][100], int n1d, int dim, 
     double w0b[], double w2b[], double x[], double *S)
{
/* This sets up the grid (para[][]) according to the priors.  
   It calculates the probability of data at each site given w: f(f_h|w).  
   This is calculated using the branch model (NSsites = 0 model = 2), with 
   BayesEB=2 used to force the use of the correct scale factors in GetPMatBranch().

   Order of site classes for iw or f(x_h|w):
                        fore   back     #sets
   Branchsite A (121 sets)
      site class 0:      w0     w0        10
      site class 1:      w1=1   w1=1       1
      site class 2a:     w0     w2       100
      site class 2b:     w1=1   w2        10

   Clade C      (111 sets)
      site class 0:      w0     w0        10
      site class 1:      w1=1   w1=1       1
      site class 2:      w2     w3       10*10*10...
*/
   int modelA=(com.model==2), i,k,h, iw, site=10;
   double fh, wbranches[NBTYPE];  /* w for back and fore branches */
   int NSsites0=com.NSsites, model0=com.model;

   for(i=0; i<n1d; i++) {
      para[0][i] = para[1][i] = -1;                       /* p0 & p1 */
      para[2][i] = w0b[0] + (i+0.5)*(w0b[1]-w0b[0])/n1d;  /* w0 */
      para[3][i] = w2b[0] + (i+0.5)*(w2b[1]-w2b[0])/n1d;  /* w2 */
      if(com.model==3)                                    /* w3 w4 ... in model C */
         for(k=1; k<com.nbtype; k++) 
            para[3+k][i] = para[3][i];
   }

   /* calculates the likelihood com.fhK[] */
   printf("\nCalculating f(x_h|w) for %d w's\n", com.ncatG);
   com.conPSiteClass = 0;
   *S = 0;
   com.model = 2;
   com.NSsites = 0;
   com.pomega = wbranches;
   for(iw=0; iw<com.ncatG; iw++) {
      if(modelA) {    /* model A:  10 + 1 + 100 + 10 */
         if(iw<n1d)        wbranches[0] = wbranches[1] = para[2][iw]; /* class 0:  w0 */
         else if(iw==n1d)  wbranches[0] = wbranches[1] = 1;           /* class 1:  w1 */
         else if(iw<n1d+1+n1d*n1d) {                                  /* class 2a: w0 w2 */
            wbranches[0] = para[2][(iw-n1d-1)/n1d];
            wbranches[1] = para[3][(iw-n1d-1)%n1d];
         }
         else {                                                       /* class 2b: w1 w2 */
            wbranches[0] = 1;
            wbranches[1] = para[3][iw-n1d-1-n1d*n1d];
         }
      }
      else {          /* model C:  10 + 1 + 10*10*... */
         if(iw<n1d)                                                 /* class 0: w0 */
            for(i=0; i<com.nbtype; i++) wbranches[i] = para[2][iw];
         else if(iw==n1d)                                           /* class 1: w1 */
            for(i=0; i<com.nbtype; i++) wbranches[i] = 1;
         else {                                                     /* class 2: w2 w3 */
            for(i=com.nbtype-1,k=iw-n1d-1; i>=0; i--) {
               wbranches[i] = para[3+i][k%n1d];
               k /= n1d;
            }
         }
         /*
         printf("\nw%-2d: ", iw+1);
         for(i=0; i<com.nbtype; i++) printf(" %10.6f", wbranches[i]);
         */
      }
      ConditionalPNode(tree.root, 0, x);
      for(h=0; h<com.npatt; h++) {
         for(i=0,fh=0; i<com.ncode; i++)
            fh += com.pi[i]*nodes[tree.root].conP[h*com.ncode+i];
         if(fh<=0) {
            if(fh<-1e-5) printf("\nfh = %.6f negative\n",fh);
            fh=1e-80;
         }
         fh = log(fh);
         for(k=0; k<com.NnodeScale; k++) 
            fh += com.nodeScaleF[k*com.npatt+h];
         com.fhK[iw*com.npatt+h] = fh;
      }
      if((iw+1)%10==0 || iw==com.ncatG-1)
         printf("\r\t %4d / %d sets.", iw+1, com.ncatG);
   }
   FPN(F0);

   for(h=0,*S=0; h<com.npatt; h++) {
      for(k=1,fh=com.fhK[h]; k<com.ncatG; k++)
         fh = max2(fh,com.fhK[k*com.npatt+h]);
       for(k=0; k<com.ncatG; k++) 
         com.fhK[k*com.npatt+h] = exp(com.fhK[k*com.npatt+h]-fh);
      *S += fh*com.fpatt[h];
   }
   com.NSsites=NSsites0;  com.model=model0;
}

void get_pclassM_iw_AC(int *iw, double *pclassM, int iclassM, int ip[], double para[][100], int n1d)
{
/* Given the point on the grid ip[] and iclassM, this returns iw and pclassM, 
   where iw locates the correct f(x_h|w) stored in com.fhK[], and pclassM is 
   the proportion of the site class under the model.
   The n1d*n1d grid for p0-p1 is mapped onto the ternary graph for p0-p1-p2.  

   See get_grid_para_like_AC() for order of iw or site classes.

   Parameters are model A: (p0 p1 w0 w2)
                  model C: (p0 p1 w0 w2 w3 ...)
*/
   int modelA=(com.model==2), i,j;
   double p[3];

   GetIndexTernary(&i, &j, &p[0], &p[1], ip[0]*n1d+ip[1], n1d);
   p[2] = 1-p[0]-p[1];
   *pclassM = p[iclassM<=2 ? iclassM : 2];
   if(modelA && iclassM>=2)  *pclassM = p[2]*p[iclassM-2]/(1-p[2]);

   if(iclassM==0)      *iw = ip[2];                 /* class 0: w0 */
   else if(iclassM==1) *iw = n1d;                   /* class 1: w1 */
   else if(modelA==0) {   /* clade model C site class 2: w2 w3 w4 ... */
      for(i=0,*iw=0; i<com.nbtype; i++)
         *iw = *iw*n1d + ip[3+i];
      *iw += n1d+1;
   }
   else if(iclassM==2) *iw = n1d+1+ip[2]*n1d+ip[3]; /* class 2a model A: w0 & w2 */
   else                *iw = n1d+1+n1d*n1d+ip[3];   /* class 2b model A: w1 & w2 */
}


int lfunNSsites_AC (FILE* frst, double x[], int np)
{
/* Bayes empirical Bayes (BEB) calculation of posterior probabilities for site 
   classes under the branch-site model A (Yang & Nielsen 2002) and clade model C
   (Bielawski & Yang 2004).  The dimension of integral is 4 for A and (3+nbtype) 
   for C.  Each dimension is approximated using n1d=10 categories, and the grid 
   is made up of ngrid=n1d^dim points.

   For branch-site model A, the probability of data at a site f(x_h|w) needs to 
   be calculated for 121=(d+1+d*d+d) sets of w's.  For model C, it needs to be 
   calculated for 111 (d+1+d^nbtype) sets.  
   Those are calculated and stored in com.fhK[], before entering the grid. 
   iw[ngrid*nclassM] identifies the right f(x_h|w), and pclassM[ngrid*nclassM] 
   is the proportion of sites under the model, f(w|ita).  Those are set up in 
   get_pclassM_iw_AC().

   The priors are set up in get_grid_para_like_AC().  See notes there.

   Parameters and priors are as follows:
      model A (p0 p1 w0 w2):    p0,p1~U(0,1), w0~U(0,1), w2~U(1,11)
      model C (p0 p1 w0 w2 w3): p0,p1~U(0,1), w0~U(0,1), w2,w3~U(0,5)

   Ziheng, UCL, 22 September 2004, modified Nov 2008 to use more than 2 branch types 
   under clade model C.
*/
   int n1d=10, debug=0, site=10;
   double w0b[]={0,1};  /* w0b for w0. */
   double wsb[]={1,11}; /* for w2 in model A */
   double w2b[]={0,3};  /* for w2-w3-w4 in model C */

   int modelA=(com.model==2), dim=(modelA?4:3+com.nbtype), ngrid,igrid, ip[3+NBTYPE], j,k,h,hp,it;
   int refsp=0, ncatG0=com.ncatG, lst=(com.readpattern?com.npatt:com.ls);
   /* # of site classes under model and index for site class */
   int nclassM = (modelA?4:3), iclassM, *iw, i;
   double para[3+NBTYPE][100]={{0}}, postpara[3+NBTYPE][100];  /* paras on grid : n1d<=100! */
   double fh, fX, *lnfXs,S1,S2, *pclassM, *postSite, *postp0p1;
   double fhk[3], t, cutoff=0.5;
   char timestr[32], paras[3+NBTYPE][5]={"p0","p1","w0","w2","w3"}, *sig, aa;

   printf("\nBEBing (dim = %d).  This may take many minutes.", dim);

   if(!modelA) 
      for(i=2; i<com.nbtype; i++) sprintf(paras[3+i], "w%d", i+2);

   for(i=0,ngrid=1; i<dim; i++) ngrid *= n1d;
   if(modelA)
      com.ncatG = n1d + 1 + n1d*n1d + n1d;  /* branch-site model A: table 1 YWN05 */
   else {                                   /* clade model C: table 2 YWN05 */
      for(i=0,com.ncatG=1; i<com.nbtype; i++) com.ncatG *= n1d;  /* w2 w3 w4 ... */
      com.ncatG += n1d + 1;         /* w0 & w1=1 */
   }

   k = (n1d*n1d + com.npatt*nclassM + ngrid + ngrid*nclassM)*sizeof(double)
      + ngrid*nclassM*sizeof(int);
   if((postp0p1=(double*)malloc(k)) == NULL) 
      error2("oom in lfunNSsites_AC");
   postSite = postp0p1 + n1d*n1d;
   lnfXs = postSite + com.npatt*nclassM;
   pclassM = lnfXs + ngrid; 
   iw = (int*)(pclassM + ngrid*nclassM);

   k = com.npatt*com.ncatG*sizeof(double);
   if((com.fhK=(double*)realloc(com.fhK,k)) == NULL) error2("oom fhK");

   BayesEB = 2;
   get_grid_para_like_AC(para, n1d, dim, w0b, (modelA?wsb:w2b), x, &S1);

   /* Set up im and pclassM, for each igrid and iclassM. */
   for(igrid=0; igrid<ngrid; igrid++) {
      for(j=dim-1,it=igrid; j>=0; j--) { ip[j]=it%n1d; it/=n1d; }
      for(k=0; k<nclassM; k++) {
         get_pclassM_iw_AC(&iw[igrid*nclassM+k], &pclassM[igrid*nclassM+k],k,ip,para,n1d);
      }
   }

   /* calculate marginal prob of data, fX, and postpara[].  S2 is scale. */
   printf("Calculating f(X), the marginal probability of data.\n");
   fX=1;  S2=-1e300;
   for(j=0; j<dim; j++)  /* postpara[0-1] for p0p1 ignored */
      for(k=0; k<n1d; k++) 
         postpara[j][k] = 1;
   for(k=0; k<n1d*n1d; k++) 
      postp0p1[k] = 1;
   for(igrid=0; igrid<ngrid; igrid++) {
      for(j=dim-1,it=igrid; j>=0; j--) {
         ip[j]=it%n1d; 
         it/=n1d; 
      }
      for(h=0,lnfXs[igrid]=0; h<com.npatt; h++) {
         for(k=0,fh=0; k<nclassM; k++)
            fh += pclassM[igrid*nclassM+k]*com.fhK[iw[igrid*nclassM+k]*com.npatt+h];
         if(fh<1e-300) {
            printf("strange: f[%3d] = %12.6g very small.\n",h,fh);
            continue;
         }
         lnfXs[igrid] += log(fh)*com.fpatt[h];
      }
      t = lnfXs[igrid]-S2;
      if(t>0) {    /* change scale factor S2 */
         t = (t<200 ? exp(-t) : 0);
         fX = fX*t+1;
         for(j=0; j<dim; j++) for(k=0; k<n1d; k++) 
            postpara[j][k] *= t;
         for(k=0; k<n1d*n1d; k++) 
            postp0p1[k] *= t;

         for(j=0; j<dim; j++)  
            postpara[j][ip[j]] ++;
         postp0p1[ip[0]*n1d+ip[1]] ++;
         S2 = lnfXs[igrid];
      }
      else if(t>-200) {
         t = exp(t);
         fX += t;
         for(j=0; j<dim; j++)  
            postpara[j][ip[j]] += t;
         postp0p1[ip[0]*n1d+ip[1]] += t;
      }
      if((igrid+1)%500==0 || igrid==ngrid-1)
         printf("\t%3d / %3d grid points\r", igrid+1,ngrid);

   }
   for(j=0; j<dim; j++) for(k=0; k<n1d; k++) 
      postpara[j][k] /= fX;
   for(k=0; k<n1d*n1d; k++) 
      postp0p1[k] /=fX;

   fX = log(fX)+S2;
   printf("\tlog(fX) = %12.6f  S = %12.6f %12.6f\n", fX+S1-dim*log(n1d*1.),S1,S2);

   /* calculate posterior probabilities for sites.  S1 is scale factor */
   printf("Calculating f(w|X), posterior probs of site classes.\n");
   for(h=0; h<com.npatt; h++) {
      S1 = -1e300;  
      for(j=0; j<nclassM; j++)
         postSite[j*com.npatt+h] = 1;
      for(igrid=0; igrid<ngrid; igrid++) {
         for(j=dim-1,it=igrid; j>=0; j--) { ip[j]=it%n1d; it/=n1d; }
         for(k=0,fh=0; k<nclassM; k++) /* duplicated calculation */
            fh += fhk[k] = pclassM[igrid*nclassM+k]*com.fhK[iw[igrid*nclassM+k]*com.npatt+h];

         for(iclassM=0; iclassM<nclassM; iclassM++) {
            fhk[iclassM] /= fh;
            t = log(fhk[iclassM]) + lnfXs[igrid]; /* t is log of term on grid */
            if(t>S1 + 50) {  /* change scale factor S1 */
               for(j=0; j<nclassM; j++)
                  postSite[j*com.npatt+h] *= exp(S1-t);
               S1 = t;
            }
            postSite[iclassM*com.npatt+h] += exp(t-S1);
         }
      }
      for(j=0; j<nclassM; j++) 
         postSite[j*com.npatt+h] *= exp(S1-fX);

      if((h+1)%10==0 || h==com.npatt-1)
         printf("\r\tdid %3d / %3d site patterns  %s", h+1,com.npatt,printtime(timestr));
   }  /* for(h) */

   if(debug) 
      for(k=0,printf("\nS%d: ",site); k<nclassM; k++) printf("%7.4f",postSite[k*com.npatt+site]);

   /* print out posterior probabilities */
   fprintf(frst,"\nBayes Empirical Bayes (BEB) probabilities for %d classes (class)", nclassM);
   fprintf(fout,"\nBayes Empirical Bayes (BEB) analysis");
   fprintf(fout," (Yang, Wong & Nielsen 2005. Mol. Biol. Evol. 22:1107-1118)");

   com.ncatG = ncatG0;

   PrintProbNSsites(frst, postSite, NULL, NULL, nclassM, refsp);
   if(com.model==2) {  /* branch&site model A */
      fprintf(fout,"\nPositive sites for foreground lineages Prob(w>1):\n");
      for(h=0; h<lst; h++) {
         hp = (!com.readpattern ? com.pose[h] : h); 
         aa = GetAASiteSpecies(refsp, hp);
         t = postSite[2*com.npatt+hp] + postSite[3*com.npatt+hp];
         if(t>cutoff) {
            sig="";  if(t>.95) sig="*";  if(t>.99) sig="**";
            fprintf(fout,"%6d %c %.3f%s\n",h+1, aa, t, sig);
         }
      }
   }

   fprintf(fout, "\n\nThe grid (see ternary graph for p0-p1)\n\n");
   for(j=2; j<dim; j++,FPN(fout)) {
      fprintf(fout, "%-2s: ", paras[j]);
      for(k=0; k<n1d; k++)
         fprintf(fout, " %6.3f", para[j][k]);
   }
   for(k=0; k<n1d; k++)
      postpara[0][k] = postpara[1][k]=-1;
   fprintf(fout, "\n\nPosterior on the grid\n\n");
   for(j=2; j<dim; j++,FPN(fout)) {
      fprintf(fout, "%-2s: ", paras[j]);
      for(k=0; k<n1d; k++)
         fprintf(fout, " %6.3f", postpara[j][k]);
   }
   fprintf(fout,"\nPosterior for p0-p1 (see the ternary graph)\n\n");
   for(k=0; k<n1d*n1d; k++) {
      fprintf(fout," %5.3f", postp0p1[k]);
      if(fabs(square((int)sqrt(k+1.))-(k+1))<1e-5) FPN(fout);
   }
   fprintf(fout,"\nsum of density on p0-p1 = %10.6f\n", sum(postp0p1,n1d*n1d));

   free(postp0p1);
   BayesEB = 0;
   return(0);
}
