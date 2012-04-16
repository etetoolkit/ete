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

#include "etree.h"

#include <cassert>
#include <iostream>
#include <fstream>
#include <string>

ETree::ETree(string filename) {
  ifstream ifs(filename.c_str());
  string toParse; // "x1:L1,x2:L2,x3:L3"

  getline(ifs, toParse, ';');
  rt = new TNode();
  rt->root = true;

  unsigned int i = 0;
  int nest = 0;
  unsigned int c1 = 0, c2 = 0;
  for ( ; i < toParse.length(); i++) {
    if (toParse[i] == '(') nest++;
    if (toParse[i] == ')') nest--;
    if (toParse[i] == ',' && nest == 1) {
      c1 = i; break;
    }
  }

  ++i;
  for ( ; i < toParse.length(); i++) {
    if (toParse[i] == '(') nest++;
    if (toParse[i] == ')') nest--;
    if (toParse[i] == ',' && nest == 1) {
      c2 = i; break;
    }
  }

  rt->root = true;
  if (c2 > 0) {
    // unrooted tree, trifurcation
    rt->nbr[0] = new TNode(toParse.substr(1,c1-1), rt, foliage);
    rt->nbr[1] = new TNode(toParse.substr(c1+1,c2-c1-1), rt, foliage);
    rt->nbr[2] = new TNode(toParse.substr(c2+1,toParse.length()-c2-2), rt, foliage);
  } else {
    // rooted tree, bifurcation
    rt->nbr[0] = new TNode(toParse.substr(1,c1-1), rt, foliage);
    rt->nbr[1] = new TNode(toParse.substr(c1+1,toParse.length()-c1-2), rt, foliage);
    rt->nbr[2] = new TNode();

    rt->nbr[2]->leaf = true;
    rt->nbr[2]->nbr[0] = rt;
    rt->nbr[2]->nbr[1] = rt->nbr[2]->nbr[2] = NULL;
    trim(rt->nbr[2]);
  }

  ifs.close();
}

ETree::ETree(const ETree& src) {
  rt = new TNode(*(src.rt), *this);
}

ETree::~ETree() {
  delete rt;
}

TNode::~TNode() {
  if (!leaf) {
    delete nbr[1];
    delete nbr[2];
    if (root) delete nbr[0];
  }
}

void ETree::Print() {
  rt->Print();
  for (unsigned int i = 0; i < foliage.size(); i++)
    cout << foliage[i]->sqname << " ";
  cout << endl;
}

void TNode::Print() {
  if (root) cout << "R";
  if (leaf) cout << "L";
  cout << "-" << sqname << "-" << distToPar << endl;
  if (leaf) return;
  if (root) nbr[0]->Print();
  nbr[1]->Print();
  nbr[2]->Print();
}

TNode::TNode(const TNode& n, ETree& t) {
  root = n.root;
  leaf = n.leaf;
  distToPar = n.distToPar;
  sqname = n.sqname;
  leafVal = n.leafVal;

  if (leaf) {
    nbr[1] = nbr[2] = NULL;
    t.foliage.push_back(this);
    return;
  }

  if (root) {
    nbr[0] = new TNode(*(n.nbr[0]), t);
    nbr[0]->nbr[0] = this;
  }
  nbr[1] = new TNode(*(n.nbr[1]), t);
  nbr[2] = new TNode(*(n.nbr[2]), t);
  nbr[1]->nbr[0] = this;
  nbr[2]->nbr[0] = this;
}

bool ETree::trim(TNode* lf) {
  if (!lf->leaf) return false;
  TNode* par = lf->nbr[0];
  
  if (par->root && !uproot()) return false;

  TNode* other;
  if (par->nbr[1] == lf) other = par->nbr[2];
  else other = par->nbr[1];
  
  other->distToPar += par->distToPar;
  other->nbr[0] = par->nbr[0];
  for (int i = 0; i < 3; i++)
    if (par->nbr[0]->nbr[i] == par)
      par->nbr[0]->nbr[i] = other;
  
  par->leaf = true; // hack to avoid destroying entire subtree
  delete par;
  delete lf;
  return true;
}

bool ETree::uproot() {
  if (rt->nbr[0]->leaf && !rt->nbr[1]->leaf) {
    TNode* tmp = rt->nbr[0];
    rt->nbr[0] = rt->nbr[1];
    rt->nbr[1] = tmp;
  }
  if (rt->nbr[0]->leaf && !rt->nbr[2]->leaf) {
    TNode* tmp = rt->nbr[0];
    rt->nbr[0] = rt->nbr[2];
    rt->nbr[2] = tmp;
  }
  
  if (rt->nbr[0]->leaf) return false;

  rt->nbr[0]->root = true;
  rt->root = false;
  rt->distToPar = rt->nbr[0]->distToPar;
  rt->nbr[0]->distToPar = 0.0;
  rt = rt->nbr[0];
  return true;
}

bool ETree::prep() {
  int L = foliage.size();

  for (int i = 0; i < L;  ) {
    switch(foliage[i]->leafVal) {
    case 0:
    case 1:
    case 2:
    case 3:
      i++; break;
    default:
      if (!trim(foliage[i])) return false;
      foliage[i] = foliage[--L];
      break;
    }
  }

  foliage.resize(L);
  
  return true;
}

// x:L

TNode::TNode(string toParse, TNode* par, Vec<TNode*> &foliage) {
  int c = toParse.rfind(':');

  nbr[0] = par;
  distToPar = atof(toParse.substr(c+1,toParse.length()-c-1).c_str());
  root = false;
  leaf = false;
  
  if (toParse[0] == '(') {
    int i = 0;
    int nest = 0;
    for ( ; i < c; i++) {
      if (toParse[i] == '(') nest++;
      if (toParse[i] == ')') nest--;
      if (toParse[i] == ',' && nest == 1) break;
    }

    nbr[1] = new TNode(toParse.substr(1,i-1), this, foliage);
    nbr[2] = new TNode(toParse.substr(i+1,c-i-2), this, foliage);
  } else {
    sqname = toParse.substr(0,c);
    nbr[1] = nbr[2] = NULL;
    leaf = true;
    leafVal = 4;
    foliage.push_back(this);
  }
}

void ETree::computeUp(EModel &m, double k) {
  rt->nbr[0]->computeUp(m, k);
  rt->nbr[1]->computeUp(m, k);
  rt->nbr[2]->computeUp(m, k);
}

void TNode::computeUp(EModel &m, double k) {
  if (leaf) {
    // U
    for (int i = 0; i < 4; i++) U[0][i] = 0;
    U[0][leafVal] = 1;

  } else {
    nbr[1]->computeUp(m, k);
    nbr[2]->computeUp(m, k);
  
    // U
    for (int i = 0; i < 4; i++)
      U[0][i] = nbr[1]->u[0][i] * nbr[2]->u[0][i]; 
  }

  // u
  double v[4][4];
  m.p(v, distToPar * k);

  for (int i = 0; i < 4; i++) {
    u[0][i] = 0;
    for (int j = 0; j < 4; j++) {
      u[0][i] += U[0][j] * v[i][j];
    }
  }

}

void ETree::computeDown(EModel &m, double k) {
  // U
  for (int i = 0; i < 4; i++) {
    rt->U[0][i] =  rt->nbr[1]->u[0][i] * rt->nbr[2]->u[0][i];
    rt->U[1][i] =  rt->nbr[0]->u[0][i] * rt->nbr[2]->u[0][i];
    rt->U[2][i] =  rt->nbr[1]->u[0][i] * rt->nbr[0]->u[0][i];
  }

  // u
  double v0[4][4], v1[4][4], v2[4][4];
  m.p(v0, rt->nbr[0]->distToPar * k);
  m.p(v1, rt->nbr[1]->distToPar * k);
  m.p(v2, rt->nbr[2]->distToPar * k);

  for (int i = 0; i < 4; i++) {
    rt->u[0][i] = 0;
    rt->u[1][i] = 0;
    rt->u[2][i] = 0;
    for (int j = 0; j < 4; j++) {
      rt->u[0][i] += rt->U[0][j] * v0[i][j];
      rt->u[1][i] += rt->U[1][j] * v1[i][j];
      rt->u[2][i] += rt->U[2][j] * v2[i][j];
    }
  }

  // recurse
  rt->nbr[0]->computeDown(m, rt->u[0], k);
  rt->nbr[1]->computeDown(m, rt->u[1], k);
  rt->nbr[2]->computeDown(m, rt->u[2], k);

}

void TNode::computeDown(EModel &m, double uu[], double k) {
  if (leaf) return;

  // U
  for (int i = 0; i < 4; i++) {
    U[1][i] =  nbr[2]->u[0][i] * uu[i];
    U[2][i] =  nbr[1]->u[0][i] * uu[i];
  }

  // u
  double v1[4][4], v2[4][4];
  m.p(v1, nbr[1]->distToPar * k);
  m.p(v2, nbr[2]->distToPar * k);

  for (int i = 0; i < 4; i++) {
    u[1][i] = 0;
    u[2][i] = 0;
    for (int j = 0; j < 4; j++) {
      u[1][i] += U[1][j] * v1[i][j];
      u[2][i] += U[2][j] * v2[i][j];
    }
  }

  // recurse

  nbr[1]->computeDown(m, u[1], k);
  nbr[2]->computeDown(m, u[2], k);
}

double ETree::computeNorm(EModel &m) {
  norm = 0.0;
  for (int i = 0; i < 4; i++)
    norm += m.f[i] * rt->nbr[0]->u[0][i] * rt->nbr[1]->u[0][i] * rt->nbr[2]->u[0][i];

  return norm;
}

double ETree::getNeutralRate() {
  return rt->getNeutralRate();
}

void ETree::scaleBy(double val) {
  rt->scaleBy(val);
  rt->scaleBy(0.0, false);
}

double TNode::getNeutralRate() {
  double r = distToPar;
  if (leaf) return r;

  r += nbr[1]->getNeutralRate();
  r += nbr[2]->getNeutralRate();
  if (root) r += nbr[0]->getNeutralRate();

  return r;
}

void TNode::scaleBy(double val, bool prop) {
  distToPar *= val;
  if (leaf || !prop) return;

  nbr[1]->scaleBy(val, prop);
  nbr[2]->scaleBy(val, prop);
  if (root) nbr[0]->scaleBy(val, prop);
}
