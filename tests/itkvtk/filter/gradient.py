"""Unittest for the itkvtk gradient filters."""

# build-in modules
import unittest

# third-party modules
import scipy

# path changes

# own modules
from medpy.itkvtk.filter import gradient_magnitude

# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-06-01"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Itkvtk gradient filter unittest."

# code
class TestItkVtkGradient(unittest.TestCase):
    
    def test_gradient_magnitude(self):
        """
        Test if the gradient magnitude filter produces the same results, independent from
        the dtype of the input array.
        """
        dtypes = [scipy.int8, scipy.int16, scipy.int32, scipy.int64,
                  scipy.uint8, scipy.uint16, scipy.uint32, scipy.uint64,
                  scipy.float32, scipy.float64, scipy.float128]
        
        arr_base = scipy.random.randint(0, 100, (20, 30, 40, 50))
        arr_reference = gradient_magnitude(arr_base)
        
        # test different dtypes
        for dtype in dtypes:
            arr = gradient_magnitude(arr_base.astype(dtype))
            self.assertTrue((arr == arr_reference).all(), 'Difference for dtype {} encountered.'.format(dtype))
            
        # test if voxel spacing is taken into account
        arr = gradient_magnitude(arr_base, [1.1, 1.2, 1.3, 4])
        self.assertFalse((arr == arr_reference).all(), 'Implementation ignores the passed voxel spacing.')
            
    
if __name__ == '__main__':
    unittest.main()            
        