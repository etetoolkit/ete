#!/usr/bin/env python

import os
import sys
import commands

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--examples", dest="test_examples", \
                      action="store_true", \
                      help="Test tutorial examples before building package")

parser.add_option("-u", "--unitest", dest="unitest", \
                      action="store_true", \
                      help="Runs all unitests before building package")

parser.add_option("-d", "--doc", dest="doc", \
                      action="store_true", \
                      help="Process documentation files")

parser.add_option("-x", "--lyx", dest="lyx", \
                      action="store_true", \
                      help="Process lyx based tutorial")

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

def _ex(cmd, interrupt=True):
    if options.verbose or options.simulate:
        print "***", cmd
    if not options.simulate:
        s = os.system(cmd)
        if s != 0 and interrupt:
            sys.exit(s)
        else:
            return s
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
SERVER="jhuerta@cgenomics"
SERVER_RELEASES_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2"
SERVER_DOC_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2/doc"
SERVER_METAPKG_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2/metapkg"
METAPKG_JAIL_PATH = "/home/jhuerta/_Devel/ete_metapackage/etepkg_CheckBeforeRm"
METAPKG_PATH = "/home/jhuerta/_Devel/ete_metapackage"
RELEASES_BASE_PATH = "/tmp"
MODULE_NAME = "ete2a1"
VERSION = MODULE_NAME+"rev"+commands.getoutput("git log --pretty=format:'' | wc -l").strip()
RELEASE_NAME = MODULE_NAME+"-"+VERSION
RELEASE_PATH = os.path.join(RELEASES_BASE_PATH, RELEASE_NAME)
RELEASE_MODULE_PATH = os.path.join(RELEASE_PATH, MODULE_NAME)
DOC_PATH = os.path.join(RELEASE_PATH, "doc")

print "================================="
print
print "VERSION", VERSION
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


# Set VERSION in all modules
print "*** Setting VERSION in all python files"
_ex('find %s/ete_dev/ -name \'*.py\' |xargs sed \'1 i __VERSION__=\"%s\" \' -i' %\
              (RELEASE_PATH, RELEASE_NAME))

# Generating VERSION file
print "*** Generating VERSION file"
_ex('echo %s > %s/VERSION' %\
              (VERSION, RELEASE_PATH))


# Check LICENSE disclaimer and add it or modify it if necessary
print  "*** Setting LICENSE in all python files"
_ex('find %s -name \'*.py\' -exec  python ___put_disclaimer.py {} \;' %\
        (RELEASE_PATH))


# Correct imports. I use ete_dev for development, but ete2 is the
# correct name for stable releases. First I install the module using a
# different name just to test it
print "*** Fixing imports..."
_ex('find %s -name \'*.py\' -o -name \'*.rst\'| xargs perl -e "s/ete_dev/ete2_tester/g" -p -i' %\
        (RELEASE_PATH))

_ex('mv %s/ete_dev %s/ete2_tester' %(RELEASE_PATH, RELEASE_PATH))
_ex('cd %s; python setup.py build --build-lib=build/lib' %(RELEASE_PATH))

if options.unitest:
    print 'export PYTHONPATH="%s/build/lib/"; python %s/test/test_all.py' %\
            (RELEASE_PATH, RELEASE_PATH)
    _ex('export PYTHONPATH="%s/build/lib/"; python %s/test/test_all.py' %\
            (RELEASE_PATH, RELEASE_PATH))

if options.test_examples:
    # Check tutorial examples
    'find %s/examples/ -name "*.py" -exec python {} \;'

    for filename in os.listdir("%s/examples/*/" %RELEASE_PATH):
        error_examples = []
        if filename.endswith(".py"):
            print "Testing", filename
            s = _ex('export PYTHONPATH="%s/build/lib/"; python %s/doc/tutorial/examples/%s;' %\
                    (RELEASE_PATH, RELEASE_PATH, filename), interrupt=False)
            if s != 0:
                error_examples.append(filename)
    print len(error_examples), "examples caused problems", error_examples


# Re-establish module name
_ex('mv %s/ete2_tester %s' %(RELEASE_PATH, RELEASE_MODULE_PATH))
_ex('find %s -name \'*.py\' -o -name \'*.rst\'| xargs perl -e "s/ete2_tester/%s/g" -p -i' %\
              (RELEASE_PATH, MODULE_NAME) )
_ex('cd %s; python setup.py build' %(RELEASE_PATH))



print "Cleaning doc dir:"
_ex("mv %s/doc %s/sdoc" %(RELEASE_PATH, RELEASE_PATH))
_ex("mkdir %s/doc" %(RELEASE_PATH))

if options.doc:
    print "*** Creating reference guide"
    #_ex('export PYTHONPATH="%s/build/lib/"; epydoc %s -n %s --exclude PyQt4  --inheritance grouped --name ete2 -o %s/doc/ete_guide_html' %\
    #              (RELEASE_PATH, RELEASE_MODULE_PATH, RELEASE_NAME, RELEASE_PATH))
    #_ex('export PYTHONPATH="%s/build/lib/"; epydoc %s -n %s  --exclude PyQt4 --pdf --inheritance grouped --name ete2 -o %s/doc/latex_guide' %\
    #_ex('export PYTHONPATH="%s/build/lib/"; epydoc %s -n %s  --exclude PyQt4  --inheritance grouped --name ete2 -o %s/doc/latex_guide' %\
    #              (RELEASE_PATH, RELEASE_MODULE_PATH, RELEASE_NAME, RELEASE_PATH))
    # _ex("cp %s/doc/latex_guide/api.pdf %s/doc/%s.pdf " %\
    #              (RELEASE_PATH, RELEASE_PATH, RELEASE_NAME))
    _ex("cd %s/sdoc; make html" % RELEASE_PATH)
    _ex("cd %s/sdoc; make latex" % RELEASE_PATH)
    _ex("cd %s/sdoc/_build/latex/; make all-pdf" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/html/ %s/doc/" %(RELEASE_PATH, RELEASE_PATH))
    _ex("cp -a %s/sdoc/_build/latex/*.pdf %s/doc/" %(RELEASE_PATH, RELEASE_PATH))


    _ex('find %s/doc | xargs perl -e "s/%s/ete2/g" -p -i' %\
            (RELEASE_PATH, MODULE_NAME) )

    copydoc= ask("Update ONLINE documentation?", ["y","n"])
    if copydoc=="y":
        # INSTALL THIS http://pypi.python.org/pypi/Sphinx-PyPI-upload/0.2.1
        print "Uploading"
        #_ex("cd %s; python setup.py upload_sphinx --upload-dir %s/doc/html/ --show-response" %\
        #        (RELEASE_PATH, RELEASE_PATH))

        _ex("cd %s; rsync -arv doc/html/ jhuerta@cgenomics:/data/services/web/ete.cgenomics.org/doc/2.1/" %\
                (RELEASE_PATH))

        #_ex("rsync -r %s/doc/ete_guide_html/ %s/html/" %\
        #        (RELEASE_PATH, SERVER+":"+SERVER_DOC_PATH))


# Clean from internal files
_ex("rm %s/.git -r" %\
        (RELEASE_PATH))
_ex('rm %s/build/ -r' %(RELEASE_PATH))
_ex('rm %s/sdoc/ -r' %(RELEASE_PATH))
_ex('rm %s/___* -r' %(RELEASE_PATH))

print "Creating tar.gz"
_ex("cd %s; python ./setup.py sdist " %RELEASE_PATH) 

release= ask("Copy release to main server?", ["y","n"])
if release=="y":
    print "Creating and submitting distribution to PyPI"
    _ex("cd %s; python ./setup.py sdist upload --show-response " %RELEASE_PATH) 
    print "Copying release to ete server..."
    _ex("scp %s/dist/%s.tar.gz %s" %\
            (RELEASE_PATH, RELEASE_NAME, SERVER+":"+SERVER_RELEASES_PATH))
    print "Updating releases table..."
    _ex("ssh %s 'cd %s; sh update_downloads.sh'" %(SERVER, SERVER_RELEASES_PATH))


updatemeta= ask("Update metapkg?", ["y","n"])
if updatemeta=="y":
    print "Updating metapkg..."
    _ex("sudo cp -a %s/%s.tar.gz %s/root/" %\
            (RELEASES_BASE_PATH, RELEASE_NAME, METAPKG_JAIL_PATH))
    print "Updating ete in chroot"
    _ex("sudo chroot %s easy_install /root/%s.tar.gz" %\
            (METAPKG_JAIL_PATH, RELEASE_NAME))
    # cd is important to avoid the full path when uncompressing
    _ex("cd %s/..; sudo tar -zcf ete_metapkg.tar.gz ete_metapackage/" %\
            (METAPKG_PATH))
    print "Copying metapkg to main server"
    _ex("scp %s/../ete_metapkg.tar.gz %s" %\
            (METAPKG_PATH,  SERVER+":"+SERVER_METAPKG_PATH))
