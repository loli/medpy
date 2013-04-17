"""
Unittest for medpy.features.texture.

@author Oskar Maier
@version d0.1.0
@since 2012-02-17
@status Development
"""


# build-in modules
import unittest

# third-party modules
import scipy

# own modules
from medpy.features.texture import running_total, efficient_local_avg,\
    running_total3d, efficient_local_avg3d

# code
class TestSurfaceClass(unittest.TestCase):
    
    def test_running_total3d(self):
        """Test the running_total / efficient_local_avg loop for efficient average intensity calculation (3D)."""
        dim = 3
        for size in range(3, 80, 10): # image sizes 3 to 80
            img, q_total, q_div, r_total, r_div = self.__get_test_running_total_data(dim, size)
            rt = running_total3d(img)
            # one voxel region
            res = efficient_local_avg(rt, (scipy.array(img.shape) - 1, scipy.array(img.shape) - 1))
            self.assertEqual(res, img[tuple(scipy.array(img.shape) - 1)]/1., 'Complete image: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, img[tuple(scipy.array(img.shape) - 1)]/1.))
            # complete image
            res = efficient_local_avg(rt, (dim * [0], scipy.array(img.shape) - 1))
            self.assertEqual(res, scipy.sum(img)/float(img.size), 'Complete image: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, scipy.sum(img)/float(img.size)))
            # max quadratic region \wo divider
            res = efficient_local_avg3d(rt, (dim * [1], scipy.array(img.shape) - 1))
            self.assertEqual(res, q_total/q_div, 'Quadratic region: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, q_total/q_div))
            # max quadratic region \w divider
            res = efficient_local_avg3d(rt, (dim * [1], scipy.array(img.shape) - 1), 10.)
            self.assertEqual(res, q_total/10., 'Quadratic region: Calculated average intensity when supplying divider returned unexpected values: got {}, expected {}.'.format(res, q_total/10.))
            # max rectangular region \wo divider
            res = efficient_local_avg3d(rt, ((dim - 1) * [1] + [2], scipy.array(img.shape) - 1))
            self.assertEqual(res, r_total/r_div, 'Rectangular region: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, r_total/r_div))
    
    def test_running_total(self):
        """Test the running_total / efficient_local_avg loop for efficient average intensity calculation."""
        for dim in range(1, 7): # dimension 1 to 6
            for size in range(3, 6): # image sizes 3 to 5
                img, q_total, q_div, r_total, r_div = self.__get_test_running_total_data(dim, size)
                rt = running_total(img)
                # one voxel region
                res = efficient_local_avg(rt, (scipy.array(img.shape) - 1, scipy.array(img.shape) - 1))
                self.assertEqual(res, img[tuple(scipy.array(img.shape) - 1)]/1., 'Complete image: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, img[tuple(scipy.array(img.shape) - 1)]/1.))
                # complete image
                res = efficient_local_avg(rt, (dim * [0], scipy.array(img.shape) - 1))
                self.assertEqual(res, scipy.sum(img)/float(img.size), 'Complete image: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, scipy.sum(img)/float(img.size)))
                # max quadratic region \wo divider
                res = efficient_local_avg(rt, (dim * [1], scipy.array(img.shape) - 1))
                self.assertEqual(res, q_total/q_div, 'Quadratic region: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, q_total/q_div))
                # max quadratic region \w divider
                res = efficient_local_avg(rt, (dim * [1], scipy.array(img.shape) - 1), 10.)
                self.assertEqual(res, q_total/10., 'Quadratic region: Calculated average intensity when supplying divider returned unexpected values: got {}, expected {}.'.format(res, q_total/10.))
                # max rectangular region \wo divider
                res = efficient_local_avg(rt, ((dim - 1) * [1] + [2], scipy.array(img.shape) - 1))
                self.assertEqual(res, r_total/r_div, 'Rectangular region: Calculated average intensity returned unexpected values: got {}, expected {}.'.format(res, r_total/r_div))
                
            
    def __get_test_running_total_data(self, d, s):
        """
        Supply the dimensions the returned quadratic image should have and its seitenlaenge (size).
        @return img, quadr_sum, quadr_divider, rect_sum, rect_div
        """
        if s < 3: raise ValueError('size s must be >= 3')
        base = range(1, s + 1)
        quad = [slice(1, None) for _ in range(d)]
        rect = [slice(1, None) for _ in range(d-1)] + [slice(2, None)]
        #quad = base[1:]
        #rect = base[2:]
        for _ in range(d - 1):
            base = s * [base]
        base = scipy.asarray(base)
        return base, scipy.sum(base[quad]), float(base[quad].size), scipy.sum(base[rect]), float(base[rect].size)
        #return scipy.asarray(base), math.pow(2, d-1) * sum(quad), float(math.pow(s-1, d)), math.pow(2, d-1) * sum(rect), float(math.pow(s-1, d-1) * (s - 2))
        
if __name__ == '__main__':
    unittest.main()