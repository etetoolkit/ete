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

#ifndef _RNG_H_
#define _RNG_H_

#define RL_LAGGED	0
#define RL_LINEAR	1
void RL_Init(const unsigned int seed);
void RL_Close(void);

double RandomStandardUniform ( void);
double RandomExp (double mean);
double RandomGamma ( double shape, double scale);
int RandomDirichlet ( double *a, double *p, int n);
int RandomDirichlet_rejection ( double *a, double *p, int n);
void SetRandomGenerator (int gen);
#endif

