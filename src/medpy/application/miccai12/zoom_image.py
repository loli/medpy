#!/usr/bin/python

"""Zoom into an image by adding new slices in the z-direction and filling them with interpolated data."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
from scipy.ndimage import interpolation

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save, header


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.2, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Zoom into an image by adding new slices in the z-direction and filling
                  them with interpolated data. Overall "enhancement" new slices will be
                  created between every two original slices.
                  
                  If you want to zoom multiple binary objects in an image without
                  interpolating between their values, use the -o switch.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # check if output image exists
    if not args.force and os.path.exists(args.output):
        logger.warning('The output image {} already exists. Exiting.'.format(args.output))
        exit(-1)
    
    # constants
    contour_dimension = 0
    
    # load input data
    input_data, input_header = load(args.input)
    
    # if normal mode, perform the zoom
    logger.info('Performing normal zoom...')
    output_data, output_header = zoom(input_data, args.enhancement, contour_dimension, hdr=input_header)

    # saving results
    save(output_data, args.output, output_header, args.force)
    
def zoom(image, factor, dimension, hdr = False, order = 3):
    """
    Zooms the provided image by the supplied factor in the supplied dimension.
    The factor is an integer determining how many slices should be put between each
    existing pair.
    If an image header (hdr) is supplied, its voxel spacing gets updated.
    Returns the image and the updated header or false.
    """
    # get logger
    logger = Logger.getInstance()

    logger.debug('Old shape = {}.'.format(image.shape))

    # perform the zoom
    zoom = [1] * image.ndim
    zoom[dimension] = (image.shape[dimension] + (image.shape[dimension] - 1) * factor) / float(image.shape[dimension])
    logger.debug('Reshaping with = {}.'.format(zoom))
    image = interpolation.zoom(image, zoom, order=order)
        
    logger.debug('New shape = {}.'.format(image.shape))
    
    if hdr:
        new_spacing = list(header.get_pixel_spacing(hdr))
        new_spacing[dimension] = new_spacing[dimension] / float(factor + 1)
        logger.debug('Setting pixel spacing from {} to {}....'.format(header.get_pixel_spacing(hdr), new_spacing))
        header.set_pixel_spacing(hdr, tuple(new_spacing))
    
    return image, hdr
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('enhancement', type=int, help='How many slices to put between each original slice.')
    #parser.add_argument('-o', dest='objects', action='store_true', help='Activate this flag to perform the zoom for any binary object in the image separatly.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main()     