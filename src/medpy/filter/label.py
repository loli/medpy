"""
@package medpy.filter.label
Filter for label images.

Provides a number of filter that work on label images.

Functions:
    - def relabel(label_image, start): Relabel an image.
    - def fit_labels_to_mask(image_labels, image_mask): Assigns all labels of an image either to the foreground or background.
    - def relabel_map(label_image, mapping, key): Relabel a label image according to a mapping.

@author Oskar Maier
@version d0.1.1
@since 2012-02-07
@status Development
"""

# build-in module

# third-party modules
import scipy

# own modules
from ..core.exceptions import ArgumentError

# code
def relabel_map(label_image, mapping, key=lambda x, y: x[y]):
    """
    Relabel an image using the supplied mapping.
    
    The mapping can be any kind of subscriptable object. The respective region id is used
    to access the new value from the mapping. The key keyword parameter can be used to
    supply another access function. The key function must have the signature
    key(mapping, region-id) and return the new region-id to assign.
    
    @param label_image A nD label_image
    @type label_image sequence
    @param mapping A mapping object
    @type mapping subscriptable object
    
    @return A binary image
    @rtype numpy.ndarray
    
    @raise ArgumentError If a region id is missing in the supplied mapping
    """    
    label_image = scipy.array(label_image)
    
    def _map(x):
        try:
            return key(mapping, x)
        except Exception as e:
            raise ArgumentError('No conversion for region id {} found in the supplied mapping. Error: {}'.format(x, e))
    
    vmap = scipy.vectorize(_map, otypes=[label_image.dtype])
         
    return vmap(label_image)

def relabel(label_image, start = 1):
    """ 
    Relabel the regions of a label image.
    Re-processes the labels to make them consecutively and starting from start.
    
    @param label_image a label image
    @type label_image sequence
    @param start the id of the first label to assign
    @type start int
    @return The relabeled image.
    @rtype numpy.ndarray
    """
    label_image = scipy.asarray(label_image)
    mapping = {}
    rav = label_image.ravel()
    for i in range(len(rav)):
        if not rav[i] in mapping:
            mapping[rav[i]] = start
            start += 1
        rav[i] = mapping[rav[i]]
    return rav.reshape(label_image.shape)

def relabel_non_zero(label_image, start = 1):
    """ 
    Relabel the regions of a label image.
    Re-processes the labels to make them consecutively and starting from start.
    Keeps all zero (0) labels, as they are considered background.
    
    @param label_image a label image
    @type label_image sequence
    @param start the id of the first label to assign
    @type start int
    @return The relabeled image.
    @rtype numpy.ndarray
    """
    if start <= 0: raise ArgumentError('The starting value can not be 0 or lower.')
    
    l = list(scipy.unique(label_image))
    if 0 in l: l.remove(0)
    mapping = dict()
    mapping[0] = 0
    for key, item in zip(l, range(start, len(l) + start)):
        mapping[key] = item
    
    return relabel_map(label_image, mapping)


def fit_labels_to_mask(image_labels, image_mask):
    """
    Reduces a label images by overlaying it with a binary mask and assign the labels
    either to the mask or to the background. The resulting binary mask is the nearest
    expression the label image can form of the supplied binary mask.
    
    @param image_labels: A labeled image, i.e., numpy array with labeled regions.
    @type image_labels sequence
    @param image_mask: A mask image, i.e., a binary image with False for background and
                       True for foreground.
    @type image_mask sequence
    @return: A mask image, i.e. a binary image with False for background and True for
             foreground.
    @rtype: numpy.ndarray
             
    @raise ValueError if the input images are not of the same shape, offset or physical
                      spacing.
    """
    image_labels = scipy.asarray(image_labels)
    image_mask = scipy.asarray(image_mask, dtype=scipy.bool_)

    if image_labels.shape != image_mask.shape:
        raise ValueError('The input images must be of the same shape.')
    
    # prepare collection dictionaries
    labels = scipy.unique(image_labels)
    collection = {}
    for label in labels:
        collection[label] = [0, 0, []]  # size, union, points
    
    # iterate over the label images pixels and collect position, size and union
    for x in range(image_labels.shape[0]):
        for y in range(image_labels.shape[1]):
            for z in range(image_labels.shape[2]):
                entry = collection[image_labels[x,y,z]]
                entry[0] += 1
                if image_mask[x,y,z]: entry[1] += 1
                entry[2].append((x,y,z))
                
    # select labels that are more than half in the mask
    for label in labels:
        if collection[label][0] / 2. >= collection[label][1]:
            del collection[label]
                
    # image_result = numpy.zeros_like(image_mask) this is eq. to image_mask.copy().fill(0), which directly applied does not allow access to the rows and colums: Why?
    image_result = image_mask.copy()
    image_result.fill(False)         

    # add labels to result mask
    for label, data in collection.iteritems():
        for point in data[2]:
            image_result[point] = True
            
    return image_result
