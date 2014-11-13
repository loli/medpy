#!/usr/bin/python

"""Executes all unittests."""

# build-in modules
import unittest
from . import metric_, graphcut_, itkvtk_, features_, filter_

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
    suite_metric.addTests(unittest.TestLoader().loadTestsFromTestCase(metric_.TestSurfaceClass))
    suite_metric.addTests(unittest.TestLoader().loadTestsFromTestCase(metric_.TestVolumeClass))
    
    # load graphcut tests
    suite_graphcut = unittest.TestSuite()
    suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(graphcut_.TestGraph))
    # !TODO: Fix tests for graphcut functionality
    #suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(graphcut.TestCut))
    #suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(graphcut.TestGenerate))
    #suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(graphcut.TestEnergyLabel))
    #suite_graphcut.addTests(unittest.TestLoader().loadTestsFromTestCase(graphcut.TestEnergyVoxel))
    
    # load itkvtk tests
    suite_itkvtk = unittest.TestSuite()
    suite_itkvtk.addTests(unittest.TestLoader().loadTestsFromTestCase(itkvtk_.TestItkVtkGradient))
    
    # load filter tests
    suite_filter = unittest.TestSuite()
    # !TODO: Fix tests for LabelImageStatistic functionality
    #suite_filter.addTests(unittest.TestLoader().loadTestsFromTestCase(filter_.TestLabelImageStatistics))
    suite_filter.addTests(unittest.TestLoader().loadTestsFromTestCase(filter_.TestIntensityRangeStandardization))
    suite_filter.addTests(unittest.TestLoader().loadTestsFromTestCase(filter_.TestHoughTransform))
    
    # load feature tests
    suite_features = unittest.TestSuite()
    suite_features.addTests(unittest.TestLoader().loadTestsFromTestCase(features_.TestHistogramFeatures))
    suite_features.addTests(unittest.TestLoader().loadTestsFromTestCase(features_.TestIntensityFeatures))
    suite_features.addTests(unittest.TestLoader().loadTestsFromTestCase(features_.TestTextureFeatures))
    
    # execute tests
    unittest.TextTestRunner(verbosity=2).run(suite_metric)
    unittest.TextTestRunner(verbosity=2).run(suite_graphcut)
    unittest.TextTestRunner(verbosity=2).run(suite_itkvtk)
    unittest.TextTestRunner(verbosity=2).run(suite_filter)
    unittest.TextTestRunner(verbosity=2).run(suite_features)

if __name__ == '__main__':
    main()