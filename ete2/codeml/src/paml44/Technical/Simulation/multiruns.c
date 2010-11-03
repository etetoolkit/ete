/* multiruns.c

     cl -O2 -Ot -W4 multiruns.c
     cc -o multiruns -O2 multiruns.c -lm

     multiruns <rstfile1> <rstfile2> ... <lnLColumn> 

  Examples (comparing three runs with lnL in column 19 in rst1):

     multiruns rst1.r1 rst1.r2 rst1.r3 19
     multiruns a/rst1 b/rst1 c/rst1 19

   March 2003, Ziheng Yang
   September 2005, changed tworuns into multiruns, ziheng yang

   This program compares outputs from multiple separate ML runs analyzing
   many data sets (using ndata) to assemble a result file.  Because of local 
   peaks and convergence problems, multiple runs for the same analysis may not 
   generate the same results.  Then we should use the results corresponding to 
   the highest lnL.  This program takes input files which have summary results 
   from multiple runs, one line for each data set.  The program takes one line 
   from each of the input files and compare the first field, which is an index 
   column and should be identical between the input files, and an lnL column.  
   The program decides which run generated the highest lnL, and copy the line 
   from that run into the output file: out.txt.

   This is useful when you analyze the same set of simulated replicate data 
   sets multiple times, using different starting values.  For example, codeml 
   may write a line of output in rst1 for each data set, including parameter 
   estimates and lnL.  You can then use this program to compare the rst1 output 
   files from multiple runs to generate one output file.  The program allows the 
   fields to be either numerical or text, but the first (index) and lnL columns
   should be numerical.

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAXNFIILES  20
#define MAXNFIELDS  1000
#define MAXLLINE    64000

void error2 (char * message);
FILE *gfopen(char *filename, char *mode);
int splitline (char line[], int fields[]);


int main(int argc, char* argv[])
{
   FILE *fout, *fin[MAXNFIILES];
   char infile[MAXNFIILES][96]={"rst1.r1", "rst1.r2"}, outfile[96]="out.txt";
   int index=0, nfile, nfileread, lnLcolumn=13, i, nrecords=0, lline=MAXLLINE;
   int nfields[MAXNFIILES],fields[MAXNFIELDS], minf, maxf, miss[MAXNFIILES];
   char *line[MAXNFIILES];
   double lnL[MAXNFIILES], lnLmin, lnLmax, indexfield[MAXNFIILES], y;

   puts("Usage: \n\tmultiruns <file1> <file2> ... <lnLcolumn>\n");
   nfile=argc-2;
   if(nfile<2) exit(1);

   for(i=0; i<nfile; i++) { 
      strcpy(infile[i], argv[1+i]);
      fin[i]=gfopen(infile[i],"r");
      if((line[i]=(char*)malloc(MAXLLINE*sizeof(char)))==NULL) error2("oom");
      printf("%s  ", infile[i]);
   }
   printf("  ==>  %s\n\n", outfile);

   sscanf(argv[argc-1], "%d", &lnLcolumn);
   lnLcolumn--;
   fout=(FILE*)gfopen(outfile,"w");

   for(nrecords=0; ; nrecords++) {
      for(i=0,nfileread=0; i<nfile; i++) { 
         nfields[i]=0; lnL[i]=0; line[i][0]='\0';  miss[i]=1;
         if(!fgets(line[i], lline, fin[i])) continue;
         nfields[i]=splitline(line[i],fields);

         if(nfields[i]>index) sscanf(line[i]+fields[index], "%lf", &indexfield[i]);
         if(nfields[i]>lnLcolumn) {
            sscanf(line[i]+fields[lnLcolumn], "%lf", &lnL[i]);
            miss[i]=0;
            nfileread++;
         }
      }
      if(nfileread==0) break;
      for(i=0,y=-1; i<nfile; i++) {
         if(!miss[i]) {
           if(y==-1) y=indexfield[i];
           else if(y!=indexfield[i]) error2("index field different");
         }
      }
      for(i=0,lnLmin=1e300,lnLmax=-1e300; i<nfile; i++) {
         if(miss[i]) continue;
         if(lnL[i]<lnLmin) { lnLmin=lnL[i];  minf=i; }
         if(lnL[i]>lnLmax) { lnLmax=lnL[i];  maxf=i; }
      }

      fprintf(fout, "%s", line[maxf]);

      printf("record %4d  (", nrecords+1);
      for(i=0; i<nfile; i++)  printf("%c", (miss[i]?'-':'+')); 
      printf(") %10.3f (%d) - %10.3f (%d) = %8.3f\n", 
         lnLmin, minf+1, lnLmax, maxf+1, lnLmin-lnLmax);
   }
   printf("\nwrote %d records into %s\n", nrecords, outfile);
   for(i=0; i<nfile; i++) { fclose(fin[i]);  free(line[i]); }
   fclose(fout);
}

void error2 (char * message)
{ printf("\nError: %s.\n", message); exit(-1); }

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

int splitline (char line[], int fields[])
{
/* This finds out how many fields there are in the line, and marks the starting 
   positions of the fields.
   Fields are separated by spaces, and texts are allowed as well.
*/
   int lline=64000, i, nfields=0, InSpace=1;
   char *p=line;

   for(i=0; i<lline && *p && *p!='\n'; i++,p++) {
      if (isspace(*p))
         InSpace=1;
      else  {
         if(InSpace) {
            InSpace=0;
            fields[nfields++]=i;
            /* if(nfields>MAXNFIELDS) puts("raise MAXNFIELDS?"); */
         }
      }
   }
   return(nfields);
}

