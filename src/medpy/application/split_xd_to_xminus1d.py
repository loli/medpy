#!/usr/bin/python

"""Splits a XD into a number of (X-1)D volumes."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.io import load, save
from medpy.core import Logger


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Splits a XD into a number of (X-1)D volumes.
                  
                  One common use case is the creation of manual markers for 4D images.
                  This script allows to split a 4D into a number of either spatial or
                  temporal 3D volumes, for which one then can create the markers. These
                  can be rejoined using the join_xd_to_xplus1d.py script.
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
    
    # load input image
    data_input, header_input = load(args.input)
    
    # preapre output file string
    name_output = args.output.replace('{}', '{:03d}')
    
    # split and save images
    slices = data_input.ndim * [slice(None)]
    for idx in range(data_input.shape[args.dimension]):
        slices[args.dimension] = slice(idx, idx + 1)
        data_output = scipy.squeeze(data_input[slices])
        save(data_output, name_output.format(idx), header_input, args.force)
        
    logger.info("Successfully terminated.")
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if not '{}' in args.output:
        raise argparse.ArgumentError(args.output, 'The output argument string must contain the seqeunce "{}".')
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume. Has to include the sequence "{}" in the place where the volume number should be placed.')
    parser.add_argument('dimension', type=int, help='The dimension along which to split (starting from 0).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()
