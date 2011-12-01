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

#ifndef _GENCODE_H_
#define _GENCODE_H_
int IsValidGencode ( const int gencode);
int CodonToAmino (const int codon, const int gencode);
int IsStop (const int codon, const int gencode);
int CodonToQcoord ( const int codon, const int gencode);
int NumberSenseCodonsInGenCode ( const int gencode);
int IsNonSynonymous ( const int codon1, const int codon2, const int gencode);
int HasTransition ( const int codon1, const int codon2);
int NumberNucChanges ( int codon1, int codon2);
int QcoordToCodon ( const int qcoord, const int gencode);
int QcoordToAmino ( const int qcoord, const int gencode);
int GetGeneticCode ( const char * gencode_str);
int FourfoldDegenerate ( const int codon, const int gencode);
int Degeneracy ( const int codon, const int gencode);

double * GetAminoFrequencies ( const double * codons, const int gencode);


#define GENCODE_UNIVERSAL               0
#define GENCODE_MAMMALIAN_MITOCHONDRIAL 1
#endif
