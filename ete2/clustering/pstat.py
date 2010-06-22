# Copyright (c) 1999-2007 Gary Strangman; All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Comments and/or additions are welcome (send e-mail to:
# strang@nmr.mgh.harvard.edu).
# 
"""
pstat.py module

#################################################
#######  Written by:  Gary Strangman  ###########
#######  Last modified:  Dec 18, 2007 ###########
#################################################

This module provides some useful list and array manipulation routines
modeled after those found in the |Stat package by Gary Perlman, plus a
number of other useful list/file manipulation functions.  The list-based
functions include:

      abut (source,*args)
      simpleabut (source, addon)
      colex (listoflists,cnums)
      collapse (listoflists,keepcols,collapsecols,fcn1=None,fcn2=None,cfcn=None)
      dm (listoflists,criterion)
      flat (l)
      linexand (listoflists,columnlist,valuelist)
      linexor (listoflists,columnlist,valuelist)
      linedelimited (inlist,delimiter)
      lineincols (inlist,colsize) 
      lineincustcols (inlist,colsizes)
      list2string (inlist)
      makelol(inlist)
      makestr(x)
      printcc (lst,extra=2)
      printincols (listoflists,colsize)
      pl (listoflists)
      printl(listoflists)
      replace (lst,oldval,newval)
      recode (inlist,listmap,cols='all')
      remap (listoflists,criterion)
      roundlist (inlist,num_digits_to_round_floats_to)
      sortby(listoflists,sortcols)
      unique (inlist)
      duplicates(inlist)
      writedelimited (listoflists, delimiter, file, writetype='w')

Some of these functions have alternate versions which are defined only if
Numeric (NumPy) can be imported.  These functions are generally named as
above, with an 'a' prefix.

      aabut (source, *args)
      acolex (a,indices,axis=1)
      acollapse (a,keepcols,collapsecols,sterr=0,ns=0)
      adm (a,criterion)
      alinexand (a,columnlist,valuelist)
      alinexor (a,columnlist,valuelist)
      areplace (a,oldval,newval)
      arecode (a,listmap,col='all')
      arowcompare (row1, row2)
      arowsame (row1, row2)
      asortrows(a,axis=0)
      aunique(inarray)
      aduplicates(inarray)

Currently, the code is all but completely un-optimized.  In many cases, the
array versions of functions amount simply to aliases to built-in array
functions/methods.  Their inclusion here is for function name consistency.
"""

## CHANGE LOG:
## ==========
## 07-11-26 ... edited to work with numpy
## 01-11-15 ... changed list2string() to accept a delimiter
## 01-06-29 ... converted exec()'s to eval()'s to make compatible with Py2.1
## 01-05-31 ... added duplicates() and aduplicates() functions
## 00-12-28 ... license made GPL, docstring and import requirements
## 99-11-01 ... changed version to 0.3
## 99-08-30 ... removed get, getstrings, put, aget, aput (into io.py)
## 03/27/99 ... added areplace function, made replace fcn recursive
## 12/31/98 ... added writefc function for ouput to fixed column sizes
## 12/07/98 ... fixed import problem (failed on collapse() fcn)
##              added __version__ variable (now 0.2)
## 12/05/98 ... updated doc-strings
##              added features to collapse() function
##              added flat() function for lists
##              fixed a broken asortrows() 
## 11/16/98 ... fixed minor bug in aput for 1D arrays
##
## 11/08/98 ... fixed aput to output large arrays correctly

import stats  # required 3rd party module
import string, copy
from types import *

__version__ = 0.4

###===========================  LIST FUNCTIONS  ==========================
###
### Here are the list functions, DEFINED FOR ALL SYSTEMS.
### Array functions (for NumPy-enabled computers) appear below.
###

def abut (source,*args):
    """
Like the |Stat abut command.  It concatenates two lists side-by-side
and returns the result.  '2D' lists are also accomodated for either argument
(source or addon).  CAUTION:  If one list is shorter, it will be repeated
until it is as long as the longest list.  If this behavior is not desired,
use pstat.simpleabut().

Usage:   abut(source, args)   where args=any # of lists
Returns: a list of lists as long as the LONGEST list past, source on the
         'left', lists in <args> attached consecutively on the 'right'
"""

    if type(source) not in [ListType,TupleType]:
        source = [source]
    for addon in args:
        if type(addon) not in [ListType,TupleType]:
            addon = [addon]
        if len(addon) < len(source):                # is source list longer?
            if len(source) % len(addon) == 0:        # are they integer multiples?
                repeats = len(source)/len(addon)    # repeat addon n times
                origadd = copy.deepcopy(addon)
                for i in range(repeats-1):
                    addon = addon + origadd
            else:
                repeats = len(source)/len(addon)+1  # repeat addon x times,
                origadd = copy.deepcopy(addon)      #    x is NOT an integer
                for i in range(repeats-1):
                    addon = addon + origadd
                    addon = addon[0:len(source)]
        elif len(source) < len(addon):                # is addon list longer?
            if len(addon) % len(source) == 0:        # are they integer multiples?
                repeats = len(addon)/len(source)    # repeat source n times
                origsour = copy.deepcopy(source)
                for i in range(repeats-1):
                    source = source + origsour
            else:
                repeats = len(addon)/len(source)+1  # repeat source x times,
                origsour = copy.deepcopy(source)    #   x is NOT an integer
                for i in range(repeats-1):
                    source = source + origsour
                source = source[0:len(addon)]

        source = simpleabut(source,addon)
    return source


def simpleabut (source, addon):
    """
Concatenates two lists as columns and returns the result.  '2D' lists
are also accomodated for either argument (source or addon).  This DOES NOT
repeat either list to make the 2 lists of equal length.  Beware of list pairs
with different lengths ... the resulting list will be the length of the
FIRST list passed.

Usage:   simpleabut(source,addon)  where source, addon=list (or list-of-lists)
Returns: a list of lists as long as source, with source on the 'left' and
                 addon on the 'right'
"""
    if type(source) not in [ListType,TupleType]:
        source = [source]
    if type(addon) not in [ListType,TupleType]:
        addon = [addon]
    minlen = min(len(source),len(addon))
    list = copy.deepcopy(source)                # start abut process
    if type(source[0]) not in [ListType,TupleType]:
        if type(addon[0]) not in [ListType,TupleType]:
            for i in range(minlen):
                list[i] = [source[i]] + [addon[i]]        # source/addon = column
        else:
            for i in range(minlen):
                list[i] = [source[i]] + addon[i]        # addon=list-of-lists
    else:
        if type(addon[0]) not in [ListType,TupleType]:
            for i in range(minlen):
                list[i] = source[i] + [addon[i]]        # source=list-of-lists
        else:
            for i in range(minlen):
                list[i] = source[i] + addon[i]        # source/addon = list-of-lists
    source = list
    return source


def colex (listoflists,cnums):
    """
Extracts from listoflists the columns specified in the list 'cnums'
(cnums can be an integer, a sequence of integers, or a string-expression that
corresponds to a slice operation on the variable x ... e.g., 'x[3:]' will colex
columns 3 onward from the listoflists).

Usage:   colex (listoflists,cnums)
Returns: a list-of-lists corresponding to the columns from listoflists
         specified by cnums, in the order the column numbers appear in cnums
"""
    global index
    column = 0
    if type(cnums) in [ListType,TupleType]:   # if multiple columns to get
        index = cnums[0]
        column = map(lambda x: x[index], listoflists)
        for col in cnums[1:]:
            index = col
            column = abut(column,map(lambda x: x[index], listoflists))
    elif type(cnums) == StringType:              # if an 'x[3:]' type expr.
        evalstring = 'map(lambda x: x'+cnums+', listoflists)'
        column = eval(evalstring)
    else:                                     # else it's just 1 col to get
        index = cnums
        column = map(lambda x: x[index], listoflists)
    return column


def collapse (listoflists,keepcols,collapsecols,fcn1=None,fcn2=None,cfcn=None):
     """
Averages data in collapsecol, keeping all unique items in keepcols
(using unique, which keeps unique LISTS of column numbers), retaining the
unique sets of values in keepcols, the mean for each.  Setting fcn1
and/or fcn2 to point to a function rather than None (e.g., stats.sterr, len)
will append those results (e.g., the sterr, N) after each calculated mean.
cfcn is the collapse function to apply (defaults to mean, defined here in the
pstat module to avoid circular imports with stats.py, but harmonicmean or
others could be passed).

Usage:    collapse (listoflists,keepcols,collapsecols,fcn1=None,fcn2=None,cfcn=None)
Returns: a list of lists with all unique permutations of entries appearing in
     columns ("conditions") specified by keepcols, abutted with the result of
     cfcn (if cfcn=None, defaults to the mean) of each column specified by
     collapsecols.
"""
     def collmean (inlist):
         s = 0
         for item in inlist:
             s = s + item
         return s/float(len(inlist))

     if type(keepcols) not in [ListType,TupleType]:
         keepcols = [keepcols]
     if type(collapsecols) not in [ListType,TupleType]:
         collapsecols = [collapsecols]
     if cfcn == None:
         cfcn = collmean
     if keepcols == []:
         means = [0]*len(collapsecols)
         for i in range(len(collapsecols)):
             avgcol = colex(listoflists,collapsecols[i])
             means[i] = cfcn(avgcol)
             if fcn1:
                 try:
                     test = fcn1(avgcol)
                 except:
                     test = 'N/A'
                     means[i] = [means[i], test]
             if fcn2:
                 try:
                     test = fcn2(avgcol)
                 except:
                     test = 'N/A'
                 try:
                     means[i] = means[i] + [len(avgcol)]
                 except TypeError:
                     means[i] = [means[i],len(avgcol)]
         return means
     else:
         values = colex(listoflists,keepcols)
         uniques = unique(values)
         uniques.sort()
         newlist = []
         if type(keepcols) not in [ListType,TupleType]:  keepcols = [keepcols]
         for item in uniques:
             if type(item) not in [ListType,TupleType]:  item =[item]
             tmprows = linexand(listoflists,keepcols,item)
             for col in collapsecols:
                 avgcol = colex(tmprows,col)
                 item.append(cfcn(avgcol))
                 if fcn1 <> None:
                     try:
                         test = fcn1(avgcol)
                     except:
                         test = 'N/A'
                     item.append(test)
                 if fcn2 <> None:
                     try:
                         test = fcn2(avgcol)
                     except:
                         test = 'N/A'
                     item.append(test)
                 newlist.append(item)
         return newlist


def dm (listoflists,criterion):
    """
Returns rows from the passed list of lists that meet the criteria in
the passed criterion expression (a string as a function of x; e.g., 'x[3]>=9'
will return all rows where the 4th column>=9 and "x[2]=='N'" will return rows
with column 2 equal to the string 'N').

Usage:   dm (listoflists, criterion)
Returns: rows from listoflists that meet the specified criterion.
"""
    function = 'filter(lambda x: '+criterion+',listoflists)'
    lines = eval(function)
    return lines


def flat(l):
    """
Returns the flattened version of a '2D' list.  List-correlate to the a.ravel()()
method of NumPy arrays.

Usage:    flat(l)
"""
    newl = []
    for i in range(len(l)):
        for j in range(len(l[i])):
            newl.append(l[i][j])
    return newl


def linexand (listoflists,columnlist,valuelist):
    """
Returns the rows of a list of lists where col (from columnlist) = val
(from valuelist) for EVERY pair of values (columnlist[i],valuelists[i]).
len(columnlist) must equal len(valuelist).

Usage:   linexand (listoflists,columnlist,valuelist)
Returns: the rows of listoflists where columnlist[i]=valuelist[i] for ALL i
"""
    if type(columnlist) not in [ListType,TupleType]:
        columnlist = [columnlist]
    if type(valuelist) not in [ListType,TupleType]:
        valuelist = [valuelist]
    criterion = ''
    for i in range(len(columnlist)):
        if type(valuelist[i])==StringType:
            critval = '\'' + valuelist[i] + '\''
        else:
            critval = str(valuelist[i])
        criterion = criterion + ' x['+str(columnlist[i])+']=='+critval+' and'
    criterion = criterion[0:-3]         # remove the "and" after the last crit
    function = 'filter(lambda x: '+criterion+',listoflists)'
    lines = eval(function)
    return lines


def linexor (listoflists,columnlist,valuelist):
    """
Returns the rows of a list of lists where col (from columnlist) = val
(from valuelist) for ANY pair of values (colunmlist[i],valuelist[i[).
One value is required for each column in columnlist.  If only one value
exists for columnlist but multiple values appear in valuelist, the
valuelist values are all assumed to pertain to the same column.

Usage:   linexor (listoflists,columnlist,valuelist)
Returns: the rows of listoflists where columnlist[i]=valuelist[i] for ANY i
"""
    if type(columnlist) not in [ListType,TupleType]:
        columnlist = [columnlist]
    if type(valuelist) not in [ListType,TupleType]:
        valuelist = [valuelist]
    criterion = ''
    if len(columnlist) == 1 and len(valuelist) > 1:
        columnlist = columnlist*len(valuelist)
    for i in range(len(columnlist)):          # build an exec string
        if type(valuelist[i])==StringType:
            critval = '\'' + valuelist[i] + '\''
        else:
            critval = str(valuelist[i])
        criterion = criterion + ' x['+str(columnlist[i])+']=='+critval+' or'
    criterion = criterion[0:-2]         # remove the "or" after the last crit
    function = 'filter(lambda x: '+criterion+',listoflists)'
    lines = eval(function)
    return lines


def linedelimited (inlist,delimiter):
    """
Returns a string composed of elements in inlist, with each element
separated by 'delimiter.'  Used by function writedelimited.  Use '\t'
for tab-delimiting.

Usage:   linedelimited (inlist,delimiter)
"""
    outstr = ''
    for item in inlist:
        if type(item) <> StringType:
            item = str(item)
        outstr = outstr + item + delimiter
    outstr = outstr[0:-1]
    return outstr


def lineincols (inlist,colsize):
    """
Returns a string composed of elements in inlist, with each element
right-aligned in columns of (fixed) colsize.

Usage:   lineincols (inlist,colsize)   where colsize is an integer
"""
    outstr = ''
    for item in inlist:
        if type(item) <> StringType:
            item = str(item)
        size = len(item)
        if size <= colsize:
            for i in range(colsize-size):
                outstr = outstr + ' '
            outstr = outstr + item
        else:
            outstr = outstr + item[0:colsize+1]
    return outstr


def lineincustcols (inlist,colsizes):
    """
Returns a string composed of elements in inlist, with each element
right-aligned in a column of width specified by a sequence colsizes.  The
length of colsizes must be greater than or equal to the number of columns
in inlist.

Usage:   lineincustcols (inlist,colsizes)
Returns: formatted string created from inlist
"""
    outstr = ''
    for i in range(len(inlist)):
        if type(inlist[i]) <> StringType:
            item = str(inlist[i])
        else:
            item = inlist[i]
        size = len(item)
        if size <= colsizes[i]:
            for j in range(colsizes[i]-size):
                outstr = outstr + ' '
            outstr = outstr + item
        else:
            outstr = outstr + item[0:colsizes[i]+1]
    return outstr


def list2string (inlist,delimit=' '):
    """
Converts a 1D list to a single long string for file output, using
the string.join function.

Usage:   list2string (inlist,delimit=' ')
Returns: the string created from inlist
"""
    stringlist = map(makestr,inlist)
    return string.join(stringlist,delimit)


def makelol(inlist):
    """
Converts a 1D list to a 2D list (i.e., a list-of-lists).  Useful when you
want to use put() to write a 1D list one item per line in the file.

Usage:   makelol(inlist)
Returns: if l = [1,2,'hi'] then returns [[1],[2],['hi']] etc.
"""
    x = []
    for item in inlist:
        x.append([item])
    return x


def makestr (x):
    if type(x) <> StringType:
        x = str(x)
    return x


def printcc (lst,extra=2):
    """
Prints a list of lists in columns, customized by the max size of items
within the columns (max size of items in col, plus 'extra' number of spaces).
Use 'dashes' or '\\n' in the list-of-lists to print dashes or blank lines,
respectively.

Usage:   printcc (lst,extra=2)
Returns: None
"""
    if type(lst[0]) not in [ListType,TupleType]:
        lst = [lst]
    rowstokill = []
    list2print = copy.deepcopy(lst)
    for i in range(len(lst)):
        if lst[i] == ['\n'] or lst[i]=='\n' or lst[i]=='dashes' or lst[i]=='' or lst[i]==['']:
            rowstokill = rowstokill + [i]
    rowstokill.reverse()   # delete blank rows from the end
    for row in rowstokill:
        del list2print[row]
    maxsize = [0]*len(list2print[0])
    for col in range(len(list2print[0])):
        items = colex(list2print,col)
        items = map(makestr,items)
        maxsize[col] = max(map(len,items)) + extra
    for row in lst:
        if row == ['\n'] or row == '\n' or row == '' or row == ['']:
            print
        elif row == ['dashes'] or row == 'dashes':
            dashes = [0]*len(maxsize)
            for j in range(len(maxsize)):
                dashes[j] = '-'*(maxsize[j]-2)
            print lineincustcols(dashes,maxsize)
        else:
            print lineincustcols(row,maxsize)
    return None


def printincols (listoflists,colsize):
    """
Prints a list of lists in columns of (fixed) colsize width, where
colsize is an integer.

Usage:   printincols (listoflists,colsize)
Returns: None
"""
    for row in listoflists:
        print lineincols(row,colsize)
    return None


def pl (listoflists):
    """
Prints a list of lists, 1 list (row) at a time.

Usage:   pl(listoflists)
Returns: None
"""
    for row in listoflists:
        if row[-1] == '\n':
            print row,
        else:
            print row
    return None


def printl(listoflists):
    """Alias for pl."""
    pl(listoflists)
    return


def replace (inlst,oldval,newval):
    """
Replaces all occurrences of 'oldval' with 'newval', recursively.

Usage:   replace (inlst,oldval,newval)
"""
    lst = inlst*1
    for i in range(len(lst)):
        if type(lst[i]) not in [ListType,TupleType]:
            if lst[i]==oldval: lst[i]=newval
        else:
            lst[i] = replace(lst[i],oldval,newval)
    return lst


def recode (inlist,listmap,cols=None):
    """
Changes the values in a list to a new set of values (useful when
you need to recode data from (e.g.) strings to numbers.  cols defaults
to None (meaning all columns are recoded).

Usage:   recode (inlist,listmap,cols=None)  cols=recode cols, listmap=2D list
Returns: inlist with the appropriate values replaced with new ones
"""
    lst = copy.deepcopy(inlist)
    if cols != None:
        if type(cols) not in [ListType,TupleType]:
            cols = [cols]
        for col in cols:
            for row in range(len(lst)):
                try:
                    idx = colex(listmap,0).index(lst[row][col])
                    lst[row][col] = listmap[idx][1]
                except ValueError:
                    pass
    else:
        for row in range(len(lst)):
            for col in range(len(lst)):
                try:
                    idx = colex(listmap,0).index(lst[row][col])
                    lst[row][col] = listmap[idx][1]
                except ValueError:
                    pass
    return lst


def remap (listoflists,criterion):
    """
Remaps values in a given column of a 2D list (listoflists).  This requires
a criterion as a function of 'x' so that the result of the following is
returned ... map(lambda x: 'criterion',listoflists).  

Usage:   remap(listoflists,criterion)    criterion=string
Returns: remapped version of listoflists
"""
    function = 'map(lambda x: '+criterion+',listoflists)'
    lines = eval(function)
    return lines


def roundlist (inlist,digits):
    """
Goes through each element in a 1D or 2D inlist, and applies the following
function to all elements of FloatType ... round(element,digits).

Usage:   roundlist(inlist,digits)
Returns: list with rounded floats
"""
    if type(inlist[0]) in [IntType, FloatType]:
        inlist = [inlist]
    l = inlist*1
    for i in range(len(l)):
        for j in range(len(l[i])):
            if type(l[i][j])==FloatType:
                l[i][j] = round(l[i][j],digits)
    return l


def sortby(listoflists,sortcols):
    """
Sorts a list of lists on the column(s) specified in the sequence
sortcols.

Usage:   sortby(listoflists,sortcols)
Returns: sorted list, unchanged column ordering
"""
    newlist = abut(colex(listoflists,sortcols),listoflists)
    newlist.sort()
    try:
        numcols = len(sortcols)
    except TypeError:
        numcols = 1
    crit = '[' + str(numcols) + ':]'
    newlist = colex(newlist,crit)
    return newlist


def unique (inlist):
    """
Returns all unique items in the passed list.  If the a list-of-lists
is passed, unique LISTS are found (i.e., items in the first dimension are
compared).

Usage:   unique (inlist)
Returns: the unique elements (or rows) in inlist
"""
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append(item)
    return uniques

def duplicates(inlist):
    """
Returns duplicate items in the FIRST dimension of the passed list.

Usage:   duplicates (inlist)
"""
    dups = []
    for i in range(len(inlist)):
        if inlist[i] in inlist[i+1:]:
            dups.append(inlist[i])
    return dups


def nonrepeats(inlist):
    """
Returns items that are NOT duplicated in the first dim of the passed list.

Usage:   nonrepeats (inlist)
"""
    nonrepeats = []
    for i in range(len(inlist)):
        if inlist.count(inlist[i]) == 1:
            nonrepeats.append(inlist[i])
    return nonrepeats


#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================
#===================   PSTAT ARRAY FUNCTIONS  =====================

try:                         # DEFINE THESE *ONLY* IF numpy IS AVAILABLE
 import numpy as N

 def aabut (source, *args):
    """
Like the |Stat abut command.  It concatenates two arrays column-wise
and returns the result.  CAUTION:  If one array is shorter, it will be
repeated until it is as long as the other.

Usage:   aabut (source, args)    where args=any # of arrays
Returns: an array as long as the LONGEST array past, source appearing on the
         'left', arrays in <args> attached on the 'right'.
"""
    if len(source.shape)==1:
        width = 1
        source = N.resize(source,[source.shape[0],width])
    else:
        width = source.shape[1]
    for addon in args:
        if len(addon.shape)==1:
            width = 1
            addon = N.resize(addon,[source.shape[0],width])
        else:
            width = source.shape[1]
        if len(addon) < len(source):
            addon = N.resize(addon,[source.shape[0],addon.shape[1]])
        elif len(source) < len(addon):
            source = N.resize(source,[addon.shape[0],source.shape[1]])
        source = N.concatenate((source,addon),1)
    return source


 def acolex (a,indices,axis=1):
    """
Extracts specified indices (a list) from passed array, along passed
axis (column extraction is default).  BEWARE: A 1D array is presumed to be a
column-array (and that the whole array will be returned as a column).

Usage:   acolex (a,indices,axis=1)
Returns: the columns of a specified by indices
"""
    if type(indices) not in [ListType,TupleType,N.ndarray]:
        indices = [indices]
    if len(N.shape(a)) == 1:
        cols = N.resize(a,[a.shape[0],1])
    else:
        cols = N.take(a,indices,axis)
    return cols


 def acollapse (a,keepcols,collapsecols,fcn1=None,fcn2=None,cfcn=None):
    """
Averages data in collapsecol, keeping all unique items in keepcols
(using unique, which keeps unique LISTS of column numbers), retaining
the unique sets of values in keepcols, the mean for each.  If stderror or
N of the mean are desired, set either or both parameters to 1.

Usage:   acollapse (a,keepcols,collapsecols,fcn1=None,fcn2=None,cfcn=None)
Returns: unique 'conditions' specified by the contents of columns specified
         by keepcols, abutted with the mean(s) of column(s) specified by
         collapsecols
"""
    def acollmean (inarray):
        return N.sum(N.ravel(inarray))

    if type(keepcols) not in [ListType,TupleType,N.ndarray]:
        keepcols = [keepcols]
    if type(collapsecols) not in [ListType,TupleType,N.ndarray]:
        collapsecols = [collapsecols]

    if cfcn == None:
        cfcn = acollmean
    if keepcols == []:
        avgcol = acolex(a,collapsecols)
        means = N.sum(avgcol)/float(len(avgcol))
        if fcn1<>None:
            try:
                test = fcn1(avgcol)
            except:
                test = N.array(['N/A']*len(means))
            means = aabut(means,test)
        if fcn2<>None:
            try:
                test = fcn2(avgcol)
            except:
                test = N.array(['N/A']*len(means))
            means = aabut(means,test)
        return means
    else:
        if type(keepcols) not in [ListType,TupleType,N.ndarray]:
            keepcols = [keepcols]
        values = colex(a,keepcols)   # so that "item" can be appended (below)
        uniques = unique(values)  # get a LIST, so .sort keeps rows intact
        uniques.sort()
        newlist = []
        for item in uniques:
            if type(item) not in [ListType,TupleType,N.ndarray]:
                item =[item]
            tmprows = alinexand(a,keepcols,item)
            for col in collapsecols:
                avgcol = acolex(tmprows,col)
                item.append(acollmean(avgcol))
                if fcn1<>None:
                    try:
                        test = fcn1(avgcol)
                    except:
                        test = 'N/A'
                    item.append(test)
                if fcn2<>None:
                    try:
                        test = fcn2(avgcol)
                    except:
                        test = 'N/A'
                    item.append(test)
                newlist.append(item)
        try:
            new_a = N.array(newlist)
        except TypeError:
            new_a = N.array(newlist,'O')
        return new_a


 def adm (a,criterion):
    """
Returns rows from the passed list of lists that meet the criteria in
the passed criterion expression (a string as a function of x).

Usage:   adm (a,criterion)   where criterion is like 'x[2]==37'
"""
    function = 'filter(lambda x: '+criterion+',a)'
    lines = eval(function)
    try:
        lines = N.array(lines)
    except:
        lines = N.array(lines,dtype='O')
    return lines


 def isstring(x):
    if type(x)==StringType:
        return 1
    else:
        return 0


 def alinexand (a,columnlist,valuelist):
    """
Returns the rows of an array where col (from columnlist) = val
(from valuelist).  One value is required for each column in columnlist.

Usage:   alinexand (a,columnlist,valuelist)
Returns: the rows of a where columnlist[i]=valuelist[i] for ALL i
"""
    if type(columnlist) not in [ListType,TupleType,N.ndarray]:
        columnlist = [columnlist]
    if type(valuelist) not in [ListType,TupleType,N.ndarray]:
        valuelist = [valuelist]
    criterion = ''
    for i in range(len(columnlist)):
        if type(valuelist[i])==StringType:
            critval = '\'' + valuelist[i] + '\''
        else:
            critval = str(valuelist[i])
        criterion = criterion + ' x['+str(columnlist[i])+']=='+critval+' and'
    criterion = criterion[0:-3]         # remove the "and" after the last crit
    return adm(a,criterion)


 def alinexor (a,columnlist,valuelist):
    """
Returns the rows of an array where col (from columnlist) = val (from
valuelist).  One value is required for each column in columnlist.
The exception is if either columnlist or valuelist has only 1 value,
in which case that item will be expanded to match the length of the
other list.

Usage:   alinexor (a,columnlist,valuelist)
Returns: the rows of a where columnlist[i]=valuelist[i] for ANY i
"""
    if type(columnlist) not in [ListType,TupleType,N.ndarray]:
        columnlist = [columnlist]
    if type(valuelist) not in [ListType,TupleType,N.ndarray]:
        valuelist = [valuelist]
    criterion = ''
    if len(columnlist) == 1 and len(valuelist) > 1:
        columnlist = columnlist*len(valuelist)
    elif len(valuelist) == 1 and len(columnlist) > 1:
        valuelist = valuelist*len(columnlist)
    for i in range(len(columnlist)):
        if type(valuelist[i])==StringType:
            critval = '\'' + valuelist[i] + '\''
        else:
            critval = str(valuelist[i])
        criterion = criterion + ' x['+str(columnlist[i])+']=='+critval+' or'
    criterion = criterion[0:-2]         # remove the "or" after the last crit
    return adm(a,criterion)


 def areplace (a,oldval,newval):
    """
Replaces all occurrences of oldval with newval in array a.

Usage:   areplace(a,oldval,newval)
"""
    return N.where(a==oldval,newval,a)


 def arecode (a,listmap,col='all'):
    """
Remaps the values in an array to a new set of values (useful when
you need to recode data from (e.g.) strings to numbers as most stats
packages require.  Can work on SINGLE columns, or 'all' columns at once.
@@@BROKEN 2007-11-26

Usage:   arecode (a,listmap,col='all')
Returns: a version of array a where listmap[i][0] = (instead) listmap[i][1]
"""
    ashape = a.shape
    if col == 'all':
        work = a.ravel()
    else:
        work = acolex(a,col)
        work = work.ravel()
    for pair in listmap:
        if type(pair[1]) == StringType or work.dtype.char=='O' or a.dtype.char=='O':
            work = N.array(work,dtype='O')
            a = N.array(a,dtype='O')
            for i in range(len(work)):
                if work[i]==pair[0]:
                    work[i] = pair[1]
            if col == 'all':
                return N.reshape(work,ashape)
            else:
                return N.concatenate([a[:,0:col],work[:,N.newaxis],a[:,col+1:]],1)
        else:   # must be a non-Object type array and replacement
            work = N.where(work==pair[0],pair[1],work)
            return N.concatenate([a[:,0:col],work[:,N.newaxis],a[:,col+1:]],1)


 def arowcompare(row1, row2):
    """
Compares two rows from an array, regardless of whether it is an
array of numbers or of python objects (which requires the cmp function).
@@@PURPOSE? 2007-11-26

Usage:   arowcompare(row1,row2)
Returns: an array of equal length containing 1s where the two rows had
         identical elements and 0 otherwise
"""
    return 
    if row1.dtype.char=='O' or row2.dtype=='O':
        cmpvect = N.logical_not(abs(N.array(map(cmp,row1,row2)))) # cmp fcn gives -1,0,1
    else:
        cmpvect = N.equal(row1,row2)
    return cmpvect


 def arowsame(row1, row2):
    """
Compares two rows from an array, regardless of whether it is an
array of numbers or of python objects (which requires the cmp function).

Usage:   arowsame(row1,row2)
Returns: 1 if the two rows are identical, 0 otherwise.
"""
    cmpval = N.alltrue(arowcompare(row1,row2))
    return cmpval


 def asortrows(a,axis=0):
    """
Sorts an array "by rows".  This differs from the Numeric.sort() function,
which sorts elements WITHIN the given axis.  Instead, this function keeps
the elements along the given axis intact, but shifts them 'up or down'
relative to one another.

Usage:   asortrows(a,axis=0)
Returns: sorted version of a
"""
    return N.sort(a,axis=axis,kind='mergesort')


 def aunique(inarray):
    """
Returns unique items in the FIRST dimension of the passed array. Only
works on arrays NOT including string items.

Usage:   aunique (inarray)
"""
    uniques = N.array([inarray[0]])
    if len(uniques.shape) == 1:            # IF IT'S A 1D ARRAY
        for item in inarray[1:]:
            if N.add.reduce(N.equal(uniques,item).ravel()) == 0:
                try:
                    uniques = N.concatenate([uniques,N.array[N.newaxis,:]])
                except TypeError:
                    uniques = N.concatenate([uniques,N.array([item])])
    else:                                  # IT MUST BE A 2+D ARRAY
        if inarray.dtype.char != 'O':  # not an Object array
            for item in inarray[1:]:
                if not N.sum(N.alltrue(N.equal(uniques,item),1)):
                    try:
                        uniques = N.concatenate( [uniques,item[N.newaxis,:]] )
                    except TypeError:    # the item to add isn't a list
                        uniques = N.concatenate([uniques,N.array([item])])
                else:
                    pass  # this item is already in the uniques array
        else:   # must be an Object array, alltrue/equal functions don't work
            for item in inarray[1:]:
                newflag = 1
                for unq in uniques:  # NOTE: cmp --> 0=same, -1=<, 1=>
                    test = N.sum(abs(N.array(map(cmp,item,unq))))
                    if test == 0:   # if item identical to any 1 row in uniques
                        newflag = 0 # then not a novel item to add
                        break
                if newflag == 1:
                    try:
                        uniques = N.concatenate( [uniques,item[N.newaxis,:]] )
                    except TypeError:    # the item to add isn't a list
                        uniques = N.concatenate([uniques,N.array([item])])
    return uniques


 def aduplicates(inarray):
    """
Returns duplicate items in the FIRST dimension of the passed array. Only
works on arrays NOT including string items.

Usage:   aunique (inarray)
"""
    inarray = N.array(inarray)
    if len(inarray.shape) == 1:            # IF IT'S A 1D ARRAY
        dups = []
        inarray = inarray.tolist()
        for i in range(len(inarray)):
            if inarray[i] in inarray[i+1:]:
                dups.append(inarray[i])
        dups = aunique(dups)
    else:                                  # IT MUST BE A 2+D ARRAY
        dups = []
        aslist = inarray.tolist()
        for i in range(len(aslist)):
            if aslist[i] in aslist[i+1:]:
                dups.append(aslist[i])
        dups = unique(dups)
        dups = N.array(dups)
    return dups

except ImportError:    # IF NUMERIC ISN'T AVAILABLE, SKIP ALL arrayfuncs
 pass
