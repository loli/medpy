#!/usr/bin/python

"""Resizes a marker-file along the slice direction (z)."""

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


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Resizes a marker-file along the slice direction (z) by adding
                  "enhancement" empty slices between every two original slices.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    contour_dimension = 2
    
    # load input data
    input_data, input_header = load(args.input)
    
    # create output array
    new_shape = list(input_data.shape)
    new_shape[contour_dimension] = input_data.shape[contour_dimension] + (input_data.shape[contour_dimension] - 1) * args.enhancement
    output_data = scipy.zeros(new_shape, scipy.uint8)
    
    # prepare slicers
    slicer_from = [slice(None)] * input_data.ndim
    slicer_to = [slice(None)] * output_data.ndim
    
    logger.debug('Old shape = {}.'.format(input_data.shape))
    
    # copy data    
    for idx in range(input_data.shape[contour_dimension]):
        slicer_from[contour_dimension] = slice(idx, idx + 1)
        slicer_to[contour_dimension] = slice(idx * (args.enhancement + 1), idx * (args.enhancement + 1) + 1)
        
        output_data[slicer_to] = input_data[slicer_from]
        
    logger.debug('New shape = {}.'.format(output_data.shape))
    
    new_spacing = list(header.get_pixel_spacing(input_header))
    new_spacing[contour_dimension] /= float(args.enhancement + 1)
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
