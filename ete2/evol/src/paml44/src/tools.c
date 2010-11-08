/* tools.c 
*/
#include "paml.h"

/************************
             sequences 
*************************/

char BASEs[]="TCAGUYRMKSWHBVD-N?";
char *EquateBASE[]={"T","C","A","G", "T", "TC","AG","CA","TG","CG","TA",
     "TCA","TCG","CAG","TAG", "TCAG","TCAG","TCAG"};
char CODONs[256][4], AAs[] = "ARNDCQEGHILKMFPSTWYV-*?X";
char nChara[256], CharaMap[256][64];
char AA3Str[]= {"AlaArgAsnAspCysGlnGluGlyHisIleLeuLysMetPheProSerThrTrpTyrVal***"};
char BINs[] = "TC";
int GeneticCode[][64] = 
     {{13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,-1,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 0:universal */

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,17,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9,12,12,16,16,16,16, 2, 2,11,11,15,15,-1,-1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 1:vertebrate mt.*/

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,17,17,
       16,16,16,16,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9,12,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 2:yeast mt. */

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,17,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 3:mold mt. */

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,17,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9,12,12,16,16,16,16, 2, 2,11,11,15,15,15,15,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 4:invertebrate mt. */

      {13,13,10,10,15,15,15,15,18,18, 5, 5, 4, 4,-1,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 5:ciliate nuclear*/

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,17,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2, 2,11,15,15,15,15,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 6:echinoderm mt.*/

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4, 4,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 7:euplotid mt. */

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,-1,17,
       10,10,10,15,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7},
                                                 /* 8:alternative yeast nu.*/

      {13,13,10,10,15,15,15,15,18,18,-1,-1, 4, 4,17,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9,12,12,16,16,16,16, 2, 2,11,11,15,15, 7, 7,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 9:ascidian mt. */

      {13,13,10,10,15,15,15,15,18,18,-1, 5, 4, 4,-1,17,
       10,10,10,10,14,14,14,14, 8, 8, 5, 5, 1, 1, 1, 1,
        9, 9, 9,12,16,16,16,16, 2, 2,11,11,15,15, 1, 1,
       19,19,19,19, 0, 0, 0, 0, 3, 3, 6, 6, 7, 7, 7, 7}, /* 10:blepharisma nu.*/

      { 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4,
        5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8,
        9, 9, 9, 9,10,10,10,10,11,11,11,11,12,12,12,12,
       13,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16} /* 11:Ziheng's regular code */
     };                                         /* GeneticCode[icode][#codon] */



int noisy=0, Iround=0, NFunCall=0, NEigenQ, NPMatUVRoot;
double SIZEp=0;

int blankline (char *str)
{
   char *p=str;
   while (*p) if (isalnum(*p++)) return(0);
   return(1);
}

int PopEmptyLines (FILE* fseq, int lline, char line[])
{
/* pop out empty lines in the sequence data file.
   returns -1 if EOF.
*/
   char *eqdel=".-?", *p;
   int i;

   for (i=0; ;i++) {
      p = fgets (line, lline, fseq);
      if (p==NULL) return(-1);
      while (*p) 
         if (*p==eqdel[0] || *p==eqdel[1] || *p==eqdel[2] || isalpha(*p)) 
/*
         if (*p==eqdel[0] || *p==eqdel[1] || *p==eqdel[2] || isalnum(*p)) 
*/
            return(0);
         else p++;
   }
}


int picksite (char *z, int l, int begin, int gap, char *result)
{
/* pick every gap-th site, e.g., the third codon position for example.
*/
   int il=begin;

   for (il=0, z+=begin; il<l; il+=gap,z+=gap) *result++ = *z;
   return(0);
}

int CodeChara (char b, int seqtype)
{
/* This codes nucleotides or amino acids into 0, 1, 2, ...
*/
   int i, n=(seqtype<=1?4:(seqtype==2?20:2));
   char *pch=(seqtype<=1?BASEs:(seqtype==2?AAs:BINs));

   if (seqtype<=1)
      switch (b) {
         case 'T':  case 'U':   return(0);
         case 'C':              return(1);
         case 'A':              return(2);
         case 'G':              return(3);
      }
   else
      for(i=0; i<n; i++)
		  if (b==pch[i]) return (i);
   if(noisy>=9) printf ("\nwarning: strange character '%c' ", b);
   return (-1);
}

int dnamaker (char z[], int ls, double pi[])
{
/* sequences z[] are coded 0,1,2,3
*/
   int i, j;
   double p[4], r, small=1e-5;

   xtoy(pi, p, 4);
   for (i=1; i<4; i++) p[i]+=p[i-1];
   if(fabs(p[3]-1)>small) error2("sum pi != 1..");
   for(i=0; i<ls; i++) {
      for(j=0,r=rndu(); j<4; j++) if(r<p[j]) break;
      z[i]=(char)j;
   }
   return (0);
}

int transform (char *z, int ls, int direction, int seqtype)
{
/* direction==1 from TCAG to 0123, ==0 from 0123 to TCGA.
*/
   int il, status=0;
   char *p, *pch=((seqtype==0||seqtype==1)?BASEs:(seqtype==2?AAs:BINs));

   if (direction)
      for (il=0,p=z; il<ls; il++,p++) {
         if ((*p=(char)CodeChara(*p, seqtype)) == (char)(-1))  status=-1;
      }
   else 
      for (il=0,p=z; il<ls; il++,p++)  *p = pch[(int) (*p)];
   return (status);
}


int f_mono_di (FILE *fout, char *z, int ls, int iring,
    double fb1[], double fb2[], double CondP[])
{
/* get mono- di- nucleitide frequencies.
*/
   int i,j, il;
   char *s;
   double t1, t2;

   t1 = 1./(double) ls;  
   t2=1./(double) (ls-1+iring);
   for (i=0; i<4; fb1[i++]=0.0) for (j=0; j<4; fb2[i*4+j++]=0.0) ;
   for (il=0, s=z; il<ls-1; il++, s++) {
      fb1[*s-1] += t1;
      fb2[(*s-1)* 4 + *(s+1)-1 ] += t2;
   }
   fb1[*s-1] += t1;
   if (iring) fb2[(*s-1)*4 + z[0]-1] += t2;
   for (i=0; i<4; i++)  for (j=0; j<4; j++) CondP[i*4+j] = fb2[i*4+j]/fb1[i];
   fprintf(fout, "\nmono-\n") ;
   FOR (i,4) fprintf(fout, "%12.4f", fb1[i]) ;   
   fprintf(fout, "\n\ndi-  & conditional P\n") ;       
   FOR (i,4) {
      FOR (j,4) fprintf(fout, "%9.4f%7.4f  ", fb2[i*4+j], CondP[i*4+j]) ;
      FPN(fout);
   }
   FPN(fout);
   return (0);
}

int PickExtreme (FILE *fout, char *z, int ls, int iring, int lfrag, int *ffrag)
{
/* picking up (lfrag)-tuples with extreme frequencies.
*/
   char *pz=z;
   int i, j, isf, n=(1<<2*lfrag), lvirt=ls-(lfrag-1)*(1-iring);
   double fb1[4], fb2[4*4], p_2[4*4];
   double prob1, prob2, ne1, ne2, u1, u2, ualpha=2.0;
   int ib[10];

   f_mono_di(fout, z, ls, iring, fb1, fb2, p_2 );
   if (iring) {
      error2("change PickExtreme()");
      FOR (i, lfrag-1)  z[ls+i]=z[i];       /* dangerous */
      z[ls+i]=(char) 0;
   }
   printf ("\ncounting %d tuple frequencies", lfrag);
   FOR (i, n) ffrag[i]=0;
   for (i=0; i<lvirt; i++, pz++) {
      for (j=0,isf=0; j<lfrag; j++)  isf=isf*4+(int)pz[j]-1;
      ffrag[isf] ++;
   }
   /* analyze */
   for (i=0; i<n; i++) {
      for (j=0,isf=i; j<lfrag; ib[lfrag-1-j]=isf%4,isf=isf/4,j++) ;
      for (j=0,prob1=1.0; j<lfrag; prob1 *= fb1[ ib[j++] ] ) ;
      for (j=0,prob2=fb1[ib[0]]; j<lfrag-1; j++)
         prob2 *= p_2[ib[j]*4+ib[j+1]];
      ne1 = (double) lvirt * prob1;
      ne2 = (double) lvirt * prob2;
      if (ne1<=0.0) ne1=0.5;
      if (ne2<=0.0) ne2=0.5;
      u1=((double) ffrag[i]-ne1) / sqrt (ne1);
      u2=((double) ffrag[i]-ne2) / sqrt (ne2);
      if ( fabs(u1)>ualpha /* && fabs(u2)>ualpha */ ) {
         fprintf (fout,"\n");
         FOR (j, lfrag) fprintf (fout,"%1c", BASEs[ib[j]]);
         fprintf (fout,"%6d %8.1f%7.2f %8.1f%7.2f ",ffrag[i],ne1,u1,ne2,u2);
         if (u1<-ualpha && u2<-ualpha)     fprintf (fout, " %c", '-');
         else if (u1>ualpha && u2>ualpha)  fprintf (fout, " %c", '+');
         else if (u1*u2<0 && fabs(u1) > ualpha && fabs(u2) > ualpha)
            fprintf (fout, " %c", '?');
         else
            fprintf (fout, " %c", ' ');
      }
   }
   return (0);
}

int zztox ( int n31, int l, char *z1, char *z2, double *x )
{
/*   x[n31][4][4]   */
   double t = 1./(double) (l / n31);
   int i, ib[2];
   int il;

   zero (x, n31*16);
   for (i=0; i<n31; i++)  {
      for (il=0; il<l; il += n31) {
         ib[0] = z1[il+i] - 1;
         ib[1] = z2[il+i] - 1;
         x [ i*16+ib[0]*4+ib[1] ] += t;
      }
/*
      fprintf (f1, "\nThe difference matrix X %6d\tin %6d\n", i+1,n31);
      for (j=0; j<4; j++) {
         for (k=0; k<4; k++) fprintf(f1, "%10.2f", x[i][j][k]);
         fputc ('\n', f1);
      }
*/
   }
   return (0);
}

int testXMat (double x[])
{
/* test whether X matrix is acceptable (0) or not (-1) */
   int it=0, i,j;
   double t;
   for (i=0,t=0; i<4; i++) FOR (j,4) {
      if (x[i*4+j]<0 || x[i*4+j]>1)  it=-1;
      t += x[i*4+j];
   }
   if (fabs(t-1) > 1e-4) it =-1;
   return(it);
}


int difcodonNG (char codon1[], char codon2[], double *SynSite,double *AsynSite, 
    double *SynDif, double *AsynDif, int transfed, int icode)
{
/* # of synonymous and non-synonymous sites and differences.
   Nei, M. and T. Gojobori (1986)
   returns the number of differences between two codons.
   The two codons (codon1 & codon2) do not contain ambiguity characters. 
   dmark[i] (=0,1,2) is the i_th different codon position, with i=0,1,ndiff
   step[j] (=0,1,2) is the codon position to be changed at step j (j=0,1,ndiff)
   b[i][j] (=0,1,2,3) is the nucleotide at position j (0,1,2) in codon i (0,1)

   I made some arbitrary decisions when the two codons have ambiguity characters
   20 September 2002.
*/
   int i,j,k, i1,i2, iy[2]={0}, iaa[2],ic[2];
   int ndiff,npath,nstop,sdpath,ndpath,dmark[3],step[3],b[2][3],bt1[3],bt2[3];
   int by[3] = {16, 4, 1};
   char str[4]="";

   for (i=0,*SynSite=0,nstop=0; i<2; i++) {
      for (j=0; j<3; j++)   {
         if (transfed) b[i][j] = (i?codon1[j]:codon2[j]);
         else          b[i][j] = (int)CodeChara((char)(i?codon1[j]:codon2[j]),0);
         iy[i] += by[j]*b[i][j];
         if(b[i][j]<0||b[i][j]>3) { 
            if(noisy>=9) 
               printf("\nwarning ambiguity in difcodonNG: %s %s", codon1,codon2);
            *SynSite = 0.5;  *AsynSite = 2.5;
            *SynDif = (codon1[2]!=codon2[2])/2;
            *AsynDif = *SynDif + (codon1[0]!=codon2[0])+(codon1[1]!=codon2[1]);
            return((int)(*SynDif + *AsynDif));
         }
      }
      iaa[i] = GeneticCode[icode][iy[i]];
      if(iaa[i]==-1) {
         printf("\nNG86: stop codon %s.\n",getcodon(str,iy[i]));
         exit(-1);
      }
      for(j=0; j<3; j++) 
         for(k=0; k<4; k++) {
            if (k==b[i][j]) continue;
            i1 = GeneticCode[icode][ iy[i] + (k-b[i][j])*by[j] ];
            if (i1==-1)
               nstop++;
            else if (i1==iaa[i])
               (*SynSite)++;
         }
   }
   *SynSite  *= 3/18.;     /*  2 codons, 2*9 possibilities. */
   *AsynSite =  3*(1-nstop/18.) - *SynSite;

#if 0    /* MEGA 1.1  */
   *AsynSite = 3 - *SynSite;
#endif

   ndiff=0;  *SynDif=*AsynDif=0;
   for(k=0; k<3; k++) dmark[k]=-1;
   for(k=0; k<3; k++) 
      if (b[0][k]-b[1][k]) dmark[ndiff++]=k;
   if (ndiff==0) return(0);
   npath=1;
   nstop=0;
   if(ndiff>1) 
      npath = (ndiff==2 ? 2 : 6);
   if (ndiff==1) { 
      if (iaa[0]==iaa[1]) (*SynDif)++;
      else                (*AsynDif)++;
   }
   else {   /* ndiff=2 or 3 */
      for(k=0; k<npath; k++) {
         for(i1=0; i1<3; i1++) 
            step[i1]=-1;
         if (ndiff==2) {
            step[0]=dmark[k];
            step[1]=dmark[1-k];
         }
         else {
            step[0]=k/2;   step[1]=k%2;
            if (step[0]<=step[1]) step[1]++;
            step[2]=3-step[0]-step[1];
         }
              
         for(i1=0; i1<3; i1++)
            bt1[i1] = bt2[i1] = b[0][i1];
         sdpath=ndpath=0;       /* mutations for each path */
         for(i1=0; i1<ndiff; i1++) {      /* mutation steps for each path */
            bt2[step[i1]] = b[1][step[i1]];
            for (i2=0,ic[0]=ic[1]=0; i2<3; i2++) {
               ic[0]+=bt1[i2]*by[i2];
               ic[1]+=bt2[i2]*by[i2];
            }
            for(i2=0; i2<2; i2++) iaa[i2]=GeneticCode[icode][ic[i2]]; 
            if (iaa[1]==-1) {
               nstop++;  sdpath=ndpath=0; break; 
            }
            if (iaa[0]==iaa[1])  sdpath++; 
            else                 ndpath++;
            for(i2=0; i2<3; i2++)
               bt1[i2] = bt2[i2];
         }
         *SynDif  += (double)sdpath;
         *AsynDif += (double)ndpath;
      }
   }
   if (npath==nstop) {
      puts ("NG86: All paths are through stop codons..");
      if (ndiff==2) { *SynDif=0; *AsynDif=2; }
      else          { *SynDif=1; *AsynDif=2; }
   }
   else {
      *SynDif /= (double)(npath-nstop);  *AsynDif /= (double)(npath-nstop);
   }
   return (ndiff);
}



int difcodonLWL85 (char codon1[], char codon2[], double sites[3], double sdiff[3], 
                    double vdiff[3], int transfed, int icode)
{
/* This partitions codon sites according to degeneracy, that is sites[3] has 
   L0, L2, L4, averaged between the two codons.  It also compares the two codons 
   and add the differences to the transition and transversion differences for use 
   in LWL85 and similar methods.
   The two codons (codon1 & codon2) should not contain ambiguity characters. 
*/
   int b[2][3], by[3] = {16, 4, 1}, i,j, ifold[2], c[2], ct, aa[2], ibase,nsame;
   char str[4]="";

   for(i=0; i<3; i++) sites[i]=sdiff[i]=vdiff[i]=0;
   /* check the two codons and code them */
   for (i=0; i<2; i++) {
      for (j=0,c[i]=0; j<3; j++)   {
         if (transfed) b[i][j] = (i?codon1[j]:codon2[j]);
         else          b[i][j] = (int)CodeChara((char)(i?codon1[j]:codon2[j]),0);
         c[i]+=b[i][j]*by[j];
         if(b[i][j]<0||b[i][j]>3) { 
            if(noisy>=9) 
               printf("\nwarning ambiguity in difcodonLWL85: %s %s", codon1,codon2);
            return(0);
         }
      }
      aa[i]=GeneticCode[icode][c[i]];
      if(aa[i]==-1) {
         printf("\nLWL85: stop codon %s.\n",getcodon(str,c[i]));
         exit(-1);
      }
   }

   for (j=0; j<3; j++) {    /* three codon positions */
      for (i=0; i<2; i++) { /* two codons */
         for(ibase=0,nsame=0; ibase<4; ibase++) {
            ct=c[i]+(ibase-b[i][j])*by[j];
            if(ibase!=b[i][j] && aa[i]==GeneticCode[icode][ct]) nsame++;
         }
         if(nsame==0)                    ifold[i]=0;
         else if (nsame==1 || nsame==2)  ifold[i]=1;
         else                            ifold[i]=2;
         sites[ifold[i]]+=.5;
      }

      if(b[0][j]==b[1][j]) continue;
      if(b[0][j]+b[1][j]==1 || b[0][j]+b[1][j]==5) { /* transition */
         sdiff[ifold[0]]+=.5;  sdiff[ifold[1]]+=.5;
      }
      else {                   /* transversion */
         vdiff[ifold[0]]+=.5;  vdiff[ifold[1]]+=.5;
      }
   }
   return (0);
}



int testTransP (double P[], int n)
{
   int i,j, status=0;
   double sum, small=1e-10;

   for (i=0; i<n; i++) {
      for (j=0,sum=0; j<n; sum+=P[i*n+j++]) 
         if (P[i*n+j]<-small) status=-1;
      if (fabs(sum-1)>small && status==0) {
         printf ("\nrow sum (#%2d) = 1 = %10.6f", i+1, sum);
         status=-1;
      }
   }
   return (status);
}


int PMatUVRoot (double P[], double t, int n, double U[], double V[], double Root[])
{
/* P(t) = U * exp{Root*t} * V
*/
   int i,j,k;
   double expt, uexpt, *pP;
   double smallp = 0;

   NPMatUVRoot++;
   if (t<-0.1) printf ("\nt = %.5f in PMatUVRoot", t);
   if (t<1e-100) { identity (P, n); return(0); }
   for (k=0,zero(P,n*n); k<n; k++)
      for (i=0,pP=P,expt=exp(t*Root[k]); i<n; i++)
         for (j=0,uexpt=U[i*n+k]*expt; j<n; j++)
            *pP++ += uexpt*V[k*n+j];

   for(i=0;i<n*n;i++)  if(P[i]<smallp)  P[i]=0;

#if (DEBUG>=5)
      if (testTransP(P,n)) {
         printf("\nP(%.6f) err in PMatUVRoot.\n", t);
         exit(-1);
      }
#endif

   return (0);
}


int PMatQRev(double Q[], double pi[], double t, int n, double space[])
{
/* This calculates P(t) = exp(Q*t), where Q is the rate matrix for a 
   time-reversible Markov process.

   Q[] or P[] has the rate matrix as input, and P(t) in return.
   space[n*n*2+n*2]
*/
   double *U=space, *V=U+n*n, *Root=V+n*n, *spacesqrtpi=Root+n;

   eigenQREV(Q, pi, n, Root, U, V, spacesqrtpi);
   PMatUVRoot(Q, t, n, U, V, Root);
   return(0);
}


void pijJC69 (double pij[2], double t)
{
   if (t<-0.0001) 
      printf ("\nt = %.5f in pijJC69", t);
   if (t<1e-100) 
      { pij[0]=1; pij[1]=0; }
   else
      { pij[0] = (1.+3*exp(-4*t/3.))/4;  pij[1] = (1-pij[0])/3; }
}



int PMatK80 (double P[], double t, double kappa)
{
/* PMat for JC69 and K80
*/
   int i,j;
   double e1, e2;

   if (t<-0.01)
      printf ("\nt = %.5f in PMatK80", t);
   if (t<1e-100) { identity (P, 4); return(0); }
   e1=exp(-4*t/(kappa+2));
   if (fabs(kappa-1)<1e-5) {
      FOR (i,4) FOR (j,4)
         if (i==j) P[i*4+j]=(1+3*e1)/4;
         else      P[i*4+j]=(1-e1)/4;
   }
   else {
      e2=exp(-2*t*(kappa+1)/(kappa+2));
      FOR (i,4) P[i*4+i]=(1+e1+2*e2)/4;
      P[0*4+1]=P[1*4+0]=P[2*4+3]=P[3*4+2]=(1+e1-2*e2)/4;
      P[0*4+2]=P[0*4+3]=P[2*4+0]=P[3*4+0]=
      P[1*4+2]=P[1*4+3]=P[2*4+1]=P[3*4+1]=(1-e1)/4;
   }
   return (0);
}


int PMatT92 (double P[], double t, double kappa, double pGC)
{
/* PMat for Tamura'92
   t is branch lnegth, number of changes per site.
*/
   double e1, e2;
   t/=(pGC*(1-pGC)*kappa + .5);

   if (t<-0.1) printf ("\nt = %.5f in PMatT92", t);
   if (t<1e-100) { identity (P, 4); return(0); }
   e1=exp(-t); e2=exp(-(kappa+1)*t/2);

   P[0*4+0]=P[2*4+2] = (1-pGC)/2*(1+e1)+pGC*e2;
   P[1*4+1]=P[3*4+3] = pGC/2*(1+e1)+(1-pGC)*e2;
   P[1*4+0]=P[3*4+2] = (1-pGC)/2*(1+e1)-(1-pGC)*e2;
   P[0*4+1]=P[2*4+3] = pGC/2*(1+e1)-pGC*e2;

   P[0*4+2]=P[2*4+0]=P[3*4+0]=P[1*4+2] = (1-pGC)/2*(1-e1);
   P[1*4+3]=P[3*4+1]=P[0*4+3]=P[2*4+1] = pGC/2*(1-e1);
   return (0);
}


int PMatTN93 (double P[], double a1t, double a2t, double bt, double pi[])
{
   double T=pi[0],C=pi[1],A=pi[2],G=pi[3], Y=T+C, R=A+G;
   double e1, e2, e3, small=-1e-3;

   if(noisy && (a1t<small || a2t<small || bt<small))
      printf ("\nat=%12.6f %12.6f  bt=%12.6f", a1t,a2t,bt);

   if(a1t+a2t+bt < 1e-300)
      { identity(P,4);  return(0); }

   e1 = exp(-bt); 
   e2 = exp(-(R*a2t + Y*bt));
   e3 = exp(-(Y*a1t + R*bt));

   P[0*4+0] = T + R*T/Y*e1 + C/Y*e3;
   P[0*4+1] = C + R*C/Y*e1 - C/Y*e3;
   P[0*4+2] = A*(1-e1);
   P[0*4+3] = G*(1-e1);

   P[1*4+0] = T + R*T/Y*e1 - T/Y*e3;
   P[1*4+1] = C + R*C/Y*e1 + T/Y*e3;
   P[1*4+2] = A*(1-e1);
   P[1*4+3] = G*(1-e1);

   P[2*4+0] = T*(1-e1);
   P[2*4+1] = C*(1-e1);
   P[2*4+2] = A + Y*A/R*e1 + G/R*e2;
   P[2*4+3] = G + Y*G/R*e1 - G/R*e2;

   P[3*4+0] = T*(1-e1);
   P[3*4+1] = C*(1-e1);
   P[3*4+2] = A + Y*A/R*e1 - A/R*e2;
   P[3*4+3] = G + Y*G/R*e1 + A/R*e2;

   return(0);
}



int EvolveHKY85 (char source[], char target[], int ls, double t,
    double rates[], double pi[4], double kappa, int isHKY85)
{
/* isHKY85=1 if HKY85,  =0 if F84
   Use NULL for rates if rates are identical among sites.
*/
   int i,j,h,n=4;
   double TransP[16],a1t,a2t,bt,r, Y = pi[0]+pi[1], R = pi[2]+pi[3];

   if (isHKY85)  a1t=a2t=kappa;
   else        { a1t=1+kappa/Y; a2t=1+kappa/R; }
   bt=t/(2*(pi[0]*pi[1]*a1t+pi[2]*pi[3]*a2t)+2*Y*R);
   a1t*=bt;   a2t*=bt;
   FOR (h, ls) {
      if (h==0 || (rates && rates[h]!=rates[h-1])) {
         r=(rates?rates[h]:1);
         PMatTN93 (TransP, a1t*r, a2t*r, bt*r, pi);
         for (i=0;i<n;i++) {
            for (j=1;j<n;j++) TransP[i*n+j]+=TransP[i*n+j-1];
            if (fabs(TransP[i*n+n-1]-1)>1e-5) error2("TransP err");
         }
      }
      for (j=0,i=source[h],r=rndu();j<n-1;j++)  if (r<TransP[i*n+j]) break;
      target[h] = (char)j;
   }
   return (0);
}

int Rates4Sites (double rates[],double alpha,int ncatG,int ls, int cdf,
    double space[])
{
/* Rates for sites from the gamma (ncatG=0) or discrete-gamma (ncatG>1).
   Rates are converted into the c.d.f. if cdf=1, which is useful for
   simulation under JC69-like models. 
   space[ncatG*5]
*/
   int h, ir, j, K=ncatG, *Lalias=(int*)(space+3*K), *counts=(int*)(space+4*K);
   double *rK=space, *freqK=space+K, *Falias=space+2*K;

   if (alpha==0) 
      { if(rates) FOR(h,ls) rates[h]=1; }
   else {
      if (K>1) {
         DiscreteGamma (freqK, rK, alpha, alpha, K, DGammaMean);

         MultiNomialAliasSetTable(K, freqK, Falias, Lalias, space+5*K);
         MultiNomialAlias(ls, K, Falias, Lalias, counts);

         for (ir=0,h=0; ir<K; ir++) 
            for (j=0; j<counts[ir]; j++)  rates[h++]=rK[ir];
      }
      else 
         for (h=0; h<ls; h++) rates[h] = rndgamma(alpha)/alpha;
      if (cdf) {
         for (h=1; h<ls; h++) rates[h] += rates[h-1];
         abyx (1/rates[ls-1], rates, ls);
      }
   }
   return (0);
}


char *getcodon (char codon[], int icodon)
{
/* id : (0,63) */
   if (icodon<0 || icodon>63) {
      printf("\ncodon %d\n", icodon);
      error2("getcodon.");
   }
   codon[0] = BASEs[icodon/16]; 
   codon[1] = BASEs[(icodon%16)/4];
   codon[2] = BASEs[icodon%4];
   codon[3] = 0;
   return (codon);
}


char *getAAstr(char *AAstr, int iaa)
{
/* iaa (0,20) with 20 meaning termination */
   if (iaa<0 || iaa>20) error2("getAAstr: iaa err. \n");
   strncpy (AAstr, AA3Str+iaa*3, 3);
   return (AAstr);
}

int NucListall(char b, int *nb, int ib[4])
{
/* Resolve an ambiguity nucleotide b into all possibilities.  
   nb is number of bases and ib (0,1,2,3) list all of them.
   Data are complete if (nb==1).
*/
   int j, k;

   k = strchr(BASEs,(int)b) - BASEs;
   if(k<0)
      { printf("NucListall: strange character %c\n",b); return(-1);}
   if(k<4) {
      *nb = 1; ib[0] = k;
   }
   else {
      *nb = strlen(EquateBASE[k]);
      for(j=0; j< *nb; j++)
         ib[j] = strchr(BASEs,EquateBASE[k][j]) - BASEs;
   }
   return(0);
}

int Codon2AA(char codon[3], char aa[3], int icode, int *iaa)
{
/* translate a triplet codon[] into amino acid (aa[] and iaa), using
   genetic code icode.  This deals with ambiguity nucleotides.
   *iaa=(0,...,19),  20 for stop or missing data.
   Distinquish between stop codon and missing data? 
   naa=0: only stop codons; 1: one AA; 2: more than 1 AA.

   Returns 0: if one amino acid
           1: if multiple amino acids (ambiguity data)
           -1: if stop codon
*/
   int nb[3],ib[3][4], ic, i, i0,i1,i2, iaa0=-1,naa=0;

   for(i=0; i<3; i++) 
      NucListall(codon[i], &nb[i], ib[i]);
   for(i0=0; i0<nb[0]; i0++)  
      for(i1=0; i1<nb[1]; i1++)
         for(i2=0; i2<nb[2]; i2++) {
            ic = ib[0][i0]*16 + ib[1][i1]*4 + ib[2][i2];         
            *iaa = GeneticCode[icode][ic];
            if(*iaa==-1) continue;
            if(naa==0)  { iaa0=*iaa; naa++; }
            else if (*iaa!=iaa0)  naa=2;
         }

   if(naa==0) {
      printf("stop codon %c%c%c\n",codon[0],codon[1],codon[2]);
      *iaa = 20;
   }
   else if(naa==2)  *iaa = 20; 
   else             *iaa = iaa0;
   strncpy(aa, AA3Str+*iaa*3, 3);

   return(naa==1 ? 0 : (naa==0 ? -1 : 1));
}

int DNA2protein(char dna[], char protein[], int lc, int icode)
{
/* translate a DNA into a protein, using genetic code icode, with lc codons.
   dna[] and protein[] can be the same string.
*/
   int h, iaa, k;
   char aa3[4];

   for(h=0; h<lc; h++) {
      k = Codon2AA(dna+h*3,aa3,icode,&iaa);
      if(k == -1) printf(" stop codon at %d out of %d\n",h+1,lc);
      protein[h] = AAs[iaa];
   }
   return(0);
}


int printcu (FILE *fout, double fcodon[], int icode)
{
/* output codon usage table and other related statistics
   space[20+1+3*5]
   Outputs the genetic code table if fcodon==NULL
*/
   int wc=8, wd=0;  /* wc: for codon, wd: decimal  */
   int it, i,j,k, iaa;
   double faa[21], fb3x4[3*5]; /* chi34, Ic, lc, */
   char *word="|-", aa3[4]="   ",codon[4]="   ", ss3[4][4], *noodle;
   static double aawt[]={89.1, 174.2, 132.1, 133.1, 121.2, 146.2,
         147.1,  75.1, 155.2, 131.2, 131.2, 146.2, 149.2, 165.2, 115.1,
         105.1, 119.1, 204.2, 181.2, 117.1};

   if (fcodon) { zero(faa,21);  zero(fb3x4,12); }
   else     wc=0;
   for(i=0; i<4; i++) strcpy(ss3[i],"\0\0\0");
   noodle = strc(4*(10+2+wc)-2,word[1]);
   fprintf(fout, "\n%s\n", noodle);
   for(i=0; i<4; i++,FPN(fout)) {
      for(j=0; j<4; j++)  {
         for(k=0; k<4; k++)  {
            it = i*16+k*4+j;   
            iaa = GeneticCode[icode][it];
            if(iaa==-1) iaa = 20;
            getcodon(codon, it);  getAAstr(aa3,iaa);
            if (!strcmp(ss3[k],aa3) && j>0)
               fprintf(fout, "     ");
            else  { 
               fprintf(fout, "%s %c", aa3,(iaa<20?AAs[iaa]:'*'));
               strcpy(ss3[k], aa3);
            }
            fprintf(fout, " %s", codon);
            if (fcodon) fprintf(fout, "%*.*f", wc,wd, fcodon[it] );
            if (k<3) fprintf(fout, " %c ", word[0]);
         }
         FPN (fout);
      }
      fputs (noodle, fout);
   }
   return(0);
}

int printcums (FILE *fout, int ns, double fcodons[], int icode)
{
   int neach0=6, neach=neach0, wc=3,wd=0;  /* wc: for codon, wd: decimal  */
   int iaa,it, i,j,k, i1, ngroup, igroup;
   char *word="|-", aa3[4]="   ",codon[4]="   ", ss3[4][4], *noodle;

   ngroup=(ns-1)/neach+1;
   for(igroup=0; igroup<ngroup; igroup++,FPN(fout)) {
      if (igroup==ngroup-1) 
         neach = ns - neach0*igroup;
      noodle = strc(4*(10+wc*neach)-2, word[1]);
      strcat(noodle, "\n");
      fputs(noodle, fout);
      for(i=0; i<4; i++) strcpy (ss3[i],"   ");
      for(i=0; i<4; i++) {
         for(j=0; j<4; j++) {
            for(k=0; k<4; k++) {
               it = i*16+k*4+j;   
               iaa = GeneticCode[icode][it]; 
               if(iaa==-1) iaa = 20;
               getcodon(codon, it);
               getAAstr(aa3,iaa);
               if ( !strcmp(ss3[k], aa3) && j>0)   fprintf(fout, "   ");
               else  { fprintf(fout, "%s", aa3); strcpy(ss3[k], aa3);  }

               fprintf(fout, " %s", codon);
               for(i1=0; i1<neach; i1++) 
                  fprintf(fout, " %*.*f", wc-1, wd, fcodons[(igroup*neach0+i1)*64+it] );
               if (k<3) fprintf(fout, " %c ", word[0]);
            }
            FPN (fout);
         }
         fputs (noodle, fout);
      }
   }
   return(0);
}

int QtoPi (double Q[], double pi[], int n, double space[])
{
/* from rate matrix Q[] to pi, the stationary frequencies:
   Q' * pi = 0     pi * 1 = 1
   space[] is of size n*(n+1).
*/
   int i,j;
   double *T = space;      /* T[n*(n+1)]  */

   for(i=0;i<n+1;i++) T[i]=1;
   for(i=1;i<n;i++) {
      for(j=0;j<n;j++)
         T[i*(n+1)+j] =  Q[j*n+i];     /* transpose */
      T[i*(n+1)+n] = 0.;
   }
   matinv(T, n, n+1, pi);
   for(i=0;i<n;i++) 
      pi[i] = T[i*(n+1)+n];
   return (0);
}

int PtoPi (double P[], double pi[], int n, double space[])
{
/* from transition probability P[ij] to pi, the stationary frequencies
   (P'-I) * pi = 0     pi * 1 = 1
   space[] is of size n*(n+1).
*/
   int i,j;
   double *T = space;      /* T[n*(n+1)]  */

   for(i=0;i<n+1;i++) T[i]=1;
   for(i=1;i<n;i++) {
      for(j=0;j<n;j++)
         T[i*(n+1)+j] = P[j*n+i]-(double)(i==j);     /* transpose */
      T[i*(n+1)+n] = 0;
   }
   matinv(T, n, n+1, pi);
   for(i=0;i<n;i++) pi[i] = T[i*(n+1)+n];
   return (0);
}

int PtoX (double P1[], double P2[], double pi[], double X[])
{
/*  from P1 & P2 to X.     X = P1' diag{pi} P2
*/
   int i, j, k;

   FOR (i,4)
      FOR (j,4)
         for (k=0,X[i*4+j]=0.0; k<4; k++)  {
            X[i*4+j] += pi[k] * P1[k*4+i] * P2[k*4+j];
         }
   return (0);
}


int ScanFastaFile (FILE *f, int *ns, int *ls, int *aligned)
{
/* This scans a fasta alignment file to get com.ns & com.ls.
   Returns -1 if the sequences are not aligned and have different lengths.
*/
   int len=0, ch, starter='>';
   char name[200];

   for (*aligned=1,*ns=-1,*ls=0; ; ) {
      ch = fgetc(f);
      if(ch == starter || ch == EOF) {
         if(*ns >= 0) {  /* process end of the sequence */
            if(*ns>1 && len!= *ls)  *aligned = 0;
            if(len> *ls)            *ls = len;
         }
         (*ns)++;      /* next sequence */
         if(ch == EOF) break;
         fscanf(f, "%s", name);
         len = 0;
      }
      else if(isgraph(ch)) {
         if(*ns == -1)
            error2("seq file error: use '>' in fasta format.");
         len++;
      }
   }
   rewind(f);
   return(0);
}


int printaSeq (FILE *fout, char z[], int ls, int lline, int gap)
{
   int i;
   FOR (i, ls) {
      fprintf (fout, "%c", z[i]);
      if (gap && (i+1)%gap==0)  fprintf (fout, " ");
      if ((i+1)%lline==0) { fprintf (fout, "%7d", i+1); FPN (fout); }
   }
   i=ls%lline;
   if (i) fprintf (fout, "%*d\n", 7+lline+lline/gap-i-i/gap, ls);
   FPN (fout);
   return (0);
}

int printsma (FILE*fout, char*spname[], char*z[], int ns, int l, int lline, int gap, int seqtype, 
    int transformed, int simple, int pose[])
{
/* print multiple aligned sequences.
   use spname==NULL if no seq names available.
   pose[h] marks the position of the h_th site in z[], useful for 
   printing out the original sequences after site patterns are collapsed. 
   Sequences z[] are coded if(transformed) and not if otherwise.
*/
   int igroup, ngroup, lt, h,hp, i, b,b0=-1,igap, lspname=41, lseqlen=7;
   char indel='-', ambi='?', equal='.';
   char *pch=(seqtype<=1 ? BASEs : (seqtype==2?AAs:BINs));
   char codon[4]="   ";

   if(l==0) return(1);
   codon[0]=-1;  /* to avoid warning */
   if (gap==0) gap=lline+1;
   ngroup=(l-1)/lline+1;
   for (igroup=0,FPN(fout); igroup<ngroup; igroup++,FPN(fout))  {
      lt=min2(l,(igroup+1)*lline);  /* seqlen mark at the end of block */
      igap=lline+(lline/gap)+lspname+1-lseqlen-1; /* spaces */
      if(igroup+1==ngroup)
         igap=(l-igroup*lline)+(l-igroup*lline)/gap+lspname+1-lseqlen-1;
      /* fprintf (fout,"%*s[%*d]\n", igap, "", lseqlen,lt); */
      for(i=0; i<ns; i++)  {
         if(spname) fprintf(fout,"%-*s  ", lspname,spname[i]);
         for (h=igroup*lline,lt=0,igap=0; lt<lline && h<l; h++,lt++) {
            hp = (pose ? pose[h] : h);
            if(seqtype==CODONseq && transformed) {
               fprintf(fout," %s", CODONs[z[i][hp]]);
               continue;
            }
            b0 = (int)z[0][hp];
            b  = (int)z[i][hp];  
            if(transformed) {
               b0 = pch[b0];
               b = pch[b];
            }
            if(i&&simple && b==b0 && b!=indel && b!=ambi)  b=equal;
            fputc(b, fout);
            if (++igap==gap)  { fputc(' ', fout); igap=0; }
         }
         FPN (fout);
      }
   }
   FPN(fout);
   return(0);
}



/* ***************************
        Simple tools
******************************/

static time_t time_start;

void starttimer (void)
{
   time_start=time(NULL);
}

char* printtime (char timestr[])
{
/* print time elapsed since last call to starttimer()
*/
   time_t t;
   int h, m, s;

   t=time(NULL)-time_start;
   h=t/3600; m=(t%3600)/60; s=t-(t/60)*60;
   if(h)  sprintf(timestr,"%d:%02d:%02d", h,m,s);
   else   sprintf(timestr,"%2d:%02d", m,s);
   return(timestr);
}

void sleep2(int wait)
{
/* Pauses for a specified number of seconds. */
   time_t t_cur=time(NULL);

   while(time(NULL)<t_cur+wait) ;
}



char *strc (int n, int c)
{
   static char s[256];
   int i;

   if (n>255) error2("line >255 in strc");
   FOR (i,n) s[i]=(char)c;    s[n]=0;
   return (s);
}

int putdouble(FILE*fout, double a)
{
   double aa=fabs(a);
   return  fprintf(fout, (aa<1e-5||aa>1e6 ? "  %11.4e" : " %11.6f"), a);
}

void strcase (char *str, int direction)
{
/* direction = 0: to lower; 1: to upper */
   char *p=str;
   if(direction)  while(*p) { *p=(char)toupper(*p); p++; }
   else           while(*p) { *p=(char)tolower(*p); p++; }
}


FILE *gfopen(char *filename, char *mode)
{
   FILE *fp;

   if(filename==NULL || filename[0]==0) 
      error2("file name empty.");

   fp=(FILE*)fopen(filename, mode);
   if(fp==NULL) {
      printf("\nerror when opening file %s\n", filename);
      if(!strchr(mode,'r')) exit(-1);
      printf("tell me the full path-name of the file? ");
      scanf("%s", filename);
      if((fp=(FILE*)fopen(filename, mode))!=NULL)  return(fp);
      puts("Can't find the file.  I give up.");
      exit(-1);
   }
   return(fp);
}


int appendfile(FILE*fout, char*filename)
{
   FILE *fin=fopen(filename,"r");
   int ch;

   if(fin) {
      while((ch=fgetc(fin))!=EOF) 
         fputc(ch,fout);
      fclose(fin);
      fflush(fout);
   }
   return(0);
}


void error2 (char * message)
{ printf("\nError: %s.\n", message); exit(-1); }

int zero (double x[], int n)
{ int i; for(i=0; i<n; i++) x[i]=0; return (0);}

double sum (double x[], int n)
{ int i; double t=0;  for(i=0; i<n; i++) t += x[i];    return(t); }

int fillxc (double x[], double c, int n)
{ int i; for(i=0; i<n; i++) x[i]=c; return (0); }

int xtoy (double x[], double y[], int n)
{ int i; for (i=0; i<n; y[i]=x[i],i++) ;  return(0); }

int abyx (double a, double x[], int n)
{ int i; for (i=0; i<n; x[i]*=a,i++) ;  return(0); }

int axtoy(double a, double x[], double y[], int n)
{ int i; for (i=0; i<n; y[i] = a*x[i],i++) ;  return(0);}

int axbytoz(double a, double x[], double b, double y[], double z[], int n)
{ int i; for(i=0; i<n; i++)   z[i] = a*x[i]+b*y[i];  return (0); }

int identity (double x[], int n)
{ int i,j;  for(i=0; i<n; i++)  { for(j=0; j<n; j++)   x[i*n+j]=0;  x[i*n+i]=1; }  return (0); }

double distance (double x[], double y[], int n)
{  int i; double t=0;
   for (i=0; i<n; i++) t += square(x[i]-y[i]);
   return(sqrt(t));
}

double innerp (double x[], double y[], int n)
{ int i; double t=0;  for(i=0; i<n; i++)  t += x[i]*y[i];  return(t); }

double norm (double x[], int n)
{ int i; double t=0;  for(i=0; i<n; i++)  t += x[i]*x[i];  return sqrt(t); }


int Add2Ptree (int counts[3], double Ptree[3])
{
/* Suppose counts[3] have the numbers of sites supporting the three trees.  This 
   routine adds a total of probability 1 to Ptree[3], by breaking ties.
*/
   int i, ibest[3]={0,0,0}, nbest=1, *x=counts;

   for(i=1; i<3; i++) {
      if(x[i] > x[ibest[0]])
         { nbest=1; ibest[0]=i; }
      else if(x[i] == x[ibest[0]]) 
         ibest[nbest++]=i;
   }
   for(i=0; i<nbest; i++) 
      Ptree[ibest[i]] += 1./nbest;
   return(0);
}

int indexing (double x[], int n, int index[], int descending, int space[])
{
/* bubble sort to calculate the indecies for the vector x[].  
   x[index[2]] will be the third largest or smallest number in x[].
   This does not change x[].     
*/
   int i,j, it=0, *mark=space;
   double t=0;

   for(i=0; i<n; i++) mark[i]=1;
   for(i=0; i<n; i++) {
      for(j=0; j<n; j++)
         if(mark[j]) { t=x[j]; it=j++; break; } /* first unused number */
      if (descending) {
         for ( ; j<n; j++)
            if (mark[j] && x[j]>t) { t=x[j]; it=j; }
      }
      else {
         for ( ; j<n; j++)
            if (mark[j] && x[j]<t) { t=x[j]; it=j; }
      }
      mark[it]=0;   index[i]=it;
   }
   return (0);
}


int f_and_x(double x[], double f[], int n, int fromf, int LastItem)
{
/* This transforms between x and f.  x and f can be identical.
   If (fromf), f->x
   else        x->f.
   The iterative variable x[] and frequency f[0,1,n-2] are related as:
      freq[k] = exp(x[k])/(1+SUM(exp(x[k]))), k=0,1,...,n-2, 
   x[] and freq[] may be the same vector.
   The last element (f[n-1] or x[n-1]=1) is updated only if(LastItem).
*/
   int i;
   double tot;

   if (fromf) {  /* f => x */
      if((tot=1-sum(f,n-1))<1e-80) error2("f[n-1]==1, not dealt with.");
      tot=1/tot;
      FOR(i,n-1)  x[i]=log(f[i]*tot);
      if(LastItem) x[n-1]=0;
   }
   else {        /* x => f */
      for(i=0,tot=1; i<n-1; i++)  tot+=(f[i]=exp(x[i]));
      FOR(i,n-1)  f[i]/=tot;
      if(LastItem) f[n-1]=1/tot;
   }
   return(0);
}

static unsigned int z_rndu=1237;
static int          w_rndu=1237;

void SetSeed (unsigned int seed)
{
   if(sizeof(int) != 4) 
      error2("oh-oh, we are in trouble.  int not 32-bit?");
   z_rndu = seed;
   w_rndu = abs(seed);
}


#ifdef FAST_RANDOM_NUMBER

double rndu (void)
{
/* 32-bit integer assumed.
   From Ripley (1987) p. 46 or table 2.4 line 2. 
   This may return 0 or 1, which can be a problem.
*/
   z_rndu = z_rndu*69069 + 1;
   if(z_rndu==0 || z_rndu==4294967295)  z_rndu = 13;
   return z_rndu/4294967295.0;
}

double rndu2 (void)
{
/* 32-bit integer assumed.
   From Ripley (1987) table 2.4 line 4. 
*/
   w_rndu = abs(w_rndu*16807)%2147483647;
   if(w_rndu==0)  w_rndu = 13;
   return w_rndu/2147483647.0;
}

#else 

double rndu (void)
{
/* U(0,1): AS 183: Appl. Stat. 31:188-190 
   Wichmann BA & Hill ID.  1982.  An efficient and portable
   pseudo-random number generator.  Appl. Stat. 31:188-190

   x, y, z are any numbers in the range 1-30000.  Integer operation up
   to 30323 required.
*/
   static unsigned int x_rndu=11, y_rndu=23;
   double r;

   x_rndu = 171*(x_rndu%177) -  2*(x_rndu/177);
   y_rndu = 172*(y_rndu%176) - 35*(y_rndu/176);
   z_rndu = 170*(z_rndu%178) - 63*(z_rndu/178);
/*
   if (x_rndu<0) x_rndu += 30269;
   if (y_rndu<0) y_rndu += 30307;
   if (z_rndu<0) z_rndu += 30323;
*/
  r = x_rndu/30269.0 + y_rndu/30307.0 + z_rndu/30323.0;
  return (r-(int)r);
}

#endif


double reflect(double x, double a, double b)
{
/* This returns a variable in the range (a,b) by reflecting x back into the range
*/
   int rounds=0;
   double x0=x, nroundsVirtual, small=1e-50;

   if(b-a<small) {
      printf("\nimproper range x0=%.6g (%.6g, %.6g)\n", x0,a,b);
      exit(-1);
   }
   nroundsVirtual = floor((x-a)/(2*(b-a)));
   x -= nroundsVirtual *2*(b-a);
   for ( ; ; rounds++) {
      if(x<=a)       x = a*2 - x;
      else if(x>=b)  x = b*2 - x;
      else break;
   }
   return(x);
}



void randorder(int order[], int n, int space[])
{
/* This orders 0,1,2,...,n-1 at random
   space[n]
*/
   int i,k, *item=space;

   for(i=0; i<n; i++) item[i]=i;
   for(i=0; i<n; i++) {
      k=(int)((n-i)*rndu());
      order[i]=item[i+k];  item[i+k]=item[i];
   }
}


double rndNormal (void)
{
/* Standard normal variate, using the Box-Muller method (1958), improved by 
   Marsaglia and Bray (1964).  The method generates a pair of random
   variates, and only one used.
   See N. L. Johnson et al. (1994), Continuous univariate distributions, 
   vol 1. p.153.
*/
   double u, v, s;

   for (; ;) {
      u = 2*rndu() - 1;
      v = 2*rndu() - 1;
      s = u*u + v*v;
      if (s>0 && s<1) break;
   }
   s = sqrt(-2*log(s)/s);
   return (u*s);
}


double rnd2NormalSym (double m)
{
/* This returns a variate from the 1:1 mixture of two normals
   N(-m, 1-m^2) and N(m, 1-m^2), which has mean 0 and variance 1.

   The value m = 0.94 is useful for generating MCMC proposals
*/
   double z = m + rndNormal()*sqrt(1-m*m);
   if(rndu()<0.5) z = -z;
   return (z);
}


double rndCauchy (void)
{
/* Standard Cauchy variate, generated using inverse CDF
*/
   return tan(Pi*(rndu()-0.5));
}

double rndt4 (void)
{
/* Standard Student's t_4 variate, with d.f. = 4.
*/
   double u, v, w, c2, r2, t4;

   for( ; ; ) {
      u = 2 * rndu() - 1;
      v = 2 * rndu() - 1;
      w = u*u + v*v;
      if(w<1) break;
   }
   c2 = u*u/w;
   r2 = 4/sqrt(w) - 4;
   t4 = sqrt(r2*c2);
   if(rndu()<0.5) t4 = -t4;

   return t4;
}


int rndpoisson (double m)
{
/* m is the rate parameter of the poisson
   Numerical Recipes in C, 2nd ed. pp. 293-295
*/
   static double sq, alm, g, oldm=-1;
   double em, t, y;

/* search from the origin
   if (m<5) { 
      if (m!=oldm) { oldm=m; g=exp(-m); }
      y=rndu();  sq=alm=g;
      for (em=0; ; ) {
         if (y<sq) break;
         sq+= (alm*=m/ ++em);
      }
   }
*/
   if (m<12) { 
      if (m!=oldm) { oldm=m; g=exp(-m); }
      em=-1; t=1;
      for (; ;) {
         em++; t*=rndu();
         if (t<=g) break;
      }
   }
   else {
     if (m!=oldm) {
        oldm=m;  sq=sqrt(2*m);  alm=log(m);
        g=m*alm-LnGamma(m+1);
     }
     do {
        do {
           y=tan(3.141592654*rndu());
           em=sq*y+m;
        } while (em<0);
        em=floor(em);
        t=0.9*(1+y*y)*exp(em*alm-LnGamma(em+1)-g);
     } while (rndu()>t);
   }
   return ((int) em);
}


double rndgamma (double a)
{
/* This returns a random variable from gamma(a, 1).
   Marsaglia and Tsang (2000) A Simple Method for generating gamma variables", 
   ACM Transactions on Mathematical Software, 26 (3): 363-372.
   This is not entirely safe and is noted to produce zero when a is small (0.001).
 */
   double a0=a, c, d, u, v, x;

   if(a<1) a ++;

   d = a - 1.0/3.0;
   c = (1.0/3.0) / sqrt(d);

   for ( ; ; ) {
      do {
         x = rndNormal();
         v = 1.0 + c * x;
      }
      while (v <= 0);
 
      v *= v * v;
      u = rndu();

      if (u < 1 - 0.0331 * x * x * x * x) 
         break;
      if (log(u) < 0.5 * x * x + d * (1 - v + log(v)))
         break;
   }
   v *= d;

   if(a0 < 1) 
      v *= pow(rndu(), 1/a0);
   if(v==0) 
      printf("\nrndgamma returning 0.\n");
   return v;
}


double rndbeta (double p, double q)
{
/* this generates a random beta(p,q) variate
*/
   double gamma1, gamma2;
   gamma1 = rndgamma(p);
   gamma2 = rndgamma(q);
   return gamma1/(gamma1+gamma2);
}


int rndNegBinomial (double shape, double mean)
{
/* mean=mean, var=mean^2/shape+m 
*/
   return (rndpoisson(rndgamma(shape)/shape*mean));
}


int MultiNomialAliasSetTable (int ncat, double prob[], double F[], int L[], double space[])
{
/* This sets up the tables F and L for the alias algorithm for generating samples from the 
   multinomial distribution MN(ncat, p) (Walker 1974; Kronmal & Peterson 1979).  
   
   F[i] has cutoff probabilities, L[i] has aliases.
   I[i] is an indicator: -1 for F[i]<1; +1 for F[i]>=1; 0 if the cell is now empty.

   Should perhaps check whether prob[] sums to 1.
*/
   signed char *I = (signed char *)space;
   int i,j,k, nsmall;

   for(i=0; i<ncat; i++)  L[i]=-9;
   for(i=0; i<ncat; i++)  F[i]=ncat*prob[i];
   for(i=0,nsmall=0; i<ncat; i++) {
      if(F[i]>=1)  I[i]=1;
      else       { I[i]=-1; nsmall++; }
   }
   for(i=0; nsmall>0; i++) {
      for(j=0; j<ncat; j++)  if(I[j]==-1) break;
      for(k=0; k<ncat; k++)  if(I[k]==1)  break;
      if(k==ncat)  break;

      L[j] = k;
      F[k] -= 1-F[j];
      if(F[k]<1) { I[k]=-1; nsmall++; }
      I[j]=0;  nsmall--;
   }
   return(0);
}


int MultiNomialAlias (int n, int ncat, double F[], int L[], int nobs[])
{
/* This generates multinomial samples using the F and L tables set up before, 
   using the alias algorithm (Walker 1974; Kronmal & Peterson 1979).
   
   F[i] has cutoff probabilities, L[i] has aliases.
   I[i] is an indicator: -1 for F[i]<1; +1 for F[i]>=1; 0 if the cell is now empty.
*/
   int i,k;
   double r;

   for(i=0; i<ncat; i++)  nobs[i]=0;
   for(i=0; i<n; i++)  {
      r = rndu()*ncat;
      k = (int)r;
      r -= k;
      if(r<=F[k]) nobs[k]++;
      else        nobs[L[k]]++;
   }
   return (0);
}     


int MultiNomial2 (int n, int ncat, double prob[], int nobs[], double space[])
{
/* sample n times from a mutinomial distribution M(ncat, prob[])
   prob[] is considered cumulative prob if (space==NULL)
   ncrude is the number or crude categories, and lcrude marks the
   starting category for each crude category.  These are used 
   to speed up the process when ncat is large.
*/
   int i, j, crude=(ncat>20), ncrude, lcrude[200];
   double r, *pcdf=(space==NULL?prob:space), small=1e-5;

   ncrude=max2(5,ncat/20); ncrude=min2(200,ncrude);
   for(i=0; i<ncat; i++) nobs[i]=0;
   if (space) {
      xtoy(prob, pcdf, ncat);
      for(i=1; i<ncat; i++) pcdf[i]+=pcdf[i-1];
   }
   if (fabs(pcdf[ncat-1]-1) > small) 
      error2("sum P!=1 in MultiNomial2");
   if (crude) {
      for(j=1,lcrude[0]=i=0; j<ncrude; j++)  {
         while (pcdf[i]<(double)j/ncrude) i++;
         lcrude[j]=i-1;
      }
   }
   for(i=0; i<n; i++) {
      r=rndu();
      j=0;
      if (crude) {
         for (; j<ncrude; j++) if (r<(j+1.)/ncrude) break;
         j=lcrude[j];
      }
      for (; j<ncat-1; j++) if (r<pcdf[j]) break;
      nobs[j] ++;
   }
   return (0);
}     


/* functions concerning the CDF and percentage points of the gamma and
   Chi2 distribution
*/
double QuantileNormal (double prob)
{
/* returns z so that Prob{x<z}=prob where x ~ N(0,1) and (1e-12)<prob<1-(1e-12)
   returns (-9999) if in error
   Odeh RE & Evans JO (1974) The percentage points of the normal distribution.
   Applied Statistics 22: 96-97 (AS70)

   Newer methods:
     Wichura MJ (1988) Algorithm AS 241: the percentage points of the
       normal distribution.  37: 477-484.
     Beasley JD & Springer SG  (1977).  Algorithm AS 111: the percentage 
       points of the normal distribution.  26: 118-121.
*/
   double a0=-.322232431088, a1=-1, a2=-.342242088547, a3=-.0204231210245;
   double a4=-.453642210148e-4, b0=.0993484626060, b1=.588581570495;
   double b2=.531103462366, b3=.103537752850, b4=.0038560700634;
   double y, z=0, p=prob, p1;

   p1 = (p<0.5 ? p : 1-p);
   if (p1<1e-20) z=999;
   else {
      y = sqrt (log(1/(p1*p1)));   
      z = y + ((((y*a4+a3)*y+a2)*y+a1)*y+a0) / ((((y*b4+b3)*y+b2)*y+b1)*y+b0);
   }
   return (p<0.5 ? -z : z);
}

double PDFNormal (double x, double mu, double sigma2)
{
   return 1/sqrt(2*Pi*sigma2)*exp(-.5/sigma2*(x-mu)*(x-mu));
}

double CDFNormal (double x)
{
/* Hill ID  (1973)  The normal integral.  Applied Statistics, 22:424-427.
   Algorithm AS 66.   (error < ?)
   adapted by Z. Yang, March 1994.  Hill's routine does not look good, and I
   haven't consulted the following reference.
      Adams AG  (1969)  Algorithm 39.  Areas under the normal curve.
      Computer J. 12: 197-198.
*/
    int invers=0;
    double p, t=1.28, y=x*x/2;

    if (x<0) {  invers=1;  x=-x; }
    if (x<t)  
       p = .5 - x * (    .398942280444 - .399903438504 * y
                   /(y + 5.75885480458 - 29.8213557808
                   /(y + 2.62433121679 + 48.6959930692
                   /(y + 5.92885724438))));
    else {
       p = 0.398942280385 * exp(-y) /
           (x - 3.8052e-8 + 1.00000615302 /
           (x + 3.98064794e-4 + 1.98615381364 /
           (x - 0.151679116635 + 5.29330324926 /
           (x + 4.8385912808 - 15.1508972451 /
           (x + 0.742380924027 + 30.789933034 /
           (x + 3.99019417011))))));
    }
    return (invers ? p : 1-p);
}


double logCDFNormal (double x)
{
/* logarithm of CDF of N(0,1). 

   The accuracy is good for the full range (-inf, 38) on my 32-bit machine.  
   When x=38, log(F(x)) = -2.88542835e-316.  When x > 38, log(F(x)) can't be 
   distinguished from 0.  F(5) = 1 - 1.89E-8, and when x>5, F(x) is hard to 
   distinguish from 1.  Instead the smaller tail area F(-5) is used for the 
   calculation, using the expansion log(1-z) = -z(1 + z/2 + z*z/3), where 
   z = F(-5) is small.
   For 3 < x < 7, both approaches are close, but when x = 8, Mathematica and 
   log(CDFNormal) give the incorrect answer -6.66133815E-16, while the correct 
   value is log(F(8)) = log(1 - F(-8)) ~= -F(-8) = -6.22096057E-16.

   F(x) when x<-10 is reliably calculatd using the series expansion, even though 
   log(CDFNormal) works until F(-38) = 2.88542835E-316.

   
   Regarding calculation of the logarithm of Pr(a < X < b), note that 
   F(-9) - F(-10) = F(10) - F(9), but the left side is better computationally.
*/
   double lnF, z=fabs(x), C, low=-10, high=5;

   /* calculate the log of the smaller area */
   if(x >= low && x <= high)
      return log(CDFNormal(x));
   if(x > high && x < -low)
      lnF = log(CDFNormal(-z));
   else {
      C = 1 - 1/(z*z) +  3/(z*z*z*z) - 15/(z*z*z*z*z*z) + 105/(z*z*z*z*z*z*z*z);
      lnF = -z*z/2 - log(sqrt(2*Pi)*z) + log(C);
   }
   if(x>0) {
      z = exp(lnF);
      lnF = -z*(1 + z/2 + z*z/3 + z*z*z/4 + z*z*z*z/5);
   }
   return(lnF);
}


double PDFCauchy (double x, double m, double sigma)
{
   double z = (x-m)/sigma;
   return 1/(Pi*sigma*(1 + z*z));
}

double PDFt (double x, double loc, double scale, double df, double lnConst)
{
/* CDF of t distribution with lococation, scale, and degree of freedom
*/
   double z = (x-loc)/scale, lnpdf=lnConst;
   
   if(lnpdf==0) {
      lnpdf = LnGamma((df+1)/2) - LnGamma(df/2) - 0.5*log(Pi*df);
   }
   lnpdf -= (df+1)/2 * log(1+z*z/df);
   return exp(lnpdf)/scale;
}

double CDFt (double x, double loc, double scale, double df, double lnbeta)
{
/* CDF of t distribution with location, scale, and degree of freedom
*/
   double z = (x-loc)/scale, cdf;
   double lnghalf = 0.57236494292470008707;  /* log{G(1/2)} = log{sqrt(Pi)} */

   if(lnbeta == 0) {
      lnbeta = LnGamma(df/2) + lnghalf - LnGamma((df+1)/2);
   }
   cdf = CDFBeta(df/(df+z*z), df/2, 0.5, lnbeta);

   if(z>=0) cdf = 1 - cdf/2;
   else     cdf /= 2;
   return(cdf);
}

double PDFSkewT (double x, double loc, double scale, double shape, double df)
{
   double z = (x-loc)/scale, pdf;
   double lnghalf=0.57236494292470008707;    /* log{G(1/2)} = log{sqrt(Pi)} */
   double lngv, lngv1, lnConst_pdft, lnbeta_cdft;

   lngv = LnGamma(df/2);
   lngv1 = LnGamma((df+1)/2);
   lnConst_pdft = lngv1 - lngv - 0.5*log(Pi*df);
   lnbeta_cdft = lngv1 + lnghalf - lngv - log(df/2);  /* log{ B((df+1)/2, 1/2) }  */

   pdf = 2/scale * PDFt(z, 0, 1, df, lnConst_pdft)
                 * CDFt(shape*z*sqrt((df+1)/(df+z*z)), 0, 1, df+1, lnbeta_cdft);

   return pdf;
}

double PDFSkewN (double x, double loc, double scale, double shape)
{
   double z = (x-loc)/scale, pdf = 2/scale;

   pdf *= PDFNormal(z,0,1) * CDFNormal(shape*z);
   return pdf;
}


double LnGamma (double x)
{
/* returns ln(gamma(x)) for x>0, accurate to 10 decimal places.
   Stirling's formula is used for the central polynomial part of the procedure.

   Pike MC & Hill ID (1966) Algorithm 291: Logarithm of the gamma function.
   Communications of the Association for Computing Machinery, 9:684
*/
   double f=0, fneg=0, z, lng;
   int nx=(int)x;

   if((double)nx==x && nx>=0 && nx<=11)
      lng = log((double)factorial(nx-1));
   else {
      if(x<=0) {
         printf("LnGamma(%.6f) not implemented", x);
         if((int)x-x==0) { puts("lnGamma undefined"); return(-1); }
         for (fneg=1; x<0; x++) fneg /= x;
         if(fneg<0) 
            error2("strange!! check lngamma");
         fneg = log(fneg);
      }
      if (x<7) {
         f = 1;
         z = x-1;
         while (++z<7)  
            f *= z;
         x = z;   
         f = -log(f);
      }
      z = 1/(x*x);
      lng = fneg+ f + (x-0.5)*log(x) - x + .918938533204673 
             + (((-.000595238095238*z+.000793650793651)*z-.002777777777778)*z
                  +.083333333333333)/x;
   }
   return  lng;
}

double PDFGamma (double x, double alpha, double beta)
{
/* gamma density: mean=alpha/beta; var=alpha/beta^2
*/
   if (x<=0 || alpha<=0 || beta<=0) {
      printf("x=%.6f a=%.6f b=%.6f", x, alpha, beta);
      error2("x a b outside range in PDFGamma()");
   }
   if (alpha>100)
      error2("large alpha in PDFGamma()");
   return pow(beta*x,alpha)/x * exp(-beta*x - LnGamma(alpha));
}

double PDF_InverseGamma (double x, double alpha, double beta)
{
/* inverse-gamma density: 
   mean=beta/(alpha-1); var=beta^2/[(alpha-1)^2*(alpha-2)]
*/
   if (x<=0 || alpha<=0 || beta<=0) {
      printf("x=%.6f a=%.6f b=%.6f", x, alpha, beta);
      error2("x a b outside range in PDF_IGamma()");
   }
   if (alpha>100)
      error2("large alpha in PDF_IGamma()");
   return pow(beta/x,alpha)/x * exp(-beta/x - LnGamma(alpha));
}


double IncompleteGamma (double x, double alpha, double ln_gamma_alpha)
{
/* returns the incomplete gamma ratio I(x,alpha) where x is the upper 
           limit of the integration and alpha is the shape parameter.
   returns (-1) if in error
   ln_gamma_alpha = ln(Gamma(alpha)), is almost redundant.
   (1) series expansion,     if (alpha>x || x<=1)
   (2) continued fraction,   otherwise
   RATNEST FORTRAN by
   Bhattacharjee GP (1970) The incomplete gamma integral.  Applied Statistics,
   19: 285-287 (AS32)
*/
   int i;
   double p=alpha, g=ln_gamma_alpha;
   double accurate=1e-10, overflow=1e60;
   double factor, gin=0, rn=0, a=0,b=0,an=0,dif=0, term=0, pn[6];

   if (x==0) return (0);
   if (x<0 || p<=0) return (-1);

   factor=exp(p*log(x)-x-g);   
   if (x>1 && x>=p) goto l30;
   /* (1) series expansion */
   gin=1;  term=1;  rn=p;
 l20:
   rn++;
   term *= x/rn;   gin += term;
   if (term > accurate) goto l20;
   gin *= factor/p;
   goto l50;
 l30:
   /* (2) continued fraction */
   a = 1-p;   b = a+x+1;  term = 0;
   pn[0] = 1;  pn[1] = x;  pn[2] = x+1;  pn[3] = x*b;
   gin = pn[2]/pn[3];
 l32:
   a++;  
   b += 2;
   term++;
   an = a*term;
   for (i=0; i<2; i++) 
      pn[i+4] = b*pn[i+2] - an*pn[i];
   if (pn[5] == 0) goto l35;
   rn = pn[4]/pn[5];
   dif = fabs(gin-rn);
   if (dif > accurate) goto l34;
   if (dif <= accurate*rn) goto l42;
 l34:
   gin = rn;
 l35:
   for (i=0; i<4; i++) pn[i] = pn[i+2];
   if (fabs(pn[4]) < overflow) goto l32;
   for (i=0; i<4; i++) pn[i] /= overflow;
   goto l32;
 l42:
   gin = 1-factor*gin;

 l50:
   return (gin);
}


double QuantileChi2 (double prob, double v)
{
/* returns z so that Prob{x<z}=prob where x is Chi2 distributed with df=v
   returns -1 if in error.   0.000002<prob<0.999998
   RATNEST FORTRAN by
       Best DJ & Roberts DE (1975) The percentage points of the 
       Chi2 distribution.  Applied Statistics 24: 385-388.  (AS91)
   Converted into C by Ziheng Yang, Oct. 1993.
*/
   double e=.5e-6, aa=.6931471805, p=prob, g, small=1e-6;
   double xx, c, ch, a=0,q=0,p1=0,p2=0,t=0,x=0,b=0,s1,s2,s3,s4,s5,s6;

   if (p<small)   return(0);
   if (p>1-small) return(9999);
   if (v<=0)      return (-1);

   g = LnGamma (v/2);
   xx=v/2;   c=xx-1;
   if (v >= -1.24*log(p)) goto l1;

   ch=pow((p*xx*exp(g+xx*aa)), 1/xx);
   if (ch-e<0) return (ch);
   goto l4;
l1:
   if (v>.32) goto l3;
   ch=0.4;   a=log(1-p);
l2:
   q=ch;  p1=1+ch*(4.67+ch);  p2=ch*(6.73+ch*(6.66+ch));
   t=-0.5+(4.67+2*ch)/p1 - (6.73+ch*(13.32+3*ch))/p2;
   ch-=(1-exp(a+g+.5*ch+c*aa)*p2/p1)/t;
   if (fabs(q/ch-1)-.01 <= 0) goto l4;
   else                       goto l2;
  
l3: 
   x = QuantileNormal(p);
   p1 = 0.222222/v;
   ch = v*pow((x*sqrt(p1)+1-p1), 3.0);
   if (ch>2.2*v+6)
      ch = -2*(log(1-p)-c*log(.5*ch)+g);
l4:
   q=ch;   p1=.5*ch;
   if ((t=IncompleteGamma (p1, xx, g))<0)
      error2("\nIncompleteGamma");
   p2=p-t;
   t=p2*exp(xx*aa+g+p1-c*log(ch));   
   b=t/ch;  a=0.5*t-b*c;

   s1=(210+a*(140+a*(105+a*(84+a*(70+60*a))))) / 420;
   s2=(420+a*(735+a*(966+a*(1141+1278*a))))/2520;
   s3=(210+a*(462+a*(707+932*a)))/2520;
   s4=(252+a*(672+1182*a)+c*(294+a*(889+1740*a)))/5040;
   s5=(84+264*a+c*(175+606*a))/2520;
   s6=(120+c*(346+127*c))/5040;
   ch+=t*(1+0.5*t*s1-b*c*(s1-b*(s2-b*(s3-b*(s4-b*(s5-b*s6))))));
   if (fabs(q/ch-1) > e) goto l4;

   return (ch);
}


int DiscreteGamma (double freqK[], double rK[], double alpha, double beta, int K, int dgammamean)
{
/* discretization of gamma distribution with equal proportions in each 
   category.
*/
   int i;
   double t, factor=alpha/beta*K, lnga1;

   if (dgammamean==0) {
      lnga1=LnGamma(alpha+1);
      for (i=0; i<K-1; i++) /* cutting points, Eq. 9 */
         freqK[i]=QuantileGamma((i+1.0)/K, alpha, beta);
      for (i=0; i<K-1; i++) /* Eq. 10 */
         freqK[i] = IncompleteGamma(freqK[i]*beta, alpha+1, lnga1);

      rK[0] = freqK[0]*factor;
      rK[K-1] = (1-freqK[K-2])*factor;
      for (i=1; i<K-1; i++)  rK[i] = (freqK[i]-freqK[i-1])*factor;
   }
   else {
      for(i=0; i<K; i++) rK[i] = QuantileGamma((i*2.+1)/(2.*K), alpha, beta);
      for(i=0,t=0; i<K; i++) t += rK[i];
      for(i=0; i<K; i++) rK[i] *= factor/t;
   }
   for (i=0; i<K; i++) freqK[i] = 1.0/K;

   return (0);
}


int AutodGamma (double M[], double freqK[], double rK[], double *rho1, double alpha, double rho, int K)
{
/* Auto-discrete-gamma distribution of rates over sites, K equal-probable
   categories, with the mean for each category used.
   This routine calculates M[], freqK[] and rK[], using alpha, rho and K.
*/
   int i,j, i1, i2;
   double *point=freqK;
   double x, y, large=20, v1;
/*
   if (fabs(rho)>1-1e-4) error2("rho out of range");
*/
   for(i=0; i<K-1; i++) 
      point[i]=QuantileNormal((i+1.0)/K);
   for (i=0; i<K; i++) {
      for (j=0; j<K; j++) {
         x = (i<K-1?point[i]:large);
         y = (j<K-1?point[j]:large);
         M[i*K+j] = CDFBinormal(x,y,rho);
      }
   }
   for (i1=0; i1<2*K-1; i1++) {
      for (i2=0; i2<K*K; i2++) {
         i=i2/K; j=i2%K;
         if (i+j != 2*(K-1)-i1) continue;
         y=0;
         if (i>0) y-= M[(i-1)*K+j];
         if (j>0) y-= M[i*K+(j-1)];
         if (i>0 && j>0) y += M[(i-1)*K+(j-1)];
         M[i*K+j] = (M[i*K+j]+y)*K;

         if (M[i*K+j]<0) printf("M(%d,%d) =%12.8f<0\n", i+1, j+1, M[i*K+j]);
      }
   }

   DiscreteGamma (freqK, rK, alpha, alpha, K, DGammaMean);

   for (i=0,v1=*rho1=0; i<K; i++) {
      v1+=rK[i]*rK[i]*freqK[i];
      for (j=0; j<K; j++)
         *rho1 += freqK[i]*M[i*K+j]*rK[i]*rK[j];
   }
   v1-=1;
   *rho1=(*rho1-1)/v1;
   return (0);
}



double LBinormal2Delete (double h, double k, double r)
{
/* L(h,k,r) = prob(x>h, y>k), where x and y are standard binormal, 
   with r = corr(x,y).

      (1) Drezner Z., and G.O. Wesolowsky (1990) On the computation of the
          bivariate normal integral.  J. Statist. Comput. Simul. 35:101-107.

      (2) Genz, A.C., Numerical computation of rectangular bivariate and 
          trivariate normal and t probabilities. Statist. Comput., 2004. 14: p. 1573-1375.

   This uses the algorithm of Genz (2004) for r>0, and 
        L(h,k,r) = F(-k) - L(-h, k, -r), if r<0.
   Here h<k is assumed.  If h>k, a swapping between h and k is performed.

   Gauss-Legendre quadrature points used.

     |r|                Genz     nGL
     <0.3   (eq. 3)       6       10
     <0.75  (eq. 3)      12       20
     <0.925 (eq. 3)      20       20
     <1     (eq. 6)      20       20
*/
   int nGL = (fabs(r)<0.3 ? 10 : 20), i,j, signr = (r>=0 ? 1 : -1);
   double *x=NULL, *w=NULL;  /* Gauss-Legendre quadrature points */
   double hk=h*k, h0=h,k0=k, L=0, t[2], hk2, y, a=0,b,c,d, bs, as, rs, smallr=1e-10;

   h=min2(h0,k0);  k=max2(h0,k0);
   if(signr==-1) { r=-r; h=-h; hk=h*k; }
   if(r>1) error2("|r| > 1 in LBinormal");
   GaussLegendreRule(&x, &w, nGL);

   if(r < 0.925) {  /* equation 3 */
      if(r>smallr) {
         hk2 = (h*h + k*k)/2; 
         a = asin(r)/2;
         for(i=0,L=0; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = sin(t[0]);
            t[1] = a*(1 + x[i]);  t[1] = sin(t[1]);
            for(j=0; j<2; j++)
               L += w[i]*exp((t[j]*hk - hk2)/(1 - t[j]*t[j]));
         }
      }
      L = L*a/(2*Pi) + CDFNormal(-h)*CDFNormal(-k);
   }
   else {   /* equation 6, using equation 7 instead of equation 5. */
      if(r>-1+smallr && r<1-smallr) {
         /* first term in equation (6), analytical */
         as = 1-r*r; 
         a = sqrt(as);
         b = fabs(h - k);
         bs = b*b;
         c = (4 - hk)/8 ; 
         d = (12 - hk)/16; 
         y = -(bs/as + hk)/2;
         if(y > -500) 
            L = a*exp(y)*(1 - c*(bs-as)*(1-d*bs/5)/3 + c*d*as*as/5);
         if(hk > -500) {
            L -= exp(-hk/2)*sqrt(2*Pi) * CDFNormal(-b/a) * b * (1 - c*bs*(1 - d*bs/5)/3);
         }
         /* second term in equation (6), numerical */
         a /= 2;
         for(i=0; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = t[0]*t[0];
            t[1] = a*(1 + x[i]);  t[1] = t[1]*t[1];
            for(j=0; j<2; j++) {
               rs = sqrt(1 - t[j]);
               y = -(bs/t[j] + hk)/2;
               if(y > -500)
                  L += a*w[i]*exp(y)*(exp(-hk*(1-rs)/(2*(1+rs)))/rs - (1+c*t[j]*(1+d*t[j])));
            }
         }
      }
      L = CDFNormal(-max2(h, k)) - L/(2*Pi);
   }
   if(signr<0)
      L = CDFNormal(-k) - L;
   if(L<-1e-12) printf("L = %.9g very negative.  Let me know please.\n", L);
   if(L<0) L=0;
   return (L);
}


double logLBinormal2Delete (double h, double k, double r)
{
/* this is to calculate the logarithm of tail probabilities of bivariate normal 
   distribution, modified from LBinormal().
   When r < 0, we use L(h,k,r) = F(-k) - L(-h, k, -r), where h < k.  
   In other words, 
   L(-10, 9, -1) = F(-9) - F(-10) is better than L(-10, 9, -1) = F(10) - F(9).
   So we use L(-10, 9, -0.3) = L(-9) - L(10, 9, 0.3).
   not       L(-10, 9, -0.3) = L(10) - L(-10, -9, 0.3).

   Results for the left tail, the very negative log(L), are reliable.  
   Results for the right tail are not reliable, that is, 
   if log(L) is close to 0 and L ~= 1.  Perhaps try to use the following to reflect:
      L(-5,-9,r) = 1 - [ F(-5) + F(-9) - L(5,9,r) ]
   Check the routine logCDFNormal() to see the idea.
*/
   int nGL = (fabs(r)<0.3 ? 10 : 20), i,j, signr = (r>=0 ? 1 : -1);
   double *x=NULL, *w=NULL;  /* Gauss-Legendre quadrature points */
   double hk=h*k, h0=h,k0=k, L, t[2], hk2, a,b,c,d, bs, as, rs;
   double S1,S2=-1e300,S3=-1e300, y,L2=0,L3=0, largeneg=-1e300, smallr=1e-10;

   h=min2(h0,k0);  k=max2(h0,k0);
   if(signr==-1) { r=-r; h=-h; hk=-hk; }
   if(fabs(r)>1+smallr) error2("|r| > 1 in LBinormal");
   GaussLegendreRule(&x, &w, nGL);

   if(r < 0.925) {  /* equation 3 */
      S1 = L = logCDFNormal(-h) + logCDFNormal(-k);
      if(r>smallr) {
         hk2 = (h*h + k*k)/2;
         a = asin(r)/2;
         for(i=0,L=0,S2=-hk2; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = sin(t[0]);
            t[1] = a*(1 + x[i]);  t[1] = sin(t[1]);
            for(j=0; j<2; j++) {
               y = -(hk2 - t[j]*hk)/(1 - t[j]*t[j]);
               if(y>S2+30) {
                  L *= exp(S2-y);
                  S2 = y;
               }
               L += w[i]*exp(y-S2);
            }
         }
         y = max2(S1,S2);
         a = exp(S1-y) + L*a/(2*Pi)*exp(S2-y);
         L = (a>0 ? y + log(a) : largeneg);
      }
   }
   else {   /* equation 6, using equation 7 instead of equation 5. */
      /*  log(L) = exp(S1) + L2*exp(S2) + L3*exp(S3)  */
      if(r>-1+smallr && r<1-smallr) {

         /* first term in equation (6), analytical:  L2 & S2 */
         as = 1-r*r; 
         a = sqrt(as); 
         b = fabs(h - k);
         bs = b*b;
         c = (4 - hk)/8;
         d = (12 - hk)/16;
         S2 = -(bs/as + hk)/2;  /* is this too large? */
         L2 = a*(1 - c*(bs-as)*(1-d*bs/5)/3 + c*d*as*as/5);
         y = -hk/2 + logCDFNormal(-b/a);
         if(y>S2+30) {
            L2 *= exp(S2-y);
            S2 = y;
         }
         L2 -= sqrt(2*Pi) * exp(y-S2) * b * (1 - c*bs*(1 - d*bs/5)/3);

         /* second term in equation (6), numerical: L3 & S3 */
         a /= 2;
         for(i=0,L3=0,S3=-1e300; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = t[0]*t[0];
            t[1] = a*(1 + x[i]);  t[1] = t[1]*t[1];
            for(j=0; j<2; j++) {
               rs = sqrt(1 - t[j]);
               y = -(bs/t[j] + hk)/2;
               if(y > S3+30) {
                  L3 *= exp(S3-y);
                  S3 = y;
               }
               L3 += a*w[i]*exp(y-S3) * (exp(-hk*(1-rs)/(2*(1+rs)))/rs - (1+c*t[j]*(1+d*t[j])));
            }
         }
      }

      S1 = logCDFNormal(-max2(h, k));
      y = max2(S1,S2); y = max2(y,S3);
      a = exp(S1-y) - (L2*exp(S2-y) + L3*exp(S3-y))/(2*Pi);
      L = (a>0 ? y + log(a) : largeneg);
   }

   if(signr==-1) {  /* r<0:  L(h,k,-r) = F(-k) - L(-h,k,r) */
      S1 = logCDFNormal(-k);
      y = max2(S1,L);
      a = exp(S1-y) - exp(L-y);
      L = (a > 0 ? y + log(a) : largeneg);
   }
   if(L>1e-12)
      printf("ln L(%2g, %.2g, %.2g) = %.6g is very large.\n", h0,k0,r*signr, L);
   if(L>0)  L=0;

   return(L);
}


double LBinormal (double h, double k, double r)
{
/* L(h,k,r) = prob(X>h, Y>k), where X and Y are standard binormal variables, 
   with r = corr(X, Y).

      (1) Drezner Z., and G.O. Wesolowsky (1990) On the computation of the
          bivariate normal integral.  J. Statist. Comput. Simul. 35:101-107.

      (2) Genz, A.C., Numerical computation of rectangular bivariate and 
          trivariate normal and t probabilities. Statist. Comput., 2004. 14: p. 1573-1375.

   This uses the algorithm of Genz (2004).  
   Here h<k is assumed.  If h>k, a swapping between h and k is performed.

   Gauss-Legendre quadrature points used.

     |r|                Genz     nGL
     <0.3   (eq. 3)       6       10
     <0.75  (eq. 3)      12       20
     <0.925 (eq. 3)      20       20
     <1     (eq. 6)      20       20
*/
   int nGL = (fabs(r)<0.3 ? 10 : 20), i,j;
   double *x=NULL, *w=NULL;  /* Gauss-Legendre quadrature points */
   double shk, h0=h,k0=k, sk, L=0, t[2], hk2, y, a=0,b,c,d, bs, as, rs, smallr=1e-10;

   h=min2(h0,k0);  k=max2(h0,k0);
   sk = (r>=0 ? k : -k);
   shk = (r>=0 ? h*k : -h*k);
   if(fabs(r)>1) error2("|r| > 1 in LBinormal");
   GaussLegendreRule(&x, &w, nGL);

   if(fabs(r) < 0.925) {  /* equation 3 */
      if(fabs(r)>smallr) {
         hk2 = (h*h + k*k)/2; 
         a = asin(r)/2;
         for(i=0,L=0; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = sin(t[0]);
            t[1] = a*(1 + x[i]);  t[1] = sin(t[1]);
            for(j=0; j<2; j++)
               L += w[i]*exp((t[j]*h*k - hk2)/(1 - t[j]*t[j]));
         }
      }
      L = L*a/(2*Pi) + CDFNormal(-h)*CDFNormal(-k);
   }
   else {   /* equation 6, using equation 7 instead of equation 5. */
      if(fabs(r) < 1) {
         /* first term in equation (6), analytical */
         as = 1-r*r; 
         a = sqrt(as);
         b = fabs(h - sk);
         bs = b*b;
         c = (4 - shk)/8 ; 
         d = (12 - shk)/16; 
         y = -(bs/as + shk)/2;
         if(y > -500) 
            L = a*exp(y)*(1 - c*(bs-as)*(1-d*bs/5)/3 + c*d*as*as/5);
         if(shk > -500) {
            L -= exp(-shk/2)*sqrt(2*Pi) * CDFNormal(-b/a) * b * (1 - c*bs*(1 - d*bs/5)/3);
         }
         /* second term in equation (6), numerical */
         a /= 2;
         for(i=0; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = t[0]*t[0];
            t[1] = a*(1 + x[i]);  t[1] = t[1]*t[1];
            for(j=0; j<2; j++) {
               rs = sqrt(1 - t[j]);
               y = -(bs/t[j] + shk)/2;
               if(y > -500)
                  L += a*w[i]*exp(y)*(exp(-shk*(1-rs)/(2*(1+rs)))/rs - (1+c*t[j]*(1+d*t[j])));
            }
         }
         L /= -2*Pi;
      }
      if(r>0)
         L += CDFNormal(-max2(h, k));
      else if(r<0) {
         L = -L;
         if(h+k<0) 
            L += CDFNormal(-h) - CDFNormal(k);
      }
   }

   if(L<-1e-12) printf("L = %.9g very negative.  Let me know please.\n", L);
   if(L<0) L=0;
   return (L);
}


double logLBinormal (double h, double k, double r)
{
/* This calculates the logarithm of the tail probability 
   log{Pr(X>h, Y>k)} where X and Y have a standard bivariate normal distribution
   with correlation r.  This is modified from LBinormal().

   L(-10, 9, -1) = F(-9) - F(-10) is better than L(-10, 9, -1) = F(10) - F(9).
   So we use L(-10, 9, -0.3) = F(-9) - L(10, 9, 0.3).
   not       L(-10, 9, -0.3) = F(10) - L(-10, -9, 0.3).

   Results for the left tail, the very negative log(L), are reliable.  
   Results for the right tail are not reliable, that is, 
   if log(L) is close to 0 and L ~= 1.  Perhaps try to use the following to reflect:
      L(-5,-9,r) = 1 - [ F(-5) + F(-9) - L(5,9,r) ]
   See logCDFNormal() for more details of the idea.
*/
   int nGL = (fabs(r)<0.3 ? 10 : 20), i,j;
   double *x=NULL, *w=NULL;  /* Gauss-Legendre quadrature points */
   double shk, h0=h,k0=k, sk, L, t[2], hk2, a,b,c,d, bs, as, rs, signr=(r>=0?1:-1);
   double S1=0,S2=-1e300,S3=-1e300, y,L1=0,L2=0,L3=0, largeneg=-1e300, smallr=1e-10;

   h=min2(h0,k0);  k=max2(h0,k0);
   sk = signr*k;
   shk = signr*h*k;
   if(fabs(r)>1+smallr) error2("|r| > 1 in LBinormal");
   GaussLegendreRule(&x, &w, nGL);

   if(fabs(r) < 0.925) {  /* equation 3 */
      S1 = L = logCDFNormal(-h) + logCDFNormal(-k);
      if(fabs(r) > smallr) {  /* this saves computation for the case of r = 0 */
         hk2 = (h*h + k*k)/2;
         a = asin(r)/2;
         for(i=0,L2=0,S2=-hk2; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = sin(t[0]);
            t[1] = a*(1 + x[i]);  t[1] = sin(t[1]);
            for(j=0; j<2; j++) {
               y = -(hk2 - t[j]*h*k)/(1 - t[j]*t[j]);
               if(y > S2+30) {
                  L *= exp(S2-y);
                  S2 = y;
               }
               L2 += a*w[i]*exp(y-S2);
            }
         }
         L2 /= 2*Pi;
         y = max2(S1, S2);
         a = exp(S1-y) + L2*exp(S2-y);
         L = (a>0 ? y + log(a) : largeneg);
      }
   }
   else {   /* equation 6, using equation 7 instead of equation 5. */
      /*  L = L1*exp(S1) + L2*exp(S2) + L3*exp(S3)  */
      if(fabs(r)<1) {
         /* first term in equation (6), analytical:  L2 & S2 */
         as = 1-r*r; 
         a = sqrt(as); 
         b = fabs(h - sk);
         bs = b*b;
         c = (4 - shk)/8;
         d = (12 - shk)/16;
         S2 = -(bs/as + shk)/2;  /* is this too large? */
         L2 = a*(1 - c*(bs-as)*(1-d*bs/5)/3 + c*d*as*as/5);
         y = -shk/2 + logCDFNormal(-b/a);
         if(y>S2+30) {
            L2 *= exp(S2-y);
            S2 = y;
         }
         L2 -= sqrt(2*Pi) * exp(y-S2) * b * (1 - c*bs*(1 - d*bs/5)/3);

         /* second term in equation (6), numerical: L3 & S3 */
         a /= 2;
         for(i=0,L3=0,S3=-1e300; i<nGL/2; i++) {
            t[0] = a*(1 - x[i]);  t[0] = t[0]*t[0];
            t[1] = a*(1 + x[i]);  t[1] = t[1]*t[1];
            for(j=0; j<2; j++) {
               rs = sqrt(1 - t[j]);
               y = -(bs/t[j] + shk)/2;
               if(y > S3+30) {
                  L3 *= exp(S3-y);
                  S3 = y;
               }
               L3 += a*w[i]*exp(y-S3) * (exp(-shk*(1-rs)/(2*(1+rs)))/rs - (1+c*t[j]*(1+d*t[j])));
            }
         }
      }


      /* L(h,k,s) term in equation (6), L1 & S1 */
      if(r>0) {
         S1 = logCDFNormal(-max2(h, k));
         L1 = 1;
      }
      else if (r<0 && h+k<0) {
         a = logCDFNormal(-k);
         y = logCDFNormal(h);
         S1 = max2(a,y);
         L1 = exp(a-S1) - exp(y-S1);
      }

      y = max2(S1,S2);
      y = max2(y,S3);
      a = L1*exp(S1-y) - signr/(2*Pi) * (L2*exp(S2-y) + L3*exp(S3-y));

      L = (a>0 ? y + log(a) : largeneg);
   }

   if(L>1e-12)
      printf("ln L(%2g, %.2g, %.2g) = %.6g is very large.\n", h0, k0, r, L);
   if(L>0)  L=0;

   return(L);
}

#if (0)
void testLBinormal (void)
{
   double x,y,r, L, lnL;
  
   for(r=-1; r<1.01; r+=0.05) {
      if(fabs(r-1)<1e-5) r=1;
      printf("\nr = %.2f\n", r);
      for(x=-10; x<=10.01; x+=0.5) {
         for(y=-10; y<=10.01; y+=0.5) {

            printf("x y r? ");  scanf("%lf%lf%lf", &x, &y, &r);

            L = LBinormal(x,y,r);
            lnL = logLBinormal(x,y,r);

            if(fabs(L-exp(lnL))>1e-10)
               printf("L - exp(lnL) = %.10g very different.\n", L - exp(lnL));

//            if(L<0 || L>1)
               printf("%6.2f %6.2f %6.2f L %15.8g = %15.8g %9.5g\n", x,y,r, L, exp(lnL), lnL);
               
            if(lnL>0)  exit(-1);
         }
      }
   }
}
#endif


double probBinomial (int n, int k, double p)
{
/* calculates  {n\choose k} * p^k * (1-p)^(n-k)
*/
   double C, up, down;

   if (n<40 || (n<1000&&k<10)) {
      for (down=min2(k,n-k),up=n,C=1; down>0; down--,up--) C*=up/down;
      if (fabs(p-.5)<1e-6) C *= pow(p,(double)n);
      else                 C *= pow(p,(double)k)*pow((1-p),(double)(n-k));
   }
   else  {
      C = exp((LnGamma(n+1.)-LnGamma(k+1.)-LnGamma(n-k+1.))/n);
      C = pow(p*C,(double)k) * pow((1-p)*C,(double)(n-k));
   }
   return C;
}


double probBetaBinomial (int n, int k, double p, double q)
{
/* This calculates beta-binomial probability of k succeses out of n trials,
   The binomial probability parameter has distribution beta(p, q)

   prob(x) = C1(-a,k) * C2(-b,n-k)/C3(-a-b,n)
*/
   double a=p,b=q, C1,C2,C3,scale1,scale2,scale3;

   if(a<=0 || b<=0) return(0);
   C1 = Binomial(-a, k, &scale1);
   C2 = Binomial(-b, n-k, &scale2);
   C3 = Binomial(-a-b, n, &scale3);
   C1 *= C2/C3;
   if(C1<0) 
      error2("error in probBetaBinomial");
   return C1*exp(scale1+scale2-scale3);
}


double PDFBeta (double x, double p, double q)
{
/* Returns pdf of beta(p,q)
*/
   double y, small=1e-20;

   if(x<small || x>1-small) 
      error2("bad x in PDFbeta");

   y = (p-1)*log(x) + (q-1)*log(1-x);
   y-= LnGamma(p) + LnGamma(q) - LnGamma(p+q);

   return(exp(y));
}

double CDFBeta (double x, double pin, double qin, double lnbeta)
{
/* Returns distribution function of the standard form of the beta distribution, 
   that is, the incomplete beta ratio I_x(p,q).

   This is also known as the incomplete beta function ratio I_x(p, q)

   lnbeta is log of the complete beta function; provide it if known,
   and otherwise use 0.

   This is called from QuantileBeta() in a root-finding loop.

    This routine is a translation into C of a Fortran subroutine
    by W. Fullerton of Los Alamos Scientific Laboratory.
    Bosten and Battiste (1974).
    Remark on Algorithm 179, CACM 17, p153, (1974).
*/
   double ans, c, finsum, p, ps, p1, q, term, xb, xi, y, small=1e-15;
   int n, i, ib;
   static double eps = 0, alneps = 0, sml = 0, alnsml = 0;

   if(x<small)        return 0;
   else if(x>1-small) return 1;
   if(pin<=0 || qin<=0)  { 
      printf("p=%.4f q=%.4f: parameter outside range in CDFBeta",pin,qin); 
      return (-1); 
   }

   if (eps == 0) {/* initialize machine constants ONCE */
      eps = pow((double)FLT_RADIX, -(double)DBL_MANT_DIG);
      alneps = log(eps);
      sml = DBL_MIN;
      alnsml = log(sml);
   }
   y = x;  p = pin;  q = qin;

    /* swap tails if x is greater than the mean */
   if (p / (p + q) < x) {
      y = 1 - y;
      p = qin;
      q = pin;
   }

   if(lnbeta==0) lnbeta = LnGamma(p) + LnGamma(q) - LnGamma(p+q);

   if ((p + q) * y / (p + 1) < eps) {  /* tail approximation */
      ans = 0;
      xb = p * log(max2(y, sml)) - log(p) - lnbeta;
      if (xb > alnsml && y != 0)
         ans = exp(xb);
      if (y != x || p != pin)
      ans = 1 - ans;
   }
   else {
      /* evaluate the infinite sum first.  term will equal */
      /* y^p / beta(ps, p) * (1 - ps)-sub-i * y^i / fac(i) */
      ps = q - floor(q);
      if (ps == 0)
         ps = 1;

      xb=LnGamma(ps)+LnGamma(p)-LnGamma(ps+p);
      xb = p * log(y) - xb - log(p);

      ans = 0;
      if (xb >= alnsml) {
         ans = exp(xb);
         term = ans * p;
         if (ps != 1) {
            n = (int)max2(alneps/log(y), 4.0);
         for(i=1 ; i<= n ; i++) {
            xi = i;
            term = term * (xi - ps) * y / xi;
            ans = ans + term / (p + xi);
         }
      }
   }

   /* evaluate the finite sum. */
   if (q > 1) {
      xb = p * log(y) + q * log(1 - y) - lnbeta - log(q);
      ib = (int) (xb/alnsml);  if(ib<0) ib=0;
      term = exp(xb - ib * alnsml);
      c = 1 / (1 - y);
      p1 = q * c / (p + q - 1);

      finsum = 0;
      n = (int) q;
      if (q == (double)n)
         n = n - 1;
         for(i=1 ; i<=n ; i++) {
            if (p1 <= 1 && term / eps <= finsum)
               break;
            xi = i;
            term = (q - xi + 1) * c * term / (p + q - xi);
            if (term > 1) {
               ib = ib - 1;
               term = term * sml;
            }
            if (ib == 0)
               finsum = finsum + term;
         }
         ans = ans + finsum;
      }
      if (y != x || p != pin)
         ans = 1 - ans;
      if(ans>1) ans=1;
      if(ans<0) ans=0;
   }
   return ans;
}

double QuantileBeta(double prob, double p, double q, double lnbeta)
{
/* This calculates the Quantile of the beta distribution

   Cran, G. W., K. J. Martin and G. E. Thomas (1977).
   Remark AS R19 and Algorithm AS 109, Applied Statistics, 26(1), 111-114.
   Remark AS R83 (v.39, 309-310) and correction (v.40(1) p.236).

   My own implementation of the algorithm did not bracket the variable well.  
   This version is Adpated from the pbeta and qbeta routines from 
   "R : A Computer Language for Statistical Data Analysis".  It fails for 
   extreme values of p and q as well, although it seems better than my 
   previous version.
   Ziheng Yang, May 2001
*/
   double fpu=3e-308, acu_min=1e-300, lower=fpu, upper=1-2.22e-16;
   /* acu_min>= fpu: Minimal value for accuracy 'acu' which will depend on (a,p); */
   int swap_tail, i_pb, i_inn, niterations=2000;
   double a, adj, g, h, pp, prev=0, qq, r, s, t, tx=0, w, y, yprev;
   double acu, xinbta;

   if(prob<0 || prob>1 || p<0 || q<0) error2("out of range in QuantileBeta");

   /* define accuracy and initialize */
   xinbta = prob;

   /* test for admissibility of parameters */
   if(p<0 || q<0 || prob<0 || prob>1)  error2("beta par err");
   if (prob == 0 || prob == 1)
      return prob;

   if(lnbeta==0) lnbeta=LnGamma(p)+LnGamma(q)-LnGamma(p+q);

   /* change tail if necessary;  afterwards   0 < a <= 1/2    */
   if (prob <= 0.5) {
      a = prob;   pp = p; qq = q; swap_tail = 0;
   }
   else {
      a = 1. - prob; pp = q; qq = p; swap_tail = 1;
   }

   /* calculate the initial approximation */
   r = sqrt(-log(a * a));
   y = r - (2.30753+0.27061*r)/(1.+ (0.99229+0.04481*r) * r);

   if (pp > 1. && qq > 1.) {
      r = (y * y - 3.) / 6.;
      s = 1. / (pp*2. - 1.);
      t = 1. / (qq*2. - 1.);
      h = 2. / (s + t);
      w = y * sqrt(h + r) / h - (t - s) * (r + 5./6. - 2./(3.*h));
      xinbta = pp / (pp + qq * exp(w + w));
   }
   else {
      r = qq*2.;
      t = 1. / (9. * qq);
      t = r * pow(1. - t + y * sqrt(t), 3.);
      if (t <= 0.)
         xinbta = 1. - exp((log((1. - a) * qq) + lnbeta) / qq);
      else {
         t = (4.*pp + r - 2.) / t;
         if (t <= 1.)
            xinbta = exp((log(a * pp) + lnbeta) / pp);
         else
            xinbta = 1. - 2./(t+1.);
      }
   }

   /* solve for x by a modified newton-raphson method, using CDFBeta */
   r = 1. - pp;
   t = 1. - qq;
   yprev = 0.;
   adj = 1.;


   
/* Changes made by Ziheng to fix a bug in qbeta()
   qbeta(0.25, 0.143891, 0.05) = 3e-308   wrong (correct value is 0.457227)
*/
   if(xinbta<=lower || xinbta>=upper)  xinbta=(a+.5)/2;

   /* Desired accuracy should depend on (a,p)
    * This is from Remark .. on AS 109, adapted.
    * However, it's not clear if this is "optimal" for IEEE double prec.
    * acu = fmax2(acu_min, pow(10., -25. - 5./(pp * pp) - 1./(a * a)));
    * NEW: 'acu' accuracy NOT for squared adjustment, but simple;
    * ---- i.e.,  "new acu" = sqrt(old acu)
    */
   acu = pow(10., -13. - 2.5/(pp * pp) - 0.5/(a * a));
   acu = max2(acu, acu_min);

   for (i_pb=0; i_pb<niterations; i_pb++) {
      y = CDFBeta(xinbta, pp, qq, lnbeta);
      y = (y - a) *
         exp(lnbeta + r * log(xinbta) + t * log(1. - xinbta));
      if (y * yprev <= 0)
         prev = max2(fabs(adj),fpu);
      for (i_inn=0,g=1; i_inn<niterations; i_inn++) {
         adj = g * y;
         if (fabs(adj) < prev) {
            tx = xinbta - adj; /* trial new x */
            if (tx >= 0. && tx <= 1.) {
               if (prev <= acu || fabs(y) <= acu)   goto L_converged;
               if (tx != 0. && tx != 1.)  break;
            }
         }
         g /= 3.;
      }
      if (fabs(tx-xinbta)<fpu) 
         goto L_converged;
      xinbta = tx;
      yprev = y;
   }
   if(!PAML_RELEASE) 
      printf("\nQuantileBeta(%.2f, %.5f, %.5f) = %.6e\t%d rounds\n", 
         prob,p,q, (swap_tail ? 1. - xinbta : xinbta), niterations);

   L_converged:
   return (swap_tail ? 1. - xinbta : xinbta);
}


static double prob_Quantile, *par_Quantile;
static double (*cdf_Quantile)(double x,double par[]);
double diff_Quantile(double x);

double diff_Quantile(double x)
{
/* This is the difference between the given p and the CDF(x), the 
   objective function to be minimized.
*/
   double px=(*cdf_Quantile)(x,par_Quantile);
   return(square(prob_Quantile-px));
}

double Quantile(double(*cdf)(double x,double par[]),
       double p,double x,double par[],double xb[2])
{
/* Use x for initial value if in range
*/
   int noisy0=noisy;
   double sdiff,step=min2(0.05,(xb[1]-xb[0])/100), e=1e-15;

   noisy=0;
   prob_Quantile=p;  par_Quantile=par; cdf_Quantile=cdf;
   if(x<=xb[0]||x>=xb[1]) x=.5;
   LineSearch(diff_Quantile, &sdiff, &x, xb, step, e);
   noisy=noisy0;

   return(x);
}




int GaussLegendreRule(double **x, double **w, int npoints)
{
/* This returns the Gauss-Legendre nodes and weights in x[] and w[].
   npoints = 10, 20, 32, 64, 128, 256, 512, 1024
*/
   int status=0;   
   static double x4[]  = {0.3399810435848562648026658, 0.8611363115940525752239465};
   static double w4[]  = {0.6521451548625461426269361, 0.3478548451374538573730639};

   static double x8[]  = {0.1834346424956498049394761, 0.5255324099163289858177390, 
                          0.7966664774136267395915539, 0.9602898564975362316835609};
   static double w8[]  = {0.3626837833783619829651504, 0.3137066458778872873379622, 
                          0.2223810344533744705443560, 0.1012285362903762591525314};

   static double x16[] = {0.0950125098376374401853193, 0.2816035507792589132304605, 
                          0.4580167776572273863424194, 0.6178762444026437484466718, 
                          0.7554044083550030338951012, 0.8656312023878317438804679, 
                          0.9445750230732325760779884, 0.9894009349916499325961542};
   static double w16[] = {0.1894506104550684962853967, 0.1826034150449235888667637, 
                          0.1691565193950025381893121, 0.1495959888165767320815017, 
                          0.1246289712555338720524763, 0.0951585116824927848099251, 
                          0.0622535239386478928628438, 0.0271524594117540948517806};

   static double x32[] = {0.048307665687738316234812570441, 0.144471961582796493485186373599, 
                        0.239287362252137074544603209166, 0.331868602282127649779916805730, 
                        0.421351276130635345364119436172, 0.506899908932229390023747474378, 
                        0.587715757240762329040745476402, 0.663044266930215200975115168663,
                        0.732182118740289680387426665091, 0.794483795967942406963097298970, 
                        0.849367613732569970133693004968, 0.896321155766052123965307243719, 
                        0.934906075937739689170919134835, 0.964762255587506430773811928118, 
                        0.985611511545268335400175044631, 0.997263861849481563544981128665};
   static double w32[] = {0.0965400885147278005667648300636, 0.0956387200792748594190820022041, 
                        0.0938443990808045656391802376681, 0.0911738786957638847128685771116, 
                        0.0876520930044038111427714627518, 0.0833119242269467552221990746043, 
                        0.0781938957870703064717409188283, 0.0723457941088485062253993564785, 
                        0.0658222227763618468376500637069, 0.0586840934785355471452836373002, 
                        0.0509980592623761761961632446895, 0.0428358980222266806568786466061, 
                        0.0342738629130214331026877322524, 0.0253920653092620594557525897892, 
                        0.0162743947309056706051705622064, 0.0070186100094700966004070637389};

   static double x64[] = {0.024350292663424432508955842854, 0.072993121787799039449542941940, 
                        0.121462819296120554470376463492, 0.169644420423992818037313629748, 
                        0.217423643740007084149648748989, 0.264687162208767416373964172510, 
                        0.311322871990210956157512698560, 0.357220158337668115950442615046, 
                        0.402270157963991603695766771260, 0.446366017253464087984947714759, 
                        0.489403145707052957478526307022, 0.531279464019894545658013903544, 
                        0.571895646202634034283878116659, 0.611155355172393250248852971019, 
                        0.648965471254657339857761231993, 0.685236313054233242563558371031,  
                        0.719881850171610826848940217832, 0.752819907260531896611863774886, 
                        0.783972358943341407610220525214, 0.813265315122797559741923338086, 
                        0.840629296252580362751691544696, 0.865999398154092819760783385070, 
                        0.889315445995114105853404038273, 0.910522137078502805756380668008, 
                        0.929569172131939575821490154559, 0.946411374858402816062481491347, 
                        0.961008799652053718918614121897, 0.973326827789910963741853507352, 
                        0.983336253884625956931299302157, 0.991013371476744320739382383443, 
                        0.996340116771955279346924500676, 0.999305041735772139456905624346};
   static double w64[] = {0.0486909570091397203833653907347, 0.0485754674415034269347990667840, 
                        0.0483447622348029571697695271580, 0.0479993885964583077281261798713,
                        0.0475401657148303086622822069442, 0.0469681828162100173253262857546, 
                        0.0462847965813144172959532492323, 0.0454916279274181444797709969713, 
                        0.0445905581637565630601347100309, 0.0435837245293234533768278609737, 
                        0.0424735151236535890073397679088, 0.0412625632426235286101562974736, 
                        0.0399537411327203413866569261283, 0.0385501531786156291289624969468, 
                        0.0370551285402400460404151018096, 0.0354722132568823838106931467152, 
                        0.0338051618371416093915654821107, 0.0320579283548515535854675043479, 
                        0.0302346570724024788679740598195, 0.0283396726142594832275113052002, 
                        0.0263774697150546586716917926252, 0.0243527025687108733381775504091, 
                        0.0222701738083832541592983303842, 0.0201348231535302093723403167285, 
                        0.0179517157756973430850453020011, 0.0157260304760247193219659952975, 
                        0.0134630478967186425980607666860, 0.0111681394601311288185904930192, 
                        0.0088467598263639477230309146597, 0.0065044579689783628561173604000, 
                        0.0041470332605624676352875357286, 0.0017832807216964329472960791450};

   static double x128[] = {0.0122236989606157641980521, 0.0366637909687334933302153, 
                        0.0610819696041395681037870, 0.0854636405045154986364980, 
                        0.1097942311276437466729747, 0.1340591994611877851175753, 
                        0.1582440427142249339974755, 0.1823343059853371824103826, 
                        0.2063155909020792171540580, 0.2301735642266599864109866, 
                        0.2538939664226943208556180, 0.2774626201779044028062316, 
                        0.3008654388776772026671541, 0.3240884350244133751832523, 
                        0.3471177285976355084261628, 0.3699395553498590266165917, 
                        0.3925402750332674427356482, 0.4149063795522750154922739, 
                        0.4370245010371041629370429, 0.4588814198335521954490891, 
                        0.4804640724041720258582757, 0.5017595591361444642896063, 
                        0.5227551520511754784539479, 0.5434383024128103634441936, 
                        0.5637966482266180839144308, 0.5838180216287630895500389, 
                        0.6034904561585486242035732, 0.6228021939105849107615396, 
                        0.6417416925623075571535249, 0.6602976322726460521059468, 
                        0.6784589224477192593677557, 0.6962147083695143323850866, 
                        0.7135543776835874133438599, 0.7304675667419088064717369, 
                        0.7469441667970619811698824, 0.7629743300440947227797691, 
                        0.7785484755064119668504941, 0.7936572947621932902433329, 
                        0.8082917575079136601196422, 0.8224431169556438424645942, 
                        0.8361029150609068471168753, 0.8492629875779689691636001, 
                        0.8619154689395484605906323, 0.8740527969580317986954180, 
                        0.8856677173453972174082924, 0.8967532880491581843864474, 
                        0.9073028834017568139214859, 0.9173101980809605370364836, 
                        0.9267692508789478433346245, 0.9356743882779163757831268, 
                        0.9440202878302201821211114, 0.9518019613412643862177963, 
                        0.9590147578536999280989185, 0.9656543664319652686458290, 
                        0.9717168187471365809043384, 0.9771984914639073871653744, 
                        0.9820961084357185360247656, 0.9864067427245862088712355, 
                        0.9901278184917343833379303, 0.9932571129002129353034372, 
                        0.9957927585349811868641612, 0.9977332486255140198821574, 
                        0.9990774599773758950119878, 0.9998248879471319144736081};
  static double w128[]  =  {0.0244461801962625182113259, 0.0244315690978500450548486, 
                        0.0244023556338495820932980, 0.0243585572646906258532685, 
                        0.0243002001679718653234426, 0.0242273192228152481200933, 
                        0.0241399579890192849977167, 0.0240381686810240526375873, 
                        0.0239220121367034556724504, 0.0237915577810034006387807, 
                        0.0236468835844476151436514, 0.0234880760165359131530253, 
                        0.0233152299940627601224157, 0.0231284488243870278792979, 
                        0.0229278441436868469204110, 0.0227135358502364613097126, 
                        0.0224856520327449668718246, 0.0222443288937997651046291, 
                        0.0219897106684604914341221, 0.0217219495380520753752610, 
                        0.0214412055392084601371119, 0.0211476464682213485370195, 
                        0.0208414477807511491135839, 0.0205227924869600694322850, 
                        0.0201918710421300411806732, 0.0198488812328308622199444, 
                        0.0194940280587066028230219, 0.0191275236099509454865185, 
                        0.0187495869405447086509195, 0.0183604439373313432212893, 
                        0.0179603271850086859401969, 0.0175494758271177046487069, 
                        0.0171281354231113768306810, 0.0166965578015892045890915, 
                        0.0162550009097851870516575, 0.0158037286593993468589656, 
                        0.0153430107688651440859909, 0.0148731226021473142523855, 
                        0.0143943450041668461768239, 0.0139069641329519852442880, 
                        0.0134112712886163323144890, 0.0129075627392673472204428, 
                        0.0123961395439509229688217, 0.0118773073727402795758911, 
                        0.0113513763240804166932817, 0.0108186607395030762476596, 
                        0.0102794790158321571332153, 0.0097341534150068058635483, 
                        0.0091830098716608743344787, 0.0086263777986167497049788, 
                        0.0080645898904860579729286, 0.0074979819256347286876720, 
                        0.0069268925668988135634267, 0.0063516631617071887872143, 
                        0.0057726375428656985893346, 0.0051901618326763302050708, 
                        0.0046045842567029551182905, 0.0040162549837386423131943, 
                        0.0034255260409102157743378, 0.0028327514714579910952857, 
                        0.0022382884309626187436221, 0.0016425030186690295387909, 
                        0.0010458126793403487793129, 0.0004493809602920903763943};

   static double x256[]  =  {0.0061239123751895295011702, 0.0183708184788136651179263, 
                        0.0306149687799790293662786, 0.0428545265363790983812423, 
                        0.0550876556946339841045614, 0.0673125211657164002422903, 
                        0.0795272891002329659032271, 0.0917301271635195520311456, 
                        0.1039192048105094036391969, 0.1160926935603328049407349, 
                        0.1282487672706070947420496, 0.1403856024113758859130249, 
                        0.1525013783386563953746068, 0.1645942775675538498292845, 
                        0.1766624860449019974037218, 0.1887041934213888264615036, 
                        0.2007175933231266700680007, 0.2127008836226259579370402, 
                        0.2246522667091319671478783, 0.2365699497582840184775084, 
                        0.2484521450010566668332427, 0.2602970699919425419785609, 
                        0.2721029478763366095052447, 0.2838680076570817417997658, 
                        0.2955904844601356145637868, 0.3072686197993190762586103, 
                        0.3189006618401062756316834, 0.3304848656624169762291870, 
                        0.3420194935223716364807297, 0.3535028151129699895377902, 
                        0.3649331078236540185334649, 0.3763086569987163902830557, 
                        0.3876277561945155836379846, 0.3988887074354591277134632, 
                        0.4100898214687165500064336, 0.4212294180176238249768124, 
                        0.4323058260337413099534411, 0.4433173839475273572169258, 
                        0.4542624399175899987744552, 0.4651393520784793136455705, 
                        0.4759464887869833063907375, 0.4866822288668903501036214, 
                        0.4973449618521814771195124, 0.5079330882286160362319249, 
                        0.5184450196736744762216617, 0.5288791792948222619514764, 
                        0.5392340018660591811279362, 0.5495079340627185570424269, 
                        0.5596994346944811451369074, 0.5698069749365687590576675, 
                        0.5798290385590829449218317, 0.5897641221544543007857861, 
                        0.5996107353629683217303882, 0.6093674010963339395223108, 
                        0.6190326557592612194309676, 0.6286050494690149754322099, 
                        0.6380831462729113686686886, 0.6474655243637248626170162, 
                        0.6567507762929732218875002, 0.6659375091820485599064084, 
                        0.6750243449311627638559187, 0.6840099204260759531248771, 
                        0.6928928877425769601053416, 0.7016719143486851594060835, 
                        0.7103456833045433133945663, 0.7189128934599714483726399, 
                        0.7273722596496521265868944, 0.7357225128859178346203729, 
                        0.7439624005491115684556831, 0.7520906865754920595875297, 
                        0.7601061516426554549419068, 0.7680075933524456359758906, 
                        0.7757938264113257391320526, 0.7834636828081838207506702, 
                        0.7910160119895459945467075, 0.7984496810321707587825429, 
                        0.8057635748129986232573891, 0.8129565961764315431364104, 
                        0.8200276660989170674034781, 0.8269757238508125142890929, 
                        0.8337997271555048943484439, 0.8404986523457627138950680, 
                        0.8470714945172962071870724, 0.8535172676795029650730355, 
                        0.8598350049033763506961731, 0.8660237584665545192975154, 
                        0.8720825999954882891300459, 0.8780106206047065439864349, 
                        0.8838069310331582848598262, 0.8894706617776108888286766, 
                        0.8950009632230845774412228, 0.9003970057703035447716200, 
                        0.9056579799601446470826819, 0.9107830965950650118909072, 
                        0.9157715868574903845266696, 0.9206227024251464955050471, 
                        0.9253357155833162028727303, 0.9299099193340056411802456, 
                        0.9343446275020030942924765, 0.9386391748378148049819261, 
                        0.9427929171174624431830761, 0.9468052312391274813720517, 
                        0.9506755153166282763638521, 0.9544031887697162417644479, 
                        0.9579876924111781293657904, 0.9614284885307321440064075, 
                        0.9647250609757064309326123, 0.9678769152284894549090038, 
                        0.9708835784807430293209233, 0.9737445997043704052660786, 
                        0.9764595497192341556210107, 0.9790280212576220388242380, 
                        0.9814496290254644057693031, 0.9837240097603154961666861, 
                        0.9858508222861259564792451, 0.9878297475648606089164877, 
                        0.9896604887450652183192437, 0.9913427712075830869221885, 
                        0.9928763426088221171435338, 0.9942609729224096649628775, 
                        0.9954964544810963565926471, 0.9965826020233815404305044, 
                        0.9975192527567208275634088, 0.9983062664730064440555005, 
                        0.9989435258434088565550263, 0.9994309374662614082408542, 
                        0.9997684374092631861048786, 0.9999560500189922307348012};
   static double w256[]  =  {0.0122476716402897559040703, 0.0122458343697479201424639, 
                        0.0122421601042728007697281, 0.0122366493950401581092426, 
                        0.0122293030687102789041463, 0.0122201222273039691917087, 
                        0.0122091082480372404075141, 0.0121962627831147135181810, 
                        0.0121815877594817721740476, 0.0121650853785355020613073, 
                        0.0121467581157944598155598, 0.0121266087205273210347185, 
                        0.0121046402153404630977578, 0.0120808558957245446559752, 
                        0.0120552593295601498143471, 0.0120278543565825711612675, 
                        0.0119986450878058119345367, 0.0119676359049058937290073, 
                        0.0119348314595635622558732, 0.0119002366727664897542872, 
                        0.0118638567340710787319046, 0.0118256971008239777711607, 
                        0.0117857634973434261816901, 0.0117440619140605503053767, 
                        0.0117005986066207402881898, 0.0116553800949452421212989, 
                        0.0116084131622531057220847, 0.0115597048540436357726687, 
                        0.0115092624770394979585864, 0.0114570935980906391523344, 
                        0.0114032060430391859648471, 0.0113476078955454919416257, 
                        0.0112903074958755095083676, 0.0112313134396496685726568, 
                        0.0111706345765534494627109, 0.0111082800090098436304608, 
                        0.0110442590908139012635176, 0.0109785814257295706379882, 
                        0.0109112568660490397007968, 0.0108422955111147959952935, 
                        0.0107717077058046266366536, 0.0106995040389797856030482, 
                        0.0106256953418965611339617, 0.0105502926865814815175336, 
                        0.0104733073841704030035696, 0.0103947509832117289971017, 
                        0.0103146352679340150682607, 0.0102329722564782196569549, 
                        0.0101497741990948656546341, 0.0100650535763063833094610, 
                        0.0099788230970349101247339, 0.0098910956966958286026307, 
                        0.0098018845352573278254988, 0.0097112029952662799642497, 
                        0.0096190646798407278571622, 0.0095254834106292848118297, 
                        0.0094304732257377527473528, 0.0093340483776232697124660, 
                        0.0092362233309563026873787, 0.0091370127604508064020005, 
                        0.0090364315486628736802278, 0.0089344947837582075484084, 
                        0.0088312177572487500253183, 0.0087266159616988071403366, 
                        0.0086207050884010143053688, 0.0085135010250224906938384, 
                        0.0084050198532215357561803, 0.0082952778462352254251714, 
                        0.0081842914664382699356198, 0.0080720773628734995009470, 
                        0.0079586523687543483536132, 0.0078440334989397118668103, 
                        0.0077282379473815556311102, 0.0076112830845456594616187, 
                        0.0074931864548058833585998, 0.0073739657738123464375724, 
                        0.0072536389258339137838291, 0.0071322239610753900716724, 
                        0.0070097390929698226212344, 0.0068862026954463203467133, 
                        0.0067616333001737987809279, 0.0066360495937810650445900, 
                        0.0065094704150536602678099, 0.0063819147521078805703752, 
                        0.0062534017395424012720636, 0.0061239506555679325423891, 
                        0.0059935809191153382211277, 0.0058623120869226530606616, 
                        0.0057301638506014371773844, 0.0055971560336829100775514, 
                        0.0054633085886443102775705, 0.0053286415939159303170811, 
                        0.0051931752508692809303288, 0.0050569298807868423875578, 
                        0.0049199259218138656695588, 0.0047821839258926913729317, 
                        0.0046437245556800603139791, 0.0045045685814478970686418, 
                        0.0043647368779680566815684, 0.0042242504213815362723565, 
                        0.0040831302860526684085998, 0.0039413976414088336277290, 
                        0.0037990737487662579981170, 0.0036561799581425021693892, 
                        0.0035127377050563073309711, 0.0033687685073155510120191, 
                        0.0032242939617941981570107, 0.0030793357411993375832054, 
                        0.0029339155908297166460123, 0.0027880553253277068805748, 
                        0.0026417768254274905641208, 0.0024951020347037068508395, 
                        0.0023480529563273120170065, 0.0022006516498399104996849, 
                        0.0020529202279661431745488, 0.0019048808534997184044191, 
                        0.0017565557363307299936069, 0.0016079671307493272424499, 
                        0.0014591373333107332010884, 0.0013100886819025044578317, 
                        0.0011608435575677247239706, 0.0010114243932084404526058, 
                        0.0008618537014200890378141, 0.0007121541634733206669090, 
                        0.0005623489540314098028152, 0.0004124632544261763284322, 
                        0.0002625349442964459062875, 0.0001127890178222721755125};

   static double x512[]  =  {0.0030649621851593961529232, 0.0091947713864329108047442, 
                        0.0153242350848981855249677, 0.0214531229597748745137841, 
                        0.0275812047119197840615246, 0.0337082500724805951232271, 
                        0.0398340288115484476830396, 0.0459583107468090617788760, 
                        0.0520808657521920701127271, 0.0582014637665182372392330, 
                        0.0643198748021442404045319, 0.0704358689536046871990309, 
                        0.0765492164062510452915674, 0.0826596874448871596284651, 
                        0.0887670524624010326092165, 0.0948710819683925428909483, 
                        0.1009715465977967786264323, 0.1070682171195026611052004, 
                        0.1131608644449665349442888, 0.1192492596368204011642726, 
                        0.1253331739174744696875513, 0.1314123786777137080093018, 
                        0.1374866454852880630171099, 0.1435557460934960331730353, 
                        0.1496194524497612685217272, 0.1556775367042018762501969, 
                        0.1617297712181921097989489, 0.1677759285729161198103670, 
                        0.1738157815779134454985394, 0.1798491032796159253350647, 
                        0.1858756669698757062678115, 0.1918952461944840310240859, 
                        0.1979076147616804833961808, 0.2039125467506523717658375, 
                        0.2099098165200239314947094, 0.2158991987163350271904893, 
                        0.2218804682825090362529109, 0.2278534004663095955103621, 
                        0.2338177708287858931763260, 0.2397733552527061887852891, 
                        0.2457199299509792442100997, 0.2516572714750633493170137, 
                        0.2575851567233626262808095, 0.2635033629496102970603704, 
                        0.2694116677712385990250046, 0.2753098491777350342234845, 
                        0.2811976855389846383013106, 0.2870749556135979555970354, 
                        0.2929414385572244074855835, 0.2987969139308507415853707, 
                        0.3046411617090842500066247, 0.3104739622884204453906292, 
                        0.3162950964954948840736281, 0.3221043455953188263048133, 
                        0.3279014912994984240551598, 0.3336863157744371275728377, 
                        0.3394586016495210024715049, 0.3452181320252866497799379, 
                        0.3509646904815714220351686, 0.3566980610856456291665404, 
                        0.3624180284003264285948478, 0.3681243774920730946589582, 
                        0.3738168939390633631820054, 0.3794953638392505477003659, 
                        0.3851595738184011246011504, 0.3908093110381124851478484, 
                        0.3964443632038105531190080, 0.4020645185727269675414064, 
                        0.4076695659618555307670286, 0.4132592947558876229222955, 
                        0.4188334949151262845483445, 0.4243919569833786700527309, 
                        0.4299344720958265754056529, 0.4354608319868747443376920, 
                        0.4409708289979766581310498, 0.4464642560854375149423431, 
                        0.4519409068281941054521446, 0.4574005754355712925046003, 
                        0.4628430567550148032795831, 0.4682681462798000434299255, 
                        0.4736756401567166435172692, 0.4790653351937284489919577, 
                        0.4844370288676086658851277, 0.4897905193315498753147078, 
                        0.4951256054227486308513615, 0.5004420866699643537454866, 
                        0.5057397633010522419821678, 0.5110184362504699101074361, 
                        0.5162779071667574777562819, 0.5215179784199908258105606, 
                        0.5267384531092077401231844, 0.5319391350698066637637706, 
                        0.5371198288809177797701793, 0.5422803398727461474300859, 
                        0.5474204741338866161668468, 0.5525400385186102421644070, 
                        0.5576388406541219339368088, 0.5627166889477890541289656, 
                        0.5677733925943407059267120, 0.5728087615830374335557009, 
                        0.5778226067048110674604360, 0.5828147395593744458765762, 
                        0.5877849725623007456415722, 0.5927331189520721562306608, 
                        0.5976589927970976321572046, 0.6025624090026994600382737, 
                        0.6074431833180683777981926, 0.6123011323431869846644595, 
                        0.6171360735357211818019505, 0.6219478252178793846326095, 
                        0.6267362065832392490988318, 0.6315010377035416553494506, 
                        0.6362421395354516935575740, 0.6409593339272863978194482, 
                        0.6456524436257089753330001, 0.6503212922823892793136899, 
                        0.6549657044606302753737317, 0.6595855056419602523685720, 
                        0.6641805222326905300017078, 0.6687505815704384167754210, 
                        0.6732955119306151731807642, 0.6778151425328787363350998, 
                        0.6823093035475509635996236, 0.6867778261019991540425409, 
                        0.6912205422869816079558685, 0.6956372851629569859851427, 
                        0.7000278887663572307915895, 0.7043921881158238155354902, 
                        0.7087300192184070848475163, 0.7130412190757284553416507, 
                        0.7173256256901052441189100, 0.7215830780706378951153816, 
                        0.7258134162392593745610389, 0.7300164812367465082373380, 
                        0.7341921151286930346516885, 0.7383401610114441496854630, 
                        0.7424604630179923197192207, 0.7465528663238341416942072, 
                        0.7506172171527880300329109, 0.7546533627827725118134392, 
                        0.7586611515515449130726824, 0.7626404328624002206015913, 
                        0.7665910571898299050923647, 0.7705128760851404930018538, 
                        0.7744057421820316760079998, 0.7782695092021337484565606, 
                        0.7821040319605041647237048, 0.7859091663710830099561901, 
                        0.7896847694521071791947507, 0.7934306993314830614379285, 
                        0.7971468152521175267628422, 0.8008329775772070161862372, 
                        0.8044890477954845355235412, 0.8081148885264243560855026, 
                        0.8117103635254042266412553, 0.8152753376888249026732770, 
                        0.8188096770591868005536242, 0.8223132488301235858819787, 
                        0.8257859213513925068443721, 0.8292275641338212850768968, 
                        0.8326380478542113781512150, 0.8360172443601974294381733, 
                        0.8393650266750627227522641, 0.8426812690025104608329811, 
                        0.8459658467313906883792422, 0.8492186364403826820199251, 
                        0.8524395159026326312771384, 0.8556283640903464362590494, 
                        0.8587850611793374495058711, 0.8619094885535289911058997, 
                        0.8650015288094114678982387, 0.8680610657604539292849800, 
                        0.8710879844414698938880857, 0.8740821711129372830049576, 
                        0.8770435132652722985416439, 0.8799718996230570848337538, 
                        0.8828672201492210155023745, 0.8857293660491754482355527, 
                        0.8885582297749017921351663, 0.8913537050289927340242104, 
                        0.8941156867686464718706125, 0.8968440712096138052506156, 
                        0.8995387558300979345474886, 0.9021996393746068223597927, 
                        0.9048266218577579723776075, 0.9074196045680354827749729, 
                        0.9099784900714992329623006, 0.9125031822154460643436214, 
                        0.9149935861320228175302595, 0.9174496082417910902748409, 
                        0.9198711562572435822074657, 0.9222581391862718942794141, 
                        0.9246104673355856526489486, 0.9269280523140828285786768, 
                        0.9292108070361711277546193, 0.9314586457250403242837002, 
                        0.9336714839158854164789745, 0.9358492384590804834007204, 
                        0.9379918275233031229867813, 0.9400991705986093544775539, 
                        0.9421711884994588697201555, 0.9442078033676905198230562, 
                        0.9462089386754479255274304, 0.9481745192280551015654245, 
                        0.9501044711668419871894147, 0.9519987219719197769813274, 
                        0.9538572004649059479887372, 0.9556798368115988811866200, 
                        0.9574665625246019772327448, 0.9592173104658971684737507, 
                        0.9609320148493677311718534, 0.9626106112432703039637754, 
                        0.9642530365726560206402068, 0.9658592291217406674540047, 
                        0.9674291285362237773389233, 0.9689626758255565756615864, 
                        0.9704598133651586944555050, 0.9719204848985835745206522, 
                        0.9733446355396324773464471, 0.9747322117744170315712560, 
                        0.9760831614633702416830300, 0.9773974338432058899681861, 
                        0.9786749795288262664309572, 0.9799157505151781656726285, 
                        0.9811197001790570947322311, 0.9822867832808596419166429, 
                        0.9834169559662839640681455, 0.9845101757679783590716126, 
                        0.9855664016071379024692622, 0.9865855937950491429603684, 
                        0.9875677140345828729848910, 0.9885127254216350200148487, 
                        0.9894205924465157453777048, 0.9902912809952868962106899, 
                        0.9911247583510480415528399, 0.9919209931951714500244370, 
                        0.9926799556084865573546763, 0.9934016170724147657859271, 
                        0.9940859504700558793702825, 0.9947329300872282225027936, 
                        0.9953425316134657151476031, 0.9959147321429772566997088, 
                        0.9964495101755774022837600, 0.9969468456176038804367370, 
                        0.9974067197828498321611183, 0.9978291153935628466036470, 
                        0.9982140165816127953876923, 0.9985614088900397275573677, 
                        0.9988712792754494246541769, 0.9991436161123782382453400, 
                        0.9993784092025992514480161, 0.9995756497983108555936109, 
                        0.9997353306710426625827368, 0.9998574463699794385446275, 
                        0.9999419946068456536361287, 0.9999889909843818679872841};
   static double w512[] = {0.0061299051754057857591564, 0.0061296748380364986664278, 
                        0.0061292141719530834395471, 0.0061285231944655327693402, 
                        0.0061276019315380226384508, 0.0061264504177879366912426, 
                        0.0061250686964845654506976, 0.0061234568195474804311878, 
                        0.0061216148475445832082156, 0.0061195428496898295184288, 
                        0.0061172409038406284754329, 0.0061147090964949169991245, 
                        0.0061119475227879095684795, 0.0061089562864885234199252, 
                        0.0061057354999954793256260, 0.0061022852843330780981965, 
                        0.0060986057691466529805468, 0.0060946970926976980917399, 
                        0.0060905594018586731119147, 0.0060861928521074844014940, 
                        0.0060815976075216427620556, 0.0060767738407720980583934, 
                        0.0060717217331167509334394, 0.0060664414743936418598512, 
                        0.0060609332630138177841916, 0.0060551973059538766317450, 
                        0.0060492338187481899521175, 0.0060430430254808039978627, 
                        0.0060366251587770195404584, 0.0060299804597946507400317, 
                        0.0060231091782149633972884, 0.0060160115722332929281516, 
                        0.0060086879085493424136484, 0.0060011384623571610896056, 
                        0.0059933635173348036527221, 0.0059853633656336707715812, 
                        0.0059771383078675312031423, 0.0059686886531012259272183, 
                        0.0059600147188390547233923, 0.0059511168310128456267588, 
                        0.0059419953239697077107922, 0.0059326505404594676575446, 
                        0.0059230828316217905872556, 0.0059132925569729856313229, 
                        0.0059032800843924967444267, 0.0058930457901090792634301, 
                        0.0058825900586866627324847, 0.0058719132830099005255609, 
                        0.0058610158642694068093892, 0.0058498982119466814015496, 
                        0.0058385607437987230901727, 0.0058270038858423319934219, 
                        0.0058152280723381015486124, 0.0058032337457741007324836, 
                        0.0057910213568492471257818, 0.0057785913644563714469284, 
                        0.0057659442356649741911390, 0.0057530804457036750229319, 
                        0.0057400004779423555815070, 0.0057267048238739963699973, 
                        0.0057131939830962084110906, 0.0056994684632924603629882, 
                        0.0056855287802130018011102, 0.0056713754576554833823756, 
                        0.0056570090274452746202723, 0.0056424300294154800102991, 
                        0.0056276390113866542566918, 0.0056126365291462173626557, 
                        0.0055974231464275703576030, 0.0055819994348889124461425, 
                        0.0055663659740917603747899, 0.0055505233514791708235538, 
                        0.0055344721623536666407146, 0.0055182130098548677502395, 
                        0.0055017465049368275723757, 0.0054850732663450758090285, 
                        0.0054681939205933684565648, 0.0054511091019401459196852, 
                        0.0054338194523647001109732, 0.0054163256215430514316688, 
                        0.0053986282668235365401123, 0.0053807280532021078251738, 
                        0.0053626256532973455128155, 0.0053443217473251833447318, 
                        0.0053258170230733487787774, 0.0053071121758755186716175, 
                        0.0052882079085851914147269, 0.0052691049315492765055207, 
                        0.0052498039625814025460136, 0.0052303057269349446719890, 
                        0.0052106109572757724261988, 0.0051907203936547190996206, 
                        0.0051706347834797735752665, 0.0051503548814879957194620, 
                        0.0051298814497171563759039, 0.0051092152574771030281542, 
                        0.0050883570813208522065339, 0.0050673077050154097256505, 
                        0.0050460679195123198490183, 0.0050246385229179444874178, 
                        0.0050030203204634735477834, 0.0049812141244746675595135, 
                        0.0049592207543413337151533, 0.0049370410364865364724225, 
                        0.0049146758043355438745290, 0.0048921258982845107556462, 
                        0.0048693921656689000083132, 0.0048464754607316430993636, 
                        0.0048233766445910410307843, 0.0048000965852084069516609, 
                        0.0047766361573554516370718, 0.0047529962425814130594576, 
                        0.0047291777291799312876071, 0.0047051815121556699579709, 
                        0.0046810084931906855725376, 0.0046566595806105458869828, 
                        0.0046321356893501986622283, 0.0046074377409195920619320, 
                        0.0045825666633690479877601, 0.0045575233912543896535753, 
                        0.0045323088656018247089130, 0.0045069240338725852313010, 
                        0.0044813698499273259161146, 0.0044556472739902818017469, 
                        0.0044297572726131868769073, 0.0044037008186389549258496, 
                        0.0043774788911651239762643, 0.0043510924755070657234522, 
                        0.0043245425631609613132305, 0.0042978301517665448748000, 
                        0.0042709562450696162035304, 0.0042439218528843240022977, 
                        0.0042167279910552210986262, 0.0041893756814190930634598, 
                        0.0041618659517665616659011, 0.0041341998358034646067195, 
                        0.0041063783731120129818357, 0.0040784026091117279353449, 
                        0.0040502735950201579699371, 0.0040219923878133783908191, 
                        0.0039935600501862743674273, 0.0039649776505126091053562, 
                        0.0039362462628048786290012, 0.0039073669666739546834366, 
                        0.0038783408472885172720108, 0.0038491689953342783540510, 
                        0.0038198525069729982349166, 0.0037903924838012961884344, 
                        0.0037607900328092568594835, 0.0037310462663388340021755, 
                        0.0037011623020420531166926, 0.0036711392628390145554094, 
                        0.0036409782768756986764252, 0.0036106804774815746300758, 
                        0.0035802470031270143713799, 0.0035496789973805134987000, 
                        0.0035189776088657205261605, 0.0034881439912182762045767, 
                        0.0034571793030424645127888, 0.0034260847078676769483860, 
                        0.0033948613741046917538288, 0.0033635104750017697209450, 
                        0.0033320331886005682236783, 0.0033004306976918751358177, 
                        0.0032687041897711642972145, 0.0032368548569939741987234, 
                        0.0032048838961311115627642, 0.0031727925085236815030060, 
                        0.0031405819000379459532169, 0.0031082532810200120618074, 
                        0.0030758078662503522550163, 0.0030432468748981576780527, 
                        0.0030105715304755267298129, 0.0029777830607914904130339, 
                        0.0029448826979058762279357, 0.0029118716780830123435331, 
                        0.0028787512417452737868732, 0.0028455226334264723964728, 
                        0.0028121871017250922921949, 0.0027787458992573726197173, 
                        0.0027452002826102393336092, 0.0027115515122940877888456, 
                        0.0026778008526954179163600, 0.0026439495720293237639656, 
                        0.0026099989422918391896635, 0.0025759502392121415000167, 
                        0.0025418047422046148318992, 0.0025075637343207750815413, 
                        0.0024732285022010581903898, 0.0024388003360264736029032, 
                        0.0024042805294701247170072, 0.0023696703796485981535706, 
                        0.0023349711870732236769383, 0.0023001842556012066042973, 
                        0.0022653108923866345474810, 0.0022303524078313603367724, 
                        0.0021953101155357629823745, 0.0021601853322493885355395, 
                        0.0021249793778214727179358, 0.0020896935751513471947536, 
                        0.0020543292501387313744068, 0.0020188877316339116255770, 
                        0.0019833703513878098109153, 0.0019477784440019430461334, 
                        0.0019121133468782766036998, 0.0018763764001689718921795, 
                        0.0018405689467260314557679, 0.0018046923320508429542037, 
                        0.0017687479042436241015783, 0.0017327370139527705642995, 
                        0.0016966610143241088445575, 0.0016605212609500562072903, 
                        0.0016243191118186897474239, 0.0015880559272627267421479, 
                        0.0015517330699084184928942, 0.0015153519046243599371387, 
                        0.0014789137984702174059640, 0.0014424201206453770259886, 
                        0.0014058722424375164225552, 0.0013692715371711025869345, 
                        0.0013326193801558190401403, 0.0012959171486349257824991, 
                        0.0012591662217335559930561, 0.0012223679804069540808915, 
                        0.0011855238073886605549070, 0.0011486350871386503607080, 
                        0.0011117032057914329649653, 0.0010747295511041247428251, 
                        0.0010377155124045074300544, 0.0010006624805390909706032, 
                        0.0009635718478212056798501, 0.0009264450079791582697455, 
                        0.0008892833561045005372012, 0.0008520882886004809402792, 
                        0.0008148612031307819965602, 0.0007776034985686972438014, 
                        0.0007403165749469818962867, 0.0007030018334087411433900, 
                        0.0006656606761599343409382, 0.0006282945064244358390880, 
                        0.0005909047284032230162400, 0.0005534927472403894647847, 
                        0.0005160599690007674370993, 0.0004786078006679509066920, 
                        0.0004411376501795405636493, 0.0004036509265333198797447, 
                        0.0003661490400356268530141, 0.0003286334028523334162522, 
                        0.0002911054302514885125319, 0.0002535665435705865135866, 
                        0.0002160181779769908583388, 0.0001784618055459532946077, 
                        0.0001408990173881984930124, 0.0001033319034969132362968, 
                        0.0000657657316592401958310, 0.0000282526373739346920387};

   static double x1024[] = {0.0015332313560626384065387, 0.0045996796509132604743248, 
                        0.0076660846940754867627839, 0.0107324176515422803327458, 
                        0.0137986496899844401539048, 0.0168647519770217265449962, 
                        0.0199306956814939776907024, 0.0229964519737322146859283, 
                        0.0260619920258297325581921, 0.0291272870119131747190088, 
                        0.0321923081084135882953009, 0.0352570264943374577920498, 
                        0.0383214133515377145376052, 0.0413854398649847193632977, 
                        0.0444490772230372159692514, 0.0475122966177132524285687, 
                        0.0505750692449610682823599, 0.0536373663049299446784129, 
                        0.0566991590022410150066456, 0.0597604185462580334848567, 
                        0.0628211161513580991486838, 0.0658812230372023327000985, 
                        0.0689407104290065036692117, 0.0719995495578116053446277, 
                        0.0750577116607543749280791, 0.0781151679813377563695878, 
                        0.0811718897697013033399379, 0.0842278482828915197978074, 
                        0.0872830147851321356094940, 0.0903373605480943146797811, 
                        0.0933908568511667930531222, 0.0964434749817259444449839, 
                        0.0994951862354057706638682, 0.1025459619163678143852404, 
                        0.1055957733375709917393206, 0.1086445918210413421754502, 
                        0.1116923886981416930665228, 0.1147391353098412365177689, 
                        0.1177848030069850158450139, 0.1208293631505633191883714, 
                        0.1238727871119809777282145, 0.1269150462733265659711591, 
                        0.1299561120276415015747167, 0.1329959557791890421802183, 
                        0.1360345489437231767245806, 0.1390718629487574087024745, 
                        0.1421078692338334288514767, 0.1451425392507896747338214, 
                        0.1481758444640297746894331, 0.1512077563507908736360111, 
                        0.1542382464014118381930443, 0.1572672861196013386077717, 
                        0.1602948470227058049622614, 0.1633209006419772551419632, 
                        0.1663454185228409920472972, 0.1693683722251631675310675, 
                        0.1723897333235182105457458, 0.1754094734074561169859457, 
                        0.1784275640817695987127083, 0.1814439769667610892475458, 
                        0.1844586836985096036255346, 0.1874716559291374498981239, 
                        0.1904828653270767897777182, 0.1934922835773360459175133, 
                        0.1964998823817661533215037, 0.1995056334593266523810493, 
                        0.2025095085463516210358758, 0.2055114793968154435588961, 
                        0.2085115177825984134657778, 0.2115095954937521680517391, 
                        0.2145056843387649520596422, 0.2174997561448267079850562, 
                        0.2204917827580939905255947, 0.2234817360439547026834844, 
                        0.2264695878872926510320010, 0.2294553101927519176581055, 
                        0.2324388748850010462953415, 0.2354202539089970401627982, 
                        0.2383994192302491690277166, 0.2413763428350825830111093, 
                        0.2443509967309017306575811, 0.2473233529464535787923793, 
                        0.2502933835320906316905658, 0.2532610605600337470850902, 
                        0.2562263561246347465424530, 0.2591892423426388177365829, 
                        0.2621496913534467061535080, 0.2651076753193766937613805, 
                        0.2680631664259263621824189, 0.2710161368820341379053566, 
                        0.2739665589203406170790369, 0.2769144047974496674298651, 
                        0.2798596467941893048479266, 0.2828022572158723421886958, 
                        0.2857422083925568078394062, 0.2886794726793061316013119, 
                        0.2916140224564490954412652, 0.2945458301298395466682397, 
                        0.2974748681311158710926665, 0.3004011089179602237287060, 
                        0.3033245249743575146018584, 0.3062450888108541472266190, 
                        0.3091627729648165073212094, 0.3120775500006891993287636, 
                        0.3149893925102530283167230, 0.3178982731128827248285835, 
                        0.3208041644558044102645582, 0.3237070392143528003701590, 
                        0.3266068700922281444141618, 0.3295036298217528976399056, 
                        0.3323972911641281245763845, 0.3352878269096896307981228, 
                        0.3381752098781638207253743, 0.3410594129189232790587667, 
                        0.3439404089112420734451077, 0.3468181707645507759736923, 
                        0.3496926714186912011050938, 0.3525638838441708576370887, 
                        0.3554317810424171123150528, 0.3582963360460310626968790, 
                        0.3611575219190411168852009, 0.3640153117571562777424605, 
                        0.3668696786880191292071420, 0.3697205958714585223322883, 
                        0.3725680364997419586702471, 0.3754119737978276686304337, 
                        0.3782523810236163824397703, 0.3810892314682027913383487, 
                        0.3839224984561266966457784, 0.3867521553456238443366159, 
                        0.3895781755288764427662286, 0.3924005324322633611914264, 
                        0.3952191995166100067331951, 0.3980341502774378774318886, 
                        0.4008453582452137890482864, 0.4036527969855987732669841, 
                        0.4064564400996966449616823, 0.4092562612243022361850445, 
                        0.4120522340321492945489319, 0.4148443322321580436639788, 
                        0.4176325295696824033106488, 0.4204167998267568670171117, 
                        0.4231971168223430347225035, 0.4259734544125757982073747, 
                        0.4287457864910091769763965, 0.4315140869888618022816824, 
                        0.4342783298752620469783905, 0.4370384891574927989076034, 
                        0.4397945388812358755048319, 0.4425464531308160773358662, 
                        0.4452942060294448782650898, 0.4480377717394637499647905, 
                        0.4507771244625871184774399, 0.4535122384401449505463744, 
                        0.4562430879533249674337895, 0.4589696473234144839484647, 
                        0.4616918909120418704091584, 0.4644097931214176352731591, 
                        0.4671233283945751261630457, 0.4698324712156108470282980, 
                        0.4725371961099243891820077, 0.4752374776444579739565725, 
                        0.4779332904279356047259052, 0.4806246091111018260453658, 
                        0.4833114083869600876643171, 0.4859936629910107111699206, 
                        0.4886713477014884570245255, 0.4913444373395996897627612, 
                        0.4940129067697591391182235, 0.4966767308998262548534419, 
                        0.4993358846813411530706387, 0.5019903431097601517846292, 
                        0.5046400812246908935430768, 0.5072850741101270528831987, 
                        0.5099252968946826264179220, 0.5125607247518258033484145, 
                        0.5151913329001124142038603, 0.5178170966034189556133159, 
                        0.5204379911711751889184691, 0.5230539919585963104401304, 
                        0.5256650743669146912153147, 0.5282712138436111840258187, 
                        0.5308723858826459955432696, 0.5334685660246891214197081, 
                        0.5360597298573503421568799, 0.5386458530154087775915395, 
                        0.5412269111810419978382210, 0.5438028800840546885350993, 
                        0.5463737355021068682427603, 0.5489394532609416558499039, 
                        0.5515000092346125858442412, 0.5540553793457104693110943, 
                        0.5566055395655897985264809, 0.5591504659145946930157566, 
                        0.5616901344622843849532002, 0.5642245213276582417822586, 
                        0.5667536026793803239405196, 0.5692773547360034755778519, 
                        0.5717957537661929461605442, 0.5743087760889495408586850, 
                        0.5768163980738322976184566, 0.5793185961411806888254667, 
                        0.5818153467623363454697137, 0.5843066264598643017272666, 
                        0.5867924118077737578782574, 0.5892726794317383594853053, 
                        0.5917474060093159907610475, 0.5942165682701680800580147, 
                        0.5966801429962784154186793, 0.5991381070221714681281111, 
                        0.6015904372351302222163013, 0.6040371105754135078618616, 
                        0.6064781040364728366534687, 0.6089133946651687366701116, 
                        0.6113429595619865853458987, 0.6137667758812519380899084, 
                        0.6161848208313453506363029, 0.6185970716749166931046915, 
                        0.6210035057290989537555048, 0.6234041003657215304299416, 
                        0.6257988330115230076688675, 0.6281876811483634175098794, 
                        0.6305706223134359819666081, 0.6329476340994783351992008, 
                        0.6353186941549832233898213, 0.6376837801844086803419153, 
                        0.6400428699483876768269192, 0.6423959412639372417070377, 
                        0.6447429720046670528676835, 0.6470839401009874959981582, 
                        0.6494188235403171892641570, 0.6517476003672899719207013, 
                        0.6540702486839613549191454, 0.6563867466500144315669620, 
                        0.6586970724829652463040876, 0.6610012044583676196647058, 
                        0.6632991209100174274984589, 0.6655908002301563325302097, 
                        0.6678762208696749663426270, 0.6701553613383155598710345, 
                        0.6724282002048740205051479, 0.6746947160974014538975312, 
                        0.6769548877034051285838219, 0.6792086937700488815250166, 
                        0.6814561131043529626873631, 0.6836971245733933167806834, 
                        0.6859317071045003002812397, 0.6881598396854568318705713, 
                        0.6903815013646959744270519, 0.6925966712514979467122689, 
                        0.6948053285161865628996815, 0.6970074523903250980984011, 
                        0.6992030221669115780303307, 0.7013920172005734910243170, 
                        0.7035744169077619204963997, 0.7057502007669450960906928, 
                        0.7079193483188013616608982, 0.7100818391664115582779368, 
                        0.7122376529754508204546805, 0.7143867694743797837842896, 
                        0.7165291684546352021941915, 0.7186648297708199730232898, 
                        0.7207937333408925681355609, 0.7229158591463558692887801, 
                        0.7250311872324454059827217, 0.7271396977083169940167956, 
                        0.7292413707472337729927181, 0.7313361865867526410034676, 
                        0.7334241255289100847554419, 0.7355051679404074033764222, 
                        0.7375792942527953241676460, 0.7396464849626580085640129, 
                        0.7417067206317964465721772, 0.7437599818874112379620360, 
                        0.7458062494222847584928838, 0.7478455039949627094612890, 
                        0.7498777264299350488635483, 0.7519028976178163024713854, 
                        0.7539209985155252531253957, 0.7559320101464640065565832, 
                        0.7579359136006964320521972, 0.7599326900351259762879594, 
                        0.7619223206736728486546595, 0.7639047868074505764130149, 
                        0.7658800697949419280166093, 0.7678481510621742029486694, 
                        0.7698090121028938864243967, 0.7717626344787406673165402, 
                        0.7737089998194208176678866, 0.7756480898228799321603470, 
                        0.7775798862554750259163361, 0.7795043709521459890141759, 
                        0.7814215258165863961053031, 0.7833313328214136695271245, 
                        0.7852337740083385943114429, 0.7871288314883341834944720, 
                        0.7890164874418038921405657, 0.7908967241187491784979139, 
                        0.7927695238389364107105941, 0.7946348689920631175175217, 
                        0.7964927420379235813750136, 0.7983431255065737724458586, 
                        0.8001860019984956219039900, 0.8020213541847606330100649, 
                        0.8038491648071928284194859, 0.8056694166785310321906380, 
                        0.8074820926825904849673728, 0.8092871757744237908160400, 
                        0.8110846489804811942036542, 0.8128744953987701856100790, 
                        0.8146566981990144342734272, 0.8164312406228120465742028, 
                        0.8181981059837931485700490, 0.8199572776677767911993239, 
                        0.8217087391329271766780945, 0.8234524739099092046215225, 
                        0.8251884656020433364270094, 0.8269166978854597764628854, 
                        0.8286371545092519686128428, 0.8303498192956294067327593, 
                        0.8320546761400697575830038, 0.8337517090114702948057846, 
                        0.8354409019522986425235764, 0.8371222390787428271411563, 
                        0.8387957045808606359402829, 0.8404612827227282810625704, 
                        0.8421189578425883674826439, 0.8437687143529971635802028, 
                        0.8454105367409711729261812, 0.8470444095681330059047621, 
                        0.8486703174708565497995875, 0.8502882451604114359791023, 
                        0.8518981774231068028225812, 0.8535000991204343530350070, 
                        0.8550939951892107040056078, 0.8566798506417190298715048, 
                        0.8582576505658499939545848, 0.8598273801252419702463831, 
                        0.8613890245594205526224495, 0.8629425691839373504743648, 
                        0.8644879993905080694542896, 0.8660253006471498760336444, 
                        0.8675544584983180445842596, 0.8690754585650418856970762, 
                        0.8705882865450599544602407, 0.8720929282129545374252050, 
                        0.8735893694202854169962281, 0.8750775960957229119854680, 
                        0.8765575942451801930826613, 0.8780293499519448719952049, 
                        0.8794928493768098630212838, 0.8809480787582035158255322, 
                        0.8823950244123190181935674, 0.8838336727332430675485994, 
                        0.8852640101930838100201983, 0.8866860233420980458621863, 
                        0.8880996988088177000235219, 0.8895050233001755566829532, 
                        0.8909019836016302565651375, 0.8922905665772905558628607, 
                        0.8936707591700388455969280, 0.8950425484016539302522575, 
                        0.8964059213729330645356690, 0.8977608652638132471078410, 
                        0.8991073673334917701488930, 0.9004454149205460236240486, 
                        0.9017749954430525531228459, 0.9030960963987053701523781, 
                        0.9044087053649335137720782, 0.9057128099990178624646022, 
                        0.9070083980382071951444166, 0.9082954572998335002127549, 
                        0.9095739756814265315746820, 0.9108439411608276105410847, 
                        0.9121053417963026725455006, 0.9133581657266545576127977, 
                        0.9146024011713345435238301, 0.9158380364305531206273175, 
                        0.9170650598853900072573273, 0.9182834599979034047218800, 
                        0.9194932253112384908353520, 0.9206943444497351509745089, 
                        0.9218868061190349456451742, 0.9230705991061873135537215, 
                        0.9242457122797550091847637, 0.9254121345899187738936182, 
                        0.9265698550685812395293315, 0.9277188628294700636112689, 
                        0.9288591470682402950895005, 0.9299906970625759697264543, 
                        0.9311135021722909341445515, 0.9322275518394288975917975, 
                        0.9333328355883627104845635, 0.9344293430258928687940732, 
                        0.9355170638413452433503852, 0.9365959878066680331449597, 
                        0.9376661047765279417201973, 0.9387274046884055757416456, 
                        0.9397798775626900648558921, 0.9408235135027729019444869, 
                        0.9418583026951410028915762, 0.9428842354094689849902736, 
                        0.9439013019987106631201510, 0.9449094928991897628355911, 
                        0.9459087986306898495121205, 0.9468992097965434727052183, 
                        0.9478807170837205248834878, 0.9488533112629158137054760, 
                        0.9498169831886358470168335, 0.9507717237992848297519245, 
                        0.9517175241172498719314184, 0.9526543752489854069548347, 
                        0.9535822683850968193944507, 0.9545011948004232815044368, 
                        0.9554111458541197976665483, 0.9563121129897384560011695, 
                        0.9572040877353088863799924, 0.9580870617034179240840996, 
                        0.9589610265912884783587268, 0.9598259741808576051234879, 
                        0.9606818963388537831043733, 0.9615287850168733926613630, 
                        0.9623666322514563965930439, 0.9631954301641612222071790, 
                        0.9640151709616388439537466, 0.9648258469357060659245549, 
                        0.9656274504634180035311332, 0.9664199740071397636802195, 
                        0.9672034101146173227737943, 0.9679777514190476018682591, 
                        0.9687429906391477383350273, 0.9694991205792235533724866, 
                        0.9702461341292372147270016, 0.9709840242648740939883669, 
                        0.9717127840476088178328839, 0.9724324066247705125950353, 
                        0.9731428852296072415565604, 0.9738442131813496343496072, 
                        0.9745363838852737078785517, 0.9752193908327628781730396, 
                        0.9758932276013691625928266, 0.9765578878548735718130775, 
                        0.9772133653433456910269459, 0.9778596539032024498104955, 
                        0.9784967474572660801033674, 0.9791246400148212617670490, 
                        0.9797433256716714551911835, 0.9803527986101944204270933, 
                        0.9809530530993969223366037, 0.9815440834949686212533729, 
                        0.9821258842393351486632952, 0.9826984498617103674201996, 
                        0.9832617749781478160230522, 0.9838158542915913364912672, 
                        0.9843606825919248853856025, 0.9848962547560215275335618, 
                        0.9854225657477916120303537, 0.9859396106182301300994116, 
                        0.9864473845054632544104222, 0.9869458826347940594679517, 
                        0.9874351003187474227003598, 0.9879150329571141058970610, 
                        0.9883856760369940166627304, 0.9888470251328386495802522, 
                        0.9892990759064927068006818, 0.9897418241072348978090276, 
                        0.9901752655718179181502248, 0.9905993962245076069415402, 
                        0.9910142120771212830473891, 0.9914197092290652598522332, 
                        0.9918158838673715386394944, 0.9922027322667336806727008, 
                        0.9925802507895418581838653, 0.9929484358859170846092543, 
                        0.9933072840937446245820355, 0.9936567920387065844051246, 
                        0.9939969564343136839997662, 0.9943277740819362116746914, 
                        0.9946492418708341635125525, 0.9949613567781865697596566, 
                        0.9952641158691200113800912, 0.9955575162967363309635588, 
                        0.9958415553021395435525955, 0.9961162302144619548145649, 
                        0.9963815384508894965215124, 0.9966374775166862927999356, 
                        0.9968840450052184754903082, 0.9971212385979772738362093, 
                        0.9973490560646014135491635, 0.9975674952628988745188845, 
                        0.9977765541388680773265018, 0.9979762307267185998745420, 
                        0.9981665231488915727109186, 0.9983474296160799746514418, 
                        0.9985189484272491654281575, 0.9986810779696581776171579, 
                        0.9988338167188825964389443, 0.9989771632388403756649803, 
                        0.9991111161818228462260355, 0.9992356742885348165163858, 
                        0.9993508363881507486653971, 0.9994566013984000492749057, 
                        0.9995529683257070064969677, 0.9996399362654382464576482, 
                        0.9997175044023747284307007, 0.9997856720116889628341744, 
                        0.9998444384611711916084367, 0.9998938032169419878731474, 
                        0.9999337658606177711221103, 0.9999643261538894550943330, 
                        0.9999854843850284447675914, 0.9999972450545584403516182};
   static double w1024[] = {0.0030664603092439082115513, 0.0030664314747171934849726, 
                        0.0030663738059349007324470, 0.0030662873034393008056861, 
                        0.0030661719680437936084028, 0.0030660278008329004477528, 
                        0.0030658548031622538363679, 0.0030656529766585847450783, 
                        0.0030654223232197073064431, 0.0030651628450145009692318, 
                        0.0030648745444828901040266, 0.0030645574243358210601357, 
                        0.0030642114875552366740338, 0.0030638367373940482295700, 
                        0.0030634331773761048702058, 0.0030630008112961604635720, 
                        0.0030625396432198379186545, 0.0030620496774835909559465, 
                        0.0030615309186946633309249, 0.0030609833717310455112352, 
                        0.0030604070417414288079918, 0.0030598019341451569616257, 
                        0.0030591680546321751827342, 0.0030585054091629766484119, 
                        0.0030578140039685464545661, 0.0030570938455503030247440, 
                        0.0030563449406800369760227, 0.0030555672963998474425352, 
                        0.0030547609200220758572342, 0.0030539258191292371925135, 
                        0.0030530620015739486603347, 0.0030521694754788558725307, 
                        0.0030512482492365564619779, 0.0030502983315095211653578, 
                        0.0030493197312300123682482, 0.0030483124576000001133114, 
                        0.0030472765200910755723677, 0.0030462119284443619831693, 
                        0.0030451186926704230517109, 0.0030439968230491688209395, 
                        0.0030428463301297590067471, 0.0030416672247305038021562, 
                        0.0030404595179387621506312, 0.0030392232211108374894710, 
                        0.0030379583458718709642643, 0.0030366649041157321154111, 
                        0.0030353429080049070377385, 0.0030339923699703840142628, 
                        0.0030326133027115366251721, 0.0030312057191960043331307, 
                        0.0030297696326595705460252, 0.0030283050566060381583022, 
                        0.0030268120048071025720655, 0.0030252904913022221991274, 
                        0.0030237405303984864452325, 0.0030221621366704811776946, 
                        0.0030205553249601516777118, 0.0030189201103766630786495, 
                        0.0030172565082962582916016, 0.0030155645343621134195681, 
                        0.0030138442044841906616068, 0.0030120955348390887083441, 
                        0.0030103185418698906302495, 0.0030085132422860092601062, 
                        0.0030066796530630300711306, 0.0030048177914425515522176, 
                        0.0030029276749320230818149, 0.0030010093213045803019478, 
                        0.0029990627485988779939449, 0.0029970879751189204574353, 
                        0.0029950850194338893942123, 0.0029930539003779692985814, 
                        0.0029909946370501703558363, 0.0029889072488141488505262, 
                        0.0029867917552980250862041, 0.0029846481763941988183689, 
                        0.0029824765322591622023349, 0.0029802768433133102577897, 
                        0.0029780491302407488518214, 0.0029757934139891002022209, 
                        0.0029735097157693059028890, 0.0029711980570554274731990, 
                        0.0029688584595844444331918, 0.0029664909453560499065010, 
                        0.0029640955366324437529314, 0.0029616722559381232326340, 
                        0.0029592211260596712038487, 0.0029567421700455418562030, 
                        0.0029542354112058439815854, 0.0029517008731121217846274, 
                        0.0029491385795971332348581, 0.0029465485547546259626151, 
                        0.0029439308229391107008170, 0.0029412854087656322747309, 
                        0.0029386123371095381418860, 0.0029359116331062444843108, 
                        0.0029331833221509998552933, 0.0029304274298986463828860, 
                        0.0029276439822633785324025, 0.0029248330054184994301727, 
                        0.0029219945257961747508486, 0.0029191285700871841705750, 
                        0.0029162351652406703883623, 0.0029133143384638857180205, 
                        0.0029103661172219362530391, 0.0029073905292375236068160, 
                        0.0029043876024906842306667, 0.0029013573652185263120627, 
                        0.0028982998459149642555740, 0.0028952150733304507490135, 
                        0.0028921030764717064173001, 0.0028889638846014470665859, 
                        0.0028857975272381085212091, 0.0028826040341555690560623, 
                        0.0028793834353828694269858, 0.0028761357612039305018167, 
                        0.0028728610421572684947521, 0.0028695593090357078067012, 
                        0.0028662305928860914743281, 0.0028628749250089892305081, 
                        0.0028594923369584031789413, 0.0028560828605414710856927, 
                        0.0028526465278181672904478, 0.0028491833711010012402964, 
                        0.0028456934229547136488796, 0.0028421767161959702837564, 
                        0.0028386332838930533848701, 0.0028350631593655507170153, 
                        0.0028314663761840422592303, 0.0028278429681697845340603, 
                        0.0028241929693943925796601, 0.0028205164141795195677262, 
                        0.0028168133370965340702726, 0.0028130837729661949782821, 
                        0.0028093277568583240752928, 0.0028055453240914762689974, 
                        0.0028017365102326074839556, 0.0027979013510967402185435, 
                        0.0027940398827466267692845, 0.0027901521414924101257281, 
                        0.0027862381638912825390663, 0.0027822979867471417676962, 
                        0.0027783316471102450029635, 0.0027743391822768604783394, 
                        0.0027703206297889167653083, 0.0027662760274336497592617, 
                        0.0027622054132432473587211, 0.0027581088254944918412282, 
                        0.0027539863027083999392661, 0.0027498378836498606195970, 
                        0.0027456636073272705694208, 0.0027414635129921673927833, 
                        0.0027372376401388605206822, 0.0027329860285040598383428, 
                        0.0027287087180665020331547, 0.0027244057490465746667821, 
                        0.0027200771619059379749851, 0.0027157229973471443987056, 
                        0.0027113432963132558499974, 0.0027069380999874587163979, 
                        0.0027025074497926766073634, 0.0026980513873911808464073, 
                        0.0026935699546841987126055, 0.0026890631938115194351518, 
                        0.0026845311471510979446691, 0.0026799738573186563850015, 
                        0.0026753913671672833892344, 0.0026707837197870311237119, 
                        0.0026661509585045101038391, 0.0026614931268824817854798, 
                        0.0026568102687194489357814, 0.0026521024280492437872770, 
                        0.0026473696491406139791397, 0.0026426119764968062894804, 
                        0.0026378294548551481626046, 0.0026330221291866270351630, 
                        0.0026281900446954674651512, 0.0026233332468187060677353, 
                        0.0026184517812257642618999, 0.0026135456938180188319369, 
                        0.0026086150307283703078113, 0.0026036598383208091684657, 
                        0.0025986801631899798721388, 0.0025936760521607427178014, 
                        0.0025886475522877335418257, 0.0025835947108549212540321, 
                        0.0025785175753751632172710, 0.0025734161935897584747222, 
                        0.0025682906134679988291122, 0.0025631408832067177780710, 
                        0.0025579670512298373098703, 0.0025527691661879125638030, 
                        0.0025475472769576743594882, 0.0025423014326415695994010, 
                        0.0025370316825672995489502, 0.0025317380762873559984451, 
                        0.0025264206635785553113127, 0.0025210794944415703629476, 
                        0.0025157146191004603745948, 0.0025103260880021986466869, 
                        0.0025049139518161981960773, 0.0024994782614338353016280, 
                        0.0024940190679679709626349, 0.0024885364227524702745874, 
                        0.0024830303773417197267843, 0.0024775009835101424263432, 
                        0.0024719482932517112531633, 0.0024663723587794599504176, 
                        0.0024607732325249921551741, 0.0024551509671379883737605, 
                        0.0024495056154857109065099, 0.0024438372306525067265426, 
                        0.0024381458659393083172574, 0.0024324315748631324732279, 
                        0.0024266944111565770692147, 0.0024209344287673158020275, 
                        0.0024151516818575909099866, 0.0024093462248037038747545, 
                        0.0024035181121955041103265, 0.0023976673988358756439882, 
                        0.0023917941397402217940673, 0.0023858983901359478493246, 
                        0.0023799802054619417548485, 0.0023740396413680528093376, 
                        0.0023680767537145683786720, 0.0023620915985716886306938, 
                        0.0023560842322189992961374, 0.0023500547111449424606655, 
                        0.0023440030920462853929883, 0.0023379294318275874140606, 
                        0.0023318337876006648123684, 0.0023257162166840538103394, 
                        0.0023195767766024715869239, 0.0023134155250862753614165, 
                        0.0023072325200709195436049, 0.0023010278196964109553481, 
                        0.0022948014823067621287099, 0.0022885535664494426857857, 
                        0.0022822841308748288053830, 0.0022759932345356507817318, 
                        0.0022696809365864386804193, 0.0022633472963829660967620, 
                        0.0022569923734816920218464, 0.0022506162276392008214839, 
                        0.0022442189188116403333494, 0.0022378005071541580875846, 
                        0.0022313610530203356561684, 0.0022249006169616211363732, 
                        0.0022184192597267597736437, 0.0022119170422612227292520, 
                        0.0022053940257066339981005, 0.0021988502714001954820607, 
                        0.0021922858408741102242558, 0.0021857007958550038097087, 
                        0.0021790951982633439377969, 0.0021724691102128581719720, 
                        0.0021658225940099498722195, 0.0021591557121531123157498, 
                        0.0021524685273323410114303, 0.0021457611024285442134846, 
                        0.0021390335005129516400021, 0.0021322857848465214018174, 
                        0.0021255180188793451473363, 0.0021187302662500514289029, 
                        0.0021119225907852072963166, 0.0021050950564987181231273, 
                        0.0020982477275912256713511, 0.0020913806684495044002679, 
                        0.0020844939436458560249764, 0.0020775876179375023304007, 
                        0.0020706617562659762464561, 0.0020637164237565111901030, 
                        0.0020567516857174286800274, 0.0020497676076395242297101, 
                        0.0020427642551954515246552, 0.0020357416942391048895728, 
                        0.0020286999908050000513193, 0.0020216392111076532034194, 
                        0.0020145594215409583780096, 0.0020074606886775631310555, 
                        0.0020003430792682425467160, 0.0019932066602412715667394, 
                        0.0019860514987017956507927, 0.0019788776619311997736447, 
                        0.0019716852173864757651327, 0.0019644742326995879988655, 
                        0.0019572447756768374356240, 0.0019499969142982240274419, 
                        0.0019427307167168074883601, 0.0019354462512580664378677, 
                        0.0019281435864192559230531, 0.0019208227908687633255086, 
                        0.0019134839334454626590447, 0.0019061270831580672642844, 
                        0.0018987523091844809062265, 0.0018913596808711472808775, 
                        0.0018839492677323979370705, 0.0018765211394497986196010, 
                        0.0018690753658714940398285, 0.0018616120170115510799024, 
                        0.0018541311630493004367905, 0.0018466328743286767122991, 
                        0.0018391172213575569552912, 0.0018315842748070976623218, 
                        0.0018240341055110702429247, 0.0018164667844651949558009, 
                        0.0018088823828264733221690, 0.0018012809719125190225581, 
                        0.0017936626232008872833327, 0.0017860274083284027592567, 
                        0.0017783753990904859184165, 0.0017707066674404779358362, 
                        0.0017630212854889641021349, 0.0017553193255030957535871, 
                        0.0017476008599059107299616, 0.0017398659612756523665312, 
                        0.0017321147023450870266539, 0.0017243471560008201813452, 
                        0.0017165633952826110422716, 0.0017087634933826857546100, 
                        0.0017009475236450491562317, 0.0016931155595647951096823, 
                        0.0016852676747874154134422, 0.0016774039431081072989678, 
                        0.0016695244384710795200224, 0.0016616292349688570408253, 
                        0.0016537184068415843295541, 0.0016457920284763272637533, 
                        0.0016378501744063736542136, 0.0016298929193105323938983, 
                        0.0016219203380124312385075, 0.0016139325054798132252838, 
                        0.0016059294968238317366751, 0.0015979113872983442154825, 
                        0.0015898782522992045381361, 0.0015818301673635540527516, 
                        0.0015737672081691112886347, 0.0015656894505334603439125, 
                        0.0015575969704133379579831, 0.0015494898439039192754876, 
                        0.0015413681472381023085203, 0.0015332319567857911038062, 
                        0.0015250813490531776215856, 0.0015169164006820223329593, 
                        0.0015087371884489335424584, 0.0015005437892646454426166, 
                        0.0014923362801732949073323, 0.0014841147383516970308228, 
                        0.0014758792411086194189814, 0.0014676298658840552399621, 
                        0.0014593666902484950408286, 0.0014510897919021973371136, 
                        0.0014427992486744579821480, 0.0014344951385228783230315, 
                        0.0014261775395326321501237, 0.0014178465299157314469528, 
                        0.0014095021880102909474427, 0.0014011445922797915073771, 
                        0.0013927738213123422970256, 0.0013843899538199418218713, 
                        0.0013759930686377377783877, 0.0013675832447232857518263, 
                        0.0013591605611558067629844, 0.0013507250971354436709363, 
                        0.0013422769319825164387192, 0.0013338161451367762689788, 
                        0.0013253428161566586165863, 0.0013168570247185350852537, 
                        0.0013083588506159642151809, 0.0012998483737589411687807, 
                        0.0012913256741731463215379, 0.0012827908319991927650686, 
                        0.0012742439274918727294554, 0.0012656850410194029319476, 
                        0.0012571142530626688591208, 0.0012485316442144679896043, 
                        0.0012399372951787519644928, 0.0012313312867698677125706, 
                        0.0012227136999117975374834, 0.0012140846156373981740056, 
                        0.0012054441150876388205601, 0.0011967922795108381551550, 
                        0.0011881291902619003419159, 0.0011794549288015500353964, 
                        0.0011707695766955663898644, 0.0011620732156140160807669, 
                        0.0011533659273304853455891, 0.0011446477937213110513287, 
                        0.0011359188967648107958214, 0.0011271793185405120501566, 
                        0.0011184291412283803494364, 0.0011096684471080465391373, 
                        0.0011008973185580330843445, 0.0010921158380549794491381, 
                        0.0010833240881728665534171, 0.0010745221515822403144596, 
                        0.0010657101110494342805238, 0.0010568880494357913638046, 
                        0.0010480560496968846800697, 0.0010392141948817375023057, 
                        0.0010303625681320423357186, 0.0010215012526813791214350, 
                        0.0010126303318544325762649, 0.0010037498890662086758941, 
                        0.0009948600078212502888805, 0.0009859607717128519688418, 
                        0.0009770522644222739122264, 0.0009681345697179550890732, 
                        0.0009592077714547255541688, 0.0009502719535730179460261, 
                        0.0009413272000980781811114, 0.0009323735951391753507612, 
                        0.0009234112228888108282347, 0.0009144401676219265933610, 
                        0.0009054605136951127822476, 0.0008964723455458144695262, 
                        0.0008874757476915376906225, 0.0008784708047290547115472, 
                        0.0008694576013336085537138, 0.0008604362222581167813022, 
                        0.0008514067523323745586954, 0.0008423692764622569855308, 
                        0.0008333238796289207169173, 0.0008242706468880048763834, 
                        0.0008152096633688312691343, 0.0008061410142736039032099, 
                        0.0007970647848766078261514, 0.0007879810605234072847989, 
                        0.0007788899266300432158601, 0.0007697914686822300749096, 
                        0.0007606857722345520114971, 0.0007515729229096583980656, 
                        0.0007424530063974587204051, 0.0007333261084543168373926, 
                        0.0007241923149022446178008, 0.0007150517116280949619884, 
                        0.0007059043845827542163241, 0.0006967504197803339882351, 
                        0.0006875899032973623698204, 0.0006784229212719745780188, 
                        0.0006692495599031030193850, 0.0006600699054496667875923, 
                        0.0006508840442297606018626, 0.0006416920626198431946113, 
                        0.0006324940470539251567018, 0.0006232900840227562488244, 
                        0.0006140802600730121876541, 0.0006048646618064809156059, 
                        0.0005956433758792483631993, 0.0005864164890008837132649, 
                        0.0005771840879336241764943, 0.0005679462594915592881427, 
                        0.0005587030905398147360662, 0.0005494546679937357307118, 
                        0.0005402010788180699282026, 0.0005309424100261499182844, 
                        0.0005216787486790752896494, 0.0005124101818848942860548, 
                        0.0005031367967977850677401, 0.0004938586806172365939677, 
                        0.0004845759205872291441124, 0.0004752886039954144966810, 
                        0.0004659968181722957880391, 0.0004567006504904070755681, 
                        0.0004474001883634926336095, 0.0004380955192456860150653, 
                        0.0004287867306306889171352, 0.0004194739100509498966958, 
                        0.0004101571450768429896514, 0.0004008365233158462997325, 
                        0.0003915121324117206363681, 0.0003821840600436882993131, 
                        0.0003728523939256121308821, 0.0003635172218051749865499, 
                        0.0003541786314630598135175, 0.0003448367107121305776064, 
                        0.0003354915473966143456333, 0.0003261432293912849189248, 
                        0.0003167918446006485317858, 0.0003074374809581322877037, 
                        0.0002980802264252762217455, 0.0002887201689909301727620, 
                        0.0002793573966704570567274, 0.0002699919975049447012834, 
                        0.0002606240595604292032823, 0.0002512536709271339139118, 
                        0.0002418809197187298044384, 0.0002325058940716253739001, 
                        0.0002231286821442978268308, 0.0002137493721166826096154, 
                        0.0002043680521896465790359, 0.0001949848105845827899210, 
                        0.0001855997355431850062940, 0.0001762129153274925249194, 
                        0.0001668244382203495280013, 0.0001574343925265138930609, 
                        0.0001480428665748079976500, 0.0001386499487219861751244, 
                        0.0001292557273595155266326, 0.0001198602909254695827354, 
                        0.0001104637279257437565603, 0.0001010661269730276014588, 
                        0.0000916675768613669107254, 0.0000822681667164572752810, 
                        0.0000728679863190274661367, 0.0000634671268598044229933, 
                        0.0000540656828939400071988, 0.0000446637581285753393838, 
                        0.0000352614859871986975067, 0.0000258591246764618586716, 
                        0.0000164577275798968681068, 0.0000070700764101825898713};

   switch(npoints) {
   case (4): 
      *x = x4;  *w = w4; break;
   case (8):
      *x = x8;  *w = w8; break;
   case (16):
      *x = x16;  *w = w16; break;
   case (32):
      *x = x32;  *w = w32; break;
   case (64):
      *x = x64;  *w = w64; break;
   case (128):
      *x = x128;  *w = w128; break;
   case (256):
      *x = x256;  *w = w256; break;
   case (512):
      *x = x512;  *w = w512; break;
   case (1024):
      *x = x1024;  *w = w1024; break;
   default :
      error2("use 10, 20, 32, 64, 128, 512, 1024 for npoints for legendre.");
   }
   return(status);
}



double NIntegrateGaussLegendre (double(*fun)(double x), double a, double b, int npoints)
{
/* this approximates the integral Nintegrate[fun[x], {x,a,b}].
   npoints is 10, 20, 32 or 64 nodes for legendre.");
*/
   int j;
   double *x=NULL, *w=NULL, s=0, t[2];

   GaussLegendreRule(&x, &w, npoints);

   /* this goes through the natural order from a to b */
   for(j=npoints/2-1; j>=0; j--) {
      t[1] = (a+b)/2 - (b-a)/2*x[j];
      s += w[j]*fun(t[1]);
   }
   for(j=0; j<npoints/2; j++) {
      t[0] = (a+b)/2 + (b-a)/2*x[j];
      s += w[j]*fun(t[0]);
   }

/*
   for(j=0,s=0; j<npoints/2; j++) {
      t[0] = (a+b)/2 + (b-a)/2*x[j];
      t[1] = (a+b)/2 - (b-a)/2*x[j];
      for(i=0; i<2; i++)
         s += w[j]*fun(t[i]);
   }
*/
   return s *= (b-a)/2;
}


int GaussLaguerreRule(double **x, double **w, int npoints)
{
/* this returns the Gauss-Laguerre nodes and weights in x[] and w[].
   npoints = 5, 10, 20.
*/
   int status=0;
   static double x5[]={0.263560319718140910203061943361E+00,
                       0.141340305910651679221840798019E+01, 
                       0.359642577104072208122318658878E+01, 
                       0.708581000585883755692212418111E+01, 
                       0.126408008442757826594332193066E+02};
   static double w5[]={0.521755610582808652475860928792E+00,
                       0.398666811083175927454133348144E+00,
                       0.759424496817075953876533114055E-01,
                       0.361175867992204845446126257304E-02,
                       0.233699723857762278911490845516E-04};

   static double x10[]={0.137793470540492430830772505653E+00,
	                   	0.729454549503170498160373121676E+00,
	                   	0.180834290174031604823292007575E+01,
	                   	0.340143369785489951448253222141E+01,
	                   	0.555249614006380363241755848687E+01,
                   		0.833015274676449670023876719727E+01,
                   		0.118437858379000655649185389191E+02,
                   		0.162792578313781020995326539358E+02,
                   		0.219965858119807619512770901956E+02,
		                	0.299206970122738915599087933408E+02};
   static double w10[]={0.308441115765020141547470834678E+00,
	                   	0.401119929155273551515780309913E+00,
	                   	0.218068287611809421588648523475E+00,
	                   	0.620874560986777473929021293135E-01,
	                   	0.950151697518110055383907219417E-02,
                   		0.753008388587538775455964353676E-03,
                   		0.282592334959956556742256382685E-04,
                   		0.424931398496268637258657665975E-06,
                   		0.183956482397963078092153522436E-08,
		                	0.991182721960900855837754728324E-12};

   static double x20[]={0.705398896919887533666890045842E-01,
                        0.372126818001611443794241388761E+00,
                        0.916582102483273564667716277074E+00,
                        0.170730653102834388068768966741E+01,
	                   	0.274919925530943212964503046049E+01,
	                   	0.404892531385088692237495336913E+01,
	                   	0.561517497086161651410453988565E+01,
	                   	0.745901745367106330976886021837E+01,
                   		0.959439286958109677247367273428E+01,
                   		0.120388025469643163096234092989E+02,
                   		0.148142934426307399785126797100E+02,
                   		0.179488955205193760173657909926E+02,
		                	0.214787882402850109757351703696E+02,
	                   	0.254517027931869055035186774846E+02,
	                   	0.299325546317006120067136561352E+02,
	                   	0.350134342404790000062849359067E+02,
	                   	0.408330570567285710620295677078E+02,
                   		0.476199940473465021399416271529E+02,
                   		0.558107957500638988907507734445E+02,
                        0.665244165256157538186403187915E+02};
   static double w20[]={0.168746801851113862149223899689E+00,
	                     0.291254362006068281716795323812E+00,
	                   	0.266686102867001288549520868998E+00,
	                   	0.166002453269506840031469127816E+00,
	                   	0.748260646687923705400624639615E-01,
	                   	0.249644173092832210728227383234E-01,
                   		0.620255084457223684744754785395E-02,
                   		0.114496238647690824203955356969E-02,
                   		0.155741773027811974779809513214E-03,
                   		0.154014408652249156893806714048E-04,
		                	0.108648636651798235147970004439E-05,
	                   	0.533012090955671475092780244305E-07,
	                   	0.175798117905058200357787637840E-08,
	                   	0.372550240251232087262924585338E-10,
	                   	0.476752925157819052449488071613E-12,
                   		0.337284424336243841236506064991E-14,
                   		0.115501433950039883096396247181E-16,
                   		0.153952214058234355346383319667E-19,
                   		0.528644272556915782880273587683E-23,
		                	0.165645661249902329590781908529E-27};
   if(npoints==5)
      { *x=x5;  *w=w5; }
   else if(npoints==10)
      { *x=x10;  *w=w10; }
   else if(npoints==20)
      { *x=x20;  *w=w20; }
   else {
      puts("use 5, 10, 20 nodes for GaussLaguerreRule.");
      status=-1;
   }
   return(status);
}

int ScatterPlot (int n, int nseries, int yLorR[], double x[], double y[],
    int nrow, int ncol, int ForE)
{
/* This plots a scatter diagram.  There are nseries of data (y) 
   for the same x.  nrow and ncol specifies the #s of rows and cols 
   in the text output.
   Use ForE=1 for floating format
   yLorR[nseries] specifies which y axis (L or R) to use, if nseries>1.
*/
   char *chart,ch, *fmt[2]={"%*.*e ", "%*.*f "}, symbol[]="*~^@",overlap='&';
   int i,j,is,iy,ny=1, ncolr=ncol+3, irow=0, icol=0, w=10, wd=2;
   double large=1e32, xmin, xmax, xgap, ymin[2], ymax[2], ygap[2];

   for (i=1,xmin=xmax=x[0]; i<n; i++) 
      { if(xmin>x[i]) xmin=x[i]; if(xmax<x[i]) xmax=x[i]; }
   for (i=0; i<2; i++) { ymin[i]=large; ymax[i]=-large; }
   for (j=0; j<(nseries>1)*nseries; j++)
      if (yLorR[j]==1) ny=2;
      else if (yLorR[j]!=0) printf ("err: y axis %d", yLorR[j]);
   for (j=0; j<nseries; j++) {
      for (i=0,iy=(nseries==1?0:yLorR[j]); i<n; i++) {
         if (ymin[iy]>y[j*n+i])  ymin[iy]=y[j*n+i];
         if (ymax[iy]<y[j*n+i])  ymax[iy]=y[j*n+i];
      }
   }
   if (xmin==xmax) { puts("no variation in x?"); }
   xgap=(xmax-xmin)/ncol;   
   for (iy=0; iy<ny; iy++) ygap[iy]=(ymax[iy]-ymin[iy])/nrow;

   printf ("\n%10s", "legend: ");
   for (is=0; is<nseries; is++) printf ("%2c", symbol[is]);
   printf ("\n%10s", "y axies: ");
   if (ny==2)  for(is=0; is<nseries; is++) printf ("%2d", yLorR[is]);

   printf ("\nx   : (%10.2e, %10.2e)", xmin, xmax);
   printf ("\ny[1]: (%10.2e, %10.2e)\n", ymin[0], ymax[0]);
   if (ny==2) printf ("y[2]: (%10.2e, %10.2e)  \n", ymin[1], ymax[1]);

   chart=(char*)malloc((nrow+1)*ncolr*sizeof(char));
   for (i=0; i<nrow+1; i++) {
      for (j=1; j<ncol; j++) chart[i*ncolr+j]=' ';
      if (i%5==0) chart[i*ncolr+0]=chart[i*ncolr+j++]='+'; 
      else        chart[i*ncolr+0]=chart[i*ncolr+j++]='|'; 
      chart[i*ncolr+j]='\0'; 
      if (i==0||i==nrow) 
         FOR(j,ncol+1) chart[i*ncolr+j]=(char)(j%10==0?'+':'-');
   }

   for (is=0; is<nseries; is++) {
      for (i=0,iy=(nseries==1?0:yLorR[is]); i<n; i++) {
         for(j=0; j<ncol+1; j++) if(x[i]<=xmin+(j+0.5)*xgap) { icol=j; break; }
         for(j=0; j<nrow+1; j++) 
            if(y[is*n+i]<=ymin[iy]+(j+0.5)*ygap[iy]) { irow=nrow-j; break;}

/*
         chart[irow*ncolr+icol]=symbol[is];
*/
         if ((ch=chart[irow*ncolr+icol])==' ' || ch=='-' || ch=='+') 
            chart[irow*ncolr+icol]=symbol[is];
         else
            chart[irow*ncolr+icol]=overlap;

      }
   }
   printf ("\n");
   for (i=0; i<nrow+1; i++) {
     if (i%5==0) printf (fmt[ForE], w-1, wd, ymin[0]+(nrow-i)*ygap[0]);
     else        printf ("%*s", w, "");
     printf ("%s", chart+i*ncolr); 
     if (ny==2 && i%5==0) printf(fmt[ForE], w-1, wd, ymin[1]+(nrow-i)*ygap[1]);
     printf ("\n");
   }
   printf ("%*s", w-6, "");
   for (j=0; j<ncol+1; j++) if(j%10==0) printf(fmt[ForE], 10-1,wd,xmin+j*xgap);
   printf ("\n%*s\n", ncol/2+1+w, "x");
   free(chart);
   return(0);
}

void rainbowRGB (double temperature, int *R, int *G, int *B)
{
/* This returns the RGB values, each between 0 and 255, for given temperature 
   value in the range (0, 1) in the rainbow.  
   Curve fitting from the following data:

    T        R       G       B
    0        14      1       22
    0.1      56      25      57
    0.2      82      82      130
    0.3      93      120     60
    0.4      82      155     137
    0.5      68      185     156
    0.6      114     207     114
    0.7      223     228     70
    0.8      243     216     88
    0.9      251     47      37
    1        177     8       0

*/
   double T=temperature, maxT=1;

   if(T>maxT) error2("temperature rescaling needed.");
   *R = (int)fabs( -5157.3*T*T*T*T + 9681.4*T*T*T - 5491.9*T*T + 1137.7*T + 6.2168 );
   *G = (int)fabs( -1181.4*T*T*T + 964.8*T*T + 203.66*T + 1.2028 );
   *B = (int)fabs( 92.463*T*T*T - 595.92*T*T + 481.11*T + 21.769 );

   if(*R>255) *R=255;
   if(*G>255) *G=255;
   if(*B>255) *B=255;
}


void GetIndexTernary(int *ix, int *iy, double *x, double *y, int itriangle, int K)
{
/*  This gives the indices (ix, iy) and the coordinates (x, y, 1-x-y) for 
    the itriangle-th triangle, with itriangle from 0, 1, ..., KK-1.  
    The ternary graph (0-1 on each axis) is partitioned into K*K equal-sized 
    triangles.  
    In the first row (ix=0), there is one triangle (iy=0);
    In the second row (ix=1), there are 3 triangles (iy=0,1,2);
    In the i-th row (ix=i), there are 2*i+1 triangles (iy=0,1,...,2*i).

    x rises when ix goes up, but y decreases when iy increases.  (x,y) is the 
    centroid in the ij-th small triangle.
    
    x and y each takes on 2*K-1 possible values.
*/
    *ix = (int)sqrt((double)itriangle);
    *iy = itriangle - square(*ix);

    *x = (1 + (*iy/2)*3 + (*iy%2))/(3.*K);
    *y = (1 + (K-1- *ix)*3 + (*iy%2))/(3.*K);
}



long factorial (int n)
{
   long f=1, i;
   if (n>11) error2("n>10 in factorial");
   for (i=2; i<=(long)n; i++) f *= i;
   return (f);
}


double Binomial (double n, int k, double *scale)
{
/* calculates (n choose k), where n is any real number, and k is integer.
   If(*scale!=0) the result should be c+exp(*scale).
*/
   double c=1,i,large=1e99;

   *scale=0;
   if((int)k!=k) 
      error2("k is not a whole number in Binomial.");
   if(n<0 && k%2==1) 
      c = -1;
   if(k==0) return(1);
   if(n>0 && (k<0 || k>n)) return (0);

   if(n>0 && (int)n==n) k=min2(k,(int)n-k);
   for (i=1; i<=k; i++) {
      c *= (n-k+i)/i;
      if(c>large) { 
         *scale += log(c); c=1; 
      } 
   }
   return(c);
}

/****************************
          Vectors and matrices 
*****************************/

double Det3x3 (double x[3*3])
{
   return 
       x[0*3+0]*x[1*3+1]*x[2*3+2] 
     + x[0*3+1]*x[1*3+2]*x[2*3+0] 
     + x[0*3+2]*x[1*3+0]*x[2*3+1] 
     - x[0*3+0]*x[1*3+2]*x[2*3+1] 
     - x[0*3+1]*x[1*3+0]*x[2*3+2] 
     - x[0*3+2]*x[1*3+1]*x[2*3+0] ;
}

int matby (double a[], double b[], double c[], int n,int m,int k)
/* a[n*m], b[m*k], c[n*k]  ......  c = a*b
*/
{
   int i,j,i1;
   double t;
   FOR (i,n)  FOR(j,k) {
      for (i1=0,t=0; i1<m; i1++) t+=a[i*m+i1]*b[i1*k+j];
      c[i*k+j] = t;
   }
   return (0);
}


int matIout (FILE *fout, int x[], int n, int m)
{
   int i,j;
   for (i=0,FPN(fout); i<n; i++,FPN(fout)) 
      FOR(j,m) fprintf(fout,"  %4d", x[i*m+j]);
   return (0);
}

int matout (FILE *fout, double x[], int n, int m)
{
   int i,j;
   for (i=0,FPN(fout); i<n; i++,FPN(fout)) 
      FOR(j,m) fprintf(fout," %11.6f", x[i*m+j]);
   return (0);
}


int matout2 (FILE * fout, double x[], int n, int m, int wid, int deci)
{
   int i,j;
   for (i=0,FPN(fout); i<n; i++,FPN(fout))
      for(j=0; j<m; j++)
         fprintf(fout," %*.*f", wid-1, deci, x[i*m+j]);
   return (0);
}

int mattransp1 (double x[], int n)
/* transpose a matrix x[n*n], stored by rows.
*/
{
   int i,j;
   double t;
   FOR (i,n)  for (j=0; j<i; j++)
      if (i!=j) {  t=x[i*n+j];  x[i*n+j]=x[j*n+i];   x[j*n+i]=t; }
   return (0);
}

int mattransp2 (double x[], double y[], int n, int m)
{
/* transpose a matrix  x[n][m] --> y[m][n]
*/
   int i,j;

   FOR (i,n)  FOR (j,m)  y[j*n+i]=x[i*m+j];
   return (0);
}

int matinv (double x[], int n, int m, double space[])
{
/* x[n*m]  ... m>=n
   space[n].  This puts the fabs(|x|) into space[0].  Check and calculate |x|.
   Det may have the wrong sign.  Check and fix.
*/
   int i,j,k;
   int *irow=(int*) space;
   double ee=1e-100, t,t1,xmax, det=1;

   for(i=0; i<n; i++) irow[i]=i;

   for(i=0; i<n; i++)  {
      xmax = fabs(x[i*m+i]);
      for (j=i+1; j<n; j++)
         if (xmax<fabs(x[j*m+i]))
            { xmax = fabs(x[j*m+i]); irow[i]=j; }
      det *= x[irow[i]*m+i];
      if (xmax < ee)   {
         printf("\nxmax = %.4e close to zero at %3d!\t\n", xmax,i+1);
         exit(-1);
      }
      if (irow[i] != i) {
         FOR (j,m) {
            t = x[i*m+j];
            x[i*m+j] = x[irow[i]*m+j];
            x[irow[i]*m+j] = t;
         }
      }
      t = 1./x[i*m+i];
      FOR (j,n) {
         if (j == i) continue;
         t1 = t*x[j*m+i];
         FOR(k,m)  x[j*m+k] -= t1*x[i*m+k];
         x[j*m+i] = -t1;
      }
      FOR(j,m)   x[i*m+j] *= t;
      x[i*m+i] = t;
   }                            /* for(i) */
   for (i=n-1; i>=0; i--) {
      if (irow[i] == i) continue;
      FOR(j,n)  {
         t = x[j*m+i];
         x[j*m+i] = x[j*m + irow[i]];
         x[j*m + irow[i]] = t;
      }
   }
   space[0]=det;
   return(0);
}


int matexp (double Q[], double t, int n, int TimeSquare, double space[])
{
/* This calculates the matrix exponential P(t) = exp(t*Q).
   Input: Q[] has the rate matrix, and t is the time or branch length.
          TimeSquare is the number of times the matrix is squared and should 
          be from 5 to 31.
   Output: Q[] has the transition probability matrix, that is P(Qt).
   space[n*n]: required working space.

      P(t) = (I + Qt/m + (Qt/m)^2/2)^m, with m = 2^TimeSquare.

   T[it=0] is the current matrix, and T[it=1] is the squared result matrix,
   used to avoid copying matrices.
   Use an even TimeSquare to avoid one round of matrix copying.
*/
   int it, i;
   double *T[2];

   if(TimeSquare<2 || TimeSquare>31) error2("TimeSquare not good");
   T[0]=Q; T[1]=space;
   for(i=0; i<n*n; i++)  T[0][i] = ldexp( Q[i]*t, -TimeSquare );

   matby (T[0], T[0], T[1], n, n, n);
   for(i=0; i<n*n; i++)  T[0][i] += T[1][i]/2;
   for(i=0; i<n; i++)  T[0][i*n+i] ++;

   for(i=0,it=0; i<TimeSquare; i++) {
      it = !it;
      matby (T[1-it], T[1-it], T[it], n, n, n);
   }
   if(it==1) 
      for(i=0;i<n*n;i++) Q[i]=T[1][i];
   return(0);
}



void HouseholderRealSym(double a[], int n, double d[], double e[]);
int EigenTridagQLImplicit(double d[], double e[], int n, double z[]);

int matsqrt (double A[], int n, double work[])
{
/* This finds the symmetrical square root of a real symmetrical matrix A[n*n].
   R * R = A.  The root is returned in A[].
   The work space if work[n*n*2+n].
   Used the same procedure as eigenRealSym(), but does not sort eigen values.
*/
   int i,j, status;
   double *U=work, *Root=U+n*n, *V=Root+n;

   xtoy(A, U, n*n);
   HouseholderRealSym(U, n, Root, V);
   status=EigenTridagQLImplicit(Root, V, n, U);
   mattransp2 (U, V, n, n);
   for(i=0;i<n;i++) 
      if(Root[i]<0) error2("negative root in matsqrt?");
      else          Root[i]=sqrt(Root[i]);
   for(i=0;i<n;i++) for(j=0;j<n;j++) 
      U[i*n+j] *= Root[j];
   matby (U, V, A, n, n, n);

   return(status);
}



int CholeskyDecomp (double A[], int n, double L[])
{
/* A=LL', where A is symmetrical and positive-definite, and L is
   lower-diagonal
   only A[i*n+j] (j>=i) are used.
*/
   int i,j,k;
   double t;

   for (i=0; i<n; i++) 
      for (j=i+1; j<n; j++)
         L[i*n+j] = 0;
   for (i=0; i<n; i++) {
      for (k=0,t=A[i*n+i]; k<i; k++) 
         t -= square(L[i*n+k]);
      if (t>=0)    
         L[i*n+i] = sqrt(t);   
      else
         return (-1);
      for (j=i+1; j<n; j++) {
         for (k=0,t=A[i*n+j]; k<i; k++) 
            t -= L[i*n+k]*L[j*n+k];
         L[j*n+i] = t/L[i*n+i];
      }
   }
   return (0);
}


int Choleskyback (double L[], double b[], double x[], int n);
int CholeskyInverse (double L[], int n);

int Choleskyback (double L[], double b[], double x[], int n)
{
/* solve Ax=b, where A=LL' is lower-diagonal.  
   x=b O.K.  Only A[i*n+j] (i>=j) are used
*/
  
   int i,j;
   double t;

   for (i=0; i<n; i++) {       /* solve Ly=b, and store results in x */
      for (j=0,t=b[i]; j<i; j++) t-=L[i*n+j]*x[j];
      x[i]=t/L[i*n+i];
   }
   for (i=n-1; i>=0; i--) {    /* solve L'x=y, and store results in x */
      for (j=i+1,t=x[i]; j<n; j++) t-=L[j*n+i]*x[j];
      x[i]=t/L[i*n+i];
   }
   return (0);
}

int CholeskyInverse (double L[], int n)
{
/* inverse of L
*/
   int i,j,k;
   double t;

   for (i=0; i<n; i++) {
      L[i*n+i]=1/L[i*n+i];
      for (j=i+1; j<n; j++) {
         for (k=i,t=0; k<j; k++) t-=L[j*n+k]*L[k*n+i];
         L[j*n+i]=t/L[j*n+j];
      }
   }
   return (0);
}


int eigenQREV (double Q[], double pi[], int n, 
               double Root[], double U[], double V[], double spacesqrtpi[])
{
/* 
   This finds the eigen solution of the rate matrix Q for a time-reversible 
   Markov process, using the algorithm for a real symmetric matrix.
   Rate matrix Q = S * diag{pi} = U * diag{Root} * V, 
   where S is symmetrical, all elements of pi are positive, and U*V = I.
   space[n] is for storing sqrt(pi).

   [U 0] [Q_0 0] [U^-1 0]    [Root  0]
   [0 I] [0   0] [0    I]  = [0     0]

   Ziheng Yang, 25 December 2001 (ref is CME/eigenQ.pdf)
*/
   int i,j, inew, jnew, nnew, status;
   double *pi_sqrt=spacesqrtpi, small=1e-100;

   for(j=0,nnew=0; j<n; j++)
      if(pi[j]>small)
         pi_sqrt[nnew++] = sqrt(pi[j]);

   /* store in U the symmetrical matrix S = sqrt(D) * Q * sqrt(-D) */

   if(nnew==n) {
      for(i=0; i<n; i++)
         for(j=0,U[i*n+i] = Q[i*n+i]; j<i; j++)
            U[i*n+j] = U[j*n+i] = (Q[i*n+j] * pi_sqrt[i]/pi_sqrt[j]);

      status=eigenRealSym(U, n, Root, V);
      for(i=0; i<n; i++) for(j=0; j<n; j++)  V[i*n+j] = U[j*n+i] * pi_sqrt[j];
      for(i=0; i<n; i++) for(j=0; j<n; j++)  U[i*n+j] /= pi_sqrt[i];
   }
   else {
      for(i=0,inew=0; i<n; i++) {
         if(pi[i]>small) {
            for(j=0,jnew=0; j<i; j++) 
               if(pi[j]>small) {
                  U[inew*nnew+jnew] = U[jnew*nnew+inew] 
                                    = Q[i*n+j] * pi_sqrt[inew]/pi_sqrt[jnew];
                  jnew++;
               }
            U[inew*nnew+inew] = Q[i*n+i];
            inew++;
         }
      }

      status=eigenRealSym(U, nnew, Root, V);

      for(i=n-1,inew=nnew-1; i>=0; i--)   /* construct Root */
         Root[i] = (pi[i]>small ? Root[inew--] : 0);
      for(i=n-1,inew=nnew-1; i>=0; i--) {  /* construct V */
         if(pi[i]>small) {
            for(j=n-1,jnew=nnew-1; j>=0; j--)
               if(pi[j]>small) {
                  V[i*n+j] = U[jnew*nnew+inew]*pi_sqrt[jnew];
                  jnew--;
               }
               else 
                  V[i*n+j] = (i==j);
            inew--;
         }
         else 
            for(j=0; j<n; j++)  V[i*n+j] = (i==j);
      }
      for(i=n-1,inew=nnew-1; i>=0; i--) {  /* construct U */
         if(pi[i]>small) {
            for(j=n-1,jnew=nnew-1;j>=0;j--)
               if(pi[j]>small) {
                  U[i*n+j] = U[inew*nnew+jnew]/pi_sqrt[inew];
                  jnew--;
               }
               else 
                  U[i*n+j] = (i==j);
            inew--;
         }
         else 
            for(j=0;j<n;j++)
               U[i*n+j] = (i==j);
      }
   }

/*   This routine works on P(t) as well as Q. */
/*
   if(fabs(Root[0])>1e-10 && noisy) printf("Root[0] = %.5e\n",Root[0]);
   Root[0]=0; 
*/
   return(status);
}


/* eigen solution for real symmetric matrix */

void HouseholderRealSym(double a[], int n, double d[], double e[]);
int EigenTridagQLImplicit(double d[], double e[], int n, double z[]);
void EigenSort(double d[], double U[], int n);

int eigenRealSym(double A[], int n, double Root[], double work[])
{
/* This finds the eigen solution of a real symmetrical matrix A[n*n].  In return, 
   A has the right vectors and Root has the eigenvalues. 
   work[n] is the working space.
   The matrix is first reduced to a tridiagonal matrix using HouseholderRealSym(), 
   and then using the QL algorithm with implicit shifts.  

   Adapted from routine tqli in Numerical Recipes in C, with reference to LAPACK
   Ziheng Yang, 23 May 2001
*/
   int status=0;
   HouseholderRealSym(A, n, Root, work);
   status = EigenTridagQLImplicit(Root, work, n, A);
   EigenSort(Root, A, n);

   return(status);
}


void EigenSort(double d[], double U[], int n)
{
/* this sorts the eigen values d[] and rearrange the (right) eigen vectors U[]
*/
   int k,j,i;
   double p;

   for (i=0;i<n-1;i++) {
      p=d[k=i];
      for (j=i+1;j<n;j++)
         if (d[j] >= p) p=d[k=j];
      if (k != i) {
         d[k]=d[i];
         d[i]=p;
         for (j=0;j<n;j++) {
            p=U[j*n+i];
            U[j*n+i]=U[j*n+k];
            U[j*n+k]=p;
         }
      }
   }
}

void HouseholderRealSym(double a[], int n, double d[], double e[])
{
/* This uses HouseholderRealSym transformation to reduce a real symmetrical matrix 
   a[n*n] into a tridiagonal matrix represented by d and e.
   d[] is the diagonal (eigends), and e[] the off-diagonal.
*/
   int m,k,j,i;
   double scale,hh,h,g,f;

   for (i=n-1;i>=1;i--) {
      m=i-1;
      h=scale=0;
      if (m > 0) {
         for (k=0;k<=m;k++)
            scale += fabs(a[i*n+k]);
         if (scale == 0)
            e[i]=a[i*n+m];
         else {
            for (k=0;k<=m;k++) {
               a[i*n+k] /= scale;
               h += a[i*n+k]*a[i*n+k];
            }
            f=a[i*n+m];
            g=(f >= 0 ? -sqrt(h) : sqrt(h));
            e[i]=scale*g;
            h -= f*g;
            a[i*n+m]=f-g;
            f=0;
            for (j=0;j<=m;j++) {
               a[j*n+i]=a[i*n+j]/h;
               g=0;
               for (k=0;k<=j;k++)
                  g += a[j*n+k]*a[i*n+k];
               for (k=j+1;k<=m;k++)
                  g += a[k*n+j]*a[i*n+k];
               e[j]=g/h;
               f += e[j]*a[i*n+j];
            }
            hh=f/(h*2);
            for (j=0;j<=m;j++) {
               f=a[i*n+j];
               e[j]=g=e[j]-hh*f;
               for (k=0;k<=j;k++)
                  a[j*n+k] -= (f*e[k]+g*a[i*n+k]);
            }
         }
      } 
      else
         e[i]=a[i*n+m];
      d[i]=h;
   }
   d[0]=e[0]=0;

   /* Get eigenvectors */
   for (i=0;i<n;i++) {
      m=i-1;
      if (d[i]) {
         for (j=0;j<=m;j++) {
            g=0;
            for (k=0;k<=m;k++)
               g += a[i*n+k]*a[k*n+j];
            for (k=0;k<=m;k++)
               a[k*n+j] -= g*a[k*n+i];
         }
      }
      d[i]=a[i*n+i];
      a[i*n+i]=1;
      for (j=0;j<=m;j++) a[j*n+i]=a[i*n+j]=0;
   }
}

#define SIGN(a,b) ((b) >= 0.0 ? fabs(a) : -fabs(a))

int EigenTridagQLImplicit(double d[], double e[], int n, double z[])
{
/* This finds the eigen solution of a tridiagonal matrix represented by d and e.  
   d[] is the diagonal (eigenvalues), e[] is the off-diagonal
   z[n*n]: as input should have the identity matrix to get the eigen solution of the 
   tridiagonal matrix, or the output from HouseholderRealSym() to get the 
   eigen solution to the original real symmetric matrix.
   z[n*n]: has the orthogonal matrix as output

   Adapted from routine tqli in Numerical Recipes in C, with reference to
   LAPACK fortran code.
   Ziheng Yang, May 2001
*/
   int m,j,iter,niter=30, status=0, i,k;
   double s,r,p,g,f,dd,c,b, aa,bb;

   for (i=1;i<n;i++) e[i-1]=e[i];  e[n-1]=0;
   for (j=0;j<n;j++) {
      iter=0;
      do {
         for (m=j;m<n-1;m++) {
            dd=fabs(d[m])+fabs(d[m+1]);
            if (fabs(e[m])+dd == dd) break;  /* ??? */
         }
         if (m != j) {
            if (iter++ == niter) {
               status=-1;
               break;
            }
            g=(d[j+1]-d[j])/(2*e[j]);

            /* r=pythag(g,1); */

            if((aa=fabs(g))>1)  r=aa*sqrt(1+1/(g*g));
            else                r=sqrt(1+g*g);

            g=d[m]-d[j]+e[j]/(g+SIGN(r,g));
            s=c=1;
            p=0;
            for (i=m-1;i>=j;i--) {
               f=s*e[i];
               b=c*e[i];

               /*  r=pythag(f,g);  */
               aa=fabs(f); bb=fabs(g);
               if(aa>bb)       { bb/=aa;  r=aa*sqrt(1+bb*bb); }
               else if(bb==0)             r=0;
               else            { aa/=bb;  r=bb*sqrt(1+aa*aa); }

               e[i+1]=r;
               if (r == 0) {
                  d[i+1] -= p;
                  e[m]=0;
                  break;
               }
               s=f/r;
               c=g/r;
               g=d[i+1]-p;
               r=(d[i]-g)*s+2*c*b;
               d[i+1]=g+(p=s*r);
               g=c*r-b;
               for (k=0;k<n;k++) {
                  f=z[k*n+i+1];
                  z[k*n+i+1]=s*z[k*n+i]+c*f;
                  z[k*n+i]=c*z[k*n+i]-s*f;
               }
            }
            if (r == 0 && i >= j) continue;
            d[j]-=p; e[j]=g; e[m]=0;
         }
      } while (m != j);
   }
   return(status);
}

#undef SIGN





int MeanVar (double x[], int n, double *m, double *v)
{
   int i;

   for (i=0,*m=0; i<n; i++) *m  = (*m*i + x[i])/(i + 1.);
   for (i=0,*v=0; i<n; i++) *v += square(x[i] -  *m);
   if (n>1) *v /= (n-1.);
   return(0);
}

int variance (double x[], int n, int nx, double mx[], double vx[])
{
/* x[nx][n], mx[nx], vx[nx][nx]
*/
   int i, j, k;

   for(i=0; i<nx; i++)  mx[i]=0;
   for(i=0; i<nx; i++) {
      for(k=0; k<n; k++) {
         mx[i] = (mx[i]*k + x[i*n+k])/(k + 1.);
      }
   }
   for(i=0; i<nx*nx; i++) 
      vx[i] = 0;
   for (i=0; i<nx; i++) 
      for (j=i; j<nx; j++) {
         for(k=0; k<n; k++) 
            vx[i*nx+j] += (x[i*n+k] - mx[i]) * (x[j*n+k] - mx[j]);
       vx[j*nx+i] = (vx[i*nx+j] /= (n - 1.));
   }
   return(0);
}

int correl (double x[], double y[], int n, double *mx, double *my,
    double *v11, double *v12, double *v22, double *r)
{
   int i;

   *mx = *my = *v11 = *v12 = *v22 = 0.0;
   for (i=0; i<n; i++) {
       *v11 += square(x[i] - *mx) * i/(i+1.);
       *v22 += square(y[i] - *my) * i/(i+1.);
       *v12 += (x[i] - *mx) * (y[i] - *my) * i/(i+1.);
       *mx = (*mx * i + x[i])/(i+1.);
       *my = (*my * i + y[i])/(i+1.);
   }

   if (*v11>0.0 && *v22>0.0)  *r = *v12/sqrt(*v11 * *v22);
   else                       *r = -9;
   return(0);
}


int bubblesort (float x[], int n)
{
/* inefficient bubble sort */
   int i,j;
   float t=0;

   for(i=0;i<n;i++) {
      for(j=i;j<n;j++)
         if(x[j]<x[i]) { t = x[i]; x[i] = x[j]; x[j] = t; }
   }
   return (0);
}


int comparedouble (const void *a, const void *b)
{  
   double aa = *(double*)a, bb= *(double*)b;
   return (aa > bb ? 1 : (aa<bb ? -1 : 0));
}


int splitline (char line[], int fields[])
{
/* This finds out how many fields there are in the line, and marks the starting 
   positions of the fields.
   Fields are separated by spaces, and texts are allowed as well.
*/
   int lline=640000, i, nfields=0, InSpace=1;
   char *p=line;

   for(i=0; i<lline && *p && *p!='\n'; i++,p++) {
      if (isspace(*p))
         InSpace=1;
      else  {
         if(InSpace) {
            InSpace=0;
            fields[nfields++]=i;
            if(nfields>MAXNFIELDS) 
               puts("raise MAXNFIELDS?");
         }
      }
   }
   return(nfields);
}


int scanfile (FILE*fin, int *nrecords, int *nx, int *ReadHeader, char line[], int ifields[])
{
   int  i, lline=640000, nxline;

   for (*nrecords=0; ; ) {
      if (!fgets(line,lline,fin)) break;
      if(*nrecords==0 && strchr(line, '\n')==NULL)
         puts(" line too short or too long?");

      if(*nrecords==0) {
         for(i=0; i<lline && line[i]; i++)
            if(isalpha(line[i])) { 
               *ReadHeader=1; break; 
            }
      }
      nxline = splitline(line, ifields);
      if(nxline == 0)
         continue;
      if(*nrecords == 0)
         *nx = nxline;
      else if (*nx != nxline)  
         break;

      if(*nx>MAXNFIELDS) error2("raise MAXNFIELDS?");

      (*nrecords)++;
      /* printf("line # %3d:  %3d variables\n", *nrecords+1, nxline); */
   }
   rewind(fin);

   if(*ReadHeader) {
      fgets(line,lline,fin);
      splitline(line, ifields);
   }
   if(*ReadHeader)    
      (*nrecords) --;

   return(0);
}




#define MAXNF2D  5
#define SQRT5    2.2360679774997896964
#define Epanechnikov(t) ((0.75-0.15*(t)*(t))/SQRT5)
int splitline (char line[], int fields[]);

/* density1d and density2d need to be reworked to account for edge effects.
   October 2006
*/


int density1d (FILE* fout, double y[], int n, int nbin, double minx, 
               double gap, double h, double space[], int propternary)
{
/* This collects the histogram and uses kernel smoothing and adaptive kernel 
   smoothing to estimate the density.  The kernel is Epanechnikov.  The 
   histogram is collected into fobs, smoothed density into fE, and density 
   from adaptive kernel smoothing into fEA[].  
   Data y[] are sorted in increasing order before calling this routine.

   space[bin+n]
*/
   int adaptive=0, i,k, iL, nused;
   double *fobs=space, *lambda=fobs+nbin, fE, fEA, xt, d, G, alpha=0.5;
   double maxx=minx+gap*nbin, edge;
   char timestr[32];

   for(i=0; i<nbin; i++)  fobs[i]=0;
   for(k=0,i=0; k<n; k++) {
      for ( ; i<nbin-1; i++)
         if(y[k]<=minx+gap*(i+1)) break;
      fobs[i]+=1./n;
   }

   /* weights for adaptive smoothing */
   if(adaptive) {
      for(k=0;k<n;k++) lambda[k]=0;
      for(k=0,G=0,iL=0; k<n; k++) {
         xt=y[k];
         for (i=iL,nused=0; i<n; i++) {
            d=fabs(xt-y[i])/h;
            if(d<SQRT5) {
               nused++;
               lambda[k] += 1-0.2*d*d;  /* based on Epanechnikov kernel */
               /* lambda[k] += Epanechnikov(d)/(n*h); */
            }
            else if(nused==0)
               iL=i;
            else
               break;
         }
         G+=log(lambda[k]);
         if((k+1)%1000==0)
            printf("\r\tGetting weights: %2d/%d  %d terms  %s", k+1,n,nused,printtime(timestr));

      }
      G = exp(G/n);
      for (k=0; k<n; k++) lambda[k] = pow(lambda[k]/G, -alpha);
      if(n>1000) printf("\r");
   }

   /* smoothing and printing */
   for (k=0; k<nbin; k++) {
      xt=minx+gap*(k+0.5);
      for (i=0,fE=fEA=0; i<n; i++) {
         d=fabs(xt-y[i])/h;
         if(d>SQRT5) continue;
         edge = (y[i]-xt > xt-minx || xt-y[i]>maxx-xt ? 2 : 1);
         fE += edge*Epanechnikov(d)/(n*h);
         if(adaptive) {
            d/=lambda[i];
            fEA += edge*Epanechnikov(d)/(n*h*lambda[i]);
         }
      }
      if(!adaptive) fprintf(fout, "%.6f\t%.6f\t%.6f\n", xt, fobs[k], fE);
      else          fprintf(fout, "%.6f\t%.6f\t%.6f\t%.6f\n", xt, fobs[k], fE, fEA);
   }
   return(0);
}

int density2d (FILE* fout, double y1[], double y2[], int n, int nbin, 
               double minx1, double minx2, double gap1, double gap2, 
               double var[4], double h, double space[], int propternary)
{
/* This collects the histogram and uses kernel smoothing and adaptive kernel 
   smoothing to estimate the 2-D density.  The kernel is Epanechnikov.  The 
   histogram is collected into f, smoothed density into fE, and density 
   from adaptive kernel smoothing into fEA[].  
   Data y1 and y2 are not sorted, unlike the 1-D routine.

   alpha goes from 0 to 1, with 0 being equivalent to fixed width smoothing.
   var[] has the 2x2 variance matrix, which is copied into S[4] and inverted.

   space[nbin*nbin+n] for observed histogram f[nbin*nbin] and for lambda[n].
*/
   char timestr[32];
   int i,j,k;
   double *fO=space, *fE=fO+nbin*nbin, *fEA=fE+nbin*nbin, *lambda=fEA+nbin*nbin;
   double h2=h*h, c2d, a,b,c,d, S[4], detS, G, x1,x2, alpha=0.5;

   /* histogram */
   for(i=0; i<nbin*nbin; i++) 
      fO[i]=fE[i]=fEA[i]=0;
   for (i=0; i<n; i++) {
      for (j=0; j<nbin-1; j++) if(y1[i]<=minx1+gap1*(j+1)) break;
      for (k=0; k<nbin-1; k++) if(y2[i]<=minx2+gap2*(k+1)) break;
      fO[j*nbin+k] += 1./n;
   }

   xtoy(var,S,4);
   a=S[0]; b=c=S[1]; d=S[3]; detS=a*d-b*c;
   S[0]=d/detS;  S[1]=S[2]=-b/detS;  S[3]=a/detS;
   /* detS=1; S[0]=S[3]=1; S[1]=S[2]=0; */
   c2d = 2/(n*Pi*h*h*sqrt(detS));

   /* weights for adaptive kernel smoothing */
   for (k=0; k<n; k++) lambda[k]=0;
   for(k=0,G=0; k<n; k++) {
      x1 = y1[k];
      x2 = y2[k];
      for(i=0;i<n;i++) {
         a = x1-y1[i];
         b = x2-y2[i];
         d = (a*S[0]+b*S[1])*a + (a*S[1]+b*S[3])*b;
         d /= h2;
         if(d<1) lambda[k] += (1-d);
      }
      G += log(lambda[k]);
      if((k+1)%1000==0)
         printf("\r\tGetting weights: %2d/%d  %s", k+1,n,printtime(timestr));
   }
   G = exp(G/n);
   for(k=0; k<n; k++) lambda[k] = pow(lambda[k]/G, -alpha);
   for(k=0; k<n; k++) lambda[k] = 1/square(lambda[k]);   /* 1/lambda^2 */
   if(n>1000) printf("\r");

   /* smoothing and printing */
   puts("\t\tSmoothing and printing.");
   for(j=0; j<nbin; j++) {
      for(k=0; k<nbin; k++) {
         x1 = minx1 + gap1*(j+0.5);
         x2 = minx2 + gap2*(k+0.5);
         if(propternary && x1+x2>1)
            continue;
         for(i=0;i<n;i++) {
            a=x1-y1[i], b=x2-y2[i];
            d=(a*S[0]+b*S[1])*a + (a*S[1]+b*S[3])*b;
            d /= h2;
            if(d<1) fE[j*nbin+k] += (1-d);

            d *= lambda[i];
            if(d<1) fEA[j*nbin+k] += (1-d)*lambda[i];
         }
      }
   }
   for(i=0; i<nbin*nbin; i++) { fE[i]*=c2d; fEA[i]*=c2d; }

   if(propternary==2) {  /* symmetrize for ternary contour plots */
      for(j=0; j<nbin; j++) {
         for(k=0; k<=j; k++) {
            x1 = minx1 + gap1*(j+0.5);
            x2 = minx2 + gap2*(k+0.5);
            if(x1+x2>1) continue;
            fO[j*nbin+k]  = fO[k*nbin+j]  = (fO[j*nbin+k] + fO[k*nbin+j])/2;
            fE[j*nbin+k]  = fE[k*nbin+j]  = (fE[j*nbin+k] + fE[k*nbin+j])/2;
            fEA[j*nbin+k] = fEA[k*nbin+j] = (fEA[j*nbin+k] + fEA[k*nbin+j])/2;
         }
      }
   }

   for(j=0; j<nbin; j++) {
      for(k=0; k<nbin; k++) {
         x1 = minx1 + gap1*(j+0.5);
         x2 = minx2 + gap2*(k+0.5);
         if(!propternary || x1+x2<=1)
            fprintf(fout, "%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n", x1,x2, fO[j*nbin+k],fE[j*nbin+k],fEA[j*nbin+k]);
      }
   }
   
   return(0);
}



int DescriptiveStatistics (FILE *fout, char infile[], int nbin, int nrho, int propternary)
{
/* This routine reads n records (observations) each of p continuous variables,
   to calculate summary statistics such as the mean, SD, median, min, max
   of each variable, as well as the variance and correlation matrices.
   It also uses kernel density estimation to smooth the histogram for each
   variable, as well as calculating 2-D densities for selected variable pairs.
   The smoothing used the kerney estimator, with both fixed window size and 
   adaptive kernel smoothing using variable bandwiths.  The kernel function 
   is Epanechnikov.  For 2-D smoothing, Fukunaga's transform is used 
   (p.77 in B.W. Silverman 1986).

   The routine reads infile (p*2+3+nf2d) times:
      1:     to scan the file
      1:     to calculate min, max, mean
      1:     to calculate variance matrix
      p:     to sort each variable for median and percentiles
      p:     to do 1-D density smooth (this uses qsort a second time)
      nf2d:  to do 2-D density smooth

   Space requirement:
      x[p];    mean[p]; median[p]; minx[p]; maxx[p]; x005[p]; x995[p];
      x025[p]; x975[p]; x25[p];  x75[p];  var[p*p];  gap[p]; rho[p*nrho];  

   Each line in the data file has p variables, read into x[p], and the variable 
   to be sorted or processed is moved into y[].  The vector y[] contains the 
   data, f[] for histogram, and lambda[n] for adaptive kernel smoothing.   
   For 1-D, y[n*2+nbin*nbin] contains the data, f[nbin] for histogram, and 
   lambda[n] for adaptive smoothing.  
   For 2-D, y[n*3+nbin*nbin] contains the data (y[n*2], f[nbin*nbin] for 
   histogram, and lambda[n] for adaptive smoothing.  *space is pointed to y 
   after the data at the start of f[].

   Future work: Sorting data to avoid useless computation.
*/
   FILE *fin=gfopen(infile,"r");
   int  n, p, i,j,k, jj,kk;
   char *fmt=" %9.6f", *fmt1=" %9.1f", timestr[32];
   double *x, *mean, *median, *minx, *maxx, *x005,*x995,*x025,*x975,*x25,*x75,*var, t;
   double *Tint;
   double h, *y, *rho, *gap, *space, a,b,c,d, v2d[4];
   int nf2d=0, ivar_f2d[MAXNF2D][2]={{5,6},{0,2}}, k2d;

   int  lline=320000, ifields[MAXNFIELDS], Ignore1stColumn=1, ReadHeader=0;
   char line[320000];
   char varstr[MAXNFIELDS][32]={""};

   scanfile(fin, &n, &p, &ReadHeader, line, ifields);
   if(ReadHeader)
      for(i=0; i<p; i++) sscanf(line+ifields[i], "%s", varstr[i]);

   x = (double*)malloc((p*13+p*p + p*nrho)*sizeof(double));
   if (x==NULL) error2("oom DescriptiveStatistics.");
   for(j=0;j<p*13+p*p + p*nrho; j++) x[j]=0;
   mean=x+p; median=mean+p; minx=median+p; maxx=minx+p; 
   x005=maxx+p; x995=x005+p; x025=x995+p; x975=x025+p; x25=x975+p; x75=x25+p;
   var=x75+p;   gap=var+p*p; rho=gap+p;
   Tint=rho+p*nrho;

   /*
   if(p>1) {
      printf("\nGreat offer!  I can smooth a few 2-D densities for free.  How many do you want? ");
      scanf("%d", &nf2d);
   }
   */

   if(nf2d>MAXNF2D) error2("I don't want to do that many!");
   for(i=0; i<nf2d; i++) {
      printf("pair #%d (e.g., type  1 3  to use variables #1 and #3)? ",i+1);
      scanf("%d%d", &ivar_f2d[i][0], &ivar_f2d[i][1]);
      ivar_f2d[i][0]--;
      ivar_f2d[i][1]--;
   }

   /* min, max, and mean */
   printf("\n(1) collecting min, max, and mean");
   for(i=0; i<n; i++) {
      for(j=0;j<p;j++) 
         fscanf(fin,"%lf", &x[j]);
      if(i==0)
         for(j=Ignore1stColumn;j<p;j++) minx[j]=maxx[j]=x[j];
      else {
         for(j=Ignore1stColumn;j<p;j++) 
            if      (minx[j]>x[j]) minx[j]=x[j];
            else if (maxx[j]<x[j]) maxx[j]=x[j];
      }
      for(j=Ignore1stColumn; j<p; j++) mean[j]+=x[j]/n;
   }

   /* variance-covariance matrix */
   printf(" %10s\n(2) variance-covariance matrix", printtime(timestr));
   rewind(fin);
   if(ReadHeader) fgets(line, lline, fin);
   for (i=0; i<n; i++) {
      for(j=0;j<p;j++) 
         fscanf(fin,"%lf", &x[j]);
      for(j=Ignore1stColumn; j<p; j++) for(k=Ignore1stColumn; k<=j; k++)
         var[j*p+k] += (x[j]-mean[j])*(x[k]-mean[k])/n;
   }
   for(j=Ignore1stColumn; j<p; j++) for(k=Ignore1stColumn; k<j; k++)
      var[k*p+j]=var[j*p+k];

   /* sorting to get median and percentiles */
   printf("%10s\n(3) median, percentiles & serial correlation",printtime(timestr));
   y=(double*)malloc((n*(2+(nf2d>0))+nbin*nbin*3)*sizeof(double));
   if(y==NULL) { printf("not enough mem for %d variables\n",n); exit(-1); }
   space=y+(1+(nf2d>0))*n;  /* space[] points to y after the data */
   for(jj=Ignore1stColumn; jj<p; jj++) {
      rewind(fin);
      if(ReadHeader) fgets(line, lline, fin);

      for(i=0;i<n;i++) {
         for(j=0; j<p; j++) fscanf(fin,"%lf", &x[j]);
         y[i] = x[jj];
      }

      for(i=0,Tint[jj]=1; i<nrho; i++) {
         correl(y, y+1+i, n-1-i, &a, &b, &c, &d, &x[0], &rho[jj*nrho+i]);
         if(rho[jj*nrho+i]<0) break;
         Tint[jj] += rho[jj*nrho+i]*2;
      }

      qsort(y, (size_t)n, sizeof(double), comparedouble);
      if(n%2==0)  median[jj]=(y[n/2]+y[n/2+1])/2;
      else        median[jj]=y[(n+1)/2];
      x005[jj] = y[(int)(n*.005)];  x995[jj] = y[(int)(n*.995)];
      x025[jj] = y[(int)(n*.025)];  x975[jj] = y[(int)(n*.975)];
      x25[jj]  = y[(int)(n*.25)];    x75[jj] = y[(int)(n*.75)];
   }

   fprintf(fout,"\n(A) Descriptive statistics\n\n       ");
   for (j=Ignore1stColumn; j<p; j++) fprintf(fout,"   %s", varstr[j]);
   fprintf(fout,"\nmean    ");  for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,mean[j]);
   fprintf(fout,"\nmedian  ");  for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,median[j]);
   fprintf(fout,"\nS.D.    ");  for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,sqrt(var[j*p+j]));
   fprintf(fout,"\nmin     ");  for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,minx[j]);
   fprintf(fout,"\nmax     ");  for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,maxx[j]);
   fprintf(fout,"\n2.5%%    "); for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,x025[j]);
   fprintf(fout,"\n97.5%%   "); for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt,x975[j]);
   fprintf(fout,"\nESS*    ");  for(j=Ignore1stColumn;j<p;j++) fprintf(fout,fmt1,n/Tint[j]);
   fflush(fout);

   /*
   FPN(F0); FPN(F0);
   for(j=Ignore1stColumn; j<p; j++) printf("%.3f(%.3f,%.3f)\n",mean[j], x025[j],x975[j]);
   free(x); free(y); return(0);
   */


   fprintf(fout, "\n\n(B) Matrix of correlation coefficients between variables\n\n");
   for (j=Ignore1stColumn; j<p; j++,fputc('\n',fout)) {
      for (k=Ignore1stColumn; k<=j; k++) {
         t = sqrt(var[j*p+j]*var[k*p+k]);
         fprintf(fout, fmt, (t>0?var[j*p+k]/t:-9));
      }
   }

   fprintf(fout, "\n\n(C) Serial correlation coefficients within variables\n");
   fprintf(fout, "\nlag  variables ...\n\n");
   for(i=0; i<nrho; i++,FPN(fout)) {
      fprintf(fout, "%d", i+1);
      for(j=Ignore1stColumn; j<p; j++)
         fprintf(fout, "\t%.6f", rho[j*nrho+i]);
   }
   fflush(fout);

/*
return(0);
*/
   printf(" %10s\n(4) Histograms and 1-D densities\n",printtime(timestr));
   fprintf(fout, "\n(D) Histograms and 1-D densities\n");
   for(jj=Ignore1stColumn; jj<p; jj++) {
      rewind(fin);
      if(ReadHeader) fgets(line, lline, fin);

      for(i=0;i<n;i++) {
         for(j=0;j<p;j++) 
            fscanf(fin,"%lf", &x[j]);
         y[i]=x[jj];
      }

      fprintf(fout, "\n%s\nmidvalue  freq    f(x)\n\n", varstr[jj]);
      /* steplength for 1-d kernel density estimation, from Eq 3.24, 3.30, 3.31 */

      if(propternary) {
         minx[jj]=0;  maxx[jj]=1;
      }
      gap[jj]=(maxx[jj]-minx[jj])/nbin;

      d = sqrt(var[jj*p+jj]);
      h = min2(d,(x75[jj]-x25[jj])/1.34) * 0.9*pow((double)n,-0.2);
      qsort(y, (size_t)n, sizeof(double), comparedouble);
      density1d(fout, y, n, nbin, minx[jj], gap[jj], h, space, propternary);

      printf("    variable %2d/%d (%s): %s%30s\r", jj+1,p,varstr[jj], printtime(timestr),"");
   }

   /* 2-D histogram and density */
   if(nf2d<=0) return(0);
   h = 2.4*pow((double)n, -1/6.0);
   printf("(5) 2-d histogram and density (h = %.6g)\n",h);
   fprintf(fout, "\n(E) 2-D histogram and density\n");

   for(k2d=0; k2d<nf2d; k2d++) {
      jj=min2(ivar_f2d[k2d][0],ivar_f2d[k2d][1]);
      kk=max2(ivar_f2d[k2d][0],ivar_f2d[k2d][1]);

      printf("    2-D smoothing for variables %s & %s\n", varstr[jj], varstr[kk]);
      fprintf(fout, "\n%s\t%s\tfreq\tdensity\n\n",  varstr[jj], varstr[kk]);
      rewind(fin);
      if(ReadHeader) fgets(line, lline, fin);

      for (i=0; i<n; i++) {
         for(j=0;j<p;j++)
            fscanf(fin,"%lf", &x[j]);
         y[i] = x[jj]; y[n+i] = x[kk];
      }

      v2d[0]=var[jj*p+jj];  
      v2d[1]=v2d[2]=var[jj*p+kk];  
      v2d[3]=var[kk*p+kk];
      density2d (fout, y, y+n, n, nbin, minx[jj], minx[kk], gap[jj], gap[kk], v2d, 
         h, space, propternary);
   }
   free(x); free(y);
   printf("\n%10s used\n", printtime(timestr));
   return(0);
}


#undef MAXNFIELDS



/******************************************
          Minimization
*******************************************/

int H_end (double x0[], double x1[], double f0, double f1,
    double e1, double e2, int n)
/*   Himmelblau termination rule.   return 1 for stop, 0 otherwise.
*/
{
   double r;
   if((r=norm(x0,n))<e2)
      r=1;
   r*=e1;
   if(distance(x1,x0,n)>=r)
      return(0);
   r=fabs(f0);  if(r<e2) r=1;     
   r*=e1;
   if(fabs(f1-f0)>=r) 
      return(0);
   return (1);
}

int AlwaysCenter=0;
double Small_Diff=1e-6;  /* reasonable values 1e-5, 1e-7 */

int gradient (int n, double x[], double f0, double g[], 
    double (*fun)(double x[],int n), double space[], int Central)
{
/*  f0 = fun(x) is always given.
*/
   int i,j;
   double *x0=space, *x1=space+n, eh0=Small_Diff, eh;  /* 1e-7 */

   if (Central) {
      for(i=0; i<n; i++)  {
         for(j=0; j<n; j++) 
            x0[j] = x1[j] = x[j];
         eh = pow(eh0*(fabs(x[i])+1), 0.67);
         x0[i] -= eh; x1[i] += eh;
         g[i] = ((*fun)(x1,n) - (*fun)(x0,n))/(eh*2.0);
      }
   }
   else {
      for(i=0; i<n; i++)  {
         for(j=0; j<n; j++)
            x1[j]=x[j];
         eh=eh0*(fabs(x[i])+1);
         x1[i]+=eh;
         g[i] = ((*fun)(x1,n)-f0)/eh;
      }
   }
   return(0);
}

int Hessian (int n, double x[], double f0, double g[], double H[],
    double (*fun)(double x[], int n), double space[])
{
/* Hessian matrix H[n*n] by the central difference method.
   # of function calls: 2*n*n
*/
   int i,j,k;
   double *x1=space, *h=x1+n, h0=Small_Diff*2; /* h0=1e-5 or 1e-6 */ 
   double fpp,fmm,fpm,fmp;  /* p:+  m:-  */

   for(k=0; k<n; k++) {
      h[k] = h0*(1 + fabs(x[k]));
      if(h[k] > x[k]) 
         printf("Hessian warning: x[%d] = %8.5g < h = %8.5g.\n", k+1, x[k],h[k]);
   }
   for(i=0; i<n; i++) {
      for (j=i; j<n; j++)  {
         for(k=0; k<n; k++) x1[k] = x[k];
         x1[i] += h[i];    x1[j] += h[j];
         fpp = (*fun)(x1,n);                  /* (+hi, +hj) */
         x1[i] -= h[i]*2;  x1[j] -= h[j]*2;
         fmm = (*fun)(x1,n);                  /* (-hi, -hj) */
         if (i==j)  {
             H[i*n+i] = (fpp+fmm-2*f0)/(4*h[i]*h[i]);
             g[i] = (fpp - fmm)/(h[i]*4);
         }
         else {
            x1[i] += 2*h[i];                     fpm = (*fun)(x1,n);  /* (+hi, -hj) */
            x1[i] -= 2*h[i];   x1[j] += 2*h[j];  fmp = (*fun)(x1,n);  /* (-hi, +hj) */
            H[i*n+j] = H[j*n+i] = (fpp+fmm-fpm-fmp)/(4*h[i]*h[j]);
         }
      }
   }
   return(0);
}

int jacobi_gradient (double x[], double J[],
    int (*fun) (double x[], double y[], int nx, int ny),
    double space[], int nx, int ny);

int jacobi_gradient (double x[], double J[],
    int (*fun) (double x[], double y[], int nx, int ny),
    double space[], int nx, int ny)
{
/* Jacobi by central difference method
   J[ny][nx]  space[2*nx+2*ny]
*/
   int i,j;
   double *x0=space, *x1=space+nx, *y0=x1+nx, *y1=y0+ny, eh0=1.0e-4, eh;

   FOR (i,nx)  {
      FOR (j, nx)  x0[j]=x1[j]=x[j];
      eh=(x[i]==0.0) ? eh0 : fabs(x[i])*eh0;
      x0[i] -= eh; x1[i] += eh;
      (*fun) (x0, y0, nx, ny);
      (*fun) (x1, y1, nx, ny);
      FOR (j,ny) J[j*nx+i] = (y1[j]-y0[j])/(eh*2.0);
   }
   return(0);
}

int nls2 (FILE *fout, double *sx, double * x0, int nx,
      int (*fun)(double x[], double y[], int nx, int ny),
      int (*jacobi)(double x[], double J[], int nx, int ny),
      int (*testx) (double x[], int nx),
      int ny, double e)
{
/* non-linear least squares: minimization of s=f(x)^2.
   by the damped NLS, or Levenberg-Marguard-Morrison(LMM) method.
   x[n] C[n,n+1] J[ny,n] y[ny] iworker[n]
*/
   int n=nx, ii, i, i1, j, istate=0, increase=0, maxround=500,sspace;
   double s0=0.0, s=0.0, t;
   double v=0.0, vmax=1.0/e, bigger=2.5, smaller=0.75;
       /* v : Marguardt factor, suggested factors in SSL II (1.5,0.5)  */
   double *x, *g, *p, *C, *J, *y, *space, *space_J;

   sspace=(n*(n+4+ny)+ny+2*(n+ny))*sizeof(double);
   if((space=(double*)malloc(sspace))==NULL) error2("oom in nls2");
   zero (space, n*(n+4+ny)+ny);
   x=space;  g=x+n;  p=g+n;  C=p+n;  J=C+n*(n+1);  y=J+ny*n; space_J=y+ny;

   (*fun) (x0, y, n, ny);
   for (i=0, s0=0; i<ny; i++)   s0 += y[i]*y[i];

   FOR (ii, maxround)  {
      increase=0;
      if (jacobi)  (*jacobi) (x0, J, n, ny);
      else         jacobi_gradient (x0, J, fun, space_J, n, ny);

      if (ii == 0) {
         for (j=0,t=0; j<ny*n; j++)
            t += J[j] * J[j];
         v = sqrt (t) / (double) (ny*n);     /*  v = 0.0;  */
      }

      FOR (i,n)  {
         for (j=0,t=0; j<ny; j++)  t += J[j*n+i] * y[j];
         g[i] = 2*t;
         C[i*(n+1)+n] = -t;
         for (j=0; j<=i; j++) {
            for (i1=0,t=0; i1<ny; i1++)  t += J[i1*n+i] * J[i1*n+j];
            C[i*(n+1)+j] = C[j*(n+1)+i] = t;
         }
         C[i*(n+1)+i] += v*v;
      }

      if (matinv( C,n,n+1, y+ny) == -1)  {
         v *= bigger;
         continue;
      }
      FOR (i,n)   p[i] = C[i*(n+1)+n];

      t = bound (n, x0, p, x, testx);
      if (t>1) t=1;
      FOR (i,n) x[i] = x0[i] + t * p[i];

      (*fun) (x, y, n, ny);
      for (i=0,s=0; i<ny; i++)  s += y[i]*y[i];

      if (fout) {
         fprintf (fout,"\n%4d  %10.6f",ii+1,s);
         /* FOR(i,n) fprintf(fout,"%8.4f",x[i]); */
      }
      if (s0<s) increase = 1;
      if (H_end(x0,x,s0,s,e,e,n)) break;
      if (increase)  {  v*=bigger;  if (v>vmax)  { istate=1; break; } }
      else    {         v*=smaller; xtoy (x, x0, n); s0=s; }
   }                    /* ii, maxround */
   if (increase)   *sx=s0;
   else       {    *sx=s;    xtoy(x, x0, n);   }
   if (ii == maxround) istate=-1;
   free (space);
   return (istate);
}



double bound (int nx, double x0[], double p[], double x[],
       int(*testx)(double x[], int nx))
{
/* find largest t so that x[]=x0[]+t*p[] is still acceptable.
   for bounded minimization, p is possibly changed in this function
   using testx()
*/
   int i, nd=0;
   double factor=20, by=1, small=1e-8;  /* small=(SIZEp>1?1e-7:1e-8) */ 

   xtoy (x0, x, nx);
   FOR (i,nx)  {
      x[i]=x0[i]+small*p[i];
      if ((*testx) (x, nx))  {  p[i]=0.0;  nd++; }
      x[i]=x0[i];
   }
   if (nd==nx) { if (noisy) puts ("bound:no move.."); return (0); }

   for (by=0.75; ; ) {
      FOR (i,nx)  x[i]=x0[i]+factor*p[i];
      if ((*testx)(x,nx)==0)  break;
      factor *= by;
   }
   return(factor);
}




double LineSearch (double(*fun)(double x),double *f,double *x0,double xb[2],double step, double e)
{
/* linear search using quadratic interpolation 

   From Wolfe M. A.  1978.  Numerical methods for unconstrained
   optimization: An introduction.  Van Nostrand Reinhold Company, New York.
   pp. 62-73.
   step is used to find the bracket (a1,a2,a3)

   This is the same routine as LineSearch2(), but I have not got time 
   to test and improve it properly.  Ziheng note, September, 2002
*/
   int ii=0, maxround=100, i;
   double factor=2, step1, percentUse=0;
   double a0,a1,a2,a3,a4=-1,a5,a6, f0,f1,f2,f3,f4=-1,f5,f6;

/* find a bracket (a1,a2,a3) with function values (f1,f2,f3)
   so that a1<a2<a3 and f2<f1 and f2<f3
*/

   if(step<=0) return(*x0);
   a0=a1=a2=a3=f0=f1=f2=f3=-1;
   if(*x0<xb[0]||*x0>xb[1]) 
      error2("err LineSearch: x0 out of range");
   f2=f0=fun(a2=a0=*x0);
   step1=min2(step,(a0-xb[0])/4);
   step1=max2(step1,e);
   for(i=0,a1=a0,f1=f0; ; i++) {
      a1-=(step1*=factor); 
      if(a1>xb[0]) {
         f1=fun(a1);
         if(f1>f2)  break;
         else {
            a3=a2; f3=f2; a2=a1; f2=f1;
         }
      }
      else {
         a1=xb[0];  f1=fun(a1);
         if(f1<=f2) { a2=a1; f2=f1; }
         break;
      }

      /* if(noisy>2) printf("\ta = %.6f\tf = %.6f %5d\n", a2, f2, NFunCall);
      */

   }

   if(i==0) { /* *x0 is the best point during the previous search */
      step1=min2(step,(xb[1]-a0)/4);
      for(i=0,a3=a2,f3=f2; ; i++) {
         a3+=(step1*=factor); 
         if(a3<xb[1]) {
            f3=fun(a3);
            if(f3>f2)  break;
            else 
               { a1=a2; f1=f2; a2=a3; f2=f3; }
         }
         else {
            a3=xb[1];  f3=fun(a3);
            if(f3<f2) { a2=a3; f2=f3; }
            break;
         }

	 if(noisy>2) printf("\ta = %.6f\tf = %.6f %5d\n", a3, f3, NFunCall);

      }
   }

   /* iteration by quadratic interpolation, fig 2.2.9-10 (pp 71-71) */
   for (ii=0; ii<maxround; ii++) {
      /* a4 is the minimum from the parabola over (a1,a2,a3)  */

      if (a1>a2+1e-99 || a3<a2-1e-99 || f2>f1+1e-99 || f2>f3+1e-99) /* for linux */
         { printf("\npoints out of order (ii=%d)!",ii+1); break; }

      a4 = (a2-a3)*f1+(a3-a1)*f2+(a1-a2)*f3;
      if (fabs(a4)>1e-100)
         a4=((a2*a2-a3*a3)*f1+(a3*a3-a1*a1)*f2+(a1*a1-a2*a2)*f3)/(2*a4);
      if (a4>a3 || a4<a1)  a4=(a1+a2)/2;  /* out of range */
      else                 percentUse++;
      f4=fun(a4);

      /*
      if (noisy>2) printf("\ta = %.6f\tf = %.6f %5d\n", a4, f4, NFunCall);
      */

      if (fabs(f2-f4)*(1+fabs(f2))<=e && fabs(a2-a4)*(1+fabs(a2))<=e)  break;

      if (a1<=a4 && a4<=a2) {    /* fig 2.2.10 */
         if (fabs(a2-a4)>.2*fabs(a1-a2)) {
            if (f1>=f4 && f4<=f2) { a3=a2; a2=a4;  f3=f2; f2=f4; }
            else { a1=a4; f1=f4; }
         }
         else {
            if (f4>f2) {
               a5=(a2+a3)/2; f5=fun(a5);
               if (f5>f2) { a1=a4; a3=a5;  f1=f4; f3=f5; }
               else       { a1=a2; a2=a5;  f1=f2; f2=f5; }
            }
            else {
               a5=(a1+a4)/2; f5=fun(a5);
               if (f5>=f4 && f4<=f2)
                  { a3=a2; a2=a4; a1=a5;  f3=f2; f2=f4; f1=f5; }
               else {
                  a6=(a1+a5)/2; f6=fun(a6);
                  if (f6>f5)
                       { a1=a6; a2=a5; a3=a4;  f1=f6; f2=f5; f3=f4; }
                  else { a2=a6; a3=a5;  f2=f6; f3=f5; }
               }
            }
         }
      }
      else {                     /* fig 2.2.9 */
         if (fabs(a2-a4)>.2*fabs(a2-a3)) {
            if (f2>=f4 && f4<=f3) { a1=a2; a2=a4;  f1=f2; f2=f4; }
            else                  { a3=a4; f3=f4; }
         }
         else {
            if (f4>f2) {
               a5=(a1+a2)/2; f5=fun(a5);
               if (f5>f2) { a1=a5; a3=a4;  f1=f5; f3=f4; }
               else       { a3=a2; a2=a5;  f3=f2; f2=f5; }
            }
            else {
               a5=(a3+a4)/2; f5=fun(a5);
               if (f2>=f4 && f4<=f5)
                  { a1=a2; a2=a4; a3=a5;  f1=f2; f2=f4; f3=f5; }
               else {
                  a6=(a3+a5)/2; f6=fun(a6);
                  if (f6>f5)
                      { a1=a4; a2=a5; a3=a6;  f1=f4; f2=f5; f3=f6; }
                  else { a1=a5; a2=a6;  f1=f5; f2=f6; }
               }
            }
         }
      }
   }   /*  for (ii) */
   if (f2<=f4)  { *f=f2; a4=a2; }
   else           *f=f4;

   return (*x0=(a4+a2)/2);
}



double fun_LineSearch (double t, double (*fun)(double x[],int n), 
       double x0[], double p[], double x[], int n);

double fun_LineSearch (double t, double (*fun)(double x[],int n), 
       double x0[], double p[], double x[], int n)
{  int i;   FOR (i,n) x[i]=x0[i] + t*p[i];   return( (*fun)(x, n) ); }



double LineSearch2 (double(*fun)(double x[],int n), double *f, double x0[], 
       double p[], double step, double limit, double e, double space[], int n)
{
/* linear search using quadratic interpolation 
   from x0[] in the direction of p[],
                x = x0 + a*p        a ~(0,limit)
   returns (a).    *f: f(x0) for input and f(x) for output

   x0[n] x[n] p[n] space[n]

   adapted from Wolfe M. A.  1978.  Numerical methods for unconstrained
   optimization: An introduction.  Van Nostrand Reinhold Company, New York.
   pp. 62-73.
   step is used to find the bracket and is increased or reduced as necessary, 
   and is not terribly important.
*/
   int ii=0, maxround=10, status, i, nsymb=0;
   double *x=space, factor=4, small=1e-10, smallgapa=0.2;
   double a0,a1,a2,a3,a4=-1,a5,a6, f0,f1,f2,f3,f4=-1,f5,f6;

/* look for bracket (a1, a2, a3) with function values (f1, f2, f3)
   step length step given, and only in the direction a>=0
*/

   if (noisy>2)
      printf ("\n%3d h-m-p %7.4f %6.4f %8.4f ",Iround+1,step,limit,norm(p,n));

   if (step<=0 || limit<small || step>=limit) {
      if (noisy>2) 
         printf ("\nh-m-p:%20.8e%20.8e%20.8e %12.6f\n",step,limit,norm(p,n),*f);
      return (0);
   }
   a0=a1=0; f1=f0=*f;
   a2=a0+step; f2=fun_LineSearch(a2, fun,x0,p,x,n);
   if (f2>f1) {  /* reduce step length so the algorithm is decreasing */
      for (; ;) {
         step/=factor;
         if (step<small) return (0);
         a3=a2;    f3=f2;
         a2=a0+step;  f2=fun_LineSearch(a2, fun,x0,p,x,n);
         if (f2<=f1) break;
         if(!PAML_RELEASE && noisy>2) { printf("-"); nsymb++; }
      }
   }
   else {       /* step length is too small? */
      for (; ;) {
         step*=factor;
         if (step>limit) step=limit;
         a3=a0+step;  f3=fun_LineSearch(a3, fun,x0,p,x,n);
         if (f3>=f2) break;

         if(!PAML_RELEASE && noisy>2) { printf("+"); nsymb++; }
         a1=a2; f1=f2;    a2=a3; f2=f3;
         if (step>=limit) {
            if(!PAML_RELEASE && noisy>2) for(; nsymb<5; nsymb++) printf(" ");
            if (noisy>2) printf(" %12.6f%3c %6.4f %5d", *f=f3, 'm', a3, NFunCall);
            *f=f3; return(a3);
         }
      }
   }

   /* iteration by quadratic interpolation, fig 2.2.9-10 (pp 71-71) */
   for (ii=0; ii<maxround; ii++) {
      /* a4 is the minimum from the parabola over (a1,a2,a3)  */
      a4 = (a2-a3)*f1+(a3-a1)*f2+(a1-a2)*f3;
      if(fabs(a4)>1e-100) 
         a4 = ((a2*a2-a3*a3)*f1+(a3*a3-a1*a1)*f2+(a1*a1-a2*a2)*f3)/(2*a4);
      if (a4>a3 || a4<a1) {   /* out of range */
         a4=(a1+a2)/2;
         status='N';
      }
      else {
         if((a4<=a2 && a2-a4>smallgapa*(a2-a1)) || (a4>a2 && a4-a2>smallgapa*(a3-a2)))
            status='Y';
         else 
            status='C';
      }
      f4 = fun_LineSearch(a4, fun,x0,p,x,n);
      if(!PAML_RELEASE && noisy>2) putchar(status);
      if (fabs(f2-f4)<e*(1+fabs(f2))) {
         if(!PAML_RELEASE && noisy>2) 
            for(nsymb+=ii+1; nsymb<5; nsymb++) printf(" ");
         break;
      }

      /* possible multiple local optima during line search */
      if(!PAML_RELEASE  && noisy>2 && ((a4<a2&&f4>f1) || (a4>a2&&f4>f3))) {
         printf("\n\na %12.6f %12.6f %12.6f %12.6f",   a1,a2,a3,a4);
         printf(  "\nf %12.6f %12.6f %12.6f %12.6f\n", f1,f2,f3,f4);

         for(a5=a1; a5<=a3; a5+=(a3-a1)/20) {
            printf("\t%.6e ",a5);
            if(n<5) FOR(i,n) printf("\t%.6f",x0[i] + a5*p[i]);
            printf("\t%.6f\n", fun_LineSearch(a5, fun,x0,p,x,n));
         }
         puts("Linesearch2 a4: multiple optima?");
      }
      if (a4<=a2) {    /* fig 2.2.10 */
         if (a2-a4>smallgapa*(a2-a1)) {
            if (f4<=f2) { a3=a2; a2=a4;  f3=f2; f2=f4; }
            else        { a1=a4; f1=f4; }
         }
         else {
            if (f4>f2) {
               a5=(a2+a3)/2; f5=fun_LineSearch(a5, fun,x0,p,x,n);
               if (f5>f2) { a1=a4; a3=a5;  f1=f4; f3=f5; }
               else       { a1=a2; a2=a5;  f1=f2; f2=f5; }
            }
            else {
               a5=(a1+a4)/2; f5=fun_LineSearch(a5, fun,x0,p,x,n);
               if (f5>=f4)
                  { a3=a2; a2=a4; a1=a5;  f3=f2; f2=f4; f1=f5; }
               else {
                  a6=(a1+a5)/2; f6=fun_LineSearch(a6, fun,x0,p,x,n);
                  if (f6>f5)
                       { a1=a6; a2=a5; a3=a4;  f1=f6; f2=f5; f3=f4; }
                  else { a2=a6; a3=a5; f2=f6; f3=f5; }
               }
            }
         }
      }
      else {                     /* fig 2.2.9 */
         if (a4-a2>smallgapa*(a3-a2)) {
            if (f2>=f4) { a1=a2; a2=a4;  f1=f2; f2=f4; }
            else        { a3=a4; f3=f4; }
         }
         else {
            if (f4>f2) {
               a5=(a1+a2)/2; f5=fun_LineSearch(a5, fun,x0,p,x,n);
               if (f5>f2) { a1=a5; a3=a4;  f1=f5; f3=f4; }
               else       { a3=a2; a2=a5;  f3=f2; f2=f5; }
            }
            else {
               a5=(a3+a4)/2; f5=fun_LineSearch(a5, fun,x0,p,x,n);
               if (f5>=f4)
                  { a1=a2; a2=a4; a3=a5;  f1=f2; f2=f4; f3=f5; }
               else {
                  a6=(a3+a5)/2; f6=fun_LineSearch(a6, fun,x0,p,x,n);
                  if (f6>f5)
                      { a1=a4; a2=a5; a3=a6;  f1=f4; f2=f5; f3=f6; }
                  else { a1=a5; a2=a6;  f1=f5; f2=f6; }
               }
            }
         }
      }
   }

   if (f2>f0 && f4>f0)  a4=0;
   if (f2<=f4)  { *f=f2; a4=a2; }
   else         *f=f4;
   if(noisy>2) printf(" %12.6f%3d %6.4f %5d", *f, ii, a4, NFunCall);

   return (a4);
}




#define Safeguard_Newton


int Newton (FILE *fout, double *f, double (* fun)(double x[], int n),
    int (* ddfun) (double x[], double *fx, double dx[], double ddx[], int n),
    int (*testx) (double x[], int n),
    double x0[], double space[], double e, int n)
{
   int i,j, maxround=500;
   double f0=1e40, small=1e-10, h, SIZEp, t, *H, *x, *g, *p, *tv;

   H=space,  x=H+n*n;   g=x+n;   p=g+n, tv=p+n;

   printf ("\n\nIterating by Newton\tnp:%6d\nInitial:", n);
   FOR (i,n) printf ("%8.4f", x0[i]);       FPN (F0);
   if (fout) fprintf (fout, "\n\nNewton\tnp:%6d\n", n);
   if (testx (x0, n)) error2("Newton..invalid initials.");
   FOR (Iround, maxround) {
       if (ddfun)
           (*ddfun) (x0, f, g, H, n);
       else  {
           *f = (*fun)(x0, n);
           Hessian (n, x0, *f, g, H, fun, tv);
       }
       matinv(H, n, n, tv);
       FOR (i,n) for (j=0,p[i]=0; j<n; j++)  p[i]-=H[i*n+j]*g[j];

       h=bound (n, x0, p, tv, testx);
       t=min2(h,1);
       SIZEp=norm(p,n);

#ifdef Safeguard_Newton
       if (SIZEp>4) {
           while (t>small) {
               FOR (i,n)  x[i]=x0[i]+t*p[i];
               if ((*f=fun(x,n)) < f0) break;
               else t/=2;
           }
       }
       if (t<small) t=min2(h, .5);
#endif

       FOR (i,n)  x[i]=x0[i]+t*p[i];
       if (noisy>2) {
            printf ("\n%3d h:%7.4f %12.6f  x", Iround+1, SIZEp, *f);
            FOR (i,n) printf ("%7.4f  ", x0[i]);
       }
       if (fout) {
            fprintf (fout, "\n%3d h:%7.4f%12.6f  x", Iround+1, SIZEp, *f);
            FOR (i,n) fprintf (fout, "%7.4f  ", x0[i]);
            fflush(fout);
       }
       if ((h=norm(x0,n))<e)  h=1;
       if (SIZEp<0.01 && distance(x,x0,n)<h*e) break;

       f0=*f;
       xtoy (x,x0,n);
    }
    xtoy (x, x0, n);    *f=fun(x0, n);

    if (Iround==maxround) return(-1);
    return(0);
}


int gradientB (int n, double x[], double f0, double g[], 
    double (*fun)(double x[],int n), double space[], int xmark[]);

extern int noisy, Iround;
extern double SIZEp;

int gradientB (int n, double x[], double f0, double g[], 
    double (*fun)(double x[],int n), double space[], int xmark[])
{
/* f0=fun(x) is always provided.
   xmark=0: central; 1: upper; -1: down
*/
   int i,j;
   double *x0=space, *x1=space+n, eh0=Small_Diff, eh;  /* eh0=1e-6 || 1e-7 */

   FOR(i,n) {
      eh=eh0*(fabs(x[i])+1);
      if (xmark[i]==0 && (AlwaysCenter || SIZEp<1)) {   /* central */
         FOR (j, n)  x0[j]=x1[j]=x[j];
         eh=pow(eh,.67);  x0[i]-=eh; x1[i]+=eh;
         g[i]=((*fun)(x1,n)-(*fun)(x0,n))/(eh*2.0);
      }
      else  {                         /* forward or backward */
         FOR (j, n)  x1[j]=x[j];
         if (xmark[i]) eh*=-xmark[i];
         x1[i] += eh;
         g[i]=((*fun)(x1,n)-f0)/eh;
      }
   }
   return(0);
}


#define BFGS
/*
#define SR1
#define DFP
*/

extern FILE *frst;

int ming2 (FILE *fout, double *f, double (*fun)(double x[], int n),
    int (*dfun)(double x[], double *f, double dx[], int n),
    double x[], double xb[][2], double space[], double e, int n)
{
/* n-variate minimization with bounds using the BFGS algorithm
     g0[n] g[n] p[n] x0[n] y[n] s[n] z[n] H[n*n] C[n*n] tv[2*n]
     xmark[n],ix[n]
   Size of space should be (check carefully?)
      #define spaceming2(n) ((n)*((n)*2+9+2)*sizeof(double))
   nfree: # free variables
   xmark[i]=0 for inside space; -1 for lower boundary; 1 for upper boundary.
   x[] has initial values at input and returns the estimates in return.
   ix[i] specifies the i-th free parameter

*/
   int i,j, i1,i2,it, maxround=10000, fail=0, *xmark, *ix, nfree;
   int Ngoodtimes=2, goodtimes=0;
   double small=1.e-30, sizep0=0;     /* small value for checking |w|=0 */
   double f0, *g0, *g, *p, *x0, *y, *s, *z, *H, *C, *tv;
   double w,v, alpha, am, h, maxstep=8;

   if(n==0) return(0);
   g0=space;   g=g0+n;  p=g+n;   x0=p+n;
   y=x0+n;     s=y+n;   z=s+n;   H=z+n;  C=H+n*n, tv=C+n*n;
   xmark=(int*)(tv+2*n);  ix=xmark+n;

   for(i=0; i<n; i++)  { xmark[i]=0; ix[i]=i; }
   for(i=0,nfree=0;i<n;i++) {
      if(x[i]<=xb[i][0]) { x[i]=xb[i][0]; xmark[i]=-1; continue; }
      if(x[i]>=xb[i][1]) { x[i]=xb[i][1]; xmark[i]= 1; continue; }
      ix[nfree++]=i;
   }
   if(noisy>2 && nfree<n && n<50) {
      FPN(F0);  FOR(j,n) printf(" %9.6f", x[j]);  FPN(F0);
      FOR(j,n) printf(" %9.5f", xb[j][0]);  FPN(F0);
      FOR(j,n) printf(" %9.5f", xb[j][1]);  FPN(F0);
      if(nfree<n && noisy>=3) printf("warning: ming2, %d paras at boundary.",n-nfree);
   }

   f0=*f=(*fun)(x,n);
   xtoy(x,x0,n);
   SIZEp=99;
   if (noisy>2) {
      printf ("\nIterating by ming2\nInitial: fx= %12.6f\nx=",f0);
      FOR(i,n) printf(" %8.5f",x[i]);   FPN(F0);
   }

   if (dfun)  (*dfun) (x0, &f0, g0, n);
   else       gradientB (n, x0, f0, g0, fun, tv, xmark);

   identity (H,nfree);
   for(Iround=0; Iround<maxround; Iround++) {
      if (fout) {
         fprintf (fout, "\n%3d %7.4f %13.6f  x: ", Iround,sizep0,f0);
         FOR (i,n) fprintf (fout, "%8.5f  ", x0[i]);
         fflush (fout);
      }

      for (i=0,zero(p,n); i<nfree; i++)  FOR (j,nfree)
         p[ix[i]] -= H[i*nfree+j]*g0[ix[j]];
      sizep0 = SIZEp; 
      SIZEp  = norm(p,n);      /* check this */

      for (i=0,am=maxstep; i<n; i++) {  /* max step length */
         if (p[i]>0 && (xb[i][1]-x0[i])/p[i]<am) am=(xb[i][1]-x0[i])/p[i];
         else if (p[i]<0 && (xb[i][0]-x0[i])/p[i]<am) am=(xb[i][0]-x0[i])/p[i];
      }

      if (Iround==0) {
         h=fabs(2*f0*.01/innerp(g0,p,n));  /* check this?? */
         h=min2(h,am/2000);

      }
      else {
         h=norm(s,nfree)/SIZEp;
         h=max2(h,am/500);
      }
      h = max2(h,1e-5);   h = min2(h,am/5);
      *f = f0;
      alpha = LineSearch2(fun,f,x0,p,h,am, min2(1e-3,e), tv,n); /* n or nfree? */

      if (alpha<=0) {
         if (fail) {
            if (AlwaysCenter) { Iround=maxround;  break; }
            else { AlwaysCenter=1; identity(H,n); fail=1; }
         }
         else   
            { if(noisy>2) printf(".. ");  identity(H,nfree); fail=1; }
      }
      else  {
         fail=0;
         FOR(i,n)  x[i]=x0[i]+alpha*p[i];
         w=min2(2,e*1000); if(e<1e-4 && e>1e-6) w=0.01;

         if(Iround==0 || SIZEp<sizep0 || (SIZEp<.001 && sizep0<.001)) goodtimes++;
         else  goodtimes=0;
         if((n==1||goodtimes>=Ngoodtimes) && SIZEp<(e>1e-5?1:.001)
            && H_end(x0,x,f0,*f,e,e,n))
            break;
      }
      if (dfun)  (*dfun) (x, f, g, n);
      else       gradientB (n, x, *f, g, fun, tv, xmark);
/*
for(i=0; i<n; i++) fprintf(frst,"%9.5f", x[i]); fprintf(frst, "%6d",AlwaysCenter);
for(i=0; i<n; i++) fprintf(frst,"%9.2f", g[i]); FPN(frst);
*/
      /* modify the working set */
      for(i=0; i<n; i++) {         /* add constraints, reduce H */
         if (xmark[i]) continue;
         if (fabs(x[i]-xb[i][0])<1e-6 && -g[i]<0)  xmark[i]=-1;
         else if (fabs(x[i]-xb[i][1])<1e-6 && -g[i]>0)  xmark[i]=1;
         if (xmark[i]==0) continue;
         xtoy (H, C, nfree*nfree);
         for(it=0; it<nfree; it++) if (ix[it]==i) break;
         for (i1=it; i1<nfree-1; i1++) ix[i1]=ix[i1+1];
         for (i1=0,nfree--; i1<nfree; i1++) FOR (i2,nfree)
            H[i1*nfree+i2]=C[(i1+(i1>=it))*(nfree+1) + i2+(i2>=it)];
      }
      for (i=0,it=0,w=0; i<n; i++) {  /* delete a constraint, enlarge H */
         if (xmark[i]==-1 && -g[i]>w)     { it=i; w=-g[i]; }
         else if (xmark[i]==1 && -g[i]<-w) { it=i; w=g[i]; }
      }
      if (w>10*SIZEp/nfree) {          /* *** */
         xtoy (H, C, nfree*nfree);
         FOR (i1,nfree) FOR (i2,nfree) H[i1*(nfree+1)+i2]=C[i1*nfree+i2];
         FOR (i1,nfree+1) H[i1*(nfree+1)+nfree]=H[nfree*(nfree+1)+i1]=0;
         H[(nfree+1)*(nfree+1)-1]=1;
         xmark[it]=0;   ix[nfree++]=it;
      }

      if (noisy>2) {
         printf (" | %d/%d", n-nfree, n);
         /* FOR (i,n)  if (xmark[i]) printf ("%4d", i+1); */
      }
      for (i=0,f0=*f; i<nfree; i++)
        {  y[i]=g[ix[i]]-g0[ix[i]];  s[i]=x[ix[i]]-x0[ix[i]]; }
      FOR (i,n) { g0[i]=g[i]; x0[i]=x[i]; }


      /* renewal of H varies with different algorithms   */
#if (defined SR1)
      /*   Symmetrical Rank One (Broyden, C. G., 1967) */
      for (i=0,w=.0; i<nfree; i++) {
         for (j=0,v=.0; j<nfree; j++) v += H[i*nfree+j] * y[j];
         z[i]=s[i] - v;
         w += y[i]*z[i];
      }
      if (fabs(w)<small)   { identity(H,nfree); fail=1; continue; }
      FOR (i,nfree)  FOR (j,nfree)  H[i*nfree+j] += z[i]*z[j]/w;
#elif (defined DFP)
      /* Davidon (1959), Fletcher and Powell (1963). */
      for (i=0,w=v=0.; i<nfree; i++) {
         for (j=0,z[i]=0; j<nfree; j++) z[i] += H[i*nfree+j] * y[j];
         w += y[i]*z[i];  v += y[i]*s[i];
      }
      if (fabs(w)<small || fabs(v)<small)  { identity(H,nfree); fail=1; continue;}
      FOR (i,nfree)  FOR (j,nfree)  
         H[i*nfree+j] += s[i]*s[j]/v - z[i]*z[j]/w;
#else /* BFGS */
      for (i=0,w=v=0.; i<nfree; i++) {
         for (j=0,z[i]=0.; j<nfree; j++) z[i]+=H[i*nfree+j]*y[j];
         w+=y[i]*z[i];    v+=y[i]*s[i];
      }
      if (fabs(v)<small)   { identity(H,nfree); fail=1; continue; }
      FOR (i,nfree)  FOR (j,nfree)
         H[i*nfree+j] += ((1+w/v)*s[i]*s[j]-z[i]*s[j]-s[i]*z[j])/v;
#endif

   }    /* for (Iround,maxround)  */

   /* try to remove this after updating LineSearch2() */
   *f=(*fun)(x,n);  
   if(noisy>2) FPN(F0);

   if (Iround==maxround) {
      if (fout) fprintf (fout,"\ncheck convergence!\n");
      return(-1);
   }
   if(nfree==n) { 
      xtoy(H, space, n*n);  /* H has variance matrix, or inverse of Hessian */
      return(1);
   }
   return(0);
}



int ming1 (FILE *fout, double *f, double (* fun)(double x[], int n),
    int (*dfun) (double x[], double *f, double dx[], int n),
    int (*testx) (double x[], int n),
    double x0[], double space[], double e, int n)
{
/* n-D minimization using quasi-Newton or conjugate gradient algorithms, 
   using function and its gradient.

   g0[n] g[n] p[n] x[n] y[n] s[n] z[n] H[n*n] tv[2*n]
   using bound()
*/
   int i,j, maxround=1000, fail=0;
   double small=1.e-20;     /* small value for checking |w|=0   */
   double f0, *g0, *g, *p, *x, *y, *s, *z, *H, *tv;
   double w,v, t, h;

   if (testx (x0, n))
      { printf ("\nInvalid initials..\n"); matout(F0,x0,1,n); return(-1); }
   f0 = *f = (*fun)(x0, n);

   if (noisy>2) {
      printf ("\n\nIterating by ming1\nInitial: fx= %12.6f\nx=", f0);
      FOR (i,n) printf ("%8.4f", x0[i]);       FPN (F0);
   }
   if (fout) {
      fprintf (fout, "\n\nIterating by ming1\nInitial: fx= %12.6f\nx=", f0);
      FOR (i,n) fprintf (fout, "%10.6f", x0[i]);
   }
   g0=space;   g=g0+n;  p=g+n;   x=p+n;
   y=x+n;      s=y+n;   z=s+n;   H=z+n;  tv=H+n*n;
   if (dfun)  (*dfun) (x0, &f0, g0, n);
   else       gradient (n, x0, f0, g0, fun, tv, AlwaysCenter);

   SIZEp=0;  xtoy (x0, x, n);  xtoy (g0,g,n);  identity (H,n);  
   FOR (Iround, maxround) {
      FOR (i,n) for (j=0,p[i]=0.; j<n; j++)  p[i] -= H[i*n+j]*g[j];
      t=bound (n, x0, p, tv, testx);

      if (Iround == 0)  h = fabs(2*f0*.01/innerp(g,p,n));
      else              h = norm(s,n)/SIZEp;
      h = max2(h,1e-5);  h = min2(h,t/8);
      SIZEp = norm(p,n);

      t = LineSearch2 (fun, f, x0, p, h, t, .00001, tv, n);

      if (t<=0 || *f<=0 || *f>1e32) {
         if (fail) {
            if(SIZEp>.1 && noisy>2) 
               printf("\nSIZEp:%9.4f  Iround:%5d", SIZEp, Iround+1);
            if (AlwaysCenter) { Iround=maxround;  break; }
            else { AlwaysCenter=1; identity(H,n); fail=1; }
         }
         else      { identity(H, n); fail=1; }
      }
      else  {
         fail=0;
         FOR(i,n)  x[i]=x0[i]+t*p[i];

         if (fout) {
            fprintf (fout, "\n%3d %7.4f%14.6f  x", Iround+1, SIZEp, *f);
            FOR (i,n) fprintf (fout, "%8.5f  ", x[i]);
            fflush (fout);
         }
         if (SIZEp<0.001 && H_end (x0,x,f0,*f,e,e,n))
            { xtoy(x,x0,n); break; }
      }
      if (dfun)  (*dfun) (x, f, g, n);
      else       gradient (n,x,*f,g,fun,tv, (AlwaysCenter||fail||SIZEp<0.01));

      for (i=0,f0=*f; i<n; i++)
         { y[i]=g[i]-g0[i];  s[i]=x[i]-x0[i];  g0[i]=g[i]; x0[i]=x[i]; }

      /* renewal of H varies with different algorithms   */
#if (defined SR1)
      /*   Symmetrical Rank One (Broyden, C. G., 1967) */
      for (i=0,w=.0; i<n; i++) {
         for (j=0,t=.0; j<n; j++) t += H[i*n+j] * y[j];
         z[i]=s[i] - t;
         w += y[i]*z[i];
      }
      if (fabs(w)<small)   { identity(H,n); fail=1; continue; }
      FOR (i,n)  FOR (j,n)  H[i*n+j] += z[i]*z[j]/w;
#elif (defined DFP)
      /* Davidon (1959), Fletcher and Powell (1963). */
      for (i=0,w=v=0.; i<n; i++) {
         for (j=0,z[i]=.0; j<n; j++) z[i] += H[i*n+j] * y[j];
         w += y[i]*z[i];  v += y[i]*s[i];
      }
      if (fabs(w)<small || fabs(v)<small)  { identity(H,n); fail=1; continue;}
      FOR (i,n)  FOR (j,n)  H[i*n+j] += s[i]*s[j]/v - z[i]*z[j]/w;
#else
      for (i=0,w=v=0.; i<n; i++) {
         for (j=0,z[i]=0.; j<n; j++) z[i] += H[i*n+j] * y[j];
         w+=y[i]*z[i];    v+=y[i]*s[i];
      }
      if (fabs(v)<small)   { identity(H,n); fail=1; continue; }
      FOR (i,n)  FOR (j,n)
         H[i*n+j] += ( (1+w/v)*s[i]*s[j] - z[i]*s[j] - s[i]*z[j] ) / v;
#endif

   }    /* for (Iround,maxround)  */

   if (Iround==maxround) {
      if (fout) fprintf (fout,"\ncheck convergence!\n");
      return(-1);
   }
   return(0);
}
