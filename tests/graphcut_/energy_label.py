"""
Unittest for the medpy.graphcut.energy methods.

@author Oskar Maier
@version r0.2.1
@since 2011-01-30
@status Release
"""

import math

# build-in modules
import sys
import unittest

# third-party modules
import numpy
from numpy.testing import assert_raises

# own modules
from medpy.graphcut.energy_label import (
    boundary_difference_of_means,
    boundary_stawiaski,
    boundary_stawiaski_directed,
    regional_atlas,
)
from medpy.graphcut.graph import GCGraph


# code
class TestEnergyLabel(unittest.TestCase):
    BOUNDARY_TERMS = [
        boundary_stawiaski,
        boundary_difference_of_means,
        boundary_stawiaski_directed,
        regional_atlas,
    ]
    BOUNDARY_TERMS_1ARG = [boundary_stawiaski, boundary_difference_of_means]
    BOUNDARY_TERMS_2ARG = [boundary_stawiaski_directed, regional_atlas]

    # dedicated function tests
    def test_boundary_stawiaski(self):
        label = [[[1, 1], [1, 1]], [[1, 2], [2, 2]], [[2, 2], [2, 2]]]
        expected_result = {(0, 1): (6, 6)}
        self.__run_boundary_stawiaski_test(
            label, numpy.zeros_like(label), expected_result, "3D images"
        )

        gradient = [[0.0, 0.0, 0.0], [0.0, 0.0, sys.float_info.max]]
        label = [[1, 2, 3], [1, 2, 4]]
        expected_result = {
            (0, 1): (2.0, 2.0),
            (1, 2): (1.0, 1.0),
            (1, 3): (sys.float_info.min, sys.float_info.min),
            (2, 3): (sys.float_info.min, sys.float_info.min),
        }
        self.__run_boundary_stawiaski_test(
            label, gradient, expected_result, "zero edge weight"
        )

        label = [[1, 3, 4], [1, 2, 5], [1, 2, 5]]
        expected_result = {
            (0, 1): (2.0, 2.0),
            (0, 2): (1.0, 1.0),
            (2, 3): (1.0, 1.0),
            (1, 2): (1.0, 1.0),
            (1, 4): (2.0, 2.0),
            (3, 4): (1.0, 1.0),
        }
        self.__run_boundary_stawiaski_test(
            label,
            numpy.zeros(numpy.asarray(label).shape, int),
            expected_result,
            "integer gradient image",
        )

        label = numpy.asarray(label, order="C")  # C-order, gradient same order
        gradient = numpy.zeros(label.shape, order="C")
        self.__run_boundary_stawiaski_test(
            label, gradient, expected_result, "order (C, C)"
        )

        label = numpy.asarray(label, order="F")  # Fortran order, gradient same order
        gradient = numpy.zeros(label.shape, order="F")
        self.__run_boundary_stawiaski_test(
            label, gradient, expected_result, "order (F, F)"
        )

        label = numpy.asarray(label, order="C")  # C-order, gradient different order
        gradient = numpy.zeros(label.shape, order="F")
        self.__run_boundary_stawiaski_test(
            label, gradient, expected_result, "order (C, F)"
        )

        label = numpy.asarray(label, order="F")  # F-order, gradient different order
        gradient = numpy.zeros(label.shape, order="C")
        self.__run_boundary_stawiaski_test(
            label, gradient, expected_result, "order (F, C)"
        )

    def __run_boundary_stawiaski_test(self, label, gradient, expected_result, msg=""):
        label = numpy.asarray(label)
        gradient = numpy.asarray(gradient)
        graph = GCGraphTest(
            numpy.unique(label).size, math.pow(numpy.unique(label).size, 2)
        )
        boundary_stawiaski(graph, label, gradient)
        graph.validate_nweights(self, expected_result, msg)

    def __run_boundary_difference_of_means_test(
        self, label, gradient, expected_result, msg=""
    ):
        label = numpy.asarray(label)
        gradient = numpy.asarray(gradient)
        graph = GCGraphTest(
            numpy.unique(label).size, math.pow(numpy.unique(label).size, 2)
        )
        boundary_difference_of_means(graph, label, gradient)
        graph.validate_nweights(self, expected_result, msg)

    # exception tests
    def test_exception_not_consecutively_labelled(self):
        label = [[1, 4, 8], [1, 3, 10], [1, 3, 10]]
        for bt in self.BOUNDARY_TERMS_1ARG:
            assert_raises(AttributeError, bt, None, label, (None,))
        for bt in self.BOUNDARY_TERMS_2ARG:
            assert_raises(AttributeError, bt, None, label, (None, None))

    def test_exception_not_starting_with_index_one(self):
        label = [[2, 3, 4], [2, 3, 4], [2, 3, 4]]
        for bt in self.BOUNDARY_TERMS_1ARG:
            assert_raises(AttributeError, bt, None, label, (None,))
        for bt in self.BOUNDARY_TERMS_2ARG:
            assert_raises(AttributeError, bt, None, label, (None, None))

    def test_boundary_difference_of_means_borders(self):
        label = [[[1, 1], [1, 1]], [[1, 2], [2, 2]], [[2, 2], [2, 2]]]
        expected_result = {(0, 1): (sys.float_info.min, sys.float_info.min)}
        self.__run_boundary_difference_of_means_test(
            label, numpy.zeros_like(label), expected_result, "3D images"
        )

        gradient = [[0.0, 0.0, 0.0], [0.0, 0.0, sys.float_info.max]]
        label = [[1, 2, 3], [1, 2, 4]]
        expected_result = {
            (0, 1): (1.0, 1.0),
            (1, 2): (1.0, 1.0),
            (1, 3): (sys.float_info.min, sys.float_info.min),
            (2, 3): (sys.float_info.min, sys.float_info.min),
        }
        self.__run_boundary_difference_of_means_test(
            label, gradient, expected_result, "zero edge weight"
        )

        label = [[1, 3, 4], [1, 2, 5], [1, 2, 5]]
        expected_result = {
            (0, 1): (sys.float_info.min, sys.float_info.min),
            (0, 2): (sys.float_info.min, sys.float_info.min),
            (2, 3): (sys.float_info.min, sys.float_info.min),
            (1, 2): (sys.float_info.min, sys.float_info.min),
            (1, 4): (sys.float_info.min, sys.float_info.min),
            (3, 4): (sys.float_info.min, sys.float_info.min),
        }
        self.__run_boundary_difference_of_means_test(
            label,
            numpy.zeros(numpy.asarray(label).shape, int),
            expected_result,
            "integer gradient image",
        )

        label = numpy.asarray(label, order="C")  # C-order, gradient same order
        gradient = numpy.zeros(label.shape, order="C")
        self.__run_boundary_difference_of_means_test(
            label, gradient, expected_result, "order (C, C)"
        )

        label = numpy.asarray(label, order="F")  # Fortran order, gradient same order
        gradient = numpy.zeros(label.shape, order="F")
        self.__run_boundary_difference_of_means_test(
            label, gradient, expected_result, "order (F, F)"
        )

        label = numpy.asarray(label, order="C")  # C-order, gradient different order
        gradient = numpy.zeros(label.shape, order="F")
        self.__run_boundary_difference_of_means_test(
            label, gradient, expected_result, "order (C, F)"
        )

        label = numpy.asarray(label, order="F")  # F-order, gradient different order
        gradient = numpy.zeros(label.shape, order="C")
        self.__run_boundary_difference_of_means_test(
            label, gradient, expected_result, "order (F, C)"
        )


class GCGraphTest(GCGraph):
    """Wrapper around GCGraph, disabling its main functionalities to enable checking of the received values."""

    def __init__(self, nodes, edges):
        self.__nodes = nodes
        self.__edges = edges
        self.__nweights = dict()

    def set_nweight(self, node_from, node_to, weight_there, weight_back):
        """Original graph sums if edges already exists."""
        # print (node_from, node_to, weight_there, weight_back)
        if not (node_from, node_to) in self.__nweights:
            self.__nweights[(node_from, node_to)] = (weight_there, weight_back)
        else:
            weight_there_old, weight_back_old = self.__nweights[(node_from, node_to)]
            self.__nweights[(node_from, node_to)] = (
                weight_there_old + weight_there,
                weight_back_old + weight_back,
            )

    def get_nweights(self):
        return self.__nweights

    def validate_nweights(self, unittest, expected_result, msg_base=""):
        """Compares the nweights hold by the graph with the once provided (as a dict)."""
        unittest.assertTrue(
            len(self.__nweights) == len(expected_result),
            "{}: Expected {} edges, but {} were added.".format(
                msg_base, len(expected_result), len(self.__nweights)
            ),
        )
        node_id_set = set()
        for key in list(self.__nweights.keys()):
            node_id_set.add(key[0])
            node_id_set.add(key[1])
        unittest.assertTrue(
            len(node_id_set) == self.__nodes
        ), "{}: Not all {} node-ids appeared in the edges, but only {}. Missing are {}.".format(
            msg_base,
            self.__nodes,
            len(node_id_set),
            set(range(0, self.__nodes)) - node_id_set,
        )
        self.__compare_dictionaries(
            unittest, self.__nweights, expected_result, msg_base
        )

    def __compare_dictionaries(self, unittest, result, expected_result, msg_base=""):
        """Evaluates the returned results."""
        unittest.assertEqual(
            len(expected_result),
            len(result),
            "{}: The expected result dict contains {} entries (for 4-connectedness), instead found {}.".format(
                msg_base, len(expected_result), len(result)
            ),
        )
        for key, value in list(result.items()):
            unittest.assertTrue(
                key in expected_result,
                "{}: Region border {} unexpectedly found in expected results.".format(
                    msg_base, key
                ),
            )
            if key in expected_result:
                unittest.assertAlmostEqual(
                    value[0],
                    expected_result[key][0],
                    msg="{}: Weight for region border {} is {}. Expected {}.".format(
                        msg_base, key, value, expected_result[key]
                    ),
                    delta=sys.float_info.epsilon,
                )
                unittest.assertAlmostEqual(
                    value[1],
                    expected_result[key][1],
                    msg="{}: Weight for region border {} is {}. Expected {}.".format(
                        msg_base, key, value, expected_result[key]
                    ),
                    delta=sys.float_info.epsilon,
                )
                unittest.assertGreater(
                    value[0],
                    0.0,
                    "{}: Encountered a weight {} <= 0.0 for key {}.".format(
                        msg_base, value, key
                    ),
                )
                unittest.assertGreater(
                    value[1],
                    0.0,
                    "{}: Encountered a weight {} <= 0.0 for key {}.".format(
                        msg_base, value, key
                    ),
                )

        for key, value in list(expected_result.items()):
            unittest.assertTrue(
                key in result,
                "{}: Region border {} expectedly but not found in results.".format(
                    msg_base, key
                ),
            )


if __name__ == "__main__":
    unittest.main()
