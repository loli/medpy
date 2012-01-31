#!/usr/bin/python

"""Executes gradient magnitude filter over images."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
from scipy.ndimage.filters import generic_gradient_magnitude, prewitt
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.utilities import image_like



# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Creates a height map of the input images using the gradient magnitude
                  filter.
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_gradient'
                  attached.
                  Note that this script produces the same results as
                  @see itkvtk.application.batch_gradient, but is implemented in pure
                  Python, instead of using ITKs GradientMagnitudeImageFilter. 
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
        
        # build output image name
        image_gradient_name = args.folder + '/' + image.split('/')[-1][:-4] + '_gradient'
        image_gradient_name += image.split('/')[-1][-4:]
        
        # check if output image exists
        if not args.force:
            if os.path.exists(image_gradient_name):
                logger.warning('The output image {} already exists. Skipping this step.'.format(image_gradient_name))
                continue        
        
        # load image using nibabel
        logger.info('Loading image {} using NiBabel...'.format(image))
        image_original = load(image)
        
        # get and prepare image data
        image_original_data = scipy.squeeze(image_original.get_data())
        
        # prepare result image
        image_gradient_data = image_original_data.astype(scipy.float32)
        
        # apply the gradient magnitude filter
        logger.info('Computing the gradient magnitude with Prewitt operator...')
        generic_gradient_magnitude(image_original_data, prewitt, output=image_gradient_data) # alternative to prewitt is sobel
        
        # save resulting mask
        logger.info('Saving resulting mask as {} in the same format as input image, only with data-type float32...'.format(image_gradient_name))
        image_gradient = image_like(image_gradient_data, image_original)
        image_gradient.get_header().set_data_dtype(scipy.float32)
        save(image_gradient, image_gradient_name)
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created images in.')
    parser.add_argument('images', nargs='+', help='One or more input images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        