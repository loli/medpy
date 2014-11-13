#!/usr/bin/python

"""Fits a label image to a mask."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.filter.label import fit_labels_to_mask


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Fits a label image to a mask.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    contour_dimension = 0
    time_dimension = 3    
    
    # load input volumes
    label_data, _ = load(args.label)
    mask_data, mask_header = load(args.mask)
    
    # prepare result volume
    result_data = scipy.zeros(label_data.shape, scipy.bool_)
    
    # prepare slicer
    slicer = [slice(None)] * label_data.ndim
    
    # iterate over time
    logger.debug('Fitting...')
    for time_id in range(label_data.shape[time_dimension]):
        slicer[time_dimension] = slice(time_id, time_id+1)
        # skip if mask does not contain
        if 0 == len(mask_data[slicer].nonzero()[0]): continue
        # extract spatial volume from all volumes
        mask_data_subvolume = scipy.squeeze(mask_data[slicer])
        label_data_subvolume = scipy.squeeze(label_data[slicer])
        result_data_subvolume = scipy.squeeze(result_data[slicer])
        # apply fitting and append
        result_data_subvolume += fit_labels_to_mask(label_data_subvolume, mask_data_subvolume)
    
    save(result_data, args.output, mask_header, args.force)
        
    logger.info("Successfully terminated.")
    
def fit_labels_to_mask2(image_labels, image_mask):
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
                for t in range(image_labels.shape[3]):
                    entry = collection[image_labels[x,y,z,t]]
                    entry[0] += 1
                    if image_mask[x,y,z,t]: entry[1] += 1
                    entry[2].append((x,y,z,t))
                
    # select labels that are more than half in the mask
    for label in labels:
        if collection[label][0] / 2. >= collection[label][1]:
            del collection[label]
                
    # image_result = numpy.zeros_like(image_mask) this is eq. to image_mask.copy().fill(0), which directly applied does not allow access to the rows and colums: Why?
    image_result = image_mask.copy()
    image_result.fill(False)         

    # add labels to result mask
    for label, data in collection.items():
        for point in data[2]:
            image_result[point] = True
            
    return image_result
    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('label', help='Label volume.')
    parser.add_argument('mask', help='Mask volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main()     