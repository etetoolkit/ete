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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include "options.h"

#define OOM(A)	if(NULL==A) { fputs("Out of memory!",stderr); fflush(stderr); exit(EXIT_FAILURE); }
#define MAXSTRING 80
typedef struct
{
  void **val;
} OPTIONS;

OPTIONS *opt = NULL;

extern int n_options;
extern char *options[];
extern char *optiondefault[];
extern char optiontype[];
extern int optionlength[];
extern char *default_optionfile;

static char GetString (int maxsize, char *string, FILE * fp);
static void ReadOptionsFromCommandLine (int argc, char **argv);
static void ReadOptionsFromFile (char *filename);
static int AddOption (const int key, const char *value);
static void SetDefaultOptions (void);
static void *GetOptionByKey (const int key);


void ReadOptions (int argc, char **argv)
{
  char *file = NULL;

  if (opt != NULL)
    puts ("Already read options.\n Over-writing.");
  else {
    SetDefaultOptions ();
  }

  // If no filename is given at command line, use default
  if (argc == 1 || argv[1][0] == '-')
    file = default_optionfile;
  // Is the first argument a file rather than an option, if so then read
  else
    file = argv[1];
  if (file != NULL)
    ReadOptionsFromFile (file);

  ReadOptionsFromCommandLine (argc, argv);

  return;
}

void SetDefaultOptions (void)
{
  int i;

  assert (NULL!=optiondefault);


  if (opt == NULL) {
    opt = malloc (sizeof (OPTIONS));
    OOM(opt);
    opt->val = malloc (n_options * sizeof (void *));
    OOM(opt->val);
    for (i = 0; i < n_options; i++)
      opt->val[i] = NULL;
  }

  for (i = 0; i < n_options; i++)
    AddOption (i, optiondefault[i]);

  return;
}

static int AddOption (const int key, const char *value)
{
  int i = -1;
  int val_len;

  assert(key>=0);
  assert(NULL!=value);

  val_len = strlen(value)+1;
  // Is there already an option here?
  if ( opt->val[key]!=NULL)
    free(opt->val[key]);
  switch (optiontype[key]) {
    case 's':
      opt->val[key] = malloc (val_len * sizeof (char));
      break;
    case 'd':
      opt->val[key] = malloc (sizeof (int));
      break;
    case 'f':
      opt->val[key] = malloc (sizeof (double));
      break;
    case 'c':
      opt->val[key] = malloc (sizeof (char));
      break;
  };

  // Read option into array
  switch (optiontype[key]) {
  case 's':
    strncpy ((char *)(opt->val[key]),value,val_len);
    i=1;
    ((char *)opt->val[key])[val_len-1] = '\0';  // Make sure null terminated
    break;
  case 'd':
    i = sscanf (value, "%d", (int *) opt->val[key]);
    break;
  case 'f':
    i = sscanf (value, "%le", (double *) opt->val[key]);
    break;
  case 'c':
    i = sscanf (value, "%c", (char *) opt->val[key]);
    break;
  };

  return i;
}

static void *GetOptionByKey (const int key)
{
  if (key >= n_options)
    return NULL;

  return opt->val[key];
}

void *GetOption (char *optname)
{
  int key = 0;

  assert(NULL!=optname);
  assert(n_options>0);
  assert(NULL!=options);

  while (key < n_options && strcmp (optname, options[key]) != 0) {
    key++;
  }
  if (key >= n_options)
    return NULL;

  return (GetOptionByKey (key));
}


void ReadOptionsFromFile (char *filename)
{
  FILE *fp;
  char str[MAXSTRING], c;
  int key;

  assert(NULL!=filename);
  assert(NULL!=options);
  assert(n_options>0);

  fp = fopen (filename, "r");
  if (NULL == fp) {
    fprintf (stderr,
	     "Failed to open file %s to read options from.\nUsing defaults and those options provided on command line.\n",
	     filename);
    return;
  }

  while ((c = GetString (MAXSTRING, str, fp)) != EOF) {
    // Was string blank? A newline in file
    if(strcmp(str,"")==0) continue;
    // Find option key
    key = 0;
    while (key < n_options && strcmp (str, options[key]) != 0) {
      key++;
    }

    if (key < n_options) {
      // Read value
      c = GetString (MAXSTRING, str, fp);
      if (c == EOF) {
	printf
	  ("Found option but there was no value before the end of the file.\n");
      }
      else
	AddOption (key, str);
    }
    else {
      printf ("Unrecognised option %s. Continuing.\n", str);
    }
  }
  fclose (fp);
}

void ReadOptionsFromCommandLine (int argc, char **argv)
{
  int i, key, mod;

  for (i = 1; i < argc; i++) {
    mod = 1;
    if (argv[i][0] != '-') {
      if (i == 1)
	continue;
      else
	mod = 0;
    }
    key = 0;
    while (key < n_options && strcmp (&argv[i][mod], options[key]) != 0) {
      key++;
    }
    if (key < n_options) {
      i++;
      if (i < argc)
	mod = AddOption (key, argv[i]);
      else
	printf ("Didn't find value before end of command line option.\n");
      if (mod == 0)
	i--;
    }
    else {
      printf ("Unrecognised option %s. Continuing.\n", argv[i]);
    }
  }
}

char GetString (int maxsize, char *string, FILE * fp)
{
  int i = 0;
  char c;

  while (isspace (c = getc (fp)) && c != '\n' && c != EOF);

  while (c == '#' && c!='\n' && c != EOF) {
    while ((c = getc (fp)) != EOF && c != '\n');
    while (isspace (c = getc (fp)) && c != EOF);
  }
  if (c != '\n')
    ungetc (c, fp);

  while (i < (maxsize - 1) && c!='\n' && (c = getc (fp)) != EOF && !isspace (c)
	 && c != '#') {
    if (c == '#')
      while ((c = getc (fp)) != EOF && c != '\n');
    if (!ispunct (c) || c == '_' || c == '-' || c == '.' || c == '+')
      string[i++] = c;
  };
  string[i] = '\0';

  if (c == '#')
    while ((c = getc (fp)) != EOF && c != '\n');
  return c;
}

void PrintOptions (void)
{
  int i;
  assert (NULL!=optiontype);
  assert (n_options>0);
  assert (NULL!=options);
  assert (NULL!=opt);

  for (i = 0; i < n_options; i++) {
    if (opt->val[i] != NULL) {
      switch (optiontype[i]) {
      case 'd':
	printf ("%12s:    %d\n", options[i], *(int *) opt->val[i]);
	break;
      case 'f':
	printf ("%12s:    %e\n", options[i], *(double *) opt->val[i]);
	break;
      case 's':
	printf ("%12s:    %s\n", options[i], (char *) opt->val[i]);
	break;
      case 'c':
	printf ("%12s:    %c\n", options[i], *(char *) opt->val[i]);
	break;
      }
    }
  }
  printf ("\n");
}
