#!/usr/bin/python

"""Executes opening and closing morphological operations over the input image(s)."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import numpy
import scipy.ndimage.morphology
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.utilities import image_like


# information
__author__ = "Oskar Maier"
__version__ = "r0.2, 2011-12-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Executes opening and closing morphological operations over the input image(s).
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
        
    # iterate over input images
    for image in args.images:
        
        # build output file name
        image_smoothed_name = args.folder + '/' + image.split('/')[-1][:-4] + '_postm'
        image_smoothed_name += image.split('/')[-1][-4:]
        
        # check if output file exists
        if not args.force:
            if os.path.exists(image_smoothed_name):
                logger.warning('The output file {} already exists. Skipping.'.format(image_smoothed_name))
                continue
        
        # get and prepare image data
        logger.info('Loading image {} using NiBabel...'.format(image))
        image_original = load(image)
        
        # get and prepare image data
        image_smoothed_data = numpy.squeeze(image_original.get_data())
        
        # perform opening and closing
        if '6c' == args.connectedness:
            footprint = scipy.ndimage.morphology.generate_binary_structure(3, 1)
        elif '18c' == args.connectedness:
            footprint = scipy.ndimage.morphology.generate_binary_structure(3, 2)
        else: # 26c
            footprint = scipy.ndimage.morphology.generate_binary_structure(3, 3)
        if args.reverse:
            logger.info('Applying closing and opening...')
            image_smoothed_data = scipy.ndimage.morphology.binary_closing(image_smoothed_data, footprint)
            image_smoothed_data = scipy.ndimage.morphology.binary_opening(image_smoothed_data, footprint)
        else:
            logger.info('Applying opening and closing...')
            image_smoothed_data = scipy.ndimage.morphology.binary_opening(image_smoothed_data, footprint)
            image_smoothed_data = scipy.ndimage.morphology.binary_closing(image_smoothed_data, footprint)

        # save resulting mask
        logger.info('Saving resulting mask as {} in the same format as input mask...'.format(image_smoothed_name))
        image_smoothed = image_like(image_smoothed_data, image_original)
        save(image_smoothed, image_smoothed_name)
            
    logger.info('Successfully terminated.')
      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The folder to store the results in.')
    parser.add_argument('images', nargs='+', help='One or more mask images.')
    parser.add_argument('-r', dest='reverse', action='store_true', help='Normally opening is applied before closing. Use this switch to reverse the order.')
    parser.add_argument('-c', '--connectedness', dest='connectedness', default='6c', choices=['6c', '18c', '26c'], help='Select the connectedness of the closing/opening element.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()            
    