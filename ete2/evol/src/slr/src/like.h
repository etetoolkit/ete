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

#ifndef _LIKE_H_
#define _LIKE_H_

#ifndef _TREE_H_
#include "tree.h"
#endif

#ifndef _MODEL_H_
#include "model.h"
#endif

#define DELTA   1e-6



int CalcLike_Sub ( NODE * node, NODE * parent, TREE * tree, MODEL * model);
int LikeVector ( TREE * tree, MODEL * model, double p[]);
int LikeVectorSub ( TREE * tree, MODEL * model, double p[]);
double LikeDiff ( double scale1, double scale2, double * like1, double * like2, double * freq, int size);
double Like ( double scale, double like[], double freq[], int usize, double * pi , int nsize, int * index);


double CalcLike ( double pt[]);
void DCalcLike ( double pt[], double grad[]);
#endif

