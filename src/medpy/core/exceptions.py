#!/usr/bin/python

"""MedPy exceptions."""

# build-in modules

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "0.1, 2011-12-11"
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
    #def __init__(self, message, exception = None):
    #    Exception.__init__(message, exception)
    
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

        