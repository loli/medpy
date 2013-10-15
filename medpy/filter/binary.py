"""
@package medpy.filter.binary
Filters for binary images.

Provides a number of filter that implement functionality for binary images only.

Functions:
    

@author Oskar Maier
@version d0.1.1
@since 2013-10-14
@status Development
"""

# build-in module

# third-party modules
import numpy
from scipy.ndimage.measurements import label

# own modules

# code
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
    labeled_array, num_features = label(img)
    component_sizes = [numpy.count_nonzero(labeled_array == label_idx) for label_idx in range(1, num_features + 1)]
    largest_component_idx = numpy.argmax(component_sizes) + 1

    out = numpy.zeros(img.shape, numpy.bool)  
    out[labeled_array == largest_component_idx] = True
    return out