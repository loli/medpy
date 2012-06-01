#!/usr/bin/python

"""Executes the watershed algorithm over images."""

# build-in modules
import argparse
import logging
import os

# third-party modules

# path changes

# own modules
from medpy.io import load, save, get_pixel_spacing
from medpy.core import Logger, ArgumentError
from medpy.itkvtk.filter import watershed


# information
__author__ = "Oskar Maier"
__version__ = "r0.6.0, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Applies the watershed segmentation an image using the supplied
                  parameters.
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
    
    # check if output image exists (will also be performed before saving, but as the watershed might be very time intensity, a initial check can save frustration)
    if not args.force:
        if os.path.exists(args.output):
            raise ArgumentError('The output image {} already exists.'.format(args.output))
    
    # loading image
    data_input, header_input = load(args.input)
    
    # apply the watershed
    logger.info('Watershedding with settings: thr={} / level={}...'.format(args.threshold, args.level))
    data_output = watershed(data_input, get_pixel_spacing(header_input), args.threshold, args.level)

    # save file
    save(data_output, args.output, header_input, args.force)
    
    logger.info('Successfully terminated.')

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='Source volume (usually a gradient image).')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('--level', type=float, default=0.0, help='The level parameter of the ITK watershed filter.')
    parser.add_argument('--threshold', type=float, default=0.0, help='The threshold parameter of the ITK watershed filter.')    
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser
    
if __name__ == "__main__":
    main()        
