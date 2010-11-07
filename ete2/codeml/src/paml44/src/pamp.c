/* PAMP.c, Copyright, Ziheng Yang, April 1995.
   Specify the sequence type in the file pamp.ctl.  Results go into mp.

                    gcc -o pamp pamp.c tools.o
                    pamp <ControlFileName>
*/

#include "paml.h"

#define NS            2000
#define NBRANCH       (NS*2-2)
#define NNODE         (NS*2-1)
#define MAXNSONS      10
#define NGENE         2000
#define LSPNAME       30
#define NCODE         20
#define NCATG         16

double DistanceREV (double Ft[], int n, double alpha, double Root[], double U[],
   double V[], double pi[], double space[], int *cond);
int PMatBranch (double Ptb[], int n, double branch[], 
    double Root[], double U[], double V[], double space[]);
int PatternLS (FILE *fout, double Ft[],double alpha, double space[], int *cond);
int testx (double x[], int np);
int GetOptions (char *ctlf);
int AlphaMP (FILE* fout);
int PatternMP (FILE *fout, double Ft[]);
int PathwayMP1 (FILE *fout, int *maxchange, int NSiteChange[], 
    double Ft[], double space[], int job);
double lfunAlpha_Sullivan (double x);
double lfunAlpha_YK96 (double x);

struct CommonInfo {
   char *z[NS], *spname[NS], seqf[256],outf[256],treef[256];
   int seqtype, ns, ls, ngene, posG[NGENE+1],lgene[NGENE],*pose,npatt, readpattern;
   int np, ntime, ncode,fix_kappa,fix_rgene,fix_alpha, clock, model, ncatG, cleandata;
   int print, nhomo;
   double *fpatt, *conP;
   /* not used */
   double lmax,pi[NCODE], kappa,alpha,rou, rgene[NGENE],piG[NGENE][NCODE];
}  com;
struct TREEB {
   int nbranch, nnode, root, branches[NBRANCH][2];
   double lnL;
}  tree;
struct TREEN {
   int father, nson, sons[MAXNSONS], ibranch;
   double branch, age, label, *conP;
   char *nodeStr, fossil;
}  *nodes;


#define NCATCHANGE 100
extern int noisy, *ancestor;
extern double *SeqDistance;
int maxchange, NSiteChange[NCATCHANGE];
double MuChange;
int LASTROUND=0; /* no use for this */

#define LSDISTANCE
#define REALSEQUENCE
#define NODESTRUCTURE
#define RECONSTRUCTION
#define PAMP
#include "treesub.c"

int main (int argc, char *argv[])
{
   FILE *ftree, *fout, *fseq;
   char ctlf[32]="pamp.ctl";
   char *Seqstr[]={"nucleotide", "", "amino-acid", "Binary"};
   int itree, ntree, i, j, s3;
   double *space, *Ft;

   com.nhomo=1;  com.print=1;
   noisy=2;  com.ncatG=8;   com.clock=0; com.cleandata=1;
   starttimer();
   GetOptions(ctlf);
   if(argc>1) { strcpy(ctlf, argv[1]); printf("\nctlfile set to %s.\n",ctlf);}

   printf("PAMP in %s\n",  VerStr);
   if ((fseq=fopen(com.seqf, "r"))==NULL) error2 ("seqfile err.");
   if ((fout=fopen (com.outf, "w"))==NULL) error2("outfile creation err.");
   if((fseq=fopen (com.seqf,"r"))==NULL)  error2("No sequence file!");
   ReadSeq (NULL, fseq, com.cleandata);
   SetMapAmbiguity();
   i=(com.ns*2-1)*sizeof(struct TREEN);
   if((nodes=(struct TREEN*)malloc(i))==NULL) error2("oom");

   fprintf (fout,"PAMP %15s, %s sequences\n", com.seqf, Seqstr[com.seqtype]);
   if (com.nhomo) fprintf (fout, "nonhomogeneous model\n");

   space = (double*)malloc(1000000*sizeof(double));  /* not safe */
   SeqDistance=(double*)malloc(com.ns*(com.ns-1)/2*sizeof(double));
   ancestor=(int*)malloc(com.ns*(com.ns-1)/2*sizeof(int));
   if (SeqDistance==NULL||ancestor==NULL) error2("oom");

   i = com.ns*(com.ns-1)/2;
   s3 = sizeof(double)*((com.ns*2-2)*(com.ns*2-2 + 4 + i) + i);
   s3 = max2(s3, com.ncode*com.ncode*(2*com.ns-2+1)*(int)sizeof(double));

   Ft = (double*) malloc(s3);
   if (space==NULL || Ft==NULL)  error2 ("oom space");

   InitializeBaseAA (fout);
   if (com.ngene>1) error2 ("option G not allowed yet");

/*
   PatternLS (fout, Ft, 0., space, &i);
   printf ("\nPairwise estimation of rate matrix done..\n");
   fflush(fout);
*/
   ftree=gfopen (com.treef,"r");
   fscanf (ftree, "%d%d", &i, &ntree);
   if (i!=com.ns) error2 ("ns in the tree file");

   for(itree=0; itree<ntree; itree++) {

      printf ("\nTREE # %2d\n", itree+1);
      fprintf (fout,"\nTREE # %2d\n", itree+1);

      if (ReadTreeN (ftree, &i,&j, 0, 1)) error2 ("err tree..");
      OutTreeN (F0, 0, 0);    FPN (F0); 
      OutTreeN (fout, 0, 0);  FPN (fout);

      for (i=0,maxchange=0; i<NCATCHANGE; i++) NSiteChange[i]=0;

      PathwayMP1 (fout, &maxchange, NSiteChange, Ft, space, 0);
      printf ("\nHartigan reconstruction done..\n");

      fprintf (fout, "\n\n(1) Branch lengths and substitution pattern\n");
      PatternMP (fout, Ft);
      printf ("pattern done..\n");    fflush(fout);

      fprintf (fout, "\n\n(2) Gamma parameter\n");
      AlphaMP (fout);
      printf ("gamma done..\n");      fflush(fout);

      fprintf (fout, "\n\n(3) Parsimony reconstructions\n");
      PathwayMP1 (fout, &maxchange, NSiteChange, Ft, space, 1);
      printf ("Yang reconstruction done..\n");    fflush(fout);
   }
   free(nodes);
   return (0);
}

int GetOptions (char *ctlf)
{
   int iopt, nopt=6, i, lline=4096, t;
   char line[4096], *pline, opt[32], *comment="*#";
   char *optstr[] = {"seqfile","outfile","treefile", "seqtype", "ncatG", "nhomo"};
   FILE  *fctl=gfopen (ctlf, "r");

   if (fctl) {
      for (;;) {
         if (fgets (line, lline, fctl) == NULL) break;
         for (i=0,t=0; i<lline&&line[i]; i++)
            if (isalnum(line[i]))  { t=1; break; }
            else if (strchr(comment,line[i])) break;
         if (t==0) continue;
         sscanf (line, "%s%*s%d", opt, &t);
         if ((pline=strstr(line, "="))==NULL) error2 ("option file.");

         for (iopt=0; iopt<nopt; iopt++) {
            if (strncmp(opt, optstr[iopt], 8)==0)  {
               if (noisy>2)
                  printf ("\n%3d %15s | %-20s %6d", iopt+1,optstr[iopt],opt,t);
               switch (iopt) {
                  case ( 0): sscanf(pline+2, "%s", com.seqf);    break;
                  case ( 1): sscanf(pline+2, "%s", com.outf);    break;
                  case ( 2): sscanf(pline+2, "%s", com.treef);    break;
                  case  (3): com.seqtype=t;   break;
                  case  (4): com.ncatG=t;     break;
                  case  (5): com.nhomo=t;     break;
               }
               break;
            }
         }
         if (iopt==nopt)
            { printf ("\nopt %s in %s\n", opt, ctlf);  exit (-1); }
      }
      fclose (fctl);
   }
   else
      if (noisy) printf ("\nno ctl file..");

   if (com.seqtype==0)       com.ncode=4;
   else if (com.seqtype==2)  com.ncode=20;
   else if (com.seqtype==3)  com.ncode=2;
   else                      error2("seqtype");
   if (com.ncatG>NCATG) error2 ("raise NCATG?");
   return (0);
}


int AlphaMP (FILE* fout)
{
   int k, ntotal;
   double x, xb[2], lnL, var;

   xb[0]=1e-3; xb[1]=99; /* alpha */
 
   fprintf (fout, "\n# changes .. # sites");
   for (k=0,ntotal=0,MuChange=var=0; k<maxchange+1; k++) {
      fprintf (fout, "\n%6d%10d", k, NSiteChange[k]);
      ntotal+=NSiteChange[k];  MuChange+=k*NSiteChange[k];   
      var+=k*k*NSiteChange[k];
   }
   MuChange/=ntotal;   
   var=(var-MuChange*MuChange*ntotal)/(ntotal-1.);
   x=MuChange*MuChange/(var-MuChange);
   fprintf (fout, "\n\n# sites%6d,  total changes%6d\nmean-var%9.4f%9.4f",
            ntotal, (int)(ntotal*MuChange+.5), MuChange, var);
   fprintf (fout, "\nalpha (method of moments)%9.4f", x);
   if (x<=0) x=9;

   LineSearch(lfunAlpha_Sullivan, &lnL, &x, xb, 0.02, 1e-8);
   fprintf (fout, "\nalpha (Sullivan et al. 1995)%9.4f\n", x);

   MuChange/=tree.nbranch; 
   LineSearch(lfunAlpha_YK96, &lnL, &x, xb, 0.02, 1e-8);
   fprintf (fout, "alpha (Yang & Kumar 1995, ncatG= %d)%9.4f\n", com.ncatG,x);
   return (0);
}

double lfunAlpha_Sullivan (double x)
{
   int k;
   double lnL=0, a=x, t;

   FOR (k, maxchange+1) { 
      if (NSiteChange[k]==0) continue;
      t=-a*log(1+MuChange/a);
      if (k)  
         t+=LnGamma(k+a)-LnGamma(k+1.) - LnGamma(a) 
          + k*log(MuChange/a/(1+MuChange/a));
      lnL += NSiteChange[k]*t;
   }
   return(-lnL);
}

double lfunAlpha_YK96 (double x)
{
   int k, ir, b=tree.nbranch, n=com.ncode;
   double lnL=0, prob, a=x, t=MuChange, p;
   double freqK[NCATG], rK[NCATG];

   DiscreteGamma (freqK, rK, a, a, com.ncatG, 0);
   FOR (k, maxchange+1) {
      if (NSiteChange[k]==0) continue;
      for (ir=0,prob=0; ir<com.ncatG; ir++) {
         p=1./n+(n-1.)/n*exp(-n/(n-1.)*rK[ir]*t);
         prob+=freqK[ir]*pow(p,(double)(b-k))*pow((1-p)/(n-1.),(double)k);
      }
      lnL += NSiteChange[k]*log(prob);
   }
   return (-lnL);
}


int OutQ (FILE *fout, int n, double Q[], double pi[], double Root[],
    double U[], double V[], double space[])
{
   char aa3[4]="";
   int i,j;
   double *T1=space, t;

   fprintf(fout,"\nrate matrix Q: Qij*dt = prob(i->j; dt)\n");
   if (n<=4) {
/*      matout (fout, pi, 1, n); */
      matout (fout, Q, n, n);
      if (n==4) {
         fprintf (fout, "Order: T, C, A, G");
         t=pi[0]*Q[0*4+1]+pi[1]*Q[1*4+0]+pi[2]*Q[2*4+3]+pi[3]*Q[3*4+2];
         fprintf (fout, "\nAverage Ts/Tv =%9.4f\n", t/(1-t));
      }
   }
   else if (n==20) {
      for (i=0; i<n; i++,FPN(fout))
         FOR (j,n) fprintf (fout, "%6.0f", Q[i*n+j]*100);
/*
      FOR (i,n) {
         fprintf (fout,"\n%-4s", getAAstr(aa3,i));
         FOR (j,i) fprintf (fout, "%4.0f", Q[i*n+j]/pi[j]*100);
         fprintf (fout, "%4.0f", -Q[i*n+i]*100);
      }
      fputs("\n     ",fout);  FOR(i,naa) fprintf(fout,"%5s",getAAstr(aa3,i));
*/
      fprintf (fout, "\n\nPAM matrix, P(0.01)\n"); 
      FOR (i,n) FOR (j,n) T1[i*n+j]=U[i*n+j]*exp(0.01*Root[j]);
      matby (T1, V, Q, n, n, n);
      FOR (i,n*n) if (Q[i]<0) Q[i]=0;
      FOR (i,n) {
         fprintf (fout,"\n%-4s", getAAstr(aa3,i));
         FOR(j,n) fprintf(fout, "%6.0f", Q[i*n+j]*10000);
      }
      fputs("\n     ",fout);  FOR(i,n) fprintf(fout,"%5s",getAAstr(aa3,i));
   }
   return (0);
}

int PMatBranch (double Ptb[], int n, double branch[], 
    double Root[], double U[], double V[], double space[])
{
/* homogeneised transition prob matrix, with one Q assumed for the whole tree
*/
   int i, j, k;
   double *T1=space, *P;

   FOR (k, tree.nbranch) {
      P=Ptb+k*n*n;
      FOR (i,n) FOR (j,n) T1[i*n+j]=U[i*n+j]*exp(Root[j]*branch[k]);
      matby (T1, V, P, n, n, n);
      FOR (i,n*n) if (P[i]<0) P[i]=0;
/*
      printf ("\nbranch %d, P(%.5f)", k+1, branch[k]);
      matout (F0, P, n, n);
      testTransP (P, n);
*/
   }
   return (0);
}


int PatternMP (FILE *fout, double Ft[])
{
/* Ft[]: input counts for the F(t) matrix for each branch, output P(t) 
*/
   int n=com.ncode, i,j,k;
   double *Q, *pi, *Root, *U, *V, *branch, *space, *T1, t;

   if((Q=(double*)malloc((n*n*6+tree.nbranch)*sizeof(double)))==NULL)
      error2("PathwayMP: oom");
   pi=Q+n*n; Root=pi+n; U=Root+n; V=U+n*n; branch=V+n*n; 
   space=T1=branch+tree.nbranch;

   for (k=0; k<tree.nbranch; k++) {  /* branch lengths */
      xtoy(Ft+k*n*n, Q, n*n);
      branch[k]=nodes[tree.branches[k][1]].branch=
         DistanceREV(Q, n, 0, Root, U, V, pi, space, &j);
   }
   OutTreeB (fout);  FPN (fout);
   FOR (i, tree.nbranch) fprintf(fout,"%9.5f", branch[i]);
   fprintf (fout,"\ntree length: %9.5f\n", sum(branch,tree.nbranch));

   /* pattern Q from average F(t) */
   fprintf(fout,"\nF(t)");
   xtoy (Ft+tree.nbranch*n*n, Q, n*n);
   matout2 (fout, Q, n, n, 12, 2);
   DistanceREV (Q, n, 0, Root, U, V, pi, space, &j);
   if (noisy>=3&&j==-1) { puts("F(t) modified in DistanceREV"); }

   OutQ (fout, n, Q, pi, Root, U, V, T1);
   if (com.nhomo==0) 
      PMatBranch (Ft, n, branch, Root, U, V, space);
   else {
      for (k=0; k<tree.nbranch; k++) {
         for (i=0; i<n; i++) {
            t=sum(Ft+k*n*n+i*n, n);
            if (t>1e-5) abyx (1/t, Ft+k*n*n+i*n, n);
            else        Ft[k*n*n+i*n+i]=1;
         }
      }
   }
   free(Q);
   return (0); 
}


int PathwayMP1 (FILE *fout, int *maxchange, int NSiteChange[], 
    double Ft[], double space[], int job)
{
/* Hartigan, JA.  1973.  Minimum mutation fits to a given tree. 
   Biometrics, 29:53-65.
   Yang, Z.  1996.  
   job=0: 1st pass: calculates maxchange, NSiteChange[], and Ft[]
   job=1: 2nd pass: reconstructs ancestral character states (->fout)
*/
   char *pch=(com.seqtype==0?BASEs:(com.seqtype==2?AAs:BINs));
   char *zz[NNODE],nodeb[NNODE],bestPath[NNODE-NS],Equivoc[NS-1];
   int n=com.ncode, nid=tree.nbranch-com.ns+1, it,i1,i2, i,j,k, h, hp,npath;
   int *Ftt=NULL, nchange, nchange0, visit[NS-1]={0};
   double sumpr, bestpr, pr, *pnode=NULL, *pnsite;


   fputs("\nList of most parsimonious reconstructions (MPRs) at each site: #MPRs (#changes)\n",fout);
   fputs("and then the most likely reconstruction out of the MPRs and its probability\n",fout);
   if((pnsite=(double*)malloc((com.ns-1)*n*sizeof(double)))==NULL)
      error2("PathwayMP1: oom");

   PATHWay=(char*)malloc(nid*(n+3)*sizeof(char));
   NCharaCur=PATHWay+nid;  ICharaCur=NCharaCur+nid;  CharaCur=ICharaCur+nid;
   if (job==0) {
      zero(Ft,n*n*(tree.nbranch+1));
      if((Ftt=(int*)malloc(n*n*tree.nbranch*sizeof(int)))==NULL) error2("oom");
   }
   else {
      pnode=(double*)malloc((nid*com.npatt+1)*(sizeof(double)+sizeof(char)));
      FOR (j,nid) zz[com.ns+j]=(char*)(pnode+nid*com.npatt)+j*com.npatt;
      FOR (j,com.ns) zz[j]=com.z[j];
      if (pnode==NULL) error2 ("oom");
   }
   for (j=0,visit[i=0]=tree.root-com.ns; j<tree.nbranch; j++) 
      if (tree.branches[j][1]>=com.ns) 
         visit[++i]=tree.branches[j][1]-com.ns;

   for (h=0; h<com.ls; h++) {
      hp=com.pose[h];
      if (job==1) {
         fprintf (fout, "\n%4d  ", h+1);
         FOR (j, com.ns) fprintf (fout, "%c", pch[com.z[j][hp]]);
         fprintf (fout, ":  ");
         FOR (j,nid*n) pnsite[j]=0;
      }
      FOR (j,com.ns) nodeb[j]=com.z[j][hp];
      if (job==0) FOR (j,n*n*tree.nbranch) Ftt[j]=0;

      InteriorStatesMP (1, hp, &nchange, NCharaCur, CharaCur, space); 
      ICharaCur[j=tree.root-com.ns]=0;  PATHWay[j]=CharaCur[j*n+0];
      FOR (j,nid) Equivoc[j]=(NCharaCur[j]>1);

      if (nchange>*maxchange) *maxchange=nchange;
      if (nchange>NCATCHANGE-1) error2 ("raise NCATCHANGE");

      NSiteChange[nchange]++;
      /* NSiteChange[nchange]+=(int)com.fpatt[hp]; */

      DownStates (tree.root);
      for (npath=0,sumpr=bestpr=0; ;) {
         for (j=0,k=visit[nid-1]; j<NCharaCur[k]; j++) {
            PATHWay[k]=CharaCur[k*n+j]; npath++;
            FOR (i,nid) nodeb[i+com.ns]=PATHWay[i];
            if (job==1) {
               FOR (i,nid) fprintf(fout,"%c",pch[PATHWay[i]]); fputc(' ',fout);
               pr=com.pi[(int)nodeb[tree.root]];
               for (i=0; i<tree.nbranch; i++) {
                  i1=nodeb[tree.branches[i][0]];
                  i2=nodeb[tree.branches[i][1]];
                  pr*=Ft[i*n*n+i1*n+i2];
               }
               sumpr+=pr;
               FOR (i,nid) pnsite[i*n+nodeb[i+com.ns]]+=pr;
               if (pr>bestpr) 
                  { bestpr=pr; FOR(i,nid) bestPath[i]=PATHWay[i];}
            }
            else {
               for (i=0,nchange0=0; i<tree.nbranch; i++) {
                  i1=nodeb[tree.branches[i][0]]; 
                  i2=nodeb[tree.branches[i][1]];
                  if(i1!=i2) nchange0++;
                  Ftt[i*n*n+i1*n+i2]++;
               }
               if (nchange0!=nchange) {
                  printf("\a\nerr:PathwayMP %d != %d", nchange, nchange0); 
                  fprintf(fout,".%d. ", nchange0); /* ??? */
               }
            }
         }
         for (j=nid-2; j>=0; j--) {
            if(Equivoc[k=visit[j]] == 0) continue;
            if (ICharaCur[k]+1<NCharaCur[k]) {
               PATHWay[k] = CharaCur[k*n + (++ICharaCur[k])];
               DownStates (k+com.ns);
               break;
            }
            else { /* if (next equivocal node is not ancestor) update node k */
               for (i=j-1; i>=0; i--) if (Equivoc[(int)visit[i]]) break;
               if (i>=0) { 
                  for (it=k+com.ns,i=visit[i]+com.ns; ; it=nodes[it].father)
                     if (it==tree.root || nodes[it].father==i) break;
                  if (it==tree.root)
                     DownStatesOneNode (k+com.ns, nodes[k+com.ns].father);
               }
            }
         }
         if (j<0) break;
      }      /* for (npath) */
/*
      printf ("\rsite pattern %4d/%4d: %6d%6d", hp+1,com.npatt,npath,nchange);
*/      
      if (job==0) 
         FOR (j,n*n*tree.nbranch) Ft[j]+=(double)Ftt[j]/npath*com.fpatt[hp];
      else {
         FOR (i,nid) zz[com.ns+i][hp]=bestPath[i];
         FOR (i,nid) pnode[i*com.npatt+hp]=pnsite[i*n+bestPath[i]]/sumpr;
         fprintf (fout, " |%4d (%d) | ", npath, nchange);
         if (npath>1) {
            FOR (i,nid) fprintf (fout, "%c", pch[bestPath[i]]);
            fprintf (fout, " (%.3f)", bestpr/sumpr);

         }
      }
   }   /* for (h) */
   free(PATHWay); 
   if (job==0) {
      free(Ftt);
      FOR (i,tree.nbranch) FOR (j,n*n) Ft[tree.nbranch*n*n+j]+=Ft[i*n*n+j];
   }
   else {
      fprintf (fout,"\n\nApprox. relative accuracy at each node, by site\n");
      FOR (h, com.ls) {
         hp=com.pose[h];
         fprintf (fout,"\n%4d  ", h+1);
         FOR (j, com.ns) fprintf (fout, "%c", pch[com.z[j][hp]]);
         fprintf (fout, ":  ");
         FOR (i,nid) if (pnode[i*com.npatt+hp]<.99999) break;
         if (i<nid)  FOR (j, nid) 
            fprintf(fout,"%c (%5.3f) ", pch[zz[j][hp]],pnode[j*com.npatt+hp]);
      }
      /* Site2Pattern (fout); */
      fprintf (fout,"\n\nlist of extant and reconstructed sequences\n\n");
      for(j=0;j<tree.nnode;j++,FPN(fout)) {
         if(j<com.ns) fprintf(fout,"%-20s", com.spname[j]);
         else         fprintf(fout,"node #%-14d", j+1);
         print1seq (fout, zz[j], (com.readpattern?com.npatt:com.ls), com.pose);
      }
      free(pnode);
   }
   free(pnsite);
   return (0);
}

double DistanceREV (double Ft[], int n,double alpha,double Root[],double U[],
   double V[], double pi[], double space[], int *cond)
{
/* input:  Ft, n, alpha
   output: Q(in Ft), t, Root, U, V, and cond
   space[n*n*2]
*/
   int i,j, InApplicable;
   double *Q=Ft, *T1=space, *T2=space+n*n, t, pi_sqrt[20], small=0.1/com.ls;

   for (i=0,t=0; i<n; i++) FOR (j,n) if (i-j) t+=Q[i*n+j];
   if (t<small)  { *cond=1; zero(Q,n*n); return (0); }

   for(i=0;i<n;i++) for (j=0;j<i;j++) 
      Q[i*n+j]=Q[j*n+i]=(Q[i*n+j]+Q[j*n+i])/2;

   abyx(1./sum(Q,n*n), Q, n*n);
   for(i=0;i<n;i++) {
      pi[i]=sum(Q+i*n, n);
      if(pi[i]>small) 
         abyx(1/pi[i], Q+i*n, n); 
   }

   eigenQREV(Q, pi, n, Root, U, V, pi_sqrt);
   for(i=0,InApplicable=0; i<n; i++) {
      if (Root[i]<=0)  {
         InApplicable=1;
         Root[i]=-300;  /* adhockery */
      }
      else 
         Root[i]=(alpha<=0?log(Root[i]):gammap(Root[i],alpha));
   }
   FOR (i,n) FOR (j,n) T1[i*n+j]=U[i*n+j]*Root[j];
   matby (T1, V, Q, n, n, n);
   for (i=0,t=0; i<n; i++) t-=pi[i]*Q[i*n+i];

   if(noisy>=9 && InApplicable) printf("Root(P)<0.  adhockery invoked\n"); 
   if(t<=0) error2("err: DistanceREV");

   FOR (i,n) Root[i]/=t;
   FOR (i, n) FOR (j,n)  { Q[i*n+j]/=t; if (i-j) Q[i*n+j]=max2(0,Q[i*n+j]); }

   return (t);
}


int PatternLS (FILE *fout, double Ft[], double alpha,double space[],int *cond)
{
/* space[n*n*2]
*/
   int n=com.ncode, i,j,k,h, it;
   double *Q=Ft,*Qt=Q+n*n,*Qm=Qt+n*n;
   double *pi,*Root,*U, *V, *T1=space, *branch, t;
   FILE *fdist=gfopen("Distance", "w");
   
   if((pi=(double*)malloc((n*n*3+tree.nbranch)*sizeof(double)))==NULL)
      error2("PatternLS: oom");
   Root=pi+n;  U=Root+n; V=U+n*n; branch=V+n*n;

   *cond=0;
   for (i=0,zero(Qt,n*n),zero(Qm,n*n); i<com.ns; i++) {
      for (j=0; j<i; j++) {
         for (h=0,zero(Q,n*n); h<com.npatt; h++) {
	    Q[(com.z[i][h])*n+com.z[j][h]] += com.fpatt[h]/2;
            Q[(com.z[j][h])*n+com.z[i][h]] += com.fpatt[h]/2;
	 }
         FOR (k,n*n) Qt[k]+=Q[k]/(com.ns*(com.ns-1)/2);
         it=i*(i-1)/2+j;
	 SeqDistance[it]=DistanceREV (Q, n, alpha, Root,U,V, pi, space, &k);

         if (k==-1) { 
            *cond=-1; printf("\n%d&%d: F(t) modified in DistanceREV",i+1,j+1);
         }

	 fprintf(fdist,"%9.5f",SeqDistance[it]);
/*
FOR (k,n) 
if (Q[k*n+k]>0) { printf ("%d %d %.5f\n", i+1, j+1, Q[k*n+k]); }
*/
         FOR (k,n*n) Qm[k]+=Q[k]/(com.ns*(com.ns-1)/2); 
      }
      FPN(fdist);
   }
   fclose (fdist);
   DistanceREV (Qt, n, alpha, Root, U, V, pi, space, &k);
   if (k==-1) { puts ("F(t) modified in DistanceREV"); }

   fprintf (fout, "\n\nQ: from average F over pairwise comparisons");
   OutQ(fout, n, Qt, pi, Root, U, V, T1);
   fprintf (fout, "\n\nQ: average of Qs over pairwise comparisons\n");
   fprintf (fout, "(disregard this if very different from the previous Q)");
   OutQ (fout, n, Qm, pi, Root, U, V, T1);

   if (tree.nbranch) {
      fillxc (branch, 0.1, tree.nbranch);
      LSDistance (&t, branch, testx);
      OutTreeB (fout);  FPN (fout);
      FOR (i,tree.nbranch) fprintf(fout,"%9.5f", branch[i]);
      PMatBranch (Ft, com.ncode, branch, Root, U, V, space);
   }
   free(pi);
   return (0);
}

int testx (double x[], int np)
{
   int i;
   double tb[]={1e-5, 99};
   FOR(i,np) if(x[i]<tb[0] ||x[i]>tb[1]) return(-1);
   return(0);
}

int SetBranch (double x[])
{
   int i, status=0;
   double small=1e-5;

   FOR (i,tree.nnode)
      if (i!=tree.root && (nodes[i].branch=x[nodes[i].ibranch])<-small)
         status=-1;
   return (status);
}
