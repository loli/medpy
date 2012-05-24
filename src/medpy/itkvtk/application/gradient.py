#!/usr/bin/python

"""Executes gradient magnitude filter over images."""

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
__version__ = "r0.2.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Creates a height map of the input images using the gradient magnitude
                  filter.
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_gradient'
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
        
        # build output image name
        image_gradient_name = args.folder + '/' + image.split('/')[-1][:-4] + '_gradient'
        image_gradient_name += image.split('/')[-1][-4:]
        
        # check if output image exists
        if not args.force:
            if os.path.exists(image_gradient_name):
                logger.warning('The output image {} already exists. Skipping this step.'.format(image_gradient_name))
                continue        
        
        # load image as float using ITK
        logger.info('Loading image {} as float using ITK...'.format(image))
        image_type = itk.Image[itk.F, args.dimensions] # causes Eclipse PyDev to complain -> ignore error warning
        reader = itk.ImageFileReader[image_type].New()
        reader.SetFileName(image)
        reader.Update()
        
        logger.debug(itku.getInformation(reader.GetOutput()))
        
        # execute the gradient map filter
        logger.info('Applying gradient map filter...')
        image_gradient = itk.GradientMagnitudeImageFilter[image_type, image_type].New()
        image_gradient.SetInput(reader.GetOutput())
        image_gradient.Update()
        
        logger.debug(itku.getInformation(image_gradient.GetOutput()))
        
        # save file
        logger.info('Saving gradient map as {}...'.format(image_gradient_name))
        writer = itk.ImageFileWriter[image_type].New()
        writer.SetFileName(image_gradient_name)
        writer.SetInput(image_gradient.GetOutput())
        writer.Update()
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created images in.')
    parser.add_argument('images', nargs='+', help='One or more input images.')
    parser.add_argument('--dimensions', dest='dimensions', type=int, default=3, help='Indicate the number of image dimensions. Defaults to three.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        