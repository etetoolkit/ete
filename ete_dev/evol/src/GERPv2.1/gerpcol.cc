/*
 * Copyright 2007 Eugene Davydov
 *
 *
 * This file is part of the GERPv2.1 package.
 *
 * GERPv2.1 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * GERPv2.1 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */


#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <cmath>

#include "etree.h"
#include "emodel.h"
#include "Mseq.h"
#include "MIter.h"
#include "Seq.h"
#include "Vec.h"

#define SIGN(a,b) ((b) >= 0.0 ? fabs(a) : -fabs(a))

double f(ETree &t, EModel &m, double x) {
  t.computeUp(m,x);
  return -t.computeNorm(m);
}


/* This routine, getBestK, is based on the routine(s) brent from the book
 * Numerical Recipes in C (Cambridge University Press), Copyright (C)
 * 1987-1992 by Numerical Recipes Software.  Used by permission.  Use of
 * this routine other than as an integral part of GERPv2.1 requires an
 * additional license from Numerical Recipes Software.  Further distribution
 * in any form is prohibited.
 */
double getBestK(ETree &t, EModel &m, double ax, double bx, double cx) {
  const int ITMAX  = 100;
  const double CGOLD = 0.3819660f;
  const double ZEPS = 1.0e-10f;

  int iter;

  double tol = 0.001;
  double a,b,d=0.0,etemp,fu,fv,fw,fx,p,q,r,tol1,tol2,u,v,w,x,xm;
  double e=0.0;
  
  a = ax;
  b = cx;
  x=w=v=bx;
  fw=fv=fx=f(t,m,x);

  double fa = f(t,m,a);
  double fb = f(t,m,b);
  if (fa < fx) return a;
  if (fb < fx) return b;

  for (iter=1;iter<=ITMAX;iter++) {
    xm=0.5*(a+b);
    tol2=2.0*(tol1=tol*fabs(x)+ZEPS);
    if (fabs(x-xm) <= (tol2-0.5*(b-a))) {
      return x;
    }
    if (fabs(e) > tol1) {
      r=(x-w)*(fx-fv);
      q=(x-v)*(fx-fw);
      p=(x-v)*q-(x-w)*r;
      q=2.0*(q-r);
      if (q > 0.0) p = -p;
      q=fabs(q);
      etemp=e;
      e=d;
      if (fabs(p) >= fabs(0.5*q*etemp) || p <= q*(a-x) || p >=
	  q*(b-x))
	d=CGOLD*(e=(x >= xm ? a-x : b-x));
      else {
	d=p/q;
	u=x+d;
	if (u-a < tol2 || b-u < tol2)
	  d=SIGN(tol1,xm-x);
      }
    } else {
      d=CGOLD*(e=(x >= xm ? a-x : b-x));
    }
    u=(fabs(d) >= tol1 ? x+d : x+SIGN(tol1,d));
    fu=f(t,m,u);
    if (fu <= fx) {
      if (u >= x) a=x; else b=x;
      v=w;w=x;x=u;
      fv=fw;fw=fx; fx=fu;
    } else {
      if (u < x) a=u; else b=u;
      if (fu <= fw || w == x) {
	v=w;
	w=u;
	fv=fw;
	fw=fu;
      } else if (fu <= fv || v == x || v == w) {
	v=u;
	fv=fu;
      }
    }
  }
  return -1;
}


int main (int argc, char *argv[]) {
  string tree_fname = "";
  string prog_name = "GERPv2.1-gerpcol";
  Vec<string> maligns;
  double total_rate = -1, sb = -1;
  string suffix = ".rates";
  double trtv = 2.0;
  bool v = false, help = false;

  for ( ; argc > 0; argc--, argv++) {
    if (argv[0][0] != '-') continue;

    switch (argv[0][1]) {
    case 'h':
      cout << prog_name << " options:" << endl << endl;
      cout << " -h \t print help menu" << endl;
      cout << " -v \t verbose mode" << endl;
      cout << " -t <filename>" << endl;
      cout << "    \t evolutionary tree filename" << endl;
      cout << " -f <filename>" << endl;
      cout << "    \t alignment filename" << endl;
      cout << " -F <filename>" << endl;
      cout << "    \t alignment file list" << endl;
      cout << " -r <rate>" << endl;
      cout << "    \t Tr/Tv ratio [default = 2.0]" << endl;
      cout << " -n <rate>" << endl;
      cout << "    \t tree neutral rate [default = computed from file]" << endl;
      cout << " -s <factor>" << endl;
      cout << "    \t tree scaling factor [default = none]" << endl;
      cout << " -x <suffix>" << endl;
      cout << "    \t suffix for naming output files [default = \".rates\"]" << endl << endl;
      cout << "Please see README.txt for more information." << endl << endl;
      help = true;
      break;
    case 'v':
      v = true;
      break;
    case 'r':
      trtv = strtod(argv[1], NULL);
      break;
    case 's':
      sb = strtod(argv[1], NULL);
      break;
    case 't':
      tree_fname = argv[1];
      break;
    case 'f':
      maligns.push_back(argv[1]);
      break;
    case 'F':
      {
	ifstream ifs(argv[1]);
	string temp;
	while (true) {
	  ifs >> temp;
	  if (!ifs.good()) break;
	  maligns.push_back(temp);
	}
	ifs.close();
      }
      break;
    case 'n':
      total_rate = strtod(argv[1], NULL);
      break;
    case 'x':
      suffix = argv[1];
      break;
    default:
      cerr << "Ignoring unrecognized option " << argv[0] << endl;
      cerr << "Use the -h option to see the help menu." << endl;
      break;
    }
  }

  if (maligns.size() < 1 || tree_fname.length() < 1) {
    if (help) exit(0);
    cerr << "ERROR:  one or more required arguments missing." << endl;
    cerr << "Use 'gerpcol -h' to see the help menu." << endl;
    exit(1);
  }

  if (v) {
    cout << prog_name << endl;
    system("date");
  }

  ETree ttmp(tree_fname);
  ETree src(ttmp);
  if (v) cout << "Neutral rate computed from tree file = " << src.getNeutralRate() << endl;
  if (sb > 0) src.scaleBy(sb);
  if (total_rate > 0) src.scaleBy(total_rate / src.getNeutralRate());
  if (v) cout << "Neutral rate after rescaling = " << src.getNeutralRate() << endl << endl;

  if (v) cout << "Processing " << maligns.size() << " alignment file(s)." << endl << endl;

  for (unsigned int a = 0; a < maligns.size(); a++) {
    if (v) cout << "Processing " << maligns[a] << ", output will be written to " << maligns[a] + suffix << endl;
    Mseq s(maligns[a]);
    EModel m(s, trtv);
    if (v) cout << "Nucleotide frequencies:  A = " << m.f[2] << ", C = " << m.f[1] << ", G = " << m.f[3] << ", T = " << m.f[0] << endl;

    ofstream fout;
    fout.open((maligns[a] + suffix).c_str(), ios::out);
    fout.precision(3);
    fout.unsetf(ios::scientific);

    map<string, Seq*> h;
    
    for (unsigned int i = 0; i < s.getSize(); i++) {
      h[s[i].getTitle()] = &(s[i]);

      if (v) {
	bool found = false;
	for (unsigned int j = 0; j < src.foliage.size(); j++) {
	  if (s[i].getTitle() == src.foliage[j]->sqname) {
	    found = true;
	    break;
	  }
	}
	if (!found) cout << "Alignment species " << s[i].getTitle() << " not found in tree and therefore ignored." << endl;
      }
    }

    if (v) {
      for (unsigned int j = 0; j < src.foliage.size(); j++) 
	if (!h[src.foliage[j]->sqname])
	  cout << "Tree species " << src.foliage[j]->sqname << " not present in this alignment and therefore ignored." << endl;
    }

    unsigned int L = s.getLength();
    if (v) {
      cout << "Processing alignment of " << L << " positions, ";
      cout << "maximum neutral rate is " << src.getNeutralRate() << endl;
    }

    for (unsigned int i = 0; i < L; i++) {
      ETree tr(src);
      for (unsigned int j = 0; j < tr.foliage.size(); j++) {
	Seq* s = h[tr.foliage[j]->sqname];
	if (s) {
	  switch(s->getLetter(i+1)) {
	  case 't': case 'T': tr.foliage[j]->leafVal = 0; break;
	  case 'c': case 'C': tr.foliage[j]->leafVal = 1; break;
	  case 'a': case 'A': tr.foliage[j]->leafVal = 2; break;
	  case 'g': case 'G': tr.foliage[j]->leafVal = 3; break;
	  default: break;
	  }
	}
      }
	  
      double rexp = 0, robs = 0;
      if (tr.prep()) {
	double r = tr.getNeutralRate();
	tr.scaleBy(1.0 / r);
	
	double x = getBestK(tr, m, 0.0, 3.0 * r, 3.1 * r);
	if (x > 3.0 * r) x = 3.0 * r;
	robs = x;
	rexp = r;
      }

      fout << rexp << '\t' << (rexp - robs) << endl;
    }

    fout.close();

    if (v) cout << "Finished processing " << maligns[a] << endl << endl;
  }

  return 0;
}
