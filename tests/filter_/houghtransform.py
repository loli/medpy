"""
Unittest for medpy.filter.houghtransform

@author Oskar Maier
@version r0.1.0
@since 2013-06-07
@status Release
"""

# build-in modules
import unittest

# third-party modules
import numpy

# own modules
from medpy.filter import ght, template_ellipsoid, template_sphere


# code
class TestHoughTransform(unittest.TestCase):
    def setUp(self):
        pass

    def test_takes_sequences(self):
        img = [[1, 2, 3, 4, 5]]
        template = [[1, 0]]
        ght(img, template)
        img = (1, 2, 3, 4, 5)
        template = (1, 0)
        ght(img, template)

    def test_even_template(self):
        # prepare
        img = [
            [1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ]
        img = numpy.asarray(img).astype(numpy.bool_)
        template = numpy.asarray([[True, True], [True, True]])
        result_array = numpy.asarray(
            [
                [4, 2, 0, 0, 0],
                [2, 2, 2, 1, 0],
                [0, 2, 4, 2, 0],
                [0, 1, 2, 1, 0],
                [0, 0, 0, 0, 0],
            ]
        ).astype(numpy.int32)
        result_dtype = numpy.int32

        # run
        result = ght(img, template)

        # test
        self.assertTrue(
            numpy.all(result == result_array),
            "Returned hough transformation differs from the expected values.",
        )
        self.assertTrue(
            result.dtype == result_dtype,
            "Returned hough transformation is not of the expected numpy.dtype",
        )

    def test_odd_template(self):
        # prepare
        img = [
            [1, 1, 1, 0, 0],
            [1, 1, 1, 0, 0],
            [1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        img = numpy.asarray(img).astype(numpy.bool_)
        template = numpy.asarray(
            [[True, True, True], [True, True, True], [True, True, True]]
        )
        result_array = numpy.asarray(
            [
                [4, 6, 4, 2, 0],
                [6, 9, 6, 3, 0],
                [4, 6, 4, 2, 0],
                [2, 3, 2, 1, 0],
                [0, 0, 0, 0, 0],
            ]
        ).astype(numpy.int32)
        result_dtype = numpy.int32

        # run
        result = ght(img, template)

        # test
        self.assertTrue(
            numpy.all(result == result_array),
            "Returned hough transformation differs from the expected values.",
        )
        self.assertTrue(
            result.dtype == result_dtype,
            "Returned hough transformation is not of the expected numpy.dtype",
        )

    def test_int_img(self):
        # prepare
        img = [[2, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        img = numpy.asarray(img)
        template = numpy.asarray([[True, True], [True, False]])
        result_array = numpy.asarray(
            [[4, 2, 0, 0], [2, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        ).astype(img.dtype)
        result_dtype = img.dtype

        # run
        result = ght(img, template)

        # test
        self.assertTrue(
            numpy.all(result == result_array),
            "Returned hough transformation differs from the expected values.",
        )
        self.assertTrue(
            result.dtype == result_dtype,
            "Returned hough transformation is not of the expected numpy.dtype",
        )

    def test_float_img(self):
        # prepare
        img = [[2.0, 3.0, 0, 0], [1.0, 2.0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        img = numpy.asarray(img)
        template = numpy.asarray([[True, True], [True, False]])
        result_array = numpy.asarray(
            [[6.0, 5.0, 0, 0], [3.0, 2.0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        ).astype(img.dtype)
        result_dtype = img.dtype

        # run
        result = ght(img, template)

        # test
        self.assertTrue(
            numpy.all(result == result_array),
            "Returned hough transformation differs from the expected values.",
        )
        self.assertTrue(
            result.dtype == result_dtype,
            "Returned hough transformation is not of the expected numpy.dtype",
        )

    def test_template_sphere_odd_radius(self):
        # prepare
        expected = [
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
        ]

        # run
        result = template_sphere(1.5, 3)

        # test
        self.assertTrue(
            numpy.all(result == expected),
            "Returned template contains not the expected spherical structure.",
        )
        self.assertTrue(
            result.dtype == numpy.bool_,
            "Returned template should be of type numpy.bool_",
        )

    def test_template_sphere_even_radius(self):
        # prepare
        expected = [
            [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
            [[0, 1, 1, 0], [1, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 0]],
            [[0, 1, 1, 0], [1, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 0]],
            [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
        ]

        # run
        result = template_sphere(2, 3)

        # test
        self.assertTrue(
            numpy.all(result == expected),
            "Returned template contains not the expected spherical structure.",
        )
        self.assertTrue(
            result.dtype == numpy.bool_,
            "Returned template should be of type numpy.bool_",
        )

    def test_template_ellipsoid(self):
        # prepare
        expected = [
            [
                [False, False, False, False, False],
                [False, True, True, True, False],
                [False, True, True, True, False],
                [False, False, False, False, False],
            ],
            [
                [False, True, True, True, False],
                [True, True, True, True, True],
                [True, True, True, True, True],
                [False, True, True, True, False],
            ],
            [
                [False, False, False, False, False],
                [False, True, True, True, False],
                [False, True, True, True, False],
                [False, False, False, False, False],
            ],
        ]

        # run
        result = template_ellipsoid((3, 4, 5))

        # test
        self.assertTrue(
            numpy.all(result == expected),
            "Returned template contains not the expected spherical structure.",
        )
        self.assertTrue(
            result.dtype == numpy.bool_,
            "Returned template should be of type numpy.bool_",
        )

    def test_exceptions(self):
        self.assertRaises(TypeError, template_sphere, 1.1)
        self.assertRaises(AttributeError, ght, [[0, 1], [2, 3]], [0, 1, 2])
        self.assertRaises(AttributeError, ght, [0, 1], [0, 1, 2])

    def test_dimensions(self):
        # 1D
        img = numpy.random.rand(10)
        template = numpy.random.randint(0, 2, (3))
        result = ght(img, template)
        self.assertEqual(
            result.ndim, 1, "Computing ght with one-dimensional input data failed."
        )
        # 2D
        img = numpy.random.rand(10, 11)
        template = numpy.random.randint(0, 2, (3, 4))
        result = ght(img, template)
        self.assertEqual(
            result.ndim, 2, "Computing ght with two-dimensional input data failed."
        )
        # 3D
        img = numpy.random.rand(10, 11, 12)
        template = numpy.random.randint(0, 2, (3, 4, 5))
        result = ght(img, template)
        self.assertEqual(
            result.ndim, 3, "Computing ght with three-dimensional input data failed."
        )
        # 4D
        img = numpy.random.rand(10, 11, 12, 13)
        template = numpy.random.randint(0, 2, (3, 4, 5, 6))
        result = ght(img, template)
        self.assertEqual(
            result.ndim, 4, "Computing ght with four-dimensional input data failed."
        )
        # 5D
        img = numpy.random.rand(3, 4, 3, 4, 3)
        template = numpy.random.randint(0, 2, (2, 2, 2, 2, 2))
        result = ght(img, template)
        self.assertEqual(
            result.ndim, 5, "Computing ght with five-dimensional input data failed."
        )


if __name__ == "__main__":
    unittest.main()
