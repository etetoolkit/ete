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
    except:
        print "No answer :(" 
    else:
        print "Got answer!" 
        print f.read()
     
        module_name = __name__.split(".")[0]
        try:
            f = url.urlopen('http://ete.cgenomics.org/releases/ete2/%s.latest' 
                    %module_name)
        except:
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
            print "A newer version is available: rev%s" %latest
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
            except:
                print "Message could be delivered :("
            else:
                print f.read()

def new_version(module_name=None, current=None):
    if not module_name:
        module_name = __name__.split(".")[0]
    try:
        f = url.urlopen('http://ete.cgenomics.org/releases/ete2/%s.latest' 
                        %module_name)
    except:
        latest = None
    else:
        latest = int(f.read())
        
    news_url = 'http://ete.cgenomics.org/releases/ete2/%s.latest_news' %module_name
    msg = read_content(news_url)
        
    if not current:
        try:
            current = int(__VERSION__.split("rev")[1])
        except (IndexError, ValueError): 
            current = None


    return current, latest, msg

def read_content(address):
    try:
        f = url.urlopen(address)
    except:
        return None
    else:
        return f.read()

