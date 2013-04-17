#!/usr/bin/python

"""Extracts a sub-volume from a medical image by an example image."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import sys
import os

# third-party modules
import numpy
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError 
from nibabel.nifti1 import Nifti1Image

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabelu import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-11"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes a medical image of arbitrary dimensions and a binary mask
                  image of the same dimensions. Extract the exact position of the
                  binary mask in the binary mask image and uses these dimensions
                  for the extraction of a sub-volume that lies inside the dimensions
                  of the medical images.
                  Extracts the sub-volume from the supplied image and saves it.
                  
                  Note that both images must be of the same dimensionality, otherwise an exception is thrown.
                  Note that the input images offset is not taken into account except for Nifti images.
                  Note to take into account the input images orientation.
                  
                  This is a convenience script, combining the functionalities of
                  extract_mask_position and extract_sub_volume.
                  """

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load mask
    logger.info('Loading mask {}...'.format(args.mask))
    try: mask_image = numpy.squeeze(load(args.mask).get_data())
    except ImageFileError as e:
        logger.critical('The mask image does not exist or its file type is unknown.')
        raise ArgumentError('The mask image does not exist or its file type is unknown.', e)
    
    # store mask images shape for later check against the input image
    mask_image_shape = mask_image.shape 
    
    # extract the position of the foreground object in the mask image
    logger.info('Extract the position of the foreground object...')
    mask = mask_image.nonzero()
    position = ((max(0, mask[0].min() - args.offset), mask[0].max() + 1 + args.offset), # crop negative values
                (max(0, mask[1].min() - args.offset), mask[1].max() + 1 + args.offset),
                (max(0, mask[2].min() - args.offset), mask[2].max() + 1 + args.offset)) # minx, maxx / miny, maxy / minz, maxz
    
    logger.debug('Extracted position is {}.'.format(position))

    # unload mask and mask image
    del mask
    del mask_image

    # load image
    logger.info('Loading image {}...'.format(args.image))
    try: image = load(args.image)
    except ImageFileError as e:
        logger.critical('The input image does not exist or its file type is unknown.')
        raise ArgumentError('The input image does not exist or its file type is unknown.', e)
    
    # reduce the image dimensions (nibabel Analyze always assumes 4)
    image_data = numpy.squeeze(image.get_data())
    
    # check if the mask image and the input image are of the same shape
    if mask_image_shape != image_data.shape:
        raise ArgumentError('The two input images are of different shape (mask: {} and image: {}).'.format(mask_image_shape, image_data.shape))
    
    # execute extraction of the sub-area  
    logger.info('Extracting sub-volume...')
    index = [slice(x[0], x[1]) for x in position]
    volume = image_data[index]
    
    # check if the output image contains data
    if 0 == len(volume):
        logger.exception('The extracted sub-volume is of zero-size. This usual means that the mask image contained no foreground object.')
        sys.exit(0)
    
    logger.debug('Extracted volume is of shape {}.'.format(volume.shape))
    
    # get base origin of the image
    if image.__class__ == Nifti1Image:
        origin_base = image.get_affine()[:,3][:image_data.ndim]
    else:
        logger.warning('Images in the {} format carry no reliable information about the origin. Assuming and origin of (0,0,0).'.format(image.__class__.__name__))
        origin_base = numpy.array([0] * image_data.ndim)
        
    # modify the volume offset to imitate numpy behavior (e.g. wrap negative values)
    offset = numpy.array([x[0] for x in position])
    for i in range(0, len(offset)):
        if None == offset[i]: offset[i] = 0
    offset[offset<0] += numpy.array(image_data.shape)[offset<0] # wrap around
    offset[offset<0] = 0 # set negative to zero
    
    # calculate final new origin
    origin = origin_base + offset
    
    logger.debug('Final origin created as {} + {} = {}.'.format(origin_base, offset, origin))
    
    # save results in same format as input image
    logger.info('Saving extracted volume...')
    save(image_like(volume, image, origin), args.output + args.image[-4:])
    
    logger.info('Successfully terminated.')

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()    
    # check output image exists if override not forced
    if not args.force:
        if os.path.exists(args.output + args.image[-4:]):
            raise ArgumentError('The supplied output file {} already exists. Run -f/force flag to override.'.format(args.output))

    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('output', help='The name (+location) of the output image \wo suffix. Will be of the same file-type as the input image.')
    parser.add_argument('image', help='A medical image of arbitrary dimensions.')
    parser.add_argument('mask', help='A mask image containing a single foreground object (non-zero).')
    parser.add_argument('-o', '--offset', dest='offset', default=0, type=int, help='Set an offset by which the extracted sub-volume size should be increased in all directions.')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()    
