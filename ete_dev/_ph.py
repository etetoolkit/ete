 #START_LICENSE###########################################################
#
#
#
# #END_LICENSE#############################################################

''' I use this module to check for newer versions of ETE '''

import urllib2 as url

try:
    from ete_dev import __ETEID__
except ImportError: 
    __ETEID__ = "Unknown"

try:
    from ete_dev import __VERSION__
except ImportError: 
    __VERSION__ = "Unknown"

def call():
    print "  == Calling home...",
    try:
        f = url.urlopen('http://ete.cgenomics.org/et_phone_home.php?VERSION=%s&ID=%s' 
                %(__VERSION__, __ETEID__))
    except url.HTTPError:
        print "No answer :(" 
    else:
        print "Got answer!" 
        print f.read()
     
        module_name = __name__.split(".")[0]
        try:
            f = url.urlopen('http://ete.cgenomics.org/releases/ete2/%s.latest' 
                    %module_name)
        except url.HTTPError:
            latest = None
        else:
            latest = int(f.read())
     
        try:
            current = int(__VERSION__.split("rev")[1])
        except (IndexError, ValueError): 
            current = None
     
        if not latest:
            print "I could not find data about your version [%s]" %module_name
            print "Are you ok?"
        elif not current:
            print "I could not determine your version [%s]" %module_name
            print "Are you ok?"
            print "Latest stable ETE version is", latest
        elif latest > current:
            print "You look a bit old."
            print "A newer version is available: rev%" %latest
            print "Use 'easy_install -U %s' to upgrade" %module_name
        else:
            print "I see you are in shape."
            print "No updates are available." 
        try:
            msg = raw_input("\n  == Do you want to leave any message?\n(Press enter to finish)\n\n").strip()
        except KeyboardInterrupt: 
            msg = None

        if msg:
            msg = url.quote(msg)
            try:
                f = url.urlopen('http://ete.cgenomics.org/et_phone_home.php?VERSION=%s&ID=%s&MSG=%s' 
                                %(__VERSION__, __ETEID__, msg))
            except url.HTTPError:
                print "Message could be delivered :("
            else:
                print f.read()


