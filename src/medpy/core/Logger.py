#!/usr/bin/python

"""A singleton log class to be used by all applications, classes and functions of MedPy."""

# build-in modules
import logging
from logging import Logger as NativeLogger
import sys

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  A singleton debug class to be used by all applications, classes and 
                  functions of MedPy for raising messages, be it info, debug, exception
                  or critical.
                  """

# code
class Logger (NativeLogger):
    """
    This singleton class represents an object that can be used by all applications and
    classes.
    """
    
    class LoggerHelper (object):
        """
        A helper class which performs the actual initialization.
        """
        def __call__(self, *args, **kw) :
            # If an instance of TestSingleton does not exist,
            # create one and assign it to TestSingleton.instance.
            if Logger._instance is None :
                Logger._instance = Logger()
            # Return TestSingleton.instance, which should contain
            # a reference to the only instance of TestSingleton
            # in the system.
            return Logger._instance
    
    """Member variable initiating and returning the instance of the class."""    
    getInstance = LoggerHelper() 
    """The member variable holding the actual instance of the class."""
    _instance = None
    """Holds the loggers handler for format changes."""
    _handler = None

    def __init__(self, name = 'MedPyLogger', level = 0) :
        # To guarantee that no one created more than one instance of Logger:
        if not Logger._instance == None :
            raise RuntimeError, 'Only one instance of Logger is allowed!'
        
        # initialize parent
        NativeLogger.__init__(self, name, level)
        
        # set attributes
        self.setHandler(logging.StreamHandler(sys.stdout)) 
        self.setLevel(logging.WARNING)
        
    def setHandler(self, hdlr):
        """
        Replaces the current handler with a new one.
        If none should be replaces, but just one added, use the parent classes
        addHandler() method.
        """
        if None != self._handler:
            self.removeHandler(self._handler)
        self._handler = hdlr
        self.addHandler(self._handler)
        
    def setLevel(self, level):
        """
        Overrides the parent method to adapt the formatting string to the level.
        """
        if logging.DEBUG == level:
            formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s (in %(module)s.%(funcName)s:%(lineno)s)", 
                                          "%d.%m.%Y %H:%M:%S") 
            self._handler.setFormatter(formatter)
        else:
            formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(message)s", 
                                          "%d.%m.%Y %H:%M:%S") 
            self._handler.setFormatter(formatter)
            
        NativeLogger.setLevel(self, level)
            
