#!/usr/bin/env python

"""Creates slice background markers for a volume through its reference mask."""

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

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-03-16"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Creates background markers  for a volume through its reference mask.
                  Takes a binary mask image. Producesbakground markers by taking the 
                  minimum and maximum slice in all direction (all in all 6 slices). The
                  generated images are put in the provided directory.
                  
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
    image_bg_name = args.folder + '/' + args.mask.split('/')[-1][:-4] + '.bg'
    image_bg_name += args.mask.split('/')[-1][-4:]
        
    # check if output image exists
    if not args.force:
        if os.path.exists(image_bg_name):
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
    
    # array of indices to access desired slices
    sls = [(slice(1), slice(None), slice(None)),
           (slice(-1, None), slice(None), slice(None)),
           (slice(None), slice(1), slice(None)),
           (slice(None), slice(-1, None), slice(None)),
           (slice(None), slice(None), slice(1)),
           (slice(None), slice(None), slice(-1, None))]
    
    # security check
    logger.info('Determine if the slices are not intersection with the reference liver mask...')
    for sl in sls:
        if not 0 == len(mask_image_data[sl].nonzero()[0]):
            logger.critical('Reference mask reaches till the image border.')
            raise ArgumentError('Reference mask reaches till the image border.')
        
    # create and save background marker image
    logger.info('Creating background marker image...')
    image_bg_data = scipy.zeros(mask_image_data.shape, dtype=scipy.bool_)
    for sl in sls:
        image_bg_data[sl] = True
    
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
    
    parser.add_argument('folder', help='The directory in which to put the generated marker mask.')
    parser.add_argument('mask', help='A mask image containing a single foreground object (non-zero).')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()    
