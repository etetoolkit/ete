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
#include <assert.h>
#include <float.h>
#include <limits.h>
#include <string.h>
#include "vec.h"

VEC vec_from_array ( const double * a, const unsigned int n){
	assert(NULL!=a);
	assert(n>0);
	VEC v = create_vec(n);
	for ( unsigned int i=0 ; i<n ; i++){
		vset(v,i,a[i]);
	}
	return v;
}

VEC create_vec ( const unsigned int n){
	assert(n>0);

	VEC v = malloc(sizeof(struct __vec));
	if ( NULL==v){return NULL;}

	v->n = n;
	v->x = malloc(n*sizeof(double));
	if ( NULL==v){ free(v); return NULL;}

	return v;
}

VEC create_zerovec ( const unsigned int n){
	assert(n>0);

        VEC v = malloc(sizeof(struct __vec));
        if ( NULL==v){return NULL;}

        v->n = n;
        v->x = calloc(n,sizeof(double));
        if ( NULL==v){ free(v); return NULL;}

        return v;
}

void initialize_vec ( VEC v, const double val){
	assert(NULL!=v);
	const int len = v->n;
	for ( unsigned int i=0 ; i<len ; i++){
		v->x[i] = val;
	}
}

void free_vec ( const VEC v){
	assert(NULL!=v);
	assert(NULL!=v->x);

	free(v->x);
	free(v);
}
	
double dotproduct_vec ( const VEC a, const VEC b){
	assert(NULL!=a);
	assert(NULL!=b);
	assert(a->n == b->n);

	const int len = a->n;
	double sum = 0.;
	for ( unsigned int i=0 ; i<len ; i++){
		sum += a->x[i] * b->x[i];
	}
	return sum;
}

double norm_vec ( const VEC v){
	double norm = dotproduct_vec(v,v);
	assert(norm>=0.);
	return norm;
}

double minelt_vec ( const VEC v){
	assert(NULL!=v);
	double minelt = DBL_MAX;
	const unsigned int len = v->n;
	for ( unsigned int i=0 ; i<len ; i++){
		if ( minelt>v->x[i]){ minelt = v->x[i];}
	}
	return minelt;
}

double maxelt_vec ( const VEC v){
	assert(NULL!=v);
        double maxelt = -DBL_MAX;
        const unsigned int len = v->n;
        for ( unsigned int i=0 ; i<len ; i++){
                if ( maxelt<v->x[i]){ maxelt = v->x[i];}
        }
	return maxelt;
}

VEC copy_vec ( const VEC v){
	assert(NULL!=v);
	const int len = v->n;
	VEC vcopy = create_vec(len);
	assert(NULL!=vcopy);
	for ( unsigned int i=0 ; i<len ; i++){
		vcopy->x[i] = v->x[i];
	}
	return vcopy;
}

void fprint_vec (FILE * fp, const char * prefix, const char * sep, const char * suffix, const VEC v){
	assert(NULL!=fp);
	assert(NULL!=sep);
	assert(NULL!=v);

	fprintf (fp,"%s%e",prefix,vget(v,0));
	const unsigned int len = vlen(v);
	for ( unsigned int i=1 ; i<len ; i++){
		fprintf (fp, "%s%e",sep,vget(v,i));
	}
	fputs(suffix,fp);
}

void fprint_rvec(FILE * fp, const char * name, const VEC v){
	assert(NULL!=fp);
	assert(NULL!=name);
	assert(NULL!=v);
	char * prefix = malloc((strlen(name)+5)*sizeof(char));
	memcpy(prefix,name,strlen(name)*sizeof(char));
	memcpy(prefix,"<-c(",5*sizeof(char));
	fprint_vec(fp,prefix,",",");\n",v);
	free(prefix);
}

double suma_vec ( const VEC v, const double a){
	assert(NULL!=v);
	const unsigned int len = vlen(v);
	double sum = 0.;
	for ( unsigned int i=0 ; i<len ; i++){
		sum += vget(v,i) + a;
	}

	return sum;
}


double sum_vec ( const VEC v){
        assert(NULL!=v);
        const unsigned int len = vlen(v);
        double sum = 0.;
        for ( unsigned int i=0 ; i<len ; i++){
                sum += vget(v,i);
        }

        return sum;
}





IVEC create_ivec ( const unsigned int n){
	assert(n>0);

	IVEC v = malloc(sizeof(struct __ivec));
	if ( NULL==v){return NULL;}

	v->n = n;
	v->x = malloc(n*sizeof(int));
	if ( NULL==v){ free(v); return NULL;}

	return v;
}

IVEC create_zeroivec ( const unsigned int n){
	assert(n>0);

        IVEC v = malloc(sizeof(struct __ivec));
        if ( NULL==v){return NULL;}

        v->n = n;
        v->x = calloc(n,sizeof(int));
        if ( NULL==v){ free(v); return NULL;}

        return v;
}

void initialize_ivec ( IVEC v, const int val){
	assert(NULL!=v);
	const int len = v->n;
	for ( unsigned int i=0 ; i<len ; i++){
		v->x[i] = val;
	}
}

void free_ivec ( const IVEC v){
	assert(NULL!=v);
	assert(NULL!=v->x);

	free(v->x);
	free(v);
}
	
int minelt_ivec ( const IVEC v){
	assert(NULL!=v);
	double minelt = INT_MAX;
	const unsigned int len = v->n;
	for ( unsigned int i=0 ; i<len ; i++){
		if ( minelt>v->x[i]){ minelt = v->x[i];}
	}
	return minelt;
}

int maxelt_ivec ( const IVEC v){
	assert(NULL!=v);
        double maxelt = -INT_MAX;
        const unsigned int len = v->n;
        for ( unsigned int i=0 ; i<len ; i++){
                if ( maxelt<v->x[i]){ maxelt = v->x[i];}
        }
	return maxelt;
}

IVEC copy_ivec ( const IVEC v){
	assert(NULL!=v);
	const int len = v->n;
	IVEC vcopy = create_ivec(len);
	assert(NULL!=vcopy);
	for ( unsigned int i=0 ; i<len ; i++){
		vcopy->x[i] = v->x[i];
	}
	return vcopy;
}

void fprint_ivec (FILE * fp, const char * prefix, const char * sep, const char * suffix, const IVEC v){
	assert(NULL!=fp);
	assert(NULL!=sep);
	assert(NULL!=v);

	fprintf (fp,"%s%d",prefix,vget(v,0));
	const unsigned int len = vlen(v);
	for ( unsigned int i=1 ; i<len ; i++){
		fprintf (fp, "%s%d",sep,vget(v,i));
	}
	fputs(suffix,fp);
}

void fprint_rivec(FILE * fp, const char * name, const IVEC v){
	assert(NULL!=fp);
	assert(NULL!=name);
	assert(NULL!=v);
	char * prefix = malloc((strlen(name)+5)*sizeof(char));
	memcpy(prefix,name,strlen(name)*sizeof(char));
	memcpy(prefix,"<-c(",5*sizeof(char));
	fprint_ivec(fp,prefix,",",");\n",v);
	free(prefix);
}

int suma_ivec ( const IVEC v, const int a){
	assert(NULL!=v);
	const unsigned int len = vlen(v);
	int sum = 0;
	for ( unsigned int i=0 ; i<len ; i++){
		sum += vget(v,i) + a;
	}

	return sum;
}


int sum_ivec ( const IVEC v){
        assert(NULL!=v);
        const unsigned int len = vlen(v);
        int sum = 0;
        for ( unsigned int i=0 ; i<len ; i++){
                sum += vget(v,i);
        }

        return sum;
}

