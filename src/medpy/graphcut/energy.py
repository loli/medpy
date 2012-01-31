"""
@package medpy.graphcut.energy
Run-time optimized energy functions for graph-cut.

Provides a number of standard energy functions for both, boundary and regional terms,
that follow the signature required for building graphs using the graph module of this
package. Additionally a number of convenience functions for re-occurring data processing
are given.

Functions:
    - def boundary_stawiaski(label_image, r1_bb, r2_bb, r1_id, r2_id, (gradient_image)): boundary term implementation in (1)

(1) Stawiaski J., Decenciere E., Bidlaut F. / "Interactive Liver Tumor Segmentation
Using Graph-cuts and watershed" / MICCAI 2008 participation

@author Oskar Maier
@version d0.1.0
@since 2012-01-18
@status Development
"""

# build-in module
import math

# third-party modules

# own modules

# code
def boundary_medium_intensity(label_image, r1_bb, r2_bb, r1_id, r2_id, (original_image)):
    """
    An implementation of the boundary term computing the difference between the regions
    mean intensity values.
    
    Usable as bounary_term function for @link graph_from_labels() function.
    
    Determines for each of the supplied region the mean intensity value and return their
    absolute difference.
    
    This boundary_function detects the similarity between regions in terms of intensity.
    
    @note This function requires the original image to be passed along. That means that
    @link graph_from_labels() has to be called with boundary_term_args set to the
    original image. 
    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param r1_bb The bounding box of the first region, as a list of slice objects.
    @type r1_bb list
    @param r2_bb The bounding box of the second region, as a list of slice objects.
    @type r2_bb list
    @param r1_id The region/node id of the first region.
    @type r1_id int
    @param r2_id The region/node id of the second region.
    @type r2_id int
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    """
    # extract masks marking the voxels covered by each region
    region1_mask = (label_image[r1_bb] == r1_id)
    region2_mask = (label_image[r2_bb] == r2_id)
    # extract the corresponding voxels from the original image
    values1 = original_image[region1_mask]
    values2 = original_image[region2_mask]
    # compute the mean intensities
    mean1 = sum(values1)/float(len(values1))
    mean2 = sum(values2)/float(len(values2))
    # return the absolute difference
    return abs(mean1 - mean2)

def boundary_stawiaski(label_image, r1_bb, r2_bb, r1_id, r2_id, (gradient_image)):
    """
    An implementation of the boundary term in (1), suitable to be used with the
    @link graph_from_labels() function.
    
    Determines for each two supplied regions the voxels forming their border assuming
    ndim*2-connectedness (e.g. 3*2=6 for 3D). From the gradient magnitude values of each
    end-point voxel the border-voxel pairs, the highest one is selected and passed to a
    strictly positive and decreasing function g, which is defined as:
    \f[
        g(x) = \left(\frac{1}{1+|x|}\right)^k
    \f]
    ,where \f$k=2\f$. The final weight \f$w_{i,j}\f$ between two regions \f$r_i\f$ and
    \f$r_j\f$ is then determined by the sum of all these neighbour values:
    \f[
        w = \sum_{e_{m,n}|inF_{(r_i,r_j)}}g(\max(|I(m)|,|I(n)|))
    \f]
    , where \f$F_{(r_i,r_j)}\f$ is the set of border voxel-pairs \f$e_{m,n}\f$ between
    the regions \f$r_i\f$ and \f$r_j\f$ and \f$|I(p)|\f$ the absolute of the gradient
    magnitude at the voxel \f$p\f$
    
    This boundary_function works as an edge indicator in the original image. In simpler
    words the weight (and therefore the energy) is obtained by summing the local contrast
    along the boundaries between two regions.
    
    @note This function requires the gradient magnitude image of the original image to
    be passed along. That means that @link graph_from_labels() has to be called with
    boundary_term_args set to the gradient image. 
    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param r1_bb The bounding box of the first region, as a list of slice objects.
    @type r1_bb list
    @param r2_bb The bounding box of the second region, as a list of slice objects.
    @type r2_bb list
    @param r1_id The region/node id of the first region.
    @type r1_id int
    @param r2_id The region/node id of the second region.
    @type r2_id int
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    """    
    # compute the region of interest (the intersection of the bounding boxes)
    roi = points_to_slices(intersection_unsecure(inflate_rectangle(slices_to_points(r1_bb), 1),
                                                 inflate_rectangle(slices_to_points(r2_bb), 1)))
    
    # prepare strictly positive and decreasing function (Note: input is expected to be a tuple)
    g = lambda x: math.pow(1./(1. + max(map(abs, x))), 2) # k = 2
    
    # prepare iterator lists (parallel iterator over all possible neighbourhood voxels and corresponding value pairs combinations)
    values, labels = __boundary_stawiaski_get_nb_iterators(gradient_image[roi], label_image[roi])
    
    # iterate over values and compute results
    sumand = 0
    for label, value in zip(labels, values):
        if (r1_id, r2_id) == label:
            sumand += g(value)
    # Note: applying a weight to this only will make a difference, when other weights are used somewhere in the graph
    return sumand

def __boundary_stawiaski_get_nb_iterators(image, label_image):
    """Returns iterators over a ndim*2-connectedness neighbourhood parallel over both supplied images."""
    values = []
    labels = []
    for dim in range(image.ndim):
        slices_x = [slice(None, -1 if di == dim else None) for di in range(image.ndim)]
        slices_y = [slice(1 if di == dim else None, None) for di in range(image.ndim)]
        values.extend(zip(image[slices_x].flat,
                          image[slices_y].flat))
        labels.extend(zip(label_image[slices_x].flat,
                          label_image[slices_y].flat))
    return (values, labels)

def inflate_rectangle(rect, val):
    """
    Inflates a rectangle into all directions (dimensions) by the supplied values.
    
    @param rect rectangle defined by its lower-left and upper-right corners
                 (lower_left, uper_right).
    @type rect sequence
    @param val value to inflate the rectangle by
    @type val int
    @return (lower_left, uper_right) with each point being a nD tuple
    @rtype tuple
    """
    return ([max(x - val, 0) for x in rect[0]], [x + val for x in rect[1]])

def slices_to_points(slices):
    """
    Translate a sequence of slice objects into the corner-points of a nD rectangle.
    
    @param slices a sequence of slices
    @type slices sequence
    @return (lower_left, uper_right) with each point being a nD tuple
    @rtype tuple
    """
    return ([sl.start for sl in slices], [sl.stop for sl in slices])

def points_to_slices(rect):
    """
    Translate a nD rectangle defined by its corner points into a sequence of slice
    objects.
    
    @Note: Due to speed considerations it is not checked weather the supplied rectangle
    fulfills all requirements. Supplying male-formed values can lead to unexpected
    results.
    
    @param rect rectangle defined by its lower-left and upper-right corners
                 (lower_left, uper_right).
    @type rect sequence
    @return list of slice objects
    @rtype list
    """
    return [slice(x, y) for x, y in zip(rect[0], rect[1])]

def intersection(rect1, rect2):
    """
    Computes the intersection rectangle of two nD rectangles increased.
    The intersection window marks the area in which the two images bounding boxes
    intersect. The returned rectangle is defined by its lower-left and upper-right
    corner.
    
    @param rect1 The first rectangle defined by its lower-left and upper-right
                  corners (lower_left, uper_right).
    @param rect2 The second rectangle defined by its lower-left and upper-right
                  corners (lower_left, uper_right).
    @return The intersection rectangle defined by its lower-left and upper-right
            corners (lower_left, uper_right) or False if no intersection occurred.
    
    """
    # check if an intersection occurs at all, otherwise return False
    for dim in range(len(rect1[0])):
        if not rect1[0][dim] < rect2[1][dim] and \
               rect1[1][dim] > rect2[0][dim]:
            return False
        
    # otherwise compute intersection cube
    return ([max(x, y) for x, y in zip(rect1[0], rect2[0])], [min(x, y) for x, y in zip(rect1[1], rect2[1])])

def intersection_unsecure(rect1, rect2):
    """
    Computes the intersection rectangle of two nD rectangles increased.
    The intersection window marks the area in which the two images bounding boxes
    intersect. The returned rectangle is defined by its lower-left and upper-right
    corner.
    
    @note this version does not check if an actual intersection occurs. Use with care!
    
    @param rect1 The first rectangle defined by its lower-left and upper-right
                  corners (lower_left, uper_right).
    @param rect2 The second rectangle defined by its lower-left and upper-right
                  corners (lower_left, uper_right).
    @return The intersection rectangle defined by its lower-left and upper-right
            corners (lower_left, uper_right) or False if no intersection occurred.
    
    """ 
    # otherwise compute intersection cube
    return ([max(x, y) for x, y in zip(rect1[0], rect2[0])], [min(x, y) for x, y in zip(rect1[1], rect2[1])])
