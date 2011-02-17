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

#ifndef _STATISTICS_H_
#define _STATISTICS_H_

#define BONFERRONI	0
#define SIDAK		1

#ifndef _VEC_H_
#include "vec.h"
#endif

struct summary {
	double mean,var;
	VEC quantiles,data;
	double mad;
};

double * Pvalue_adjust_SingleStep ( const double * pval, const int n, const int method);
double * Pvalue_adjust_StepDown ( const double * pval, const int n, const int method);
double * Pvalue_adjust_StepUp ( const double * pval, const int n, const int method);
double mean ( const VEC v);
double median ( const VEC v);
double quantile (const VEC v, const double q);
VEC quantiles ( const VEC v, const VEC q);
double variance (const VEC v);
double sd(const VEC v);
double mad ( const VEC v);
struct summary * summarise_vec(const VEC v);
struct summary * fprint_summary (FILE * fp, const char * name, struct summary * s);
void free_summary ( struct summary * s);

double pFDR_storey02 ( const double * pval, const unsigned int m, const double lambda, const double gamma);
double FDR_storey02 (const double * pval, const unsigned int m, const double lambda, const double gamma);
double * qvals_storey02 ( const double * pval, const unsigned int m);
double estimate_lambda_deltaapprox ( const double * pval, const unsigned int m, const double gamma );
double estimate_lambda_storey04 ( const double * pval, const unsigned int m );
#endif

