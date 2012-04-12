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
__version__ = "r1.0, 2011-12-13"
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
        # in 3D case: size 1 = 6-connectedness, 2 = 12-connectedness, 3 = 18-connectedness, etc.
        footprint = scipy.ndimage.morphology.generate_binary_structure(image_smoothed_data.ndim, args.size)
        if 'opening' == args.type:
            logger.info('Applying opening...')
            image_smoothed_data = scipy.ndimage.morphology.binary_opening(image_smoothed_data, footprint, iterations=args.iterations)
        else: # closing
            logger.info('Applying closing...')
            image_smoothed_data = scipy.ndimage.morphology.binary_closing(image_smoothed_data, footprint, iterations=args.iterations)

        # apply additional hole closing step
        logger.info('Closing holes...')
        image_smoothed_data = scipy.ndimage.morphology.binary_fill_holes(image_smoothed_data)

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
    parser.add_argument('-t', '--type', dest='type', choices=['closing', 'opening'], default='closing', help='The type of the morphological operation.')
    #parser.add_argument('-c', '--connectedness', dest='connectedness', default='6c', choices=['6c', '18c', '26c'], help='Select the connectedness of the closing/opening element.')
    parser.add_argument('-i', '--iterations', dest='iterations', default=0, type=int, help='The number of iteration to execute. Supply a value of 1 or higher to restrict the effect of the morphological operation. Otherwise it is applied until saturation.')
    parser.add_argument('-s', '--size', dest='size', default=3, type=int, help='Size of the closing element (>=1). The higher this value, the bigger the wholes that get closed (closing) resp. unconnected elements that are removed (opening). In the 3D case, 1 equals a 6-connectedness, 2 a 12-connectedness, 3 a 18-connectedness, etc.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()            
    