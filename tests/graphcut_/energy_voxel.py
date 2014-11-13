"""
Unittest for the medpy.graphcut.energy_voxel methods.

!TODO:
- Write tests for the other boundary difference term
- Write tests for the boundary maximum terms


@author Oskar Maier
@version r0.1.4
@since 2011-04-11
@status Release
"""

# build-in modules
import sys
import unittest

# third-party modules
import scipy

# own modules
from medpy.graphcut.graph import GCGraph
from medpy.graphcut.energy_voxel import (boundary_difference_linear, boundary_difference_division,
                                         boundary_difference_exponential, boundary_difference_power)
from medpy.graphcut.energy_voxel import (boundary_maximum_linear, boundary_maximum_division,
                                         boundary_maximum_exponential, boundary_maximum_power)

# code
class TestEnergyVoxel(unittest.TestCase):
        
    def test_boundary_difference_linear(self):
        self.__test_boundary_difference_2d(boundary_difference_linear)
        self.__test_boundary_difference_3d(boundary_difference_linear)
        self.__test_boundary_difference(boundary_difference_linear)
        
    def test_boundary_difference_division(self):
#        self.__test_boundary_difference_2d(boundary_difference_division)
#        self.__test_boundary_difference_3d(boundary_difference_division)
#        self.__test_boundary_difference(boundary_difference_division)
        pass
        
    def test_boundary_difference_exponential(self):
#        self.__test_boundary_difference_2d(boundary_difference_exponential)
#        self.__test_boundary_difference_3d(boundary_difference_exponential)
#        self.__test_boundary_difference(boundary_difference_exponential)
        pass
        
    def test_boundary_difference_power(self):
#        self.__test_boundary_difference_2d(boundary_difference_power)
#        self.__test_boundary_difference_3d(boundary_difference_power)
#        self.__test_boundary_difference(boundary_difference_power)
        pass
        
    def __test_boundary_difference(self, boundary_term):
        """Test intensity difference based boundary terms for border conditions."""
        # TEST1: test for behavior on occurrence of empty dimensions
        original = [[[1,0,1,2,3],
                     [1,0,1,4,3],
                     [0,1,1,6,4]]]
        original = scipy.asarray(original)
        expected_result = {(8, 13): (0.66666666666666674, 0.66666666666666674), (5, 6): (0.83333333333333337, 0.83333333333333337), (8, 9): (0.83333333333333337, 0.83333333333333337), (1, 6): (1.0, 1.0), (10, 11): (0.83333333333333337, 0.83333333333333337), (1, 2): (0.83333333333333337, 0.83333333333333337), (4, 9): (1.0, 1.0), (12, 13): (0.16666666666666663, 0.16666666666666663), (7, 12): (1.0, 1.0), (0, 1): (0.83333333333333337, 0.83333333333333337), (9, 14): (0.83333333333333337, 0.83333333333333337), (6, 11): (0.83333333333333337, 0.83333333333333337), (2, 3): (0.83333333333333337, 0.83333333333333337), (6, 7): (0.83333333333333337, 0.83333333333333337), (11, 12): (1.0, 1.0), (2, 7): (1.0, 1.0), (5, 10): (0.83333333333333337, 0.83333333333333337), (13, 14): (0.66666666666666674, 0.66666666666666674), (7, 8): (0.5, 0.5), (3, 8): (0.66666666666666674, 0.66666666666666674), (0, 5): (1.0, 1.0), (3, 4): (0.83333333333333337, 0.83333333333333337)}
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        boundary_term(graph, (original))
        graph.validate_nweights(self, expected_result, "TEST1")
        
        # TEST2: test for behavior on occurrence of very small (~0) and 1 weights
        original = [[[0,0,0,0,0.5],
                     [0,0,0,0,0.5],
                     [0,0,0,0,0.5]]]
        original = scipy.asarray(original)
        expected_result = {(8, 13): (1.0, 1.0), (5, 6): (1.0, 1.0), (8, 9): (sys.float_info.min, sys.float_info.min), (1, 6): (1.0, 1.0), (10, 11): (1.0, 1.0), (1, 2): (1.0, 1.0), (4, 9): (1.0, 1.0), (12, 13): (1.0, 1.0), (7, 12): (1.0, 1.0), (0, 1): (1.0, 1.0), (9, 14): (1.0, 1.0), (6, 11): (1.0, 1.0), (2, 3): (1.0, 1.0), (6, 7): (1.0, 1.0), (11, 12): (1.0, 1.0), (2, 7): (1.0, 1.0), (5, 10): (1.0, 1.0), (13, 14): (2.2250738585072014e-308, 2.2250738585072014e-308), (7, 8): (1.0, 1.0), (3, 8): (1.0, 1.0), (0, 5): (1.0, 1.0), (3, 4): (sys.float_info.min, sys.float_info.min)}
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        boundary_term(graph, (original))
        graph.validate_nweights(self, expected_result, "TEST2")
        
        # TEST3: test scale, i.e. that irregardless of the value the highest step should always yield the lowest weight
        # The results of this test have to be the same as the one above
        original = [[[0,0,0,0,99999],
                     [0,0,0,0,99999],
                     [0,0,0,0,99999]]]
        original = scipy.asarray(original)
        expected_result = {(8, 13): (1.0, 1.0), (5, 6): (1.0, 1.0), (8, 9): (2.2250738585072014e-308, 2.2250738585072014e-308), (1, 6): (1.0, 1.0), (10, 11): (1.0, 1.0), (1, 2): (1.0, 1.0), (4, 9): (1.0, 1.0), (12, 13): (1.0, 1.0), (7, 12): (1.0, 1.0), (0, 1): (1.0, 1.0), (9, 14): (1.0, 1.0), (6, 11): (1.0, 1.0), (2, 3): (1.0, 1.0), (6, 7): (1.0, 1.0), (11, 12): (1.0, 1.0), (2, 7): (1.0, 1.0), (5, 10): (1.0, 1.0), (13, 14): (2.2250738585072014e-308, 2.2250738585072014e-308), (7, 8): (1.0, 1.0), (3, 8): (1.0, 1.0), (0, 5): (1.0, 1.0), (3, 4): (2.2250738585072014e-308, 2.2250738585072014e-308)}
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        boundary_term(graph, (original))
        graph.validate_nweights(self, expected_result, "TEST3")
       
        # TEST4: check behavior for float original image
        original = [[[1,0,1,2,3],
                     [1,0,1,4,3],
                     [0,1,1,6,4]]]
        original = scipy.asarray(original)
        expected_result = {(8, 13): (0.66666666666666674, 0.66666666666666674), (5, 6): (0.83333333333333337, 0.83333333333333337), (8, 9): (0.83333333333333337, 0.83333333333333337), (1, 6): (1.0, 1.0), (10, 11): (0.83333333333333337, 0.83333333333333337), (1, 2): (0.83333333333333337, 0.83333333333333337), (4, 9): (1.0, 1.0), (12, 13): (0.16666666666666663, 0.16666666666666663), (7, 12): (1.0, 1.0), (0, 1): (0.83333333333333337, 0.83333333333333337), (9, 14): (0.83333333333333337, 0.83333333333333337), (6, 11): (0.83333333333333337, 0.83333333333333337), (2, 3): (0.83333333333333337, 0.83333333333333337), (6, 7): (0.83333333333333337, 0.83333333333333337), (11, 12): (1.0, 1.0), (2, 7): (1.0, 1.0), (5, 10): (0.83333333333333337, 0.83333333333333337), (13, 14): (0.66666666666666674, 0.66666666666666674), (7, 8): (0.5, 0.5), (3, 8): (0.66666666666666674, 0.66666666666666674), (0, 5): (1.0, 1.0), (3, 4): (0.83333333333333337, 0.83333333333333337)}
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        boundary_term(graph, (original))
        graph.validate_nweights(self, expected_result, "TEST4")
        
        # TEST5: reaction to different array orders
        original = [[[1,0,1,2,3],
                     [1,0,1,4,3],
                     [0,1,1,6,4]]]
        expected_result = {(8, 13): (0.66666666666666674, 0.66666666666666674), (5, 6): (0.83333333333333337, 0.83333333333333337), (8, 9): (0.83333333333333337, 0.83333333333333337), (1, 6): (1.0, 1.0), (10, 11): (0.83333333333333337, 0.83333333333333337), (1, 2): (0.83333333333333337, 0.83333333333333337), (4, 9): (1.0, 1.0), (12, 13): (0.16666666666666663, 0.16666666666666663), (7, 12): (1.0, 1.0), (0, 1): (0.83333333333333337, 0.83333333333333337), (9, 14): (0.83333333333333337, 0.83333333333333337), (6, 11): (0.83333333333333337, 0.83333333333333337), (2, 3): (0.83333333333333337, 0.83333333333333337), (6, 7): (0.83333333333333337, 0.83333333333333337), (11, 12): (1.0, 1.0), (2, 7): (1.0, 1.0), (5, 10): (0.83333333333333337, 0.83333333333333337), (13, 14): (0.66666666666666674, 0.66666666666666674), (7, 8): (0.5, 0.5), (3, 8): (0.66666666666666674, 0.66666666666666674), (0, 5): (1.0, 1.0), (3, 4): (0.83333333333333337, 0.83333333333333337)}
        
        original = scipy.asarray(original, order='C') # C-order
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))        
        boundary_term(graph, (original))
        graph.validate_nweights(self, expected_result, "TEST5 (C)")
        
        original = scipy.asarray(original, order='F') # Fortran order
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        boundary_term(graph, (original))
        graph.validate_nweights(self, expected_result, "TEST5 (F)")
     
        
    def __test_boundary_difference_2d(self, boundary_term):
        """Test intensity difference based boundary terms for 2D case."""
        # the gradient magnitude image
        original = [[1,0,1,2,3],
                    [1,0,1,4,3],
                    [0,1,1,6,4]]
        original = scipy.asarray(original)
        # the expected results
        expected_result = {(8, 13): (0.66666666666666674, 0.66666666666666674), (5, 6): (0.83333333333333337, 0.83333333333333337), (8, 9): (0.83333333333333337, 0.83333333333333337), (1, 6): (1.0, 1.0), (10, 11): (0.83333333333333337, 0.83333333333333337), (1, 2): (0.83333333333333337, 0.83333333333333337), (4, 9): (1.0, 1.0), (12, 13): (0.16666666666666663, 0.16666666666666663), (7, 12): (1.0, 1.0), (0, 1): (0.83333333333333337, 0.83333333333333337), (9, 14): (0.83333333333333337, 0.83333333333333337), (6, 11): (0.83333333333333337, 0.83333333333333337), (2, 3): (0.83333333333333337, 0.83333333333333337), (6, 7): (0.83333333333333337, 0.83333333333333337), (11, 12): (1.0, 1.0), (2, 7): (1.0, 1.0), (5, 10): (0.83333333333333337, 0.83333333333333337), (13, 14): (0.66666666666666674, 0.66666666666666674), (7, 8): (0.5, 0.5), (3, 8): (0.66666666666666674, 0.66666666666666674), (0, 5): (1.0, 1.0), (3, 4): (0.83333333333333337, 0.83333333333333337)}
        # initialize graph object
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        # run the function
        boundary_term(graph, (original))
        # check created graph for validity
        graph.validate_nweights(self, expected_result, "Voxels means 2D")        
        
    def __test_boundary_difference_3d(self, boundary_term):
        """Test intensity difference based boundary terms for 3D case."""
        # the gradient magnitude image
        original = [[[1,0,1,2,3],
                     [1,0,1,4,3],
                     [0,1,1,6,4]],
                    [[1,0,1,2,3],
                     [1,0,1,4,3],
                     [0,1,1,6,4]]]
        original = scipy.asarray(original)
        # the expected results
        expected_result = {(8, 13): (0.66666666666666674, 0.66666666666666674), (12, 27): (1.0, 1.0), (7, 12): (1.0, 1.0), (6, 21): (1.0, 1.0), (8, 9): (0.83333333333333337, 0.83333333333333337), (21, 26): (0.83333333333333337, 0.83333333333333337), (1, 6): (1.0, 1.0), (13, 14): (0.66666666666666674, 0.66666666666666674), (20, 25): (0.83333333333333337, 0.83333333333333337), (18, 19): (0.83333333333333337, 0.83333333333333337), (18, 23): (0.66666666666666674, 0.66666666666666674), (4, 9): (1.0, 1.0), (8, 23): (1.0, 1.0), (0, 15): (1.0, 1.0), (22, 27): (1.0, 1.0), (23, 24): (0.83333333333333337, 0.83333333333333337), (1, 16): (1.0, 1.0), (5, 20): (1.0, 1.0), (25, 26): (0.83333333333333337, 0.83333333333333337), (15, 20): (1.0, 1.0), (2, 17): (1.0, 1.0), (17, 22): (1.0, 1.0), (9, 24): (1.0, 1.0), (20, 21): (0.83333333333333337, 0.83333333333333337), (27, 28): (0.16666666666666663, 0.16666666666666663), (0, 1): (0.83333333333333337, 0.83333333333333337), (5, 6): (0.83333333333333337, 0.83333333333333337), (1, 2): (0.83333333333333337, 0.83333333333333337), (9, 14): (0.83333333333333337, 0.83333333333333337), (21, 22): (0.83333333333333337, 0.83333333333333337), (6, 11): (0.83333333333333337, 0.83333333333333337), (6, 7): (0.83333333333333337, 0.83333333333333337), (19, 24): (1.0, 1.0), (22, 23): (0.5, 0.5), (11, 26): (1.0, 1.0), (28, 29): (0.66666666666666674, 0.66666666666666674), (0, 5): (1.0, 1.0), (15, 16): (0.83333333333333337, 0.83333333333333337), (24, 29): (0.83333333333333337, 0.83333333333333337), (7, 22): (1.0, 1.0), (17, 18): (0.83333333333333337, 0.83333333333333337), (11, 12): (1.0, 1.0), (14, 29): (1.0, 1.0), (16, 17): (0.83333333333333337, 0.83333333333333337), (2, 7): (1.0, 1.0), (5, 10): (0.83333333333333337, 0.83333333333333337), (4, 19): (1.0, 1.0), (23, 28): (0.66666666666666674, 0.66666666666666674), (7, 8): (0.5, 0.5), (13, 28): (1.0, 1.0), (10, 25): (1.0, 1.0), (3, 8): (0.66666666666666674, 0.66666666666666674), (12, 13): (0.16666666666666663, 0.16666666666666663), (3, 18): (1.0, 1.0), (2, 3): (0.83333333333333337, 0.83333333333333337), (16, 21): (1.0, 1.0), (10, 11): (0.83333333333333337, 0.83333333333333337), (3, 4): (0.83333333333333337, 0.83333333333333337), (26, 27): (1.0, 1.0)}
        # initialize graph object
        graph = GCGraphTest(original.size, self.__voxel_4conectedness(original.shape))
        # run the function
        boundary_term(graph, (original))
        # check created graph for validity
        graph.validate_nweights(self, expected_result, "Voxels means 3D")

    def __voxel_4conectedness(self, shape):
        """
        Returns the number of edges for the supplied image shape assuming 4-connectedness.
        """
        shape = list(shape)
        while 1 in shape: shape.remove(1)
        return int(round(sum([(dim - 1)/float(dim) for dim in shape]) * scipy.prod(shape)))

class GCGraphTest(GCGraph):
    """Wrapper around GCGraph, disabling its main functionalities to enable checking of the received values."""
    
    def __init__(self, nodes, edges):
        self.__nodes = nodes
        self.__edges = edges
        self.__nweights = dict()
        
    def set_nweight(self, node_from, node_to, weight_there, weight_back):
        self.__nweights[(node_from, node_to)] = (weight_there, weight_back)
        
    def get_nweights(self):
        return self.__nweights

    def validate_nweights(self, unittest, expected_result, msg_base = ''):
        """Compares the nweights hold by the graph with the once provided (as a dict)."""
        unittest.assertTrue(len(self.__nweights) == self.__edges, '{}: Expected {} edges, but {} were added.'.format(msg_base, self.__edges, len(self.__nweights)))
        node_id_set = set()
        for key in self.__nweights.keys():
            node_id_set.add(key[0])
            node_id_set.add(key[1])
        unittest.assertTrue(len(node_id_set) == self.__nodes), '{}: Not all {} node-ids appeared in the edges, but only {}. Missing are {}.'.format(msg_base, self.__nodes, len(node_id_set), set(range(0, self.__nodes)) - node_id_set)
        self.__compare_dictionaries(unittest, self.__nweights, expected_result, msg_base)

    def __compare_dictionaries(self, unittest, result, expected_result, msg_base = ''):
        """Evaluates the returned results."""
        unittest.assertEqual(len(expected_result), len(result), '{}: The expected result dict contains {} entries (for 4-connectedness), instead found {}.'.format(msg_base, len(expected_result), len(result)))
        for key, value in result.items():
            unittest.assertTrue(key in expected_result, '{}: Region border {} unexpectedly found in results.'.format(msg_base, key))
            if key in expected_result:
                unittest.assertAlmostEqual(value[0], expected_result[key][0], msg='{}: Weight for region border {} is {}. Expected {}.'.format(msg_base, key, value, expected_result[key]), delta=sys.float_info.epsilon)
                unittest.assertAlmostEqual(value[1], expected_result[key][1], msg='{}: Weight for region border {} is {}. Expected {}.'.format(msg_base, key, value, expected_result[key]), delta=sys.float_info.epsilon)
                unittest.assertGreater(value[0], 0.0, '{}: Encountered a weight {} <= 0.0 for key {}.'.format(msg_base, value, key))
                unittest.assertGreater(value[1], 0.0, '{}: Encountered a weight {} <= 0.0 for key {}.'.format(msg_base, value, key))
                unittest.assertLessEqual(value[0], 1.0, '{}: Encountered a weight {} > 1.0 for key {}.'.format(msg_base, value, key))
                unittest.assertLessEqual(value[1], 1.0, '{}: Encountered a weight {} > 1.0 for key {}.'.format(msg_base, value, key))
                
        for key, value in expected_result.items():
            unittest.assertTrue(key in result, '{}: Region border {} expectedly but not found in results.'.format(msg_base, key))

if __name__ == '__main__':
    unittest.main()    
        