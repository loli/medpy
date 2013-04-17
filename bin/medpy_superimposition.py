#!/usr/bin/python

"""Creates the superimposition image of two label images."""

# build-in modules
from argparse import ArgumentError
import argparse
import logging
import os

# third-party modules
import scipy
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.utilities import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-01-04"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes two label images as input and creates their superimposition i.e.
                  all the regions borders are preserved and the resulting image contains
                  more or the same number of regions as the respective input images.
                  
                  The resulting image has the same name as the first input image, just
                  with a '_superimp' suffix.
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

    # build output image name
    image_superimposition_name = args.folder + '/' + args.image1.split('/')[-1][:-4] + '_superimp'
    image_superimposition_name += args.image1.split('/')[-1][-4:]
        
    # check if output image exists
    if not args.force:
        if os.path.exists(image_superimposition_name):
            raise ArgumentError('The output image {} already exists. Please provide the -f/force flag, if you wish to override it.'.format(image_superimposition_name))
    
    # load image1 using nibabel
    logger.info('Loading gradient image {} using NiBabel...'.format(args.image1))
    image1 = load(args.image1)
    
    # load image2 using nibabel
    logger.info('Loading gradient image {} using NiBabel...'.format(args.image2))
    image2 = load(args.image2)
    
    # extract and prepare data of input images
    image1_data = scipy.squeeze(image1.get_data())
    image2_data = scipy.squeeze(image2.get_data())
        
    # check input images to be valid
    logger.info('Checking input images for correctness...')
    if image1_data.shape != image2_data.shape:
        raise ArgumentError('The two input images shape do not match with 1:{} and 2:{}'.format(image1.shape, image2.shape))
    int_types = (scipy.uint, scipy.uint0, scipy.uint8, scipy.uint16, scipy.uint32, scipy.uint64, scipy.uintc, scipy.uintp,
                 scipy.int_, scipy.int0, scipy.int8, scipy.int16, scipy.int32, scipy.int64, scipy.intc, scipy.intp)
    if image1_data.dtype not in int_types:
        raise ArgumentError('Input image 1 is of type {}, an int type is required.'.format(image1_data.dtype))
    if image2_data.dtype not in int_types:
        raise ArgumentError('Input image 2 is of type {}, an int type is required.'.format(image2_data.dtype))
    if 4294967295 < abs(image1_data.min()) + image1_data.max() + abs(image2_data.min()) + image2_data.max():
        raise ArgumentError('The input images contain so many (or not consecutive) labels, that they will not fit in a uint32 range.')
        
    # create superimposition of the two label images
    logger.info('Creating superimposition image...')
    image_superimposition_data = scipy.zeros(image1_data.shape, dtype=scipy.uint32)
    translation = {}
    label_id_counter = 0
    for x in range(image1_data.shape[0]):
        for y in range(image1_data.shape[1]):
            for z in range(image1_data.shape[2]):
                label1 = image1_data[x,y,z]
                label2 = image2_data[x,y,z]
                if not (label1, label2) in translation:
                    translation[(label1, label2)] = label_id_counter
                    label_id_counter += 1
                image_superimposition_data[x,y,z] = translation[(label1, label2)]
    
    # save resulting superimposition image
    logger.info('Saving superimposition image as {} in the same format as input image 1, only with data-type uint32...'.format(image_superimposition_name))
    image_superimposition = image_like(image_superimposition_data, image1)
    image_superimposition.get_header().set_data_dtype(scipy.uint32) # save as uint32
    save(image_superimposition, image_superimposition_name)
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created superimposition image in.')
    parser.add_argument('image1', help='The first input label image.')
    parser.add_argument('image2', help='The second input label image.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        