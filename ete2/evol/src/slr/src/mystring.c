/*
 *  Copyright 2003-2008 Tim Massingham (tim.massingham@ebi.ac.uk)
 *  Funded by EMBL - European Bioinformatics Institute
 */
/*
 *  This file is part of SLR ("Sitewise Likelihood Ratio")
 *
 *  SLR is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  SLR is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with SLR.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "mystring.h"

#define OOM(A) { if (NULL==(A) ){fputs("Out of memory\n",stderr); exit(EXIT_FAILURE);} }
static void check_is_mystring (const Mystring string);
static void double_length_of_mystring ( Mystring string);

Mystring new_mystring (const int len){
   Mystring string;
   
   assert(len>=1);

   string = malloc ( Mystring_size );
   string->maxlen = (len>0)?len:1;
   string->len = 0;
   string->string = malloc(string->maxlen*sizeof(char));

   check_is_mystring(string);
   return string;
}

static void check_is_mystring ( const Mystring string){
#ifdef NDEBUG
   return;
#endif

   assert(NULL!=string);
   assert(string->len>=0);
   assert(string->maxlen>0);
   assert(string->len <= string->maxlen);
   assert(NULL!=string->string);
}

void free_mystring (Mystring string){
   check_is_mystring (string);
   free (string->string);
   free (string);
}

void append_char_to_mystring ( const char c, Mystring string){
   check_is_mystring (string);
   
   if ( string->len == string->maxlen){
      double_length_of_mystring (string);
   }
   string->string[string->len++] = c;

   check_is_mystring(string);
}

static void double_length_of_mystring (Mystring string){
   char * new_mem;
   check_is_mystring(string);

   new_mem = malloc(string->maxlen * 2 * sizeof(char));	OOM(new_mem);
   memcpy (new_mem,string->string,string->len * sizeof(char));
   free(string->string);
   string->string = new_mem;
   string->maxlen *= 2;

   check_is_mystring (string);
}

char * cstring_of_mystring(const Mystring string){
   char * cstring;

   check_is_mystring(string);

   cstring = malloc( (string->len+1) * sizeof(char) );
   memcpy(cstring,string->string,string->len * sizeof(char));
   cstring[string->len] = '\0';

   return cstring;
}

Mystring mystring_of_cstring ( const char * str){
   Mystring string;
   int len;

   assert(NULL!=str);

   len = strlen(str);
   string = new_mystring (len);
   memcpy(string->string,str,len);
   string->len = len;

   check_is_mystring(string);
   return string;
}


#ifdef TEST
   int main (int argc, char * argv[]){
      Mystring a;
      char *b;
      int i,nstr;

      assert(argc>1);
      for ( nstr=1 ; nstr<argc ; nstr++){
	 a = new_mystring(10);
	 for ( i=0 ; i<strlen(argv[nstr]) ; i++){
	    append_char_to_mystring(argv[nstr][i],a);
	 }
	 b = cstring_of_mystring (a);
	 free_mystring(a);
	 printf ("String %d is \"%s\"\n",nstr,b);
	 free(b);
      }
      return EXIT_SUCCESS;
   }
#endif
