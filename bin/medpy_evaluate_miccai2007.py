#!/usr/bin/python

"""
Evaluates a number of masks against a reference mask.


Copyright (C) 2013 Oskar Maier

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

# build-in modules
import argparse
import logging
import sys

# third-party modules
import numpy

# path changes

# own modules
from medpy.core import Logger
from medpy.metric import Volume, Surface
from medpy.io import get_pixel_spacing, load


# information
__author__ = "Oskar Maier"
__version__ = "r0.4.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Evaluates a number of masks against a reference mask.
                  The resulting score i printed to the stdout in a CSV format.
                  
                  The applied evaluation metrics are taken from the 'MICCAI 2007 Grand
                  Challenge'. For more details @see metric.Surface, @see metric.Volume
                  and the MICCAI07 Challenge Paper "Comparison and Evaluation of Methods
                  for Liver Segmentation From CT Datasets", Heiman, T. et al., IEEE
                  Transactions on Medical Imaging, Vol.28, No.8, Aug. 2009
                  
                  Copyright (C) 2013 Oskar Maier
                  This program comes with ABSOLUTELY NO WARRANTY; This is free software,
                  and you are welcome to redistribute it under certain conditions; see
                  the LICENSE file or <http://www.gnu.org/licenses/> for details.   
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
    
    # load reference image
    image_reference_data, image_reference_header = load(args.reference)
    
    # prepare reference image data
    image_reference_data = (0 != image_reference_data) # ensures that the reference mask is of type bool
    image_reference_size = len(image_reference_data.nonzero()[0])
    
    # raise exception when the input mask is zero
    if 0 >= image_reference_size:
        raise Exception('The reference mask if of size <= 0.')
    
    # extract pyhsical pixel spacing
    spacing = numpy.array(get_pixel_spacing(image_reference_header))
    
    # print header if requested
    if args.header:
        print '{}/{};'.format(args.reference.split('/')[-1], image_reference_size) ,
        print 'mask-size;VolumetricOverlapError;RelativeVolumeDifference;AverageSymmetricSurfaceDistance;MaximumSymmetricSurfaceDistance;RootMeanSquareSymmetricSurfaceDistance'
    
    # load mask using nibabel
    image_mask_data, image_mask_header = load(args.input)
            
    # check if physical pixel spacing is coherent
    mask_spacing = numpy.array(get_pixel_spacing(image_mask_header))
    if not (spacing == mask_spacing).all():
        if not args.ignore:
            print 'Stopped. Incoherent pixel spacing (reference={}/mask={})\n'.format(spacing, mask_spacing)
            logger.warning('The physical pixel spacings of reference ({}) and mask ({}) do not comply. Breaking evaluation.'.format(spacing, mask_spacing))
            sys.exit(-1)
        else:
            logger.warning('The physical pixel spacings of reference ({}) and mask ({}) do not comply. Evaluation continued nevertheless, as ignore flag is set.'.format(spacing, mask_spacing))
            
    # prepare mask data
    image_mask_data = (0 != image_mask_data) # ensures that the mask is of type bool
    image_mask_size = len(image_mask_data.nonzero()[0])
    
    # write mask name and size into file
    print '{};{}'.format(args.input.split('/')[-1], image_mask_size) ,

    # warn when the mask is of size 0 or less
    if 0 >= image_mask_size:
        print ';Skipped: mask size is 0'
        logger.warning('The mask is of size <= 0. Breaking evaluation.')
        sys.exit(-1)
    
    # skip if reference mask ratio hints to bad results
    if 0.75 > 1. * image_reference_size / image_mask_size or 1.25 < 1. * image_reference_size / image_mask_size:
        print ';Skipped: reference/mask <0.075 or >1.25'
        logger.warning('The reference/mask ration of the mask is <0.075 or >1.25. Breaking evaluation.')
        sys.exit(-1)
    
    # volume metrics
    logger.info('Calculating volume metrics...')
    v = Volume(image_mask_data, image_reference_data)
    print ';{};{}'.format(v.get_volumetric_overlap_error(),
                            v.get_relative_volume_difference()) ,
    
    logger.info('Calculating surface metrics...')
    s = Surface(image_mask_data, image_reference_data, spacing)
    print ';{};{};{}'.format(s.get_average_symmetric_surface_distance(),
                               s.get_maximum_symmetric_surface_distance(),
                               s.get_root_mean_square_symmetric_surface_distance())

    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('reference', help='The mask image that serves as reference.')
    parser.add_argument('input', help='The mask image to evaluate.')
    parser.add_argument('-p', dest='header', action='store_true', help='Also print a CSV header line.')
    parser.add_argument('-i', dest='ignore', action='store_true', help='Ignore a mismatch of the voxel spacing. A warnign will still be signaled.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
