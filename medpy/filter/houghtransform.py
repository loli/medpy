"""
@package medpy.filter.houghtransform
Provides functionality connected with the Hough Transform.
    
See http://en.wikipedia.org/wiki/Hough_transform and http://en.wikipedia.org/wiki/Generalised_Hough_transform
for more information on the subject.

@author Oskar Maier
@version d0.1.2
@since 2013-06-07
@status Release
"""

# build-in modules
import math

# third-party modules
import scipy

# own modules
from medpy.filter.utilities import pad

# public methods
def ght_alternative (img, template, indices):
    """
    Alternative implementation of the general hough transform, which uses iteration over
    indices rather than broadcasting rules like @see ght().
    
    It is therefore considerably slower, especially for large, multi-dimensional arrays.
    The only application are cases, where the hough transform should only be computed for
    a small number of points (=template centers) in the image. In this case the indices
    of interest can be provided as a list.
    
    @param img the original image on which to search for the structure
    @type img numpy.ndarray
    @param template a boolean array containing the structure to search for
    @type template nump.ndarray
    @param indices a sequence of image indices
    @type indices sequence
    
    @return the general hough transformation
    @rtype numpy.ndarray
    """
    # cast template to bool and img to scipy array
    img = scipy.asarray(img)
    template = scipy.asarray(template).astype(scipy.bool_)
    
    # check supplied parameters
    if img.ndim != template.ndim:
        raise AttributeError('The supplied image and template must be of the same dimensionality.')
    if not scipy.all(scipy.greater_equal(img.shape, template.shape)):
        raise AttributeError('The supplied template is bigger than the image. This setting makes no sense for a hough transform.')
    
    # pad the original image
    img_padded = pad(img, footprint=template, mode='constant')
    
    # prepare the hough image
    if scipy.bool_ == img.dtype:
        img_hough = scipy.zeros(img.shape, scipy.int32)
    else:
        img_hough = scipy.zeros(img.shape, img.dtype)
        
    # iterate over the pixels, apply the template center to each of these and save the sum into the hough image
    for idx_hough in indices:
        idx_hough = tuple(idx_hough)
        slices_img_padded = [slice(idx_hough[i], None) for i in range(img_hough.ndim)]
        img_hough[idx_hough] = sum(img_padded[slices_img_padded][template])     
        
    return img_hough

def ght(img, template):
    """
    Implementation of the general hough transform for all dimensions.
    
    Providing a template, this method searches in the image for structures similar to the
    one depicted by the template. The returned hough image denotes how well the structure
    fit in each index.
    
    The indices of the returned image correspond with the centers of the template. At the
    corresponding locations of the original image the template is applied (like a stamp)
    and the underlying voxel values summed up to form the hough images value. It is
    suggested to normalize the input image before for speaking results.
    
    This function behaves as the general hough transform if a binary image has been
    supplied. In the case of a gray-scale image, the values of the pixels under the
    templates structure are summed up, thus weighting becomes possible.
    
    @note:
    The center of a structure with odd side-length is simple the arrays middle. When an
    even-sided array has been supplied as template, the middle rounded down is taken as
    the structures center. This means that in the second case the hough image is shifted
    by half a voxel (ndim * [-0.5]).
    
    @param img the original image on which to search for the structure
    @type img numpy.ndarray
    @param template a boolean array containing the structure to search for
    @type template nump.ndarray
    
    @return the general hough transformation
    @rtype numpy.ndarray
    """    
    # cast template to bool and img to scipy array
    img = scipy.asarray(img)
    template = scipy.asarray(template).astype(scipy.bool_)
    
    # check supplied parameters
    if img.ndim != template.ndim:
        raise AttributeError('The supplied image and template must be of the same dimensionality.')
    if not scipy.all(scipy.greater_equal(img.shape, template.shape)):
        raise AttributeError('The supplied template is bigger than the image. This setting makes no sense for a hough transform.')    
    
    # compute center of template array
    center = (scipy.asarray(template.shape) - 1) / 2 # integer division intended
    
    # prepare the hough image
    if scipy.bool_ == img.dtype:
        img_hough = scipy.zeros(img.shape, scipy.int32)
    else:
        img_hough = scipy.zeros(img.shape, img.dtype)
    
    # iterate over the templates non-zero positions and sum up the images accordingly shifted 
    for idx in scipy.transpose(template.nonzero()):
        slicers_hough = []
        slicers_orig = []
        for i in range(img.ndim):
            pos = -1 * (idx[i] - center[i])
            if 0 == pos: # no shift
                slicers_hough.append(slice(None, None))
                slicers_orig.append(slice(None, None))
            elif pos > 0: # right shifted hough
                slicers_hough.append(slice(pos, None))
                slicers_orig.append(slice(None, -1 * pos))
            else: # left shifted hough
                slicers_hough.append(slice(None, pos))
                slicers_orig.append(slice(-1 * pos, None))
        img_hough[slicers_hough] += img[slicers_orig]
        
    return img_hough

def template_sphere (radius, dimensions):
    """
    Returns a spherical binary structure of a of the supplied radius that can be used as
    template input to the generalized hough transform.

    @param radius the circles radius in voxel
    @type radius integer
    @param dimension the dimensionality of the circle
    @type radius integer
    
    @return a bool array containing a sphere
    @rtype scipy.ndarray
    """
    if int(dimensions) != dimensions:
        raise TypeError('The supplied dimension parameter must be of type integer.')
    dimensions = int(dimensions)
    
    return template_ellipsoid(dimensions * [radius * 2])

def template_ellipsoid (shape):
    """
    Returns an ellipsoid binary structure of a of the supplied radius that can be used as
    template input to the generalized hough transform.
    
    @param shape the main axes of the ellipsoid
    @type shape sequence
    
    @return a bool array containing an ellipsoid
    @rtype scipy.ndarray
    """
    # prepare template array
    template = scipy.zeros(map(lambda x: round(x / 2.), shape), dtype=scipy.bool_) # in odd shape cases, this will include the ellipses middle line, otherwise not

    # get real world offset to compute the ellipsoid membership
    rw_offset = []
    for s in shape:
        if int(s) % 2 == 0: rw_offset.append(0.5 - (s % 2) / 2.) # number before point is even 
        else: rw_offset.append(-1 * (s % int(s)) / 2.) # number before point is odd 

    # prepare an array containing the squares of the half axes to avoid computing inside the loop
    shape_pow = scipy.power(scipy.asarray(shape) / 2., 2)

    # we use the ellipse normal form to find all point in its surface as well as volume
    # e.g. for 2D, all voxels inside the ellipse (or on its surface) with half-axes a and b
    #      follow x^2/a^2 + y^2/b^2 <= 1; for higher dimensions accordingly
    # to not have to iterate over each voxel, we make use of the ellipsoids symmetry
    # and construct just a part of the whole ellipse here
    for idx in scipy.ndindex(template.shape):
        distance = sum((math.pow(coordinate + rwo, 2) / axes_pow for axes_pow, coordinate, rwo in zip(shape_pow, idx, rw_offset))) # plus once since ndarray is zero based, but real-world coordinates not
        if distance <= 1: template[idx] = True
        
    # we take now our ellipse part and flip it once along each dimension, concatenating it in each step
    # the slicers are constructed to flip in each step the current dimension i.e. to behave like arr[...,::-1,...]
    for i in range(template.ndim):
        slicers = [(slice(None, None, -1) if i == j else slice(None)) for j in range(template.ndim)]
        if 0 == int(shape[i]) % 2: # even case
            template = scipy.concatenate((template[slicers], template), i)
        else: # odd case, in which an overlap has to be created
            slicers_truncate = [(slice(None, -1) if i == j else slice(None)) for j in range(template.ndim)]
            template = scipy.concatenate((template[slicers][slicers_truncate], template), i)

    return template

