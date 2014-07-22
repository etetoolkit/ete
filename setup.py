"""
The ETE toolkit: A Python Environment for Tree Exploration
"""
# Scipy is no longer necessary.
#    ["scipy", "Scipy is only required for the clustering validation functions.", 0],
PYTHON_DEPENDENCIES = [
    ["numpy", "Numpy is required for the ArrayTable and ClusterTree classes.", 0],
    ["MySQLdb", "MySQLdb only is required by the PhylomeDB access API.", 0],
    ["PyQt4", "PyQt4 is required for tree visualization and image rendering.", 0],
    ["lxml", "lxml is required from Nexml and Phyloxml support.", 0]
]

TAGS = [
    "Development Status :: 6 - Mature",
    "Environment :: Console",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: Developers",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]

def install(setup): #pylint: disable=W0621
    from setuptools import find_packages
    import sys
    import os
    import hashlib
    import time, random
    import re

    # Generates a unique id for ete installation. If this is an upgrade,
    # use the previous id. ETEID is only used to get basic statistics
    # about number of users/installations. The id generated is just a
    # random unique text string. This installation script does not collect
    # any personal information about you or your system.
    try:
        # Avoids importing a previously generated id
        _wd = os.getcwd()
        try:
            sys.path.remove(_wd)
        except ValueError:
            _fix_path = False
            pass
        else:
            _fix_path = True

        # Is there a previous ETE installation? If so, use the same id
        from ete_dev import __ETEID__ as ETEID

        if _fix_path:
            sys.path.insert(0, _wd)

    except ImportError:
        ETEID = None
    if not ETEID:
        hash_str = str(time.time() + random.random()).encode('utf-8')
        ETEID = hashlib.md5(hash_str).hexdigest()

    print()
    print("Installing ETE (A python Environment for Tree Exploration).")
    print()

    print("Checking dependencies...")
    missing = False
    for mname, msg, ex in PYTHON_DEPENDENCIES:
        if not can_import(mname):

            print(("WARNING:\033[93m Optional library [%s] could not be found \033[0m" % mname))
            print(("  ", msg))
            missing=True

    #if missing:
    #    print("\nHowever, you can still install ETE without such functionality.")
    #    if ask( "Do you want to continue with the installation anyway?",
    #            ["y", "n"]) == "n":
    #        sys.exit()

    # writes installation id as a variable into the main module
    init_content = open("ete_dev/__init__.py").read()
    init_content = re.sub('__ETEID__="[\w\d]*"', '__ETEID__="%s"'
                        %ETEID, init_content)
    open("ete_dev/__init__.py", "w").write(init_content)

    print(("Your installation ID is: %s" % ETEID))

    ete_version = open("VERSION").readline().strip()
    revision = ete_version.split("rev")[-1]
    mod_name = "ete_dev"

    long_description = open("README").read()
    long_description += open("INSTALL").read()
    long_description.replace("ete_dev", mod_name)

    try:
        _s = setup(
            name = "ete_dev",
            version = ete_version,
            packages = find_packages(),
            scripts = ['bin/ete'],
            requires = [],

            # Project uses reStructuredText, so ensure that the docutils get
            # installed or upgraded on the target machine
            install_requires = [
                ],
            package_data = {
                },
            # metadata for upload to PyPI
            author = "Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon",
            author_email = "jhcepas@gmail.com",
            maintainer = "Jaime Huerta-Cepas",
            maintainer_email = "jhcepas@gmail.com",
            platforms = "OS Independent",
            license = "GPLv3",
            description = "A python Environment for phylogenetic Tree Exploration",
            long_description = long_description,
            classifiers = TAGS,
            provides = ["ete_dev"],
            keywords = "bioinformatics phylogeny evolution phylogenomics genomics"
            " tree clustering phylogenetics phylogenetic ete orthology"
            " paralogy",
            url = "http://etetoolkit.org",
            use_2to3=True,
            download_url = "http://etetoolkit.org/static/releases/ete2/",
        )
    except:
        raise
    else:
        notwanted = set(["-h", "--help", "-n", "--dry-run"])
        seen = set(_s.script_args)
        wanted = set(["install", "bdist", "bdist_egg"])
        if (wanted & seen) and not (notwanted & seen):
            phone_home(ETEID, ete_version)

def phone_home(ETEID, ete_version):
    "Reports new ete user"""
    # Python2
    url = "http://etetoolkit.org/static/et_phone_home.php?ID=%s&VERSION=%s&MSG=%s"
    welcome = 'New%20alien%20in%20earth%21'

    try:
        import urllib2
        try:
            urllib2.urlopen(url % (ETEID, ete_version, welcome))
        except urllib2.HTTPError as e:
            pass
    except ImportError:
        # Python 3
        import urllib.request, urllib.error
        try:
            urllib.request.urlopen(url % (ETEID, ete_version, welcome))
        except urllib.error.HTTPError as e:
            pass

def can_import(mname):
    'Test if a module can be imported '
    if mname=="PyQt4":
        try:
            __import__("PyQt4.QtCore")
            __import__("PyQt4.QtGui")
        except ImportError:
            try:
                __import__("QtCore")
                __import__("QtGui")
            except ImportError:
                return False
        else:
            return True
    elif mname == "MySQLdb":
        try:
            import MySQLdb
        except ImportError:
            return False
        else:
            return True
    else:
        try:
            __import__(mname)
        except ImportError:
            return None
        else:
            return True

def ask(string, valid_values, default=-1, case_sensitive=False):
    """ Asks for a keyboard answer """
    # Python 2/3
    try:
        get_input = raw_input
    except NameError:
        get_input = input

    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        v = get_input("%s [%s]" % (string,','.join(valid_values)))
        if v == '' and default >= 0:
            v = valid_values[default]
        if not case_sensitive:
            v = v.lower()
    return v

if __name__ == '__main__':
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
    install(setup)

