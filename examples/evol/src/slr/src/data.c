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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <err.h>
#include "gencode.h"
#include "model.h"
#include "bases.h"
#include "data.h"
#include "utility.h"
#include <assert.h>
#include <limits.h>
#include <float.h>
#include <stdbool.h>

#define Free(A) if( A != NULL){ free( A );  A = NULL;}
#ifndef OOM
#define OOM(A) if ( A == NULL){ \
                  printf ("Out of Memory! %s:%d\n",__FILE__,__LINE__); \
                  exit (EXIT_FAILURE); }
#endif



static int      lexo(const int **seq, const int i, const int j, const int n);
static int      lexo2(const int *seq1, const int **seq, const int i, const int n);
static void     UpdateIndex(DATA_SET * data, const int a, const int b);
static int     *ReadNucleo(FILE * fp, int n_pts, const char * name);
static int     *ReadAmino (FILE * fp, int n_pts, const char * name);
static void     SaveNucleoSeq(FILE * fp, int *seq, int length);
static void     save_amino_seq(FILE * fp, int *seq, int length);



void 
CheckIsDataSet(const DATA_SET * data)
{
	int             Nbases;

#ifdef NDEBUG
	return;
#endif

	assert(IsSeqtype(data->seq_type));
	assert(data->seq_type != SEQTYPE_CODON || IsValidGencode(data->gencode));

	//Check that number of data points in correct
		assert(data->n_pts > 0);
	assert(data->n_unique_pts > 0);
	assert(data->n_unique_pts <= data->n_pts);
	assert(data->compressed == 0 || data->compressed == 1);
	assert(data->compressed || data->n_unique_pts == data->n_pts);


	assert(data->n_sp > 0);

	assert(data->n_bases ==
	       NumberPossibleBases(data->seq_type, data->gencode));

	Nbases = NumberPossibleBases(data->seq_type, data->gencode);
	/*Check that sequence information is valid*/
	for (int i = 0; i < data->n_sp; i++) {
		int gapchar = GapChar(data->seq_type);
		assert(NULL != data->seq[i]);
		for (int j = 0; j < data->n_unique_pts; j++) {
			assert((0 <= data->seq[i][j] && data->seq[i][j] < Nbases )
		       		|| data->seq[i][j] == gapchar);
		}
	}

	/*Check names*/
	for (int i = 0; i < data->n_sp; i++) {
		assert(NULL != data->sp_name[i]);
	}

	//Are frequencies present and consistant.
	assert(NULL != data->freq);

	//Check index
	assert(NULL != data->index);
	for (int i = 0; i < data->n_pts; i++) {
		assert(data->index[i] < data->n_unique_pts);
		assert(data->index[i] >= -Nbases || data->index[i] == -INT_MAX);
	}
}


void 
CheckIsSorted_DS(const DATA_SET * data)
{
	int             i;
#ifdef NDEBUG
	return;
#endif

	for (i = 1; i < data->n_unique_pts; i++) {
		assert(lexo((const int **) data->seq, i - 1, i, data->n_sp) <= 0);
	}
}


/*
 * Convert an uncompressed nucleotide dataset into codons.
 */
DATA_SET       *
ConvertNucToCodon(const DATA_SET * data, const int gencode)
{
	DATA_SET       *data_new;
	int             i, j, base, tmp, ngaps;

	CheckIsDataSet(data);

	if (data->compressed == 1)
		return NULL;
    unsigned int ncodons = data->n_pts / 3;
    
    if ( 0 != (data->n_pts % 3)  ){
        fprintf(stderr,
        "#  Warning: sequence length is not divisible by three and so cannot have\n"\
        "# coding structure. It will be trunctated to %d sites (%d codons).\n", 3*ncodons, ncodons);
    }
	data_new = CreateDataSet(ncodons, data->n_sp);

    bool odd_gap_anywhere = false;
	for (i = 0; i < data->n_sp; i++) {
        bool odd_gap_in_sequence = false;
		for (j = 0; j < data_new->n_pts; j++) {
			ngaps = 0;
			tmp = data->seq[i][3 * j] * 16;
			if (tmp == 64)
				ngaps++;
			base = tmp;
			tmp = data->seq[i][3 * j + 1] * 4;
			if (tmp == 16)
				ngaps++;
			base += tmp;
			tmp = data->seq[i][3 * j + 2];
			if (tmp == 4)
				ngaps++;
			base += tmp;
			switch (ngaps) {
			case 0:
				break;
			default:
                if ( ! odd_gap_anywhere ){
                    puts(  "#  Warning: Odd gapping found. Treating entire codon as gap. This may\n"\
                           "# be the result of ambiguous nucleotides being translated into gaps.");
                    odd_gap_anywhere = true;
                }
                if ( ! odd_gap_in_sequence ){ 
				   printf ("#  Warning: Odd gapping in sequence %s,\tcodon sites: ", data->sp_name[i]);
                   odd_gap_in_sequence = true;
                }
                printf("%d ",j);
			case 3:
				base = GapChar(SEQTYPE_CODON);
			}
			data_new->seq[i][j] = base;
			if (-1 == data_new->seq[i][j])
				printf("Got -1 on %d\n", base);
		}
        if ( odd_gap_in_sequence ){fputc('\n',stdout);}
		data_new->sp_name[i] = calloc((size_t) (MAX_SP_NAME + 1), sizeof(char));
		sscanf(data->sp_name[i], "%s", data_new->sp_name[i]);
	}
	data_new->n_bases = 64;
	data_new->seq_type = SEQTYPE_CODON;
	data_new->gencode = gencode;

	CheckIsDataSet(data_new);
	return data_new;
}

DATA_SET *
ConvertCodonToQcoord(DATA_SET * data)
{
	int             seqtype;

	if (NULL==data){return NULL;}
	CheckIsDataSet(data);
	assert(data->seq_type == SEQTYPE_CODON);

	seqtype = data->seq_type;
	for (int i = 0; i < data->n_sp; i++)
		for (int j = 0 ; j < data->n_unique_pts; j++)
			data->seq[i][j] =
				CodonAsQcoord(data->seq[i][j], seqtype, data->gencode);
	for (int i = 0 ; i < data->n_pts; i++)
		if (data->index[i] < 0 && data->index[i] != -INT_MAX) {
			int j = -data->index[i] - 1;
			data->index[i] = -CodonAsQcoord(j, seqtype, data->gencode) - 1;
		}
	data->seq_type = SEQTYPE_CODONQ;
	data->n_bases = NumberPossibleBases(data->seq_type, data->gencode);

	CheckIsDataSet(data);
	return data;
}


double         *
GetBaseFreqs(const DATA_SET * data, const int perspecies)
{
	int             sp, pos, n = 0;
	char            gapchar;
	double         *freq;

	CheckIsDataSet(data);
	if (0 != perspecies) {
		fputs("Warning: perspecies frequencies not implemented\n", stderr);
		exit(EXIT_FAILURE);
	}
	gapchar = GapChar(data->seq_type);

	freq = calloc(data->n_bases, sizeof(double));
	OOM(freq);

	for (sp = 0; sp < data->n_sp; sp++) {
		for (pos = 0; pos < data->n_unique_pts; pos++) {
			if (data->seq[sp][pos] != gapchar) {
				freq[data->seq[sp][pos]] += data->freq[pos];
				n += data->freq[pos];
			}
		}
	}

	for (pos = 0; pos < data->n_pts; pos++) {
		if (data->index[pos] < 0 && data->index[pos] != -INT_MAX) {
			freq[-1 - data->index[pos]]++;
			n++;
		}
	}

	for (pos = 0; pos < data->n_bases; pos++) {
		freq[pos] /= n;
	}

	return freq;
}

//Create a vector of codon frequencies.
// method = 0 Empirical codon frequencies
// 1 F3x4
// 2 F1x4
double         *
CodonBaseFreqs(const DATA_SET * data, const int method,
		   const int perspecies, double *bf)
{
	double         *freqs;
	int             i, j, b;
	float           b3x4[12], b64[64];
	float          *speciesf = NULL;
	double          prob, n;

	CheckIsDataSet(data);

	if (method < 0 || method > 2 || perspecies < 0 || perspecies > 1)
		return NULL;

	freqs = calloc(64, sizeof(double));
	for (i = 0; i < 12; i++)
		b3x4[i] = 0;
	for (i = 0; i < 64; i++)
		b64[i] = 0;
	n = 0;

	if (1 == perspecies) {
		fputs("Warning: using per species frequencies but calculation may be in error!\n", stderr);
		speciesf = calloc(data->n_sp * 13, sizeof(float));
		if (NULL == speciesf)
			return NULL;

		for (i = 0; i < data->n_sp; i++)
			for (j = 0; j < data->n_unique_pts; j++)
				if (data->seq[i][j] != 64) {
					b64[data->seq[i][j]] += data->freq[j];
					n += data->freq[j];
					b = (data->seq[i][j] >> 4) & 3;
					speciesf[i * 13 + b] += data->freq[j];
					b = (data->seq[i][j] >> 2) & 3;
					speciesf[i * 13 + b + 4] += data->freq[j];
					b = (data->seq[i][j]) & 3;
					speciesf[i * 13 + b + 8] += data->freq[j];
					speciesf[i * 13 + 12] += data->freq[j];
				}
		for (i = 0; i < data->n_sp; i++)
			for (j = 0; j < 12; j++) {
				speciesf[i * 13 + j] /= speciesf[i * 13 + 12] * data->n_sp;
				b3x4[j] += speciesf[i * 13 + j];
			}
		for (i = 0; i < data->n_pts; i++)
			if (data->index[i] < 0 && data->index[i] != -INT_MAX) {
				b64[-data->index[i] - 1]++;
				n++;
			}
		if (0 != method)
			n = 1;

	} else {
		for (i = 0; i < data->n_sp; i++)
			for (j = 0; j < data->n_unique_pts; j++)
				if (data->seq[i][j] != 64) {
					b64[data->seq[i][j]] += data->freq[j];
					b = (data->seq[i][j] >> 4) & 3;
					b3x4[b] += data->freq[j];
					b = (data->seq[i][j] >> 2) & 3;
					b3x4[b + 4] += data->freq[j];
					b = (data->seq[i][j]) & 3;
					b3x4[b + 8] += data->freq[j];
					n += data->freq[j];
				}
		for (i = 0; i < data->n_pts; i++)
			if (data->index[i] < 0 && data->index[i] != -INT_MAX) {
				int             codon = -data->index[i] - 1;
				b64[codon]++;
				n++;
				b = (codon >> 4) & 3;
				b3x4[b]++;
				b = (codon >> 2) & 3;
				b3x4[b + 4]++;
				b = (codon) & 3;
				b3x4[b + 8]++;
			}
	}

	if (method == 2) {
		b3x4[0] += b3x4[4] + b3x4[8];
		b3x4[1] += b3x4[5] + b3x4[9];
		b3x4[2] += b3x4[6] + b3x4[10];
		b3x4[3] += b3x4[7] + b3x4[11];
		b3x4[4] = b3x4[8] = b3x4[0];
		b3x4[5] = b3x4[9] = b3x4[1];
		b3x4[6] = b3x4[10] = b3x4[2];
		b3x4[7] = b3x4[11] = b3x4[3];
		n = b3x4[0] + b3x4[1] + b3x4[2] + b3x4[3];
	}
	switch (method) {
	case 0:
		for (i = 0; i < 64; i++)
			freqs[i] = b64[i] / n;
		break;
	case 1:
	case 2:
		for (i = 0; i < 64; i++) {
			freqs[i] = 1.0;
			b = (i >> 4) & 3;
			freqs[i] *= b3x4[b] / n;
			b = (i >> 2) & 3;
			freqs[i] *= b3x4[b + 4] / n;
			b = (i) & 3;
			freqs[i] *= b3x4[b + 8] / n;
		}
	}

	//Deal with ` stop ' codons
		prob = 0.0;
	for (i = 0; i < 64; i++) {
		if (!IsStop(i, data->gencode))
			prob += freqs[i];
		else {
			freqs[i] = 0.0;
		}
	}
	if (method == 0 && fabs(prob = 1.0) < 1e-16) {
		printf
			("There appears to be stop codons in data! (or CodonBaseFreqs is wrong\n");
		exit(0);
	}
	for (i = 0; i < 64; i++)
		freqs[i] /= prob;

	if (NULL != bf) {
		for (i = 0; i < 12; i++) {
			bf[i] = b3x4[i] / n;
		}
	}
	Free(speciesf);

	return freqs;
}

double         *
CreateMGFreqs(const double *pi, const int codonf, const int gencode)
{
	double         *mgfreq, f;
	double          b14[4];
	int             i, j, cdn1;
	assert(NULL != pi);

	if (0 == codonf) {
		fputs("CreateMGFreqs not compatible with codonf=0 (b64 freqs)\n", stderr);
		exit(EXIT_FAILURE);
	}
	mgfreq = calloc(12, sizeof(double));
	for (cdn1 = 0; cdn1 < 64; cdn1++) {
		f = pi[cdn1];

		mgfreq[8 + (cdn1 & 3)] += f;
		mgfreq[4 + ((cdn1 >> 2) & 3)] += f;
		mgfreq[(cdn1 >> 4) & 3] += f;
	}

	for (i = 0; i < 12; i += 4) {
		f = 0.;
		for (j = 0; j < 4; j++) {
			f += mgfreq[i + j];
		}
		for (j = 0; j < 4; j++) {
			mgfreq[i + j] /= f;
		}
	}

	/* Case using F1x4  */
	if (2 == codonf) {
		for (i = 0; i < 4; i++) {
			b14[i] = 0;
		}
		for (i = 0; i < 12; i += 4) {
			for (j = 0; j < 4; j++) {
				b14[j] += mgfreq[i + j];
			}
		}
		for (i = 0; i < 12; i += 4) {
			for (j = 0; j < 4; j++) {
				mgfreq[i + j] = b14[j] / 3.;
			}
		}
	}
	return mgfreq;
}

DATA_SET       *
CombineDatasets(const DATA_SET * data1, const DATA_SET * data2)
{
	DATA_SET       *data, *tmp;
	int             species, site, site2;

	CheckIsDataSet(data1);
	CheckIsDataSet(data2);

	assert(data1->n_sp == data2->n_sp);
	assert(data1->seq_type == data2->seq_type);
	assert(data1->n_bases == data2->n_bases);

	data =
		CreateDataSet(data1->n_unique_pts + data2->n_unique_pts, data1->n_sp);
	data->n_pts = data1->n_pts + data2->n_pts;
	data->seq_type = data1->seq_type;
	data->n_bases = data1->n_bases;
	free(data->index);
	data->index = malloc(data->n_pts * sizeof(int));
	if (NULL == data->index) {
		FreeDataSet(data);
		return NULL;
	}
	for (species = 0; species < data1->n_sp; species++) {
		for (site = 0; site < data1->n_unique_pts; site++) {
			data->seq[species][site] = data1->seq[species][site];
		}
		for (site2 = 0; site2 < data2->n_unique_pts; site++, site2++) {
			data->seq[species][site] = data2->seq[species][site2];
		}
		data->sp_name[species] =
			calloc((size_t) (MAX_SP_NAME + 1), sizeof(char));
		assert(strcmp(data1->sp_name[species], data2->sp_name[species]) == 0);
		sscanf(data1->sp_name[species], "%s", data->sp_name[species]);
	}

	for (site = 0; site < data1->n_unique_pts; site++) {
		data->freq[site] = data1->freq[site];
	}
	for (site2 = 0; site2 < data2->n_unique_pts; site2++, site++) {
		data->freq[site] = data2->freq[site2];
	}

	for (site = 0; site < data1->n_pts; site++) {
		data->index[site] = data1->index[site];
	}
	for (site2 = 0; site2 < data2->n_pts; site2++, site++) {
		if (data2->index[site2] >= 0)
			data->index[site] = data2->index[site2] + data1->n_pts;
		else
			data->index[site] = data2->index[site2];
	}

	sort_data(data);
	tmp = compress_data(data);
	if (NULL == tmp) {
		printf("Error compressing sequence! Returning uncompressed set\n");
		tmp = data;
	} else {
		FreeDataSet(data);
	}
	data = RemoveTrivialObs(tmp);
	if (NULL == data) {
		printf
			("Error removing trivial observations (single chars and all gaps).\nReturning compressed sequence.\n");
		data = tmp;
	} else {
		FreeDataSet(tmp);
	}

	CheckIsDataSet(data);
	return data;
}

double         *
AminoFreqs(const DATA_SET * data, const int perspecies)
{
	int             i, j, nongap = 0;
	double          gapchar;
	double         *f, *speciesf;

	CheckIsDataSet(data);

	if (perspecies < 0 || perspecies > 1)
		return NULL;

	f = calloc(20, sizeof(double));
	if (NULL == f)
		return NULL;

	gapchar = GapChar(SEQTYPE_AMINO);

	if (perspecies == 0) {
		speciesf = malloc(20 * sizeof(double));
		if (NULL == speciesf)
			return NULL;
		for (i = 0; i < data->n_sp; i++) {
			for (j = 0; j < 20; j++)
				speciesf[j] = 0.;
			nongap = 0;
			for (j = 0; j < data->n_unique_pts; j++)
				if (0 <= data->seq[i][j] && data->seq[i][j] < 20) {
					speciesf[data->seq[i][j]] += data->freq[j];
					nongap += data->freq[j];
				}
			for (j = 0; j < 20; j++)
				f[j] += speciesf[j] / nongap;
		}
		for (i = 0; i < 20; i++)
			f[i] /= data->n_sp;
		free(speciesf);

	} else {
		for (i = 0; i < data->n_sp; i++)
			for (j = 0; j < data->n_unique_pts; j++)
				if (0 <= data->seq[i][j] && data->seq[i][j] < 20) {
					f[data->seq[i][j]] += data->freq[j];
					nongap += data->freq[j];
				}
		for (i = 0; i < data->n_pts; i++)
			if (data->index[i] < 0 && data->index[i] != -INT_MAX) {
				f[-data->index[i] - 1]++;
				nongap++;
			}
		for (i = 0; i < 20; i++)
			f[i] /= nongap;
	}


	return f;
}






DATA_SET       *
ExtractSequences(int *seqs, int n_seq, DATA_SET * data)
{
	DATA_SET       *data_new;
	int             i, k;

	CheckIsDataSet(data);

	data_new = CreateDataSet(data->n_pts, n_seq);
	data_new->n_unique_pts = data->n_unique_pts;
	for (i = 0; i < n_seq; i++) {
		for (k = 0; k < data->n_unique_pts; k++) {
			data_new->seq[i][k] = data->seq[seqs[i]][k];
			data_new->freq[k] = data->freq[k];
		}
		data->sp_name[i] = calloc((size_t) (17), sizeof(char));
		sscanf(data->sp_name[seqs[i]], "%s", data->sp_name[i]);
	}
	data_new->seq_type = data->seq_type;
	data_new->n_bases = data->n_bases;
	data_new->compressed = data->compressed;

	CheckIsDataSet(data_new);
	return data_new;
}


DATA_SET       *
CreateDataSet(const int n_size, const int n_sp)
{
	DATA_SET       *data;
	int             a;

	data = malloc(sizeof(DATA_SET));
	OOM(data);
	data->n_pts = n_size;
	data->n_unique_pts = n_size;
	data->n_sp = n_sp;
	data->compressed = 0;

	data->seq_type = -1;
	data->n_bases = -1;

	data->seq = calloc(n_sp, sizeof(int *));
	data->sp_name = calloc(n_sp, sizeof(char *));
	for (a = 0; a < n_sp; a++) {
		data->sp_name[a] = NULL;
		data->seq[a] = calloc((size_t) n_size, sizeof(int));
		OOM(data->seq[a]);
	}

	data->freq = calloc((size_t) n_size, sizeof(double));
	OOM(data->freq);
	for (a = 0; a < n_size; a++)
		data->freq[a] = 1.0;

	data->index = malloc(n_size * sizeof(int));
	OOM(data->index);
	for (a = 0; a < n_size; a++)
		data->index[a] = a;

	return data;
}

DATA_SET *
sort_data(DATA_SET * data)
{
	int             n_pts, l, ir, a, i, j;
	double          tmp = 1.0;
	int            *seq1;
	int            **seq;

	if (NULL==data){return NULL;}
	CheckIsDataSet(data);

	n_pts = data->n_unique_pts;
	if (n_pts < 2)
		return data;
	seq = calloc((size_t)data->n_sp,sizeof(int *));
	seq1 = calloc((size_t) data->n_sp, sizeof(int));
	OOM(seq1);
	for (a = 0; a < data->n_sp; a++)
		seq[a] = data->seq[a];

	l = ((n_pts) >> 1);
	ir = n_pts - 1;

	for (;;) {
		if (l > 0) {
			l--;
			for (a = 0; a < data->n_sp; a++)
				seq1[a] = seq[a][l];
			tmp = data->freq[l];
			UpdateIndex(data, l, -1);
		} else {
			for (a = 0; a < data->n_sp; a++)
				seq1[a] = seq[a][ir];
			tmp = data->freq[ir];
			UpdateIndex(data, ir, -1);
			for (a = 0; a < data->n_sp; a++)
				seq[a][ir] = seq[a][0];
			data->freq[ir] = data->freq[0];
			UpdateIndex(data, 0, ir);
			if (--ir == 0) {
				for (a = 0; a < data->n_sp; a++)
					seq[a][0] = seq1[a];
				data->freq[0] = tmp;
				UpdateIndex(data, -1, 0);
				break;
			}
		}

		i = l;
		j = l + l + 1;
		while (j <= ir) {
			if (j < ir && lexo((const int **) seq, j, j + 1, data->n_sp) < 0)
				j++;

			if (lexo2((const int *) seq1, (const int **) seq, j, data->n_sp) < 0) {
				for (a = 0; a < data->n_sp; a++)
					seq[a][i] = seq[a][j];
				data->freq[i] = data->freq[j];
				UpdateIndex(data, j, i);
				i = j;
				j++;
				j <<= 1;
				j--;
			} else
				break;
		}
		for (a = 0; a < data->n_sp; a++)
			seq[a][i] = seq1[a];
		data->freq[i] = tmp;
		UpdateIndex(data, -1, i);
	}

	for (a = 1; a < data->n_unique_pts; a++) {
		assert(lexo((const int **) seq, a - 1, a, data->n_sp) <= 0);
	}
	for (a = 0; a < data->n_pts; a++)
		assert(data->index[a] < data->n_unique_pts);
	free(seq1);
	free(seq);

	CheckIsDataSet(data);
	CheckIsSorted_DS(data);
	return data;
}

static int 
lexo(const int **seq, const int i, const int j, const int n)
{
	int             a = 0;

	while (a < n && seq[a][i] == seq[a][j])
		a++;

	if (a == n)
		return 0;
	else if (seq[a][i] < seq[a][j])
		return -1;
	else if (seq[a][i] > seq[a][j])
		return 1;

	abort();
}


static int 
lexo2(const int *seq1, const int **seq, const int i, const int n)
{
	int             a = 0;

	while (a < n && seq1[a] == seq[a][i])
		a++;

	if (a == n)
		return 0;
	else if (seq1[a] < seq[a][i])
		return -1;
	else if (seq1[a] > seq[a][i])
		return 1;

	abort();
}


DATA_SET       *
compress_data(const DATA_SET * data)
{
	int             a, b, total = 1;
	int             n_pts;
	DATA_SET       *new;

	CheckIsDataSet(data);
	CheckIsSorted_DS(data);

	for (a = 0; a < data->n_pts; a++)
		assert(data->index[a] < data->n_unique_pts);


	n_pts = data->n_unique_pts;
	for (a = 1; a < n_pts; a++) {
		assert(lexo((const int **) data->seq, a - 1, a, data->n_sp) <= 0);
		if (lexo((const int **) data->seq, a - 1, a, data->n_sp) != 0)
			total++;
	}

	new = CreateDataSet(total, data->n_sp);
	new->n_pts = data->n_pts;
	new->seq_type = data->seq_type;
	new->n_pts = data->n_pts;
	new->n_unique_pts = total;
	new->n_sp = data->n_sp;
	new->n_bases = data->n_bases;
	new->gencode = data->gencode;
	for (a = 0; a < data->n_sp; a++) {
		if (data->sp_name[a] != NULL) {
			new->sp_name[a] = calloc(MAX_SP_NAME + 1, sizeof(int));
			OOM(new->sp_name[a]);
			strcpy(new->sp_name[a], data->sp_name[a]);
		}
	}


	free(new->index);
	new->index = malloc(data->n_pts * sizeof(int));
	for (a = 0; a < data->n_pts; a++)
		new->index[a] = data->index[a];

	for (a = 0; a < data->n_sp; a++)
		new->seq[a][0] = data->seq[a][0];
	new->freq[0] = data->freq[0];
	total = 0;
	for (a = 1; a < n_pts; a++)
		if (lexo((const int **) data->seq, a - 1, a, data->n_sp) != 0) {
			total++;
			for (b = 0; b < data->n_sp; b++)
				new->seq[b][total] = data->seq[b][a];
			UpdateIndex(new, a, total);
			new->freq[total] = data->freq[a];
		} else {
			new->freq[total] += data->freq[a];
			UpdateIndex(new, a, total);
		}

	new->compressed = 1;

	CheckIsDataSet(new);
	return new;
}

static void 
UpdateIndex(DATA_SET * data, const int a, const int b)
{
	int             i;

	assert(NULL != data);

	for (i = 0; i < data->n_pts; i++)
		if (data->index[i] == a)
			data->index[i] = b;
}

DATA_SET       *
RemoveTrivialObs(const DATA_SET * data)
{
	int             total = 0;
	int             gapchar, n_upts;
	int             a, b, i;
	DATA_SET       *new;

	CheckIsDataSet(data);

	n_upts = data->n_unique_pts;
	for (i = 0; i < n_upts; i++)
		if (NumNongaps(data, i) >= 2)
			total++;

	new = CreateDataSet(total, data->n_sp);
	free(new->index);
	new->index = malloc(data->n_pts * sizeof(int));
	for (a = 0; a < data->n_pts; a++)
		new->index[a] = data->index[a];
	new->n_pts = data->n_pts;
	new->seq_type = data->seq_type;
	new->n_unique_pts = total;
	new->n_sp = data->n_sp;
	new->n_bases = data->n_bases;
	new->compressed = data->compressed;
	new->gencode = data->gencode;
	for (a = 0; a < data->n_sp; a++) {
		if (data->sp_name[a] != NULL) {
			new->sp_name[a] = calloc(MAX_SP_NAME + 1, sizeof(int));
			OOM(new->sp_name[a]);
			strcpy(new->sp_name[a], data->sp_name[a]);
		}
	}


	total = 0;
	gapchar = GapChar(data->seq_type);
	for (a = 0; a < n_upts; a++)
		switch (NumNongaps(data, a)) {
		case 0:
			UpdateIndex(new, a, -INT_MAX);
			break;
		case 1:{
				int             singlechar = gapchar;
				for (b = 0; b < data->n_sp; b++)
					if (data->seq[b][a] != gapchar)
						singlechar = data->seq[b][a];
				if (singlechar == gapchar) {
					printf("Something fishy -- all gaps\n");
					exit(EXIT_FAILURE);
				}
				UpdateIndex(new, a, -(singlechar + 1));
				break;
			}
		default:
			CopySiteByIndex(data, a, new, total);
			new->freq[total] = data->freq[a];
			UpdateIndex(new, a, total);
			total++;
			break;
		}

	CheckIsDataSet(new);
	return new;
}


void 
CopySiteByIndex(const DATA_SET * old, const int old_idx, DATA_SET * new, const int new_idx)
{
	int             i;
	CheckIsDataSet(old);
	assert(old->n_sp == new->n_sp);
	assert(old_idx >= 0 && old_idx < old->n_unique_pts);
	assert(new_idx >= 0 && new_idx < new->n_unique_pts);
	assert(old->seq_type == new->seq_type);
	if (SEQTYPE_CODON == old->seq_type) {
		/*
		 * If seqtype is not codon, should these be equal in anycase
		 * (by definition)?)
		 */
		assert(old->gencode == new->gencode);
	}
	for (i = 0; i < old->n_sp; i++) {
		new->seq[i][new_idx] = old->seq[i][old_idx];
	}
	new->freq[new_idx] = 1.;
}

void 
CopySite(const DATA_SET * old, const int oldsite, DATA_SET * new, const int new_site)
{
	int             old_idx;
	CheckIsDataSet(old);

	old_idx = old->index[oldsite];
	if (old_idx >= 0) {
		CopySiteByIndex(old, old_idx, new, new_site);
	} else {
		printf("Called CopySite but data set has been compressed and information about site %d has been lost\n", oldsite);
		exit(EXIT_FAILURE);
	}
}

int 
NumNongaps(const DATA_SET * data, const int site)
{
	int             gapchar, Nchar;
	int             i;
	assert(NULL != data);
	assert(site >= 0 && site < data->n_unique_pts);

	CheckIsDataSet(data);

	gapchar = GapChar(data->seq_type);
	Nchar = 0;
	for (i = 0; i < data->n_sp; i++)
		if (data->seq[i][site] < gapchar)
			Nchar++;

	return (Nchar);
}



void 
FreeDataSet(DATA_SET * data)
{
	int             a;

	CheckIsDataSet(data);

	for (a = 0; a < data->n_sp; a++) {
		if (data->sp_name[a] != NULL)
			free(data->sp_name[a]);
		free(data->seq[a]);
	}

	free(data->seq);
	free(data->sp_name);
	free(data->freq);
	free(data->index);
	free(data);
}


void 
PrintData(const DATA_SET * data)
{
	int             a, b;
	char (*printfun) (int);

	CheckIsDataSet(data);
	
	switch (data->seq_type){
		case SEQTYPE_NUCLEO:
			printfun = NucleoAsChar;
			break;
		case SEQTYPE_AMINO:
			printfun = AminoAsChar;
			break;
		case SEQTYPE_CODON:
		    /* Codons requiring encoding as character or printing as a string */
			err(EXIT_FAILURE,"%s:%d, PrintData. Seqtype codon not handled\n",__FILE__,__LINE__);
			break;
	}
	for (a = 0; a < data->n_sp; a++) {
		for (b = 0; b < data->n_unique_pts; b++)
			printf("%c", (*printfun) (data->seq[a][b]));
		printf("\n");
	}
}

void 
PrintSite(const DATA_SET * data, const int i)
{
	int             j;

	CheckIsDataSet(data);

	for (j = 0; j < data->n_sp; j++)
		printf("%2.2d ", data->seq[j][i]);
	printf("\n");
}



DATA_SET       *
CopyDataSet(const DATA_SET * data)
{
	DATA_SET       *data_new;
	int             i, j;

	CheckIsDataSet(data);

	data_new = CreateDataSet(data->n_unique_pts, data->n_sp);
	if (NULL == data_new)
		return NULL;

	data_new->seq_type = data->seq_type;
	data_new->n_pts = data->n_pts;
	data_new->n_unique_pts = data->n_unique_pts;
	data_new->n_bases = data->n_bases;
	data_new->compressed = data->compressed;
	data_new->n_sp = data->n_sp;
	for (i = 0; i < data->n_sp; i++) {
		data_new->sp_name[i] =
			malloc((1 + strlen(data->sp_name[i])) * sizeof(char));
		strcpy(data_new->sp_name[i], data->sp_name[i]);
		for (j = 0; j < data->n_unique_pts; j++)
			data_new->seq[i][j] = data->seq[i][j];
	}
	for (i = 0; i < data->n_unique_pts; i++)
		data_new->freq[i] = data->freq[i];

	//Index consists of all points, not just the unique ones with
		// which the size of the new data set was specified.
		Free(data_new->index);
	data_new->index = malloc(data->n_pts * sizeof(int));
	OOM(data_new);
	for (i = 0; i < data->n_pts; i++) {
		data_new->index[i] = data->index[i];
	}

	CheckIsDataSet(data_new);
	return data_new;
}


void 
CopySiteToDataSet(const DATA_SET * data, DATA_SET * data_single,
		  const int site)
{
	CheckIsDataSet(data);

	data_single->seq_type = data->seq_type;
	data_single->gencode = data->gencode;
	data_single->n_pts = 1;
	data_single->n_unique_pts = 1;
	data_single->n_bases = data->n_bases;
	data_single->compressed = 0;

	CopySite(data, site, data_single, 0);
	data_single->index[0] = 0;

	CheckIsDataSet(data_single);
}


int 
CountGapsAtSite(const DATA_SET * data, const int i)
{
	int             gaps = 0, gapchar, a;
	int             idx;

	CheckIsDataSet(data);

	idx = data->index[i];
	if (idx == -INT_MAX)
		return data->n_sp;
	else if (idx < 0)
		return (data->n_sp - 1);
	gapchar = GapChar(data->seq_type);
	for (a = 0; a < data->n_sp; a++)
		if (data->seq[a][idx] == gapchar)
			gaps++;

	return gaps;
}

int 
IsSiteSynonymous(const DATA_SET * data, const int i, const int gencode)
{
	int             a, last;
	int             gapchar;
	int             idx;

	CheckIsDataSet(data);

	gapchar = GapChar(data->seq_type);
	idx = data->index[i];
	if (idx < 0)
		//Case of all gaps or single character
			return 1;

	/* Find first non-gap character. */
	last = 0;
	while (last < data->n_sp && data->seq[last][idx] == gapchar) {
		last++;
	}
	/* Case there are no sites, or on last site */
	if (last >= data->n_sp)
		return 1;
	/* Check against rest of sequence */
	for (a = last + 1; a < data->n_sp; a++) {
		if (data->seq[a][idx] != gapchar
		    && IsNonSynonymous(QcoordToCodon(data->seq[last][idx], gencode),
				  QcoordToCodon(data->seq[a][idx], gencode),
				       gencode)) {
			return 0;
		}
	}

	return 1;
}


double 
SiteEntropy(const DATA_SET * data, const int site, const double *pi)
{
	int             i, gapchar;
	double          e = 0.;
	int             siteidx;

	CheckIsDataSet(data);

	siteidx = data->index[site];
	if (siteidx == -INT_MAX)
		//all gaps
			return 0.;
	else if (siteidx < 0)
		//single character
			return (-log(pi[-siteidx - 1]));

	gapchar = GapChar(data->seq_type);
	for (i = 0; i < data->n_sp; i++)
		if (data->seq[i][siteidx] != gapchar)
			e -= log(pi[data->seq[i][siteidx]]);

	return e;
}

int 
IsConserved(const DATA_SET * data, const int i)
{
	int             a, last;
	int             gapchar;
	int             idx;

	CheckIsDataSet(data);

	gapchar = GapChar(data->seq_type);
	idx = data->index[i];
	if (idx < 0)
		//Case of all gaps or single character
			return 1;

	last = 0;
	while (last < data->n_sp && data->seq[last][idx] == gapchar) {
		last++;
	}

	if (last >= data->n_sp)
		return 1;
	for (a = last; a < data->n_sp; a++)
		if (data->seq[a][idx] != gapchar
		    && data->seq[a][idx] != data->seq[last][idx])
			return 0;

	return 1;
}


DATA_SET       *
SelectFromData(const DATA_SET * data, const int *idx, const int n)
{
	int             sp, site, new_sp;
	DATA_SET       *data_new;

	CheckIsDataSet(data);

	assert(NULL != data);
	assert(NULL != idx);
	assert(n > 0);
	for (sp = 0; sp < n; sp++) {
		assert(idx[sp] < data->n_sp);
	}

	data_new = CreateDataSet(data->n_unique_pts, n);
	data_new->seq_type = data->seq_type;
	data_new->n_pts = data->n_pts;
	data_new->n_bases = data->n_bases;

	//Frequencies of observation same as original site
		// (at least for the moment.Could compress further.)
		for (site = 0; site < data->n_unique_pts; site++) {
			data_new->freq[site] = data->freq[site];
		}
	//Sitewise indexes same as original data
		// (again, could remove redundent observations to further
		    // reduce size of set).
		for (site = 0; site < data->n_pts; site++) {
		data_new->index[site] = data->index[site];
	}

	//Copy over data required.
		for (new_sp = 0; new_sp < n; new_sp++) {
		sp = idx[new_sp];
		for (site = 0; site < data->n_unique_pts; site++) {
			data_new->seq[new_sp][site] = data->seq[sp][site];
		}
	}

	//Copy species names
		for (new_sp = 0; new_sp < n; new_sp++) {
		sp = idx[new_sp];
		if (data->sp_name[sp] != NULL) {
			data_new->sp_name[new_sp] =
				malloc((1 + strlen(data->sp_name[sp])) * sizeof(char));
			strcpy(data_new->sp_name[new_sp], data->sp_name[sp]);
		}
	}

	CheckIsDataSet(data_new);
	return data_new;
}

/*
 * Reads sequence data out of file. Returns struct containing data, else
 * returns NULL is io error
 */
DATA_SET       *
read_data(const char *filename, const int seqtype)
{
	FILE           *fp;
	int             i, j;
	int n_sp, n_pts;

	/* Attempt to open data file */
	fp = fopen(filename, "r");
	if (fp == NULL) {
		printf("Can't open data file %s for input!\n", filename);
		return NULL;
	}
	if ( SEQTYPE_NUCLEO!= seqtype && SEQTYPE_AMINO!=seqtype){
		fputs("Can only read nucleotide or amino acid sequences\n",stderr);
		exit(EXIT_FAILURE);
	}

	/* Read in number of species and data points */
	(void) fscanf(fp, "%d %d", &n_sp, &n_pts);
	DATA_SET * data = CreateDataSet(n_pts,n_sp);
	data->seq_type = seqtype;
	data->n_bases = NumberPossibleBases(seqtype,GENCODE_UNIVERSAL);

	if (data->n_pts <= 0) {
		printf("Suspiciously little data, can't do much with %d points!\n", data->n_pts);
		free(data);
		return NULL;
	}
	/* Read species name followed by sequence */
	for (i = 0; i < data->n_sp; i++) {
		data->sp_name[i] = calloc((size_t) (MAX_SP_NAME + 1), sizeof(char));
		OOM(data->sp_name[i]);
		(void) fscanf(fp, "%s", data->sp_name[i]);
		if (data->seq_type == SEQTYPE_NUCLEO)
			data->seq[i] = ReadNucleo(fp, data->n_pts, data->sp_name[i]);
		else if (data->seq_type == SEQTYPE_AMINO)
			data->seq[i] = ReadAmino (fp, data->n_pts, data->sp_name[i]);

		if (data->seq[i] == NULL) {
			printf("Problems reading data, aborting\n");
			for (j = 0; j < i; j++)
				free(data->seq[j]);
			free(data);
			return NULL;
		}
	}
	data->freq = calloc((size_t) data->n_pts, sizeof(double));
	OOM(data->freq);
	for (i = 0; i < data->n_pts; i++)
		data->freq[i] = 1.0;

	data->index = malloc(data->n_pts * sizeof(int));
	OOM(data->index);
	for (i = 0; i < data->n_pts; i++)
		data->index[i] = i;

	(void) fclose(fp);

	return data;
}

/* Save sequence data to file */
int 
save_data(char *filename, DATA_SET * data)
{
	FILE           *fp;
	int             i;

	fp = fopen(filename, "w");
	if (fp == NULL) {
		printf("Can't open file for export.\n");
		return -1;
	}
	if (data->seq_type == SEQTYPE_NUCLEO)
		fprintf(fp, "Nucleo\n");
	else if (data->seq_type == SEQTYPE_AMINO)
		fprintf(fp, "Animo\n");
	else {
		printf(" Don't recognise sequence type in save_data.\n");
		(void) fclose(fp);
		return -1;
	}

	fprintf(fp, "%d %d\n", data->n_sp, data->n_pts);

	for (i = 0; i < data->n_sp; i++) {
		if (data->sp_name[i] == NULL)
			fprintf(fp, "Sp%d\n", i);
		else
			fprintf(fp, "%s\n", data->sp_name[i]);

		if (data->seq_type == SEQTYPE_NUCLEO)
			(void) SaveNucleoSeq(fp, data->seq[i], data->n_pts);
		else if (data->seq_type == SEQTYPE_AMINO)
			(void) save_amino_seq(fp, data->seq[i], data->n_pts);

		fprintf(fp, "\n");
	}

	fclose(fp);
	return 0;
}




/*
 * Reads in sequence if nucleotides and returns array 'W' weak A,T     'S'
 * strong C,G 'R' purine A,G   'Y' pyrimidines C,T 'K' keto T,G     'M' amino
 * A,C
 */
static int     *
ReadNucleo (FILE * fp, int n_pts, const char * name)
{
	int            *seq;
	char            c;
	int             i, j;

	seq = calloc((size_t) n_pts, sizeof(int));
	OOM(seq);

    bool has_ambig_nuc = false;
	for (i = 0; i < n_pts; i++) {
		c = gchar(fp);
		j = ToNucleo(c);


		if (-1 == j) {
            if ( false==has_ambig_nuc ){
               printf("#  Warning: Found unrecognised nucleotide in sequence %s: ",name);
               has_ambig_nuc = true;
            }
            printf("%c(%d) ",c,i);
			j = GapChar(SEQTYPE_NUCLEO);
		}
		seq[i] = j;
	}
    if(has_ambig_nuc){ fputc('\n',stdout); }

	return seq;
}

/* Reads in sequence of animo acids and returns array */
static int     *
ReadAmino(FILE * fp, int n_pts, const char * name)
{
	int            *seq;
	char            c;
	int             i, j;

	seq = calloc((size_t) n_pts, sizeof(int));
	OOM(seq);

    bool has_ambig_nuc = false;
	for (i = 0; i < n_pts; i++) {
		c = gchar(fp);
		j = ToAmino(c);

		if (-1 == j) {
            if ( false==has_ambig_nuc ){
               printf("#  Warning: Found unrecognised nucleotide in sequence %s: ",name);
               has_ambig_nuc = true;
            }
            printf("%c(%d) ",c,i);
			j = GapChar(SEQTYPE_AMINO);
		}
		seq[i] = j;
	}

	return seq;
}


static void 
SaveNucleoSeq(FILE * fp, int *seq, int length)
{
	int             i;

	for (i = 0; i < length; i++) {
		fprintf(fp, "%c", NucleoAsChar(seq[i]));
		if (i % 60 == 59)
			fprintf(fp, "\n");
	}
}

static void 
save_amino_seq(FILE * fp, int *seq, int length)
{
	int             i;

	for (i = 0; i < length; i++) {
		fprintf(fp, "%c", AminoAsChar(seq[i]));
		if (i % 60 == 59)
			fprintf(fp, "\n");
	}
}

int count_sequence_stops ( const int * seq, const int n, const int gencode){
	assert(NULL!=seq);
	assert(n>0);
	assert(IsValidGencode(gencode));

	int nstop = 0;
	for ( int i=0 ; i<n ; i++){
		if (IsStop(seq[i],gencode)){
			nstop++;
		}
	}
	return nstop;
}

int count_alignment_stops ( const DATA_SET * data){
	CheckIsDataSet(data);

	int nstop = 0;
	for ( int sp=0 ; sp<data->n_sp ; sp++){
		nstop += count_sequence_stops (data->seq[sp],data->n_unique_pts,data->gencode);
	}
	return nstop;
}

