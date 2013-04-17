"""
Unittest for medpy.metric.volume.

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
from medpy.metric import Volume

# code
class TestVolumeClass(unittest.TestCase):
    
    # the size of the test images (_size*_size*_size); do not change! 
    _size = 24
    
    def test_get_volumetric_overlap_error(self):
        i1, i2, i3, i4, i5 = self._createTestImages()
        
        # same image
        v = Volume(i1, i1)
        self.assertEqual(v.get_volumetric_overlap_error(), 0)
        
        # same image with both offsets the same
        v = Volume(i1, i1, [1,2,3], [1,2,3])
        self.assertEqual(v.get_volumetric_overlap_error(), 0)
        
        # same image with different offsets
        v = Volume(i1, i1, [0,0,0], [1,1,1])
        self.assertAlmostEqual(v.get_volumetric_overlap_error(), 37.364705882)
        
        # overlapping image with objects of same volume
        v = Volume(i1, i2)
        self.assertAlmostEqual(v.get_volumetric_overlap_error(), 93.333333333)
        
        # not overlapping image with objects of same volume
        v = Volume(i1, i3)
        self.assertEqual(v.get_volumetric_overlap_error(), 100)
        
        # included object with different volume
        v = Volume(i1, i4)
        self.assertEqual(v.get_volumetric_overlap_error(), 87.5)
        
        # included object with different volume in image of different size
        v = Volume(i1, i5)
        self.assertEqual(v.get_volumetric_overlap_error(), 87.5)
        
        # reversed versions where sensible #
        # same image with different offsets
        v = Volume(i1, i1, [1,1,1], [0,0,0])
        self.assertAlmostEqual(v.get_volumetric_overlap_error(), 37.364705882)
        
        # overlapping image with objects of same volume
        v = Volume(i2, i1)
        self.assertAlmostEqual(v.get_volumetric_overlap_error(), 93.333333333)
        
        # not overlapping image with objects of same volume
        v = Volume(i3, i1)
        self.assertEqual(v.get_volumetric_overlap_error(), 100)
        
        # included object with different volume
        v = Volume(i4, i1)
        self.assertEqual(v.get_volumetric_overlap_error(), 87.5)
        
        # included object with different volume in image of different size
        v = Volume(i5, i1)
        self.assertEqual(v.get_volumetric_overlap_error(), 87.5)

    def test_get_relative_volume_difference(self):
        i1, i2, i3, i4, i5 = self._createTestImages()
        
        # same image
        v = Volume(i1, i1)
        self.assertEqual(v.get_relative_volume_difference(), 0)
        
        # same image with both offsets the same
        v = Volume(i1, i1, [1,2,3], [1,2,3])
        self.assertEqual(v.get_relative_volume_difference(), 0)
        
        # same image with different offsets
        v = Volume(i1, i1, [0,0,0], [1,1,1])
        self.assertEqual(v.get_relative_volume_difference(), 0)
        
        # overlapping image with objects of same volume
        v = Volume(i1, i2)
        self.assertEqual(v.get_relative_volume_difference(), 0)
        
        # not overlapping image with objects of same volume
        v = Volume(i1, i3)
        self.assertEqual(v.get_relative_volume_difference(), 0)
        
        # included object with different volume
        v = Volume(i1, i4)
        self.assertEqual(v.get_relative_volume_difference(), 700)
        
        # included object with different volume in image of different size
        v = Volume(i1, i5)
        self.assertEqual(v.get_relative_volume_difference(), 700)
        
        # included object with different volume / reversed
        v = Volume(i4, i1)
        self.assertEqual(v.get_relative_volume_difference(), -87.5)
        
        # included object with different volume in image of different size / reversed
        v = Volume(i5, i1)
        self.assertEqual(v.get_relative_volume_difference(), -87.5)        
        
    def _createTestImages(self):
        """Creates some images used in the tests."""
        img_1 = scipy.zeros(self._size**3, dtype=int).reshape(self._size,self._size,self._size)
        for i in range(0, self._size/2):
            for j in range(0, self._size/2):
                for k in range(0, self._size/2):
                    img_1[i, j, k] = 1
                    
        img_2 = scipy.zeros(self._size**3, dtype=int).reshape(self._size,self._size,self._size)
        for i in range(self._size/4, 3*self._size/4):
            for j in range(self._size/4, 3*self._size/4):
                for k in range(self._size/4, 3*self._size/4):
                    img_2[i, j, k] = 1
                    
        img_3 = scipy.zeros(self._size**3, dtype=int).reshape(self._size,self._size,self._size)
        for i in range(self._size/2, self._size):
            for j in range(self._size/2, self._size):
                for k in range(self._size/2, self._size):
                    img_3[i, j, k] = 1

        img_4 = scipy.zeros(self._size**3, dtype=int).reshape(self._size,self._size,self._size)
        for i in range(self._size/8, 3*self._size/8):
            for j in range(self._size/8, 3*self._size/8):
                for k in range(self._size/8, 3*self._size/8):
                    img_4[i, j, k] = 1
                    
        img_5 = scipy.zeros((3*self._size/8)**3, dtype=int).reshape(3*self._size/8,3*self._size/8,3*self._size/8)
        for i in range(self._size/8, 3*self._size/8):
            for j in range(self._size/8, 3*self._size/8):
                for k in range(self._size/8, 3*self._size/8):
                    img_5[i, j, k] = 1                    
                    
        return img_1, img_2, img_3, img_4, img_5

if __name__ == '__main__':
    unittest.main()
