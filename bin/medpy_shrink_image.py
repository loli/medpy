#!/usr/bin/python

"""Shrink an image by skipping every the slides between every x slides."""

# build-in modules
import argparse
import logging

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
    Shrinks an image by discarding slices. Reverse operation of zoom_image.py.
    Reduces the image by keeping one slice, then discarding "discard" slices, then
    keeping the next and so on.
    """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    contour_dimension = 0
    
    # load input data
    input_data, input_header = load(args.input)
    
    logger.debug('Old shape = {}.'.format(input_data.shape))
    
    # compute new shape
    new_shape = list(input_data.shape)
    new_shape[contour_dimension] = 1 + (new_shape[contour_dimension] - 1) / (args.discard + 1)
    
    # prepare output image
    output_data = scipy.zeros(new_shape, dtype=input_data.dtype)
    
    # prepare slicers
    slicer_in = [slice(None)] * input_data.ndim
    slicer_out = [slice(None)] * input_data.ndim
    
    # prepare skip-counter and output image slice counter
    skipc = 0
    slicec = 0
    
    logger.debug('Shrinking from {} to {}...'.format(input_data.shape, new_shape))
    for idx in range(input_data.shape[contour_dimension]):
        
        if 0 == skipc:
            # transfer slice
            slicer_in[contour_dimension] = slice(idx, idx + 1)
            slicer_out[contour_dimension]  = slice(slicec, slicec + 1)
            output_data[slicer_out] = input_data[slicer_in]
            
            # resert resp. increase counter
            skipc = args.discard
            slicec += 1
            
        else: # skip slice
            # decrease skip counter
            skipc -= 1

    
    # set new pixel spacing
    new_spacing = list(header.get_pixel_spacing(input_header))
    new_spacing[contour_dimension] = new_spacing[contour_dimension] * float(args.discard + 1)
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
    parser.add_argument('discard', type=int, help='How many slices to discard between each two slices which are kept.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main()     