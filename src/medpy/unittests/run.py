#!/usr/bin/python

"""Executes all unittests."""

# build-in modules
import unittest
from medpy.unittests.metric import TestSurfaceClass, TestVolumeClass
from medpy.unittests.graphcut import TestGenerateCut, TestGraph, TestParse, TestBkMfmc, TestEnergyLabel

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
    
    # load graphcut tests
    suite_graphcut = unittest.TestSuite()
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGraph))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenerateCut))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestParse))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEnergyLabel))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBkMfmc))
    
    # execute tests
    unittest.TextTestRunner(verbosity=2).run(suite_metric)
    unittest.TextTestRunner(verbosity=2).run(suite_graphcut)

if __name__ == '__main__':
    main()