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

#ifndef _LINEMIN_H_
#define _LINEMIN_H_

double linemin_multid ( double (*fun)(const double *, void *), int dim, double * x, double *xnew, double * direct, void * info, const double min, const double max, const double tol, const int noisy, int * neval );
double linemin_1d ( double (*fun)(const double *, void *), double * x, void * info, const double min, const double max, const double tol, const int noisy, int * neval);
double linemin_backtrack ( double (*fun)(const double *, void *), int dim, double * x, double *xnew, double * direct, void * info, const double min, const double max, const double tol, const int noisy, int * neval );
#endif

