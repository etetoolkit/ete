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

#ifndef _MYSTRING_H_
#define _MYSTRING_H_

struct __mystring_struct {
   char * string;
   int len, maxlen;
};
typedef struct __mystring_struct * Mystring;
#define Mystring_size sizeof(struct __mystring_struct)

Mystring new_mystring (const int len);
void free_mystring (Mystring string);
void append_char_to_mystring ( const char c, Mystring string);
char * cstring_of_mystring(const Mystring string);
Mystring mystring_of_cstring (const char * str);
#endif

