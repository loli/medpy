#!/usr/bin/python

"""Evaluates a number of masks against a reference mask."""

# build-in modules
import argparse
import logging
import sys
import os

# third-party modules
import numpy

# path changes

# own modules
from medpy.core import Logger
from medpy.metric import Volume, Surface
from medpy.io import get_pixel_spacing
from medpy import io


# information
__author__ = "Oskar Maier"
__version__ = "r0.3.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Evaluates a number of masks against a reference mask.
                  The resulting score are saved in the supplied folder as a CSV file
                  with the same name as the reference mask, only with an '_evaluation'
                  as suffix attached.
                  The applied evaluation metrics are taken from the 'MICCAI 2007 Grand
                  Challenge'. For more details @see metric.Surface, @see metric.Volume
                  and the MICCAI07 Challenge Paper "Comparison and Evaluation of Methods
                  for Liver Segmentation From CT Datasets", Heiman, T. et al., IEEE
                  Transactions on Medical Imaging, Vol.28, No.8, Aug. 2009
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
    file_evaluation_name = '{}.csv'.format(args.output)
    
    # check if output file exists
    if not args.force:
        if os.path.exists(file_evaluation_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_evaluation_name))
            sys.exit(0)
    
    # load reference image
    image_reference_data, image_reference_header = io.load(args.reference)
    
    # prepare reference image data
    image_reference_data = (0 != image_reference_data) # ensures that the reference mask is of type bool
    image_reference_size = len(image_reference_data.nonzero()[0])
    
    # raise exception when the input mask is zero
    if 0 >= image_reference_size:
        raise Exception('The reference mask if of size <= 0.')
    
    # extract pyhsical pixel spacing
    spacing = numpy.array(get_pixel_spacing(image_reference_header))
    
    # open output file
    with open(file_evaluation_name, 'w') as f:
        
        # write header into file
        f.write('{}/{};'.format(args.reference.split('/')[-1], image_reference_size))
        f.write('mask-size;VolumetricOverlapError;RelativeVolumeDifference;AverageSymmetricSurfaceDistance;MaximumSymmetricSurfaceDistance;RootMeanSquareSymmetricSurfaceDistance\n')
        
        # iterate over input images
        for mask in args.masks:
            
            # load mask using nibabel
            image_mask_data, image_mask_header = io.load(mask)
            
            # check if physical pixel spacing is coherent
            mask_spacing = numpy.array(get_pixel_spacing(image_mask_header))
            if not (spacing == mask_spacing).all():
                if not args.ignore:
                    f.write('Skipped: incoherent pixel spacing (reference={}/mask={})\n'.format(spacing, mask_spacing))
                    logger.warning('The physical pixel spacings of reference ({}) and mask ({}) do not comply. Skip evaluation.'.format(spacing, mask_spacing))
                    continue
                logger.warning('The physical pixel spacings of reference ({}) and mask ({}) do not comply. Evaluation continued nevertheless, as ignore flag is set.'.format(spacing, mask_spacing))
            
            # prepare mask data
            image_mask_data = (0 != image_mask_data) # ensures that the mask is of type bool
            image_mask_size = len(image_mask_data.nonzero()[0])
            
            # write mask name and size into file
            f.write('{};{}'.format(mask.split('/')[-1], image_mask_size))

            # warn when the mask is of size 0 or less
            if 0 >= image_mask_size:
                f.write(';Skipped: mask size is 0\n')
                logger.warning('The mask {} is of size <= 0. Skipping evaluation.'.format(mask))
                continue
            
            # skip if reference mask ratio hints to bad results
            if 0.75 > 1. * image_reference_size / image_mask_size or 1.25 < 1. * image_reference_size / image_mask_size:
                f.write(';Skipped: reference/mask <0.075 or >1.25\n')
                logger.warning('The reference/mask ration of mask {} is <0.075 or >1.25. Skipping evaluation.'.format(mask))
                continue
            
            # volume metrics
            logger.info('Calculating volume metrics...')
            v = Volume(image_mask_data, image_reference_data)
            f.write(';{};{}'.format(v.get_volumetric_overlap_error(),
                                    v.get_relative_volume_difference()))
            
            logger.info('Calculating surface metrics...')
            s = Surface(image_mask_data, image_reference_data, spacing)
            f.write(';{};{};{}'.format(s.get_average_symmetric_surface_distance(),
                                       s.get_maximum_symmetric_surface_distance(),
                                       s.get_root_mean_square_symmetric_surface_distance()))

            f.write('\n')
            f.flush()
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('output', help='Name of the resulting evaluation file (\wo suffix).')
    parser.add_argument('reference', help='The mask image that serves as reference.')
    parser.add_argument('masks', nargs='+', help='One or more mask images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    parser.add_argument('-i', dest='ignore', action='store_true', help='Ignore a mismatch of the voxel spacing. A warnign will still be signaled.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
