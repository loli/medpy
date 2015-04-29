#!/usr/bin/python

"""
Takes a brain TOF-MRA and finds vessel-occlusion by using a vesselness-image and a skeleton of the vessel-tree.
"""

# build-in modules
import argparse
import logging
import os


# third-party modules
from scipy import ndimage
import numpy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.io.header import get_pixel_spacing


from medpy.occlusion.filters import occlusion_detection

# information
__author__ = "Albrecht Kleinfeld and Oskar Maier"
__version__ = "r0.2.0, 2014-08-25"
__email__ = "albrecht.kleinfeld@gmx.de"
__status__ = ""
__description__ = """
                  input:
                    cen: centerline
                    ves: vesselness of the brain
                    mra: tof-mra image of the brain
                    com: length of branchend
                      
                  Copyright (C) 2014 Albrecht Kleinfeld and Oskar Maier
                  This program comes with ABSOLUTELY NO WARRANTY; This is free software,
                  and you are welcome to redistribute it under certain conditions; see
                  the LICENSE file or <http://www.gnu.org/licenses/> for details.   
                  """

# code
def main():
    parser = getParser()
    args = getArguments(parser)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)


    # load input vesselness and apply gaussian filter
    logger.info('Loading tof-mra image {}...'.format(args.image))
    image_data, image__data_header = load(args.image)
    
    # load input vesselness and apply gaussian filter
    logger.info('Loading vesselness {}...'.format(args.vesselness))
    image_vesselness_data, image_vesselness_data_header = load(args.vesselness)
    image_vesselness_data = numpy.asarray(ndimage.gaussian_filter(image_vesselness_data, sigma=0.7),numpy.float32)
    
    # load input skeleton
    logger.info('Loading skeleton {}...'.format(args.skeleton))
    image_skeleton_data, image_skeleton_data_header = load(args.skeleton)
    image_skeleton_data = image_skeleton_data.astype(numpy.bool)
    
    # load input segmentation
    logger.info('Loading segmentation {}...'.format(args.segmentation))
    image_segmentation_data, image_segmentation_data_header = load(args.segmentation)
    image_segmentation_data = image_segmentation_data.astype(numpy.bool)
    
    # check if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists.'.format(args.output))
        
    image_occlusion = occlusion_detection(image_vesselness_data, image_skeleton_data, image_segmentation_data, get_pixel_spacing(image__data_header), logger)

    # save resulting image with occlusion-markers
    logger.info('Saving resulting image with occlusion-markers as {}.'.format(args.output))
    save(image_occlusion.astype(numpy.bool), args.output, image_skeleton_data_header, args.force)
    
    
    
    logger.info('Successfully terminated.')



def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if not args.image and not args.vesselness and not args.skeleton and not args.segmentation:
        parser.error('needs a tof-mra image, a vesselness image, the skeleton of the vascular tree, the segmentation of the vascular tree')
    
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    
    parser.add_argument('image', help='The original tof-mra image.')
    parser.add_argument('vesselness', help='The vesselness values of the tof-mra image.')
    parser.add_argument('skeleton', help='The skeleton of the vascular tree.')
    parser.add_argument('segmentation', help='The segmentation of the vascular tree.')
    parser.add_argument('output', help='The output image with occlusion markers.')
    
    parser.add_argument('-mask', help='The mask of the brain.')
    
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
   
    return parser    
    
    
if __name__ == "__main__":
    main()
