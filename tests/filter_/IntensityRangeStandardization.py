"""Unittest for the IntensityRangeStandardization class."""

# build-in modules
import pickle
import tempfile
import unittest

# third-party modules
import numpy

# own modules
from medpy.filter import (
    InformationLossException,
    IntensityRangeStandardization,
    SingleIntensityAccumulationError,
    UntrainedException,
)

# path changes


# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2013-09-04"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "IntensityRangeStandardization class unittest."

BASE_IMAGE = numpy.asarray([[1, 2, 3], [3, 5, 4], [7, 8, 9], [2, 4, 8]])


# code
class TestIntensityRangeStandardization(unittest.TestCase):
    good_trainingset = [BASE_IMAGE + x for x in range(10)]
    good_image = BASE_IMAGE + 11
    bad_image = BASE_IMAGE + numpy.arange(1, 24, 2).reshape((4, 3))
    uniform_image = numpy.zeros((4, 3))
    single_intensity_image = numpy.asarray(
        [[0, 0, 0], [0, 0, 0], [0, 0, 1000000], [0, 0, 0]]
    )

    def test_ValidInitializationCases(self):
        """Test valid initialization cases."""
        IntensityRangeStandardization()
        IntensityRangeStandardization(landmarkp=IntensityRangeStandardization.L2)
        IntensityRangeStandardization(landmarkp=IntensityRangeStandardization.L3)
        IntensityRangeStandardization(landmarkp=IntensityRangeStandardization.L4)
        IntensityRangeStandardization(landmarkp=(50,))
        IntensityRangeStandardization(landmarkp=[50])
        IntensityRangeStandardization(landmarkp=numpy.asarray([50]))

    def test_InvalidInitializationCases(self):
        """Test invalid initialization cases."""
        cutoffp_testvalues = [
            (-1, 99),
            (101, 99),
            (1, 101),
            (1, -2),
            (40, 40),
            (1,),
            (1, 2, 3),
            (1),
            "123",
            None,
            (None, 100),
        ]
        for cutoffp in cutoffp_testvalues:
            self.assertRaises(
                ValueError, IntensityRangeStandardization, cutoffp=cutoffp
            )

        landmarkp_testvalues = [[], "string", ("50",), (1,), (99,), (-1,), (101,)]
        for landmarkp in landmarkp_testvalues:
            self.assertRaises(
                ValueError,
                IntensityRangeStandardization,
                cutoffp=(1, 99),
                landmarkp=landmarkp,
            )

        stdrange_testvalues = [[], [1], [1, 2, 3], ["a", "b"], [4, 3]]
        for stdrange in stdrange_testvalues:
            self.assertRaises(
                ValueError, IntensityRangeStandardization, stdrange=stdrange
            )

    def test_InvalidUseCases(self):
        """Test invalid use-cases."""
        irs = IntensityRangeStandardization()
        self.assertRaises(
            UntrainedException,
            irs.transform,
            image=TestIntensityRangeStandardization.good_image,
        )

    def test_MethodLimits(self):
        """Test the limits of the method."""
        irs = IntensityRangeStandardization()
        irs.train(TestIntensityRangeStandardization.good_trainingset)
        self.assertRaises(
            InformationLossException,
            irs.transform,
            image=TestIntensityRangeStandardization.bad_image,
        )

        irs = IntensityRangeStandardization()
        irs.train(TestIntensityRangeStandardization.good_trainingset)
        self.assertRaises(
            SingleIntensityAccumulationError,
            irs.transform,
            image=TestIntensityRangeStandardization.uniform_image,
        )

        irs = IntensityRangeStandardization()
        irs.train(TestIntensityRangeStandardization.good_trainingset)
        self.assertRaises(
            SingleIntensityAccumulationError,
            irs.transform,
            image=TestIntensityRangeStandardization.single_intensity_image,
        )

        irs = IntensityRangeStandardization()
        self.assertRaises(
            SingleIntensityAccumulationError,
            irs.train,
            images=[TestIntensityRangeStandardization.uniform_image] * 10,
        )

        irs = IntensityRangeStandardization()
        self.assertRaises(
            SingleIntensityAccumulationError,
            irs.train,
            images=[TestIntensityRangeStandardization.single_intensity_image] * 10,
        )

    def test_Method(self):
        """Test the normal functioning of the method."""
        # test training with good and bad images
        irs = IntensityRangeStandardization()
        irs.train(
            TestIntensityRangeStandardization.good_trainingset
            + [TestIntensityRangeStandardization.bad_image]
        )
        irs.transform(TestIntensityRangeStandardization.bad_image)

        # test equal methods
        irs = IntensityRangeStandardization()
        irs_ = irs.train(TestIntensityRangeStandardization.good_trainingset)
        self.assertEqual(irs, irs_)

        irs = IntensityRangeStandardization()
        irs.train(TestIntensityRangeStandardization.good_trainingset)
        timages = []
        for i in TestIntensityRangeStandardization.good_trainingset:
            timages.append(irs.transform(i))

        irs = IntensityRangeStandardization()
        irs_, timages_ = irs.train_transform(
            TestIntensityRangeStandardization.good_trainingset
        )

        self.assertEqual(
            irs,
            irs_,
            "instance returned by transform() method is not the same as the once initialized",
        )
        for ti, ti_ in zip(timages, timages_):
            numpy.testing.assert_allclose(
                ti,
                ti_,
                err_msg="train_transform() failed to produce the same results as transform()",
            )

        # test pickling
        irs = IntensityRangeStandardization()
        irs_ = irs.train(TestIntensityRangeStandardization.good_trainingset)
        timages = []
        for i in TestIntensityRangeStandardization.good_trainingset:
            timages.append(irs.transform(i))

        with tempfile.TemporaryFile() as f:
            pickle.dump(irs, f)
            f.seek(0, 0)
            irs_ = pickle.load(f)

        timages_ = []
        for i in TestIntensityRangeStandardization.good_trainingset:
            timages_.append(irs_.transform(i))

        for ti, ti_ in zip(timages, timages_):
            numpy.testing.assert_allclose(
                ti, ti_, err_msg="pickling failed to preserve the instances model"
            )


if __name__ == "__main__":
    unittest.main()
