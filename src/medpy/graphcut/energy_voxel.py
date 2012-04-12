"""
@package medpy.graphcut.energy_voxel
Run-time optimized energy functions for graph-cut on voxel images.

Provides a number of standard energy functions for both, boundary and regional terms,
that follow the signature required for building graphs using the graph module of this
package. Additionally a number of convenience functions for re-occurring data processing
are given.

Functions:
    - def boundary_difference_of_means((original_image)): simple mean value base boundary term

@author Oskar Maier
@version d0.1.2
@since 2012-03-23
@status Development
"""

# build-in module
import sys

# third-party modules
import scipy

# own modules

##
# !TODO: Implement a test for the voxel based graph cut. The expected cut is to separate the left 3/5 of the array
# from the rightmost 2/5. It is a good test, that is sensitive to distortion of the weights.
# An additional good test would be a very short example of an image where 0 weights could occur (this should never happen).
# test = [[[1,0,1,2,3],
#          [1,0,1,4,3].
#          [0,1,1,6,4]],
#         [[1,0,1,2,3],
#          [1,0,1,4,3].
#          [0,1,1,6,4]]]

# foreground = [[[0,0,0,0,0],
#                [0,0,0,0,0],
#                [1,0,0,0,0]]
#               [[0,0,0,0,0],
#                [0,0,0,0,0],
#                [1,0,0,0,0]]]

# background = [[[0,0,0,0,1],
#                [0,0,0,0,0],
#                [0,0,0,0,0]]
#               [[0,0,0,0,1],
#                [0,0,0,0,0],
#                [0,0,0,0,0]]]

# code
def boundary_difference_of_means(graph, (original_image)):
    """
    An implementation of the boundary term, suitable to be used with the
    @link graph_from_voxels() function.
    
    The simple energy function finds all edges between all neighbours of the image and
    uses their difference in mean values as edge weight.
    
    The graph weights generated have to be strictly positive and preferably in the
    interval (0, 1].
    
    To ensure this, the maximum possible difference in mean values is computed as
    \f[
        \alpha = \|\min I - \max I\|
    \f]
    , where \f$\min I\f$ constitutes the lowest intensity value in the image, while
    \f$\max I\f$ constitutes the highest. 
    
    With this value the weights between a voxel \f$x\f$ and its neighbour \f$y\f$ can be
    computed
    \f[
        w(x,y) = 1 - \frac{\|I_x - I_y\|}{\alpha + 1}
    \f]
    for which \f$w(x,y) \in (0, 1]\f$ holds true.
    
    @note This function requires the original image to be passed along. That means that
    @link graph_from_voxels() has to be called with boundary_term_args set to the
    original image. 
    
    @param original_image The original image.
    @type original_image numpy.ndarray
    
    @return a dictionary with the edges as keys and the respective weight tuples as
            values
    @rtype dict
    """
    original_image = original_image.astype(scipy.float_)
    
    ####
    # Notice:
    # In the first version the max_intensity_difference was simply increased by a 1 to
    # achieve strictly positive weights. While essentially keeping the order of the
    # weights, this nevertheless led to a distortion of their relations and, subsequently
    # to invalid graph cuts when the weights were summed up.
    # The new version simply adds sys.float_info.min to the result weight array, but is
    # computationally slightly more expensive. 
    max_intensity_difference = float(abs(original_image.max() - original_image.min()))

    # right neighbour (x)
    difference_to_x_neighbour = scipy.absolute(original_image[:-1] - original_image[1:])

    difference_to_x_neighbour /= max_intensity_difference
    difference_to_x_neighbour[difference_to_x_neighbour >= 1] = 1
    difference_to_x_neighbour = (1 - difference_to_x_neighbour) + sys.float_info.min # this alone can lead to values > 1, therefore the next step
    difference_to_x_neighbour = scipy.minimum(difference_to_x_neighbour, scipy.ones(difference_to_x_neighbour.shape, dtype=scipy.float_))

    x_offset = __flatten_index(1, 0, 0, original_image.shape[1], original_image.shape[2])
    # Note: The lines followed by an "# ABS" are not actually required and do nothing
    # They are just added to keep consistency with the y and z computations, where they are required
    #x_idx_offset_divider = (original_image.shape[0] - 1) * x_offset # ABS
    #x_idx_offset = lambda x: int(x / x_idx_offset_divider) * x_offset # ABS
    for key, value in enumerate(difference_to_x_neighbour.ravel()):
        #key += x_idx_offset(key) # ABS
        #print "x", key, key + x_offset, value, value
        #print '\tg -> add_edge( {}, {}, {}, {} );'.format(key, key + x_offset, value, value)
        graph.set_nweight(key, key + x_offset, value, value)
        
    # bottom neighbour (y)
    difference_to_y_neighbour = scipy.absolute(original_image[:,:-1] - original_image[:,1:])
    difference_to_y_neighbour /= max_intensity_difference
    difference_to_y_neighbour = (1 - difference_to_y_neighbour) + sys.float_info.min # this alone can lead to values > 1, therefore the next step
    difference_to_y_neighbour = scipy.minimum(difference_to_y_neighbour, scipy.ones(difference_to_y_neighbour.shape, dtype=scipy.float_))
    y_offset = __flatten_index(0, 1, 0, original_image.shape[1], original_image.shape[2])
    y_idx_offset_divider = (original_image.shape[1] - 1) * y_offset
    y_idx_offset = lambda x: int(x / y_idx_offset_divider) * y_offset
    for key, value in enumerate(difference_to_y_neighbour.ravel()):
        key += y_idx_offset(key)
        #print "y", key, key + y_offset, value, value
        #print '\tg -> add_edge( {}, {}, {}, {} );'.format(key, key + y_offset, value, value)
        graph.set_nweight(key, key + y_offset, value, value)
    # in neighbour (z)
    difference_to_z_neighbour = scipy.absolute(original_image[:,:,:-1] - original_image[:,:,1:])
    difference_to_z_neighbour /= max_intensity_difference
    difference_to_z_neighbour = (1 - difference_to_z_neighbour) + sys.float_info.min # this alone can lead to values > 1, therefore the next step
    difference_to_z_neighbour = scipy.minimum(difference_to_z_neighbour, scipy.ones(difference_to_z_neighbour.shape, dtype=scipy.float_))
    z_offset = __flatten_index(0, 0, 1, original_image.shape[1], original_image.shape[2])
    z_idx_offset_divider = (original_image.shape[2] - 1) * z_offset
    z_idx_offset = lambda x: int(x / z_idx_offset_divider) * z_offset
    for key, value in enumerate(difference_to_z_neighbour.ravel()):
        key += z_idx_offset(key)
        #print "z", key, key + z_offset, value, value
        #print '\tg -> add_edge( {}, {}, {}, {} );'.format(key, key + z_offset, value, value)
        graph.set_nweight(key, key + z_offset, value, value)
                         
def __flatten_index (x, y, z, ny, nz):
    """
    Takes a three dimensional index (x,y,z) and compues the index required to access the
    same element in the flattened version of the array.
    """
    return nz * (y + ny * x) + z
    