import re
import commands
import os
import sys
import readline
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--notest", dest="notest", action='store_true')
parser.add_option("--nodoc", dest="nodoc", action='store_true')
parser.add_option("--simulate", dest="simulate", action='store_true')
parser.add_option("--verbose", dest="verbose", action='store_true')
parser.add_option("--doconly", dest="verbose", action='store_true')

(options, args) = parser.parse_args()


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

        
SERVER="huerta@etetoolkit.embl.de"
SERVER_RELEASES_PATH = "/var/www/etetoolkit/static/releases/ete2"

TEMP_PATH = "/tmp"
CURRENT_VERSION = open('VERSION').readline().strip()
a, b, c, tag  = re.search("(\d+)\.(\d+)\.(\d+)(.+)?", CURRENT_VERSION).groups()
a, b, c = map(int, (a, b, c))
SERIES_VERSION = "%s.%s" %(a, b) 
print '===================================================='
print 'CURRENT VERSION:', a, b, c, tag
print '===================================================='
# test examples

# commit changes in VERSION
if tag:
    tag1, tag2 = re.search('(.+?)(\d+)', tag).groups()
    tag2 = int(tag2)
    NEW_VERSION = "%s.%s.%s%s%s" %(a, b, c, tag1, tag2+1)
else:
    NEW_VERSION = "%s.%s.%s%s" %(a, b, c+1)

if ask('Increase version to "%s" ?' %NEW_VERSION, ['y', 'n']) == 'n':
    NEW_VERSION = raw_input('new version string:').strip()

if ask('Write "%s" and commit changes?' %NEW_VERSION, ['y', 'n']) == 'y':
    open('VERSION', 'w').write(NEW_VERSION)
    _ex('git commit -a -m "new release %s " && git tag -f %s && git tag -f %s' %(NEW_VERSION, NEW_VERSION, SERIES_VERSION))
else:
    NEW_VERSION = CURRENT_VERSION
    

    
# build docs 
if not options.nodoc: 
    _ex('(cd doc/ && make html)')

# build source dist
_ex('rm testclone -rf && git clone . testclone/ && cd testclone/ && python setup.py sdist')

# test distribution
if not options.notest:
    _ex('cd testclone/dist/ && tar xf ete2-%s.tar.gz && cd ete2-%s/test/ && python test_all.py && python test_treeview.py' %(NEW_VERSION, NEW_VERSION))
    
sys.exit(0)


    

if options.doc:
    print "*** Creating reference guide"
    # Generates PDF doc
    _ex("cd %s/sdoc; make latex" % RELEASE_PATH)
    _ex("cd %s/sdoc/_build/latex/; make all-pdf" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/latex/*.pdf %s/doc/" %(RELEASE_PATH, RELEASE_PATH))

    # Generates HTML doc (it includes a link to the PDF doc, so it
    # must be executed after PDF commands)
    _ex("cd %s/sdoc; make html" % RELEASE_PATH)
    _ex("cp -a %s/sdoc/_build/html/ %s/doc/" %(RELEASE_PATH, RELEASE_PATH))

    copydoc= ask("Update ONLINE PYPI documentation?", ["y","n"])
    if copydoc=="y":
        # INSTALL THIS http://pypi.python.org/pypi/Sphinx-PyPI-upload/0.2.1
        print "Uploading"      
        _ex("cd %s; python setup.py upload_sphinx --upload-dir %s/doc/html/ --show-response" %\
                (RELEASE_PATH, RELEASE_PATH))
        

MODULE_RELEASE = "%s.%s" %(a, b)

REVISION = commands.getoutput("git log --pretty=format:'' | wc -l").strip()
NEW_VERSION = "%s.%s.%s" %(a, b, c+1)


VERSION_LOG = commands.getoutput("git log --pretty=format:'%s' | head -n1").strip()
RELEASE_NAME = MODULE_NAME+"-"+VERSION
RELEASE_PATH = os.path.join(RELEASES_BASE_PATH, RELEASE_NAME)
RELEASE_MODULE_PATH = os.path.join(RELEASE_PATH, MODULE_NAME)
DOC_PATH = os.path.join(RELEASE_PATH, "doc")

