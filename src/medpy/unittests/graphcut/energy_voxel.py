"""
Unittest for the medpy.graphcut.energy_voxel methods.

!TODO:
- Write the test according to the example of the energy_label test
  (All existing code is from there and has to be strongly adapted.)
- Update the description in medpy.graphcut.energy_voxel

@author Oskar Maier
@version d0.0.1
@since 2011-04-11
@status Development
"""

# build-in modules
import sys
import unittest

# third-party modules
import scipy

# own modules
from medpy.graphcut import boundary_difference_of_means_voxel

# code
class TestEnergyVoxel(unittest.TestCase):
        
    def test_boundary_difference_of_means_voxel_borders(self):
        """
        Test the @link medpy.graphcut.boundary_difference_of_means_voxel() border conditions.
        """ 
        # TEST1: test for a label image with not continuous label ids not starting from 0
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        expected_result = {(1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test1')
        # TEST2: test for a label image with negative labels
        label = [[-1, 4, 8],
                 [-1, 3, 10],
                 [1, -3, 10]]
        expected_result = {(-1, 1): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (-1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (-3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (-3, 1): (sys.float_info.epsilon, sys.float_info.epsilon), (-3, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (-1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test2')
        # TEST3: test for behavior on occurrence of very small (~0) and 1 weights
        gradient = [[0., 0., 0.],
                    [0., 0., sys.float_info.max]]
        label = [[0, 1, 2],
                 [0, 1, 3]]
        expected_result = {(0, 1): (1.0, 1.0), (1, 2): (1.0, 1.0), (1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (2, 3): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (gradient))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test3')
        # TEST4: check behavior for integer gradient image
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        label = scipy.asarray(label)
        expected_result = {(1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros(label.shape, scipy.int_)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test4')
        # TEST5: reaction to different array orders
        label = [[1, 4, 8],
                 [1, 3, 10],
                 [1, 3, 10]]
        label = scipy.asarray(label, order='C') # C-order, gradient same order
        expected_result = {(1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (C,C)')
        label = scipy.asarray(label, order='F') # Fortran order, gradient same order
        expected_result = {(1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros_like(label)))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (F, F)')
        label = scipy.asarray(label, order='C') # C-order, gradient different order
        expected_result = {(1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros(label.shape, order='F')))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (C, F)')
        label = scipy.asarray(label, order='F') # F-order, gradient different order
        expected_result = {(1, 3): (sys.float_info.epsilon, sys.float_info.epsilon), (4, 8): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (8, 10): (sys.float_info.epsilon, sys.float_info.epsilon), (1, 4): (sys.float_info.epsilon, sys.float_info.epsilon), (3, 4): (sys.float_info.epsilon, sys.float_info.epsilon)}
        result = boundary_difference_of_means_label(label, (scipy.zeros(label.shape, order='C')))
        result = self._reorder_keys(result)
        self.__compare_dictionaries(result, expected_result, 'Test5 (F, C)')        
        
    def test_boundary_difference_of_means_voxel_2d(self):
        """
        Test the @link medpy.graphcut.boundary_difference_of_means_voxel() function for 2D.
        """
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
        result = boundary_difference_of_means_label(label, (original))
        result = self._reorder_keys(result)
        # check returned values
        self.__compare_dictionaries(result, expected_result)
        
    def test_boundary_difference_of_means_voxel_3d(self):
        """
        Test the @link medpy.graphcut.boundary_difference_of_means_voxel() function for 3D.
        """
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
        result = boundary_difference_of_means_label(label, (original))
        result = self._reorder_keys(result)
        # check returned values
        self.__compare_dictionaries(result, expected_result)
        
    def _reorder_keys(self, dic, msg_base = ''):
        """Reorders the keys of the result dictionary to be inside itslef ordered."""
        di = {}
        for key, value in dic.iteritems():
            new_key = (min(key[0], key[1]), max(key[0], key[1]))
            if not new_key == key:
                self.assertTrue(not new_key in dic, '{}: Found edges {} and reversed edge {} in the result dictionary, which is not legal.'.format(msg_base, key, new_key))
            di[new_key] = value
        return di
        
    def __to_two_directed(self, dic):
        """Takes a dictionary of values and converts it into one with two directions."""
        for key, value in dic.iteritems():
            dic[key] = (value, value)
        return dic
    
    def __compare_dictionaries(self, result, expected_result, msg_base = ''):
        """Evaluates the returned results."""
        self.assertEqual(len(expected_result), len(result), '{}: Expected {} region neighbourhoods (4-connectedness), instead got {}.'.format(msg_base, len(expected_result), len(result)))
        for key, value in result.iteritems():
            self.assertTrue(key in expected_result, '{}: Region border {} unexpectedly found in results.'.format(msg_base, key))
            if key in expected_result:
                self.assertAlmostEqual(value[0], expected_result[key][0], msg='{}: Weight for region border {} is {}. Expected {}.'.format(msg_base, key, value, expected_result[key]))
                self.assertAlmostEqual(value[1], expected_result[key][1], msg='{}: Weight for region border {} is {}. Expected {}.'.format(msg_base, key, value, expected_result[key]))
                self.assertGreater(value[0], 0.0, '{}: Encountered a weight {} <= 0.0 for key {}.'.format(msg_base, value, key))
                self.assertGreater(value[1], 0.0, '{}: Encountered a weight {} <= 0.0 for key {}.'.format(msg_base, value, key))
                
        for key, value in expected_result.iteritems():
            self.assertTrue(key in result, '{}: Region border {} expectedly but not found in results.'.format(msg_base, key))
        
if __name__ == '__main__':
    unittest.main()    
        