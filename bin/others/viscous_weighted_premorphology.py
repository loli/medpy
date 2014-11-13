#!/usr/bin/python

"""Viscous post-morphology operations with arbitrary discrete functions."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
from numpy import histogram
from scipy.ndimage.morphology import generate_binary_structure,\
    iterate_structure, grey_closing
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.utilities import image_like


# information
__author__ = "Oskar Maier"
__version__ = "r0.2, 2011-12-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Perform post-morphology operations over a gradient image as required
                  for a viscous watershed.
                  This step is a pre-processing step that has to be followed by a
                  standard watershed segmentation, but makes it behave as if the
                  a viscous liquid was used.
                  The gradient images histogram is divided into bins roughly containing
                  the same number of voxels and on each a closing operation is performed.
                  The number of bin and the size of the sphere used for the closing over
                  each is determined by the provided discrete function.
                  The resulting image will be saved under the same name and type as the
                  input image, only with an '_wviscous' and its parameters as suffix.
                  See "The viscous watershed transform" by Vachier, Corinne and Meyer,
                  Fernand (Journal of Mathematical Imaging and Vision) for more details.
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
    
    logger.info('Executing weighted viscous morphology with {} ({} bins).'.format(','.join(map(str, args.func)), len(args.func)))
        
    # iterate over input images
    for image in args.images:
        
        # build output file name
        image_viscous_name = args.folder + '/' + image.split('/')[-1][:-4] + '_wviscous_' + '_'.join(map(str, args.func))
        image_viscous_name += image.split('/')[-1][-4:]
        
        # check if output file exists
        if not args.force:
            if os.path.exists(image_viscous_name):
                logger.warning('The output file {} already exists. Skipping this image.'.format(image_viscous_name))
                continue
        
        # get and prepare image data
        logger.info('Loading image {} using NiBabel...'.format(image))
        image_gradient = load(image)
        
        # get and prepare image data
        image_gradient_data = scipy.squeeze(image_gradient.get_data())
        
        # prepare result image and extract required attributes of input image
        if args.debug:
            logger.debug('Intensity range of gradient image is ({}, {})'.format(image_gradient_data.min(), image_gradient_data.max()))
        
        # create gradient images flattened histogram
        bins = hist_flatened(image_gradient_data, len(args.func))
        logger.debug('{} bins created'.format(len(bins) -1))
        
        # check if the number of bins is consistent
        if len(args.func) != len(bins) - 1:
            raise Exception('Inconsistency between the number of requested and created bins ({} to {})'.format(args.sections, len(bins) - 1))
        
        # prepare result file
        image_viscous_data = image_gradient_data
        
        # transform the gradient images topography
        logger.info('Applying the viscous morphological operations on {} sections...'.format(len(args.func)))
        for sl in range(1, len(args.func) + 1):
            
            # create sphere to use in this step
            if 0 >= args.func[sl - 1]: continue # sphere of sizes 0 or below lead to no changes and are not executed
            sphere = iterate_structure(generate_binary_structure(3, 1), args.func[sl - 1]).astype(scipy.int_)
            
            # create masks to extract the affected voxels (i.e. the current slice of the topographic image representation)
            mask_greater = (image_gradient_data >= bins[sl]) # all voxels with are over the current slice
            mask_lower = (image_gradient_data < bins[sl - 1]) # all voxels which are under the current slice
            mask_equal = scipy.invert(mask_greater | mask_lower) # all voxels in the current slice
            
            # extract slice
            image_threshold_data = image_gradient_data.copy()
            image_threshold_data[mask_lower] = 0 # set all voxels under the current slice to zero
            image_threshold_data[mask_greater] = image_threshold_data[mask_equal].max() # set all voxels over the current slice to the max of all voxels in the current slice
            
            logger.debug('{} of {} voxels belong to this level.'.format(len(mask_equal.nonzero()[0]), scipy.prod(image_threshold_data.shape)))            
            
            # apply the closing with the appropriate sphere
            logger.debug('Applying a disk of {} to all values >= {} and < {} (sec {})...'.format(args.func[sl - 1], bins[sl - 1],  bins[sl], sl))
            image_closed_data = grey_closing(image_threshold_data, footprint=sphere)
            
            # add result of this slice to the general results
            image_viscous_data = scipy.maximum(image_viscous_data, image_closed_data)
                    
        # save resulting gradient image
        logger.info('Saving resulting gradient image as {}...'.format(image_viscous_name))
        image_viscous = image_like(image_viscous_data, image_gradient)
        save(image_viscous, image_viscous_name)
            
    logger.info('Successfully terminated.')
      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    args.func = list(map(int, args.func.split(',')))
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The folder to store the results in.')
    parser.add_argument('func', help='The discrete function determining the sphere sizes to use on each bin. Each value has to be comma separated e.g. 1,0,1,2')
    parser.add_argument('images', nargs='+', help='One or more gradient images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser

def hist_flatened(im,nbr_bins=10):
    """
    @param im: the (gray-scale) image as numpy/scipy array
    @param nbr_bins: the number of bins
    @return: the bins of the flattened histogram of the image
    """
    #get image histogram
    imhist, bins = histogram(im.flatten(), 1000)
    
    # only take bins with content into account
    nz = imhist.nonzero()
    imhist = imhist[nz]
    bins = bins[nz]
    
    # prepare iteration
    bins_final = [bins[0]] # set initial bin delimiter
    bins_content = scipy.prod(im.shape) / float(nbr_bins)
    tmp_content = 0
    for i in range(len(imhist) - 1):
        tmp_content += imhist[i]
        if tmp_content >= bins_content: # bin full
            #bins_final.append(bins[i+1]) # add new bin delimiter
            #tmp_content = 0
            div = float(imhist[i]) / (bins_content - (tmp_content - imhist[i])) # what i got / what i want
            bins_final.append(bins[i] + (bins[i+1] - bins[i]) / div) # append a partial bin border, assuming that the dist inside the bin in equal
            tmp_content = imhist[i] - (bins_content - (tmp_content - imhist[i]))
            
    bins_final.append(im.max() + 1) # one added to work against rounding errors
        
    return bins_final
    
if __name__ == "__main__":
    main()            
    