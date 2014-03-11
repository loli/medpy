"""
@package medpy.io
Image I/O functionalities.

Provides functionalities for loading, saving and manipulating images.

Modules:
    - load: Functionality for loading images.
    - save: Functionality for saving images.
    - header: Image header manipulation routines.
"""

# determines the modules that should be imported when "from metric import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from load import load
from save import save
from header import get_pixel_spacing, get_offset, set_pixel_spacing, set_offset, copy_meta_data