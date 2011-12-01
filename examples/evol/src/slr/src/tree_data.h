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

#ifndef _TREE_DATA_H_
#define _TREE_DATA_H_

#ifndef _TREE_H_
#include "tree.h"
#endif
#ifndef _DATA_H_
#include "data.h"
#endif
#ifndef _MODEL_H_
#include "model.h"
#endif

struct single_fun {
        TREE * tree;
        MODEL * model;
        double * p;
};


int add_data_to_tree ( const DATA_SET * data, TREE * tree, MODEL * model);
void add_single_site_to_tree ( TREE * tree, const DATA_SET * data, const MODEL * model, const int a);
NODE * find_leaf ( const int i, const TREE * tree, const DATA_SET * data);
#endif

