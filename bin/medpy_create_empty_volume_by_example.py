#!/usr/bin/python

"""Creates an empty volume with the same attributes as the passes example image."""

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
__version__ = "r0.1.0, 2012-08-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
    Creates an empty volume with the same attributes as the passes example image.
    """

# code
def main():
    args = getArguments(getParser())
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # loading input image
    input_data, input_header = load(args.example)
    
    # create empty volume with same attributes
    output_data = scipy.zeros(input_data.shape, dtype=input_data.dtype)
    
    # save resulting image
    save(output_data, args.output, input_header, args.force)
        
    logger.info("Successfully terminated.")

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('example', help='The example volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 