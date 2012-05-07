#!/usr/bin/python

import argparse
import logging
import sys
import os

import scipy
from nibabel.loadsave import load, save

from medpy.core import Logger
from medpy.utilities import image_like


__description__ = """
                  Takes a list of contour files and creates a contour volume corresponding to the example image.
                  The file names of the contour text files are expect to be in the format
                  IM-0001-{sl-no}-{type}contour-manual where sl-no denotes the
                  corresponding slice number and type to the contour type.
                  """

__contour_types__ = {'icontour': 1,
                     'ocontour': 2,
                     'p1contour': 3,
                     'p2contour': 4}

def main():
    args = getArguments(getParser())
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)    
    
    # test if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists. Breaking.'.format(args.output))
            sys.exit(-1)    
    
    # open example image
    example_image = load(args.example)
    example_data = scipy.squeeze(example_image.get_data())
    
    # create target image
    image_data = scipy.zeros(example_data.shape, dtype=scipy.uint8)
    
    indices = [slice(None)] * image_data.ndim
    
    # iterate over contour files
    for coordinate_file in args.coordinates:
        logger.info('Parsing contour file {}...'.format(coordinate_file))
        
        # extract slice number and contour type from file name
        # example: IM-0001-0009-icontour-manual.txt for slice 9 (both are starting from 0)
        filename = coordinate_file.strip().split('/')[-1].strip().split('-')
        slice_no = int(filename[1])
        contour_type = __contour_types__[filename[2]]
        indices[args.axis] = slice(slice_no, slice_no + 1) # might be subject to change
        
        # open input text file and assign pixels
        with open(coordinate_file) as f:
            for line in f.readlines():
                line = line.strip()
                if '#' == line[0]: continue
                coordinates = map(int, map(round, map(float, line.split(' '))))
                target_slice = scipy.squeeze(image_data[indices]) # hope this creates a view
                target_slice[tuple(coordinates)] = contour_type
    
    # save result contour volume
    logger.info('Saving contour volume as {} in the same format as example image, only with data-type uint8...'.format(args.output))
    image = image_like(image_data, example_image)
    image.get_header().set_data_dtype(scipy.uint8) # save as bool
    save(image, args.output) 

    
    print "Successfully terminated."


def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('example', help='Example image of same dimensions and desired file type as the output image.')
    parser.add_argument('axis', type=int, help='The axis to which to apply the contours (starting from 0).')
    parser.add_argument('output',  help='Target location and name of the created image (incl. suffix).')
    parser.add_argument('coordinates', nargs='+', help='A number of text files containing X and Y coordinates.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')    
    return parser    

if __name__ == "__main__":
    main()        