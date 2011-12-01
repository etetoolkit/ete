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

#ifndef _MODEL_H_
#define _MODEL_H_


enum model_branches { Branches_Fixed, Branches_Variable, Branches_Proportional };
extern const char * model_branches_string[];

typedef struct md {
        double * q;
        double * p;
        double * ev, *v, * inv_ev;
        double * space;
        double scale;
        double rate;
        int nbase;
        int gencode;
        void (*Getq)( struct md *);
	void (*Gets)( double *,struct md *);
        double (*Scale)( struct md *);
        double (*Rate)( struct md *);
        void (*Update)(struct md *, double ,int);
        double (*GetParam)(struct md *, int);
        double * pi, *mgfreq;
        double * param;
        int nparam;
        int updated, factorized;
        double * tmp_plik;
        int seqtype,freq_type;
	const int * desc;

        int exact_obs;
        int n_unique_pts,n_pts;
        double * pt_freq;
        int * index;

        double *dp,*F,*dq;
        void (*GetdQ)(struct md *,int ,double *);

        int alternate_scaling,optimize_pi;
	enum model_branches has_branches;
} MODEL;


void DoDiagonalOfQ ( double * mat, const int n);
void MakeQ_From_S ( double * mat, const double * pi, const int n);
int MakeSym_From_Q ( double * mat, const double * spi, const int n);
void MakeFactQ_FromFactSym ( double * ev, double * inv_ev, double *v,const double * spi, const int n);
void FactorizeMatrix ( double *mat, const int n,double * ev, double * v, double * space);
double         *MakeP_From_FactQ(const double *v, const double *ev, const double *inv_ev, const double length, const double rate, const double scale, double *p, const int n, double *space, const double *pi, const double *q);
void MakeQ_From_S_stdfreq(double *mat, const double *pi, const int n);
void MakeQ_From_S_WGfreq(double *mat, const double *pi, const int n);
void MakeQ_From_S_Largetfreq(double *mat, const double *pi, const int n);
void MakeQ_From_S_MGfreq(double *mat, const double *pi, const int n, const int gencode);
void ParamToPi(const double *param, double *pi, const int npi);
void PiToParam ( const double * pi, double * param, const int npi);
void dPidParam_param ( const double * param, double * dpidparam, const int npi);
void dPidParam_pi ( const double * pi, double * dpidparam, const int npi);

void CheckModelDerivatives ( MODEL * model, const double blen, const double * param, const double delta );



MODEL * NewModel ( const int n, const int nparam);
double * GetQ ( MODEL * model);
double * GetP ( MODEL * model, const double length, double * mat);
void FreeModel ( MODEL * model);
void MakeDerivFromP ( MODEL * model, const double blen, double * bmat);
void MakeRateDerivFromP ( MODEL * model, const double blen, double * dp);
void MakeSdQS ( MODEL * model, const int param);
void GetQP ( const double * Q, const double * P, double * QP, const int n);




#define Scale(A)	A->Scale(A)
#define Rate(A)		A->Rate(A)

#endif
