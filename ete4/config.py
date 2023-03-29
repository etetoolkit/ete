"""
Constants with the XDG-compliant directories for ete.
"""

# See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

from os import environ

def ete_path(xdg_var, default):
    return environ.get(xdg_var, environ['HOME'] + default) + '/ete'

ETE_DATA_HOME = ete_path('XDG_DATA_HOME', '/.local/share')
ETE_CONFIG_HOME = ete_path('XDG_CONFIG_HOME', '/.config')
ETE_CACHE_HOME = ete_path('XDG_CACHE_HOME', '/.cache')
