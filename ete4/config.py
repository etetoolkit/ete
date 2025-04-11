"""
Constants with the XDG-compliant directories for ete.
"""

# See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

import os
from os.path import dirname, exists
import requests


# Helper function to define global ETE_* variables.
def ete_path(xdg_var, default):
    return os.environ.get(xdg_var, os.environ['HOME'] + default) + '/ete'

ETE_DATA_HOME   = ete_path('XDG_DATA_HOME',   '/.local/share')
ETE_CONFIG_HOME = ete_path('XDG_CONFIG_HOME', '/.config')
ETE_CACHE_HOME  = ete_path('XDG_CACHE_HOME',  '/.cache')


def update_ete_data(path, url, overwrite=False):
    """Refresh the contents of path with the ones in the given in the url."""
    # Resolve relative paths to refer to ETE_DATA_HOME.
    if not path.startswith('/'):
        path = ETE_DATA_HOME + '/' + path

    # Keep existing file if we asked for it.
    if not overwrite and exists(path):
        return

    # Create the directory.
    if dirname(path) and not exists(dirname(path)):
        os.system('mkdir -p ' + dirname(path))

    # Resolve relative urls to refer to ete-data repository.
    if not url.startswith('https://'):
        url = 'https://github.com/etetoolkit/ete-data/raw/main/' + url

    # Update local file with the content from the url.
    with open(path, 'wb') as f:
        print(f'{url} -> {path}')
        f.write(requests.get(url).content)
    # NOTE: If we had wget, this is similar to:
    #   os.system(f'wget -c -nv -O {path} {url}')
    # only wget could be better since it resumes partially downloaded files.


# Example:
#
#   path = 'gtdb202dump.tar.gz'
#   url = ('https://github.com/etetoolkit/ete-data/raw/main'
#          '/gtdb_taxonomy/gtdb202/gtdb202dump.tar.gz')
#
#   update_ete_data(path, url)
