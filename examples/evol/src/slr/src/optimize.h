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

#ifndef _OPTIMIZE_H_
#define _OPTIMIZE_H_
/* Constants needed for optimizer:
 * 	opt->trust	Initial trust region, default 1
 * 	tol		Tolerance, default 1e-8
 * 	RESTART		Restart optimizer at optima.
 * 	max_step	Maximum number of steps to take.
 */

/* Suggested improvements:
 * 	Need testing in more extreme cases.
 * 	Termination criteria need to be worked on. Current look at last step
 * and norm of current gradient.
 * 	Possibility of incorrect termination in a saddle-point? May only fail
 * if we land exactly in the saddle point as Hessian is guaranteed to be
 * positive definite
 */

void Optimize (  double * x, int n, void (*df)(const double *,double *, void *), double (*f)(const double *, void*), double * fx, void * data, double *bd, int noisy);

#endif
