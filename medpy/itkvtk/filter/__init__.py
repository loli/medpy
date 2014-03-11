"""
@package medpy.itkvtk.filter
Various image filters and manipulation functions that depend on ITK.

Modules:
    - gradient: Gradient filters
    - watershed: Watershed filters
    
@author Oskar Maier
"""

# determines the modules that should be imported when "from filter import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from gradient import gradient_magnitude
from watershed import watershed 