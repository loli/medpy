"""
Unittest for medpy.features.intensity.

@author Oskar Maier
@version d0.1.1
@since 2013-08-26
@status Development
"""


# build-in modules
import unittest
import math

# third-party modules
import numpy

# own modules
from medpy.features.intensity import intensities, centerdistance,\
    centerdistance_xdminus1, indices, local_mean_gauss, local_histogram
from medpy.features.utilities import join, append
from medpy.core.exceptions import ArgumentError

# code
class TestIntensityFeatures(unittest.TestCase):
    
    def test_local_histogram(self):
        """Test the feature: local_histogram."""
        
        i = numpy.asarray([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]])
        e = numpy.asarray([[5/9., 4/9.], [3/9., 6/9.], [5/9., 4/9.],\
                           [3/9., 6/9.], [0.,   1.  ], [3/9., 6/9.],\
                           [5/9., 4/9.], [3/9., 6/9.], [5/9., 4/9.]])
        r = local_histogram(i, size = 3, bins = 2, rang = None, cutoffp = (0, 100), cval = 0, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 2D local range failed')
        
        m = [[False, False, False],
             [False, True, False],
             [False, False, False]]
        e = [0, 1] 
        r = local_histogram(i, size = 3, bins = 2, rang = None, cutoffp = (0, 100), cval = 0, mask = m)
        self.assertEqual(len(r), 1, 'local histogram: 2D masked failed')
        numpy.testing.assert_allclose(r[0], e, err_msg = 'local histogram: 2D local range masked failed')
        
        e = numpy.asarray([(0, 1)] * 9)
        r = local_histogram(i, size = 3, bins = 2, rang = None, cutoffp = (0, 100), cval = 1, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 2D local range with cval=1 failed')
        
        e = numpy.asarray([(0, 1)] * 9)
        r = local_histogram(i, size = 3, bins = 2, rang = 'image', cutoffp = (0, 100), cval = 0, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 2D range over complete image failed')
        
        i = numpy.asarray([[2, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]])
        e = numpy.asarray([(1, 0)] * 9)
        r = local_histogram(i, size = 3, bins = 2, rang = 'image', cutoffp = (1, 99), cval = 0, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 2D rang over complete image \w cutoffp failed')
        
        e = numpy.asarray([[5/8., 3/8.], [3/8., 5/8.], [5/9., 4/9.],\
                           [3/8., 5/8.], [0.,   1.  ], [3/9., 6/9.],\
                           [5/9., 4/9.], [3/9., 6/9.], [5/9., 4/9.]])
        r = local_histogram(i, size = 3, bins = 2, rang = (0, 1.9), cutoffp = (1, 99), cval = 0, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 2D rang supplied failed')
        
        i = numpy.asarray([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]])
        i = numpy.asarray([i, i, i])
        e = numpy.asarray([(0, 1)] * (9 * 3))
        r = local_histogram(i, size = 3, bins = 2, rang = None, cutoffp = (0, 100), cval = 1, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 3D local range with cval=1 failed')
        
        i = numpy.asarray([i, i, i])
        e = numpy.asarray([(0, 1)] * (9 * 3 * 3))
        r = local_histogram(i, size = 3, bins = 2, rang = None, cutoffp = (0, 100), cval = 1, mask = slice(None))
        numpy.testing.assert_allclose(r, e, err_msg = 'local histogram: 4D local range with cval=1 failed')   
        
    
    def test_local_mean_gauss(self):
        """Test the feature: local_mean_gauss."""

        # 2D to zero case
        i = numpy.asarray([[0, 1, 2],
                           [1, 2, 3],
                           [2, 3, 4]])
        e = [0, 1, 1,\
             1, 2, 2,\
             1, 2, 2]
        r = local_mean_gauss(i, 1)
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 2D failed')

        # 2D to zero case
        i = numpy.asarray([[0, 1],
                           [1, 0]])
        e = [0, 0,\
             0, 0]
        r = local_mean_gauss(i, 1)
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 2D to zero failed')
        
        # 2D zero case        
        i = numpy.asarray([[0, 0],
                           [0, 0]])
        r = local_mean_gauss(i, 1)
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 2D zero case failed')
        
        # 2D different axes
        i = numpy.asarray([[0, 0, 0, 1],
                           [0, 0, 1, 2],
                           [0, 1, 2, 3],
                           [1, 2, 3, 4]])
        e = [0, 0, 0, 0,\
             0, 0, 1, 1,\
             0, 0, 1, 1,\
             0, 1, 1, 2]
        r = local_mean_gauss(i, (1, 0.5))
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 2D different axes failed')
        
        # 2D voxelspacing
        r = local_mean_gauss(i, 1, voxelspacing = [1., 2.])
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 2D voxelspacing failed')

        # 3D with 2D kernel
        i = numpy.asarray([i, i])
        e = numpy.asarray([e, e]).ravel()
        r = local_mean_gauss(i, (0, 1, 0.5))
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 3D with 2D kernel failed')
        
        # 3D
        e = numpy.asarray([[[0, 0, 0, 1],
                            [0, 0, 0, 1],
                            [0, 0, 0, 1],
                            [0, 0, 1, 1]],
                           [[0, 0, 0, 1],
                            [0, 0, 0, 1],
                            [0, 0, 0, 1],
                            [0, 0, 1, 1]]]).ravel()
        r = local_mean_gauss(i, 2)
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 3D failed')
        
        # 4D
        i = numpy.asarray([i, i])
        e = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0,\
             1, 0, 0, 0, 1, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1,\
             1, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 2]
        r = local_mean_gauss(i, 1)
        numpy.testing.assert_allclose(r, e, err_msg = 'local mean gauss: 4D failed')
    
    def test_indices(self):
        """Test the feature: indices."""
        
        # 2D
        i = numpy.asarray([[0, 0],
                           [0, 0]])
        e = [[0,0], [0, 1], \
             [1, 0], [1, 1]]
        r = indices(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'indices: 2D failed')
        
        # 2D multi-spectral
        r = indices([i, i])
        numpy.testing.assert_allclose(r, e, err_msg = 'indices: 2D multi-spectral failed')
        
        # 2D with voxelspacing
        r = indices(i, voxelspacing = (1, 2.5))
        e = [[0,0], [0, 2.5], \
             [1, 0], [1, 2.5]]
        numpy.testing.assert_allclose(r, e, err_msg = 'indices: 2D \w voxelspacing failed')    
        
        # 2D with mask
        m = [[True, False],
             [True, False]]
        e = [[0,0], [1, 0]]
        r = indices(i, mask = m)
        numpy.testing.assert_allclose(r, e, err_msg = 'indices: 2D masked failed')    
        
        # 3D
        i = numpy.asarray([[0, 0],
                           [0, 0]])
        i = numpy.asarray([i, i])
        e = [[0,0,0], [0,0,1], [0,1,0], [0,1,1],
             [1,0,0], [1,0,1], [1,1,0], [1,1,1]]
        r = indices(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'indices: 3D failed')
        
        # 4D
        i = numpy.asarray([i, i])
        e = [[0,0,0,0], [0,0,0,1], [0,0,1,0], [0,0,1,1],
             [0,1,0,0], [0,1,0,1], [0,1,1,0], [0,1,1,1],
             [1,0,0,0], [1,0,0,1], [1,0,1,0], [1,0,1,1],
             [1,1,0,0], [1,1,0,1], [1,1,1,0], [1,1,1,1]]
        r = indices(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'indices: 4D failed')
    
    def test_centerdistance_xdminus1(self):
        """Test the feature: centerdistance_xdminus1."""
        
        # 2D with dim (invalid)
        i = numpy.asarray([[0, 0],
                           [0, 0]])
        self.assertRaises(ArgumentError, centerdistance_xdminus1, i, 0)
        
        # 3D with invalid dims (invalid)
        i = numpy.asarray([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 0]])
        i = numpy.asarray([i, i, i])
        self.assertRaises(ArgumentError, centerdistance_xdminus1, i, (0, 1))
        
        # 3D with invalid dim
        self.assertRaises(ArgumentError, centerdistance_xdminus1, i, 3)
        
        # 3D with valid dim 0
        e = [math.sqrt(2), 1, math.sqrt(2),\
             1, 0, 1,\
             math.sqrt(2), 1, math.sqrt(2)]
        e = numpy.asarray([e, e, e]).ravel()
        r = centerdistance_xdminus1(i, 0)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: 3D, dim = 0 failed')
        
        # 3D multi-spectral
        r = centerdistance_xdminus1([i, i], 0)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: 3D, multi-spectral failed')
        
        # 3D masked
        m = [[True, False, False],
             [False, True, False],
             [False, False, True]]
        e = [math.sqrt(2), 0, math.sqrt(2)]
        e = numpy.asarray([e, e, e]).ravel()
        r = centerdistance_xdminus1(i, 0, mask = [m, m, m])
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: 3D, masked failed')
        
        # 3D with valid dim 0, uneven image
        i = numpy.asarray([[[0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 0, 0, 0]],
                           [[0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 0, 0, 0]]])
        e = [math.sqrt(3.25), math.sqrt(1.25), math.sqrt(1.25), math.sqrt(3.25), \
             math.sqrt(2.25), math.sqrt(0.25), math.sqrt(0.25), math.sqrt(2.25), \
             math.sqrt(3.25), math.sqrt(1.25), math.sqrt(1.25), math.sqrt(3.25)]
        e = numpy.asarray([e, e]).ravel()
        r = centerdistance_xdminus1(i, 0)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: uneven 3D, dim = 0 failed')
        
        # 3D with valid dim 1, uneven image
        e = [[math.sqrt(2.5), math.sqrt(0.5), math.sqrt(0.5), math.sqrt(2.5)],
             [math.sqrt(2.5), math.sqrt(0.5), math.sqrt(0.5), math.sqrt(2.5)]]
        e = numpy.asarray([e, e, e])
        e = numpy.rollaxis(e, 0, 2).ravel()
        r = centerdistance_xdminus1(i, 1)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: uneven 3D, dim = 1 failed')
        
        # 3D with valid dim 2, uneven image
        e = [[math.sqrt(1.25), math.sqrt(0.25), math.sqrt(1.25)],
             [math.sqrt(1.25), math.sqrt(0.25), math.sqrt(1.25)]]
        e = numpy.asarray([e, e, e, e])
        e = numpy.rollaxis(e, 0, 3).ravel()
        r = centerdistance_xdminus1(i, 2)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: uneven 3D, dim = 2 failed')
        
        # 4D with valid dims 1, 3
        i = numpy.asarray([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 0]])
        i = numpy.asarray([i, i, i])
        i = numpy.asarray([i, i, i])
        e = [[math.sqrt(2), 1, math.sqrt(2)],
             [1, 0, 1],
             [math.sqrt(2), 1, math.sqrt(2)]]
        e = numpy.asarray([e] * 3)
        e = numpy.rollaxis(e, 0, 2)
        e = numpy.asarray([e] * 3)
        e = numpy.rollaxis(e, 0, 4).ravel()
        r = centerdistance_xdminus1(i, (1, 3))
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance_xdminus1: 4D, dim = (1, 3) failed')
    
    def test_centerdistance(self):
        """Test the feature: centerdistance."""
        
        i = numpy.asarray([[0, 0],
                           [0, 0]])
        e = [math.sqrt(0.5), math.sqrt(0.5),\
             math.sqrt(0.5), math.sqrt(0.5)]
        r = centerdistance(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 2D, single-spectrum, 2x2, unmasked and not normalized')
        
        r = centerdistance([i, i])
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 2D, multi-spectrum, 2x2, unmasked and not normalized')
        
        i = numpy.asarray([[1, 0.],
                           [2, 3.]])        
        r = centerdistance(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 2D, single-spectrum, 2x2, unmasked and not normalized: feature not independent of image content')
        
        i = numpy.asarray([[0, 0, 0],
                           [0, 0, 0],
                           [0, 0, 0]])
        e = [math.sqrt(2), 1, math.sqrt(2),\
             1, 0, 1,\
             math.sqrt(2), 1, math.sqrt(2)]
        r = centerdistance(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 2D, single-spectrum, 3x3, unmasked and not normalized')
        
        m = [[True, False, False],
             [False, True, False],
             [False, False, True]]
        e = [math.sqrt(2), 0, math.sqrt(2)]
        r = centerdistance(i, mask = m)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 2D, single-spectrum, 2x2, masked and not normalized')        
        
        e = [math.sqrt(1.25), 1, math.sqrt(1.25),\
             math.sqrt(0.25), 0, math.sqrt(0.25),\
             math.sqrt(1.25), 1, math.sqrt(1.25)]
        s = [1., 0.5]
        r = centerdistance(i, voxelspacing = s)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 2D, single-spectrum, 3x3, unmasked and not normalized: voxel spacing not taken into account')
        
        i = numpy.asarray([i, i, i])
        e = [math.sqrt(2), 1, math.sqrt(2),\
             1, 0, 1,\
             math.sqrt(2), 1, math.sqrt(2)]        
        en1 = [math.sqrt(3), math.sqrt(2), math.sqrt(3),\
               math.sqrt(2), 1,            math.sqrt(2),\
               math.sqrt(3), math.sqrt(2), math.sqrt(3)]
        e = numpy.asarray([en1, e, en1]).ravel()
        r = centerdistance(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 3D, single-spectrum, 3x3x3, unmasked and not normalized')
        
        i = numpy.asarray([i, i, i])
        en2 = [math.sqrt(4), math.sqrt(3), math.sqrt(4),\
               math.sqrt(3), math.sqrt(2), math.sqrt(3),\
               math.sqrt(4), math.sqrt(3), math.sqrt(4)]
        e = numpy.asarray([numpy.asarray([en2, en1, en2]).ravel(), e, numpy.asarray([en2, en1, en2]).ravel()]).ravel()
        r = centerdistance(i)
        numpy.testing.assert_allclose(r, e, err_msg = 'centerdistance: 4D, single-spectrum, 3x3x3x3, unmasked and not normalized')
        
    
    def test_intensities(self):
        """Test the feature: image intensity."""
        
        # Test 2D image with various settings
        i = numpy.asarray([[-1., 1, 2],
                           [ 0., 2, 4],
                           [ 1., 3, 5]])
        m = [[True, False, False],
             [False, True, False],
             [True, True, False]]
        e = [-1., 1, 2, 0, 2, 4, 1, 3, 5]
        em = [-1., 2., 1., 3.]
        
        r = intensities(i) # normalize = False, mask = slice(None)
        numpy.testing.assert_allclose(r, e, err_msg = 'intensities: 2D, single-spectrum, unmasked and not normalized')
        
        r = intensities(i, mask = m) # normalize = False
        numpy.testing.assert_allclose(r, em, err_msg = 'intensities: 2D, single-spectrum, masked and not normalized')
        
        r = intensities([i, i]) # normalize = False, mask = slice(None)
        numpy.testing.assert_allclose(r, join(e, e), err_msg = 'intensities: 2D, multi-spectrum, unmasked and not normalized')
        
        # Test 3D image
        i = numpy.asarray([i, i + 0.5])
        e = append(e, numpy.asarray(e) + 0.5)
        
        r = intensities(i) # normalize = False, mask = slice(None)
        numpy.testing.assert_allclose(r, e, err_msg = 'intensities: 3D, single-spectrum, unmasked and not normalized')
        
        # Test 4D image
        i = numpy.asarray([i, i + 0.5])
        e = append(e, numpy.asarray(e) + 0.5)
        
        r = intensities(i) # normalize = False, mask = slice(None)
        numpy.testing.assert_allclose(r, e, err_msg = 'intensities: 4D, single-spectrum, unmasked and not normalized')
        
        
    
if __name__ == '__main__':
    unittest.main()