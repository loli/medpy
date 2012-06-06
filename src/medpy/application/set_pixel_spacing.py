#!/usr/bin/python

"""Manually add pixel spacing to an image file."""

# build-in modules
import argparse
import logging

# third-party modules

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, header, save


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-06-04"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Manually add pixel spacing to an image file
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load input
    data_input, header_input = load(args.input)
    
    # change pixel spacing
    logger.info('Setting pixel spacing along {} to {}...'.format(data_input.shape, args.spacing))
    header.set_pixel_spacing(header_input, args.spacing)
    
    # save file
    save(data_input, args.output, header_input, args.force)
    
    logger.info("Successfully terminated.")    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('spacing', type=float, nargs='+', help='The spacing values.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()