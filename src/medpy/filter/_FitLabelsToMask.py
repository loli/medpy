#!/usr/bin/python

"""A function to reduce a label image."""

# build-in modules

# third-party modules
import numpy

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "a0.3, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = "Function to reduce a label image."

# code
def fit_labels_to_mask(image_labels, image_mask):
    """
    Reduces a label images by overlaying it with a binary mask and assign the labels
    either to the mask or to the background. The resulting binary mask is the nearest
    expression the label image can form of the supplied binary mask.
    
    @param image_labels: A labeled image, i.e., numpy array with labeled regions.
    @param image_mask: A mask image, i.e., a binary numpy array with False for
                       background and True for foreground.
    @return: A mask image, i.e. a binary numpy array with False for
             background and True for foreground.
             
    Note that the input images must be of the same shape, offset and physical spacing.
    """
    # !TODO: Write a unittest for this
    # !TODO: Apply the intersection window also for this to deal with different
    #        sized images and with offsets
    if image_labels.shape != image_mask.shape:
        raise ValueError('The input images must be of the same shape.')
    
    # prepare collection dictionaries
    labels = numpy.unique(image_labels)
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

def labels_reduce_old(image_labels, image_mask):
    """
    Reduces a label images by overlaying it with a binary mask and assign the labels
    either to the mask or to the background. The resulting binary mask is the nearest
    expression the label image can form of the supplied binary mask.
    
    @param image_labels: A labeled image, i.e., numpy array with labeled regions.
    @param image_mask: A mask image, i.e., a binary numpy array with False for
                       background and True for foreground.
    @return: A mask image, i.e. a binary numpy array with False for
             background and True for foreground.
             
    Note that the input images must be of the same shape, offset and physical spacing.
    """
    # !TODO: Old version of labels_reduce which speed depends on the number of labels,
    # rather than the image size. By a magnitude slower.
    if image_labels.shape != image_mask.shape:
        raise ValueError('The input images must be of the same shape.')

    # image_result = numpy.zeros_like(image_mask) this is eq. to image_mask.copy().fill(0), which directly applied does not allow access to the rows and colums: Why?
    image_result = image_mask.copy()
    image_result.fill(False)
    
    # create window for the mask image, to iterate only over labels in the mask area
    mask_window = [slice(x.min(), x.max()+1) for x in image_mask.nonzero()]
    
    for label in numpy.unique(image_labels[mask_window]):
        # create image holding only the current label
        image_label = (label == image_labels)
        
        # get the window (slice) of the label and its size (in voxels)
        nz = image_label.nonzero()
        window = [slice(x.min(), x.max()+1) for x in nz]
        size_label = len(nz[0])
        
        # compute the union in the window area
        union = image_label[window] & image_mask [window]
        
        # if the label is more than half in the mask, mark its voxels as foreground
        if size_label / 2. < len(union.nonzero()[0]):
            image_result[window] |= image_label [window]
            
    return image_result

        