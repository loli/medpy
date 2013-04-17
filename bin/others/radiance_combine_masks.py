#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Combines a number of binary masks into an image understood by the Radiance® tool."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import os
import scipy

# third-party modules
from nibabel.loadsave import load, save 

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabel import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.2, 2012-03-26"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Combines a number of binary image segmentation masks into a single mask
                  understood by the Radiance® IOERT planing tool.
                  
                  Supply target image name and a number of binary segmentation images
                  (of which all voxels > 0 are interpretated as foreground) coupled with
                  segmentation identifiers.
                  
                  This tool creates three output files (.hdr, .img, .msk), as expected by
                  the Radiance® inclusion tool.
                  
                  The bit depth of the resulting image is chosen to accommodate the
                  number of input mask and can lie between 8 and 64 unsigned bits.

                  Segmentation mask inside the Radiance® are stored together in one image
                  and allowed to overlap. To import segmentations into Radiance®, the
                  usually employed multiple binary images have to be combined.
                  
                  In the Radiance® segmentation format, each bit of a voxel represents a
                  single segmentation i.e. a voxel with 00000101 in 8-bit format would
                  contain a segmentation voxel for the first and the third mask. 
                  
                  Example usage:
                  radiance_combine_mask output_file mask1.nii Liver mask2.nii Sacrum
                  """

# NOTE on .msk file format
# segmentation1_name <tab> bit <tab> red <tab> green <tab> blue
# segmentation2_name <tab> bit <tab> red <tab> green <tab> blue
# ...

# EXAMPLE of .msk file format
# Liver    1    200    125    0
# Sacrum   4    255    255    45

# List of mask colours. Are repeatED after run out of colours.
__COLOURS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (206, 255, 29), (255, 29, 206), (120, 219, 226), (135, 169, 107), (250, 231, 181), (253, 124, 110), (31, 117, 254), (115, 102, 189), (222, 93, 131), (255, 127, 73), (176, 183, 198), (28, 211, 162), (221, 68, 146)]

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
    
    # build output image name
    output_hdr_name = args.output + '.hdr'
    output_img_name = args.output + '.img'
    output_msk_name = args.output + '.msk'
    
    # check if output image exists
    if not args.force:
        if os.path.exists(output_hdr_name):
            logger.warning('The output header {} already exists. Breaking.'.format(output_hdr_name))
            exit(1)
        elif os.path.exists(output_img_name):
            logger.warning('The output image {} already exists. Breaking.'.format(output_img_name))
            exit(1)
        elif os.path.exists(output_msk_name):
            logger.warning('The output infor file {} already exists. Breaking.'.format(output_msk_name))
            exit(1)
    
    # decide on most suitable bit format        
    if len(args.masks) / 2 <= 8:
        bit_format = scipy.uint8
    elif len(args.masks) / 2 <= 16:
        bit_format = scipy.uint16
    elif len(args.masks) / 2 <= 32:
        bit_format = scipy.uint32
    elif len(args.masks) / 2 <= 64:
        bit_format = scipy.uint64
    else:
        raise ArgumentError('It is not possible to combine more than 64 single masks.')
    
    logger.info('Creating a Radiance® segmentation image in {} bit format...'.format(bit_format))
    
    # loading first mask image as reference and template for saving
    logger.info('Loading mask {} ({} segmentation) using NiBabel...'.format(args.masks[0], args.masks[1]))
    image_mask = load(args.masks[0])
    image_mask_data = scipy.squeeze(image_mask.get_data())
    
    # prepare result image
    image_radiance_data = scipy.zeros(image_mask_data.shape, dtype=bit_format)
    
    logger.debug('Result image is of dimensions {} and type {}.'.format(image_radiance_data.shape, image_radiance_data.dtype))
    
    # preparing .msk file
    f = open(output_msk_name, 'w')
    
    # adding first mask to result image
    image_radiance_data[image_mask_data > 0] = 1
    
    # adding first mask segmentation identifier to the .msk file
    f.write('{}\t1\t{}\t{}\t{}\n'.format(args.masks[1], *__COLOURS[0%len(__COLOURS)]))
            
    for i in range(2, len(args.masks), 2):
        # loading mask image
        logger.info('Loading mask {} ({} segmentation) using NiBabel...'.format(args.masks[i], args.masks[i+1]))
        image_mask_data = scipy.squeeze(load(args.masks[i]).get_data())
        
        # check if the shape of the images is consistent
        if image_mask_data.shape != image_radiance_data.shape:
            raise ArgumentError('Mask {} is with {} of a different shape as the first mask image (which has {}).'.format(args.masks[i], image_mask_data.shape, image_radiance_data.shape))
        
        # adding mask to result image
        image_radiance_data[image_mask_data > 0] += pow(2, i/2)
        
        # adding mask segmentation identifier to the .msk file
        f.write('{}\t{}\t{}\t{}\t{}\n'.format(args.masks[i+1], pow(2, i/2), *__COLOURS[(i/2)%len(__COLOURS)]))

    logger.info('Saving Radiance® segmentation image as {}/.img/.msk...'.format(output_hdr_name))
    image_mask.get_header().set_data_dtype(bit_format)
    save(image_like(image_radiance_data, image_mask), output_hdr_name)
    
    logger.info('Successfully terminated.')
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if 0 != len(args.masks) % 2:
        raise ArgumentError('Every supplied mask image must be followed directly by a string that identifies its segmentation.')
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('output', help='The Radiance® segmentation image to create (\wo suffix).')
    parser.add_argument('masks', nargs="+", help='One or more segmentation input masks and segmentation identifiers. E.g.: mask1.nii Liver mask2.nii Sacrum')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser
    
if __name__ == "__main__":
    main()