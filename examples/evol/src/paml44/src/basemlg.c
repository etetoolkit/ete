/* BASEMLG.c 
   ML parameter estimation for models with Gamma-distributed rates
   over sites, combined with tree topology estimation from DNA sequences

                   Copyright, Ziheng YANG, July 1992 onwards
                      cc -o basemlg -fast basemlg.c tools.o -lm
                        basemlg <ControlFileName>
*/


#include "paml.h"

#define NS          10
#define NTREE       20    
#define NBRANCH     (NS*2-2)      
#define NNODE       (NS*2-1) 
#define MAXNSONS    10
#define NGENE       4
#define LSPNAME     30
#define NCODE       4
#define NP          (NBRANCH+NGENE+5)

extern char BASEs[];
extern int noisy, NFunCall, *ancestor;
extern double *SeqDistance;

int Forestry (FILE *fout, double space[]);
int GetOptions (char *ctlf);
int SetxBound (int np, double xb[][2]);
int testx (double x[], int np);
int GetInitials (double x[], int *fromfile);
void TestFunction (FILE *fout, double x[], double space[]);
int GetMem (int nbranch, int nR, int nitem);
void GetSave (int nitem, int *nm, int M[], double alpha, double c);
double GetBmx (int ninter, int nsum, int im, int M[], int nodeb[]);
int RhoRate (double x[]);
int lfunG_print (double x[], int np);
double lfunG (double x[], int np);
int lfunG_d (double x[], double *lnL, double dl[], int np);
int lfunG_dd (double x[], double *lnL, double dl[], double ddl[], int np);

struct CommonInfo {
   char *z[NS], *spname[NS], seqf[32],outf[32],treef[32];
   int  seqtype, ns, ls, ngene, posG[NGENE+1],lgene[NGENE],*pose,npatt, readpattern;
   int  clock,fix_alpha,fix_kappa,fix_rgene,Malpha,print,verbose;
   int  model, runmode, cleandata, ndata;
   int np, ntime, nrate, ncode, nrgene, icode, coding, fix_blength;
   double *fpatt, pi[4], lmax, alpha,kappa, rgene[NGENE],piG[NGENE][4],*conP;
   double *SSave, *ErSave, *EaSave;
   int  nhomo, nparK, ncatG, fix_rho, getSE, npi0;   /* unused */
   double pi_sqrt[4], rho;                           /* unused */
}  com;

struct TREEB {
   int  nbranch, nnode, root, branches[NBRANCH][2];
   double lnL;
}  tree;

struct TREEN {
   int father, nson, sons[MAXNSONS], ibranch;
   double branch, age, label, *conP;
   char *nodeStr, fossil;
}  nodes[2*NS-1];

static int nR=4, CijkIs0[64];
static double Cijk[64], Root[4];

FILE *frub, *flfh, *frate, *finitials=NULL;
char *ratef="rates";
char *models[]={"JC69","K80","F81","F84","HKY85","T92","TN93","REV","UNREST", "REVu","UNRESTu"};
enum {JC69, K80, F81, F84, HKY85, T92, TN93, REV, UNREST, REVu, UNRESTu} MODELS;
char *clockstr[]={"", "Global clock", "Local clock", "ClockCombined"};
enum {GlobalClock=1, LocalClock, ClockCombined} ClockModels;

/*
#define REV_UNREST
*/
#define BASEMLG
int LASTROUND=0; /* no use for this */
#include "treesub.c"

int main (int argc, char *argv[])
{
   FILE *fout, *fseq=NULL, *fpair[6];
   char pairfs[1][32]={"2base.t"};
   char ctlf[32]="baseml.ctl";
   double  space[50000];

   noisy=2;  com.cleandata=1;  /* works with clean data only */
   com.runmode=0;
   com.clock=0;    com.fix_rgene=0;

   com.seqtype=0;     com.model=F84;
   com.fix_kappa=0;   com.kappa=5;
   com.fix_alpha=0;   com.alpha=0.2;
   com.ncode=4;

   starttimer();
   SetSeed(4*(int)time(NULL)+1);

   printf("BASEMLG in %s\n",  VerStr);
   frate=fopen(ratef,"w");  frub=fopen("rub","w");  flfh=fopen("lnf","w");

   if (argc>1) { strcpy(ctlf, argv[1]); printf ("\nctlfile is %s.\n", ctlf); }
   GetOptions (ctlf);
   finitials=fopen("in.basemlg","r");

   if ((fout=fopen (com.outf, "w"))==NULL) error2("outfile creation err.");
   if((fseq=fopen (com.seqf,"r"))==NULL)  error2("No sequence file!");
   ReadSeq (NULL, fseq, com.cleandata);
   if((fpair[0]=(FILE*)fopen(pairfs[0],"w"))==NULL) error2("2base.t file open error");

   fprintf (fout,"BASEMLG %15s %8s + Gamma", com.seqf, models[com.model]);
   if (com.clock) fprintf (fout, ", Clock");
   if (com.model!=JC69 && com.model!=F81 && com.fix_kappa)
      fprintf (fout,"\nkappa =%7.3f given\n", com.kappa);
   if (com.ngene>1) fprintf (fout, " (%d genes)  ", com.ngene);

   SeqDistance=(double*)malloc(com.ns*(com.ns-1)/2*sizeof(double));
   ancestor=(int*)malloc(com.ns*(com.ns-1)/2*sizeof(int));
   if (SeqDistance==NULL||ancestor==NULL) error2("oom");

   InitializeBaseAA(fout);
   if (com.model==JC69) PatternWeightJC69like(fout);

   DistanceMatNuc (fout, fpair[0], com.model, com.alpha);
   if (com.model<=HKY85)
      EigenTN93 (com.model, com.kappa, com.kappa, com.pi, &nR, Root, Cijk);
   Forestry (fout, space);
   fclose(fseq);  fclose(fpair[0]);
   if(finitials) { fclose(finitials);  finitials=NULL; }
   return (0);
}

/* x[] is arranged in order of t[ntime], rgene[], kappa and alpha (if any) */

int Forestry (FILE *fout, double space[])
{
   int  status=0, i,j, itree, ntree, np;
   int pauptree=0, btree=0, haslength, iteration=1;
   double x[NP], xb[NP][2], lnL[NTREE]={0}, e=1e-6, *var=space+NP;
   FILE *ftree;

   if ((ftree=fopen(com.treef,"r"))==NULL)   error2("treefile err.");
   GetTreeFileType(ftree,&ntree,&pauptree,0);

   fprintf (flfh,"%6d%6d%6d\n", ntree, com.ls, com.npatt);
   fprintf(frate,"Rates for sites, from BASEMLG, %d tree(s)\n\n", ntree);

   for (itree=0; itree<ntree; itree++) {
      printf("\nTREE # %2d\n", itree+1 );
      fprintf(fout,"\nTREE # %2d:  ", itree+1);
      fprintf(flfh,"\n\n%2d\n", itree+1);
      fprintf(frub,"\n\nTREE # %2d", itree+1);
      fprintf(frate,"\nTREE # %2d\n", itree+1);

      if(ReadTreeN(ftree,&haslength,&i,0,1))
           { puts("err or end of tree file."); break; }

      com.ntime = com.clock ? tree.nnode-com.ns: tree.nbranch;

      OutTreeN (F0, 0, 0);   
      OutTreeN (fout, 0, 0);  
      fflush (fout);  fflush (flfh);

      i=(com.clock||com.model>HKY85 ? 2 : 2+!com.fix_alpha);
      GetMem(tree.nbranch, nR, i);
      GetInitials(x, &i);
      if(i==-1) iteration=0;
      np = com.np;
      printf("\nnp =%6d\n", np);
      NFunCall=0;
/*
      TestFunction (fout, x, space);
*/
      if (itree==0 && i==0) {
         printf("\a");
         printf ("\n\nSuggest using BASEML to get initial values..");
         for(j=0; j<com.ntime; j++) fprintf (fout,"%9.5f", x[j]);
      }

      for(i=0; i<np; i++) printf("%9.5f", x[i]);   FPN(F0);
      if(!iteration) puts("parameters are fixed, calculating lnL . . .");
      lnL[itree]=lfunG(x, np);
      if(noisy) printf("\nlnL0 = %12.6f", -lnL[itree]);

      if(iteration) {
         if (com.clock||com.model==REV) {
            SetxBound (np, xb);
            i=ming2(frub,&lnL[itree],lfunG,
               ((com.clock||com.model>HKY85)?NULL:lfunG_d),x,xb, space,e,np);
            Hessian (np,x,lnL[itree],space,var,lfunG,var+np*np);
            matinv (var, np, np, var+np*np);
         }
         else 
            i=Newton(frub, &lnL[itree], lfunG, lfunG_dd,testx,x,var,e,np);
      }
      if(noisy) printf("\nOut...\nlnL:%14.6f\n", -lnL[itree]);


      if (i || j<np) { status=-1; fprintf (fout, "\n\ncheck convergence.."); }
      fprintf(fout,"\nlnL(np:%3d):%14.6f%+12.6f\n", com.np,
         -lnL[itree], -lnL[itree]+lnL[0]);
      OutTreeB (fout);  FPN (fout);

      for(i=0; i<np; i++) fprintf (fout,"%9.5f", x[i]);   FPN (fout);
      if(iteration) 
         for(i=0; i<np; i++)
            fprintf (fout,"%9.5f", var[i*np+i]>0.?sqrt(var[i*np+i]):0.);

      fprintf (fout, "\n\n# fun calls:%10d\n", NFunCall);
      OutTreeN(fout,1,1);  fputs(";\n", fout);
      lfunG_print (x, np);
/*
      RhoRate (x);
*/
   }        /* for (itree) */
   fclose (ftree);
   return (0);
}



int SetBranch (double x[])
{
   int i, status=0;
   double small=1e-5;

   if (com.clock) {
       FOR (i,com.ntime) nodes[i+com.ns].age=x[i];
       FOR (i,tree.nnode) {
          if (i==tree.root) continue;
          nodes[i].branch = nodes[nodes[i].father].age-nodes[i].age;
          if (nodes[i].branch<-small) status=-1;
       }
   }
   else
      FOR (i,tree.nnode)
         if (i!=tree.root && (nodes[i].branch=x[nodes[i].ibranch])<-small)
            status=-1;
   return (status);
}

int testx (double x[], int np)
{
   int i,k;
   double tb[]={1e-5,4}, rgeneb[]={.01,20}, kappab[]={0,80}, alphab[]={.01,99};

   if (SetBranch(x)) return (-1);
   FOR (i,com.ntime)   if (x[i]<tb[0] || x[i]>tb[1])   return (-1);
   if (np==com.ntime)  return (0); 
   for (i=0,k=com.ntime; i<com.nrgene; i++,k++) 
      if (x[k]<rgeneb[0] || x[k]>rgeneb[1])   return (-1);
   for (i=0; i<com.nrate; i++,k++)
      if (x[k]<kappab[0] || x[k]>kappab[1])    return(-1);
   if (!com.fix_alpha && (x[np-1]<alphab[0] || x[np-1]>alphab[1]))  return(-1);
   return (0);
}

int SetxBound (int np, double xb[][2])
{
/* sets lower and upper bounds for variables during iteration
*/
   int i,j, k=com.ntime+com.nrgene+com.nrate;
   double tb[]={.4e-5, 20}, rgeneb[]={1e-4,99}, rateb[]={1e-5,999};
   double alphab[]={0.005, 99}, pb[2]={1e-5,1-1e-5};

   if(com.clock) {
      xb[0][0]=tb[0];  xb[0][1]=tb[1];
      for(i=1;i<com.ntime;i++) FOR(j,2) { xb[i][0]=pb[0]; xb[i][1]=pb[1]; }
   }
   else 
      FOR (i,com.ntime)  FOR (j,2) xb[i][j]=tb[j];
   FOR (i,com.nrgene) FOR (j,2) xb[com.ntime+i][j]=rgeneb[j]; 
   FOR (i,com.nrate)  FOR (j,2) xb[com.ntime+com.nrgene+i][j]=rateb[j];
   if(!com.fix_alpha) FOR (j,2) xb[k][j]=alphab[j];
   if(noisy) {
      puts("\nBounds:\n");
      FOR(i,np) printf(" %10.6f", xb[i][0]);  FPN(F0);
      FOR(i,np) printf(" %10.6f", xb[i][1]);  FPN(F0);
   }
   return(0);
}

int GetInitials (double x[], int *fromfile)
{
   int i,j;
   double t;

   com.nrgene = (!com.fix_rgene)*(com.ngene-1);
   com.nrate=0;
   if (com.model==REV) {
      com.nrate=5;
      x[com.ntime+com.nrgene] = 1;
      FOR (i,com.nrate-1) x[com.ntime+com.nrgene+i+1]=1/com.kappa;
   }
   else if (!com.fix_kappa)
      { com.nrate=1; x[com.ntime+com.nrgene]=com.kappa; }
   if (com.model<=HKY85)
      EigenTN93 (com.model, com.kappa, com.kappa, com.pi, &nR, Root, Cijk);

   com.np = com.ntime+com.nrgene+com.nrate+(!com.fix_alpha);
   FOR (j,com.nrgene) x[com.ntime+j]=1;
   if (!com.fix_alpha)  x[com.np-1]=com.alpha;

   if (com.clock) for(j=1,x[0]=0.1; j<com.ntime; j++) x[j]=0.5;
   else           FOR (j,com.ntime) x[j]=0.1;

   LSDistance (&t, x, testx);
   for(j=0; j<com.ntime; j++) 
      if (x[j]<1e-5) x[j]=1e-4;

   if(finitials) readx(x,fromfile);
   else    *fromfile=0;

   return (0);
}

void TestFunction (FILE* fout, double x[], double space[])
{
   int i, np=com.np;
   double lnL;

   printf ("\ntest functions\n");
   SetSeed (23);
   FOR (i,np) x[i]=(double)i*rndu()+0.0001;
   matout (F0, x, 1, np);    matout (fout, x, 1, np);

   lnL=lfunG(x, np);
   printf ("\n\nnp:%6d\nlnL:%12.8f\n", np, lnL);
   fprintf (fout, "\n\nnp:%6d\nlnL:%12.8f\n", np, lnL);

   printf ("\ndl and gradient");     fprintf (fout, "\ndl and gradient");
   lfunG_d (x, &lnL, space, np);
   printf ("\nlnL:%12.8f", lnL);     fprintf (fout, "\nlnL:%12.8f", lnL);
   matout (F0, space, 1, np);        matout (fout, space, 1, np);
   gradient (np, x, lnL, space, lfunG, space+np, 0);
   printf ("\nlnL:%12.8f", lnL);     fprintf (fout, "\nlnL:%12.8f", lnL);
   matout (F0, space, 1, np);        matout (fout, space, 1, np);
   
   printf ("\nddl & Hessian");       fprintf (fout, "\nddl & Hessian");
   lfunG_dd (x, &lnL, space, space+np, np);
   printf ("\nlnL:%12.8f", lnL);     fprintf (fout, "\nlnL:%12.8f", lnL);
   matout (F0, space, 1, np);        matout (fout, space, 1, np);
   matout2 (F0, space+np, np, np, 8, 3);
   matout2 (fout, space+np, np, np, 8, 3);
   fflush (fout);
   Hessian (np, x, lnL, space, space+np, lfunG, space+np+np*np);
   printf ("\nlnL:%12.8f", lnL);     fprintf (fout, "\nlnL:%12.8f", lnL);
   matout2 (F0, space+np, np, np, 8, 3);
   matout2 (fout, space+np, np, np, 8, 3);

   exit (0);
}

int GetMem (int nbranch, int nR, int nitem)
{
/* ns=4: 98KB,  5: 1.6MB,  6: 25MB,  7: 402MB    (for HKY85, 3/3/93)
   nitem=1:ErSave; 2:SSave & ErSave; 3:SSave & ErSave & EaSave 
*/
   int nm, j;
   double memsize=-1;

   for(j=0,nm=1; j<nbranch; j++)   nm*=nR;
   if(nm>1) memsize=(double)nm*nitem*sizeof(double);
   printf ("\nMemory required: %6.0fK bytes\n", memsize/1024);
   if(nm*nitem*sizeof(double)<=0 || 
      (com.conP=(double*)realloc(com.conP, nm*nitem*sizeof(double)))==NULL)
      error2("out of memory");

   com.ErSave  = com.conP;
   if (nitem>1) com.SSave=com.ErSave+nm;
   if (nitem>2) com.EaSave=com.SSave+nm;
   return(0);
}


void GetSave (int nitem, int *nm, int M[], double alpha, double c)
{
/* correct for both clock=0 and 1
   nitem=1:ErSave; 2:SSave & ErSave; 3:SSave & ErSave & EaSave 
*/
   int im, j, it;
   double S;

   for(j=0,*nm=1; j<tree.nbranch; j++)   *nm*=nR;
   for (im=0; im< *nm; im++) {
      for (j=0,it=im,S=0; j<tree.nbranch; j++) {
         M[j]=it%nR;    it/=nR;
         if (M[j]) S+=nodes[tree.branches[j][1]].branch*Root[M[j]];
      }
      com.ErSave[im] = pow(alpha/(alpha-c*S),alpha);
      if (nitem>1) com.SSave[im]  = S;
      if (nitem>2) com.EaSave[im] = log(alpha/(alpha-c*S))-c*S/(alpha-c*S);
   }
}

double GetBmx (int ninter, int nsum, int im, int M[], int nodeb[])
{
   int isum, j, it, i, nR4=nR*4;
   double y, Bmx;

   for (j=0,it=im; j<tree.nbranch;  M[j]=it%nR,it/=nR,j++) ;
   for (isum=0,Bmx=0; isum<nsum; isum++) {
      for (j=0,it=isum; j<ninter; nodeb[com.ns+j]=it&3,it>>=2,j++) ;
      for (j=0,y=com.pi[nodeb[tree.root]]; j<tree.nbranch; j++) {
         i = nodeb[tree.branches[j][0]]*nR4
           + nodeb[tree.branches[j][1]]*nR + M[j];
         if (CijkIs0[i]) goto nextone;
         y *= Cijk[i];
      }
      Bmx += y;
      nextone: ;
   }
   return (Bmx);
}

int RhoRate (double x[])
{
/* rate factors for all possible site patterns, and the correlation 
   coefficient (Yang and Wang, in press).
*/
   int  i,j, h, nodeb[NNODE], M[NBRANCH], accurate=(com.ns<8);
   int  im, nm, nsum=1<<(2*(tree.nnode-com.ns)), *fobs;
   int  ninter=tree.nbranch-com.ns+1;
   double lnL, fh, sumfh=0, rh, Bmx, alpha, kappa;
   double mrh=0, mrh0=0, vrh=0, vrh0=0;

   if (com.ngene>1) error2 ("ngene>1");
   alpha=(com.fix_alpha ? com.alpha : x[com.np-1]);
   kappa=(com.fix_kappa ? com.kappa : x[com.ntime]);

   fprintf (flfh, "\n\nmodel:%6d\n  kappa:%9.4f\nalpha:%9.4f\nBranches",
            com.model, kappa, alpha);
   matout (flfh, x, 1, tree.nbranch);
   if (com.model<=HKY85 && !com.fix_kappa)  
       RootTN93 (com.model, kappa, kappa, com.pi, &rh, Root);
#ifdef REV_UNREST
   if (com.model==REV)
       EigenREV (NULL, x+com.ntime+com.nrgene, com.pi, &nR, Root, Cijk);
#endif
   if (SetBranch (x)) puts ("\nx[] err..");
   GetSave (2, &nm, M, alpha, 1);
   fobs = (int*) malloc ((1<<(2*com.ns)) * sizeof (int));

   FOR (h,(1<<2*com.ns)) fobs[h]=0;
   for (h=0; h<com.npatt; h++) {
      for (j=0,im=0; j<com.ns; j++) im = im*4+com.z[j][h];
      fobs[im]=(int)com.fpatt[h];
   }
   for (h=0,lnL=0; h<(1<<2*com.ns); h++) {
      if (accurate==0 && fobs[h]==0) continue;
      for (j=0,im=h; j<com.ns; nodeb[com.ns-1-j]=im%4,im/=4,j++);
      for (im=0,fh=0,rh=0; im<nm; im++) {
         Bmx=GetBmx (ninter, nsum, im, M, nodeb);
         fh += Bmx*com.ErSave[im];
         rh += Bmx*com.ErSave[im]*alpha/(alpha-com.SSave[im]);
      }  /* for (im) */
      if (fh<=0)  printf ("\a\nRhoRate: h=%4d  fh=%9.4f \n", h, fh);
      rh /= fh;      vrh += fh*rh*rh;
      sumfh += fh;   mrh += fh*rh;   mrh0+=rh*(double)fobs[h]/(double)com.ls;
      if (fobs[h]) {
         vrh0+= rh*rh*(double)fobs[h]/(double)com.ls;
         lnL -= log(fh)*(double)fobs[h];
      }
      fprintf (flfh,"\n%6d%9.2f%8.4f  ", fobs[h], fh*com.ls, rh);
      FOR (i,com.ns) fprintf (flfh, "%c", BASEs[nodeb[i]]);
   }    /* for (h) */
   vrh-=1;     vrh0-=mrh0*mrh0;
   fprintf (flfh, "\n%s Vrh", accurate?"accurate":"approximate");
   fprintf (flfh,"\nsumfh = 1 =%12.6f      mrh = 1 =%12.6f\n", sumfh, mrh);
   fprintf (flfh, "\nVr :%12.6f  Vr0:%12.6f   mrh0:%12.6f", vrh, vrh0, mrh0);
   fprintf (flfh, "\nPEV:%12.6f      %12.6f", 1/alpha-vrh, 1/alpha-vrh0);
   fprintf (flfh, "\nRHO:%12.6f      %12.6f", sqrt(vrh*alpha), sqrt(vrh0*alpha));
   fprintf (flfh,"\nLn(L)=%12.6f\n", -lnL);
   free (fobs);
   return (0);
}

int lfunG_print (double x[], int np)
{
/* This prints log(f) into lfh, and rates into rates
*/
   int  i,j, h,hp, igene, lt, nodeb[NNODE], M[NBRANCH];
   int  im, nm, nsum=1<<(2*(tree.nnode-com.ns));
   int  ninter=tree.nbranch-com.ns+1;
   double lnL, fh, rh, mrh0=0,vrh0=0, Bmx, y, alpha,kappa, *fhs,*rates=NULL;

   fputs("\nEstimation of rates for sites by BASEMLG.\n",frate);
 
   if ((rates=(double*)malloc(com.npatt*2*sizeof(double)))==NULL) error2("oom");
   fhs=rates+com.npatt;
   
   FOR (i, com.nrgene) com.rgene[i+1]=x[com.ntime+i];
   kappa=(com.fix_kappa ? com.kappa : x[com.ntime+com.nrgene]);
   alpha=(com.fix_alpha ? com.alpha : x[com.np-1]);

   if (com.model<=HKY85 && !com.fix_kappa)  
       RootTN93(com.model,kappa,kappa,com.pi,&y,Root);
#ifdef REV_UNREST
   if (com.model==REV)
       EigenREV(NULL,x+com.ntime+com.nrgene,com.pi,&nR,Root,Cijk);
#endif
   if (SetBranch(x)) puts("\nx[] err..");
   for(j=0,nm=1; j<tree.nbranch; j++)  nm*=nR;

   for (h=0,lnL=0,igene=-1,lt=0; h<com.npatt; lt+=(int)com.fpatt[h++]) {
      FOR(j,com.ns) nodeb[j] = com.z[j][h];
      if (h==0 || lt==com.lgene[igene])
         GetSave (2, &nm, M, alpha, com.rgene[++igene]);
      for (im=0,fh=0,rh=0; im<nm; im++) {
         Bmx=GetBmx (ninter, nsum, im, M, nodeb);
         fh += Bmx*com.ErSave[im];
         rh += Bmx*com.ErSave[im]*alpha/(alpha-com.SSave[im]);
      }  /* for (im) */
      if (fh<=0)  printf ("\a\nlfunG_print: h=%4d  fh=%9.4f \n", h, fh);
      rh/=fh;
      vrh0+=rh*rh*com.fpatt[h]/com.ls;
      mrh0+=rh*com.fpatt[h]/com.ls;
      rates[h]=rh;

      fhs[h]=fh;  fh=log(fh);
      lnL -= fh*com.fpatt[h];
      fprintf (flfh,"\n%4d%6.0f%14.8f%9.2f%9.4f  ",
         h+1, com.fpatt[h], fh, com.ls*fhs[h], rh);
      FOR (i,com.ns) fprintf (flfh, "%c", BASEs[com.z[i][h]]);

   }    /* for (h) */
   vrh0 -= mrh0*mrh0;
   if (com.print>=2)
      fprintf (flfh,"\n\nVrh0:%12.6f\nmrh0:%12.6f\nrho0:%12.6f\n", vrh0, mrh0, sqrt(vrh0*alpha));

   fputs("\n Site Freq  Data     Nexp.    Rates\n\n",frate);
 
   FOR(h, com.ls) {
      hp=com.pose[h];
      fprintf(frate,"%4d %5.0f  ",h+1,com.fpatt[hp]);  
      FOR(j,com.ns) fprintf (frate,"%c", BASEs[com.z[j][hp]]);
      fprintf(frate,"%9.2f%9.4f\n", com.ls*fhs[hp],rates[hp]);
   }
   fprintf(frate, "\nlnL = %12.6f", -lnL);
   if(com.ngene==1) {
      fprintf(frate, "\nVr0:%12.6f   mrh0:%12.6f", vrh0, mrh0);
      fprintf(frate, "\nApproximate corr(r,r^) =%12.6f\n",sqrt(vrh0*alpha));
   }
   return (0);
}

double lfunG (double x[], int np)
{
/* likelihood with spatial rate variation
*/
   int  i,j, h, igene, lt, nodeb[NNODE], M[NBRANCH];
   int  im, nm, nsum=1<<(2*(tree.nnode-com.ns));
   int  ninter=tree.nbranch-com.ns+1;
   double lnL, fh, rh, Bmx, y, alpha,kappa;

   NFunCall++;
   FOR (i, com.nrgene) com.rgene[i+1]=x[com.ntime+i];
   kappa=(com.fix_kappa ? com.kappa : x[com.ntime+com.nrgene]);
   alpha=(com.fix_alpha ? com.alpha : x[np-1]);
   if (com.model<=HKY85 && !com.fix_kappa)  
       RootTN93 (com.model, kappa, kappa, com.pi, &y, Root);
#ifdef REV_UNREST
   if (com.model==REV)
       EigenREV (NULL, x+com.ntime+com.nrgene, com.pi, &nR, Root, Cijk);
#endif
   if (SetBranch (x)) puts ("\nx[] err..");

   for (h=0,lnL=0,igene=-1,lt=0; h<com.npatt; lt+=(int)com.fpatt[h++]) {
      FOR(j,com.ns) nodeb[j] = com.z[j][h];
      if (h==0 || lt==com.lgene[igene])
         GetSave (1, &nm, M, alpha, com.rgene[++igene]);
      for (im=0,fh=0,rh=0; im<nm; im++) {
         Bmx=GetBmx (ninter, nsum, im, M, nodeb);
         fh += Bmx*com.ErSave[im];
      }  /* for (im) */
      if (fh<=0)  printf ("\a\nlfunG: h=%4d  fh=%9.4f \n", h, fh);
      lnL -= log(fh)*com.fpatt[h];
   }    /* for (h) */
   return (lnL);
}

int lfunG_d (double x[], double *lnL, double dl[], int np)
{
   int  nbranch=tree.nbranch, ninter=nbranch-com.ns+1;
   int  i,j, nodeb[NNODE], M[NBRANCH], h, igene,lt;
   int  im, nm, nsum=1<<(2*(tree.nnode-com.ns));
   double fh, y, Bmx, S, alpha, kappa, Er, dfh[NP];
   double drk1[4], c=1;
   double *p=com.pi, T=p[0],C=p[1],A=p[2],G=p[3],Y=T+C,R=A+G;

   if (com.clock||com.model>HKY85) error2 ("err lfunG_d");
   NFunCall++;
   FOR (i, com.nrgene) com.rgene[i+1]=x[com.ntime+i];
   kappa=(com.fix_kappa ? com.kappa : x[com.ntime+com.nrgene]);
   alpha=(com.fix_alpha ? com.alpha : x[np-1]);
   if (SetBranch (x)) puts ("\nx[] err..");
   if (!com.fix_kappa) {
      RootTN93 (com.model, kappa, kappa, p, &S, Root);
      y=T*C+A*G;
      drk1[1]=2*y*S*S;
      drk1[2]=2*(y-R*R)*Y*S*S;
      drk1[3]=2*(y-Y*Y)*R*S*S;
      if (com.model==F84) {
         y=2*T*C/Y+2*A*G/R;
         drk1[1]=y*S*S;
         drk1[2]=-S+(1+kappa)*y*S*S;
      }
   }
   *lnL=0; zero(dl,np);
   for (h=0,igene=-1,lt=0; h<com.npatt; lt+=(int)com.fpatt[h++]) {
      FOR(j,com.ns) nodeb[j] = com.z[j][h];
      if (h==0 || lt==com.lgene[igene])
         GetSave (2+!com.fix_alpha, &nm, M, alpha, (c=com.rgene[++igene]));
      for (im=0,fh=0,zero(dfh,np); im<nm; im++) {
         Bmx=GetBmx (ninter, nsum, im, M, nodeb);
         S = com.SSave[im];
         Er = com.ErSave[im]*Bmx;
         fh += Er;
         FOR (j, nbranch)
            if (M[j]) dfh[j]+=c*Er*alpha*Root[M[j]]/(alpha-c*S);       /* t */
         if (com.ngene>0 && igene>0)
            dfh[com.ntime+igene-1]+=Er*alpha/(alpha-c*S)*S;            /* c */
         if (!com.fix_kappa) {
            for (j=0,y=0; j<nbranch; j++) if (M[j]) y+=x[j]*drk1[M[j]];
            dfh[com.ntime+com.nrgene] += Er*alpha/(alpha-c*S)*y*c;     /* k */
         }
         if (!com.fix_alpha)  dfh[np-1] += Er*com.EaSave[im];       /* a */
      }  /* for (im) */
      if (fh<=0)  printf ("\a\nlfunG_d: h=%4d  fh=%9.4f \n", h, fh);
      *lnL -= log(fh)*com.fpatt[h];
      FOR (j, np) dl[j] -= dfh[j]/fh*com.fpatt[h];
   }    /* for (h) */
   return(0);
}

int lfunG_dd (double x[], double *lnL, double dl[], double ddl[], int np)
{
   int  nbranch=tree.nbranch, ninter=nbranch-com.ns+1;
   int  i,j,k, nodeb[NNODE], M[NBRANCH], h, igene,lt;
   int  im, nm, nsum=1<<(2*(tree.nnode-com.ns));
   double fh, y, Bmx,S,alpha,kappa, Er,Ea, y1,y2;
   double dfh[NP], ddfh[NP*NP], drk1[4], drk2[4], c=1, s1=0,s2=0;
   double T=com.pi[0],C=com.pi[1],A=com.pi[2],G=com.pi[3],Y=T+C,R=A+G;


   if (com.clock||com.model>HKY85) error2 ("err lfunG_dd");
   NFunCall++;
   FOR (i, com.nrgene) com.rgene[i+1]=x[com.ntime+i];
   kappa=(com.fix_kappa ? com.kappa : x[com.ntime+com.nrgene]);
   alpha=(com.fix_alpha ? com.alpha : x[np-1]);
   if (SetBranch (x)) puts ("\nx[] err..");

   if (!com.fix_kappa) {
      RootTN93 (com.model, kappa, kappa, com.pi, &S, Root);

      y=T*C+A*G;
      drk1[1]=2*y*S*S;
      drk1[2]=2*(y-R*R)*Y*S*S;
      drk1[3]=2*(y-Y*Y)*R*S*S;

      drk2[1]=-8*y*y*S*S*S;
      drk2[2]=-8*y*Y*(y-R*R)*S*S*S;
      drk2[3]=-8*y*R*(y-Y*Y)*S*S*S;

      if (com.model==F84) {
         y=2*T*C/Y+2*A*G/R;
         drk1[1]=y*S*S;
         drk1[2]=-S+(1+kappa)*y*S*S;

         drk2[1]=-2*y*y*S*S*S;
         drk2[2]=2*y*S*S*(1-(1+kappa)*y*S);
      }
   }
   *lnL=0, zero(dl,np), zero(ddl,np*np);
   for (h=0,igene=-1,lt=0; h<com.npatt; lt+=(int)com.fpatt[h++]) {
      FOR(j,com.ns) nodeb[j] = com.z[j][h];
      if (h==0 || lt==com.lgene[igene])
         GetSave (2+!com.fix_alpha, &nm, M, alpha, (c=com.rgene[++igene]));
      for (im=0,fh=0,zero(dfh,np),zero(ddfh,np*np); im<nm; im++) {
         Bmx=GetBmx (ninter, nsum, im, M, nodeb);
         S = com.SSave[im];
         Er = com.ErSave[im]*Bmx;
         y=1./(alpha-c*S);
         fh += Er;
         y1=Er*alpha*y;
         for (j=0,y2=y1*(1+alpha)*y*c*c; j<nbranch; j++) {
            if (M[j]) {
               dfh[j]+=y1*Root[M[j]]*c;                           /* t  */
               for (i=j; i<nbranch; i++)                          /* tt */
                  if (M[i]) ddfh[i*np+j]+=y2*Root[M[i]]*Root[M[j]];
            }
         }
         if (!com.fix_kappa) {
            for (j=0,s1=0,s2=0; j<nbranch; j++)
               if (M[j]) { s1+=x[j]*drk1[M[j]];  s2+=x[j]*drk2[M[j]]; }
            k=com.ntime+com.nrgene;
            dfh[k] += c*y1*s1;                                    /* k  */
            for (j=0,y2=y*s1*(alpha+1); j<nbranch; j++)  if (M[j])
               ddfh[k*np+j] += c*y1*(Root[M[j]]*y2*c+drk1[M[j]]); /* kt */
            ddfh[k*np+k] += y1*c*(c*s1*y2+s2);                    /* kk */
         }
         if (com.ngene>0 && igene>0) {
            k=com.ntime+igene-1;
            dfh[k]+=y1*S;                                         /* c  */
            ddfh[k*np+k]+=y*y1*S*S*(1+alpha);                      /* cc */
            y2=alpha*y*y1*(1+c*S);
            FOR (j,nbranch)  ddfh[k*np+j]+=y2*Root[M[j]];         /* ct */
            if (!com.fix_kappa)
               ddfh[(com.ntime+com.nrgene)*np+k]+=y2*s1;          /* ck */
         }
         if (!com.fix_alpha) {
            Ea = com.EaSave[im];
            dfh[np-1] += Er*Ea;                                   /* a  */
            ddfh[np*np-1]+=Er*(Ea*Ea+1/alpha-y+c*S*y*y);           /* aa */
            y2=Er*y*(Ea*alpha-c*S*y);
            FOR (j,nbranch)  ddfh[(np-1)*np+j]+=c*Root[M[j]]*y2;  /* at */
            if (com.ngene>0 && igene>0)
               ddfh[(np-1)*np+nbranch+igene-1]+=S*y2;             /* ac */
            if (!com.fix_kappa)
               ddfh[(np-1)*np+com.ntime+com.nrgene] += c*y2*s1;   /* ak */
         }
      }  /* for (im) */
      if (fh<=0) printf ("\a\nlfunG_dd: h=%4d  fh=%9.4f \n", h, fh);
      *lnL -= log(fh)*com.fpatt[h];
      FOR (j, np) dl[j] -= dfh[j]/fh*com.fpatt[h];
      FOR (j, np) for (i=j; i<np; i++) {
         ddl[i*np+j] -=
             (fh*ddfh[i*np+j]-dfh[i]*dfh[j])/(fh*fh)*com.fpatt[h];
         ddl[j*np+i] = ddl[i*np+j];
      }
   }    /* for (h) */
   return(0);
}

int GetOptions (char *ctlf)
{
   int i, nopt=27, lline=255;
   char line[255], *pline, opt[32], *comment="*#";
   char *optstr[]={"seqfile","outfile","treefile", "noisy",
        "cleandata", "ndata", "verbose","runmode",
        "clock","fix_rgene","Mgene","nhomo","getSE","RateAncestor",
        "model","fix_kappa","kappa","fix_alpha","alpha","Malpha","ncatG", 
        "fix_rho","rho","nparK", "Small_Diff", "method", "fix_blength"};
   double t;
   FILE  *fctl=fopen (ctlf, "r");

   if (fctl) {
      if (noisy) printf ("\n\nReading options from %s..\n", ctlf);
      for (;;) {
         if (fgets (line, lline, fctl) == NULL) break;
         for (i=0,t=0,pline=line; i<lline&&line[i]; i++)
            if (isalnum(line[i]))  { t=1; break; }
            else if (strchr(comment,line[i])) break;
         if (t==0) continue;
         sscanf (line, "%s%*s%lf", opt, &t);
         if ((pline=strstr(line, "="))==NULL) error2("option file.");

         for (i=0; i<nopt; i++) {
            if (strncmp(opt, optstr[i], 8)==0)  {
               if (noisy>2)
                  printf ("\n%3d %15s | %-20s %6.2f", i+1,optstr[i],opt,t);
               switch (i) {
                  case ( 0): sscanf(pline+2, "%s", com.seqf);    break;
                  case ( 1): sscanf(pline+2, "%s", com.outf);    break;
                  case ( 2): sscanf(pline+2, "%s", com.treef);   break;
                  case ( 3): noisy=(int)t;           break;
                  case ( 4): com.cleandata=(int)t;   break;
                  case ( 5):                         break;   /* ndata */
                  case ( 6): com.verbose=(int)t;     break;
                  case ( 7): com.runmode=(int)t;     break;
                  case ( 8): com.clock=(int)t;       break;
                  case ( 9):                         break;  /* fix_rgene */
                  case (10): com.fix_rgene=(int)t;   break;
                  case (11): com.nhomo=(int)t;       break;
                  case (12): com.getSE=(int)t;       break;
                  case (13): com.print=(int)t;       break;
                  case (14): com.model=(int)t;       break;
                  case (15): com.fix_kappa=(int)t;   break;
                  case (16): com.kappa=t;            break;
                  case (17): com.fix_alpha=(int)t;   break;
                  case (18): com.alpha=t;            break;
                  case (19):                         break;  /* Malpha */
                  case (20): com.ncatG=(int)t;       break;
                  case (21): com.fix_rho=(int)t;     break;
                  case (22): com.rho=t;              break;
                  case (23): com.nparK=(int)t;       break;
                  case (24):                         break;   /* smallDiff */
                  case (25):                         break;   /* method */
                  case (26):                         break;   /* fix_blength */
               }
               break;
            }
         }
         if (i==nopt)
            { printf ("\noption %s in %s\n", opt, ctlf);  exit (-1); }
      }
      fclose (fctl);
   }
   else
      if (noisy) printf ("\nno ctl file..");

   if (com.runmode)  error2("runmode!=0 for BASEMLG?");
   if (com.model!=F84 && com.kappa<=0)  error2("init kappa..");
   if (com.alpha<=0) error2("init alpha..");
   if (com.alpha==0 || com.Malpha || com.rho>0 || com.nhomo>0 || com.nparK>0 
      || com.model>HKY85)
       error2 ("\noptions in file baseml.ctl inappropriate.. giving up..");
   if (com.model==JC69 || com.model==F81) { com.fix_kappa=1; com.kappa=1; }
   if(com.cleandata==0) { 
      puts("cleandata set to 1, with ambiguity data removed. ");
      com.cleandata=1;
   }
   return (0);
}


/*
28 July 2002.
I have not checked the program carefully since I implemented T92.  Models up to 
HKY85 should be fine.
*/
