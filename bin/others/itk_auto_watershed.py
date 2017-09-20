#!/usr/bin/env python

"""Executes the watershed algorithm over images using a image-size based function to determine the best parameters."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import itk

# path changes

# own modules
from medpy.core import Logger
import medpy.itkvtk.utilities.itku as itku


# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Applies the watershed segmentation to a number of images  using a
                  image-size based function to determine the best parameters
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_watershed_[parameters]'
                  attached.
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
    
    # iterate over input images
    for image in args.images:
        
        # load image as float using ITK
        logger.info('Loading image {} as float using ITK...'.format(image))
        image_type = itk.Image[itk.F, 3]
        reader = itk.ImageFileReader[image_type].New()
        reader.SetFileName(image)
        reader.Update()
        
        logger.debug(itku.getInformation(reader.GetOutput()))
        
        # compute ideal parameters
        rs = reader.GetOutput().GetLargestPossibleRegion().GetSize()
        threshold = underfit(rs.GetElement(0) * rs.GetElement(1) * rs.GetElement(2))
        level = 0
        logger.debug('{}, {}, {}'.format(rs.GetElement(0), rs.GetElement(1), rs.GetElement(2)))
        logger.debug('The image contains {} voxels, the resulting threshold is {}.'.format(rs.GetElement(0) * rs.GetElement(1) * rs.GetElement(2), threshold))
        
        # build output image name
        image_watershed_name = args.folder + '/' + image.split('/')[-1][:-4] + '_watershed'
        image_watershed_name += '_thr{}_lvl{}'.format(threshold, level)
        image_watershed_name += image.split('/')[-1][-4:]
        
        # check if output image exists
        if not args.force:
            if os.path.exists(image_watershed_name):
                logger.warning('The output image {} already exists. Skipping this step.'.format(image_watershed_name))
                continue
        
        # initialize the watershed filter object
        image_watershed = itk.WatershedImageFilter[image_type].New()
        image_watershed.SetInput(reader.GetOutput())
        image_watershed.SetThreshold(threshold)
        image_watershed.SetLevel(level)
        
        logger.info('Watershedding with settings: thr={} / level={}...'.format(threshold, level))
        image_watershed.Update()
        
        logger.debug(itku.getInformation(image_watershed.GetOutput()))
        
        # save file
        logger.info('Saving watershed image as {}...'.format(image_watershed_name))
        watershed_image_type = itku.getImageType(image_watershed.GetOutput())
        writer = itk.ImageFileWriter[watershed_image_type].New()
        writer.SetFileName(image_watershed_name)
        writer.SetInput(image_watershed.GetOutput())
        writer.Update()
                
    logger.info('Successfully terminated.')
   
def underfit(size):
    "Computes the ideal threshold from the image size using the under-fit function."
    a = 3.1207310999162396e-10
    b = 0.0033448399543457843
    return size * a + b
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created images in.')
    parser.add_argument('images', nargs='+', help='One or more input images (best in .mhd format).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
