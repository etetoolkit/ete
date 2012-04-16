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

#ifndef EMODEL_H
#define EMODEL_H

#include <string>
#include "Mseq.h"

using namespace std;

class EModel {
 public:
  EModel() { }
  EModel(Mseq s, double trtv);

  void p(double v[][4], double dist);

  double alpha, beta, y, r;
  double f[4]; // T C A G
  double eig2, eig3, eig4;
};


#endif
