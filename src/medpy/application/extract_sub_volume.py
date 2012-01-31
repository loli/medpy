#!/usr/bin/python

"""Extracts a sub-volume from a medical image."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import sys
import os

# third-party modules
import numpy
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError 
from nibabel import Nifti1Image

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabel import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-11"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes a medical image of arbitrary dimensions and the dimensions
                  of a sub-volume that lies inside the dimensions of this images.
                  Extracts the sub-volume from the supplied image and saves it.
                  
                  The volume to be extracted is defined by its slices, the syntax is the same as
                  for numpy array indexes (i.e. starting with zero-index, the first literal (x) of any
                  x:y included and the second (y) excluded).
                  E.g. '2:3,4:6' would extract the slice no. 3 in X and 5, 6 in Y direction of a 2D image.
                  E.g. '99:199,149:199,99:249' would extract the respective slices in X,Y and Z direction of a 3D image.
                       This could, for example, be used to extract the area of the liver form a CT scan.
                  To keep all slices in one direction just omit the respective value:
                  E.g. '99:199,149:199,' would work ust as example II, but extract all Z slices.
                       Note here the trailing colon.
                       
                  Note that the volume dimensions must be the same as the image dimensions, otherwise as exception is thrown.
                  Note that the input images offset is not taken into account except for Nifti images.
                  Note that the sub-volume is not checked to actually be inside the image dimensions.
                  Note to take into account the input images orientation when supplying the sub-volume.
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
    
    # load images
    logger.info('Loading {}...'.format(args.image))
    try: image = load(args.image)
    except ImageFileError as e:
        logger.critical('The input image does not exist or its file type is unknown.')
        raise ArgumentError('The input image does not exist or its file type is unknown.', e)
    
    # reduce the image dimensions (nibabel Analyze always assumes 4)
    image_data = numpy.squeeze(image.get_data())
    
    # check image dimensions against sub-volume dimensions
    if len(image_data.shape) != len(args.volume):
        logger.critical('The supplied input image is of different dimension as the sub volume requested ({} to {})'.format(len(image_data.shape), len(args.volume)))
        raise ArgumentError('The supplied input image is of different dimension as the sub volume requested ({} to {})'.format(len(image_data.shape), len(args.volume)))
    
    # execute extraction of the sub-area  
    logger.info('Extracting sub-volume...')
    index = [slice(x[0], x[1]) for x in args.volume]
    volume = image_data[index]
    
    # check if the output image contains data
    if 0 == len(volume):
        logger.exception('The extracted sub-volume is of zero-size. This usual means that the supplied volume coordinates and the image coordinates do not intersect. Exiting the application.')
        sys.exit(0)
    
    logger.debug('Extracted volume is of shape {}.'.format(volume.shape))
    
    # get base origin of the image
    if image.__class__ == Nifti1Image:
        origin_base = image.get_affine()[:,3][:image_data.ndim]
    else:
        logger.warning('Images in the {} format carry no reliable information about the origin. Assuming and origin of (0,0,0).'.format(image.__class__.__name__))
        origin_base = numpy.array([0] * image_data.ndim)
        
    # modify the volume offset to imitate numpy behavior (e.g. wrap negative values)
    offset = numpy.array([x[0] for x in args.volume])
    for i in range(0, len(offset)):
        if None == offset[i]: offset[i] = 0
    offset[offset<0] += numpy.array(image_data.shape)[offset<0] # wrap around
    offset[offset<0] = 0 # set negative to zero
    
    # calculate final new origin
    origin = origin_base + offset
    
    logger.debug('Final origin created as {} + {} = {}.'.format(origin_base, offset, origin))
    
    # save results in same format as input image
    logger.info('Saving extracted volume...')
    save(image_like(volume, image, origin), args.output + args.image[-4:])
    
    logger.info('Successfully terminated.')

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()    
    # check output image exists if override not forced
    if not args.force:
        if os.path.exists(args.output):
            raise ArgumentError('The supplied output file {} already exists.'.format(args.output))
    # parse volume and adapt to zero-indexing
    try:
        def _to_int_or_none(string):
            if 0 == len(string): return None
            return int(string)
        def _to_int_or_none_double (string):
            if 0 == len(string): return [None, None]
            return map(_to_int_or_none, string.split(':'))        
        args.volume = map(_to_int_or_none_double, args.volume.split(','))
        args.volume = [(x[0], x[1]) for x in args.volume]
    except (ValueError, IndexError) as e:
        raise ArgumentError('Maleformed volume parameter "{}", see description with -h flag.'.format(args.volume), e)

    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('image', help='A medical image of arbitrary dimensions.')
    parser.add_argument('output', help='The name (+location) of the output image. Will be of the same file-type as the input image.')
    parser.add_argument('volume', help='The coordinated of the sub-volume of the images that should be extracted.\nExample: 30:59,40:67,45:75 for a 3D image.\nSee -h for more information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()    