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

#ifndef _CODONMODEL_H_
#define _CODONMODEL_H_

#ifndef _MODEL_H_
#include "model.h"
#endif

MODEL * NewCodonModel ( const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type, const enum model_branches branopt);
MODEL *NewCodonModel_singleDnDs (const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type);
MODEL * NewCodonModel_single ( const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type);
MODEL * NewCodonModel_full ( const int gencode, const double kappa, const double omega, const double *pi, const int codonf, const int freq_type, const enum model_branches branopt);
double GetScale_single ( MODEL * model, const double f);
void SetAminoAndCodonFuncs ( const int nucleo_type, const int amino_type, const char * nucleofile, const char * aminofile);
double *  GetEquilibriumDistCodon (const double * pi,const int codonf, const int gencode);

#endif
