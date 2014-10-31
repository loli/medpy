#!/usr/bin/python

"""Creates registration masks from ground-truth or manual markers."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy.ndimage
from scipy.ndimage.morphology import binary_fill_holes

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.core.exceptions import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.1, 2012-08-17"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
    Creates registration masks from ground-truth or manual markers.
    
    Takes either a ground-truth or manual-marker binary 3D volume, selects the first
    basal slice, dilates it and repeats it to form a tube out of it, that  containts
    the RV and the surrounding structures, that are deemed to be most important for
    the registration process.
    
    These include:
        - the complete RV in all slices
        - RV epi- and endocardium
        - black wall around RV and a little bit further
        - A corner of the LV blood-pool
    """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    spatial_dimension = 0
    
    # loading input image
    input_data, input_header = load(args.input)
    
    # check if it has the right dimensions, otherwise cut down to expected number
    if 3 < input_data.ndim:
        _tmp = input_data.shape
        slicer = [slice(0, 1) for _ in range(input_data.ndim)]
        for slid in range(3):
            slicer[slid] = slice(None)
        input_data = scipy.squeeze(input_data[slicer])
        logger.warning('Found more than the expected number of 3 dimensions in the input image. Reduced from shape {} to {}.'.format(_tmp, input_data.shape))
    elif 3 > input_data.ndim:
        raise ArgumentError('Invalid number of image dimensions {}, expects 3.'.format(input_data.ndim))
    
    # if input volume is of type manual markers, remove all above 1
    if 'manual' == args.type:
        logger.info('Extracting foreground markers...')
        input_data[input_data > 1] = 0
    
    # select the first basal slice
    logger.info('Selecting basal slice...')
    slicer = [slice(None) for _ in range(input_data.ndim)]
    basal_slice = None
    for slid in range(input_data.shape[spatial_dimension]):
        slicer[spatial_dimension] = slice(slid, slid + 1)
        if input_data[slicer].any():
            basal_slice = input_data[slicer].astype(scipy.bool_)
            break
        
    # raise error if no slice with values found
    if None == basal_slice:
        raise ArgumentError('The supported input image contains no non-zero data.')
    
    logger.debug('Found basal slice of shape {} at spatial position {} with {} voxels.'.format(basal_slice.shape, slid, len(basal_slice.nonzero()[0])))
    
    # filling eventual holes
    logger.debug('Filling eventual holes...')
    basal_slice[0] = binary_fill_holes(scipy.squeeze(basal_slice)) # !TODO: Use spatial_dimension instead of the 0 here
    
    # dilate the slice
    logger.info('Dilating...')
    basal_slice = scipy.ndimage.binary_dilation(basal_slice, iterations=args.dilations)
    
    logger.debug('{} voxels after dilation with {} iterations.'.format(len(basal_slice.nonzero()[0]), args.dilations))
    
    # build up the tube
    logger.info('Constructing tube...')
    output_data = scipy.concatenate([basal_slice for _ in range(input_data.shape[spatial_dimension])], axis=spatial_dimension)
    
    logger.debug('Shape of constructed tube is {}.'.format(output_data.shape))
    
    # check if resulting shape is valid
    if input_data.shape != output_data.shape:
        raise Exception('The shape of the final data differs with {} of the shape of the original image {}.'.format(output_data.shape, input_data.shape))
    
    # save resulting image
    save(output_data, args.output, input_header, args.force)
        
    logger.info("Successfully terminated.")

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='The ground-truth resp. manual marker volume. Treated as boolean.')
    parser.add_argument('output', help='Target volume. Contains a binary tube.')
    parser.add_argument('type', choices=['ground', 'manual'], help='Whether the supplied input volume contains the ground truth or manual markers.')
    parser.add_argument('--dilations', type=int, default=20, help='The number of dilations to execute. This should normally not be changed.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 
    