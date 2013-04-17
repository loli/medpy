#!/usr/bin/python

"Extracts the first basal slice from a massive 3/4D RV volume."

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save, header
from medpy.io.header import __update_header_from_array_nibabel


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Extracts the first basal slice from a massive 3/4D RV volume.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load input image
    data_input, header_input = load(args.input)
    
    # transform to uin8
    data_input = data_input.astype(scipy.uint8)
                                      
    # reduce to 3D, if larger dimensionality
    if data_input.ndim > 3:
        for _ in range(data_input.ndim - 3): data_input = data_input[...,0]
        
    # iter over slices (2D) until first with content is detected
    for plane in data_input:
        if scipy.any(plane):
            # set pixel spacing
            spacing = list(header.get_pixel_spacing(header_input))
            spacing = spacing[1:3]
            __update_header_from_array_nibabel(header_input, plane)
            header.set_pixel_spacing(header_input, spacing)
            # save image
            save(plane, args.output, header_input, args.force)
            break
    
    logger.info("Successfully terminated.")    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        