/* descriptive statistics

   cc -o ds -O2 ds.c tools.c -lm
   cl -O2 -Ot ds.c tools.c

*/
#include "paml.h"


void main(int argc, char *argv[])
{
   FILE *fp;
   char infile[96]="in.txt", outfile[96]="out.txt";
   int propternary=0;

   if(argc>1) strcpy(infile, argv[1]);
   if(argc>2) strcpy(outfile,argv[2]);
   fp = (FILE*)gfopen(outfile,"w");
   puts("results go into out.txt");
   starttimer();
   DescriptiveStatistics(fp, infile, 50, 100, propternary);
}
