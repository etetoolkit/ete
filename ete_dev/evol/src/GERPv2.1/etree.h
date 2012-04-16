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

#ifndef ETREE_H
#define ETREE_H

#include <string>
using std::string;

#include "emodel.h"

#include "Mseq.h"
#include "MIter.h"
#include "Seq.h"
#include "Vec.h"

#include <map>

using namespace std;

class ETree;

class TNode {
 public:
  TNode() {
    distToPar = 0.0;
    root = false;
    leaf = false;
  }
  TNode(string toParse, TNode* par, Vec<TNode*> &foliage);
  TNode(const TNode& n, ETree& t);

  ~TNode();

  void computeUp(EModel &m, double k);
  void computeDown(EModel &m, double uu[], double k);

  double getNeutralRate();
  void scaleBy(double val, bool prop = true);

  TNode *nbr[3]; // nbr[0] is parent, except at root
  double U[3][4];
  double u[3][4];
  bool root, leaf;
  double distToPar;
  void Print();

  string sqname;
  int leafVal;
};

class ETree {
 public:
  ETree() { }
  ETree(string filename);
  ETree(const ETree& src);

  ~ETree();

  bool uproot();
  bool trim(TNode* lf);
  bool prep();

  void computeUp(EModel &m, double k = 1.0);
  void computeDown(EModel &m, double k = 1.0);
  double computeNorm(EModel &m);

  double getNeutralRate();
  void scaleBy(double val);
  void Print();

  TNode* rt;
  Vec<TNode*> foliage;
  double norm;
};

#endif
