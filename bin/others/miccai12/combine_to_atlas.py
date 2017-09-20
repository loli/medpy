#!/usr/bin/env python

"""Combines a number of binary images to an atlas with values between 0 and 1."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-06-15"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
    Combines a number of binary images to an atlas with values between 0 and 1.
    """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)  
    
    # load first input volume as example
    input_data, input_header = load(args.inputs[0])
    
    # create target array
    output_data = scipy.zeros(input_data.shape, scipy.float32)
    
    # add first input mask
    output_data += input_data
    
    # iterate over input masks, load them and add them to the output volume
    logger.info('Iterating over input masks...')
    for input_name in args.inputs[1:]:
        input_data, _ = load(input_name)
        output_data += input_data
        
    # divide by number of input files
    output_data /= float(len(args.inputs))
    
    logger.debug('Max and min values in created atlas are {} and {}.'.format(output_data.max(), output_data.min()))
    
    # save created image
    logger.info('Saving atlas...')
    save(output_data, args.output, input_header, args.force)
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('output', help='The target volume.')
    parser.add_argument('inputs', nargs='+', help='A number of binary mask files.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main()     