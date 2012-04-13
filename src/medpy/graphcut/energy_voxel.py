"""
@package medpy.graphcut.energy_voxel
Run-time optimized energy functions for graph-cut on voxel images.

Provides a number of standard energy functions for both, boundary and regional terms,
that follow the signature required for building graphs using the graph module of this
package. Additionally a number of convenience functions for re-occurring data processing
are given.

Functions:
    - def boundary_difference_of_means(graph, (original_image)): simple mean value base boundary term

@author Oskar Maier
@version d0.1.2
@since 2012-03-23
@status Development
"""

# build-in module
import sys

# third-party modules
import scipy
import math

# own modules

# code
def boundary_difference_of_means(graph, (original_image)):
    """
    An implementation of the boundary term, suitable to be used with the
    generate.graph_from_voxels() function.
    
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
    generate.graph_from_voxels() has to be called with boundary_term_args set to the
    original image.
    
    @note To achieve weights between in the interval \f$(0, 1]\f$, the intensity
    differences between neighbouring voxels are scaled assuming \f$\|\min I - \max I\|\f$
    as the maximum, and \f$0\f$ as the minimal possible intensity difference.
    
    @note This function is tested only 2D and 3D images but theoretically works for all
    dimensions.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param original_image The original image.
    @type original_image numpy.ndarray
    """
    original_image = scipy.asarray(original_image)
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

    # iterate over the image dimensions and for each create the appropriate edges and compute the associated weights
    for dim in range(original_image.ndim):
        # construct slice-objects for the current dimension
        slices_exclude_last = [slice(None)] * original_image.ndim
        slices_exclude_last[dim] = slice(-1)
        slices_exclude_first = [slice(None)] * original_image.ndim
        slices_exclude_first[dim] = slice(1, None)
        # compute difference between all layers in the current dimensions direction     
        difference_to_neighbour = scipy.absolute(original_image[slices_exclude_last] - original_image[slices_exclude_first])
        # normalize the intensity distances to the interval (0, 1]
        difference_to_neighbour /= max_intensity_difference
        #difference_to_neighbour[difference_to_neighbour > 1] = 1 # this line should not be required, but might be due to rounding errors
        difference_to_neighbour = (1. - difference_to_neighbour) # reverse weights such that high intensity difference lead to small weights and hence more likely to a cut at this edge
        difference_to_neighbour[difference_to_neighbour == 0.] = sys.float_info.min # required to avoid zero values
        # compute key offset for relative key difference
        offset_key = [1 if i == dim else 0 for i in range(original_image.ndim)]
        offset = __flatten_index(offset_key, original_image.shape)
        # generate index offset function for index dependent offset
        idx_offset_divider = (original_image.shape[dim] - 1) * offset
        idx_offset = lambda x: int(x / idx_offset_divider) * offset
        
        for key, value in enumerate(difference_to_neighbour.ravel()):
            # debug lines
            #print dim, key, key + offset, value, value
            #print '\tg -> add_edge( {}, {}, {}, {} );'.format(key, key + offset, value, value)
            
            # apply index dependent offset
            key += idx_offset(key) 
            
            # add edges and set the weight
            graph.set_nweight(key, key + offset, value, value)

def boundary_difference_of_means2(graph, (original_image)):
    original_image = scipy.asarray(original_image)
    original_image = original_image.astype(scipy.float_)

    max_intensity_difference = float(abs(original_image.max() - original_image.min()))
    sigma = 25

    # iterate over the image dimensions and for each create the appropriate edges and compute the associated weights
    for dim in range(original_image.ndim):
        # construct slice-objects for the current dimension
        slices_exclude_last = [slice(None)] * original_image.ndim
        slices_exclude_last[dim] = slice(-1)
        slices_exclude_first = [slice(None)] * original_image.ndim
        slices_exclude_first[dim] = slice(1, None)
        # compute difference between all layers in the current dimensions direction     
        difference_to_neighbour = scipy.absolute(original_image[slices_exclude_last] - original_image[slices_exclude_first])
        
        # apply exp-(x**2/sigma**2)
        difference_to_neighbour = scipy.power(difference_to_neighbour, 2)
        difference_to_neighbour /= math.pow(sigma, 2)
        difference_to_neighbour *= -1
        difference_to_neighbour = scipy.exp(difference_to_neighbour)
        difference_to_neighbour[difference_to_neighbour <= 0] = sys.float_info.min
        
        # compute key offset for relative key difference
        offset_key = [1 if i == dim else 0 for i in range(original_image.ndim)]
        offset = __flatten_index(offset_key, original_image.shape)
        # generate index offset function for index dependent offset
        idx_offset_divider = (original_image.shape[dim] - 1) * offset
        idx_offset = lambda x: int(x / idx_offset_divider) * offset
        
        for key, value in enumerate(difference_to_neighbour.ravel()):
            # debug lines
            #print dim, key, key + offset, value, value
            #print '\tg -> add_edge( {}, {}, {}, {} );'.format(key, key + offset, value, value)
            
            # apply index dependent offset
            key += idx_offset(key) 
            
            # add edges and set the weight
            graph.set_nweight(key, key + offset, value, value)    

def __skeleton_maximum(graph, image, function):
    """
    A skeleton for the calculation of maximum intensity based boundary terms.
    
    This function is equivalent to energy_voxel.__skeleton_difference(), but uses the
    maximum intensity rather than the intensity difference of neighbouring voxels. It is
    therefore suitable to be used with the gradient image, rather than the original
    image.
    
    The computation of the edge weights follows
    \f[
        w(p,q) = g(max(I_p, I_q))
    \f]
    ,where \f$g(\cdot)\f$ is the supplied boundary term function.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param image The image to compute on
    @type image numpy.ndarray
    @param function A function to compute the boundary term over an array of
                    maximum intensities
    @type function function
    
    @see energy_voxel.__skeleton_difference() for more details.
    """
    pass
    

def __skeleton_difference(graph, image, function):
    """
    A skeleton for the calculation of intensity difference based boundary terms.
    
    Iterates over the images dimensions and generates for each an array of absolute
    neighbouring voxel \f$(p, q)\f$ intensity differences \f$|I_p, I_q|\f$. These are
    then passed to the supplied function \f$g(\cdot)\f$ for for boundary term
    computation. Finally the returned edge weights are added to the graph.
    
    Formally for each edge \f$(p, q)\f$ of the image, their edge weight is computed as
    \f[
        w(p,q) = g(|I_p - I_q|)
    \f]
    ,where \f$g(\cdot)\f$ is the supplied boundary term function.
    
    The boundary term function has to take an array of intensity differences as only
    parameter and return an array of the same shape containing the edge weights. For the
    implemented function the condition \f$g(\cdot)\in(0, 1]\f$ must hold true, i.e., it
    has to be strictly positive with \f$1\f$ as the upper limit.
    
    @note the underlying neighbourhood connectivity is 4 for 2D, 6 for 3D, etc. 
    
    @note This function is able to work with images of arbitrary dimensions, but was only
    tested for 2D and 3D cases.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param image The image to compute on
    @type image numpy.ndarray
    @param function A function to compute the boundary term over an array of
                    absolute intensity differences
    @type function function
    """
    pass

def __skeleton_base(graph, image, boundary_term, neighbourhood_function):
    """
    Base of the skeleton for voxel based boundary term calculation.
    
    This function holds the low level procedures shared by nearly all boundary terms.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param image The image containing the voxel intensity values
    @type image numpy.ndarray
    @param boundary_term A function to compute the boundary term over an array of
                           absolute intensity differences
    @type boundary_term function
    @param neighbourhood_function A function that takes two arrays of neighbouring pixels
                                  and computes an intensity term from them that is
                                  returned as a single array of the same shape
    @type neighbourhood_function function
    """
    image = scipy.asarray(image)
    image = image.astype(scipy.float_)

    # iterate over the image dimensions and for each create the appropriate edges and compute the associated weights
    for dim in range(image.ndim):
        # construct slice-objects for the current dimension
        slices_exclude_last = [slice(None)] * image.ndim
        slices_exclude_last[dim] = slice(-1)
        slices_exclude_first = [slice(None)] * image.ndim
        slices_exclude_first[dim] = slice(1, None)
        
        # compute difference between all layers in the current dimensions direction
        neighbourhood_intensity_term = neighbourhood_function(image[slices_exclude_last], image[slices_exclude_first])
        
        # apply boundary term
        neighbourhood_intensity_term = scipy.power(neighbourhood_intensity_term, 2)
        neighbourhood_intensity_term /= math.pow(sigma, 2)
        neighbourhood_intensity_term *= -1
        neighbourhood_intensity_term = scipy.exp(neighbourhood_intensity_term)
        neighbourhood_intensity_term[neighbourhood_intensity_term <= 0] = sys.float_info.min
        
        # compute key offset for relative key difference
        offset_key = [1 if i == dim else 0 for i in range(image.ndim)]
        offset = __flatten_index(offset_key, image.shape)
        # generate index offset function for index dependent offset
        idx_offset_divider = (image.shape[dim] - 1) * offset
        idx_offset = lambda x: int(x / idx_offset_divider) * offset
        
        for key, value in enumerate(neighbourhood_intensity_term.ravel()):
            # debug lines
            #print dim, key, key + offset, value, value
            #print '\tg -> add_edge( {}, {}, {}, {} );'.format(key, key + offset, value, value)
            
            # apply index dependent offset
            key += idx_offset(key) 
            
            # add edges and set the weight
            graph.set_nweight(key, key + offset, value, value)    
    

def __flatten_index(pos, shape):
    """
    Takes a three dimensional index (x,y,z) and computes the index required to access the
    same element in the flattened version of the array.
    """
    res = 0
    acc = 1
    for pi, si in zip(reversed(pos), reversed(shape)):
        res += pi * acc
        acc *= si
    return res
    