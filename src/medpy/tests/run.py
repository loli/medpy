#!/usr/bin/python

"""Executes all unittests."""

# build-in modules
import unittest
from medpy.tests.metric import TestSurfaceClass, TestVolumeClass

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "0.1, 2011-12-05"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = "Unittest executer."

# code
def main():
    # load metric tests
    suite_metric = unittest.TestSuite()
    suite_metric.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSurfaceClass))
    suite_metric.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVolumeClass))
    
    # execute tests
    unittest.TextTestRunner(verbosity=2).run(suite_metric)

if __name__ == '__main__':
    main()