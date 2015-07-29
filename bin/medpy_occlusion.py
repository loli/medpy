#!/usr/bin/python

"""
Copyright (C) 2015 Albrecht Kleinfeld and Oskar Maier
This program comes with ABSOLUTELY NO WARRANTY; This is free software,
and you are welcome to redistribute it under certain conditions; see
the LICENSE file or <http://www.gnu.org/licenses/> for details. 
"""

# build-in modules
import argparse
import logging
import os


# third-party modules
from scipy import ndimage
import numpy

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.io.header import get_pixel_spacing


from medpy.occlusion.filters import occlusion_detection, remove_short_branches, component_size_label, gap_closing

# information
__author__ = "Albrecht Kleinfeld and Oskar Maier"
__version__ = "r1.0.0, 2015-07-27"
__email__ = "albrecht.kleinfeld@gmx.de"
__status__ = ""
__description__ = """
                  Finds occlusions in TOF-MRA-images 
                  by using the vesselness-image, 
                  the skeleton and the segmentation of the vessel-tree.
                  An additional mask of the brain could enhance the result.
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
    logger.info('Loading vesselness {}...'.format(args.vesselness))
    image_vesselness_data, image_vesselness_data_header = load(args.vesselness)
    image_vesselness_data = numpy.asarray(ndimage.gaussian_filter(image_vesselness_data, sigma=0.7),numpy.float32)
    
    # load input skeleton
    logger.info('Loading skeleton {}...'.format(args.skeleton))
    image_skeleton_data, image_skeleton_data_header = load(args.skeleton)
    image_skeleton_data = image_skeleton_data.astype(numpy.bool)
    
    # load input segmentation
    logger.info('Loading segmentation {}...'.format(args.segmentation))
    image_segmentation_data, _ = load(args.segmentation)
    image_segmentation_data = image_segmentation_data.astype(numpy.bool)
    
    # check if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists.'.format(args.output))
        if args.skeleton_output and os.path.exists(args.skeleton_output):
            logger.warning('The output of the enhanced centerline {} already exists.'.format(args.skeleton_output))
    
    # loading a mask of the brain
    if args.mask:
        logger.info('Loading the mask of the brain {}...'.format(args.segmentation))
        image_brainmask_data, _ = load(args.mask)
        image_brainmask_data = image_brainmask_data.astype(numpy.bool)
        
        image_skeleton_data = image_skeleton_data * image_brainmask_data
        image_segmentation_data = image_segmentation_data * image_brainmask_data
    
    logger.info('Preparing the skeleton')
    original_image_skeleton_data = image_skeleton_data.copy()
    # removing small components
    image_skeleton_data = component_size_label( image_skeleton_data, numpy.ones((3,3,3) ))
    image_skeleton_data [ image_skeleton_data <= 4 ] = 0
    image_skeleton_data = image_skeleton_data.astype(numpy.bool)
    

    # starting enhancement of centerline
    if not args.switch_off:
        # fill holes in the centerline
        logger.info('Starting to enhance the skeleton')
        image_skeleton_data = ndimage.binary_fill_holes( image_skeleton_data )
        image_skeleton_data = image_skeleton_data.astype(numpy.bool)
        
        # starting to remove short branches
        image_skeleton_data = remove_short_branches( image_skeleton_data, image_vesselness_data, 3, logger)
        original_image_skeleton_data = remove_short_branches( original_image_skeleton_data, image_vesselness_data, 3, logger)
        # closing gaps
        logger.info('Starting to close gaps in the skeleton')
        image_skeleton_data = gap_closing(image_vesselness_data, image_skeleton_data, original_image_skeleton_data, get_pixel_spacing(image_vesselness_data_header), logger)
        
        image_skeleton_data = component_size_label( image_skeleton_data, numpy.ones((3,3,3) ))
        image_skeleton_data [ image_skeleton_data <= 4 ] = 0
        image_skeleton_data = image_skeleton_data.astype(numpy.bool)
        
        
        # save resulting image with enhanced skeleton
        if args.skeleton_output:
            logger.info('Saving resulting image with enhanced skeleton as {}.'.format(args.skeleton_output))
            save(image_skeleton_data.astype(numpy.bool), args.skeleton_output, image_skeleton_data_header, args.force)

        
    # starting detection of occlusions
    image_occlusion = occlusion_detection(image_vesselness_data, image_skeleton_data, image_segmentation_data, get_pixel_spacing(image_vesselness_data_header), logger)

    # save resulting image with occlusion-markers
    logger.info('Saving resulting image with occlusion-markers as {}.'.format(args.output))
    save(image_occlusion, args.output, image_skeleton_data_header, args.force)
    #save(image_occlusion.astype(numpy.bool), args.output, image_skeleton_data_header, args.force)

    logger.info('Successfully terminated.')



def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if not args.vesselness and not args.skeleton and not args.segmentation and not args.output:
        parser.error('needs a vesselness image, the skeleton of the vascular tree, the segmentation of the vascular tree and a path for the output image. An additional mask of the brain could enhance the result.')
        
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('vesselness', help='The vesselness values of the tof-mra image.')
    parser.add_argument('skeleton', help='The skeleton of the vascular tree.')
    parser.add_argument('segmentation', help='The segmentation of the vascular tree.')
    parser.add_argument('output', help='The output image with occlusion markers.')
    
    enhancement_group = parser.add_argument_group('enhancement of the centerline')
    enhancement_group.add_argument('-skeleton_output', help='The output of the enhanced skeleton.')
    enhancement_group.add_argument('-n', dest='switch_off', action='store_true', help='Switches off the enhancement of the skeleton.')
        
    parser.add_argument('-mask', help='The mask of the brain.')
    
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
   
    return parser    
    
    
if __name__ == "__main__":
    main()
