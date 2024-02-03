"""
Unittest for medpy.features.texture.

@author Alexander Ruesch
@version r0.1.0
@since 2012-02-17
@status Development
"""


# build-in modules
import unittest

# third-party modules
import numpy
from scipy import stats

# own modules
from medpy.features.texture import coarseness, contrast, directionality


# code
class TestTextureFeatures(unittest.TestCase):
    """Test the Tamura Texture features programmed in medpy.features.texture.
    Functions are:  coarseness(image, voxelspacing = None, mask = slice(None))
                    contrast(image, mask = slice(None))
                    directionality(image, voxelspacing = None, mask = slice(None), min_distance = 4)
    """

    def setUp(self):
        self.image1 = numpy.zeros([100, 100])
        self.image1[:, ::3] = 1
        self.voxelspacing1 = (1.0, 3.0)
        self.mask1 = tuple([slice(0, 50, 1), slice(0, 50, 1)])

    def test_Coarseness(self):
        res = coarseness(self.image1)
        self.assertEqual(
            res,
            1.33,
            "coarseness: 2D image [1,0,0...], no voxelspacing, no mask: got {} ,expected {}".format(
                res, 1.33
            ),
        )

        res = coarseness(self.image1, voxelspacing=self.voxelspacing1)
        self.assertEqual(
            res,
            1.0,
            "coarseness: 2D image [1,0,0...], voxelspacing = (1,3), no mask: got {} ,expected {}".format(
                res, 1.0
            ),
        )
        # @TODO: there is a very strong relation to the border handle if the texture is very small (1px)
        res = coarseness(self.image1, voxelspacing=self.voxelspacing1, mask=self.mask1)
        self.assertEqual(
            res,
            76.26,
            "coarseness: 2D image [1,0,0...], voxelspacing = (1,3), mask = [slice(0,50,1),slice(0,50,1)]: got {} ,expected {}".format(
                res, 76.26
            ),
        )

        res = coarseness(numpy.zeros([100, 100]))
        self.assertEqual(
            res,
            1.0,
            "coarseness: 2D image [0,0,0,...], no voxelspacing, no mask: got {} ,expected {}".format(
                res, 1.0
            ),
        )

        res = coarseness(self.image1, voxelspacing=(1, 2, 3))
        self.assertEqual(
            res,
            None,
            "coarseness: 2D image [1,0,0,...], voxelspacing = (1,2,3), no mask: got {} ,expected {} ".format(
                res, None
            ),
        )

    def test_Contrast(self):
        standard_deviation = numpy.std(self.image1)
        kurtosis = stats.kurtosis(self.image1, axis=None, bias=True, fisher=False)
        Fcon1 = standard_deviation / (kurtosis**0.25)

        res = contrast(self.image1)
        self.assertEqual(
            res,
            Fcon1,
            "contrast: 2D image, no mask: got {} ,expected {}".format(res, Fcon1),
        )

        image2 = self.image1[0:50, 0:50]
        standard_deviation = numpy.std(image2)
        kurtosis = stats.kurtosis(image2, axis=None, bias=True, fisher=False)
        Fcon2 = standard_deviation / (kurtosis**0.25)

        res = contrast(self.image1, mask=self.mask1)
        self.assertEqual(
            res,
            Fcon2,
            "contrast: 2D image, mask = [slice(0,50,1), slice(0,50,1)]: got {} ,expected {}".format(
                res, Fcon2
            ),
        )

    def test_Directionality(self):
        res = directionality(self.image1)
        self.assertEqual(
            res,
            1.0,
            "directionality: 2D image, no voxelspacing, no mask, default min_distance, default threshold: got {} ,expected {}".format(
                res, 1.0
            ),
        )

        res = directionality(self.image1, voxelspacing=self.voxelspacing1)
        self.assertEqual(
            res,
            1.0,
            "directionality: 2D image, voxelspacing = (1.0, 3.0), no mask, default min_distance, default threshold: got {} ,expected {}".format(
                res, 1.0
            ),
        )

        res = directionality(self.image1, voxelspacing=(1, 2, 3))
        self.assertEqual(
            res,
            None,
            "directionality: 2D image, voxelspacing = (1,2,3), no mask, default min_distance, default threshold: got {} ,expected {}".format(
                res, None
            ),
        )

        res = directionality(
            self.image1, voxelspacing=self.voxelspacing1, mask=self.mask1
        )
        self.assertEqual(
            res,
            1.0,
            "directionality: 2D image, voxelspacing(1.0, 3.0), mask = [slice(0,50,1), slice(0,50,1)], default min_distance, default threshold: got {} ,expected {}".format(
                res, 1.0
            ),
        )

        res = directionality(self.image1, min_distance=10)
        self.assertEqual(
            res,
            1.0,
            "directionality: 2D image, no voxelspacing, no mask , min_distance= 10, default threshold: got {} ,expected {}".format(
                res, 1.0
            ),
        )

        res = directionality(self.image1, threshold=0.5)
        self.assertEqual(
            res,
            1.0,
            "directionality: 2D image, no voxelspacing, no mask, default min_distance, threshold = 0.5: got {} ,expected {}".format(
                res, 1.0
            ),
        )


if __name__ == "__main__":
    unittest.main()
