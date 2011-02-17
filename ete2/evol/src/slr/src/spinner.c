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

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "spinner.h"


int maxtype = 3;
int SpinNType[3] = {4,4,5};
char spin1states[4] = {'\\','|','/','-'};
char spin2states[4] = {'.','o','O','o'};
char spin3states[5] = {'.',':','+','*','0'};
char * SpinStates[3] = {spin1states,spin2states,spin3states};

SPINNER * CreateSpinner ( int type){
	SPINNER * spin;

	if(type<0 || type>=maxtype)
		return NULL;

	spin = malloc (sizeof(SPINNER));
	if (NULL!=spin){
		spin->type = type;
		spin->nstates = SpinNType[type];
		spin->step = 0;
	}

	return spin;
}

void UpdateSpinner ( SPINNER * spin){
	if(NULL==spin)
		return;

	if(0!=spin->step)
		printf ("\b");
	putchar (SpinStates[spin->type][(spin->step)%(spin->nstates)]);
	fflush(stdout);
	spin->step++;
}

void DeleteSpinner (SPINNER * spin){
	if(NULL==spin)
		return;
	if(0!=spin->step){
		putchar('\b');
		fflush(stdout);
	}
	free(spin);
}

