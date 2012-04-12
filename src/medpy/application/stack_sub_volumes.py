#!/usr/bin/python

"""Stacks a number of volumes into one dimension."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import os

# third-party modules
import numpy
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError 

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabel import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.2, 2011-03-29"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes a arbitrary number of medical images that are of equal depth in
                  all but one dimension. The images are then stacked on top of each other
                  to produce a single result image. The dimension in which to stack is
                  supplied by the dimension parameter.
                  
                  Note that the supplied images must be of the same data type.
                  Note to take into account the input images orientations.
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
    
    # prepare result file name
    result_name = args.output + args.images[0][-4:]
    
    # check if output image exists
    if not args.force:
        if os.path.exists(result_name):
            logger.warning('The output file {} already exists. Breaking.'.format(result_name))
            exit(1)
    
    # load first image as result image
    logger.info('Loading {}...'.format(args.images[0]))
    try: result_image = load(args.images[0])
    except ImageFileError as e:
        logger.critical('The input image does not exist or its file type is unknown.')
        raise ArgumentError('The input image does not exist or its file type is unknown.', e)
    
    # reduce the image dimensions (nibabel Analyze always assumes 4)
    result_data = numpy.squeeze(result_image.get_data())
    
    # iterate over remaining images and concatenate
    for image_name in args.images[1:]:
        logger.info('Loading {}...'.format(image_name))
        try: image_data = numpy.squeeze(load(image_name).get_data())
        except ImageFileError as e:
            logger.critical('The input image does not exist or its file type is unknown.')
            raise ArgumentError('The input image does not exist or its file type is unknown.', e)  
        
        # change to zero matrix if requested
        if args.zero:
            image_data = numpy.zeros(image_data.shape, image_data.dtype)
        
        #concatenate
        if args.reversed:
            result_data = numpy.concatenate((image_data, result_data), args.dimension)
        else: 
            result_data = numpy.concatenate((result_data, image_data), args.dimension)

    logger.debug('Final image is of shape {}.'.format(result_data.shape))

    # save results in same format as input image
    logger.info('Saving concatenated image as {}...'.format(result_name))
    
    save(image_like(result_data, result_image, [0] * result_data.ndim), result_name)
    
    logger.info('Successfully terminated.')

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('dimension', type=int, help='The dimension in which direction to stack (starting from 0:x).')
    parser.add_argument('output', help='The name (+location) of the output image. Will be of the same file-type as the input images.')
    parser.add_argument('images', nargs='+', help='The images to concatenate/stack.')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-z', dest='zero', action='store_true', help='Add all exept the fist image as empty images.')
    parser.add_argument('-r', dest='reversed', action='store_true', help='Stack in resversed order as how the files are supplied.')
    
    return parser    
    
if __name__ == "__main__":
    main()    