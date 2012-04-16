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
#include <err.h>
#include "tree.h"
#include "model.h"
#include "bases.h"
#include "utility.h"
#include "options.h"
#include "matrix.h"
#include "like.h"
#include "data.h"
#include "tree_data.h"
#include <limits.h>
#include <assert.h>


#define EVERY		20
#define SCALE		1


double          CalcLike_Single(const double *param, void *data);
void            UpdateAllParams(MODEL * model, TREE * tree, const double *p);
void            UpdateParam(MODEL * model, TREE * tree, const double p, const int i);
void            GradLike_Single(double *param, double *grad, void *data);
double *        GradLike_Full(const double *param, double *grad, void *data);
double *        InfoLike_Full(const double *param, double *info, void *data);
double          LikeFun_Single(TREE * tree, MODEL * model, double *p);
void            GradLike2(TREE * tree, MODEL * model, double *p, double *grad);
void            Backwards(NODE * node, NODE * parent, TREE * tree, MODEL * model);
void            DoDerivatives(MODEL * model, TREE * tree, double *grad, double *lvec);
void
DoBranchDerivatives(MODEL * model, const TREE * tree, double *grad,
		    double *lvec, double lscale);
void
DoModelDerviatives(MODEL * model, TREE * tree, double *grad,
		   double *lvec, double lscale);

static double   GetParam(MODEL * model, TREE * tree, int i);





int
CalcLike_Sub(NODE * node, NODE * parent, TREE * tree, MODEL * model)
{
	double         *result;
	double         *tmp1;
	double         *tmp2;
	double          max;
	int             a, b, c;

	node->scalefactor = 0.0;
	node->scale = 0;

	if (ISLEAF(node)) {
		/*
		 * Have to possible options, largely depending on whether we
		 * have the possibility of a probability distribution at each
		 * leaf tip rather than exact observations
		 */
		a = find_connection(node, parent);
		GetP(model, node->blength[a], node->mat);

		if (model->exact_obs == 1) {
			tmp2 = parent->plik;
			tmp1 = node->mid;
			for (a = 0; a < model->n_unique_pts; a++) {
				if (node->seq[a] != GapChar(model->seqtype))
					for (b = 0; b < model->nbase; b++) {
						*tmp1++ = node->mat[node->seq[a] + b * model->nbase];
						*tmp2++ *= node->mat[node->seq[a] + b * model->nbase];
					}
				else {
					for (b = 0; b < model->nbase; b++)
						*tmp1++ = 1.0;
					tmp2 += model->nbase;
				}
			}
		} else {
			for (a = 0; a < model->n_unique_pts; a++) {
				result = node->mid + a * model->nbase;
				/* Zero results array */
				for (b = 0; b < model->nbase; b++)
					result[b] = 0;
				/*
				 * Main loop, using pointer addition to keep
				 * track of indices
				 */
				tmp2 = node->mat;
				for (b = 0; b < model->nbase; b++) {
					tmp1 = node->plik;
					tmp1 += a * model->nbase;
					for (c = 0; c < model->nbase; c++)
						result[b] += (*tmp1++) * (*tmp2++);
				}
				/* Multiply parent like by result */
				tmp1 = parent->plik;
				tmp1 += a * model->nbase;

				for (b = 0; b < model->nbase; b++) {
					*tmp1++ *= result[b];
				}
			}
		}

		parent->scale += 1;

		return 0;
	}
	/*
	 * Now we are not at leaf, so we must recurse down the tree if we
	 * can. Firstly, turn likelihood array into 1's
	 */
	tmp1 = node->plik;
	for (a = 0; a < model->nbase * model->n_unique_pts; a++)
		tmp1[a] = 1.0;

	a = -1;
	while (++a < node->nbran && CHILD(node, a) != NULL)
		if (CHILD(node, a) != parent) {
			(void) CalcLike_Sub(CHILD(node, a), node, tree, model);
		}
	/*
	 * Now we've recursed down the tree, we must do all the calculations
	 * for this node.
	 */
	if (parent == NULL)
		return 0;

	//Scale on this node
		if (1 == SCALE && node->scale > EVERY) {
		max = 0.0;
		for (a = 0; a < model->n_unique_pts * model->nbase; a++)
			if (node->plik[a] > max)
				max = node->plik[a];
		for (a = 0; a < model->n_unique_pts * model->nbase; a++)
			node->plik[a] /= max;
		node->scalefactor += log(max);
		node->scale = 0;
	}
	a = find_connection(node, parent);
	GetP(model, node->blength[a], node->mat);
	Matrix_MatrixT_Mult(node->plik, model->n_unique_pts, model->nbase, node->mat, model->nbase, model->nbase, node->mid);
	tmp1 = parent->plik;
	tmp2 = node->mid;
	for (b = 0; b < model->nbase * model->n_unique_pts; b++)
		tmp1[b] *= tmp2[b];

	parent->scale += node->scale + 1;
	parent->scalefactor += node->scalefactor;

	return 0;
}


int
LikeVector(TREE * tree, MODEL * model, double *p)
{
	static double  *p_tmp = NULL;
	static int      last_nupts = 0;

	if (model->n_unique_pts > last_nupts) {
		if (p_tmp != NULL)
			free(p_tmp);
		p_tmp = malloc(model->n_unique_pts * sizeof(double));
		OOM(p_tmp);
		last_nupts = model->n_unique_pts;
	}
	(void) LikeVectorSub(tree, model, p);

	return 0;
}

int
LikeVectorSub(TREE * tree, MODEL * model, double *p)
{
	int             a, b;
	double         *plik, *freq;

	(void) CalcLike_Sub(tree->tree, NULL, tree, model);
	plik = (tree->tree)->plik;
	freq = model->pi;
	for (a = 0; a < model->n_unique_pts; a++) {
		p[a] = 0.;
		for (b = 0; b < model->nbase; b++) {
			if (*plik < 0.) {
				*plik = 0.;
			}
			if (!finite(*plik)) {
				*plik = 0.;
			}
			p[a] += *plik++ * freq[b];
		}
	}

	return 0;
}

double
LikeDiff(double scale1, double scale2, double like1[], double like2[],
	 double freq[], int size)
{
	int             a;
	double          result = 0.;
	double          tot = 0.;

	for (a = 0; a < size; a++) {
		result += freq[a] * log(like1[a] / like2[a]);
		tot += freq[a];
	}
	result += tot * (scale1 - scale2);

	return result;
}


double
Like(double scale, double like[], double freq[], int usize, double *pi, int nsize, int *index)
{
	int             a;
	double          result = 0, tot = 0;

	for (a = 0; a < usize; a++) {
		if (like[a] > DBL_MIN) {
			result += freq[a] * log(like[a]);
		} else {
			return -DBL_MAX;
		}
		tot += freq[a];
	}
	result += scale * tot;

	for (a = 0; a < nsize; a++) {
		if (index[a] < 0 && index[a] != -INT_MAX) {
			result += log(pi[-index[a] - 1]);
		}
	}

	return result;
}


/*
 * Returns derivative of log-likelihood function with resprect to parameter i
 */
double
PartialDeriv(TREE * tree, MODEL * model, double *p, int n)
{
	int             i;
	double          d, tot, loglike, *freq;
	double         *space;
	double          scale1, scale2;

	d = GetParam(model, tree, n);
	UpdateParam(model, tree, d + DELTA, n);
	LikeVector(tree, model, p);
	scale1 = (tree->tree)->scalefactor;

	space = p + model->n_unique_pts;
	for (i = 0; i < model->n_unique_pts; i++)
		space[i] = p[i];

	UpdateParam(model, tree, (d > DELTA) ? (d - DELTA) : DBL_EPSILON, n);
	LikeVector(tree, model, p);
	scale2 = (tree->tree)->scalefactor;
	UpdateParam(model, tree, d, n);

	freq = model->pt_freq;
	loglike = 0.0;
	tot = 0.;
	for (i = 0; i < model->n_unique_pts; i++) {
		if (space[i] <= DBL_MIN) {
			return -DBL_MAX;
		}
		if (p[i] <= DBL_MIN)
			return DBL_MAX;
		loglike += freq[i] * log(space[i] / p[i]);
		tot += freq[i];
	}
	loglike += tot * (scale1 - scale2);

	if (d > DELTA)
		loglike /= 2.0 * DELTA;
	else
		loglike /= DELTA + d - DBL_EPSILON;

	return loglike;
}

/* Returns first derivative vector of log-likelihood function */
int
GradLike(TREE * tree, MODEL * model, double p[], double grad[])
{
	int             i, nparam;

	nparam = (Branches_Variable==model->has_branches) ? model->nparam + tree->n_br : model->nparam;
	for (i = 0; i < nparam; i++)
		grad[i] = PartialDeriv(tree, model, p, i);

	return 0;
}

/* Returns the (i,j) 2nd partial derivative of the likelihood function */
double
Partial2Deriv(TREE * tree, MODEL * model, double p[], int a, int b)
{
	static double  *space = NULL;
	static int      size = 0;
	int             i;
	double          d, *freq, loglike, e;
	double          scale, scalepm, scalemp;
	double          scalepp, scalemm;

	if (space == NULL || size < model->n_unique_pts) {
		size = model->n_unique_pts;
		if (space != NULL)
			free(space);
		space = malloc(size * sizeof(double));
	}
	if (a == b) {
		d = GetParam(model, tree, a);
		UpdateParam(model, tree, d + DELTA, a);
		LikeVector(tree, model, p);
		for (i = 0; i < model->n_unique_pts; i++)
			if (p[i] > DBL_MIN)
				space[i] = log(p[i]);
			else
				return -DBL_MAX;
		scalepp = (tree->tree)->scalefactor;
		UpdateParam(model, tree, (d > DELTA) ? (d - DELTA) : DBL_EPSILON, a);
		LikeVector(tree, model, p);
		for (i = 0; i < model->n_unique_pts; i++)
			if (p[i] > DBL_MIN)
				space[i] += log(p[i]);
			else
				return -DBL_MAX;
		scalemm = (tree->tree)->scalefactor;
		UpdateParam(model, tree, d, a);
		LikeVector(tree, model, p);
		scale = (tree->tree)->scalefactor;

		loglike = 0.0;
		d = 0.;
		freq = model->pt_freq;
		for (i = 0; i < model->n_unique_pts; i++) {
			if (p[i] > DBL_MIN)
				loglike += freq[i] * (space[i] - 2.0 * log(p[i]));
			else
				return DBL_MAX;
			d += freq[i];
		}
		loglike += d * (scalepp + scalemm - scale - scale);

		loglike /= DELTA * DELTA;

		UpdateParam(model, tree, d, a);

		return loglike;
	} else {
		d = GetParam(model, tree, a);
		e = GetParam(model, tree, b);

		UpdateParam(model, tree, d + DELTA, a);
		UpdateParam(model, tree, e + DELTA, b);
		LikeVector(tree, model, p);
		for (i = 0; i < model->n_unique_pts; i++)
			space[i] = log(p[i]);
		scalepp = (tree->tree)->scalefactor;

		UpdateParam(model, tree, (d > DELTA) ? (d - DELTA) : DBL_EPSILON, a);
		LikeVector(tree, model, p);
		for (i = 0; i < model->n_unique_pts; i++)
			space[i] -= log(p[i]);
		scalemp = (tree->tree)->scalefactor;

		UpdateParam(model, tree, (e > DELTA) ? (e - DELTA) : DBL_EPSILON, b);
		LikeVector(tree, model, p);
		for (i = 0; i < model->n_unique_pts; i++)
			space[i] += log(p[i]);
		scalemm = (tree->tree)->scalefactor;

		UpdateParam(model, tree, d + DELTA, a);
		LikeVector(tree, model, p);
		for (i = 0; i < model->n_unique_pts; i++)
			space[i] -= log(p[i]);
		scalepm = (tree->tree)->scalefactor;

		freq = model->pt_freq;
		loglike = 0.0;
		d = 0.;
		for (i = 0; i < model->n_unique_pts; i++) {
			loglike += freq[i] * space[i];
			d += freq[i];
		}
		loglike += d * (scalepp + scalemm - scalepm - scalemp);
		loglike /= 4.0 * DELTA * DELTA;

		UpdateParam(model, tree, d, a);
		UpdateParam(model, tree, e, b);
		return loglike;
	}

	return 0.0;
}


int
HessianLike(TREE * tree, MODEL * model, double p[], double hess[])
{
	int             i, j, n;

	n = model->n_unique_pts;
	for (i = 0; i < n; i++) {
		for (j = 0; j < i; j++) {
			hess[i * n + j] = Partial2Deriv(tree, model, p, i, j);
			hess[j * n + i] = hess[i * n + j];
		}
		hess[i * n + i] = Partial2Deriv(tree, model, p, i, i);
	}

	return 0;
}



double
LikeFun_Single(TREE * tree, MODEL * model, double *p)
{
	double          scale;

	LikeVector(tree, model, p);
	scale = (tree->tree)->scalefactor;
	scale =
		Like(scale, p, model->pt_freq, model->n_unique_pts, model->pi,
		     model->n_pts, model->index);

	return scale;
}



double
CalcLike_Single(const double *param, void *data)
{
	struct single_fun *info;
	double          like;

	info = (struct single_fun *) data;
	UpdateAllParams(info->model, info->tree, param);
	like = -LikeFun_Single(info->tree, info->model, info->p);

	return like;
}


void
UpdateAllParams(MODEL * model, TREE * tree, const double *p)
{
	int             i = 0, a;
	NODE           *node;

	if (Branches_Variable==model->has_branches){
		for (; i < tree->n_br; i++) {
			node = tree->branches[i];
			node->blength[0] = p[i];
			a = find_connection(node->branch[0], node);
			(node->branch[0])->blength[a] = p[i];
		}
	}

	for (a = 0; a < model->nparam; a++){
		model->Update(model, p[a + i], a);
	}
}

void
UpdateParam(MODEL * model, TREE * tree, const double p, const int i)
{
	NODE           *node;
	int             a;

	if (Branches_Variable==model->has_branches && i < tree->n_br) {
		node = tree->branches[i];
		node->blength[0] = p;
		a = find_connection(node->branch[0], node);
		(node->branch[0])->blength[a] = p;
		return;
	}
	model->Update(model, p, (Branches_Variable==model->has_branches)?i-tree->n_br:i);

	return;
}


/*
 * Only dealing with single marix parameter (omega). More efficient to
 * calculate derivatives numerically than doing a full back substitution in
 * order to calculate them analytically
 */
void
GradLike_Single(double *param, double *grad, void *data)
{
	struct single_fun *info;
	double          like1, like2, like3, param0;

	info = (struct single_fun *) data;
	UpdateAllParams(info->model, info->tree, param);

	/* Calculation of derivative using forward differences only */
	like1 =
		Like(((info->tree)->tree)->scalefactor, info->p, (info->model)->pt_freq,
		     (info->model)->n_unique_pts, (info->model)->pi,
		     (info->model)->n_pts, (info->model)->index);
	param0 = param[0];
	param[0] += DELTA;
	UpdateAllParams(info->model, info->tree, param);
	like2 = LikeFun_Single(info->tree, info->model, info->p);
	grad[0] = -(like2 - like1) / DELTA;
	/*
	 * If derivative is small (less than ten times error), use central
	 * differences
	 */
	if (fabs(like2 - like1) < 10 * DELTA && param0 > DELTA) {
		param[0] = param0 - DELTA;
		UpdateAllParams(info->model, info->tree, param);
		like3 = LikeFun_Single(info->tree, info->model, info->p);
		grad[0] = -0.5 * (like2 - like3) / DELTA;
	}
	param[0] = param0;
	UpdateAllParams(info->model, info->tree, param);

}


double *
GradLike_Full(const double *param, double *grad, void *data)
{
	struct single_fun *info;
	int             i, n, npts;
	double         *ptgrad;

	info = (struct single_fun *) data;
	UpdateAllParams(info->model, info->tree, param);
	n = info->model->nparam;
	if (Branches_Variable==info->model->has_branches) {
		n += info->tree->n_br;
	}
	npts = info->model->n_unique_pts;

	ptgrad = calloc(npts * n, sizeof(double));
	GradLike2(info->tree, info->model, info->p, ptgrad);
	for (i = 0; i < n; i++) {
		grad[i] = 0.;
		for (int j = 0; j < npts; j++) {
			grad[i] += info->model->pt_freq[j] * ptgrad[i * npts + j];
		}
		grad[i] *= -1.;
	}
	free(ptgrad);
	return grad;
}

double *
InfoLike_Full(const double *param, double *info, void *data)
{
	fputs("# Warning: InfoLike_Full implements an approximation to the observed information!\n",stderr);
	fputs("# Warning: Calculation is based on \\sum (D log L)^2 rather than \\sum D^2 log L\n",stderr);
	fputs("# Warning: Formulas are equivalent asymptotically.\n",stderr);
	struct single_fun *state;
	int             n, npts;
	double         *ptgrad;

	state = (struct single_fun *) data;
	UpdateAllParams(state->model, state->tree, param);
	n = state->model->nparam;
	if (Branches_Variable==state->model->has_branches) {
		n += state->tree->n_br;
	}
	npts = state->model->n_unique_pts;

	ptgrad = calloc(npts * n, sizeof(double));
	GradLike2(state->tree, state->model, state->p, ptgrad);
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			info[i * n + j] = 0.;
			for (int k = 0; k < npts; k++) {
				info[i * n + j] += state->model->pt_freq[k] * ptgrad[i * npts + k] * ptgrad[j * npts + k];
			}
		}
	}
	free(ptgrad);
	return info;
}



void
GradLike2(TREE * tree, MODEL * model, double *p, double *grad)
{
	DoDerivatives(model, tree, grad, p);
}




void
Backwards(NODE * node, NODE * parent, TREE * tree, MODEL * model)
{
	int             i, j;
	double         *tmp_plik, max;
	NODE           *bnode;

	if (parent == NULL)
		goto descend;

	/* If parent is root, then don 't require back information. */
	if (tree->tree == parent) {
		for (i = 0; i < model->nbase * model->n_unique_pts; i++)
			node->back[i] = 1.;
		i = 0;
		node->bscalefactor = 0.;
		node->bscale = 0;
		while (i < parent->nbran && parent->branch[i] != NULL) {
			bnode = parent->branch[i];
			if (bnode != node) {
				tmp_plik = bnode->mid;
				for (j = 0; j < model->nbase * model->n_unique_pts; j++)
					node->back[j] *= tmp_plik[j];
				node->bscalefactor += bnode->scalefactor;
				node->bscale += bnode->scale;
			}
			i++;
		}
		/* If not at root node */
	} else if (NULL != parent) {
		Matrix_MatrixT_Mult(parent->back, model->n_unique_pts, model->nbase, parent->mat, model->nbase, model->nbase, node->back);

		node->bscalefactor = parent->bscalefactor;
		node->bscale = parent->bscale;
		i = 1;
		while (i < parent->nbran && parent->branch[i] != NULL) {
			bnode = parent->branch[i];
			if (bnode != node) {
				tmp_plik = bnode->mid;
				for (j = 0; j < model->nbase * model->n_unique_pts; j++)
					node->back[j] *= tmp_plik[j];
				node->bscalefactor += bnode->scalefactor;
				node->bscale += bnode->scale;
			}
			i++;
		}

	}
	node->bscale++;

	if (1 == SCALE && node->bscale > EVERY) {
		max = 0.0;
		for (i = 0; i < model->n_unique_pts * model->nbase; i++)
			if (node->back[i] > max)
				max = node->back[i];
		for (i = 0; i < model->n_unique_pts * model->nbase; i++)
			node->back[i] /= max;
		node->bscalefactor += log(max);
		node->bscale = 0;
	}
descend:
	/* Descend down tree */
	i = 0;
	while (i < node->nbran && node->branch[i] != NULL) {
		if (node->branch[i] != parent) {
			Backwards(node->branch[i], node, tree, model);
		}
		i++;
	}

	return;
}

void
DoDerivatives(MODEL * model, TREE * tree, double *grad, double *lvec)
{
	double          lscale;
	double         *grad_ptr;


	lscale = (tree->tree)->scalefactor;
	grad_ptr = grad;

	Backwards(tree->tree, NULL, tree, model);
	DoBranchDerivatives(model, tree, grad_ptr, lvec, lscale);
	if (Branches_Variable==model->has_branches) {
		grad_ptr += tree->n_br * model->n_unique_pts;
	}
	DoModelDerviatives(model, tree, grad_ptr, lvec, lscale);
}

void
DoBranchDerivatives(MODEL * model, const TREE * tree, double *grad,
		    double *lvec, double lscale)
{
	int             i, j, k, n, npts;
	NODE           *node;
	int             base;
	double          tmp, *pt_freq, fact;

	n = model->nbase;
	npts = model->n_unique_pts;
	pt_freq = model->pt_freq;
	fact = Rate(model) * Scale(model);

	for (i = 0; i < tree->n_br; i++) {
		node = tree->branches[i];
		node->bscalefactor =
			exp(node->scalefactor + node->bscalefactor - lscale);
		GetQP(model->q, node->mat, node->bmat, n);
		Matrix_MatrixT_Mult(node->back, model->n_unique_pts, model->nbase, node->bmat, model->nbase, model->nbase, model->tmp_plik);

		if (Branches_Variable==model->has_branches) {
			if (!ISLEAF(tree->branches[i])) {
				for (j = 0; j < model->n_unique_pts; j++) {
					tmp = 0.;
					for (k = 0; k < n; k++)
						tmp +=
							model->pi[k] * model->tmp_plik[j * n + k] * node->plik[j * n + k];
					tmp *= fact;
					tmp /= lvec[j];
					grad[i * npts + j] = tmp * node->bscalefactor;
				}

			} else {
				for (j = 0; j < model->n_unique_pts; j++) {
					base = (tree->branches[i])->seq[j];
					if (GapChar(model->seqtype) != base) {
						tmp = model->pi[base] * model->tmp_plik[j * n + base];
					} else {
						tmp = 0.;
						for (k = 0; k < n; k++)
							tmp += model->pi[k] * model->tmp_plik[j * n + k];
					}
					tmp *= fact;
					tmp /= lvec[j];
					grad[i * npts + j] = tmp * node->bscalefactor;
				}
			}
		}
	}
}

void
DoModelDerviatives(MODEL * model, TREE * tree, double *grad,
		   double *lvec, double lscale)
{
	double          factor, tmp, expscale;
	double         *gradpi, *dpidparam;
	double sum;

	factor = Scale(model) * Rate(model);
	const unsigned int n = model->nbase;
	const unsigned int npts = model->n_unique_pts;
	unsigned int nparam = model->nparam;
	if (model->optimize_pi) {
		nparam++;
		gradpi = calloc(nparam * npts, sizeof(double));
	} else {
		gradpi = grad;
	}
	const unsigned int pioffset = model->nparam - model->nbase + 1;
	expscale = exp(lscale);

	for (unsigned int i = 0; i < nparam; i++) {
		if ( Branches_Proportional==model->has_branches && 0==i){
			for ( unsigned int j=0 ; j<tree->n_br ; j++){
				NODE * node = tree->branches[j];
				MakeRateDerivFromP(model,node->blength[0],node->bmat);
			}
		} else {
			MakeSdQS(model, i);
			for (unsigned int j = 0; j < tree->n_br; j++){
				/* Note: code make assumption that parent node is always branch 0*/
				NODE * node = tree->branches[j];
				MakeDerivFromP(model, node->blength[0], node->bmat);
				/*Matrix_MatrixT_Mult(node->back, model->n_unique_pts, model->nbase, node->bmat, model->nbase, model->nbase, node->dback);*/
			}
		}
		for (unsigned int j = 0; j < npts; j++) {
			tmp = 0.;
			for (unsigned int k = 0; k < tree->n_br; k++) {
				NODE * node = tree->branches[k];
				sum = 0.;
				if (!ISLEAF(node)) {
					//warn("%s:%d\tThis function is not properly debugged\n",__FILE__,__LINE__);
					for ( unsigned int base=0 ; base<n ; base++){
						for (unsigned int l = 0; l < n; l++){
							tmp +=
								model->pi[l] * node->bmat[l*n+base] * node->back[j * n + l] * node->plik[j * n + base]
								* node->bscalefactor;
							/*sum += model->pi[l] * node->mat[l*n+base] * node->back[j * n + l] * node->plik[j * n + base]
								* node->bscalefactor;*/
						}
						/*if ( model->optimize_pi && i>=pioffset){ 
							l = i - pioffset; 
							tmp += node->mat[l*n+base] * node->back[j * n + l] * node->plik[j * n + base]
								* node->bscalefactor;
						}*/
					}
				} else {
					unsigned int base = node->seq[j];
					if (GapChar(model->seqtype) != base) {
						for ( unsigned int l=0 ; l<n ; l++){
							tmp += model->pi[l] * node->bmat[l*n+base] * node->back[j * n + l] * node->bscalefactor;
							/*sum += model->pi[l] * node->mat[l*n+base] * node->back[j * n + l] * node->bscalefactor;*/
						}
						/*if ( model->optimize_pi && i>=pioffset){ 
							l = i - pioffset; 
							tmp += node->mat[l*n+base] * node->back[j * n + l] * node->bscalefactor;
						}*/
					} else {
						//warn("%s:%d\tThis function is not properly debugged\n",__FILE__,__LINE__);
						/* Note: it might be possible to simply this using reversibility.
						 *  \sum_i \pi_i dP_{ia}/d\pi_j = \delta_{ja} - P_{ja}
						 * Needs checking! Derived from \sum_i \pi_i P_{ia} = \pi_a 
						 * -- for non-pi's, this sum is zero
						 */
						for (unsigned int base = 0; base < n; base++){
							for ( unsigned int l=0 ; l<n ; l++){
								tmp += model->pi[l] * node->bmat[l*n+base] * node->back[j * n + l] * node->bscalefactor;
								/*sum += model->pi[l] * node->mat[l*n+base] * node->back[j * n + l] * node->bscalefactor;*/
							}
							/*if ( model->optimize_pi && i>=pioffset){ 
								l = i - pioffset; 
								tmp += node->mat[l*n+base] * node->back[j * n + l] * node->bscalefactor;
							}*/
						}
					}
				}

			}
			
			if ( model->optimize_pi && i>=pioffset){ 
				unsigned int base = i - pioffset; 
				tmp += tree->tree->plik[j*n+base] * expscale;
			}
			tmp /= lvec[j];
			gradpi[i * npts + j] = tmp;
		}
	}

	if (model->optimize_pi) {
		int             pioffset = nparam - model->nbase;
		dpidparam = calloc((n - 1) * n, sizeof(double));
		dPidParam_pi(model->pi, dpidparam, n);
		for (unsigned int i = 0; i < pioffset; i++) {
			for (unsigned int j = 0; j < npts; j++) {
				grad[i * npts + j] = gradpi[i * npts + j];
			}
		}
		for (unsigned int p = 0; p < n - 1; p++) {
			unsigned int             paramn = p + pioffset;
			for (unsigned int j = 0; j < npts; j++) {
				grad[paramn * npts + j] = 0.;
				for (unsigned int pi = 0; pi < n; pi++) {
					grad[paramn * npts + j] += dpidparam[p * n + pi] * gradpi[(pi + pioffset) * npts + j];
				}
			}
		}
		free(dpidparam);
		free(gradpi);
	}
}




double
log2v(double a, double b)
{
	double          max, min;

	max = (a > b) ? a : b;
	min = (a <= b) ? a : b;

	return (log(max) + log1p(min / max));
}



static double
GetParam(MODEL * model, TREE * tree, int i)
{
	assert(NULL != model);
	assert(NULL != tree);
	assert(i > 0);
	int             offset = 0;

	if (Branches_Variable==model->has_branches) {
		if (i < tree->n_br)
			return (tree->branches[i])->blength[0];
		else
			offset = tree->n_br;
	}
	assert(i - offset > 0 && i - offset < model->nparam);
	return model->GetParam(model, i - offset);
}
