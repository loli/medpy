"""Unittest for the surface metrics class."""

# build-in modules
import unittest

# third-party modules
import scipy

# path changes

# own modules
from medpy.metric import Surface

# information
__author__ = "Oskar Maier"
__version__ = "0.1, 2011-12-05"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = "Surface metric class unittest."

# code
class TestSurfaceClass(unittest.TestCase):
    
    def setUp(self):
        # !TODO: This is ran before each test case!
        # Define input images for the distance tests
        self._imaged1 = scipy.zeros(8, dtype=bool).reshape(2,2,2)
        self._imaged1[0,0,0] = True # 2x2x2 image with pixel in near corner
        self._imaged2 = scipy.zeros(8, dtype=bool).reshape(2,2,2)
        self._imaged2[1,1,1] = True # 2x2x2 image with pixel in far corner
        self._imaged3 = scipy.zeros(8, dtype=bool).reshape(2,2,2) # 2x2x2 image \wo object
        self._imaged4 = scipy.zeros(64, dtype=bool).reshape(4,4,4)
        self._imaged4[0,0,0] = True
        self._imaged4[1,1,1] = True
        self._imaged4[2,2,2] = True
        self._imaged4[3,3,3] = True # 4x4x4 image with pixels at the diagonal
        
        # two images, first a cube with a whole, not touching the borders and
        # second single pixel in the middle, exactely filling the whole
        self._imagedA = scipy.zeros(5*5*5, dtype=bool).reshape(5, 5, 5) 
        self._imagedA[1:4,1:4,1:4] = True
        self._imagedA[2:3,2:3,2:3] = False
        self._imagedB = scipy.zeros(5*5*5, dtype=bool).reshape(5, 5, 5)
        self._imagedB[2:3,2:3,2:3] = True
        
        # Define input image for the contour test
        self._imagec = scipy.zeros(64, dtype=bool).reshape(4,4,4)
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    self._imagec[i,j,k] = True    

    def test_Initialization(self):
        #self.assertRaises(Exception, Surface(self._imaged1, self._imaged3))
        pass

    def test_ComputeContour(self):
        reference = self._imagec.copy()
        reference[1,1,1] = False
        
        voxels = Surface.ComputeContour(self._imagec)
        self.assertTrue((voxels == reference).all())
                         
    def test_GetMaximumSymmetricSurfaceDistance(self):
        # same image
        s = Surface(self._imaged1, self._imaged1)
        self.assertEqual(s.GetMaximumSymmetricSurfaceDistance(), 0.)

        # similar image
        s = Surface(self._imaged1, self._imaged2)
        self.assertAlmostEqual(s.GetMaximumSymmetricSurfaceDistance(), 1.732050808)
        
        # shifted image
        s = Surface(self._imaged1, self._imaged1, (1,1,1), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.GetMaximumSymmetricSurfaceDistance(), 1.732050808)
        
        # shifte image \w non-one physical pixel spacing
        s = Surface(self._imaged1, self._imaged1, (2,2,2), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.GetMaximumSymmetricSurfaceDistance(), 3.464101615)
        
        # different image
        s = Surface(self._imaged1, self._imaged4)
        self.assertAlmostEqual(s.GetMaximumSymmetricSurfaceDistance(), 5.196152423)
        
        # cube images A->B
        s = Surface(self._imagedA, self._imagedB)
        self.assertAlmostEqual(s.GetMaximumSymmetricSurfaceDistance(), 1.73205080757)
        
        # cube images B->A
        s = Surface(self._imagedB, self._imagedA)
        self.assertAlmostEqual(s.GetMaximumSymmetricSurfaceDistance(), 1.73205080757)
        
    def test_GetAverageSymmetricSurfaceDistance(self):
        # same image
        s = Surface(self._imaged1, self._imaged1)
        self.assertEqual(s.GetAverageSymmetricSurfaceDistance(), 0.)

        # similar image
        s = Surface(self._imaged1, self._imaged2)
        self.assertAlmostEqual(s.GetAverageSymmetricSurfaceDistance(), 1.732050808)
        
        # shifted image
        s = Surface(self._imaged1, self._imaged1, (1,1,1), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.GetAverageSymmetricSurfaceDistance(), 1.732050808)
        
        # shifte image \w non-one physical pixel spacing
        s = Surface(self._imaged1, self._imaged1, (2,2,2), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.GetAverageSymmetricSurfaceDistance(), 3.464101615)
        
        # different image
        s = Surface(self._imaged1, self._imaged4)
        self.assertAlmostEqual(s.GetAverageSymmetricSurfaceDistance(), 2.078460969)
        
        # cube images A->B
        s = Surface(self._imagedA, self._imagedB)
        self.assertAlmostEqual(s.GetAverageSymmetricSurfaceDistance(), 1.40099885959)
        
        # cube images B->A
        s = Surface(self._imagedB, self._imagedA)
        self.assertAlmostEqual(s.GetAverageSymmetricSurfaceDistance(), 1.40099885959)
        
    def test_GetRootMeanSquareSymmetricSurfaceDistance(self):
        # same image
        s = Surface(self._imaged1, self._imaged1)
        self.assertEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 0.)

        # similar image
        s = Surface(self._imaged1, self._imaged2)
        self.assertAlmostEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 1.732050808)
        
        # shifted image
        s = Surface(self._imaged1, self._imaged1, (1,1,1), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 1.732050808)
        
        # shifte image \w non-one physical pixel spacing
        s = Surface(self._imaged1, self._imaged1, (2,2,2), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 3.464101615)
        
        # different image
        s = Surface(self._imaged1, self._imaged4)
        self.assertAlmostEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 2.898275349)
        
        # cube images A->B
        s = Surface(self._imagedA, self._imagedB)
        self.assertAlmostEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 1.4272480643)
        
        # cube images B->A
        s = Surface(self._imagedB, self._imagedA)
        self.assertAlmostEqual(s.GetRootMeanSquareSymmetricSurfaceDistance(), 1.4272480643)

if __name__ == '__main__':
    unittest.main()
