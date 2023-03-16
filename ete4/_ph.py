''' I use this module to check for newer versions of ETE '''

try:
    from urllib2 import urlopen, URLError
    from urllib2 import quote as urlquote
except ImportError:
    from urllib.request import urlopen, URLError
    from urllib.parse import quote as urquote

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
