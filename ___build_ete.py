#!/usr/bin/env python 

import os
import sys
import commands

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-c", "--chroot", dest="chroot", \
		      action="store", type="string", default='',\
		      help="Path to a pre-existent installation of the ete metapackage. Do not create the chroot environment from scratch. It uses the provided path. Useful to just update config or add new users.")

parser.add_option("-v", "--verbose", dest="verbose", \
		      action="store_true", \
		      help="It shows the commands that are executed at every step.")

parser.add_option("-q", "--quite", dest="simulate", \
		      action="store_true", \
		      help="Do not actually do anything. ")


(options, args) = parser.parse_args()

print options

def print_in_columns(header, *values):
    ncols = len(values)
    nrows = max([len(l) for l in values])
    if nrows < 1:
	return 
    c2longest = {}
    # Does not work in python2.4
    # get = lambda i,x: '' if i>len(x)-1 else x[i]
    def get(i, x):
	if i>(len(x)-1):
	    return ''
	else:
	    return x[i]

    for c in xrange(ncols):
	c2longest[c] = max([len(str(get(r, list(values[c])))) for r in xrange(nrows)])
	c2longest[c] = max(c2longest[c], len(str(get(c, header))))

    if header is not None: 
	print '\t'.join([str(get(c,header)).ljust(c2longest[c]) for c in xrange(ncols)])
   	print '\t'.join(['='*c2longest[c] for c in xrange(ncols)])


    for i in xrange(nrows):
	print '\t'.join([str(get(i,list(l))).ljust(c2longest[c]) for c,l in enumerate(values)])

def _ex(cmd):
    if options.verbose or options.simulate: 
	print "***", cmd
    if not options.simulate:
	return  os.system(cmd)
    else:
	return 0

def ask(string, valid_values, default=-1, case_sensitive=False):
    """ Asks for a keyborad answer """
    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
	v = raw_input("%s [%s] " % (string, ', '.join(valid_values))).strip()
	if v == '' and default>=0:
            v = valid_values[default]
	if not case_sensitive:
            v = v.lower()
    return v

def ask_path(string, default_path):
    v = None
    while v is None:
	v = raw_input("%s [%s] " % (string, default_path)).strip()
	if v == '':
            v = default_path
	if not os.path.exists(v):
	    print >>sys.stderr, v, "does not exist."
	    v = None
    return v



#Check repo is commited

#Creates a release clone
RELEASES_BASE_PATH = "/tmp"
BRANCH_NAME = "2.0"
RELEASE_NAME = BRANCH_NAME+"rev"+commands.getoutput("git log --pretty=format:'' | wc -l").strip()
MODULE_NAME = "ete2"
RELEASE_PATH = os.path.join(RELEASES_BASE_PATH, RELEASE_NAME)
RELEASE_MODULE_PATH = os.path.join(RELEASE_PATH, "ete2")
DOC_PATH = os.path.join(RELEASE_PATH, "doc")

print "================================="
print
print "RELEASE:", RELEASE_NAME
print "RELEASE_PATH:", RELEASE_PATH
print
print "================================="



if os.path.exists(RELEASE_PATH):
    print RELEASE_PATH, "exists"
    overwrite = ask("Overwrite?",["y","n"])
    if overwrite=="y":
	_ex("rm %s -r" %RELEASE_PATH)
    else:
	print "Aborted."
	sys.exit(-1)

print "Creating a repository clone in ", RELEASE_PATH
_ex("git clone . %s" %RELEASE_PATH)

# Correct imports. I use ete_dev for development, but ete2 is the
# correct name for stable releases
print "*** Fixing imports..."
_ex('find %s -name \'*.py\'| xargs perl -e "s/from ete_dev/from %s/g" -p -i' %\
	      (RELEASE_PATH, MODULE_NAME) )


# Set VERSION in all modules
print "*** Setting VERSION in all python files"
_ex('find %s -name \'*.py\' |xargs sed "1 i __VERSION__=\"%s\""  -i' %\
	      (RELEASE_MODULE_PATH, RELEASE_NAME))

# Check LICENSE disclamer and add it or modify it if necessary 
print  "*** Setting LICENSE in all python files"
_ex('find %s -name \'*.py\' -exec  python ___put_disclamer.py {} \;' %\
	(RELEASE_MODULE_PATH))

sys.exit()
# Unitests ---> Search for problems
print "*** Running unittest..."
# python $OUTPATH/unittest/test_all.py

# Generate reference guide 
print "*** Creating reference guide"
_ex("epydoc %s -n %s  --inheritance grouped --name ete2 -o %s/reference_guide/" %\
	      (RELEASE_NAME, DOC_PATH))


