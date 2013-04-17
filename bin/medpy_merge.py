#!/usr/bin/python

"""Merges to images into one."""

# build-in modules
import argparse
import logging

# third-party modules

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Merges to images into one.
                  
                  All voxels of the first supplied image that equal False (e.g. zeros),
                  are replaced by the corresponding voxels of the second image.
                  
                  A common use case is the merging of two marker images.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load first input image
    data_input1, header_input1 = load(args.input1)
    
    # load second input image
    data_input2, _ = load(args.input2)
    
    # merge
    data_input1[data_input1 == False] += data_input2[data_input1 == False]

    # save resulting volume
    save(data_input1, args.output, header_input1, args.force)
    
    logger.info("Successfully terminated.")    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input1', help='Source volume one.')
    parser.add_argument('input2', help='Source volume two.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-e', dest='empty', action='store_true', help='Instead of copying the voxel data, create an empty copy conserving all meta-data if possible.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        