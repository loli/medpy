"""
@package medpy.io
Image I/O functionalities.

Provides functionalities for loading, saving and manipulating images.

Modules:
    - load: Functionality for loading images.
    - save: Functionality for saving images.
    - imageheader: Image header object.
"""

# determines the modules that should be imported when "from metric import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from load import load
from save import save
from header import get_pixel_spacing