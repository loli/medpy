#!/usr/bin/env python

"""Extracts the position of a binary mask in an image."""

# build-in modules
import argparse
import logging
import sys
import os

# third-party modules
import numpy
from nibabel.loadsave import load

# path changes

# own modules
from medpy.core import Logger


# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes one or more binary masks as input, locates the position of the
                  foreground object, extracts its bounding box and saves the result
                  into a CSV file.
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
    
    # build output file name
    file_csv_name = args.csv + '.csv'
    
    # check if output file exists
    if not args.force:
        if os.path.exists(file_csv_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_csv_name))
            sys.exit(0)
    
    # open output file
    with open(file_csv_name, 'w') as f:
        
        # write header into file
        f.write('image;min_x;min_y;min_z;max_x;max_y;max_z\n')
        
        # iterate over input images
        for image in args.images:
            
            # get and prepare image data
            logger.info('Processing image {}...'.format(image))
            image_data = numpy.squeeze(load(image).get_data())
            
            # count number of labels and flag a warning if they reach the ushort border
            mask = image_data.nonzero()

            # count number of labels and write into file
            f.write('{};{};{};{};{};{};{}\n'.format(image.split('/')[-1],
                                                    mask[0].min(),
                                                    mask[1].min(),
                                                    mask[2].min(),
                                                    mask[0].max(),
                                                    mask[1].max(),
                                                    mask[2].max()))
            
            f.flush()
            
    logger.info('Successfully terminated.')
      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('csv', help='The file to store the results in (\wo suffix).')
    parser.add_argument('images', nargs='+', help='One or more images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()            
    