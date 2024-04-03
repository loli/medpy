"""
Unittest for medpy.features.histogram.

@author Oskar Maier
@version r0.1.1
@since 2012-03-05
@status Release
"""

# build-in modules
import math
import unittest

# third-party modules
import numpy

# own modules
from medpy.features.histogram import (
    fuzzy_histogram,
    gaussian_membership,
    sigmoidal_difference_membership,
    trapezoid_membership,
    triangular_membership,
)


# code
class TestHistogramFeatures(unittest.TestCase):
    def test_fuzzy_histogram_contribution(self):
        """Test if all values contribute with nearly one to the created histograms."""
        values = numpy.random.randint(0, 100, 1000)

        # test triangular
        h, _ = fuzzy_histogram(
            values, membership="triangular", normed=False, guarantee=True
        )
        self.assertAlmostEqual(
            sum(h),
            values.size,
            msg="Triangular contribution does not equal out. {} != {}.".format(
                sum(h), values.size
            ),
        )

        # test trapezoid
        h, _ = fuzzy_histogram(
            values, membership="trapezoid", normed=False, guarantee=True
        )
        self.assertAlmostEqual(
            sum(h),
            values.size,
            msg="Trapezoid contribution does not equal out. {} != {}.".format(
                sum(h), values.size
            ),
        )

        # test gaussian
        h, _ = fuzzy_histogram(
            values, membership="gaussian", normed=False, guarantee=True
        )
        self.assertAlmostEqual(
            sum(h),
            values.size,
            msg="Gaussian contribution does not equal out. {} != {}.".format(
                sum(h), values.size
            ),
            delta=values.size * 0.001,
        )  # gaussian maximal error eps

        # test sigmoid
        h, _ = fuzzy_histogram(
            values, membership="sigmoid", normed=False, guarantee=True
        )
        self.assertAlmostEqual(
            sum(h),
            values.size,
            msg="Sigmoid contribution does not equal out. {} != {}.".format(
                sum(h), values.size
            ),
            delta=values.size * 0.001,
        )  # sigmoidal maximal error eps

    def test_triangular_membership_contribution(self):
        """Tests if all values contribute equally using the triangular membership function."""
        contribution = 1.0

        for smoothness in [0.5]:
            for bin_width in [0.5, 1, 1.5, 10]:
                mbs = []
                for bin_idx in range(
                    -int(math.ceil(smoothness)), int(math.ceil(smoothness)) + 1
                ):
                    mbs.append(
                        triangular_membership(
                            bin_idx * bin_width, bin_width, smoothness
                        )
                    )
                value = -0.5 * bin_width
                for _ in range(1, 11):
                    result = 0
                    for bin_idx in range(len(mbs)):
                        result += mbs[bin_idx](value)
                    self.assertAlmostEqual(
                        contribution,
                        result,
                        msg="invalid contribution of {} instead of expected {}".format(
                            result, contribution
                        ),
                    )
                    value += 1.0 / 10 * bin_width

    def test_trapezoid_membership_contribution(self):
        """Tests if all values contribute equally using the trapezoid membership function."""
        contribution = 1.0

        for smoothness in [0.1, 0.2, 0.3, 0.4, 0.49]:
            for bin_width in [0.5, 1, 1.5, 10]:
                mbs = []
                for bin_idx in range(
                    -int(math.ceil(smoothness)), int(math.ceil(smoothness)) + 1
                ):
                    mbs.append(
                        trapezoid_membership(bin_idx * bin_width, bin_width, smoothness)
                    )
                value = -0.5 * bin_width
                for _ in range(1, 11):
                    result = 0
                    for bin_idx in range(len(mbs)):
                        result += mbs[bin_idx](value)
                    self.assertAlmostEqual(
                        contribution,
                        result,
                        msg="invalid contribution of {} instead of expected {}".format(
                            result, contribution
                        ),
                    )
                    value += 1.0 / 10 * bin_width

    def test_gaussian_membership_contribution(self):
        """Tests if all values contribute equally using the gaussian membership function."""
        contribution = 1.0
        eps = 0.001  # maximal error per value

        for smoothness in [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            1,
            2,
            2.51,
            3,
            4,
            5,
            6,
            7,
            7.49,
            8,
            9,
            10,
        ]:
            for bin_width in [0.5, 1, 1.5, 10]:
                mbs = []
                for bin_idx in range(
                    -int(math.ceil(smoothness)), int(math.ceil(smoothness)) + 1
                ):
                    mbs.append(
                        gaussian_membership(bin_idx * bin_width, bin_width, smoothness)
                    )
                value = -0.5 * bin_width
                for _ in range(1, 11):
                    result = 0
                    for bin_idx in range(len(mbs)):
                        result += mbs[bin_idx](value)
                    self.assertAlmostEqual(
                        contribution,
                        result,
                        delta=eps,
                        msg="invalid contribution of {} instead of expected {}".format(
                            result, contribution
                        ),
                    )
                    value += 1.0 / 10 * bin_width

    def test_sigmoidal_difference_membership_contribution(self):
        """Tests if all values contribute equally using the gaussian membership function."""
        contribution = 1.0
        eps = 0.001  # maximal error per value

        for smoothness in [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            1,
            2,
            2.51,
            3,
            4,
            5,
            6,
            7,
            7.49,
            8,
            9,
            10,
        ]:
            for bin_width in [0.5, 1, 1.5, 10]:
                mbs = []
                for bin_idx in range(
                    -int(math.ceil(smoothness)), int(math.ceil(smoothness)) + 1
                ):
                    mbs.append(
                        sigmoidal_difference_membership(
                            bin_idx * bin_width, bin_width, smoothness
                        )
                    )
                value = -0.5 * bin_width
                for _ in range(1, 11):
                    result = 0
                    for bin_idx in range(len(mbs)):
                        result += mbs[bin_idx](value)
                    self.assertAlmostEqual(
                        contribution,
                        result,
                        delta=eps,
                        msg="invalid contribution of {} instead of expected {}".format(
                            result, contribution
                        ),
                    )
                    value += 1.0 / 10 * bin_width

    def test_fuzzy_histogram_std_behaviour(self):
        """Test the standard behaviour of fuzzy histogram."""
        values = numpy.random.randint(0, 10, 100)

        _, b = fuzzy_histogram(values, bins=12)
        self.assertEqual(len(b), 13, "violation of requested histogram size.")
        self.assertEqual(b[0], values.min(), "invalid lower histogram border.")
        self.assertEqual(b[-1], values.max(), "invalid upper histogram border.")

        h, _ = fuzzy_histogram(values, normed=True)
        self.assertAlmostEqual(sum(h), 1.0, msg="histogram not normed.")

        _, b = fuzzy_histogram(values, bins=12, guarantee=True)
        self.assertEqual(
            len(b),
            13,
            "violation of requested histogram size with guarantee set to True.",
        )

        _, b = fuzzy_histogram(values, range=(-5, 5))
        self.assertEqual(b[0], -5.0, "violation of requested ranges lower bound.")
        self.assertEqual(b[-1], 5.0, "violation of requested ranges lower bound.")

    def test_fuzzy_histogram_parameters(self):
        values = numpy.random.randint(0, 10, 100)

        # membership functions
        fuzzy_histogram(values, membership="triangular")
        fuzzy_histogram(values, membership="trapezoid")
        fuzzy_histogram(values, membership="gaussian")
        fuzzy_histogram(values, membership="sigmoid")

        # int/float
        fuzzy_histogram(values, range=(0, 10))  # int in range
        fuzzy_histogram(values, range=(0.0, 10.0))  # float in range
        fuzzy_histogram(values, bins=10)  # int in bins
        fuzzy_histogram(values, membership="sigmoid", smoothness=1)  # int in smoothness
        fuzzy_histogram(
            values, membership="sigmoid", smoothness=1.0
        )  # float in smoothness

    def test_fuzzy_histogram_exceptions(self):
        values = numpy.random.randint(0, 10, 100)

        # test fuzzy histogram exceptions
        self.assertRaises(AttributeError, fuzzy_histogram, values, range=(0, 0))
        self.assertRaises(AttributeError, fuzzy_histogram, values, range=(0, -1))
        self.assertRaises(AttributeError, fuzzy_histogram, values, bins=0)
        self.assertRaises(AttributeError, fuzzy_histogram, values, bins=-1)
        self.assertRaises(AttributeError, fuzzy_histogram, values, bins=0.5)
        self.assertRaises(AttributeError, fuzzy_histogram, values, membership="")
        self.assertRaises(AttributeError, fuzzy_histogram, values, membership="x")
        self.assertRaises(AttributeError, fuzzy_histogram, values, membership=True)
        self.assertRaises(AttributeError, fuzzy_histogram, values, membership=None)
        self.assertRaises(AttributeError, fuzzy_histogram, values, smoothness=-1.0)
        self.assertRaises(AttributeError, fuzzy_histogram, values, smoothness=-1)
        self.assertRaises(AttributeError, fuzzy_histogram, values, smoothness=-1.0)
        self.assertRaises(AttributeError, fuzzy_histogram, values, smoothness=-1)

        # test triangular and trapezium exceptions
        self.assertRaises(
            AttributeError,
            fuzzy_histogram,
            values,
            membership="triangular",
            smoothness=0.51,
        )
        self.assertRaises(
            AttributeError,
            fuzzy_histogram,
            values,
            membership="trapezoid",
            smoothness=0.51,
        )
        self.assertRaises(
            AttributeError,
            fuzzy_histogram,
            values,
            membership="trapezoid",
            smoothness=0.09,
        )

        # test gaussian exceptions
        self.assertRaises(
            AttributeError,
            fuzzy_histogram,
            values,
            membership="gaussian",
            smoothness=1.0 / 11,
        )
        self.assertRaises(
            AttributeError,
            fuzzy_histogram,
            values,
            membership="gaussian",
            smoothness=11,
        )

        # test sigmoidal exceptions
        self.assertRaises(
            AttributeError,
            fuzzy_histogram,
            values,
            membership="sigmoid",
            smoothness=1.0 / 11,
        )
        self.assertRaises(
            AttributeError, fuzzy_histogram, values, membership="sigmoid", smoothness=11
        )


if __name__ == "__main__":
    unittest.main()
