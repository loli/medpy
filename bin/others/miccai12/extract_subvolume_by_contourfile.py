#!/usr/bin/env python

"""Takes a volume and a contour file and returns the cropped volume free of irrelevant slices."""

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
__version__ = "r0.1.0, 2012-06-26"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes a volume and a contour file and returns the cropped volume free of irrelevant slices.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)

    # load input image
    input_data, input_header = load(args.input)
    
    logger.debug('Old shape={}.'.format(input_data.shape))
    
    # compute cut
    logger.info('Computing cut and cropping volume...')
    cut = __parse_contour_list(args.contours, input_data)
    # crop volume
    input_data = input_data[cut]
    
    logger.debug('New shape={}.'.format(input_data.shape))
    
    # save result contour volume
    save(input_data, args.output, input_header, args.force)

    logger.info("Successfully terminated.")

def __parse_contour_list(clist, arr):
    """
    Parses a contour file and computes from it a bounding box that can be used to cut
    from a 4D volume all irrelevant slices along the axial view (z-axes).
    """ 
    # constants
    no_of_time_slices = 20
    
    # collect all slice numbers
    slices = []
    with open(clist, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if 0 == len(line): continue
            
            contour_file = line.split('\\')[-1]
            slices.append(int(contour_file.split('-')[1]))
            
    # translate slice number to temporal and spatial slices indices
    time_indices = []
    space_indices = [] 
    for idx in slices:
        time_indices.append(idx % no_of_time_slices)
        space_indices.append((idx / no_of_time_slices)) # ! int division desired here
        
    # return border values
    bbox = [slice(None)] * arr.ndim
    bbox[0] = slice(min(space_indices), max(space_indices) + 1)
    return bbox
    

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('contours', help='COntour file.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 