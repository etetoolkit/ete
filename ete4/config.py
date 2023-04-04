"""
Constants with the XDG-compliant directories for ete.
"""

# See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

from os import environ, system
from os.path import dirname, exists


def ete_path(xdg_var, default):
    return environ.get(xdg_var, environ['HOME'] + default) + '/ete'

ETE_DATA_HOME = ete_path('XDG_DATA_HOME', '/.local/share')
ETE_CONFIG_HOME = ete_path('XDG_CONFIG_HOME', '/.config')
ETE_CACHE_HOME = ete_path('XDG_CACHE_HOME', '/.cache')


def update_ete_data(path, url):
    """Refresh the contents of path with the ones in the given in the url."""
    # Resolve relative paths to refer to ETE_DATA_HOME.
    if not path.startswith('/'):
        path = ETE_DATA_HOME + '/' + path

    if dirname(path) and not exists(dirname(path)):
        system('mkdir -p ' + dirname(path))  # create the directory

    system(f'wget -c -nv -O {path} {url}')  # update from the web
    # TODO: Some possible improvements:
    #   - Raise an exception if the update doesn't happen.
    #   - Do not require wget to be installed.


# Example:
#
#   path = 'gtdb202dump.tar.gz'
#   url = ('https://github.com/etetoolkit/ete-data/raw/main'
#          '/gtdb_taxonomy/gtdb202/gtdb202dump.tar.gz')
#
#   update_ete_data(path, url)
