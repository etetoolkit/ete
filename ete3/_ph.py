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
from __future__ import absolute_import
from __future__ import print_function

try:
    from urllib2 import urlopen, URLError
    from urllib2 import quote as urlquote
except ImportError:
    from urllib.request import urlopen, URLError
    from urllib.parse import quote as urquote

from six.moves import input

try:
    from . import __ETEID__
except ImportError:
    __ETEID__ = "Unknown"

try:
    from .version import __version__
except ImportError:
     __version__ = 'unknown'

def call():
    print("  == Calling home...", end=' ')
    try:
        f = urlopen('http://etetoolkit.org/static/et_phone_home.php?VERSION=%s&ID=%s'
                %(__version__, __ETEID__))
    except URLError:
        print("No answer :(")
    else:
        print("Got answer!")
        try:
            f = urlopen('http://pypi.python.org/pypi/ete3/')
        except URLError:
            latest = None
        else:
            latest = int(f.read())

        try:
            current = int(__version__.split("rev")[1])
        except (IndexError, ValueError):
            current = None

        if not latest:
            print("I could not find data about your version [%s]" %__version__)
            print("Are you ok?")
        elif not current:
            print("I could not determine your version [%s]" %__version__)
            print("Are you ok?")
            print("Latest stable ETE version is", latest)
        elif latest > current:
            print("You look a bit old.")
            print("A newer version is available: rev%s" %latest)
        else:
            print("I see you are in good shape.")
            print("No updates are available.")
        try:
            msg = input("\n  == Do you want to leave any message?\n(Press enter to finish)\n\n").strip()
        except KeyboardInterrupt:
            msg = None

        if msg:
            msg = urlquote(msg)
            try:
                f = urlopen('http://etetoolkit.org/static/et_phone_home.php?VERSION=%s&ID=%s&MSG=%s'
                                %(__version__, __ETEID__, msg))
            except URLError:
                print("Message could be delivered :(")
            else:
                print("Message delivered")

def new_version(module_name=None, current=None):
    if not module_name:
        module_name = __name__.split(".")[0]
    try:
        f = urlopen('http://etetoolkit.org/releases/ete3/%s.latest'
                        %module_name)
    except URLError:
        latest = None
    else:
        latest = int(f.read())

    news_url = 'http://etetoolkit.org/releases/ete3/%s.latest_news' %module_name
    msg = read_content(news_url)

    if not current:
        try:
            current = int(__version__.split("rev")[1])
        except (IndexError, ValueError):
            current = None

    return current, latest, msg

def read_content(address):
    try:
        f = urlopen(address)
    except URLError:
        return None
    else:
        return f.read()

