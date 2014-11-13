"""
Unittest for the medpy.graphcut.energy methods.

@author Oskar Maier
@version r0.2.1
@since 2011-01-30
@status Release
"""

# build-in modules
import sys
import unittest

# third-party modules
import scipy

# own modules
from medpy.graphcut.energy_label import boundary_stawiaski, boundary_difference_of_means

# code
class TestEnergyLabel(unittest.TestCase):
    
    def test_boundary_stawiaski_borders(self):
        """Test the @link medpy.graphcut.test_boundary_stawiaski() border conditions.""" 
        # TEST1: test for a label image with not continuous label ids not starting from 0
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        expected_result = {(1, 3): (2.0, 2.0), (1, 4): (1.0, 1.0), (4, 8): (1.0, 1.0), (3, 4): (1.0, 1.0), (3, 10): (2.0, 2.0), (8, 10): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros_like(label)))
        self.__compare_dictionaries(result, expected_result, 'Test1')
        # TEST2: test for a label image with negative labels
        label = [[-1, 4, 8],
                 [-1, 3, 10],
                 [1, -3, 10]]
        expected_result = {(-1, 1): (1.0, 1.0), (4, 8): (1.0, 1.0), (-1, 3): (1.0, 1.0), (3, 10): (1.0, 1.0), (-3, 10): (1.0, 1.0), (8, 10): (1.0, 1.0), (-3, 1): (1.0, 1.0), (-3, 3): (1.0, 1.0), (-1, 4): (1.0, 1.0), (3, 4): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros_like(label)))
        self.__compare_dictionaries(result, expected_result, 'Test2')
        # TEST3: test for behavior on occurrence of very small (~0) and 1 weights
        gradient = [[0., 0., 0.],
                    [0., 0., sys.float_info.max]]
        label = [[0, 1, 2],
                 [0, 1, 3]]
        expected_result = {(0, 1): (2.0, 2.0), (1, 2): (1.0, 1.0), (1, 3): (sys.float_info.min, sys.float_info.min), (2, 3): (sys.float_info.min, sys.float_info.min)}
        result = boundary_stawiaski(label, (gradient))
        self.__compare_dictionaries(result, expected_result, 'Test3')
        # TEST4: check behavior for integer gradient image
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        label = scipy.asarray(label)
        expected_result = {(1, 3): (2.0, 2.0), (1, 4): (1.0, 1.0), (4, 8): (1.0, 1.0), (3, 4): (1.0, 1.0), (3, 10): (2.0, 2.0), (8, 10): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros(label.shape, scipy.int_)))
        self.__compare_dictionaries(result, expected_result, 'Test4')
        # TEST5: reaction to different array orders
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        label = scipy.asarray(label, order='C') # C-order, gradient same order
        expected_result = {(1, 3): (2.0, 2.0), (1, 4): (1.0, 1.0), (4, 8): (1.0, 1.0), (3, 4): (1.0, 1.0), (3, 10): (2.0, 2.0), (8, 10): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros_like(label)))
        self.__compare_dictionaries(result, expected_result, 'Test5 (C,C)')
        label = scipy.asarray(label, order='F') # Fortran order, gradient same order
        expected_result = {(1, 3): (2.0, 2.0), (1, 4): (1.0, 1.0), (4, 8): (1.0, 1.0), (3, 4): (1.0, 1.0), (3, 10): (2.0, 2.0), (8, 10): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros_like(label)))
        self.__compare_dictionaries(result, expected_result, 'Test5 (F, F)')
        label = scipy.asarray(label, order='C') # C-order, gradient different order
        expected_result = {(1, 3): (2.0, 2.0), (1, 4): (1.0, 1.0), (4, 8): (1.0, 1.0), (3, 4): (1.0, 1.0), (3, 10): (2.0, 2.0), (8, 10): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros(label.shape, order='F')))
        self.__compare_dictionaries(result, expected_result, 'Test5 (C, F)')
        label = scipy.asarray(label, order='F') # F-order, gradient different order
        expected_result = {(1, 3): (2.0, 2.0), (1, 4): (1.0, 1.0), (4, 8): (1.0, 1.0), (3, 4): (1.0, 1.0), (3, 10): (2.0, 2.0), (8, 10): (1.0, 1.0)}
        result = boundary_stawiaski(label, (scipy.zeros(label.shape, order='C')))
        self.__compare_dictionaries(result, expected_result, 'Test5 (F, C)')
        
    def test_boundary_stawiaski_2d(self):
        """Test the @link medpy.graphcut.test_boundary_stawiaski() function for 2D."""
        # the gradient magnitude image
        gradient = [[0., 0., 0., 0.1, 0.1, 0.5],
                    [0., 0., 0., 0.1, 0.1, 0.1],
                    [0., 0.3, 0.3, 0.2, 0.2, 0.2],
                    [0., 0., 0.3, 0.3, 0.3, 0.2],
                    [0., 0., 0.3, 0.2, 0.2, 0.4]]
        # the label image (labels have to start from 0)
        label = [[0, 0, 0, 1, 1, 5],
                 [0, 0, 0, 1, 1, 1],
                 [0, 3, 3, 2, 2, 2],
                 [0, 0, 3, 3, 3, 2],
                 [0, 0, 3, 2, 2, 4]]
        # the expected result
        expected_result = {(0,1): 1.652892562,
                           (0,3): 3.550295856,
                           (1,2): 2.083333333,
                           (1,5): 0.888888889,
                           (2,3): 4.142011834,
                           (2,4): 1.020408163}
        expected_result = self.__to_two_directed(expected_result)
        # run the function
        result = boundary_stawiaski(label, (gradient))
        # check returned values
        self.__compare_dictionaries(result, expected_result)
        
    def test_boundary_stawiaski_3d(self):
        """Test the @link medpy.graphcut.test_boundary_stawiaski() function for 3D."""
        # the gradient magnitude image
        gradient = [[[0., 0., 0., 0.1, 0.1, 0.5],
                     [0., 0., 0., 0.1, 0.1, 0.1],
                     [0., 0.3, 0.3, 0.2, 0.2, 0.2],
                     [0., 0., 0.3, 0.3, 0.3, 0.2],
                     [0., 0., 0.3, 0.2, 0.2, 0.4]],
                    [[0., 0., 0., 0.1, 0.1, 0.6],
                     [0., 0., 0., 0.1, 0.1, 0.1],
                     [0., 0.3, 0.3, 0.2, 0.2, 0.2],
                     [0., 0., 0.3, 0.3, 0.3, 0.2],
                     [0., 0., 0.3, 0.2, 0.2, 0.4]]]
        # the label image (labels have to start from 0)
        label = [[[0, 0, 0, 1, 1, 5],
                  [0, 0, 0, 1, 1, 1],
                  [0, 3, 3, 2, 2, 2],
                  [0, 0, 3, 3, 3, 2],
                  [0, 0, 3, 2, 2, 4]],
                 [[0, 0, 0, 1, 1, 6],
                  [0, 0, 0, 1, 1, 1],
                  [0, 3, 3, 2, 2, 2],
                  [0, 0, 3, 3, 3, 2],
                  [0, 0, 3, 2, 2, 4]]]
        # the expected result
        expected_result = {(0,1): 3.305785124,
                           (0,3): 7.100591712,
                           (1,2): 4.166666666,
                           (1,5): 0.888888889,
                           (1,6): 0.78125,
                           (2,3): 8.284023668,
                           (2,4): 2.040816326,
                           (5,6): 0.390625} # only 3D edge
        expected_result = self.__to_two_directed(expected_result)
        # run the function
        result = boundary_stawiaski(label, (gradient))
        # check returned values
        self.__compare_dictionaries(result, expected_result)
        
        
        
        
    def test_boundary_difference_of_means_borders(self):
        """Test the @link medpy.graphcut.boundary_difference_of_means() border conditions.""" 
        # TEST1: test for a label image with not continuous label ids not starting from 0
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        expected_result = {(1, 3): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min), (1, 4): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test1')
        # TEST2: test for a label image with negative labels
        label = [[-1, 4, 8],
                 [-1, 3, 10],
                 [1, -3, 10]]
        expected_result = {(-1, 1): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (-1, 3): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (-3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min), (-3, 1): (sys.float_info.min, sys.float_info.min), (-3, 3): (sys.float_info.min, sys.float_info.min), (-1, 4): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test2')
        # TEST3: test for behavior on occurrence of very small (~0) and 1 weights
        gradient = [[0., 0., 0.],
                    [0., 0., sys.float_info.max]]
        label = [[0, 1, 2],
                 [0, 1, 3]]
        expected_result = {(0, 1): (1.0, 1.0), (1, 2): (1.0, 1.0), (1, 3): (sys.float_info.min, sys.float_info.min), (2, 3): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (gradient))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test3')
        # TEST4: check behavior for integer gradient image
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        label = scipy.asarray(label)
        expected_result = {(1, 3): (sys.float_info.min, sys.float_info.min), (1, 4): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros(label.shape, scipy.int_)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test4')
        # TEST5: reaction to different array orders
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        label = scipy.asarray(label, order='C') # C-order, gradient same order
        expected_result = {(1, 3): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min), (1, 4): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (C,C)')
        label = scipy.asarray(label, order='F') # Fortran order, gradient same order
        expected_result = {(1, 3): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min), (1, 4): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (F, F)')
        label = scipy.asarray(label, order='C') # C-order, gradient different order
        expected_result = {(1, 3): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min), (1, 4): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros(label.shape, order='F')))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (C, F)')
        label = scipy.asarray(label, order='F') # F-order, gradient different order
        expected_result = {(1, 3): (sys.float_info.min, sys.float_info.min), (4, 8): (sys.float_info.min, sys.float_info.min), (3, 10): (sys.float_info.min, sys.float_info.min), (8, 10): (sys.float_info.min, sys.float_info.min), (1, 4): (sys.float_info.min, sys.float_info.min), (3, 4): (sys.float_info.min, sys.float_info.min)}
        result = boundary_difference_of_means(label, (scipy.zeros(label.shape, order='C')))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (F, C)')  
        
    def test_boundary_difference_of_means_2d(self):
        """Test the @link medpy.graphcut.boundary_difference_of_means() function for 2D."""
        # the original image
        original = [[0., 0., 0., 0.1, 0.1, 0.5],
                    [0., 0., 0., 0.1, 0.1, 0.1],
                    [0., 0.3, 0.3, 0.2, 0.2, 0.2],
                    [0., 0., 0.3, 0.3, 0.3, 0.2],
                    [0., 0., 0.3, 0.2, 0.2, 0.4]]
        # the label image (labels have to start from 0)
        label = [[0, 0, 0, 1, 1, 5],
                 [0, 0, 0, 1, 1, 1],
                 [0, 3, 3, 2, 2, 2],
                 [0, 0, 3, 3, 3, 2],
                 [0, 0, 3, 2, 2, 4]]
        # the expected result
        expected_result = {(0,1): 0.8,
                           (0,3): 0.4,
                           (1,2): 0.8,
                           (1,5): 0.2,
                           (2,3): 0.8,
                           (2,4): 0.6}
        expected_result = self.__to_two_directed(expected_result)
        # run the function
        result = boundary_difference_of_means(label, (original))
        result = self._reorder_keys(result)
        # check returned values
        self.__compare_dictionaries(result, expected_result)
        
    def test_boundary_difference_of_means_3d(self):
        """Test the @link medpy.graphcut.boundary_difference_of_means() function for 3D."""
        # 3D VERSION
        # the gradient magnitude image
        original = [[[0., 0., 0., 0.1, 0.1, 0.5],
                     [0., 0., 0., 0.1, 0.1, 0.1],
                     [0., 0.3, 0.3, 0.2, 0.2, 0.2],
                     [0., 0., 0.3, 0.3, 0.3, 0.2],
                     [0., 0., 0.3, 0.2, 0.2, 0.4]],
                    [[0., 0., 0., 0.1, 0.1, 0.6],
                     [0., 0., 0., 0.1, 0.1, 0.1],
                     [0., 0.3, 0.3, 0.2, 0.2, 0.2],
                     [0., 0., 0.3, 0.3, 0.3, 0.2],
                     [0., 0., 0.3, 0.2, 0.2, 0.4]]]
        # the label image (labels have to start from 0)
        label = [[[0, 0, 0, 1, 1, 5],
                  [0, 0, 0, 1, 1, 1],
                  [0, 3, 3, 2, 2, 2],
                  [0, 0, 3, 3, 3, 2],
                  [0, 0, 3, 2, 2, 4]],
                 [[0, 0, 0, 1, 1, 6],
                  [0, 0, 0, 1, 1, 1],
                  [0, 3, 3, 2, 2, 2],
                  [0, 0, 3, 3, 3, 2],
                  [0, 0, 3, 2, 2, 4]]]
        # the expected result
        expected_result = {(0,1): 0.833333333,
                           (0,3): 0.5,
                           (1,2): 0.833333333,
                           (1,5): 0.333333333,
                           (1,6): 0.166666667,
                           (2,3): 0.833333333,
                           (2,4): 0.666666667,
                           (5,6): 0.833333333} # only 3D edge
        expected_result = self.__to_two_directed(expected_result)
        # run the function
        result = boundary_difference_of_means(label, (original))
        result = self._reorder_keys(result)
        # check returned values
        self.__compare_dictionaries(result, expected_result)
        
    def _reorder_keys(self, dic, msg_base = ''):
        """Reorders the keys of the result dictionary to be inside itslef ordered."""
        di = {}
        for key, value in dic.items():
            new_key = (min(key[0], key[1]), max(key[0], key[1]))
            if not new_key == key:
                self.assertTrue(not new_key in dic, '{}: Found edges {} and reversed edge {} in the result dictionary, which is not legal.'.format(msg_base, key, new_key))
            di[new_key] = value
        return di
        
    def __to_two_directed(self, dic):
        """Takes a dictionary of values and converts it into one with two directions."""
        for key, value in dic.items():
            dic[key] = (value, value)
        return dic
    
    def __compare_dictionaries(self, result, expected_result, msg_base = ''):
        """Evaluates the returned results."""
        self.assertEqual(len(expected_result), len(result), '{}: Expected {} region neighbourhoods (4-connectedness), instead got {}.'.format(msg_base, len(expected_result), len(result)))
        for key, value in result.items():
            self.assertTrue(key in expected_result, '{}: Region border {} unexpectedly found in results.'.format(msg_base, key))
            if key in expected_result:
                self.assertAlmostEqual(value[0], expected_result[key][0], msg='{}: Weight for region border {} is {}. Expected {}.'.format(msg_base, key, value, expected_result[key]), places=8)
                self.assertAlmostEqual(value[1], expected_result[key][1], msg='{}: Weight for region border {} is {}. Expected {}.'.format(msg_base, key, value, expected_result[key]), places=8)
                self.assertGreater(value[0], 0.0, '{}: Encountered a weight {} <= 0.0 for key {}.'.format(msg_base, value, key))
                self.assertGreater(value[1], 0.0, '{}: Encountered a weight {} <= 0.0 for key {}.'.format(msg_base, value, key))
                
        for key, value in expected_result.items():
            self.assertTrue(key in result, '{}: Region border {} expectedly but not found in results.'.format(msg_base, key))
        
if __name__ == '__main__':
    unittest.main()    
        