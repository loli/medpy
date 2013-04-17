"""
Unittest for medpy.metric.surface.

@author Oskar Maier
@version r0.1.0
@since 2011-12-05
@status Release
"""

# build-in modules
import unittest

# third-party modules
import scipy

# own modules
from medpy.metric import Surface

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
        
        voxels = Surface.compute_contour(self._imagec)
        self.assertTrue((voxels == reference).all())
                         
    def test_get_maximum_symmetric_surface_distance(self):
        # same image
        s = Surface(self._imaged1, self._imaged1)
        self.assertEqual(s.get_maximum_symmetric_surface_distance(), 0.)

        # similar image
        s = Surface(self._imaged1, self._imaged2)
        self.assertAlmostEqual(s.get_maximum_symmetric_surface_distance(), 1.732050808)
        
        # shifted image
        s = Surface(self._imaged1, self._imaged1, (1,1,1), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.get_maximum_symmetric_surface_distance(), 1.732050808)
        
        # shifte image \w non-one physical pixel spacing
        s = Surface(self._imaged1, self._imaged1, (2,2,2), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.get_maximum_symmetric_surface_distance(), 3.464101615)
        
        # different image
        s = Surface(self._imaged1, self._imaged4)
        self.assertAlmostEqual(s.get_maximum_symmetric_surface_distance(), 5.196152423)
        
        # cube images A->B
        s = Surface(self._imagedA, self._imagedB)
        self.assertAlmostEqual(s.get_maximum_symmetric_surface_distance(), 1.73205080757)
        
        # cube images B->A
        s = Surface(self._imagedB, self._imagedA)
        self.assertAlmostEqual(s.get_maximum_symmetric_surface_distance(), 1.73205080757)
        
    def test_get_average_symmetric_surface_distance(self):
        # same image
        s = Surface(self._imaged1, self._imaged1)
        self.assertEqual(s.get_average_symmetric_surface_distance(), 0.)

        # similar image
        s = Surface(self._imaged1, self._imaged2)
        self.assertAlmostEqual(s.get_average_symmetric_surface_distance(), 1.732050808)
        
        # shifted image
        s = Surface(self._imaged1, self._imaged1, (1,1,1), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.get_average_symmetric_surface_distance(), 1.732050808)
        
        # shifte image \w non-one physical pixel spacing
        s = Surface(self._imaged1, self._imaged1, (2,2,2), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.get_average_symmetric_surface_distance(), 3.464101615)
        
        # different image
        s = Surface(self._imaged1, self._imaged4)
        self.assertAlmostEqual(s.get_average_symmetric_surface_distance(), 2.078460969)
        
        # cube images A->B
        s = Surface(self._imagedA, self._imagedB)
        self.assertAlmostEqual(s.get_average_symmetric_surface_distance(), 1.40099885959)
        
        # cube images B->A
        s = Surface(self._imagedB, self._imagedA)
        self.assertAlmostEqual(s.get_average_symmetric_surface_distance(), 1.40099885959)
        
    def test_get_root_mean_square_symmetric_surface_distance(self):
        # same image
        s = Surface(self._imaged1, self._imaged1)
        self.assertEqual(s.get_root_mean_square_symmetric_surface_distance(), 0.)

        # similar image
        s = Surface(self._imaged1, self._imaged2)
        self.assertAlmostEqual(s.get_root_mean_square_symmetric_surface_distance(), 1.732050808)
        
        # shifted image
        s = Surface(self._imaged1, self._imaged1, (1,1,1), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.get_root_mean_square_symmetric_surface_distance(), 1.732050808)
        
        # shifte image \w non-one physical pixel spacing
        s = Surface(self._imaged1, self._imaged1, (2,2,2), (0,0,0), (1,1,1))
        self.assertAlmostEqual(s.get_root_mean_square_symmetric_surface_distance(), 3.464101615)
        
        # different image
        s = Surface(self._imaged1, self._imaged4)
        self.assertAlmostEqual(s.get_root_mean_square_symmetric_surface_distance(), 2.898275349)
        
        # cube images A->B
        s = Surface(self._imagedA, self._imagedB)
        self.assertAlmostEqual(s.get_root_mean_square_symmetric_surface_distance(), 1.4272480643)
        
        # cube images B->A
        s = Surface(self._imagedB, self._imagedA)
        self.assertAlmostEqual(s.get_root_mean_square_symmetric_surface_distance(), 1.4272480643)

if __name__ == '__main__':
    unittest.main()
