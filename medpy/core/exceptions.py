#!/usr/bin/python

"""MedPy exceptions."""

# build-in modules

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "0.2, 2011-12-11"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  All MedPy exceptions.
                  """

# code
class ArgumentError(Exception):
    """
    Thrown by an application when an invalid command line argument has been supplied.
    """
    pass
    
class FunctionError(Exception):
    """
    Thrown when a supplied function returns unexpected results.
    """
    pass
    
class SubprocessError(Exception):
    """
    Thrown by an application when a subprocess execution failed.
    """
    pass

class ImageTypeError(Exception):
    """
    Thrown when trying to load or save an image of unknown type.
    """
    pass

class DependencyError(Exception):
    """
    Thrown when a required module could not be loaded.
    """
    pass

class ImageLoadingError(Exception):
    """
    Thrown when a image could not be loaded.
    """
    pass

class ImageSavingError(Exception):
    """
    Thrown when a image could not be loaded.
    """
    pass

class MetaDataError(Exception):
    """
    Thrown when an image meta data failure occurred.
    """
    pass