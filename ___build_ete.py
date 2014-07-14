#!/usr/bin/env python

# requires: 
#  pdflatex tools
# python twitter module 
# sphinx

import os
import sys
import commands
import readline
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

parser.add_option("-D", "--doc-only", dest="doc_only", \
                      action="store_true", \
                      help="Process last modifications of the documentation files. No git commit necessary. Package is not uploaded to PyPI")

parser.add_option("-x", "--lyx", dest="lyx", \
                      action="store_true", \
                      help="Process lyx based tutorial")

parser.add_option("-v", "--verbose", dest="verbose", \
                      action="store_true", \
                      help="It shows the commands that are executed at every step.")

parser.add_option("-s", "--simulate", dest="simulate", \
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
        readline.set_startup_hook(lambda: readline.insert_text(default))
        try:
            v = raw_input("%s [%s] " % (string, ', '.join(valid_values))).strip()
            if v == '' and default>=0:
                v = valid_values[default]
            if not case_sensitive:
                v = v.lower()
        finally:
            readline.set_startup_hook()
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
SERVER="huerta@etetoolkit.embl.de"
SERVER_RELEASES_PATH = "/var/www/etetoolkit/static/releases/ete2/"
SERVER_DOC_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2/doc"
SERVER_METAPKG_PATH = "/home/services/web/ete.cgenomics.org/releases/ete2/metapkg"
METAPKG_JAIL_PATH = "/home/jhuerta/_Devel/ete_metapackage/etepkg_CheckBeforeRm"
METAPKG_PATH = "/home/jhuerta/_Devel/ete_metapackage"
RELEASES_BASE_PATH = "/tmp"
MODULE_NAME = "ete2"
MODULE_RELEASE = "2.2"
REVISION = commands.getoutput("git log --pretty=format:'' | wc -l").strip()
VERSION = MODULE_RELEASE+ "." + REVISION
VERSION_LOG = commands.getoutput("git log --pretty=format:'%s' | head -n1").strip()
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
        _ex("rm %s -rf" %RELEASE_PATH)
    else:
        print "Aborted."
        sys.exit(-1)

if options.doc_only:
    print "Creating a repository copy in ", RELEASE_PATH
    options.doc = True
    process_package = False
    _ex("mkdir %s; cp -a ./ %s" %(RELEASE_PATH, RELEASE_PATH))
else:
    process_package = True
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

# Generating INSTALL file
print "*** Generating INSTALL file"
_ex('cp %s/doc/install/index.rst %s/INSTALL' %\
              (RELEASE_PATH, RELEASE_PATH))

# Check LICENSE disclaimer and add it or modify it if necessary
print  "*** Setting LICENSE in all python files"
_ex('find %s/ete_dev/ -name \'*.py\' -exec  python ___put_disclaimer.py {} \;' %\
        (RELEASE_PATH))

# Correct imports. I use ete_dev for development, but ete2 is the
# correct name for stable releases. First I install the module using a
# different name just to test it
print "*** Fixing imports..."
_ex('find %s -name \'*.py\' -o -name \'*.rst\'| xargs perl -e "s/ete_dev/ete2_tester/g" -p -i' %\
        (RELEASE_PATH))
_ex('cp %s/scripts/ete_dev %s/scripts/ete2_tester' %\
              (RELEASE_PATH, RELEASE_PATH))
_ex('mv %s/ete_dev %s/ete2_tester' %(RELEASE_PATH, RELEASE_PATH))
_ex('cd %s; python setup.py build --build-lib=build/lib' %(RELEASE_PATH))

if options.unitest:
    print 'export PYTHONPATH="%s/build/lib/"; python %s/test/test_all.py' %\
            (RELEASE_PATH, RELEASE_PATH)
    _ex('export PYTHONPATH="%s/build/lib/"; python %s/test/test_all.py' %\
            (RELEASE_PATH, RELEASE_PATH))

if options.test_examples:
    # Check tutorial examples
    exfiles = commands.getoutput('find %s/examples/ -name "*.py"' %\
            RELEASE_PATH).split("\n")
    error_examples = []
    for filename in exfiles:
        print "Testing", filename
        path = os.path.split(filename)[0]
        cmd = 'cd %s; PYTHONPATH="%s/build/lib/" python %s' %\
            (path, RELEASE_PATH, filename)
        print cmd
        s = _ex(cmd, interrupt=False)
        if s != 0:
            error_examples.append(filename)
    print len(error_examples), "examples caused problems"
    print '\n'.join(map(str, error_examples))
    if ask("Continue?", ["y","n"]) == "n":
        exit(-1)


# Re-establish module name
_ex('mv %s/ete2_tester %s' %(RELEASE_PATH, RELEASE_MODULE_PATH))
_ex('rm %s/scripts/ete2_tester' % (RELEASE_PATH))
_ex('find %s -name \'*.py\' -o -name \'*.rst\' | xargs perl -e "s/ete2_tester/%s/g" -p -i' %\
              (RELEASE_PATH, MODULE_NAME) )
_ex('find %s/scripts/ -type f | xargs perl -e "s/ete_dev/%s/g" -p -i' %\
              (RELEASE_PATH, MODULE_NAME) )

_ex('mv %s/scripts/ete_dev %s/scripts/%s' %\
              (RELEASE_PATH, RELEASE_PATH,  MODULE_NAME) )
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

    # Generates PDF doc
    _ex("cd %s/sdoc; make latex" % RELEASE_PATH)
    _ex("cd %s/sdoc/_build/latex/; make all-pdf" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/latex/*.pdf %s/doc/" %(RELEASE_PATH, RELEASE_PATH))

    # Generates HTML doc (it includes a link to the PDF doc, so it
    # must be executed after PDF commands)
    _ex("cd %s/sdoc; make html" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/html/ %s/doc/" %(RELEASE_PATH, RELEASE_PATH))

    # Set the correct ete module name in all doc files
    _ex('find %s/doc | xargs perl -e "s/ete_dev/%s/g" -p -i' %\
            (RELEASE_PATH, MODULE_NAME) )

    copydoc= ask("Update ONLINE PYPI documentation?", ["y","n"])
    if copydoc=="y":
        # INSTALL THIS http://pypi.python.org/pypi/Sphinx-PyPI-upload/0.2.1
        print "Uploading"
        
        # Always upload DOC to the main page
        _ex(' cd %s; cp VERSION _VERSION;  perl -e "s/%s/ete2/g" -p -i VERSION;' %\
                (RELEASE_PATH, MODULE_NAME))
        
        _ex("cd %s; python setup.py upload_sphinx --upload-dir %s/doc/html/ --show-response" %\
                (RELEASE_PATH, RELEASE_PATH))
        
        # Restore real VERSION 
        _ex(' cd %s; mv _VERSION VERSION;' % (RELEASE_PATH) )

    copydoc= ask("Update CGENOMICS documentation?", ["y","n"])
    if copydoc=="y":
        _ex("cd %s; rsync -arv doc/html/ jhuerta@cgenomics:/data/services/web/ete.cgenomics.org/doc/%s/" %\
                (RELEASE_PATH, MODULE_RELEASE))

if process_package:
    # Clean from internal files
    _ex("rm %s/.git -rf" %\
            (RELEASE_PATH))
    _ex('rm %s/build/ -rf' %(RELEASE_PATH))
    _ex('rm %s/sdoc/ -rf' %(RELEASE_PATH))
    _ex('rm %s/___* -rf' %(RELEASE_PATH))
     
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
        _ex("ssh %s 'cd %s; echo %s > %s.latest; sh update_downloads.sh;'" %(SERVER, SERVER_RELEASES_PATH, REVISION, MODULE_NAME))


    if ask("Update examples package in server?", ["y","n"]) == "y":
        print "Creating examples package" 
        _ex("cd %s; tar -zcf examples-%s.tar.gz examples/" %\
                (RELEASE_PATH, MODULE_NAME) )

        print "Copying examples to ete server..."
        _ex("scp %s/examples-%s.tar.gz %s" %\
                (RELEASE_PATH, MODULE_NAME, SERVER+":"+SERVER_RELEASES_PATH))

     
    announce = ask("publish tweet?", ["y","n"])
    if announce == "y":
        msg = ask(default=VERSION_LOG)
        if ask("publish tweet?", ["y","n"]) == "y":
            _ex("twitter -eetetoolkit set %s" %msg) 
