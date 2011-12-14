#!/usr/bin/python

"""Evaluates a number of masks against a reference mask."""

# build-in modules
import argparse
import logging
import sys
import os

# third-party modules
import numpy
import nibabel
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.metric import Volume, Surface
from medpy.core import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "r0.2, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Evaluates a number of masks against a reference mask.
                  The resulting score are saved in the supplied folder as a CSV file
                  with the same name as the reference mask, only with an '_evaluation'
                  as suffix attached.
                  """

# code
# !TODO: Eventually take offsets into account
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
    file_evaluation_name = args.folder + '/' + args.reference.split('/')[-1][:-4] + '_evaluation'
    file_evaluation_name += '.csv'
    
    # check if output file exists
    if not args.force:
        if os.path.exists(file_evaluation_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_evaluation_name))
            sys.exit(0)
    
    # load reference image
    logger.info('Loading reference mask {} using NiBabel...'.format(args.reference))
    image_reference = load(args.reference)
    
    # check if image is of type nifti (currently only supported format)
    # !TODO: Add support for other formats. Problem: getting the physical spacing.
    if not isinstance(image_reference, nibabel.nifti1.Nifti1Image):
        raise ArgumentError('The reference mask is of type {}. Currently only Nifti1 images are supported.'.format(image_reference.__class__.__name__))
    
    # get and prepare reference image data
    image_reference_data = numpy.squeeze(image_reference.get_data())
    image_reference_data = (0 != image_reference_data) # ensures that the reference mask is of type bool
    image_reference_size = len(image_reference_data.nonzero()[0])
    
    # raise exception when the input mask is zero
    if 0 >= image_reference_size:
        raise Exception('The reference mask if of size <= 0.')
    
    # extract pyhsical pixel spacing
    spacing = numpy.array(image_reference.get_header().get_zooms()[0:3])
    
    # open output file
    with open(file_evaluation_name, 'w') as f:
        
        # write header into file
        f.write('{}/{};'.format(args.reference.split('/')[-1], image_reference_size))
        f.write('mask-size;VolumetricOverlapError;RelativeVolumeDifference;AverageSymmetricSurfaceDistance;MaximumSymmetricSurfaceDistance;RootMeanSquareSymmetricSurfaceDistance\n')
        
        # iterate over input images
        for mask in args.masks:
            
            # load mask using nibabel
            logger.info('Loading mask {} using NiBabel...'.format(mask))
            image_mask = load(mask)
            
            if not isinstance(image_mask, nibabel.nifti1.Nifti1Image):
                f.write('Skipped: unsupported image type ({})\n'.format(image_mask.__class__.__name__))
                logger.warning('The mask is of type {}. Currently only Nifti1 images are supported.'.format(image_mask.__class__.__name__))
                continue
            
            # check if physical pixel spacing is coherent
            if not (spacing == numpy.array(image_mask.get_header().get_zooms()[0:3])).all():
                f.write('Skipped: incoherent pixel spacing (reference={}/mask={})\n'.format(spacing, image_mask.get_header().get_zooms()[0:3]))
                logger.warning('The physical pixel spacings of reference ({}) and mask ({}) do not comply. Skip evaluation.'.format(spacing, image_mask.get_header().get_zooms()))
                continue
            
            # get and prepare mask data
            image_mask_data = numpy.squeeze(image_mask.get_data())
            image_mask_data = (0 != image_mask_data) # ensures that the mask is of type bool
            image_mask_size = len(image_mask_data.nonzero()[0])
            
            # write mask name and size into file
            f.write('{};{};'.format(mask.split('/')[-1], image_mask_size))

            # warn when the mask is of size 0 or less
            if 0 >= image_mask_size:
                f.write('Skipped: mask size is 0\n')
                logger.warning('The mask {} is of size <= 0. Skipping evaluation.'.format(mask))
                continue
            
            # skip if reference mask ratio hints to bad results
            if 0.75 > 1. * image_reference_size / image_mask_size or 1.25 < 1. * image_reference_size / image_mask_size:
                f.write('Skipped: reference/mask <0.075 or >1.25\n')
                logger.warning('The reference/mask ration of mask {} is <0.075 or >1.25. Skipping evaluation.'.format(mask))
                continue
            
            # volume metrics
            logger.info('Calculating volume metrics...')
            v = Volume(image_mask_data, image_reference_data)
            f.write('{};{};'.format(v.GetVolumetricOverlapError(),
                                    v.GetRelativeVolumeDifference()))
            
            logger.info('Calculating surface metrics...')
            s = Surface(image_mask_data, image_reference_data, spacing)
            f.write('{};{};{}\n'.format(s.GetAverageSymmetricSurfaceDistance(),
                                        s.GetMaximumSymmetricSurfaceDistance(),
                                        s.GetRootMeanSquareSymmetricSurfaceDistance()))
            
            f.flush()
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the result file in.')
    parser.add_argument('reference', help='The mask image that serves as reference.')
    parser.add_argument('masks', nargs='+', help='One or more mask images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        