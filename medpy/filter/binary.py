"""
@package medpy.filter.binary
Filters for binary images.

Provides a number of filter that implement functionality for binary images only.

Functions:
    - def largest_connected_component(img, structure = None)
    - def size_threshold(img, thr, comp='lt', voxelspacing = None)
    

@author Oskar Maier
@version d0.2.1
@since 2013-10-14
@status Development
"""

# build-in module
from operator import  lt, le, gt, ge, ne, eq

# third-party modules
import numpy 
from scipy.ndimage.measurements import label

# own modules

# code
def size_threshold(img, thr, comp='lt', structure = None):
    """
    Removes binary objects from an image identified by a size threshold.
    
    The unconnected binary objects in an image are identified and all removed
    whose size compares (e.g. less-than) to a supplied threshold value.
    
    The threshold `thr` can be any positive integer value. The comparison operator
    can be one of lt, le, gt, ge, ne or eq. The operators used are the functions of
    the same name supplied by the `operator` module of python.
    
    Parameters
    ----------
    img : array_like
        Array whose objects should be removed. Will be cast to type numpy.bool.
    thr : int
        Integer defining the threshold size of the binary objects to remove.
    comp : {'lt', 'le', 'gt', 'ge', 'ne', 'eq'}
        The type of comparison to perform. Use e.g. 'lt' for less-than.
    structure : array of ints, optional
        A structuring element that defines feature connections.
        `structure` must be symmetric. If no structuring element is provided,
        one is automatically generated with a squared connectivity equal to
        one. That is, for a 2-D `input` array, the default structuring element
        is::
        
            [[0,1,0],
            [1,1,1],
            [0,1,0]]
    
    Returns
    -------
    binary_image : ndarray
        The supplied binary images with all objects removed that positively compare
        to the threshold `thr` using the comparison operator defined with `comp`.
        
    Notes
    -----
    If your voxel size is no isotrop i.e. of side-length 1 for all dimensions, simply
    divide the supplied threshold through the real voxel size.
    """
    
    operators = {'lt': lt, 'le': le, 'gt': gt, 'ge': ge, 'eq': eq, 'ne': ne}
    
    img = numpy.asarray(img).astype(numpy.bool)
    if comp not in operators:
        raise ValueError("comp must be one of {}".format(operators.keys()))
    comp = operators[comp]
    
    labeled_array, num_features = label(img, structure)
    for oidx in range(1, num_features + 1):
        omask = labeled_array == oidx
        if comp(numpy.count_nonzero(omask), thr):
            img[omask] = False
            
    return img

def largest_connected_component(img, structure = None):
    """
    Select the largest connected binary component in an image.
    Treats all zero values in the input image as background and all others as foreground.
    The return value is an binary array of equal dimensions as the input array with TRUE
    values where the largest connected component is situated.
    
    @param img A binary image
    @type numpy.ndarray
    @param structure A structuring element that defines the connectivity. Structure must be symmetric. If no structuring element is provided, one is automatically generated with a squared connectivity equal to one.
    @type numpy.ndarray
    
    @return A binary image
    @rtype numpy.ndarray
    """   
    labeled_array, num_features = label(img, structure)
    component_sizes = [numpy.count_nonzero(labeled_array == label_idx) for label_idx in range(1, num_features + 1)]
    largest_component_idx = numpy.argmax(component_sizes) + 1

    out = numpy.zeros(img.shape, numpy.bool)  
    out[labeled_array == largest_component_idx] = True
    return out
