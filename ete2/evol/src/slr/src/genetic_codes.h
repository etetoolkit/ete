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

#ifndef _GENETIC_CODES_H_
#define _GENETIC_CODES_H_

int GenCodes[2][64] = {{ 11,2,11,2,   16,16,16,16,   1,15,1,15,   9,9,12,9,
                        5,8,5,8,    14,14,14,14,   1,1,1,1,     10,10,10,10,
                        6,3,6,3,    0,0,0,0,       7,7,7,7,     19,19,19,19,
                        -1,18,-1,18,  15,15,15,15,  -1,4,17,4,    10,13,10,13},
                        { 11,2,11,2,   16,16,16,16,  -1,15,-1,15,  12,9,12,9,
                        5,8,5,8,    14,14,14,14,   1,1,1,1,     10,10,10,10,
                        6,3,6,3,    0,0,0,0,       7,7,7,7,     19,19,19,19,
                       -1,18,-1,18,  15,15,15,15,   17,4,17,4,   10,13,10,13}};

int CodonDegen[2][64] = {{ 1,1,1,1, 3,3,3,3, 17,1,17,1, 2,2,0,2,
			   1,1,1,1, 3,3,3,3, 19,3,19,3, 19,3,19,3,
			   1,1,1,1, 3,3,3,3, 3,3,3,3, 3,3,3,3,
			   5,1,1,1, 3,3,3,3, 0,1,0,1, 17,1,17,1},
			 { 1,1,1,1, 3,3,3,3, 1,1,1,1, 1,1,1,1,
			   1,1,1,1, 3,3,3,3, 3,3,3,3, 19,3,19,3,
			   1,1,1,1, 3,3,3,3, 3,3,3,3, 3,3,3,3,
			   1,1,1,1, 3,3,3,3, 1,1,1,1, 17,1,17,1}};
#endif

