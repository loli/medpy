#!/usr/bin/env python

"""Creates minimal foreground and background markers for a volume through its reference mask."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import os
import scipy

# third-party modules
import numpy
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError 

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabelu import image_like
from scipy import ndimage

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-03-15"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Creates minimal foreground and background markers for a volume through
                  its reference mask. Takes a binary mask image. Produces a 
                  foreground marker image of the same dimensions with a single voxel
                  seedpoint roughly in the center of the liver. Also produces a
                  background marker image with overall 8 seed points in the farthest
                  corners of the image. The generated images are put in the provided
                  directory.
                  
                  Note that both images must be of the same dimensionality, otherwise an exception is thrown.
                  Note to take into account the input images orientation.
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
    
    # build output image name
    image_fg_name = args.folder + '/' + args.mask.split('/')[-1][:-4] + '.fg'
    image_fg_name += args.mask.split('/')[-1][-4:]
    image_bg_name = args.folder + '/' + args.mask.split('/')[-1][:-4] + '.bg'
    image_bg_name += args.mask.split('/')[-1][-4:]
        
    # check if output image exists
    if not args.force:
        if os.path.exists(image_fg_name):
            logger.warning('The output image {} already exists. Breaking.'.format(image_fg_name))
            exit(1)
        elif os.path.exists(image_bg_name):
            logger.warning('The output image {} already exists. Breaking.'.format(image_bg_name))
            exit(1)
    
    # load mask
    logger.info('Loading mask {}...'.format(args.mask))
    
    try: 
        mask_image = load(args.mask)
        mask_image_data = numpy.squeeze(mask_image.get_data()).astype(scipy.bool_)
    except ImageFileError as e:
        logger.critical('The mask image does not exist or its file type is unknown.')
        raise ArgumentError('The mask image does not exist or its file type is unknown.', e)  
    
    # erode mask stepwise
    logger.info('Step-wise reducing mask to find center...')
    mask_remains = mask_image_data.copy()
    while (True):
        mask_remains_next = ndimage.binary_erosion(mask_remains, iterations=2)
        if 0 == len(mask_remains_next.nonzero()[0]):
            break
        mask_remains = mask_remains_next
    
    # extract one of the remaining voxels
    voxels = mask_remains.nonzero()
    marker = (voxels[0][0], voxels[1][0], voxels[2][0])
    
    logger.debug('Extracted foreground seed is {}.'.format(marker))
    
    # check suitability of corners as background markers
    logger.info('Checking if the corners are suitable background seed candidates...')
    if True == mask_image_data[0,0,0] or \
       True == mask_image_data[-1,0,0] or \
       True == mask_image_data[0,-1,0] or \
       True == mask_image_data[0,0,-1] or \
       True == mask_image_data[-1,-1,0] or \
       True == mask_image_data[-1,0,-1] or \
       True == mask_image_data[0,-1,-1] or \
       True == mask_image_data[-1,-1,-1]:
        logger.critical('The corners of the image do not correspond to background voxels.')
        raise ArgumentError('The corners of the image do not correspond to background voxels.')
    
    # create and save foreground marker image
    logger.info('Creating foreground marker image...')
    image_fg_data = scipy.zeros(mask_image_data.shape, dtype=scipy.bool_)
    image_fg_data[marker[0], marker[1], marker[2]] = True

    logger.info('Saving foreground marker image...')
    mask_image.get_header().set_data_dtype(scipy.int8)
    save(image_like(image_fg_data, mask_image), image_fg_name)

    # create and save background marker image
    logger.info('Creating background marker image...')
    image_bg_data = scipy.zeros(mask_image_data.shape, dtype=scipy.bool_)
    image_bg_data[0,0,0] = True
    image_bg_data[-1,0,0] = True
    image_bg_data[0,-1,0] = True
    image_bg_data[0,0,-1] = True
    image_bg_data[-1,-1,0] = True
    image_bg_data[-1,0,-1] = True
    image_bg_data[0,-1,-1] = True
    image_bg_data[-1,-1,-1] = True
    
    logger.info('Saving background marker image...')
    mask_image.get_header().set_data_dtype(scipy.int8)
    save(image_like(image_bg_data, mask_image), image_bg_name)
    
    logger.info('Successfully terminated.')

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('folder', help='The directory in which to put the generated masks.')
    parser.add_argument('mask', help='A mask image containing a single foreground object (non-zero).')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()    
