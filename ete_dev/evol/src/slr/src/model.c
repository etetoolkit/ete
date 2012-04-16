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
#include <math.h>
#include <float.h>
#include <limits.h>
#include <assert.h>
#include <err.h>
#include <string.h>
#include "model.h"
#include "utility.h"
#include "matrix.h"
#include "gencode.h"

const char * model_branches_string[] = { "fixed", "variable", "proportional"};

void            CalculateF(double *F, const double *d, double *space, const double factor, const int n);
void            GetdQ(MODEL * model, const int param, double *dq);

void 
DoDiagonalOfQ(double *mat, const int n)
{
	int             i, j;

	if (NULL == mat)
		return;

	for (i = 0; i < n; i++) {
		mat[i * n + i] = 0.;
		double rsum = 0.;
		for (j = 0; j < n; j++)
			rsum += mat[i*n+j];
		mat[i*n+i] = -rsum;
	}
}



void 
MakeQ_From_S_stdfreq(double *mat, const double *pi, const int n)
{
	int             i, j;

	assert(NULL != mat);
	assert(NULL != pi);
	assert(n > 0);

	for (i = 0; i < n; i++)
		for (j = 0; j < n; j++)
			mat[i * n + j] *= pi[j];

	DoDiagonalOfQ(mat, n);
}


void 
MakeQ_From_S_WGfreq(double *mat, const double *pi, const int n)
{
	int             i, j;

	assert(NULL != mat);
	assert(NULL != pi);
	assert(n > 0);

	for (i = 0; i < n; i++) {
		if (pi[i] > DBL_EPSILON) {
			for (j = 0; j < n; j++) {
				mat[i * n + j] *= sqrt(pi[j] / pi[i]);
			}
		} else {
			for (j = 0; j < n; j++) {
				mat[i * n + j] = 0;
			}
			//mat[i * n + i] = 1;
		}
	}

	DoDiagonalOfQ(mat, n);
}

void 
MakeQ_From_S_Largetfreq(double *mat, const double *pi, const int n)
{
	int             i, j;

	assert(NULL != mat);
	assert(NULL != pi);
	assert(n > 0);

	for (i = 0; i < n; i++) {
		if (pi[i] > DBL_EPSILON) {
			for (j = 0; j < n; j++) {
				mat[i * n + j] /= pi[i];
			}
		} else {
			for (j = 0; j < n; j++) {
				mat[i * n + j] = 0.;
			}
			//mat[i * n + i] = 1.;
		}
	}

	DoDiagonalOfQ(mat, n);
}

void 
MakeQ_From_S_MGfreq(double *mat, const double *pi, const int n, const int gencode)
{
	int             i, j;
	int             cdn1, cdn2, diff, nuc, pos;

	assert(NULL != mat);
	assert(NULL != pi);
	assert(n > 0);

	/*
	 * Lot of following code reflects that in GetdQ_Codon and should be
	 * refactored
	 */
	for (i = 0; i < n; i++) {
		cdn1 = QcoordToCodon(i, gencode);
		for (j = 0; j < n; j++) {
			if (i == j) {
				continue;
			}
			cdn2 = QcoordToCodon(j, gencode);
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
			} else {
				err(EXIT_FAILURE, "Impossible condition in MakeQ_From_S_MGfreq %s:%d\n", __FILE__, __LINE__);
			}

			mat[i * n + j] *= pi[pos * 4 + nuc];
		}
	}

	DoDiagonalOfQ(mat, n);
}


int 
MakeSym_From_Q(double *mat, const double *pi, const int n)
{
	int             i, j;
	assert(NULL != mat);
	assert(NULL != pi);
	assert(n > 0);

	for (i = 0; i < n; i++) {
		if (pi[i] > DBL_MIN)
			for (j = 0; j < n; j++) {
				if (pi[j] > DBL_MIN) {
					mat[i * n + j] *= sqrt(pi[i] / pi[j]);
				}
			}
		else {
			for (j = 0; j < n; j++) {
				mat[i * n + j] = 0.;
				mat[j * n + i] = 0.;
			}
			mat[i * n + i] = 1.;
		}

	}

	return 0;
}



extern double   t[];
void 
MakeFactQ_FromFactSym(double *ev, double *inv_ev, double *v, const double *pi, const int n)
{
	int             i, j;
	assert(NULL != ev);
	assert(NULL != inv_ev);
	assert(NULL != v);
	assert(NULL != pi);
	assert(n > 0);

	/*
	 * Know that all eigenvectors must be less than zero. Make sure they
	 * are
	 */
	for (i = 0; i < n; i++)
		if (v[i] > 0.) {
			v[i] = 0.;
		}
	/*
	 * Output from LAPACK routine is transpose of ev. Want both ev and
	 * inv_ev to be what ev would have been
	 */
	//NormalizeRows(ev, n);
	TransposeMatrix(ev, inv_ev, n);
	CopyMatrix(inv_ev, ev, n);


	for (i = 0; i < n; i++)
		if (pi[i] > DBL_MIN)
			for (j = 0; j < n; j++) {
				inv_ev[i * n + j] *= sqrt(pi[i]);
				ev[i * n + j] /= sqrt(pi[i]);
			}
}



/* space required n*n + 3n	 */
void 
FactorizeMatrix(double *mat, const int n, double *ev, double *v, double *space)
{
	double         *ri, *vi;
	int             i;

	ri = space;
	space += n;
	vi = space;
	space += n * n;
	if (NULL == mat || NULL == ev || NULL == v || NULL == space || n < 1)
		return;

	for (i = 0; i < n * n; i++)
		ev[i] = mat[i];
	Factorize(ev, v, n);

}


/* space required n */
double         *
MakeP_From_FactQ(const double *v, const double *ev, const double *inv_ev, const double length, const double rate, const double scale, double *p, const int n, double *space, const double *pi, const double *q)
{
	int             i, j;
	double         *expl, *tmp;
	double          ev1;

	if (NULL == v || NULL == ev || NULL == inv_ev || n < 1 || length < 0.)
		return NULL;

	if (NULL == p) {
		p = malloc(n * n * sizeof(double));
		if (NULL == p)
			return NULL;
	}
	if (length * rate * scale < -DBL_EPSILON) {
		err(EXIT_FAILURE,"Error. lrs less than zero. len=%e, rate=%e scale=%e\n", length, rate, scale);
	}

	expl = space;
	space += n;
	tmp = space;
	space += n;
	ev1 = 0.;
	for (i = 0; i < n; i++) {
		expl[i] = exp(length * rate * scale * v[i]);
		if (expl[i] > ev1 && fabs(1. - expl[i]) > DBL_EPSILON)
			ev1 = expl[i];
	}

	/*
	 * Does largest ev dominate. If so, we are at equilibrium. Return
	 * matrix with equilibrium distribution as rows. This is actually
	 * horrid hack, should test (1+n_pi_equal_to_zero)th largest expl[i]
	 * to be very small rather than trying to divine it by looking at
	 * whether the ev's are close to 1. or not.
	 */
	/*if (fabs(ev1) < 1e-8) {
		for (i = 0; i < n; i++)
			for (j = 0; j < n; j++)
				p[i * n + j] = pi[j];
		return p;
	}*/
	for (i = 0; i < n; i++)
		for (j = 0; j < n; j++)
			p[i * n + j] = ev[i * n + j] * expl[j];

	/*
	 * Multiplying MD by M^1. Note that M^1 is stored as its transpose,
	 * for efficiency.
	 */
	Matrix_MatrixT_Mult(p, n, n, inv_ev, n, n, tmp);
	for (i = 0; i < n * n; i++)
		p[i] = tmp[i];


	return p;
}

double         *
GetQ(MODEL * model)
{
	if (model->updated)
		model->Getq(model);
	return model->q;
}


extern double   t[];
double         *
GetP(MODEL * model, const double length, double *mat)
{
	int             nbase;
	double         *tmp;

	if ( NULL==mat){
		mat = calloc(model->nbase*model->nbase,sizeof(double));
	}
	nbase = model->nbase;
	if (model->updated) {
		model->Getq(model);
		model->updated = 0;
		model->factorized = 0;
	}
	if (!model->factorized) {
		tmp = model->space;
		model->space += nbase * nbase;
		CopyMatrix(model->q, tmp, nbase);
		MakeSym_From_Q(tmp, model->pi, nbase);
		FactorizeMatrix(tmp, nbase, model->ev, model->v, model->space);
		model->space = tmp;
		MakeFactQ_FromFactSym(model->ev, model->inv_ev, model->v, model->pi, nbase);
		model->Getq(model);
		model->factorized = 1;

	}
	const double lenfact = (Branches_Proportional==model->has_branches)?model->param[0]:1.0;
	MakeP_From_FactQ(model->v, model->ev, model->inv_ev, lenfact*length, Rate(model), Scale(model), mat, nbase, model->space, model->pi, model->q);

	return mat;
}

MODEL          *
NewModel(const int n, const int nparam)
{
	MODEL          *model;

	model = malloc(sizeof(MODEL));
	if (NULL == model) {
		return NULL;
	}
	model->p = malloc((size_t) (n * n * sizeof(double)));
	model->q = malloc((size_t) (n * n * sizeof(double)));
	model->ev = malloc(n * n * sizeof(double));
	model->inv_ev = malloc(n * n * sizeof(double));
	model->v = malloc(n * sizeof(double));
	model->space = malloc((2 * n * n + 3 * n) * sizeof(double));
	model->scale = 1.0;
	model->nbase = n;
	model->updated = 1;
	model->factorized = 0;
	model->pi = NULL;
	model->mgfreq = NULL;
	model->param = malloc(nparam * sizeof(double));
	model->tmp_plik = NULL;

	model->dq = malloc(n * n * sizeof(double));
	model->F = malloc(n * n * sizeof(double));
	model->dp = malloc(n * n * sizeof(double));

	if (NULL == model->q || NULL == model->p || NULL == model->ev ||
	NULL == model->inv_ev || NULL == model->v || NULL == model->space ||
	    NULL == model->param || NULL == model->dq ||
	    NULL == model->F || NULL == model->dp) {
		FreeModel(model);
		return NULL;
	}
	model->pt_freq = NULL;
	model->index = NULL;

	model->has_branches = Branches_Fixed;
	model->optimize_pi = 0;
	model->alternate_scaling = 0;

	return model;
}


void 
FreeModel(MODEL * model)
{
	if (NULL != model) {
		Free(model->q);
		Free(model->p);
		Free(model->ev);
		Free(model->inv_ev);
		Free(model->v);
		Free(model->space);
		Free(model->pi);
		Free(model->mgfreq);
		Free(model->param);
		Free(model->tmp_plik);

		Free(model->F);
		Free(model->dp);
		Free(model->dq);

		Free(model);
	}
}

void 
MakeDerivFromP(MODEL * model, const double blen, double *bmat)
{
	double         *tmp, *dp;
	double          factor;

	const unsigned int n = model->nbase;
	tmp = model->space;
	dp = bmat;

	factor = Scale(model) * Rate(model) * blen;
	const double sfactor = (Branches_Proportional==model->has_branches)?model->param[0]:1.;
	CalculateF(model->F, model->v, model->space, sfactor*factor, n);

	/* Calculate A1 = S^{-1} dQ S */
	/* Hadamard conjugate (A2 = F.A1) */
	HadamardMult(model->dq, model->F, n);
	/* Calculate A3 = S A2 S^{-1} */
	Matrix_MatrixT_Mult(model->F, n, n, model->inv_ev, n, n, tmp);

	Matrix_Matrix_Mult(model->ev, n, n, tmp, n, n, dp);
	/* Multiply through by factor */
	for (unsigned int i = 0; i < n * n; i++)
		dp[i] *= factor;

}

void MakeRateDerivFromP ( MODEL * model, const double blen, double * dp){
	assert(NULL!=model);
	assert(blen>=0.);
	assert(NULL!=dp);
	assert(Branches_Proportional==model->has_branches);

	const unsigned int nbase = model->nbase;

	GetQ(model);
	GetP(model,blen,model->p);
	GetQP(model->q,model->p,dp,nbase);
	for ( unsigned int i=0 ; i<nbase*nbase ; i++){
		dp[i] *= blen * Scale(model);
	}
}

void 
MakeSdQS(MODEL * model, const int param)
{
	int             n;
	double         *tmp;

	n = model->nbase;
	tmp = model->space;

	GetdQ(model, param, model->q);
	Matrix_Matrix_Mult(model->dq, n, n, model->ev, n, n, tmp);
	MatrixT_Matrix_Mult(model->inv_ev, n, n, tmp, n, n, model->dq);

}




/*
 * Calculates the F matrix needed to get analytic derivatives.
 */
void 
CalculateF(double *F, const double *d, double *space, const double factor, const int n)
{
	int             i, j;

	for (i = 0; i < n; i++)
		space[i] = exp(d[i] * factor);

	/* Construct F. Matrix is symmetric */
	for (i = 0; i < n; i++)
		for (j = 0; j <= i; j++) {
			if (fabs(factor * (d[i] - d[j])) > DBL_EPSILON)
				F[i * n + j] = (space[i] - space[j]) / (factor * (d[i] - d[j]));
			else
				F[i * n + j] = space[i];
		}
	for (i = 0; i < n; i++)
		for (j = 0; j < i; j++)
			F[j * n + i] = F[i * n + j];
}

void 
GetdQ(MODEL * model, const int n, double *q)
{
	model->GetdQ(model, n, q);
}

void 
GetQP(const double *Q, const double *P, double *QP, const int n)
{
	Matrix_Matrix_Mult(Q, n, n, P, n, n, QP);
}


void 
ParamToPi(const double *param, double *pi, const int npi)
{
	double          sum;
	assert(NULL != param);
	assert(NULL != pi);
	assert(npi > 0);

	/*
	 * for ( int i=0 ; i<npi-1 ; i++){ pi[i] = param[i]; } return;
	 */

	pi[0] = 1.;
	sum = 1.;
	for (int i = 1; i < npi; i++) {
		pi[i] = param[i - 1];
		sum += param[i - 1];
	}
	for (int i = 0; i < npi; i++) {
		pi[i] /= sum;
	}
}

void 
PiToParam(const double *pi, double *param, const int npi)
{
	assert(NULL != param);
	assert(NULL != pi);
	assert(npi > 0);

	/*
	 * for ( int i=0 ; i<npi-1 ; i++){ param[i] = pi[i]; } return;
	 */

	for (int i = 1; i < npi; i++) {
		param[i - 1] = pi[i] / pi[0];
	}
}

void 
dPidParam_param(const double *param, double *dpidparam, const int npi)
{
	double          A;
	assert(NULL != param);
	assert(NULL != dpidparam);
	assert(npi >= 0);


	A = 1.;
	for (int i = 0; i < npi - 1; i++) {
		A += param[i];
	}

	for (int p = 0; p < npi - 1; p++) {
		for (int pi = 0; pi < npi; pi++) {
			if (0 == pi) {
				dpidparam[p * npi + pi] = -1. / (A * A);
				continue;
			}
			if (pi - 1 == p) {
				dpidparam[p * npi + pi] = (A - param[pi - 1]) / (A * A);
				continue;
			}
			dpidparam[p * npi + pi] = -param[pi - 1] / (A * A);
		}
	}
}

void 
dPidParam_pi(const double *pi, double *dpidparam, const int npi)
{
	assert(NULL != pi);
	assert(NULL != dpidparam);
	assert(npi >= 0);

	/*
	 * for ( int i=0 ; i<(npi-1)*npi ; i++) dpidparam[i] = 0.; for ( int
	 * i=0 ; i<npi-1 ; i++) dpidparam[i*npi+i] = 1.; return;
	 */

	for (int i = 0; i < npi - 1; i++) {
		for (int j = 0; j < npi; j++) {
			if (0 == j) {
				dpidparam[i * npi + j] = -pi[0] * pi[0];
				continue;
			}
			if (j - 1 == i) {
				dpidparam[i * npi + j] = (1. - pi[j]) * pi[0];
				continue;
			}
			dpidparam[i * npi + j] = -pi[j] * pi[0];
		}
	}
}

void 
CheckModelDerivatives(MODEL * model, const double blen, const double *param, const double delta)
{
	int             nparam, pioffset, nbase;
	double         *p_test, *dp_test;

	assert(NULL != model);
	assert(NULL != param);
	assert(blen >= 0.);
	assert(delta >= 0.);

	nparam = model->nparam;
	nbase = model->nbase;
	pioffset = model->nparam - model->nbase + 1;
	p_test = calloc(nbase * nbase, sizeof(double));
	dp_test = calloc((nparam + 1) * nbase * nbase, sizeof(double));

	for (int i = 0; i < nparam; i++) {
		model->Update(model, param[i], i);
	}

	/* Get analytic derivatives, interms of S-params and (perhaps) pi's */
	GetP(model,blen,model->p);
	for (int i = 0; i < nparam; i++) {
		if ( Branches_Proportional==model->has_branches && 0==i){
			MakeRateDerivFromP(model,blen,dp_test+i*nbase*nbase);
		} else {
			MakeSdQS(model, i);
			MakeDerivFromP(model, blen, dp_test + i * nbase * nbase);
		}
	}
	if (model->optimize_pi) {
		double         *dpidparam, *tmp;
		tmp = calloc((nbase - 1) * nbase * nbase, sizeof(double));
		dpidparam = calloc(nbase * (nbase - 1), sizeof(double));
		dPidParam_pi(model->pi, dpidparam, nbase);
		MakeSdQS(model, nparam);
		MakeDerivFromP(model, blen, dp_test + nparam * nbase * nbase);

		for (int j = 0; j < nbase - 1; j++) {
			for (int base = 0; base < nbase; base++) {
				for (int i = 0; i < nbase * nbase; i++) {
					tmp[j * nbase * nbase + i] += dp_test[(base + pioffset) * nbase * nbase + i] * dpidparam[j * nbase + base];
				}
			}
		}
		for (int j = 0; j < nbase - 1; j++) {
			for (int i = 0; i < nbase * nbase; i++) {
				dp_test[(j + pioffset) * nbase * nbase + i] = tmp[j * nbase * nbase + i];
			}
		}
		free(dpidparam);
		free(tmp);
	}
	for (int i = 0; i < nparam; i++) {
		double          sumsqrdiff = 0., sumsqrsum = 0.;

		model->Update(model, param[i] + delta, i);
		GetP(model, blen, model->p);
		memcpy(p_test, model->p, nbase * nbase * sizeof(double));

		model->Update(model, param[i] - delta, i);
		GetP(model, blen, model->p);
		for (int j = 0; j < model->nbase * model->nbase; j++) {
			p_test[j] -= model->p[j];
			p_test[j] /= 2 * delta;
			sumsqrdiff += (p_test[j] - dp_test[i * nbase * nbase + j]) * (p_test[j] - dp_test[i * nbase * nbase + j]);
			sumsqrsum += (p_test[j] + dp_test[i * nbase * nbase + j]) * (p_test[j] + dp_test[i * nbase * nbase + j]);
		}
		printf("param %d (%e): sumsqr = %e\tdiff = %e\t%e %e\n", i, param[i], sumsqrsum, sumsqrdiff,p_test[0],dp_test[i*nbase*nbase]);
		model->Update(model, param[i], i);
	}

	free(p_test);
	free(dp_test);
}
