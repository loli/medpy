"""
Unittest for medpy.filter.utilities

@author Oskar Maier
@version r0.1.0
@since 2013-12-03
@status Release
"""

# build-in modules
import unittest

# third-party modules
import numpy

# own modules
from medpy.filter import pad


# code
class TestUtilities(unittest.TestCase):
    def setUp(self):
        pass

    def test_pad_bordercases(self):
        "Test pad for border cases in 3D"
        input = numpy.ones((3, 3, 3))

        # no padding in all dimensions
        pad(input=input, size=1, mode="reflect")
        pad(input=input, size=1, mode="mirror")
        pad(input=input, size=1, mode="constant")
        pad(input=input, size=1, mode="nearest")
        pad(input=input, size=1, mode="wrap")

        # no padding in one dimension
        pad(input=input, size=(1, 2, 2), mode="reflect")
        pad(input=input, size=(1, 2, 2), mode="mirror")
        pad(input=input, size=(1, 2, 2), mode="constant")
        pad(input=input, size=(1, 2, 2), mode="nearest")
        pad(input=input, size=(1, 2, 2), mode="wrap")

        # same size as image
        pad(input=input, size=3, mode="reflect")
        pad(input=input, size=3, mode="mirror")
        pad(input=input, size=3, mode="constant")
        pad(input=input, size=3, mode="nearest")
        pad(input=input, size=3, mode="wrap")

        # bigger than image
        pad(input=input, size=4, mode="reflect")
        pad(input=input, size=4, mode="mirror")
        pad(input=input, size=4, mode="constant")
        pad(input=input, size=4, mode="nearest")
        pad(input=input, size=4, mode="wrap")

    def test_pad_odd(self):
        "Test pad for odd footprints in 2D"
        input = numpy.asarray([[1, 3, 4], [2, 2, 2]])
        size = 3

        expected = numpy.asarray(
            [[2, 2, 2, 2, 2], [3, 1, 3, 4, 3], [2, 2, 2, 2, 2], [3, 1, 3, 4, 3]]
        )
        result = pad(input=input, size=size, mode="mirror")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray(
            [[1, 1, 3, 4, 4], [1, 1, 3, 4, 4], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]]
        )
        result = pad(input=input, size=size, mode="reflect")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray(
            [[2, 2, 2, 2, 2], [4, 1, 3, 4, 1], [2, 2, 2, 2, 2], [4, 1, 3, 4, 1]]
        )
        result = pad(input=input, size=size, mode="wrap")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray(
            [[1, 1, 3, 4, 4], [1, 1, 3, 4, 4], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]]
        )
        result = pad(input=input, size=size, mode="nearest")
        numpy.testing.assert_array_equal(result, expected)
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray(
            [[0, 0, 0, 0, 0], [0, 1, 3, 4, 0], [0, 2, 2, 2, 0], [0, 0, 0, 0, 0]]
        )
        result = pad(input=input, size=size, mode="constant", cval=0)
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray(
            [[9, 9, 9, 9, 9], [9, 1, 3, 4, 9], [9, 2, 2, 2, 9], [9, 9, 9, 9, 9]]
        )
        result = pad(input=input, size=size, mode="constant", cval=9)
        self.assertTrue(numpy.all(result == expected))

    def test_pad_even(self):
        "Test pad for even footprints in 2D"
        input = numpy.asarray([[1, 3, 4], [2, 2, 2]])
        size = (2, 3)

        expected = numpy.asarray([[3, 1, 3, 4, 3], [2, 2, 2, 2, 2], [3, 1, 3, 4, 3]])
        result = pad(input=input, size=size, mode="mirror")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray([[1, 1, 3, 4, 4], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]])
        result = pad(input=input, size=size, mode="reflect")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray([[4, 1, 3, 4, 1], [2, 2, 2, 2, 2], [4, 1, 3, 4, 1]])
        result = pad(input=input, size=size, mode="wrap")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray([[1, 1, 3, 4, 4], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]])
        result = pad(input=input, size=size, mode="nearest")
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray([[0, 1, 3, 4, 0], [0, 2, 2, 2, 0], [0, 0, 0, 0, 0]])
        result = pad(input=input, size=size, mode="constant", cval=0)
        self.assertTrue(numpy.all(result == expected))

        expected = numpy.asarray([[9, 1, 3, 4, 9], [9, 2, 2, 2, 9], [9, 9, 9, 9, 9]])
        result = pad(input=input, size=size, mode="constant", cval=9)
        self.assertTrue(numpy.all(result == expected))


if __name__ == "__main__":
    unittest.main()
