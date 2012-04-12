#!/usr/bin/python

"""Executes the watershed algorithm over images."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
import pymorph
import mahotas
from scipy.ndimage.measurements import watershed_ift
from scipy.ndimage.filters import generic_gradient_magnitude, sobel, prewitt
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.utilities import image_like
from medpy.filter.MinimaExtraction import local_minima
from scipy.ndimage.morphology import grey_opening
from scipy import ndimage



# information
__author__ = "Oskar Maier"
__version__ = "a0.3, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Applies the watershed segmentation to a number of images with a range
                  of parameters..
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_watershed_ift'
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
        image_watershed_name = args.folder + '/' + image.split('/')[-1][:-4] + '_watershed_ift'
        image_watershed_name += image.split('/')[-1][-4:]
        
        # check if output image exists
        if not args.force:
            if os.path.exists(image_watershed_name):
                logger.warning('The output image {} already exists. Skipping this image.'.format(image_watershed_name))
                continue
        
        # load image using nibabel
        logger.info('Loading gradient image {} using NiBabel...'.format(image))
        image_gradient = load(image)
        
        # get and prepare image data
        image_gradient_data = scipy.squeeze(image_gradient.get_data())
        
        print "Input image:"
        print image_gradient_data.dtype
        print image_gradient_data.max()
        print image_gradient_data.min()
        
        # convert original image to uint16, squeezing existing data to fit the results
        # uint8 (0 to 255), int16 (0 to 65535), uint32 (0 to 4294967295), uint64 (0 to 18,446,744,073,709,551,615)
        # !TODO: Check this through!
        scale_factor = (65535. - 0.) /  float(image_gradient_data.max() - image_gradient_data.min())
        shift_factor = image_gradient_data.max() - 0.
        image_unsigned_data = (image_gradient_data * scale_factor).round().astype(scipy.int16)
        image_unsigned_data += shift_factor
        image_unsigned_data = image_unsigned_data.astype(scipy.uint16)
        image_unsigned_data = image_unsigned_data.copy()
        
        print "Unsigned image:"
        print image_unsigned_data.dtype
        print image_unsigned_data.max()
        print image_unsigned_data.min()        
        
        # save resulting mask
        logger.info('Saving resulting mask as {} in the same format as input image, only with data-type uint16...'.format("tmp.nii"))
        image_unsigned = image_like(image_unsigned_data, image_gradient)
        image_unsigned.get_header().set_data_dtype(scipy.uint16) # save as uint16
        save(image_unsigned, "tmp.nii")        
        
        # extracting local minima as seedpoints
        logger.info('Executing local minima...')
        local_minima_indices, _ = local_minima(image_unsigned_data)
        image_minima_data = scipy.zeros(image_unsigned_data.shape, dtype=scipy.int32) # output is the same as marker dtype
        #image_minima_data = scipy.zeros_like(image_unsigned_data).astype(scipy.int32) # output is the same as marker dtype
        counter = 0
        
        # the number of local minima is equivalent to the number of final regions created... this allows for an easy adjustment
        print local_minima_indices.shape
        print len(local_minima_indices)
        
        for index in local_minima_indices: # setting consecutive label markes in the positions of the local minima
            image_minima_data[index[0], index[1], index[2]] = counter
            counter += 1
        
        # watershed
        logger.info('Executing the watershed...')
        #image_watershed_data = watershed_ift(image_unsigned_data, image_minima_data) # output is of same dtype as image_minima_data
        image_watershed_data = mahotas.cwatershed(image_unsigned_data, image_minima_data.astype(scipy.uint16), ndimage.generate_binary_structure(3, 1))
        
        print "Watershed image:"
        print image_watershed_data.dtype
        print image_watershed_data.max()
        print image_watershed_data.min() 
        
        # remove original seed points
        logger.info('Removing seed points...')
        image_watershed_data = grey_opening(image_watershed_data, (2,2,2)) # alternatively mode="mirror"
        
        # save resulting mask
        logger.info('Saving watershed image as {} in the same format as input image, only with data-type int32...'.format(image_watershed_name))
        image_watershed = image_like(image_watershed_data, image_gradient)
        image_watershed.get_header().set_data_dtype(scipy.int32) # save as int32
        save(image_watershed, image_watershed_name)
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created images in.')
    parser.add_argument('images', nargs='+', help='One or more input gradient images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        