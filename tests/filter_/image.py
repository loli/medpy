"""
Unittest for medpy.filter.image

@author Oskar Maier
@version r0.1.0
@since 2013-12-04
@status Release
"""

# build-in modules
import unittest

# third-party modules
import numpy
from scipy.ndimage import gaussian_filter

# own modules
from medpy.filter.image import average_filter, sls, ssd, sum_filter


# code
class TestMetrics(unittest.TestCase):
    def setUp(self):
        pass

    def test_sls(self):
        m = numpy.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        s = numpy.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])
        sn_fp = numpy.array([[0, 1, 0], [1, 1, 0]])
        pn_fp = numpy.array([[1, 0], [1, 0], [0, 1]])

        # reflect
        patches = [
            numpy.array([[18, 33, 43], [46, 69, 83], [70, 101, 123]]),
            numpy.array([[43, 54, 68], [59, 70, 88], [75, 86, 108]]),
            numpy.array([[54, 81, 99], [70, 101, 123], [86, 121, 147]]),
        ]
        patches = [patch / 3.0 for patch in patches]
        noise = gaussian_filter(numpy.average(patches, 0), sigma=3)
        e = [-1 * numpy.exp(-1 * patch / noise) for patch in patches]
        e = numpy.rollaxis(numpy.asarray(e), 0, e[0].ndim + 1)
        r = sls(
            m, s, sn_footprint=sn_fp, pn_footprint=pn_fp, noise="local", signed=True
        )
        numpy.testing.assert_allclose(r, e)

        e *= -1
        r = sls(
            m,
            -1 * s,
            sn_footprint=sn_fp,
            pn_footprint=pn_fp,
            noise="local",
            signed=True,
        )
        numpy.testing.assert_allclose(r, e)

        r = sls(
            m, s, sn_footprint=sn_fp, pn_footprint=pn_fp, noise="local", signed=False
        )
        numpy.testing.assert_allclose(r, e)

        r = sls(
            m,
            -1 * s,
            sn_footprint=sn_fp,
            pn_footprint=pn_fp,
            noise="local",
            signed=False,
        )
        numpy.testing.assert_allclose(r, e)

        noise = noise.sum() / 9.0
        e = [-1 * numpy.exp(-1 * patch / noise) for patch in patches]
        e = numpy.rollaxis(numpy.asarray(e), 0, e[0].ndim + 1)
        r = sls(
            m, s, sn_footprint=sn_fp, pn_footprint=pn_fp, noise="global", signed=True
        )
        numpy.testing.assert_allclose(r, e)

    def test_ssd(self):
        m = numpy.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        s = numpy.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])

        e = numpy.array([[1, 4, 9], [9, 16, 25], [25, 36, 49]])
        r, sgn = ssd(m, s, normalized=False, signed=False, size=1)
        self.assertEqual(sgn, 1, "signed=False failed to return scalar 1")
        numpy.testing.assert_allclose(r, e)

        esgn = numpy.array([[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]])
        r, sgn = ssd(m, s, normalized=False, signed=True, size=1)
        numpy.testing.assert_allclose(sgn, esgn, err_msg="signed=True failed")
        numpy.testing.assert_allclose(r, e)

        esgn = numpy.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        r, sgn = ssd(s, m, normalized=False, signed=True, size=1)
        numpy.testing.assert_allclose(sgn, esgn, err_msg="signed=True failed")
        numpy.testing.assert_allclose(r, e)

        r, _ = ssd(m, s, normalized=True, signed=False, size=1)
        numpy.testing.assert_allclose(r, e, err_msg="normalized=True failed")

        fp = numpy.array([[1, 0], [1, 0], [0, 1]])
        e = numpy.array([[26, 45, 50], [46, 69, 70], [50, 77, 90]])
        r, _ = ssd(m, s, normalized=False, signed=False, footprint=fp, mode="mirror")
        numpy.testing.assert_allclose(r, e, err_msg="using footprint failed")

        e = e / 3.0
        r, _ = ssd(m, s, normalized=True, signed=False, footprint=fp, mode="mirror")
        numpy.testing.assert_allclose(
            r, e, err_msg="normalized=True using footprint failed"
        )

    def test_average_filter(self):
        i = numpy.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])

        fp = numpy.array([[1, 1]])
        e = numpy.array([[3, 5, 3], [7, 9, 5], [11, 13, 7]])
        r = average_filter(i, footprint=fp, mode="constant", cval=0, output=float)
        numpy.testing.assert_allclose(r, e / 2.0)

        r = average_filter(i, footprint=fp, mode="constant", cval=0, output=int)
        numpy.testing.assert_allclose(r, e / 2)

        r = average_filter(i, footprint=fp, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e / 2)

        fp = numpy.array([[1, 0], [1, 0], [0, 1]])
        e = numpy.array([[5, 7, 3], [10, 13, 8], [8, 10, 12]])
        r = average_filter(i, footprint=fp, mode="constant", cval=0, output=float)
        numpy.testing.assert_allclose(r, e / 3.0)

        i = numpy.array([[1, 3, 4], [2, 2, 2]])
        fp = numpy.array([[1, 0, 1]])
        e = numpy.array([[6, 5, 6], [4, 4, 4]])
        r = average_filter(i, footprint=fp, mode="mirror", output=float)
        numpy.testing.assert_allclose(r, e / 2.0)

        e = numpy.array([[4, 5, 7], [4, 4, 4]])
        r = average_filter(i, footprint=fp, mode="reflect", output=float)
        numpy.testing.assert_allclose(r, e / 2.0)

    def test_sum_filter(self):
        i = numpy.array([[1, 2, 3], [3, 4, 5], [5, 6, 7]])

        # test reaction to size parameter
        r = sum_filter(i, size=1)
        numpy.testing.assert_allclose(r, i)

        e = numpy.array([[10, 14, 8], [18, 22, 12], [11, 13, 7]])
        r = sum_filter(i, size=2, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        e = numpy.array([[10, 18, 14], [21, 36, 27], [18, 30, 22]])
        r = sum_filter(i, size=3, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        e = numpy.array([[36, 36, 36], [36, 36, 36], [36, 36, 36]])
        r = sum_filter(i, size=5, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        r = sum_filter(i, size=10, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        # test reaction to footprint parameter
        fp = numpy.array([[1]])
        r = sum_filter(i, footprint=fp)
        numpy.testing.assert_allclose(r, i)

        fp = numpy.array([[1, 1], [1, 1]])
        e = numpy.array([[10, 14, 8], [18, 22, 12], [11, 13, 7]])
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        fp = numpy.array([[1, 1]])
        e = numpy.array([[3, 5, 3], [7, 9, 5], [11, 13, 7]])
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        fp = numpy.array([[1], [1]])
        e = numpy.array([[4, 6, 8], [8, 10, 12], [5, 6, 7]])
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        fp = numpy.array([[1, 0], [1, 0], [0, 1]])
        e = numpy.array([[5, 7, 3], [10, 13, 8], [8, 10, 12]])
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        fp = numpy.array([[1, 0], [0, 1], [0, 1]])
        e = numpy.array([[6, 8, 0], [11, 14, 3], [9, 11, 5]])
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        numpy.testing.assert_allclose(r, e)

        # test border treatment modes
        i = numpy.array([[1, 3, 4], [2, 2, 2]])
        fp = numpy.array([[1, 0, 1]])

        e = 6
        r = sum_filter(i, footprint=fp, mode="mirror")
        self.assertAlmostEqual(r[0, 0], e, msg="mirror mode failed")

        e = 4
        r = sum_filter(i, footprint=fp, mode="reflect")
        self.assertAlmostEqual(r[0, 0], e, msg="reflect mode failed")

        e = 7
        r = sum_filter(i, footprint=fp, mode="wrap")
        self.assertAlmostEqual(r[0, 0], e, msg="wrap mode failed")

        e = 4
        r = sum_filter(i, footprint=fp, mode="nearest")
        self.assertAlmostEqual(r[0, 0], e, msg="nearest mode failed")

        e = 3
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        self.assertAlmostEqual(r[0, 0], e, msg="constant mode failed")

        e = 12
        r = sum_filter(i, footprint=fp, mode="constant", cval=9)
        self.assertAlmostEqual(r[0, 0], e, msg="constant mode failed")

        fp = numpy.array([[1, 0, 0], [0, 0, 0]])

        e = 3
        r = sum_filter(i, footprint=fp, mode="mirror")
        self.assertAlmostEqual(r[0, 0], e, msg="mirror mode failed")

        e = 1
        r = sum_filter(i, footprint=fp, mode="reflect")
        self.assertAlmostEqual(r[0, 0], e, msg="reflect mode failed")

        e = 4
        r = sum_filter(i, footprint=fp, mode="wrap")
        self.assertAlmostEqual(r[0, 0], e, msg="wrap mode failed")

        e = 1
        r = sum_filter(i, footprint=fp, mode="nearest")
        self.assertAlmostEqual(r[0, 0], e, msg="nearest mode failed")

        e = 0
        r = sum_filter(i, footprint=fp, mode="constant", cval=0)
        self.assertAlmostEqual(r[0, 0], e, msg="constant mode failed")

        e = 9
        r = sum_filter(i, footprint=fp, mode="constant", cval=9)
        self.assertAlmostEqual(r[0, 0], e, msg="constant mode failed")


if __name__ == "__main__":
    unittest.main()
