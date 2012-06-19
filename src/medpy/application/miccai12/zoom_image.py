#!/usr/bin/python

"""Zoom into an image by adding new slices in the z-direction and filling them with interpolated data."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save, header
from scipy.ndimage import interpolation


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Zoom into an image by adding new slices in the z-direction and filling
                  them with interpolated data. Overall "enhancement" new slices will be
                  created between every two original slices.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # check if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists. Exiting.'.format(args.output))
            exit(-1)
    
    # constants
    contour_dimension = 0
    
    # load input data
    input_data, input_header = load(args.input)
    
    logger.debug('Old shape = {}.'.format(input_data.shape))
    
    # perform the zoom
    zoom = [1] * input_data.ndim
    zoom[contour_dimension] = (input_data.shape[contour_dimension] + (input_data.shape[contour_dimension] - 1) * args.enhancement) / float(input_data.shape[contour_dimension])
    logger.debug('Reshaping with = {}.'.format(zoom))
    output_data = interpolation.zoom(input_data, zoom)
        
    logger.debug('New shape = {}.'.format(output_data.shape))
    
    new_spacing = list(header.get_pixel_spacing(input_header))
    new_spacing[contour_dimension] = new_spacing[contour_dimension] / float(args.enhancement + 1)
    logger.debug('Setting pixel spacing from {} to {}....'.format(header.get_pixel_spacing(input_header), new_spacing))
    header.set_pixel_spacing(input_header, tuple(new_spacing))
    
    save(output_data, args.output, input_header, args.force)
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('enhancement', type=int, help='How many slices to put between each original slice.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main()     