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

#ifndef _MATRIX_H_
#define _MATRIX_H_

void Matrix_Matrix_Mult ( const double * A, const int nr1, const int nc1, const double * B, const int nr2, const int nc2, double *C);
void Matrix_MatrixT_Mult ( const double * A, const int nr1, const int nc1, const double * B, const int nr2, const int nc2, double *C);
void MatrixT_Matrix_Mult ( const double * A, const int nr1, const int nc1, const double * B, const int nr2, const int nc2, double *C);

void NormalizeColumns ( double * mat, int n);
void NormalizeRows ( double * mat, int n);
void TransposeMatrix (double *a, double *b, int n);
double MatrixFMax ( double * A, int n);
double VectorNorm ( double * A, int n);
double VectorDotProduct ( const double * A, const double * B, const int n);
void GramSchmidtTranspose ( double * A,int n);
void CopyMatrix ( const double *A, double *B, int n);
int Factorize ( double * A, double * val, int n);
void HadamardMult ( double * A, double * B, int n);
void MakeMatrixIdentity (double * mat, const int n);
void MakeMatrixDiagonal(double *A, const int n);
double MatrixMaxElt ( double * A, int n);
double MatrixMinElt (double * A, int n);
int InvertMatrix (double * A, int n);

int IsFiniteVector (const double * a, const int n);
int IsZeroVector ( const double *a , const int n);
#endif
