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
#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <err.h>
#include "gencode.h"
#include "genetic_codes.h"
#include "bases.h"


/*
 * Returns number of sense codons for a given genetic code
 */
int 
NumberSenseCodonsInGenCode(const int gencode)
{
	assert(IsValidGencode(gencode));

	switch (gencode) {
	case GENCODE_UNIVERSAL:
		return 61;
	case GENCODE_MAMMALIAN_MITOCHONDRIAL:
		return 60;
	}

	//Should never reach here
		abort();
	return -1;
}


/*
 * Converts enumerated codons into enumerated sense codons
 */
int 
CodonToQcoord(const int codon, const int gencode)
{
	int             mod;
	assert(IsValidGencode(gencode));
	assert(IsValidBase(codon, SEQTYPE_CODON, gencode));

	/*GapChar is same for both SEQTYPE_CODON and SEQTYPE_CODONQ*/
			if (GapChar(SEQTYPE_CODON) == codon)
			return codon;

	if (IsStop(codon, gencode))
		return -1;

	mod = 0;
	switch (gencode) {
	case GENCODE_UNIVERSAL:
		if (codon >= 48)
			mod--;
		if (codon >= 50)
			mod--;
		if (codon >= 56)
			mod--;
		return (codon + mod);
	case GENCODE_MAMMALIAN_MITOCHONDRIAL:
		if (codon >= 8)
			mod--;
		if (codon >= 10)
			mod--;
		if (codon >= 48)
			mod--;
		if (codon >= 50)
			mod--;
		return (codon + mod);
	}

	/*Should never reach here*/
		abort();
	return -1;
}

/*
 * Convert from enumerate sense codons into enumerated codons
 */
int 
QcoordToCodon(const int qcoord, const int gencode)
{
	int             mod;

	assert(IsValidGencode(gencode));
	assert(IsValidBase(qcoord, SEQTYPE_CODONQ, gencode));

	if (GapChar(SEQTYPE_CODONQ) == qcoord)
		return qcoord;

	mod = 0;
	switch (gencode) {
	case GENCODE_UNIVERSAL:
		if (qcoord > 47)
			mod++;
		if (qcoord > 48)
			mod++;
		if (qcoord > 53)
			mod++;
		return (qcoord + mod);
	case GENCODE_MAMMALIAN_MITOCHONDRIAL:
		if (qcoord > 7)
			mod++;
		if (qcoord > 8)
			mod++;
		if (qcoord > 45)
			mod++;
		if (qcoord > 46)
			mod++;
		return (qcoord + mod);
	}

	/*Should never reach here*/
		abort();
	return -1;
}


/* Is stop codon? */
int 
IsStop(const int codon, const int gencode)
{
	assert(IsValidGencode(gencode));
	assert(IsValidBase(codon, SEQTYPE_CODON, gencode));

	if (CodonToAmino(codon, gencode) == -1)
		return 1;
	return 0;
}


/*
 * Converts enumerated codons into amino acid No contracts since these are
 * tested in other functions
 */
int 
QcoordToAmino(const int qcoord, const int gencode)
{
	int             codon;

	codon = QcoordToCodon(qcoord, gencode);
	return CodonToAmino(codon, gencode);
}


/*
 * Converts enumerated codon into amino acid
 */
int 
CodonToAmino(const int codon, const int gencode)
{
	assert(IsValidGencode(gencode));
	assert(IsValidBase(codon, SEQTYPE_CODON, gencode));

	if (codon != GapChar(SEQTYPE_CODON))
		return GenCodes[gencode][codon];
	else
		return GapChar(SEQTYPE_AMINO);

	/*Should never reach here*/
		abort();
	return -3;
}


/*
 * Is gencode given valid
 */
int 
IsValidGencode(const int gencode)
{
	if (GENCODE_UNIVERSAL == gencode
	    || GENCODE_MAMMALIAN_MITOCHONDRIAL == gencode)
		return 1;

	return 0;
}


/*
 * Is changde from codon1 to codon2 synonymous
 */
int 
IsNonSynonymous(const int codon1, const int codon2, const int gencode)
{
	assert(IsValidGencode(gencode));
	assert(IsValidBase(codon1, SEQTYPE_CODON, gencode));
	assert(IsValidBase(codon2, SEQTYPE_CODON, gencode));

	if (CodonToAmino(codon1, gencode) != CodonToAmino(codon2, gencode))
		return 1;

	return 0;
}


/*
 * Is change from codon1 to codon2 a single transition? (A<->G) or (C<->Y)
 */
int 
HasTransition(const int codon1, const int codon2)
{
	int             a, b;

	assert(IsValidBase(codon1, SEQTYPE_CODON, 0));
	assert(IsValidBase(codon2, SEQTYPE_CODON, 0));

	/*
	 * Horrid bit-banging to find out whether mutation is a transition or
	 * not. Uses property that sums of A+G, A+A, G+G, C+C, T+T, C+T are
	 * all even. The other sums are odd
	 */
	a = codon1 & 3;
	b = codon2 & 3;
	if ((a + b) % 2 == 0 && a != b)
		return 1;
	a = (codon1 >> 2) & 3;
	b = (codon2 >> 2) & 3;
	if ((a + b) % 2 == 0 && a != b)
		return 1;
	a = (codon1 >> 4) & 3;
	b = (codon2 >> 4) & 3;
	if ((a + b) % 2 == 0 && a != b)
		return 1;

	return 0;
}


/*
 * Returns minimum number of nucleotide changes required to get from codon1
 * to codon2
 */
int 
NumberNucChanges(int codon1, int codon2)
{
	int             c = 0;

	assert(IsValidBase(codon1, SEQTYPE_CODON, 0));
	assert(IsValidBase(codon1, SEQTYPE_CODON, 0));


	c += !((codon1 & 3) == (codon2 & 3));
	codon1 >>= 2;
	codon2 >>= 2;
	c += !((codon1 & 3) == (codon2 & 3));
	codon1 >>= 2;
	codon2 >>= 2;
	c += !((codon1 & 3) == (codon2 & 3));

	assert(c >= 0 && c <= 3);
	return c;
}



int 
GetGeneticCode(const char *gencode_str)
{
	int             gencode;

	assert(NULL != gencode_str);

	if (strcmp(gencode_str, "universal") == 0) {
		gencode = GENCODE_UNIVERSAL;
	} else if (strcmp(gencode_str, "mammalian") == 0) {
		gencode = GENCODE_MAMMALIAN_MITOCHONDRIAL;
	} else {
		puts("Unrecognised genetic code - defaulting to universal");
		puts("Recognised codes are Universal \"universal\" or");
		puts("Mammalian mitochondrial \"mammalian\"");
		gencode = GENCODE_UNIVERSAL;
	}

	assert(IsValidGencode(gencode));

	return gencode;
}


int 
FourfoldDegenerate(const int codon, const int gencode)
{
	assert(IsValidGencode(gencode));
	assert(IsValidBase(codon, SEQTYPE_CODON, gencode));

	if ((CodonDegen[gencode][codon] & 3) == 3) {
		return 1;
	}
	return 0;
}

int 
Degeneracy(const int codon, const int gencode)
{
	assert(IsValidGencode(gencode));
	assert(IsValidBase(codon, SEQTYPE_CODON, gencode));

	return CodonDegen[gencode][codon];
}

double         *
GetAminoFrequencies(const double *codons, const int gencode)
{
	double         *af;

	assert(NULL != codons);
	assert(IsValidGencode(gencode));

	af = calloc(20, sizeof(double));	/* Err. Magic number */
	if (NULL == af) {
		warn("Failed to allocate memory %s:%d\n. Returing null", __FILE__, __LINE__);
		return NULL;
	}
	for (int codon = 0; codon < 64; codon++) {
		if (IsStop(codon, gencode)) {
			continue;
		}
		af[CodonToAmino(codon, gencode)] += codons[codon];
	}


	return af;
}
