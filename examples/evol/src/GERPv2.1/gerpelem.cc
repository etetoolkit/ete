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
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <cmath>

#include "Mseq.h"
#include "MIter.h"
#include "Seq.h"
#include "Vec.h"

#define NSHUFFLES (10)

int MIN_LEN = 4, MAX_LEN = 2000;
int ITOL = 10;
double depth = 0.5, penalty = 0.5;
int allowed = 10, border = 2;
double cden = 10.0, cexp = 1.15;

string rates_fname = "";
string prog_name = "GERPv2.1-gerpelem";
string suffix = ".elems", wsuffix = ".exclude";
bool v = false, w = false, help = false;
double fpr = 0.01;
double xfrac = 0.5;

int MIN_SC = 0, MAX_SC = 0;

int seqlen;
double mNR;

typedef struct {
  unsigned int L;
  unsigned short len;
  int score;
  double p;
} elem;

typedef struct {
  double r;
  int s;
  bool shallow, exclude;
} pos;

struct less_dp : public binary_function<elem, elem, bool> {
  bool operator()(elem x, elem y) {
    if (x.len < y.len) return true;
    if (x.len > y.len) return false;
    return x.score < y.score;
  }
};

struct less_pval : public binary_function<elem, elem, bool> {
  bool operator()(elem x, elem y) {
    if (x.p < y.p) return true;
    if (x.p > y.p) return false;
    return (x.score > y.score);
  }
};

inline unsigned int to2d(unsigned int i, unsigned int j, unsigned int n) {
  return (j + i * n);
}

void ptogp(double* p, double *gp, int N) {
  gp[N-1] = p[N-1];
  for (int i = N-2; i >= 0; i--) {
    gp[i] = gp[i+1] + p[i];
  }
}

void getCElems(Vec<elem> &found, Vec<pos> &a)
{
  Vec<unsigned int> b;
  Vec<unsigned int> e;
 
  for (unsigned int i = 0; i < a.size(); i++) {
    if (a[i].s > 0) {
      unsigned int j = i;
      while (j < a.size() && a[j].s > 0) j++;
      b.push_back(i+1);
      e.push_back(j);
      i = j;
    }
  }

  int* ss = new int[a.size()+1];
  ss[0] = 0;
  for (unsigned int i = 1; i <= a.size(); i++) {
    ss[i] = ss[i-1] + a[i-1].s;
  }

  for (unsigned int i = 0; i < b.size(); i++) {
    unsigned int L = b[i];

    unsigned int j;
    for (j = i; j < e.size(); j++) {
      unsigned int R = e[j];
      unsigned short len = R - L + 1;
      if (len > MAX_LEN) break;
      if (len < MIN_LEN) continue;

      double escore = (ss[R] - ss[L-1]) / (double)ITOL;
      if (escore < 0) continue;
      if (escore < (mNR * pow(len, cexp) / cden)) continue;

      int shallow_count = 0;
      for (unsigned int k = L; k <= R; k++) {
	if (a[k-1].shallow) shallow_count++;
      }
      if (shallow_count > allowed) continue;

      elem etemp;
      etemp.L = L;
      etemp.len = len;
      etemp.score = ss[R] - ss[L-1];
      etemp.p = 1.0;
      found.push_back(etemp);
    }
  }

  delete [] ss;
  sort(found.begin(), found.end(), less_dp());
}

void shuffle(Vec<pos> &a)
{
  for (unsigned int i = 0; i < a.size(); i++) {
    if (a[i].shallow) continue;
    unsigned int j;
    do {
      j = rand() % a.size();
    } while (a[j].shallow);
    pos t;
    t = a[i]; a[i] = a[j]; a[j] = t;
  }
}

void filterOverlap(Vec<elem> &src, Vec<elem> &dst)
{
  Vec<unsigned int> ub;
  Vec<unsigned int> ue;

  ub.push_back(0);
  ue.push_back(0);
  ub.push_back(seqlen + 1);
  ue.push_back(seqlen + 1);

  for (unsigned int i = 0; i < src.size(); i++) {
    Vec<unsigned int>::iterator LB = lower_bound(ub.begin(), ub.end(), src[i].L);
    int idx = LB - ub.begin();
    
    if (src[i].L >= ub[idx] || src[i].L <= ue[idx-1]) continue;
    if (src[i].L + src[i].len - 1 >= ub[idx]) continue;

    ub.insert(ub.begin() + idx, src[i].L);
    ue.insert(ue.begin() + idx, src[i].L + src[i].len - 1);

    dst.push_back(src[i]);
  }
}

double computeMedianNR(Vec<pos> &a)
{
  Vec<double> rm;
  rm.reserve(a.size());
  for (unsigned int i = 0; i < a.size(); i++) {
    if (a[i].r > depth) rm.push_back(a[i].r);
  }

  sort(rm.begin(), rm.end());
  return rm[rm.size() / 2];
  //  Vec<double>::iterator rmlb = lower_bound(rm.begin(), rm.end(), depth);
  //int rmidx = rmlb - rm.begin();
  //return rm[(rmidx + rm.size() - 1) / 2];
}

void markShallow(Vec<pos> &a, int penalize) {
  for (int i = 0; i < seqlen; i++) {
    if (a[i].r < depth) {
      int j = i;
      while (j < seqlen && a[j].r < depth) {
	a[j].s = penalize;
        j++;
      }

      for (int k = i + border; k < j - border; k++) {
	a[k].shallow = true;
      }
      i = j;
    }
  }
}

void markExclude(Vec<pos> &a, Vec<elem> &e, unsigned int stop)
{
  for (unsigned int i = 0; i < stop; i++) {
    for (unsigned short j = 0; j < e[i].len; j++) {
      a[e[i].L + j - 1].exclude = true;
    }
  }
}

void computeP(Vec<pos> &a, Vec<elem> &found, Vec<elem> sfound[],
	      int numTotal)

{
  int SC_RANGE = MAX_SC - MIN_SC + 1;
  int Z = -MIN_SC;
  int ZL = Z * MAX_LEN;

  double* fr = new double[SC_RANGE];
  double punit = 1.0 / (double)(seqlen + SC_RANGE - numTotal);

  for (int i = MIN_SC; i <= MAX_SC; i++)
    fr[Z + i] = punit;

  for (int i = 0; i < seqlen; i++) {
    if (!a[i].shallow && !a[i].exclude) fr[Z + a[i].s] += punit;
  }

  int n = MAX_LEN * SC_RANGE;
  double *p = new double[2 * n];
  double *gp = new double[2 * n];
  memset(p, 0, 2 * n * sizeof(double));
  memset(gp, 0, 2 * n * sizeof(double));

  p[to2d(0, ZL, n)] = 1.0;
  ptogp(p, gp, n);

  unsigned int celem = 0;
  unsigned int scelem[NSHUFFLES];
  for (int i = 0; i < NSHUFFLES; i++) scelem[i] = 0;

  for (int i = 1; i <= MAX_LEN; i++) {
    memset(p + (i%2) * n, 0, n * sizeof(double));
    for (int j = 0; j < n; j++) {
      int klim = ((Z-j+n < SC_RANGE) ? (Z - j + n) : SC_RANGE);
      for (int k = ((Z > j) ? (Z-j) : 0); k < klim; k++) {
	int nj = j + (k - Z);
	p[to2d(i % 2, nj, n)] += p[to2d((i-1)%2,j,n)] * fr[k];
      }
    }

    ptogp(p + (i%2) * n, gp + (i%2) * n, n);

    while (celem < found.size() && found[celem].len == i) {
      found[celem].p = gp[to2d(i%2, found[celem].score + ZL, n)];
      celem++;
    }
    for (int si = 0; si < NSHUFFLES; si++) {
      while (scelem[si] < sfound[si].size() &&
	     sfound[si][scelem[si]].len == i) {
	sfound[si][scelem[si]].p = gp[to2d(i%2, sfound[si][scelem[si]].score + ZL, n)];
	scelem[si]++;
      }
    } 
  }

  delete [] p;
  delete [] gp;
  delete [] fr;
}

void readRates(Vec<pos> &a)
{
  ifstream ifs(rates_fname.c_str());
  
  while (true) {
    pos ptemp;
    double rs;
    ifs >> ptemp.r >> rs;
    if (ifs.eof()) break;

    int it;
    if (rs >= 0) it = (int)(rs * ITOL + 0.5);
    else it = -(int)(-rs * ITOL - 0.5);
    
    ptemp.s = it;
    ptemp.shallow = false;
    ptemp.exclude = false;
    a.push_back(ptemp);

    if (it > MAX_SC) MAX_SC = it;
    if (it < MIN_SC) MIN_SC = it;
  }

  seqlen = a.size();
  if (v) cout << "processing file " << rates_fname << " containing " << seqlen << " position scores" << endl;

  ifs.close();
}

void readParameters(int argc, char *argv[]) {
  for ( ; argc > 0; argc--, argv++) {
    if (argv[0][0] != '-') continue;

    switch (argv[0][1]) {
    case 'h':
      cout << prog_name << " options:" << endl << endl;
      cout << " -h \t print help menu" << endl;
      cout << " -v \t verbose mode" << endl;
      cout << " -f <filename>" << endl;
      cout << "    \t column scores filename" << endl;
      cout << " -x <suffix>" << endl;
      cout << "    \t suffix for naming output files [default = \".elems\"]" << endl;
      cout << " -w <suffix>" << endl;
      cout << "    \t suffix for naming exclusion region file [default = no output]" << endl;
      cout << " -l <length>" << endl;
      cout << "    \t minimum element length [default = 3]" << endl;
      cout << " -L <length>" << endl;
      cout << "    \t maximum element length [default = 2000]" << endl;
      cout << " -t <inverse tolerance>" << endl;
      cout << "    \t inverse of the rounding tolerance [default = 10]" << endl;
      cout << " -d <threshold>" << endl;
      cout << "    \t depth threshold for shallow columns, in substitutions per site [default = 0.5]" << endl;
      cout << " -p <penalty>" << endl;
      cout << "    \t penalty coefficient for shallow columns, as fraction of the median neutral rate [default = 0.5]" << endl;
      cout << " -b <number>" << endl;
      cout << "    \t number of border nucleotides for shallow regions [default = 2]" << endl;
      cout << " -a <number>" << endl;
      cout << "    \t total number of allowed non-border shallow nucleotides per element [default = 10]" << endl;
      cout << " -e <ratio>" << endl;
      cout << "    \t acceptable false positive [default = 0.01]" << endl;
      cout << " -u <ratio>" << endl;
      cout << "    \t fraction of first-pass constrained elements to exclude in the second pass [default = 0.5]" << endl;
      cout << " -q <value>" << endl;
      cout << "    \t denominator for minimum candidate element score formula [default = 10.0]" << endl;
      cout << " -r <value>" << endl;
      cout << "    \t exponent for minimum candidate element score formula [default = 1.15]" << endl;
      cout << endl << "Please see README.txt for more information" << endl << endl;
      help = true;
      break;
    case 'v':
      v = true;
      break;
    case 'l':
      MIN_LEN = (int)strtod(argv[1], NULL);
      break;
    case 'L':
      MAX_LEN = (int)strtod(argv[1], NULL);
      break;
    case 'p':
      penalty = strtod(argv[1], NULL);
      break;
    case 't':
      ITOL = (int)strtod(argv[1], NULL);
      break;
    case 'a':
      allowed = (int)strtod(argv[1], NULL);
      break;
    case 'd':
      depth = strtod(argv[1], NULL);
      break;
    case 'b':
      border = (int)strtod(argv[1], NULL);
      break;
    case 'x':
      suffix = argv[1];
      break;
    case 'w':
      wsuffix = argv[1];
      break;
    case 'e':
      fpr = strtod(argv[1], NULL);
      break;
    case 'f':
      rates_fname = argv[1];
      break;
    case 'u':
      xfrac = strtod(argv[1], NULL);
      break;
    case 'q':
      cden = strtod(argv[1], NULL);
      break;
    case 'r':
      cexp = strtod(argv[1], NULL);
      break;
    default:
      cerr << "Ignoring unrecognized option " << argv[0] << endl;
      cerr << "Use the -h option to see the help menu." << endl;
      break;
    }
  }

  if (rates_fname.length() < 1) {
    if (help) exit(0);
    cerr << "ERROR:  one or more required arguments missing." << endl;
    cerr << "Use 'gerpelem -h' to see the help menu." << endl;
    exit(1);
  }
  
  if (v) {
    cout << prog_name << endl;
    system("date");
  }
}

unsigned int findCutoff(Vec<elem> &f, Vec<elem> sf[NSHUFFLES],
			double cstop)
{
  unsigned int si[NSHUFFLES] = {0};
  unsigned int sitot = 0, lensum = 0, slensum = 0;
  unsigned int i;
  
  for (i = 0; i < f.size(); i++) {
    lensum += f[i].len;

    for (int j = 0; j < NSHUFFLES; j++) {
      while (si[j] < sf[j].size() && sf[j][si[j]].p < f[i].p) {
	si[j]++;
	sitot++;
	slensum += sf[j][si[j]].len;
      }
    }

    if (sitot > cstop * NSHUFFLES * (i+1)) break;
    //if (slensum > lstop * NSHUFFLES * lensum) break;
  }

  if (v) {
    cout << "false positive cutoff exceeded after " << (i+1) << " elements totaling " << lensum << " bases in length" << endl;
    cout << (double)(sitot / (double)NSHUFFLES) << " shuffled elements found totaling " << (double)(slensum / (double)NSHUFFLES) << " bases in length" << endl;
  }
  return i;
}

int main (int argc, char *argv[]) {
  srand(time(NULL));
  readParameters(argc, argv);

  Vec<pos> a;
  readRates(a);
  mNR = computeMedianNR(a);
  if (v) cout << "median neutral rate is " << mNR << endl;

  int penalize = -(int)(mNR * penalty * ITOL + 0.5);
  if (penalize < MIN_SC) {
    if (v) cout << "default penalty too severe; setting penalty to match the lowest RS score observed in alignment" << endl;
    penalize = MIN_SC;
  }

  markShallow(a, penalize);
  unsigned int numShallow = 0;
  unsigned int numExclude = 0;
  unsigned int numTotal = 0;

  for (unsigned int i = 0; i < a.size(); i++) {
    if (a[i].shallow) numShallow++;
    //    if (a[i].exclude) numExclude++;
    //if (a[i].shallow || a[i].exclude) numTotal++;
  }

  if (v) cout << numShallow << " non-border shallow positions excluded" << endl;

  // first pass

  Vec<elem> found;
  Vec<elem> sfound[NSHUFFLES];

  getCElems(found, a);
  if (v) cout << found.size() << " candidate elements found" << endl << endl;

  if (v) cout << "finding highly constrained regions to exclude" << endl;
  if (w) cout << "exclusion regions will be output to " << rates_fname << wsuffix << endl;

  for (int i = 0; i < NSHUFFLES; i++) {
    shuffle(a);
    getCElems(sfound[i], a);
  }

  computeP(a, found, sfound, numShallow);

  Vec<elem> ffound;
  Vec<elem> fsfound[NSHUFFLES];

  sort(found.begin(), found.end(), less_pval());
  filterOverlap(found, ffound);

  for (int i = 0; i < NSHUFFLES; i++) {
    sort(sfound[i].begin(), sfound[i].end(), less_pval());
    filterOverlap(sfound[i], fsfound[i]);
  }

  unsigned int stop = findCutoff(ffound, fsfound, fpr);
  stop = (unsigned int)((double)stop * xfrac);
  if (v) cout << "excluded " << stop << " most constrained elements" << endl << endl;

  if (w) {
    ofstream efs;
    efs.open((rates_fname + wsuffix).c_str(), ios::out);
    for (unsigned int i = 0; i < stop; i++) {
      efs << ffound[i].L << ' ' << (ffound[i].L + ffound[i].len - 1) <<
	' ' << ffound[i].len << ' ' << ffound[i].score/(double)ITOL <<
	' ' << ffound[i].p << endl;
    }
    efs.close();
  }

  if (v) {
    cout << "finding final constrained elements" << endl;
    cout << "results will be output to " << rates_fname << suffix << endl;
  }
  // second pass
  markExclude(a, ffound, stop);

  //  found.clear();
  ffound.clear();
  for (int i = 0; i < NSHUFFLES; i++) {
    sfound[i].clear();
    fsfound[i].clear();
  }

  //getCElems(found, a);
  sort(found.begin(), found.end(), less_dp());

  Vec<pos> base;
  base.reserve(a.size());
  for (unsigned int i = 0; i < a.size(); i++) {
    if (!a[i].exclude) base.push_back(a[i]);
  }

  for (int i = 0; i < NSHUFFLES; i++) {
    shuffle(base);
    getCElems(sfound[i], base);
  }

  for (unsigned int i = 0; i < a.size(); i++) {
    //    if (a[i].shallow) numShallow++;
    if (a[i].exclude) numExclude++;
    if (a[i].shallow || a[i].exclude) numTotal++;
  }

  if (v) {
    cout << numExclude << " constrained positions excluded" << endl;
    cout << numTotal << " total positions excluded" << endl;
  }

  computeP(a, found, sfound, numTotal);

  sort(found.begin(), found.end(), less_pval());
  filterOverlap(found, ffound);

  for (int i = 0; i < NSHUFFLES; i++) {
    sort(sfound[i].begin(), sfound[i].end(), less_pval());
    filterOverlap(sfound[i], fsfound[i]);
  }

  stop = findCutoff(ffound, fsfound, fpr);
  ofstream ofs;
  ofs.open((rates_fname + suffix).c_str(), ios::out);

  unsigned int lensum = 0;
  for (unsigned int i = 0; i < stop; i++) 
  {
    ofs << ffound[i].L << ' ' << (ffound[i].L + ffound[i].len - 1) << ' ' <<
      ffound[i].len << ' ' <<
      ffound[i].score/(double)ITOL << ' ' << ffound[i].p << endl;
    lensum += ffound[i].len;
  }

  ofs.close();

  if (v) cout << "found " << stop << " elements totaling " << lensum << " bases in length" << endl << endl;

  return 0;
}
