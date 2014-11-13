#!/usr/bin/python

"""Check supported image formats."""

# build-in modules
import unittest
from . import io_

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2013-09-16"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Check supported image formats."

# code
def main():
    # load io tests
    suite_io = unittest.TestSuite()
    suite_io.addTests(unittest.TestLoader().loadTestsFromTestCase(io_.TestIOFacilities))
    suite_io.addTests(unittest.TestLoader().loadTestsFromTestCase(io_.TestMetadataConsistency))
    
    # execute tests
    unittest.TextTestRunner(verbosity=2).run(suite_io)

if __name__ == '__main__':
    main()