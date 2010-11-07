/* testPMat.c

   November 2003, Z Yang

   This small program tests two methods or routines for calculating the 
   transition probability matrix for a time reversible Markov rate matrix.  
   The first is the routine matexp(), which uses repeated squaring and works 
   on a general matrix (not necesarily time reversible).  For large distances, 
   more squaring should be used, but I have not tested this extensively.  You
   can change TimeSquare to see its effect.  
   The second method, PMatQRev, uses a routine for eigen values and eigen 
   vectors for a symmetrical matrix.  It involves some copying and moving 
   around when some frequencies are 0.  
   For each algorithm, this program generates random frequencies and random rate 
   matrix and then calls an algorithm to calculate P(t) = exp(Q*t).

     cl -O2 -Ot -W4 testPMat.c tools.c
     cc -O3 testPMat.c tools.c -lm
     testPMat
*/

#include "paml.h"

int main(void)
{
   int n=400, noisy=0, i,j;
   int nr=10, ir, TimeSquare=10, algorithm; /* TimeSquare should be larger for large t */
   double t=5, *Q, *pi, *space, s;
   char timestr[96], *AlgStr[2]={"repeated squaring", "eigensolution"};
   
   if((Q=(double*)malloc(n*n*5*sizeof(double))) ==NULL) error2("oom");
   pi=Q+n*n; space=pi+n;

   for(algorithm=0; algorithm<2; algorithm++) {
      starttime();
      SetSeed(1234567);
      for (i=0; i<n; i++)  pi[i]=rndu();
      s=sum(pi,n);
      for (i=0; i<n; i++)  pi[i]/=s;

      for(ir=0; ir<nr; ir++) {
         printf("Replicate %d/%d ", ir+1,nr);

   	   for (i=0; i<n; i++)  
            for (j=0,Q[i*n+i]=0; j<i; j++)
               Q[i*n+j]=Q[j*n+i] = square(rndu());
         for (i=0; i<n; i++)
            for (j=0; j<n; j++)
               Q[i*n+j] *= pi[j];
         for(i=0,s=0; i<n; i++)  {  /* rescaling Q so that average rate is 1 */
            Q[i*n+i]=0; Q[i*n+i]=-sum(Q+i*n, n); 
            s-=pi[i]*Q[i*n+i];
         }

         if(noisy) {
            matout(stdout, pi, 1, n);
            matout(stdout, Q, n, n);
         }

         if(algorithm==0) 
            matexp(Q, 1, n, TimeSquare, space);
         else 
            PMatQRev(Q, pi, 1, n, space);
         printf("%s, time: %s\n", AlgStr[algorithm], printtime(timestr));
         if(noisy) 
            matout(stdout, Q, n, n);
      }
   }
   return (0);
}
