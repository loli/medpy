#!/usr/bin/python

"""Extracts per-slice surface contours from a binary object image."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
import scipy.ndimage
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError

# path changes

# own modules
from medpy.core import Logger
from medpy.core.exceptions import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "r1.0, 2012-04-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Extracts per-slice surface contours from a binary object image.
                  Takes as input a binary image, extracts the surface of the contained
                  foreground object and saves them per-slice (in the supplied dimension)
                  in the supplied folder.
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
    logger.info('Loading source image {}...'.format(args.input))
    try: 
        input_data = scipy.squeeze(load(args.input).get_data()).astype(scipy.bool_)
    except ImageFileError as e:
        logger.critical('The region image does not exist or its file type is unknown.')
        raise ArgumentError('The region image does not exist or its file type is unknown.', e)
    
    # iterate over designated dimension and create for each such extracted slice a text file
    logger.info('Processing per-slice and writing to files...')
    idx = [slice(None)] * input_data.ndim
    for slice_idx in range(input_data.shape[args.dimension]):
        idx[args.dimension] = slice(slice_idx, slice_idx + 1)
        # 2009: IM-0001-0027-icontour-manual
        file_name = '{}/IM-0001-{:04d}-{}contour-auto.txt'.format(args.target, slice_idx + args.offset, args.ctype)
        # 2012: P01-0080-icontour-manual.txt
        #file_name = '{}/P01-{:04d}-{}contour-auto.txt'.format(args.target, slice_idx + args.offset, args.ctype)
        
        # check if output file already exists
        if not args.force:
            if os.path.exists(file_name):
                logger.warning('The output file {} already exists. Skipping.'.format(file_name))
                continue
        
        # extract current slice
        image_slice = scipy.squeeze(input_data[idx])
        
        # perform some additional morphological operations
        image_slice = scipy.ndimage.morphology.binary_fill_holes(image_slice)
            
        # erode contour in slice
        input_eroded = scipy.ndimage.morphology.binary_erosion(image_slice, border_value=1)
        image_slice ^= input_eroded # xor
        
        # extract contour positions and put into right order
        contour_tmp = image_slice.nonzero()
        contour = [[] for i in range(len(contour_tmp[0]))]
        for i in range(len(contour_tmp[0])):
            for j in range(len(contour_tmp)):
                contour[i].append(contour_tmp[j][i]) # x, y, z, ....
        
        # save contour to file
        logger.debug('Creating file {}...'.format(file_name))
        with open(file_name, 'w') as f:
            for line in contour:
                f.write('{}\n'.format(' '.join(map(str, line))))
                
    logger.info('Successfully terminated.')
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    
    parser.add_argument('input', help='The input binary image containing a single connected object.')
    parser.add_argument('dimension', type=int, help='The dimension over which to extract the per-slice contours.')
    parser.add_argument('ctype', help='The contour type. Can be i or o.')
    parser.add_argument('offset', type=int, help='The slice offset to rightly place the processed sub-volume.')
    parser.add_argument('target', help='The target folder in which to store the generated files.')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    

if __name__ == "__main__":
    main()
    