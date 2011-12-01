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
#include <math.h>
#include <limits.h>
#include <float.h>
#include "gencode.h"
#include "model.h"
#include "bases.h"
#include "codonmodel.h"
#include "utility.h"
#include "data.h"
#include "utility.h"
#include "matrix.h"
#include <assert.h>
#include <err.h>


void            Update_Codon_singleDnDs(MODEL * model, double p, int i);
void            Update_Codon_single(MODEL * model, double p, int i);
void            Update_Codon_full(MODEL * model, double p, int i);
double          Scale_Codon_single(MODEL * model);
double          Rate_Codon(MODEL * model);
double          Scale_Codon(MODEL * model);
double          GetParam_Codon_singleDnDs(MODEL * model, int i);
double          GetParam_Codon_single(MODEL * model, int i);
double          GetParam_Codon_full(MODEL * model, int i);
void            GetQ_Codon(MODEL * model);
double         *GetS_Codon(double *mat, double kappa, double omega, int gencode);
double          CodonOmegaFunc_GY(int i, int j, int gencode, double omega);
double          CodonOmegaFunc_YN(int i, int j, int gencode, double omega);
double          CodonOmegaFunc_Trad(int i, int j, int gencode, double omega);
double          CodonOmegaDFunc_GY(int i, int j, int gencode, double omega);
double          CodonOmegaDFunc_YN(int i, int j, int gencode, double omega);
double          CodonOmegaDFunc_Trad(int i, int j, int gencode, double omega);
double          NucleoFunc_Trad(int i, int j);
double          NucleoFunc_Empirical(int i, int j);
int             FindAmino(int a);
void            GetdQ_Codon(MODEL * model, int n, double *q);
void            GetdQ_Codon_single(MODEL * model, int n, double *q);
void            GetdQ_Codon_singleDnDs(MODEL * model, int n, double *q);

double          CodonNeutScale = -1.;

double          (*CodonOmegaFunc) (int, int, int, double) = CodonOmegaFunc_Trad;
double          (*CodonOmegaDFunc) (int, int, int, double) = CodonOmegaDFunc_Trad;
double          (*NucleoFunc) (int, int) = NucleoFunc_Trad;
double         *AminoParam;
double         *NucleoParam;




double          NucleoParam_GY_Nov2003[6] =
{1.430297e+00, 1.098538e+00, 8.583175e-01, 1.356069e+00, 8.964170e-01,
1.0};
double          AminoParam_YN_Aug2003[75] =
{7.246981e-01, 1.172268e+00, 9.984862e-01, 6.918285e-01, 1.119923e+00,
	7.342144e-01, 1.093398e+00, 9.163887e-01, 9.258153e-01, 3.689281e-01, 1.117877e+00, 9.666899e-01,
	8.665321e-01, 7.172281e-01, 1.036078e+00, 7.999008e-01, 8.178675e-01, 1.175573e+00, 1.101923e+00,
	1.632942e+00, 1.190617e+00, 1.284592e+00, 8.129305e-01, 1.246469e+00, 7.808750e-01, 9.804973e-01,
	1.061974e+00, 1.325889e+00, 9.899367e-01, 8.584490e-01, 1.021484e+00, 1.260317e+00, 1.417204e+00,
	1.255548e+00, 8.538310e-01, 8.561884e-01, 1.190469e+00, 1.155259e+00, 7.158043e-01, 8.713178e-01,
	1.062488e+00, 9.738178e-01, 1.164306e+00, 1.279585e+00, 1.219570e+00, 1.032123e+00, 1.287629e+00,
	1.691095e+00, 8.098733e-01, 1.335368e+00, 1.075144e+00, 1.004477e+00, 1.592494e+00, 1.655791e+00,
	1.149040e+00, 1.068516e+00, 1.405100e+00, 9.940865e-01, 8.231903e-01, 1.448649e+00, 2.091072e+00,
	7.927921e-01, 1.161951e+00, 6.347661e-01, 8.120879e-01, 1.178658e+00, 1.482881e+00, 1.262502e+00,
7.766948e-01, 1.728667e+00, 1.347645e+00, 8.128504e-01, 1.151783e+00, 1.017869e+00, 1.073362e+00};
double          AminoParam_GY_Jul2003[75] =
{6.835927e-01, 1.209163e+00, 9.952726e-01, 6.380563e-01, 1.147592e+00,
	6.916782e-01, 1.110758e+00, 8.949536e-01, 9.215446e-01, 3.098561e-01, 1.139620e+00, 9.515103e-01,
	8.349999e-01, 6.606077e-01, 1.041374e+00, 7.547796e-01, 7.866363e-01, 1.206560e+00, 1.123561e+00,
	1.817343e+00, 1.232033e+00, 1.346350e+00, 7.784764e-01, 1.306142e+00, 7.398674e-01, 9.749373e-01,
	1.079480e+00, 1.406613e+00, 9.872082e-01, 8.361083e-01, 1.022391e+00, 1.324936e+00, 1.518539e+00,
	1.317973e+00, 8.279554e-01, 8.313834e-01, 1.233493e+00, 1.197644e+00, 6.717507e-01, 8.455513e-01,
	1.075794e+00, 9.598423e-01, 1.200579e+00, 1.344447e+00, 1.262965e+00, 1.035998e+00, 1.351633e+00,
	1.882542e+00, 7.709710e-01, 1.417736e+00, 1.090398e+00, 1.000074e+00, 1.747740e+00, 1.826574e+00,
	1.187643e+00, 1.077477e+00, 1.494502e+00, 9.920281e-01, 7.984678e-01, 1.563178e+00, 2.370527e+00,
	7.582842e-01, 1.191066e+00, 5.778130e-01, 7.737373e-01, 1.209538e+00, 1.598847e+00, 1.313805e+00,
7.414139e-01, 1.902686e+00, 1.423158e+00, 7.801932e-01, 1.194610e+00, 1.020845e+00, 1.094042e+00};
double          AminoParam_GYemp_Nov2003[75] =
{7.737833e-01, 1.220770e+00, 1.035662e+00, 7.042135e-01, 1.086157e+00,
	7.680027e-01, 1.175832e+00, 9.352375e-01, 9.984958e-01, 3.007928e-01, 1.076708e+00, 1.092336e+00,
	8.174411e-01, 6.994509e-01, 1.088471e+00, 8.128131e-01, 8.024236e-01, 1.437222e+00, 1.065822e+00,
	1.577826e+00, 1.159208e+00, 1.374619e+00, 7.926101e-01, 1.290983e+00, 7.921278e-01, 1.051153e+00,
	1.090887e+00, 1.451640e+00, 1.015597e+00, 9.042904e-01, 1.078779e+00, 1.374507e+00, 1.484140e+00,
	1.390131e+00, 8.815731e-01, 7.614190e-01, 1.189809e+00, 1.119326e+00, 7.348799e-01, 9.133559e-01,
	1.086405e+00, 1.005420e+00, 1.263204e+00, 1.389563e+00, 1.297804e+00, 1.098671e+00, 1.380120e+00,
	1.581971e+00, 8.199853e-01, 1.337614e+00, 1.122506e+00, 9.865101e-01, 1.648070e+00, 1.719274e+00,
	1.152722e+00, 1.112156e+00, 1.383218e+00, 9.736752e-01, 8.731189e-01, 1.515785e+00, 2.490438e+00,
	6.945752e-01, 1.160155e+00, 5.578432e-01, 7.624124e-01, 1.192739e+00, 1.485196e+00, 1.257224e+00,
8.024160e-01, 1.995234e+00, 1.381933e+00, 7.594042e-01, 1.100241e+00, 1.022193e+00, 1.062310e+00};
int             AminoMap[75] =
{60, 57, 61, 56, 64, 131, 134, 120, 121, 135, 129, 122, 132, 107, 106, 112,
	109, 114, 37, 38, 77, 75, 76, 67, 11, 30, 33, 31, 29, 96, 91, 92, 101, 99, 54, 50, 46, 53,
	20, 15, 18, 5, 3, 22, 27, 21, 24, 25, 180, 177, 181, 171, 178, 174, 184, 183, 155, 161,
168, 156, 157, 166, 119, 105, 115, 118, 7, 137, 151, 140, 143, 146, 87, 88, 82};

void
SetAminoAndCodonFuncs(const int nucleo_type, const int amino_type, const char *nucleofile, const char *aminofile)
{
	FILE           *fp;
	int             Err = 0, i;
	double         *aminos = NULL, *nucleos = NULL;

	/* Dealt with Nucleotide */
	switch (nucleo_type) {
	case 0:
		NucleoFunc = NucleoFunc_Trad;
		break;
	case 1:
		NucleoFunc = NucleoFunc_Empirical;

		if (NULL != nucleofile) {
			printf("# Reading nucleotide substitution parameters from %s\n", nucleofile);
			fp = fopen(nucleofile, "r");
			if (NULL == fp) {
				printf("# Reading failed\n");
				nucleofile = NULL;
			}
		}
		if (NULL == nucleofile) {
			printf("# Falling back to default nucleotide substitution parameter file\n");
			fp = fopen("NucleoParam", "r");
		}
		if (NULL != fp) {
			nucleos = malloc(6 * sizeof(double));
			Err = ReadVectorFromOpenFile(nucleos, 5, fp);
			nucleos[5] = 1.;
			for (i = 0; i < 5; i++)
				if (nucleos[i] < 0.) {
					Err = EOF;
					printf
						("# Read invalid data. Nucleotide parameter %d is less than zero.\n",
						 i + 1);
				}
			if (EOF == Err)
				free(nucleos);
		}
		if (NULL == fp || EOF == Err) {
			printf("# Reading failed. Falling back to default values\n");
			NucleoParam = NucleoParam_GY_Nov2003;
		}
		break;
	default:
		printf("# Unrecognised nucleo_type. Using traditional model.\n");
		NucleoFunc = NucleoFunc_Trad;
	}

	Err = 0;
	/* Deal with amino acids */
	switch (amino_type) {
	case 0:
		CodonOmegaFunc = CodonOmegaFunc_Trad;
		CodonOmegaDFunc = CodonOmegaDFunc_Trad;
		return;
	case 1:
		CodonOmegaFunc = CodonOmegaFunc_GY;
		CodonOmegaDFunc = CodonOmegaDFunc_GY;
		break;
	case 2:
		CodonOmegaFunc = CodonOmegaFunc_YN;
		CodonOmegaDFunc = CodonOmegaDFunc_YN;
		break;
	default:
		printf("# Unrecogonised amino_type. Using traditional model.\n");
		CodonOmegaFunc = CodonOmegaFunc_Trad;
		CodonOmegaDFunc = CodonOmegaDFunc_Trad;
		return;
	}

	if (NULL != aminofile) {
		printf("# Reading amino acid substitution parameters from %s\n", aminofile);
		fp = fopen(aminofile, "r");
		if (NULL == fp) {
			printf("# Reading failed\n");
			aminofile = NULL;
		}
	}
	if (NULL == aminofile) {
		if (2 == amino_type)
			aminofile = "AminoParam_YN";
		else if (1 == amino_type) {
			if (1 == nucleo_type)
				aminofile = "AminoParam_GYemp";
			else
				aminofile = "AminoParam_GY";
		}
		printf("# Falling back to default amino acid substition parameter file\n");
		fp = fopen(aminofile, "r");
	}
	if (NULL != fp) {
		aminos = malloc(75 * sizeof(double));
		Err = ReadVectorFromOpenFile(aminos, 75, fp);
		for (i = 0; i < 75; i++)
			if (aminos[i] < 0.) {
				Err = EOF;
				printf
					("# Read invalid data. Amino parameter %d is less than zero.\n",
					 i + 1);
			}
		if (EOF == Err)
			free(aminos);
	}
	if (NULL == fp || EOF == Err) {
		printf("# Reading failed. Falling back to default values\n");
		if (2 == amino_type)
			AminoParam = AminoParam_YN_Aug2003;
		else if (1 == amino_type) {
			if (1 == nucleo_type)
				AminoParam = AminoParam_GYemp_Nov2003;
			else
				AminoParam = AminoParam_GY_Jul2003;
		}
	}
}


double
CodonOmegaFunc_GY(int i, int j, int gencode, double omega)
{
	int             ai, aj, t;

	/* Convert to amino acids */
	ai = CodonToAmino(i, gencode);
	aj = CodonToAmino(j, gencode);
	if (ai == aj)
		return 1.0;
	t = LowerTriangularCoordinate(ai, aj, 20);

	t = FindAmino(t);

	omega = (omega > 0.) ? omega : 1e-16;
	return pow(omega, AminoParam[t]);
}

double
CodonOmegaDFunc_GY(int i, int j, int gencode, double omega)
{
	int             ai, aj, t;

	/* Convert to amino acids */
	ai = CodonToAmino(i, gencode);
	aj = CodonToAmino(j, gencode);
	if (ai == aj)
		return 0.0;
	t = LowerTriangularCoordinate(ai, aj, 20);

	t = FindAmino(t);

	omega = (omega > 0.) ? omega : 1e-16;

	return (AminoParam[t] * pow(omega, (AminoParam[t] - 1.)));
}

double
CodonOmegaFunc_YN(int i, int j, int gencode, double omega)
{
	int             ai, aj, t;

	if (fabs(1. - omega) <= DBL_EPSILON)
		return 1.0;
	/* Convert to amino acids */
	ai = CodonToAmino(i, gencode);
	aj = CodonToAmino(j, gencode);
	if (ai == aj)
		return 1.0;
	t = LowerTriangularCoordinate(ai, aj, 20);
	t = FindAmino(t);

	omega = (omega > 0.) ? omega : 1e-16;

	return (log(omega) * AminoParam[t] /
		(-expm1(-log(omega) * AminoParam[t])));
}

double
CodonOmegaDFunc_YN(int i, int j, int gencode, double omega)
{
	int             ai, aj, t;

	if (fabs(1. - omega) <= DBL_EPSILON)
		return 1.0;
	/* Convert to amino acids */
	ai = CodonToAmino(i, gencode);
	aj = CodonToAmino(j, gencode);
	if (ai == aj)
		return 1.0;
	t = LowerTriangularCoordinate(ai, aj, 20);
	t = FindAmino(t);

	omega = (omega > 0.) ? omega : 1e-16;

	return (AminoParam[t] *
		((1. - pow(omega, -AminoParam[t])) / omega -
		 AminoParam[t] * log(omega) * pow(omega,
					      -AminoParam[t] - 1.)) / ((1. -
									pow
								     (omega,
								  AminoParam
								      [t]))
								     * (1. -
									pow
								     (omega,
								  AminoParam
								    [t]))));
}
double
CodonOmegaFunc_Trad(int i, int j, int gencode, double omega)
{
	return omega;
}

double
CodonOmegaDFunc_Trad(int i, int j, int gencode, double omega)
{
	return 1.;
}

double
NucleoFunc_Trad(int i, int j)
{
	return 1.;
}

double
NucleoFunc_Empirical(int i, int j)
{
	int             t = 0;

	while (t < 3 && (i & 3) == (j & 3)) {
		t++;
		i >>= 2;
		j >>= 2;
	}
	t = UpperTriangularCoordinate((i & 3), (j & 3), 4);


	return NucleoParam[t];
}



double         *
GetS_Codon(double *mat, double kappa, double omega, int gencode)
{
	int             nbase;
	int             i, j, ib, jb;

	nbase = NumberSenseCodonsInGenCode(gencode);
	if (-1 == nbase)
		return NULL;

	if (NULL == mat) {
		mat = malloc(nbase * nbase * sizeof(double));
		if (NULL == mat)
			return NULL;
	}
	for (i = 0; i < nbase; i++)
		mat[i * nbase + i] = 0.;
	/*
	 * Construct codon S matrix, using the symmetric property to reduce
	 * the complexity constant of the algorithm. This method can be
	 * improved on considerably by only consider one nucleotide mutations
	 * rather than all the possible changes and then zero those that
	 * require more than one mutation.
	 */
	for (i = 0; i < 64; i++) {
		ib = CodonToQcoord(i, gencode);
		if (!IsStop(i, gencode)) {
			for (j = 0; j < i; j++) {
				jb = CodonToQcoord(j, gencode);
				if (i != j && !IsStop(j, gencode)) {
					if (NumberNucChanges(i, j) > 1) {
						mat[ib * nbase + jb] = 0.;
					} else if (NumberNucChanges == 0)
						printf("Error!\n");
					else {
						mat[ib * nbase + jb] = NucleoFunc(i, j);
						if (HasTransition(i, j))
							mat[ib * nbase + jb] *= kappa;
						if (IsNonSynonymous(i, j, gencode)) {
							mat[ib * nbase + jb] *= CodonOmegaFunc(i, j, gencode, omega);
						}
					}
					mat[jb * nbase + ib] = mat[ib * nbase + jb];
				}
			}
		}
	}

	return mat;
}




void
GetQ_Codon(MODEL * model)
{
	double         *mat;
	int             n;

	n = model->nbase;
	mat = model->q;
	const unsigned int paramoffset = (Branches_Proportional==model->has_branches)?1:0;
	const double kappa = model->param[0+paramoffset];
	const double omega = model->param[1+paramoffset];

	mat = GetS_Codon(mat, kappa, omega, model->gencode);
	if (NULL == mat)
		return;

	switch (model->freq_type) {
	case 0:
		MakeQ_From_S_stdfreq(mat, model->pi, n);
		break;
	case 1:
		MakeQ_From_S_WGfreq(mat, model->pi, n);
		break;
	case 2:
		MakeQ_From_S_MGfreq(mat, model->mgfreq, n, model->gencode);
		break;
	case 3:
		MakeQ_From_S_Largetfreq(mat, model->pi, n);
		break;
	default:
		fprintf(stderr, "%s:%d freq_type not recognised\n", __FILE__, __LINE__);
		fflush(stderr);
		exit(EXIT_FAILURE);
	}

	model->scale = 0.;
	if (model->alternate_scaling) {
		for (int i = 0; i < n; i++) {
			model->scale -= mat[i * n + i];
		}
		model->scale /= model->nbase;
	} else {
		for (int i = 0; i < n; i++) {
			model->scale -= mat[i * n + i] * model->pi[i];
		}
	}
	model->scale = 1. / model->scale;
	assert(model->scale>0);

	return;
}

double
Scale_Codon(MODEL * model)
{
	return model->scale;
}

double
Rate_Codon(MODEL * model)
{
	return 1.0;
}

double
Rate_Codon_singleDnDs(MODEL * model)
{
	return model->param[2];
}

void
Update_Codon(MODEL * model, double p, int i)
{
	assert(i >= 0 && i < model->nparam);

	model->param[i] = p;
	model->updated = 1;
}

MODEL          *
NewCodonModel(const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type, const enum model_branches branopt)
{
	int             n;
	MODEL          *model;
	
	const unsigned int nparam = (Branches_Proportional==branopt)?3:2;
	n = NumberSenseCodonsInGenCode(gencode);
	model = NewModel(n, nparam);
	if (NULL != model) {
		model->gencode = gencode;
		model->Getq = GetQ_Codon;
		model->Scale = Scale_Codon;
		model->Rate = Rate_Codon;
		model->Update = Update_Codon;
		model->GetParam = GetParam_Codon_full;
		model->GetdQ = GetdQ_Codon;

		model->param[0] = 1.; /* scale param. Overwritten if nparam=2*/
		model->param[nparam-2] = kappa;
		model->param[nparam-1] = omega;
		model->seqtype = SEQTYPE_CODON;
		model->nparam = nparam;

		model->has_branches = branopt;

		model->pi = GetEquilibriumDistCodon(pi, codonf, gencode);
		model->freq_type = freq_type;
		if (freq_type == 2) {
			model->mgfreq = CreateMGFreqs(pi, codonf, gencode);
		}
	}
	return model;
}


MODEL          *
NewCodonModel_single(const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type)
{
	MODEL          *model;

	model = NewCodonModel(gencode, kappa, omega, pi, codonf, freq_type, Branches_Fixed);

	model->nparam = 1;
	model->Scale = Scale_Codon_single;
	model->Update = Update_Codon_single;
	model->GetParam = GetParam_Codon_single;
	model->GetdQ = GetdQ_Codon_single;

	return model;
}

MODEL          *
NewCodonModel_singleDnDs(const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type)
{
	MODEL          *model;

	model = NewCodonModel(gencode, kappa, omega, pi, codonf, freq_type, Branches_Fixed);

	model->nparam = 2;
	model->Scale = Scale_Codon_single;
	model->Update = Update_Codon_singleDnDs;
	model->GetParam = GetParam_Codon_singleDnDs;
	model->GetdQ = GetdQ_Codon_singleDnDs;
	model->Rate = Rate_Codon_singleDnDs;

	return model;
}



void
Update_Codon_single(MODEL * model, double p, int i)
{

	if (i != 0)
		return;
	model->param[1] = p;
	model->updated = 1;
}

void
Update_Codon_singleDnDs(MODEL * model, double p, int i)
{
	if (i < 0 || i > 1)
		return;
	model->param[i + 1] = p;
	/* i=0 Change omega, i=1 change rate (no need to recalculate matrix */
	if (0 == i)
		model->updated = 1;
}

double
Scale_Codon_single(MODEL * model)
{
	double          omega;
	if (CodonNeutScale < 0) {
		omega = model->param[1];
		model->param[1] = 1.0;
		model->Getq(model);
		CodonNeutScale = model->scale;
		model->param[1] = omega;
		model->updated = 1;
	}
	return CodonNeutScale;
}


double
GetScale_single(MODEL * model, const double f)
{
	double          omega, scale;

	omega = model->param[1];
	model->param[1] = f;
	model->Getq(model);
	scale = model->scale;
	model->param[1] = omega;
	model->updated = 1;

	return scale;
}

double
GetParam_Codon_full(MODEL * model, int i)
{
	assert(i >= 0 && i < model->nparam);
	return model->param[i];
}


double
GetParam_Codon_single(MODEL * model, int i)
{
	return (model->param[1]);
}

double
GetParam_Codon_singleDnDs(MODEL * model, int i)
{
	assert(i >= 0 && i < 2);
	return (model->param[i - 1]);
}


int
FindAmino(int a)
{
	int             i = 0;

	while (i < 75 && AminoMap[i] != a) {
		i++;
	}

	if (i == 75)
		return -1;
	return i;
}


void
GetdQ_Codon_single(MODEL * model, int n, double *q)
{
	if (n != 0)
		return;
	else
		GetdQ_Codon(model, 1, q);
}

void
GetdQ_Codon_singleDnDs(MODEL * model, int n, double *q)
{
	int             i, j, nbase;
	double          s;


	switch (n) {
	case 0:		/* dQ/dw  */
		GetdQ_Codon(model, 1, q);
		break;
	case 1:		/* dQ/drate */
		nbase = model->nbase;
		s = Scale(model);
		for (i = 0; i < model->nbase; i++) {
			for (j = 0; j < model->nbase; j++) {
				model->dq[i * nbase + j] = model->q[i * nbase + j] * s;
			}
		}
		break;
	}

}




void
GetdQ_Codon(MODEL * model, int param, double *q)
{
	int             tran, nonsyn;
	double         *mat;
	double          ds, s;
	int             diff, pos, nuc;

	const unsigned int nbase = model->nbase;
	const unsigned int nparam = model->nparam;
	const unsigned int gencode = model->gencode;
	mat = model->dq;
	s = Scale(model);

	const unsigned int paramoffset = (Branches_Proportional==model->has_branches)?1:0;
	const double kappa = model->param[0+paramoffset];
	const double omega = model->param[1+paramoffset];

	if (param<0 || param>=nparam)
		return;

	double scalefact = 1.;
	if ( Branches_Proportional==model->has_branches){
		model->Getq(model);
		if ( 0 == param){
			CopyMatrix(model->q,mat,nbase);
			for ( unsigned int i=0 ; i<nbase*nbase ; i++){
				mat[i] *= s;
			}
			return;
		} else {
			param--;
		}
		scalefact = model->param[0];
	}
	for (int i = 0; i < nbase * nbase; i++)
		mat[i] = 0.;
	for (int i = 0; i < 64; i++) {
		int ai = CodonToQcoord(i, gencode);
		if (!IsStop(i, gencode)) {
			for (int j = 0; j < i; j++) {
				int aj = CodonToQcoord(j, gencode);
				if (i != j && !IsStop(j, gencode) && NumberNucChanges(i, j) < 2) {
					tran = 0;
					nonsyn = 0;
					if (HasTransition(i, j))
						tran = 1;
					if (IsNonSynonymous(i, j, gencode)) {
						nonsyn = 1;
					}
					if (param == 0 && tran == 1) {
						mat[ai * nbase + aj] = NucleoFunc(i, j);
						if (nonsyn == 1)
							mat[ai * nbase + aj] *= CodonOmegaFunc(i, j, gencode, omega);
					} else if (param == 1 && nonsyn == 1) {
						mat[ai * nbase + aj] =
							NucleoFunc(i, j) * CodonOmegaDFunc(i, j, gencode, omega);
						if (tran == 1)
							mat[ai * nbase + aj] *= kappa;
					}
					mat[aj * nbase + ai] = mat[ai * nbase + aj];
				}
			}
		}
	}

	switch (model->freq_type) {
	case 0:
		for (int i = 0; i < nbase; i++)
			for (int j = 0; j < nbase; j++)
				mat[i * nbase + j] *= model->pi[j];
		break;

	case 1:
		for (int i = 0; i < nbase; i++) {
			if (model->pi[i] > DBL_EPSILON) {
				for (int j = 0; j < nbase; j++)
					mat[i * nbase + j] *= sqrt(model->pi[j] / model->pi[i]);
			} else {
				for (int j = 0; j < nbase; j++)
					mat[i * nbase + j] = 0.;
			}
		}
		break;

	case 2:
		for (int i = 0; i < nbase; i++) {
			int cdn1 = QcoordToCodon(i, model->gencode);
			for (int j = 0; j < nbase; j++) {
				if (i == j) {
					continue;
				}
				int cdn2 = QcoordToCodon(j, model->gencode);
				diff = cdn1 ^ cdn2;
				if ((diff & 3) != 0) {
					pos = 2;
					nuc = cdn2 & 3;
				} else if (((diff >> 2) & 3) != 0) {
					pos = 1;
					nuc = (cdn2 >> 2) & 3;
				} else if (((diff >> 4) & 3) != 0) {
					pos = 0;
					nuc = (cdn2 >> 4) & 3;
				}
				mat[i * nbase + j] *= model->mgfreq[pos * 4 + nuc];
			}
		}
		break;

	case 3:
		for (int i = 0; i < nbase; i++) {
			if (model->pi[i] > DBL_EPSILON) {
				for (int j = 0; j < nbase ; j++) {
					mat[i * nbase + j] /= model->pi[i];
				}
			} else {
				for (int j = 0; j < nbase; j++) {
					mat[i * nbase + j] = 0.;
				}
			}
		}
		break;

	default:
		fprintf(stderr, "Unrecognised freq_type in %s:%d\n", __FILE__, __LINE__);
		exit(EXIT_FAILURE);
	}

	DoDiagonalOfQ(mat, nbase);

	ds = 0.;
	for (int i = 0; i < nbase; i++)
		ds += model->pi[i] * mat[i * nbase + i];
	ds *= s;

	for (int i = 0; i < nbase; i++)
		for (int j = 0; j < nbase; j++)
			mat[i * nbase + j] = scalefact * (mat[i * nbase + j] + ds * q[i * nbase + j]);

}


MODEL          *
NewCodonModel_full(const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type, const enum model_branches branopt)
{
	int             n;
	MODEL          *model;

	const unsigned int nparam = (Branches_Proportional==branopt)?3:2;
	n = NumberSenseCodonsInGenCode(gencode);
	model = NewModel(n, nparam);
	if (NULL != model) {
		model->gencode = gencode;
		model->Getq = GetQ_Codon;
		model->Scale = Scale_Codon;
		model->Rate = Rate_Codon;
		model->Update = Update_Codon_full;
		model->GetParam = GetParam_Codon_full;
		model->GetdQ = GetdQ_Codon;

		model->param[0] = 1.; /*  Scale parameter. Overwriten if nparam=2 */
		model->param[nparam-2] = kappa;
		model->param[nparam-1] = omega;
		model->seqtype = SEQTYPE_CODON;
		model->nparam = nparam;

		model->has_branches = branopt;

		model->pi = GetEquilibriumDistCodon(pi, codonf, gencode);

		model->freq_type = freq_type;
		if (freq_type == 2) {
			model->mgfreq = CreateMGFreqs(pi, codonf, gencode);
		}
	}
	return model;
}

void
Update_Codon_full(MODEL * model, double p, int i)
{

	if (i < 0 || i >=model->nparam) {
		return;
	}
	model->param[i] = p;
	model->updated = 1;
}

double         *
GetEquilibriumDistCodon(const double *pi, const int codonf, const int gencode)
{
	double         *eq, *api;
	double          b34[12];
	double         *tpi;
	int             cdn, pos, nuc;

	tpi = calloc(64, sizeof(double));
	if (NULL == tpi) {
		err(EXIT_FAILURE, "Out of memory %s:%d\n", __FILE__, __LINE__);
	}
	if (codonf == 1 || codonf == 2) {
		for (pos = 0; pos < 12; pos++) {
			b34[pos] = 0.;
		}
		for (cdn = 0; cdn < 64; cdn++) {
			nuc = cdn & 3;
			b34[8 + nuc] += pi[cdn];
			nuc = (cdn >> 2) & 3;
			b34[4 + nuc] += pi[cdn];
			nuc = (cdn >> 4) & 3;
			b34[nuc] += pi[cdn];
		}

		/* F1x4 case */
		if (codonf == 2) {
			for (nuc = 0; nuc < 4; nuc++) {
				b34[nuc] += b34[4 + nuc];
			}
			for (nuc = 0; nuc < 4; nuc++) {
				b34[nuc] += b34[8 + nuc];
			}
			for (nuc = 0; nuc < 4; nuc++) {
				b34[nuc] /= 3;
				b34[4 + nuc] = b34[nuc];
				b34[8 + nuc] = b34[nuc];
			}
		}
		for (cdn = 0; cdn < 64; cdn++) {
			tpi[cdn] = b34[8 + (cdn & 3)] * b34[4 + ((cdn >> 2) & 3)] * b34[(cdn >> 4) & 3];
		}
	} else {
		for (cdn = 0; cdn < 64; cdn++) {
			tpi[cdn] = pi[cdn];
		}
	}

	api = GetAminoFrequencies(pi, gencode);


	eq = calloc(NumberSenseCodonsInGenCode(gencode), sizeof(double));
	if (NULL == eq) {
		err(EXIT_FAILURE, "Out of memory %s:%d\n", __FILE__, __LINE__);
	}
	for (cdn = 0; cdn < 64; cdn++) {
		if (!IsStop(cdn, gencode)) {
			eq[CodonToQcoord(cdn, gencode)] = tpi[cdn];
		}
	}
	free(tpi);

	(void)norm_vector(eq, NumberSenseCodonsInGenCode(gencode), 1.0);

	return eq;
}
