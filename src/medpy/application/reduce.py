#!/usr/bin/python

"""Executes a reduce operation taking a mask and a number of label images as input."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import numpy
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.filter import fit_labels_to_mask
from medpy.utilities import image_like


# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Reduces label images by fitting them as best as possible to a supplied
                  mask and subsequently creating mask out of them.
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_reduced' attached.
                  For each region the intersection with the reference mask is computed
                  and if the value exceeds 50% of the total region size, it is marked
                  as mask, otherwise as background. For more details on how the fitting
                  is performed @see filter.fit_labels_to_mask.
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
    
    # load mask image
    logger.info('Loading mask {} using NiBabel...'.format(args.mask))
    image_mask = load(args.mask)
    
    # get and prepare mask image data
    image_mask_data = numpy.squeeze(image_mask.get_data())
    image_mask_data = (0 != image_mask_data) # ensures that the mask is of type bool
    
    # iterate over input images
    for image in args.images:

        # build output image name
        image_reduced_name = args.folder + '/' + image.split('/')[-1][:-4] + '_reduced'
        image_reduced_name += image.split('/')[-1][-4:]
        
        # check if output image exists
        if not args.force:
            if os.path.exists(image_reduced_name):
                logger.warning('The output image {} already exists. Skipping this image.'.format(image_reduced_name))
                continue
        
        # load image using nibabel
        logger.info('Loading image {} using NiBabel...'.format(image))
        image_labels = load(image)
        
        # get and prepare image data
        image_labels_data = numpy.squeeze(image_labels.get_data())
        
        # create a mask from the label image
        logger.info('Reducing the label image...')
        image_reduced_data = fit_labels_to_mask(image_labels_data, image_mask_data)
        
        # save resulting mask
        logger.info('Saving resulting mask as {} in the same format as input mask, only with data-type int8...'.format(image_reduced_name))
        image_reduced = image_like(image_reduced_data, image_mask)
        image_reduced.get_header().set_data_dtype(numpy.int8) # bool sadly not recognized
        save(image_reduced, image_reduced_name)
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created images in.')
    parser.add_argument('mask', help='The mask image to which to fit the label images.')
    parser.add_argument('images', nargs='+', help='One or more input label images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        