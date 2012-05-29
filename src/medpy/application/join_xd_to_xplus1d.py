#!/usr/bin/python

"""Joins a number of XD volumes into a (X+1)D volume."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.io import load, save
from medpy.core import Logger
from medpy.core.exceptions import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Joins a number of XD volumes into a (X+1)D volume.
                  The new dimension will be appended to the already existing once.
                  
                  One common use is when a number of 3D volumes, each representing a
                  moment in time, are availabel. With this script they can be joined
                  into a proper 4D volume. 
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
    
    # load first input image as example 
    example_data, example_header = load(args.inputs[0])
    
    # prepare empty output volume
    output_data = scipy.zeros([len(args.inputs)] + list(example_data.shape), dtype=example_data.dtype)
    
    # add first image to output volume
    output_data[0] = example_data
    
    # load input images and add to output volume
    for idx, image in enumerate(args.inputs[1:]):
        image_data, _ = load(image)
        if image_data.dtype != example_data.dtype:
            raise ArgumentError('The dtype {} of image {} differs from the one of the first image {}, which is {}.'.format(image_data.dtype, image, args.inputs[0], example_data.dtype))
        if image_data.shape != example_data.shape:
            raise ArgumentError('The shape {} of image {} differs from the one of the first image {}, which is {}.'.format(image_data.shape, image, args.inputs[0], example_data.shape))
        output_data[idx + 1] = image_data
        
    # swap first and last axis to move new dimension to the end
    output_data = scipy.swapaxes(output_data, 0, -1)
        
    # save created volume
    save(output_data, args.output, example_header, args.force)
        
    logger.info("Successfully terminated.")
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('inputs', nargs='+', help='Source volumes of same shape and dtype.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()
