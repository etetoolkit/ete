# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://etetoolkit.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the GPL copyleft license (2008-2015).  
#
# If you make use of ETE in published work, please cite:
#
# Jaime Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon.
# ETE: a python Environment for Tree Exploration. Jaime BMC
# Bioinformatics 2010,:24doi:10.1186/1471-2105-11-24
#
# Note that extra references to the specific methods implemented in 
# the toolkit may be available in the documentation. 
# 
# More info at http://etetoolkit.org. Contact: huerta@embl.de
#
# 
# #END_LICENSE#############################################################


''' I use this module to check for newer versions of ETE '''

import urllib2 as url

try:
    from ete2 import __ETEID__
except ImportError: 
    __ETEID__ = "Unknown"

try:
    from ete2 import __VERSION__
except ImportError: 
    __VERSION__ = "Unknown"

def call():
    print "  == Calling home...",
    try:
        f = url.urlopen('http://etetoolkit.org/et_phone_home.php?VERSION=%s&ID=%s' 
                %(__VERSION__, __ETEID__))
    except:
        print "No answer :(" 
    else:
        print "Got answer!" 
        print f.read()
     
        module_name = __name__.split(".")[0]
        try:
            f = url.urlopen('http://etetoolkit.org/releases/ete2/%s.latest' 
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
                f = url.urlopen('http://etetoolkit.org/et_phone_home.php?VERSION=%s&ID=%s&MSG=%s' 
                                %(__VERSION__, __ETEID__, msg))
            except:
                print "Message could be delivered :("
            else:
                print f.read()

def new_version(module_name=None, current=None):
    if not module_name:
        module_name = __name__.split(".")[0]
    try:
        f = url.urlopen('http://etetoolkit.org/releases/ete2/%s.latest' 
                        %module_name)
    except:
        latest = None
    else:
        latest = int(f.read())
        
    news_url = 'http://etetoolkit.org/releases/ete2/%s.latest_news' %module_name
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

