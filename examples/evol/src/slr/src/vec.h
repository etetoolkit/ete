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

#ifndef _VEC_H_
#define _VEC_H_

#ifndef _STDIO_H_
#include <stdio.h>
#endif

struct __vec {
	double * x;
	unsigned int n;
};

typedef struct __vec * VEC;

struct __ivec {
        int * x;
        unsigned int n;
};

typedef struct __ivec * IVEC;


VEC create_vec ( const unsigned int n);
VEC create_zerovec ( const unsigned int n);
void initialize_vec ( VEC v, const double val);
void free_vec ( const VEC v);
IVEC create_ivec ( const unsigned int n);
IVEC create_zeroivec ( const unsigned int n);
void initialize_ivec ( IVEC v, const int val);
void free_ivec ( const IVEC v);

double minelt_vec ( const VEC v);
double maxelt_vec ( const VEC v);
VEC copy_vec ( const VEC v);
int minelt_ivec ( const IVEC v);
int maxelt_ivec ( const IVEC v);
IVEC copy_ivec ( const IVEC v);

void fprint_vec (FILE * fp, const char * prefix, const char * sep, const char * suffix, const VEC v);
void fprint_rvec(FILE * fp, const char * name, const VEC v);
void fprint_ivec (FILE * fp, const char * prefix, const char * sep, const char * suffix, const IVEC v);
void fprint_rivec(FILE * fp, const char * name, const IVEC v);

double suma_vec ( const VEC v, const double a);
double sum_vec ( const VEC v);
int suma_ivec ( const IVEC v, const int a);
int sum_ivec ( const IVEC v);


double dotproduct_vec ( const VEC a, const VEC B);
double norm_vec ( const VEC v);

#define vget(VEC,I) VEC->x[(I)]
#define vset(VEC,I,VAL) VEC->x[(I)] = (VAL)
#define vlen(VEC) VEC->n


#endif
