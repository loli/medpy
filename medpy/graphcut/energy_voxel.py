"""
@package medpy.graphcut.energy_voxel
Run-time optimized energy functions for graph-cut on voxel images.

Provides a number of standard energy functions for both, boundary and regional terms,
that follow the signature required for building graphs using the graph module of this
package. Additionally a number of convenience functions for re-occurring data processing
are given.

Functions:
    - def boundary_maximum_linear(graph, (gradient_image, spacing))
    - def boundary_difference_linear(graph, (original_image, spacing))
    - def boundary_maximum_exponential(graph, (gradient_image, sigma, spacing))
    - def boundary_difference_exponential(graph, (original_image, sigma, spacing))
    - def boundary_maximum_division(graph, (gradient_image, sigma, spacing))
    - def boundary_difference_division(graph, (original_image, sigma, spacing))
    - def boundary_maximum_power(graph, (gradient_image, sigma, spacing))
    - def boundary_difference_power(graph, (original_image, sigma, spacing))

@author Oskar Maier
@version d0.3.0
@since 2012-03-23
@status Development
"""

# build-in module
import sys

# third-party modules
import numpy
import scipy
import math

# own modules

# code
def regional_probability_map(graph, (probability_map, alpha)):
    """
    Setting the regional term with a probability map.
    
    Takes an image/graph/map as input where each entry contains a probability value for
    the corresponding GC graph node to belong to the foreground object. The probabilities
    must be in the range [0, 1]. The reverse weights are assigned to the sink
    (which corresponds to the background).
    """
    probability_map = scipy.asarray(probability_map)
    probabilities = numpy.vstack([(probability_map * alpha).flat,
                                  ((1 - probability_map) * alpha).flat]).T
    graph.set_tweights_all(probabilities)

def boundary_maximum_linear(graph, (gradient_image, spacing)):
    """
    The same as energy_voxel.boundary_difference_linear(), but working on the gradient
    image instead of the original.
    
    @see energy_voxel.boundary_difference_linear() for details.
    """
    gradient_image = scipy.asarray(gradient_image)
    
    # compute maximum (possible) intensity difference
    max_intensity_difference = float(abs(gradient_image.max() - gradient_image.min()))
    
    def boundary_term_linear(intensities):
        """
        Implementation of a linear boundary term computation over an array.
        """
        # normalize the intensity distances to the interval (0, 1]
        intensities /= max_intensity_difference
        #difference_to_neighbour[difference_to_neighbour > 1] = 1 # this line should not be required, but might be due to rounding errors
        intensities = (1. - intensities) # reverse weights such that high intensity difference lead to small weights and hence more likely to a cut at this edge
        intensities[intensities == 0.] = sys.float_info.min # required to avoid zero values
        return intensities
    
    __skeleton_maximum(graph, gradient_image, boundary_term_linear)

def boundary_difference_linear(graph, (original_image, spacing)):
    """
    An implementation of the boundary term, suitable to be used with the
    generate.graph_from_voxels() function.
    
    Finds all edges between all neighbours of the image and uses their normalized
    difference in intensity values as edge weight.
    
    The weights are linearly normalized using the maximum possible intensity difference
    of the image.
    
    Formally this value is computed as
    \f[
        \sigma = |max I - \min I|
    \f]
    , where \f$\min I\f$ constitutes the lowest intensity value in the image, while
    \f$\max I\f$ constitutes the highest. 
    
    The weights between two neighbouring voxels \f$(p, q)\f$ is then computed as
    \f[
        w(p,q) = 1 - \frac{|I_p - I_q|}{\sigma} + \epsilon
    \f]
    , where \f$\epsilon\f$ is a infinitively small number and for which
    \f$w(p, q) \in (0, 1]\f$ holds true.
    
    When the created edge weights should be weighted according to the slice distance,
    provide the list of slice thicknesses via the spacing parameter. Then all weights
    computed for the corresponding direction are divided by the respective slice
    thickness. Set this parameter to False for equally weighted edges.     
    
    @note This function requires the original image to be passed along. That means that
    generate.graph_from_voxels() has to be called with boundary_term_args set to the
    original image.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param original_image The original image.
    @type original_image numpy.ndarray
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False        
    """
    original_image = scipy.asarray(original_image)
    
    # compute maximum (possible) intensity difference
    max_intensity_difference = float(abs(original_image.max() - original_image.min()))
    
    def boundary_term_linear(intensities):
        """
        Implementation of a linear boundary term computation over an array.
        """
        # normalize the intensity distances to the interval (0, 1]
        intensities /= max_intensity_difference
        #difference_to_neighbour[difference_to_neighbour > 1] = 1 # this line should not be required, but might be due to rounding errors
        intensities = (1. - intensities) # reverse weights such that high intensity difference lead to small weights and hence more likely to a cut at this edge
        intensities[intensities == 0.] = sys.float_info.min # required to avoid zero values
        return intensities
    
    __skeleton_difference(graph, original_image, boundary_term_linear)

def boundary_maximum_exponential(graph, (gradient_image, sigma, spacing)):
    """
    The same as energy_voxel.boundary_difference_exponential(), but working on the gradient
    image instead of the original.
    
    @see energy_voxel.boundary_difference_exponential() for details.
    """
    gradient_image = scipy.asarray(gradient_image)
    
    def boundary_term_exponential(intensities):
        """
        Implementation of a exponential boundary term computation over an array.
        """
        # apply exp-(x**2/sigma**2)
        intensities = scipy.power(intensities, 2)
        intensities /= math.pow(sigma, 2)
        intensities *= -1
        intensities = scipy.exp(intensities)
        intensities[intensities <= 0] = sys.float_info.min
        return intensities
    
    __skeleton_maximum(graph, gradient_image, boundary_term_exponential)    

def boundary_difference_exponential(graph, (original_image, sigma, spacing)):
    """
    An implementation of the boundary term, suitable to be used with the
    generate.graph_from_voxels() function.
    
    Finds all edges between all neighbours of the image and uses their difference in
    intensity values as edge weight.
    
    The weights are normalized using an exponential function and a smoothing factor
    \f$\sigma\f$.
    
    The \f$\sigma\f$. value has to be supplied manually, since its ideal settings
    differ greatly from application to application.
    
    The weights between two neighbouring voxels \f$(p, q)\f$ is then computed as
    \f[
        w(p,q) = \exp^{-\frac{|I_p - I_q|^2}{\sigma^2}}
    \f]
    , for which \f$w(p, q) \in (0, 1]\f$ holds true.
    
    When the created edge weights should be weighted according to the slice distance,
    provide the list of slice thicknesses via the spacing parameter. Then all weights
    computed for the corresponding direction are divided by the respective slice
    thickness. Set this parameter to False for equally weighted edges.     
    
    @note This function requires the original image to be passed along. That means that
    generate.graph_from_voxels() has to be called with boundary_term_args set to the
    original image.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param original_image The original image.
    @type original_image numpy.ndarray
    @param sigma The sigma to use in the boundary term
    @type sigma float
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False        
    """
    original_image = scipy.asarray(original_image)
    
    def boundary_term_exponential(intensities):
        """
        Implementation of a exponential boundary term computation over an array.
        """
        # apply exp-(x**2/sigma**2)
        intensities = scipy.power(intensities, 2)
        intensities /= math.pow(sigma, 2)
        intensities *= -1
        intensities = scipy.exp(intensities)
        intensities[intensities <= 0] = sys.float_info.min
        return intensities
    
    __skeleton_difference(graph, original_image, boundary_term_exponential, spacing)
    
def boundary_maximum_division(graph, (gradient_image, sigma, spacing)):
    """
    The same as energy_voxel.boundary_difference_division(), but working on the gradient
    image instead of the original.
    
    @see energy_voxel.boundary_difference_division() for details.
    """
    gradient_image = scipy.asarray(gradient_image)
    
    def boundary_term_division(intensities):
        """
        Implementation of a exponential boundary term computation over an array.
        """
        # apply 1 / (1  + x/sigma)
        intensities /= sigma
        intensities = 1. / (intensities + 1)
        intensities[intensities <= 0] = sys.float_info.min
        return intensities
    
    __skeleton_difference(graph, gradient_image, boundary_term_division)
    
def boundary_difference_division(graph, (original_image, sigma, spacing)):
    """
    An implementation of the boundary term, suitable to be used with the
    generate.graph_from_voxels() function.
    
    Finds all edges between all neighbours of the image and uses their difference in
    intensity values as edge weight.
    
    The weights are normalized using an division function and a smoothing factor
    \f$\sigma\f$.
    
    The \f$\sigma\f$. value has to be supplied manually, since its ideal settings
    differ greatly from application to application.
    
    The weights between two neighbouring voxels \f$(p, q)\f$ is then computed as
    \f[
        w(p,q) = \frac{1}{1 + \frac{|I_p - I_q|}{\sigma}}
    \f]
    , for which \f$w(p, q) \in (0, 1]\f$ holds true.
    
    When the created edge weights should be weighted according to the slice distance,
    provide the list of slice thicknesses via the spacing parameter. Then all weights
    computed for the corresponding direction are divided by the respective slice
    thickness. Set this parameter to False for equally weighted edges.     
    
    @note This function requires the original image to be passed along. That means that
    generate.graph_from_voxels() has to be called with boundary_term_args set to the
    original image.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param original_image The original image.
    @type original_image numpy.ndarray
    @param sigma The sigma to use in the boundary term
    @type sigma float
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False        
    """
    original_image = scipy.asarray(original_image)
    
    def boundary_term_division(intensities):
        """
        Implementation of a exponential boundary term computation over an array.
        """
        # apply 1 / (1  + x/sigma)
        intensities /= sigma
        intensities = 1. / (intensities + 1)
        intensities[intensities <= 0] = sys.float_info.min
        return intensities
    
    __skeleton_difference(graph, original_image, boundary_term_division)
    
def boundary_maximum_power(graph, (gradient_image, sigma, spacing)):
    """
    The same as energy_voxel.boundary_difference_power(), but working on the gradient
    image instead of the original.
    
    @see energy_voxel.boundary_difference_power() for details.
    """
    gradient_image = scipy.asarray(gradient_image)
    
    def boundary_term_division(intensities):
        """
        Implementation of a exponential boundary term computation over an array.
        """
        # apply (1 / (1  + x))^sigma
        intensities = 1. / (intensities + 1)
        intensities = scipy.power(intensities, sigma)
        intensities[intensities <= 0] = sys.float_info.min
        return intensities
    
    __skeleton_maximum(graph, gradient_image, boundary_term_division)       
    
    
def boundary_difference_power(graph, (original_image, sigma, spacing)):
    """
    An implementation of the boundary term, suitable to be used with the
    generate.graph_from_voxels() function.
    
    Finds all edges between all neighbours of the image and uses their difference in
    intensity values as edge weight.
    
    The weights are normalized using an power function and a smoothing factor
    \f$\sigma\f$.
    
    The \f$\sigma\f$. value has to be supplied manually, since its ideal settings
    differ greatly from application to application.
    
    The weights between two neighbouring voxels \f$(p, q)\f$ is then computed as
    \f[
        w(p,q) = \frac{1}{1 + |I_p - I_q|}^\sigma
    \f]
    , for which \f$w(p, q) \in (0, 1]\f$ holds true.
    
    When the created edge weights should be weighted according to the slice distance,
    provide the list of slice thicknesses via the spacing parameter. Then all weights
    computed for the corresponding direction are divided by the respective slice
    thickness. Set this parameter to False for equally weighted edges. 
    
    @note This function requires the original image to be passed along. That means that
    generate.graph_from_voxels() has to be called with boundary_term_args set to the
    original image.
    
    @param graph An initialized graph.GCGraph object
    @type graph.GCGraph
    @param original_image The original image.
    @type original_image numpy.ndarray
    @param sigma The sigma to use in the boundary term
    @type sigma float
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False    
    """
    original_image = scipy.asarray(original_image)
    
    def boundary_term_division(intensities):
        """
        Implementation of a exponential boundary term computation over an array.
        """
        # apply (1 / (1  + x))^sigma
        intensities = 1. / (intensities + 1)
        intensities = scipy.power(intensities, sigma)
        intensities[intensities <= 0] = sys.float_info.min
        return intensities
    
    __skeleton_difference(graph, original_image, boundary_term_division)   

def __skeleton_maximum(graph, image, boundary_term, spacing):
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
    @param boundary_term A function to compute the boundary term over an array of
                         maximum intensities
    @type boundary_term function
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False    
    
    @see energy_voxel.__skeleton_difference() for more details.
    """
    def intensity_maximum(neighbour_one, neighbour_two):
        """
        Takes two voxel arrays constituting neighbours and computes the maximum between
        their intensities.
        """
        return scipy.maximum(neighbour_one, neighbour_two)
        
    __skeleton_base(graph, image, boundary_term, intensity_maximum, spacing)
    

def __skeleton_difference(graph, image, boundary_term, spacing):
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
    @param boundary_term A function to compute the boundary term over an array of
                         absolute intensity differences
    @type boundary_term function
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False    
    """
    def intensity_difference(neighbour_one, neighbour_two):
        """
        Takes two voxel arrays constituting neighbours and computes the absolute
        intensity differences.
        """
        return scipy.absolute(neighbour_one - neighbour_two)
        
    __skeleton_base(graph, image, boundary_term, intensity_difference, spacing)

def __skeleton_base(graph, image, boundary_term, neighbourhood_function, spacing):
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
    @param spacing A sequence containing the slice spacing used for weighting the
                   computed neighbourhood weight value for different dimensions. If
                   False, no distance based weighting of the graph edges is performed.
    @param spacing sequence | False
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
        neighbourhood_intensity_term = boundary_term(neighbourhood_intensity_term)
        # compute key offset for relative key difference
        offset_key = [1 if i == dim else 0 for i in range(image.ndim)]
        offset = __flatten_index(offset_key, image.shape)
        # generate index offset function for index dependent offset
        idx_offset_divider = (image.shape[dim] - 1) * offset
        idx_offset = lambda x: int(x / idx_offset_divider) * offset
        
        # weight the computed distanced in dimension dim by the corresponding slice spacing provided
        if spacing: neighbourhood_intensity_term /= spacing[dim]
        
        for key, value in enumerate(neighbourhood_intensity_term.ravel()):
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
    