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

#include "emodel.h"

#include <cmath>
#include <iostream>
#include <fstream>

EModel::EModel(Mseq s, double trtv) {
  unsigned int cA = 0, cC = 0, cG = 0, cT = 0;
  for (unsigned int i = 0; i < s.getSize(); i++)
    for (unsigned int j = 1; j <= s.getLength(); j++) {
      switch(s[i][j]) {
      case 'a':
      case 'A':
	cA++;
	break;
      case 'c':
      case 'C':
	cC++;
	break;
      case 'g':
      case 'G':
	cG++;
	break;
      case 't':
      case 'T':
	cT++;
	break;
      default:
	break;
      }
    }

  unsigned int cN = cA + cC + cG + cT;
  f[0] = cT / (double)cN;
  f[1] = cC / (double)cN;
  f[2] = cA / (double)cN;
  f[3] = cG / (double)cN;

  double tvc = 2 * (f[2] + f[3]) * (f[0] + f[1]);
  double trc = 2 * (f[2] * f[3] + f[0] * f[1]);
  double k = trtv * tvc / trc;

  beta = 1.0 / (trc * k + tvc);
  alpha = k * beta;

  y = f[1] + f[0];
  r = f[2] + f[3];
  eig2 = - beta;
  eig3 = - (y * beta + r * alpha);
  eig4 = - (y * alpha + r * beta);
}

// probability of transitioning from a to b over duration dist

void EModel::p(double v[][4], double dist) {
  double e2 = exp(eig2 * dist);
  double e3 = exp(eig3 * dist);
  double e4 = exp(eig4 * dist);

  v[0][0] = f[0] + e2 * r * f[0] / y + e4 * f[1] / y;
  v[1][0] = f[0] + e2 * r * f[0] / y - e4 * f[0] / y;
  v[2][0] = f[0] - e2 * f[0];
  v[3][0] = f[0] - e2 * f[0];
  v[0][1] = f[1] + e2 * r * f[1] / y - e4 * f[1] / y;
  v[1][1] = f[1] + e2 * r * f[1] / y + e4 * f[0] / y;
  v[2][1] = f[1] - e2 * f[1];
  v[3][1] = f[1] - e2 * f[1];
  v[0][2] = f[2] - e2 * f[2];
  v[1][2] = f[2] - e2 * f[2];
  v[2][2] = f[2] + e2 * f[2] * y / r + e3 * f[3] / r;
  v[3][2] = f[2] + e2 * f[2] * y / r - e3 * f[2] / r;
  v[0][3] = f[3] - e2 * f[3];
  v[1][3] = f[3] - e2 * f[3];
  v[2][3] = f[3] + e2 * f[3] * y / r - e3 * f[3] / r;
  v[3][3] = f[3] + e2 * f[3] * y / r + e3 * f[2] / r;
}
