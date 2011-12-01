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

#define _USE_MATH_DEFINES

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <limits.h>
#include <string.h>
#include <time.h>
#include <assert.h>
#include "rng.h"


#define SEEDFILE32 ".rng32"
#define SEEDFILE64 ".rng64"
#define SEED       0

#ifdef WINDOWS
	#define ULL_TYPE 		unsigned long int
	#define ULL_TYPE_MAX 	4294967295U
#else
	#define ULL_TYPE unsigned long long int
	#define ULL_TYPE_MAX	18446744073709551615ULL
#endif

#define RL_LINEAR32_A 42353223
#define RL_LINEAR64_A 6364136223846793005ULL

#define OOM(A)  if ( A == NULL){ \
                  printf ("Out of memory\n"); \
                  exit (EXIT_FAILURE); }

/* Magic numbers for "Additive" Fibonarci generator
 * (see Knuth).
 * Suggested values for (RL_LAGGED_L,RL_LAGGED_K)
 * include (24,55) , (30,127) , (83,258) and (107,378)
 * The larger the numbers, the better statistical properties
 * of the generator (in general).
 * We generate RL_LAGGED_G numbers at a time and use the
 * first RL_LAGGED_N of them.
 * RL_LAGGED_G >= RL_LAGGED_K
 * RL_LAGGED_G >= RL_LAGGED_N*/
#define RL_LAGGED_L 107
#define RL_LAGGED_K 378
#define RL_LAGGED_G 1009
#define RL_LAGGED_N 100



#define RL_DENSITY	0
#define RL_RANDOM	1

static double RL_standard_uniform (double x, int r);
static ULL_TYPE RL_lagged64 (void);
static void RL_lagged64_g (ULL_TYPE *n);
static ULL_TYPE RL_linear64 (void);
void RL_sort_d (int n, double *number);
static int ValidGenerator (int gen);
static int double_comparison (const void *dp1, const void *dp2);
static long long int ipow (int x, int y);
static void InitialiseLaggedFromClock (ULL_TYPE *d, const int n);
static void InitialiseLaggedFromSeed (const unsigned int seed, ULL_TYPE *d, const int n);


static ULL_TYPE (*RL_generator64) (void) = RL_lagged64;
static ULL_TYPE history64[RL_LAGGED_K];
static ULL_TYPE seed = SEED;


/*   Changed random number generator
 */
void SetRandomGenerator (int gen)
{
  assert (ValidGenerator (gen));

  switch (gen) {
  case RL_LAGGED:
    RL_generator64 = RL_lagged64;
    break;
  case RL_LINEAR:
    RL_generator64 = RL_linear64;
    break;
  default:
    abort ();
  }
}

/*   Check if generator is valid
 */
static int ValidGenerator (int gen)
{
  switch (gen) {
  case RL_LAGGED:
  case RL_LINEAR:
    return 1;
  }

  return 0;
}


/*   Interface for random uniform(0,1) observation
 */
double RandomStandardUniform (void)
{
  double x = 0.;

  x = RL_standard_uniform (x, RL_RANDOM);

  assert (x >= 0. && x <= 1.);
  return x;
}


/*   Interface for random exponential by inverse CDF method
 */
double RandomExp (double mean)
{
  double x=0.;

  assert (mean >= 0.);

  x = RL_standard_uniform (x, RL_RANDOM);
  x = -mean * log (x);

  assert (x >= 0.);
  return x;
}

/*   Generates random observation from Gamma distribution.
 */
double RandomGamma (double shape, double scale)
{
  double x, y, v;

  assert (shape >= 0.);
  assert (scale >= 0.);

  if (shape < 1.) {
    do {
      v = RandomStandardUniform ();
      x = RandomStandardUniform ();
      y = M_E / (shape * M_E);
      if (x < y) {
	x = pow (v, 1. / shape);
	if (M_E * v > y)
	  y = y * exp (-x);
      }
      else {
	x = 1. - log (v);
	y = y + (1. - y) * pow (x, shape - 1.);
      }
    }
    while (y < v);
    x *= scale;
  }
  else if (shape > 1.) {
    do {
      do {
	y = tan (M_PI * RandomStandardUniform ());
	x = sqrt (2. * shape - 1.) * y + shape - 1.;
      }
      while (x < 0);
      v = RandomStandardUniform ();
      y =
	(1. + y * y) * exp ((shape - 1.) * log (x / (shape - 1.)) -
			    sqrt (2. * shape - 1.) * y);
    }
    while (y < v);
    x *= scale;
  }
  else {
    x = RandomExp (scale);
  }

  assert (x >= 0.);
  return x;
}


/*   Generate observation from Dirichlet distribution.
 */
int RandomDirichlet (double *a, double *p, int n)
{
  int b;
  double t = 0.;

  assert (n > 1);
  assert (NULL != a);
  assert (NULL != p);

  for (b = 0; b < n; b++) {
    assert (a[b] >= 0.);
    if (a[b] > DBL_EPSILON)
      p[b] = RandomGamma (a[b], 1.);
    else
      p[b] = 0;
    t += p[b];
    assert (p[b] >= 0.);
  }
  for (b = 0; b < n; b++)
    p[b] /= t;

  return 0;
}


/*  Random Dirichlet vector using the rejection method of Stefanescu, 
 *  Kybernetika 25(6) 1989 p467-475.
 *  Only good for Dirichlet when all parameters (other than n) are << 1*/
int RandomDirichlet_rejection (double *a, double *p, int n)
{
  int b;
  int reject = -1;
  double t;

  for (b = 0; b < n; b++)
    assert (a[b] >= 0.);

  do {
    reject++;
    t = 0.;
    for (b = 0; b < n; b++) {
      p[b] = RandomStandardUniform ();
      p[b] = pow (p[b], 1. / a[b]);
      t += p[b];
    }
    t += RandomStandardUniform ();
  }
  while (t > 1.);

  for (b = 0; b < n; b++) {
    assert (p[b] >= 0.);
    p[b] /= t;
  }

  return 0;
}


/*   Function for dealing with standard uniform distribution
 */
static double RL_standard_uniform (double x, int r)
{
  double y = 0;

  switch (r) {
  case RL_DENSITY:
    y = 1;
    break;
  case RL_RANDOM:
    y = (double) (*RL_generator64) () / ULL_TYPE_MAX;
    assert(y>=0. && y<=1.);
    break;
  case 2:
    y = x;
    break;
  case 3:
    y = 1 - x;
    break;
  case 4:
    y = x;
    break;
  }
  return y;
}


/*  64bit Linear congruence generator*/
ULL_TYPE RL_linear64 (void)
{
  /*extern ULL_TYPE seed; */
  time_t *me = NULL;

  /*  If seed is zero then this is first time we have run
   *     * algorithm - generate random number from clock*/
  if (seed == 0) {
    seed = (long long int) time (me);
    seed = (seed != 0) ? seed : 42353223;
  }

  /*  Since m=2^64 and we are dealing with 64bit machines
   * then the taking of modulo m happens auto-magically due
   * to buffer over-flow*/
  seed = (RL_LINEAR64_A * seed + 1) & ULL_TYPE_MAX;

  return seed;
}


/*  64bit Lagged generator, see Knuth*/
ULL_TYPE RL_lagged64 (void)
{
  static ULL_TYPE n[RL_LAGGED_G];
  static int i = RL_LAGGED_N;
  ULL_TYPE a;

  /*   If run out of pre-generated numbers, generate another set */
  if (i == RL_LAGGED_N) {
    RL_lagged64_g (n);
    i = 0;
  }

  a = n[i++];
  return a;
}

/*   Generate another set of numbers for lagged generator, see Knuth
 */
void RL_lagged64_g (ULL_TYPE *n)
{
  int l, k;

  for (k = 0; k < RL_LAGGED_K; k++)
    n[k] = history64[k];
  for (; k < RL_LAGGED_G; k++)
    n[k] = n[k - RL_LAGGED_K] + n[k - RL_LAGGED_L];
  for (l = 0; l < RL_LAGGED_L; l++, k++)
    history64[l] = n[k - RL_LAGGED_K] + n[k - RL_LAGGED_L];
  for (; l < RL_LAGGED_K; l++, k++)
    history64[l] = n[k - RL_LAGGED_K] + n[l - RL_LAGGED_L];
}

/*  Sorts an array of doubles
 */
void RL_sort_d (int n, double *number)
{
  assert (n > 0);
  assert (NULL != number);

  qsort (number, n, sizeof (double), double_comparison);
}

static int double_comparison (const void *dp1, const void *dp2)
{

  if (*(const double *) dp1 < *(const double *) dp2)
    return -1;

  return 1;
}


/*  Initialisation function for random number generators.
 *  Reads state of lagged generator from file ~/.rng64
 */
void RL_Init (const unsigned int seed)
{
  FILE *seed_file;
  char *s, *r;
  char t[100];
  int a;

  SetRandomGenerator (RL_LAGGED);

	if ( seed != 0){
		InitialiseLaggedFromSeed (seed, history64, RL_LAGGED_K);
		return;
	}
  
  #ifdef WINDOWS
    InitialiseLaggedFromClock (history64, RL_LAGGED_K);
    return;
  #endif
  	

  s = getenv ("HOME");
  if ( NULL!=s){
  	r = strcpy (t, s);
  	r = strcat (t, "/");
  } else {
	  t[0] = '\0';
  }
  r = strcat (t, SEEDFILE64);

  seed_file = fopen (t, "r");
  if (NULL == seed_file) {
    /*  22July05. /dev/random appears to be very slow on some computers 
     * -- to date, my PentiumM laptop and (classic) Athlon computer but P4s
     * seem to be fine. This may have something to do with the onboard RNG on
     * the P4. Disabled /dev/random.*/
    /* If seed file cannot be opened, try /dev/random */
    /*seed_file = fopen ("/dev/random", "r");
    if (NULL == seed_file) {*/
      /* Do not have /dev/random or seed file, fall back on
       * C library and pretend it works.
       */
      InitialiseLaggedFromClock (history64, RL_LAGGED_K);
      return;
    /*} else {
      puts ("Initialising random number generator from /dev/random. May take a while.");
      for (a = 0; a < RL_LAGGED_K; a++){
        printf("Read value %d\n",a);
	fread (&history64[a],sizeof(ULL_TYPE),1,seed_file);
      }
      return;
    }*/
  }

  for (a = 0; a < RL_LAGGED_K; a++){
    (void) fscanf (seed_file, "%llu\n", &history64[a]);
  }
    
  fclose (seed_file);

}


/*  Initialise rand() from clock.
 *  This routine makes some dangerous assumptions about the relative
 * sizes of long long int and int.
 */
static void InitialiseLaggedFromClock (ULL_TYPE *d, const int n)
{
  time_t t;
  assert (NULL != d);
  assert (n > 0);

  time (&t);
	InitialiseLaggedFromSeed(t,d,n);
}

static void InitialiseLaggedFromSeed (const unsigned int seed, ULL_TYPE *d, const int n){
  assert (NULL != d);
  assert (n > 0);

  srand (seed);
  for ( int i = 0; i < n; i++) {
  	d[i] = 0;
  	for ( int j=0 ; j<sizeof(ULL_TYPE) ; j++){
			d[i] += rand()&0xff;
			d[i] <<= 8;
		}
	}
}


/*  Saves state of lagged generator to file ~/.rng64
 */
void RL_Close (void)
{
  FILE *seed_file;
  char *s, *r;
  char t[100];
  int a;
  
  #ifdef WINDOWS
  	return;
  #endif

  s = getenv ("HOME");
  OOM (s);
  r = strcpy (t, s);
  r = strcat (t, "/");
  r = strcat (t, SEEDFILE64);
  seed_file = fopen (t, "w");
  if (seed_file == NULL) {
    printf ("Failed to open random number file for writing!\n");
    exit (EXIT_FAILURE);
  }
  for (a = 0; a < RL_LAGGED_K; a++)
    fprintf (seed_file, "%llu\n", history64[a]);
  fclose (seed_file);
}


/*  Divide and conquer method for calculating x^y.
 *  Even with overhead of function calling, this is
 * quicker than naive method for surprisingly small y.
 */
static long long int ipow (int x, int y)
{
  long long int z;

  assert (y >= 0);

  if (y >= 2) {
    /* Divide and conquer recursion. */
    z = ipow (x, y / 2);
    switch (y % 2) {
    case 0:
      return z * z;
    case 1:
      return x * z * z;
    }
  }
  else if (1 == y) {
    return x;
  }

  assert (0 == y);
  return 1;			/*  Only occurs when y==0 */
}
