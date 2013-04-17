#!/usr/bin/python

"""Executes all unittests."""

# build-in modules
import unittest
from metric import *
from graphcut import *
from io import *
from itkvtk import *

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.1.5, 2011-12-05"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
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
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCut))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGenerate))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEnergyLabel))
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEnergyVoxel))
    
    # load io tests
    suite_io = unittest.TestSuite()
    suite_io.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIOFacilities))
    
    # laod itkvtk tests
    suite_itkvtk = unittest.TestSuite()
    suite_itkvtk.addTests(unittest.TestLoader().loadTestsFromTestCase(TestItkVtkGradient))
    
    # execute tests
    unittest.TextTestRunner(verbosity=2).run(suite_metric)
    unittest.TextTestRunner(verbosity=2).run(suite_graphcut)
    unittest.TextTestRunner(verbosity=2).run(suite_io)
    unittest.TextTestRunner(verbosity=2).run(suite_itkvtk)

if __name__ == '__main__':
    main()