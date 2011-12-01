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

#ifndef _DATA_H_
#define _DATA_H_

#define MAX_SP_NAME 80


typedef struct {
        char    seq_type;
        int     n_pts;
        int     n_unique_pts;
        int     n_sp;
        int     n_bases;
        int     compressed;
        char  ** sp_name;
        int ** seq;
        double  * freq;
        int * index;
	int gencode;
} DATA_SET;

void CheckIsDataSet ( const DATA_SET * data);
void CheckIsSorted_DS ( const DATA_SET * data);

DATA_SET * CreateDataSet ( const int n_size, const int n_sp);
void FreeDataSet ( DATA_SET * data);


DATA_SET * sort_data ( DATA_SET * data);
DATA_SET * compress_data ( const DATA_SET * data);
DATA_SET * RemoveTrivialObs ( const DATA_SET * data);

DATA_SET * CombineDatasets ( const DATA_SET * data1, const DATA_SET * data2);
void CopySite (const DATA_SET * old, const int oldsite, DATA_SET * new, const int newsite);
void CopySiteByIndex (const DATA_SET * old, const int old_idx, DATA_SET * new, const int new_idx);
DATA_SET * CopyDataSet ( const DATA_SET * data);
void CopySiteToDataSet ( const DATA_SET * data, DATA_SET * data_single, const int site);
DATA_SET * SelectFromData ( const DATA_SET * data, const int * idx, const int n);
DATA_SET * ExtractSequences ( int * seqs, int n_seq, DATA_SET * data);

DATA_SET * ConvertNucToCodon ( const DATA_SET * data, const int gencode);
DATA_SET * ConvertCodonToQcoord (DATA_SET * data);


double * CodonBaseFreqs ( const DATA_SET * data, const int method, const int species, double * bf);
double * GetBaseFreqs ( const DATA_SET * data, const int perspecies);
double * CreateMGFreqs ( const double * pi, const int codonf ,const int gencode);
double * AminoFreqs ( const DATA_SET * data, const int species);
double SiteEntropy ( const DATA_SET * data, const int site, const double *pi);


DATA_SET * read_data ( const char * filename, const int seqtype);
int save_data ( char * filename, DATA_SET * data);
void PrintData ( const DATA_SET * data);
void PrintSite ( const DATA_SET * data, const int i);


int CountGapsAtSite ( const DATA_SET * data, const int i);
int IsSiteSynonymous ( const DATA_SET * data, const int i, const int gencode);
int IsConserved ( const DATA_SET * data, const int i);
int NumNongaps ( const DATA_SET * data, const int site);
int count_sequence_stops ( const int * seq, const int n, const int gencode);
int count_alignment_stops ( const DATA_SET * data);

#endif

