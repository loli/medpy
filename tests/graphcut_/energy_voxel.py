"""
Unittest for the medpy.graphcut.energy_voxel methods.

@author Oskar Maier
@version r0.1.0
@since 2016-02-20
@status Release
"""

import unittest

# third-party modules
import numpy

# build-in modules
import pytest
from numpy.testing import assert_array_equal

# own modules
from medpy.graphcut import graph_from_voxels
from medpy.graphcut.energy_voxel import (
    boundary_difference_division,
    boundary_difference_exponential,
    boundary_difference_linear,
    boundary_difference_power,
    boundary_maximum_division,
    boundary_maximum_exponential,
    boundary_maximum_linear,
    boundary_maximum_power,
    regional_probability_map,
)


class TestEnergyVoxel(unittest.TestCase):
    BOUNDARY_TERMS = [
        boundary_difference_linear,
        boundary_difference_exponential,
        boundary_difference_division,
        boundary_difference_power,
        boundary_maximum_linear,
        boundary_maximum_exponential,
        boundary_maximum_division,
        boundary_maximum_power,
    ]
    BOUNDARY_TERMS_2ARGS = [boundary_difference_linear, boundary_maximum_linear]
    BOUNDARY_TERMS_3ARGS = [
        boundary_difference_exponential,
        boundary_difference_division,
        boundary_difference_power,
        boundary_maximum_exponential,
        boundary_maximum_division,
        boundary_maximum_power,
    ]

    image = numpy.asarray(
        [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]], dtype=float
    )
    fgmarkers = numpy.asarray([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]])
    bgmarkers = numpy.asarray([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    result = numpy.asarray(
        [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]], dtype=numpy.bool_
    )

    gradient = numpy.asarray(
        [[0, 0, 0, 0], [0, 1, 1, 1], [0, 1, 0, 0], [0, 1, 0, 0]], dtype=float
    )

    # Base functionality tests
    def test_boundary_difference_linear_2D(self):
        self.__test_boundary_term_2d(boundary_difference_linear, (self.image, False))

    def test_boundary_difference_exponential_2D(self):
        self.__test_boundary_term_2d(
            boundary_difference_exponential, (self.image, 1.0, False)
        )

    def test_boundary_difference_division_2D(self):
        self.__test_boundary_term_2d(
            boundary_difference_division, (self.image, 0.5, False)
        )

    def test_boundary_difference_power_2D(self):
        self.__test_boundary_term_2d(
            boundary_difference_power, (self.image, 2.0, False)
        )

    def test_boundary_maximum_linear_2D(self):
        self.__test_boundary_term_2d(boundary_maximum_linear, (self.gradient, False))

    def test_boundary_maximum_exponential_2D(self):
        self.__test_boundary_term_2d(
            boundary_maximum_exponential, (self.gradient, 1.0, False)
        )

    def test_boundary_maximum_division_2D(self):
        self.__test_boundary_term_2d(
            boundary_maximum_division, (self.gradient, 0.5, False)
        )

    def test_boundary_maximum_power_2D(self):
        self.__test_boundary_term_2d(
            boundary_maximum_power, (self.gradient, 2.0, False)
        )

    def test_regional_probability_map(self):
        probability = self.image / 2.0
        self.__test_regional_term_2d(regional_probability_map, (probability, 1.0))

    # Spacing tests
    def test_spacing(self):
        image = numpy.asarray(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 2, 0, 0],
                [0, 0, 2, 0, 0],
                [0, 0, 2, 0, 0],
                [0, 0, 2, 0, 0],
            ],
            dtype=float,
        )
        fgmarkers = numpy.asarray(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
            ],
            dtype=numpy.bool_,
        )
        bgmarkers = numpy.asarray(
            [
                [1, 0, 0, 0, 1],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            dtype=numpy.bool_,
        )
        expected = image.astype(numpy.bool_)
        graph = graph_from_voxels(
            fgmarkers,
            bgmarkers,
            boundary_term=boundary_difference_division,
            boundary_term_args=(image, 1.0, (1.0, 5.0)),
        )
        result = self.__execute(graph, image)
        assert_array_equal(result, expected)

    # Special case tests
    def test_negative_image(self):
        image = numpy.asarray([[-1, 1, -4], [2, -7, 3], [-2.3, 3, -7]], dtype=float)
        self.__test_all_on_image(image)

    @pytest.mark.filterwarnings("ignore:invalid value encountered")
    def test_zero_image(self):
        image = numpy.asarray([[0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=float)
        self.__test_all_on_image(image)

    # Helper functions
    def __test_all_on_image(self, image):
        for bt in self.BOUNDARY_TERMS_2ARGS:
            graph = graph_from_voxels(
                self.fgmarkers,
                self.bgmarkers,
                boundary_term=bt,
                boundary_term_args=(image, False),
            )
            self.__execute(graph, self.image)

        for bt in self.BOUNDARY_TERMS_3ARGS:
            graph = graph_from_voxels(
                self.fgmarkers,
                self.bgmarkers,
                boundary_term=bt,
                boundary_term_args=(image, 1.0, False),
            )
            self.__execute(graph, self.image)

    def __test_boundary_term_2d(self, term, term_args):
        graph = graph_from_voxels(
            self.fgmarkers,
            self.bgmarkers,
            boundary_term=term,
            boundary_term_args=term_args,
        )
        result = self.__execute(graph, self.image)
        assert_array_equal(result, self.result)

    def __test_regional_term_2d(self, term, term_args):
        graph = graph_from_voxels(
            self.fgmarkers,
            self.bgmarkers,
            regional_term=term,
            regional_term_args=term_args,
        )
        result = self.__execute(graph, self.image)
        assert_array_equal(result, self.result)

    def __execute(self, graph, image):
        """Executes a graph cut and returns the processed results."""
        # execute min-cut / executing BK_MFMC
        try:
            graph.maxflow()
        except Exception as e:
            self.fail(
                "An error was thrown during the external executions: {}".format(
                    e.message
                )
            )

        # reshape results to form a valid mask
        result = numpy.zeros(image.size, dtype=numpy.bool_)
        for idx in range(len(result)):
            result[idx] = 0 if graph.termtype.SINK == graph.what_segment(idx) else 1
        return result.reshape(image.shape)

    def __print_nweights(self, graph):
        n = graph.get_node_num()
        for i in range(n):
            for j in range(i, n):
                if not i == j:
                    print((i, j, graph.get_edge(i, j)))
