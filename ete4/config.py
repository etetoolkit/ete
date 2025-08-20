"""
ETE Toolkit XDG-compliant directory constants configuration file.

This file defines the standard paths for ETE to store data, configuration, and cache on different operating systems.
It follows the XDG Base Directory specification to ensure compatibility across different systems.
"""

# See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
# The XDG Base Directory specification defines which standard directories applications should use 
# to store different types of data

import os
# Import dirname and exists functions from os.path module for path handling and file existence checking
from os.path import dirname, exists
# Import requests library for HTTP requests to download files
import requests


# Helper function: used to define global ETE_* variables
# Parameters:
#   xdg_var: XDG environment variable name (e.g., XDG_DATA_HOME)
#   default: Default path (relative to user home directory) when environment variable is not set
def ete_path(xdg_var, default):
    """
    Determine ETE-related directory paths according to XDG standard
    
    First check if the corresponding XDG environment variable is set, if so use its value,
    otherwise use the default path (user home directory + default subdirectory).
    Finally create a subdirectory named 'ete' under that path.
    """
    # Get user home directory and concatenate default path as prefix
    prefix = os.path.expanduser('~') + default
    # Use environment variable value if set, otherwise use default prefix, then add '/ete' subdirectory
    return os.environ.get(xdg_var, prefix) + '/ete'

# Define ETE data storage directory (for database and other data files)
ETE_DATA_HOME   = ete_path('XDG_DATA_HOME',   '/.local/share')
# Define ETE configuration file directory (for configuration files)
ETE_CONFIG_HOME = ete_path('XDG_CONFIG_HOME', '/.config')
# Define ETE cache directory (for temporary files and cache)
ETE_CACHE_HOME  = ete_path('XDG_CACHE_HOME',  '/.cache')


def update_ete_data(path, url, overwrite=False):
    """
    Download data from specified URL and update local file
    
    Parameters:
      path: Local file path (relative or absolute path)
      url: Data source URL (relative or absolute URL)
      overwrite: Whether to overwrite existing files, default is False (no overwrite)
    """
    # Handle relative paths: if path is not an absolute path (doesn't start with '/'), 
    # resolve it as a relative path under ETE_DATA_HOME
    if not path.startswith('/'):
        path = ETE_DATA_HOME + '/' + path

    # If file already exists and not forcing overwrite, return directly without updating
    if not overwrite and exists(path):
        return

    # Create directory: if path contains directory and directory doesn't exist, create the directory
    # dirname(path) gets the directory part of the path, exists(dirname(path)) checks if directory exists
    if dirname(path) and not exists(dirname(path)):
        # Use system command to create directory (mkdir -p can recursively create multi-level directories)
        os.system('mkdir -p ' + dirname(path))

    # Handle relative URL: if URL is not an absolute URL (doesn't start with 'https://'), 
    # resolve it as a relative URL to the ete-data repository
    if not url.startswith('https://'):
        url = 'https://github.com/etetoolkit/ete-data/raw/refs/heads/main/' + url

    # Download content from URL and write to local file
    with open(path, 'wb') as f:  # Open file in binary write mode
        print(f'{url} -> {path}')  # Print download information, showing which URL downloads to which path
        f.write(requests.get(url).content)  # Send HTTP GET request to get content and write to file
    # Note: If we had wget command, we could achieve similar functionality, and wget supports resume download 
    # which is more advantageous for large file downloads
    #   os.system(f'wget -c -nv -O {path} {url}')
    # The advantage of wget is that it can resume partially downloaded files


# Usage example:
#
#   # Define the file name to download
#   path = 'gtdb202dump.tar.gz'
#   # Define the complete URL of the file on GitHub
#   url = ('https://github.com/etetoolkit/ete-data/raw/refs/heads/main'
#          '/gtdb_taxonomy/gtdb202/gtdb202dump.tar.gz')
#
#   # Call function to update data
#   update_ete_data(path, url)