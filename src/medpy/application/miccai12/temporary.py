#!/usr/bin/python

"Temporary script for fast executions of code."

# build-in modules
import argparse
import logging

# third-party modules

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from scipy import ndimage


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Temporary scripts.
                  """

# code
def main():
    #degree = 100
    shift = (0, 0, 00)
    plane=(2, 1)
    
    args = getArguments(getParser())
    degree = args.angle

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load input image
    data_input, header_input = load(args.input)
                                      
    # rotate
    data_input = ndimage.interpolation.rotate(data_input, degree, axes=plane, reshape=False)
    data_input[data_input > 0] = 1
    
    # shift
    data_input = ndimage.interpolation.shift(data_input, shift)
    
    # save image
    save(data_input, args.output, header_input, args.force)
    
    logger.info("Successfully terminated.")    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('-a', dest='angle', type=int, help='Rotation angle.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        