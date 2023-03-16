#!/usr/bin/python3

"""
Init of evol plugin
"""

__author__  = "Francois-Jose Serra"
__email__   = "francois@barrabin.org"
__licence__ = "GPLv3"
__version__ = "0.0"


from .parser.codemlparser import *
from .evoltree            import *
from .model               import Model
__all__ = evoltree.__all__
