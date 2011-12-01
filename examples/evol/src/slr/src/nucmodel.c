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
#include "model.h"
#include "bases.h"
#include "matrix.h"
#include <assert.h>
#include <err.h>
#include <math.h>
#include <float.h>

void            GetQ_Nuc(MODEL * model);
void            GetS_JC69(double *mat, MODEL * model);
void            GetS_NNN(double *mat, MODEL * model);
double          Scale_Nuc(MODEL * model);
double          Rate_Nuc(MODEL * model);
void            Update_Nuc(MODEL * model, double p, int i);
double          GetParam_Nuc(MODEL * model, int i);
void            GetdQ_JC69(MODEL * model, int n, double *q);
void            GetdQ_NNN(MODEL * model, int n, double *q);



MODEL          *
NewJC69Model_full(int nbr)
{
	MODEL          *model;

	model = NewModel(4, 0);
	if (NULL != model) {
		model->Getq = GetQ_Nuc;
		model->Gets = GetS_JC69;
		model->Scale = Scale_Nuc;
		model->Rate = Rate_Nuc;
		model->Update = Update_Nuc;
		model->GetParam = GetParam_Nuc;
		model->GetdQ = GetdQ_JC69;

		model->seqtype = SEQTYPE_NUCLEO;
		model->nparam = 0;
		model->has_branches = Branches_Variable;

		model->pi = calloc(4, sizeof(double));
		for (int i = 0; i < 4; i++) {
			model->pi[i] = 0.25;
		}
		model->freq_type = 0;
	}
	return model;
}

MODEL          *
NewNNNModel_full(const int *desc, const double *params, const int nparam, const double *pi, const int freq_type, const int nbr, const int alt_scale, const int opt_pi)
{
	MODEL          *model;
	int             tnparam;

	assert(NULL != desc);
	assert(NULL != params);
	assert(nparam >= 0);
	assert(NULL != pi);
	assert(nbr >= 0);
	assert(alt_scale == 0 || alt_scale == 1);

	tnparam = opt_pi ? (nparam + 3) : nparam;
	model = NewModel(4, tnparam);
	if (NULL == model) {
		warn("NewModel returned NULL at %s:%d. Trying to continue.\n", __FILE__, __LINE__);
		return NULL;
	}
	model->Getq = GetQ_Nuc;
	model->Gets = GetS_NNN;
	model->Scale = Scale_Nuc;
	model->Rate = Rate_Nuc;
	model->Update = Update_Nuc;
	model->GetParam = GetParam_Nuc;
	model->GetdQ = GetdQ_NNN;

	model->seqtype = SEQTYPE_NUCLEO;
	model->has_branches = (nbr>0)?Branches_Variable:Branches_Fixed;
	model->desc = desc;
	model->nparam = tnparam;
	model->alternate_scaling = alt_scale;
	model->optimize_pi = opt_pi;
	for (int i = 0; i < nparam; i++) {	/* pi's are special */
		model->param[i] = params[i];
	}
	if ( opt_pi){
		for (int i = 1; i < model->nbase; i++) {
			model->param[nparam + i - 1] = pi[i] / pi[0];
		}
	}

	model->pi = calloc(4, sizeof(double));
	for (int i = 0; i < 4; i++) {
		model->pi[i] = pi[i];
	}
	model->freq_type = freq_type;

	return model;
}

void 
GetQ_Nuc(MODEL * model)
{
	double         *mat;
	int             n;

	assert(NULL != model);

	mat = model->q;
	n = model->nbase;

	model->Gets(mat, model);
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
		err(EXIT_FAILURE, "MGfreq not applicable for nucleotide models\n");
	case 3:
		MakeQ_From_S_Largetfreq(mat, model->pi, n);
		break;
	default:
		err(EXIT_FAILURE, "Frequency type %d not recognised at %s:%d\n", model->freq_type, __FILE__, __LINE__);
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

	return;
}

void 
GetS_JC69(double *mat, MODEL * model)
{
	int             n;

	assert(NULL != mat);
	assert(NULL != model);
	n = model->nbase;

	/* Diagonals of this matrix ignored later on */
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			mat[i * n + j] = 1.;
		}
	}
}

void 
GetS_NNN(double *mat, MODEL * model)
{
	int             n;

	assert(NULL != mat);
	assert(NULL != model);
	n = model->nbase;

	/* Diagonals calculated later */
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			int             param = model->desc[i * n + j];
			if (param == -1) {
				mat[i * n + j] = 1.;
			} else {
				mat[i * n + j] = model->param[param];
			}
		}
	}
}

double 
Scale_Nuc(MODEL * model)
{
	assert(NULL != model);
	return model->scale;
}

double 
Rate_Nuc(MODEL * model)
{
	return 1.;
}

void 
Update_Nuc(MODEL * model, double p, int i)
{
	int             pioffset;
	assert(NULL != model);
	assert(i >= 0 && i < model->nparam);

	pioffset = model->nparam - model->nbase + 1;
	model->param[i] = p;

	if (model->optimize_pi && i >= pioffset) {
		ParamToPi(model->param + pioffset, model->pi, model->nbase);
	}
	model->updated = 1;
}

double 
GetParam_Nuc(MODEL * model, int i)
{
	assert(NULL != model);
	assert(i >= 0 && i < model->nparam);

	return model->param[i];
}

void 
GetdQ_JC69(MODEL * model, int n, double *q)
{
	/*  Does model have scaling factor  */
	if ( Branches_Proportional==model->has_branches && 0==n){
		model->Getq(model);
		CopyMatrix(q,model->dq,model->nbase);
		const double s = Scale(model);
		for ( unsigned int i=0 ; i<model->nbase*model->nbase ; i++){
			model->dq[i] *= s;
		}
	} else {
		warn("Called GetdQ for JC69, which has no parameters!\n");
	}
	return;
}

/*
 * Function desperately needs refactoring -- attempt to do derivatives
 * analytically is becoming messy
 */
void 
GetdQ_NNN(MODEL * model, int p, double *q)
{
	double          s, ds;
	double         *dmat;
	int             n, pioffset;

	assert(NULL != model);
	assert(p >= 0);		/* Limit may be more than model->nparam since
				 * pi params are dealt with differently */
	assert(NULL != q);

	n = model->nbase;
	pioffset = model->nparam - model->nbase + 1;
	dmat = model->dq;
	s = Scale(model);
	model->Getq(model);

	if ( Branches_Proportional == model->has_branches && 0==p){
		CopyMatrix(model->q,dmat,n);
		for (unsigned int i=0 ; i<n*n ; i++){
			dmat[i] *= s;
		}
		return;
	}
	if (model->optimize_pi && p >= pioffset) {
		int             base = p - pioffset;
		assert(base >= 0 && base < model->nbase);
		model->Gets(dmat, model);
		switch (model->freq_type) {
		case 0:	/* Standard freqs */
			for (int i = 0; i < n; i++) {
				for (int j = 0; j < n; j++) {
					if (j != base) {
						dmat[i * n + j] = 0.;
					}
				}
			}
			break;
		case 1:	/* GWF freqs */
			for (int i = 0; i < n; i++) {
				for (int j = 0; j < n; j++) {
					if (i == j) {
						dmat[i * n + j] = 0.;
						continue;
					}
					if (i == base && model->pi[i] > DBL_EPSILON) {
						dmat[i * n + j] *= -0.5 * sqrt(model->pi[j] / model->pi[i]) / model->pi[i];
						continue;
					}
					if (j == base && model->pi[i] > DBL_EPSILON && model->pi[j] > DBL_EPSILON) {
						dmat[i * n + j] *= 0.5 / sqrt(model->pi[i] * model->pi[j]);
						continue;
					}
					dmat[i * n + j] = 0.;
				}
			}
			break;
		case 2:	/* MG freqs */
			err(EXIT_FAILURE, "Err in %s:%d. Called with MG freqs.\n", __FILE__, __LINE__);
			break;
		case 3:	/* Larget freqs */
			for (int i = 0; i < n; i++) {
				for (int j = 0; j < n; j++) {
					if (i == base && model->pi[i] > DBL_EPSILON) {
						dmat[i * n + j] /= model->pi[i] * model->pi[i] * -1.;
						continue;
					}
					dmat[i * n + j] = 0.;
				}
			}
		}
	} else {
		if ( Branches_Proportional==model->has_branches){
			assert(0!=p);
			p--;
		}
		for (int i = 0; i < n; i++) {
			for (int j = 0; j < n; j++) {
				if (model->desc[i * n + j] != p) {
					dmat[i * n + j] = 0.;
				} else {
					dmat[i * n + j] = 1.;
				}
			}
		}

		switch (model->freq_type) {
		case 0:	/* Standard freqs */
			for (int i = 0; i < n; i++) {
				for (int j = 0; j < n; j++) {
					dmat[i * n + j] *= model->pi[j];
				}
			}
			break;
		case 1:	/* GWF freqs */
			for (int i = 0; i < n; i++) {
				if (model->pi[i] > DBL_EPSILON) {
					for (int j = 0; j < n; j++) {
						dmat[i * n + j] *= sqrt(model->pi[j] / model->pi[i]);
					}
				} else {
					for (int j = 0; j < n; j++) {
						dmat[i * n + j] *= 0.;
					}
				}
			}
			break;
		case 2:	/* MG freqs */
			err(EXIT_FAILURE, "Err in %s:%d. Called with MG freqs.\n", __FILE__, __LINE__);
			break;
		case 3:	/* Larget freqs */
			for (int i = 0; i < n; i++) {
				if (model->pi[i] > DBL_EPSILON) {
					for (int j = 0; j < n; j++) {
						dmat[i * n + j] /= model->pi[i];
					}
				} else {
					for (int j = 0; j < n; j++) {
						dmat[i * n + j] = 0.;
					}
				}
			}
			break;
		default:
			err(EXIT_FAILURE, "Unrecognised frequency type %d in %s:%d\n", model->freq_type, __FILE__, __LINE__);
		}
	}

	DoDiagonalOfQ(dmat, n);

	ds = 0.;
	if (model->alternate_scaling) {
		for (int i = 0; i < n; i++) {
			ds += dmat[i * n + i];
		}
		ds /= model->nbase;
	} else {
		for (int i = 0; i < n; i++)
			ds += model->pi[i] * dmat[i * n + i];
		if (model->optimize_pi && p >= pioffset) {
			int             base = p - pioffset;
			ds += q[base * n + base];
		}
	}
	ds *= s;

	for (int i = 0; i < n; i++)
		for (int j = 0; j < n; j++)
			dmat[i * n + j] = (dmat[i * n + j] + ds * q[i * n + j]);

	return;
}
