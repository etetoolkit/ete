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

#ifndef _NUCMODEL_H_
#define _NUCMODEL_H_

#ifndef _MODEL_H_
#include "model.h"
#endif

MODEL *NewJC69Model_full (int nbr);
MODEL * NewNNNModel_full ( const int * desc, const double * params, const int nparam, const double * pi, const int freq_type, const int nbr, const int alt_scale, const int opt_pi);

const int desc_JC69[] = { -1, -1, -1, -1,
                          -1, -1, -1, -1,
                          -1, -1, -1, -1,
                          -1, -1, -1, -1};
      
const int desc_HKY[]  = { -1, -1,  0, -1,
						  -1, -1, -1,  0,
						   0, -1, -1, -1,
						  -1,  0, -1, -1};
						  
const int desc_REV[]  = { -1, -1,  0, 1,
                          -1, -1,  2, 3,
                           0,  2, -1, 4,
                           1,  3,  4, -1};
#endif
