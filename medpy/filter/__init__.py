"""
@package medpy.filter
Various image filters and manipulation functions.

Modules:
    - label: Filter for label images.
    
@author Oskar Maier
"""

# determines the modules that should be imported when "from filter import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from label import relabel, fit_labels_to_mask, relabel_map, relabel_non_zero