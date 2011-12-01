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

#ifndef _UTILITY_H_
#define _UTILITY_H_

#ifndef _STDIO_H_
#include <stdio.h>
#endif

#ifndef _STDBOOL_H_
#include <stdbool.h>
#endif

void slrwarn ( int i, char * s);
void PrintMatrix ( const double * m, const int n);
void PrintVector ( const double * x, const int n);
void fprint_vector ( FILE * fp, const char * sep, const double * x, const int n);
void fprint_ivector ( FILE * fp, const char * sep, const int * x, const int n);
void Free ( void * mem);
int NumberPairs (int i);
void PrintMatrixAsBinary ( double *m, int n);
void PrintMatrixAsSign (double *m, int n);
int UpperTriangularCoordinate ( int i, int j, int n);
int LowerTriangularCoordinate ( int i, int j, int n);
int TriangularCoordinate ( int i, int j, int n);
int ReadVectorFromOpenFile (double * x, int n, FILE * fp);

char * ReadString ( FILE * fp);
char gchar ( FILE * fp);

char * mitoa ( int i);
int sign (const double x);

double * norm_vector ( double * vec, const int n, const double sum);
double * scale_vector ( double * vec, const int n, const double fact);

int teeint ( FILE * fp, const char * s, const int i);

double * CopyVector ( const double * A, double * B, const unsigned int n);
unsigned int sum_bool ( const bool * x, const unsigned int n);

#endif
