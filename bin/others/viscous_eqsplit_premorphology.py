#!/usr/bin/env python

"""Executes morphological operations over a gradient image on different levels."""

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
__version__ = "r0.3, 2011-12-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes a gradient image as input and performs on various levels of its
                  topographic representation morphological closing operations as required
                  by the viscous watershed. This step is a pre-processing step that has
                  to be followed by a standard watershed segmentation, but makes it
                  behave as if the a viscous liquid was used.
                  To separate the gradient image into different regions, its topography
                  is considered and the morphological closing in applied to vertical
                  slices of said topographical representation.
                  To take into account the different range of intensity values (and
                  therefore different heights of the topography) that can appear,
                  a histogram of the images intensity values is created and subsequently
                  equalized. This way the vertical slices are of different size but
                  contain nearly exactely the same amount of pixels.
                  This step becomes especially important when the input image contains
                  very steep gradients, as may for example appear if a metal implant
                  is inside the scan range (metal being of a high density and leading
                  to very bright spots).
                  The provided 'sections' parameter determines the number of bin of the
                  equalized histogram and therefore the number of slices in which the
                  topography is split.
                  The 'dsize' parameter determines the sizxe of the biggest disc applied
                  in the closing operation. In each subsequent slice a smaller disc is
                  applied.
                  The resulting image will be saved under the same name and type as the
                  input image, only with an '_viscous' and its parameters as suffix.
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
    
    logger.info('Selected viscous type is {}'.format(args.type))
    
    # iterate over input images
    for image in args.images:
        
        # get and prepare image data
        logger.info('Loading image {} using NiBabel...'.format(image))
        image_gradient = load(image)
        
        # get and prepare image data
        image_gradient_data = scipy.squeeze(image_gradient.get_data())
        
        logger.debug('Intensity range of gradient image is ({}, {})'.format(image_gradient_data.min(), image_gradient_data.max()))
        
        # build output file name and check for its existence, if not in sections mode
        if 'sections' != args.type:
            # build output file name
            image_viscous_name = args.folder + '/' + image.split('/')[-1][:-4] + '_viscous_{}_sec_{}_ds_{}'.format(args.type, args.sections, args.dsize)
            image_viscous_name += image.split('/')[-1][-4:]
        
            # check if output file exists
            if not args.force:
                if os.path.exists(image_viscous_name):
                    logger.warning('The output file {} already exists. Skipping this image.'.format(image_viscous_name))
                    continue
                

        # execute plain closing i.e. a closing operation over the whole image, if in plain mode
        if 'plain' == args.type:
            # prepare the disc structure (a ball with a diameter of (args.dsize * 2 + 1))
            disc = iterate_structure(generate_binary_structure(3, 1), args.dsize).astype(scipy.int_)
            
            # apply closing
            logger.info('Applying the morphology over whole image at once...')
            image_viscous_data = grey_closing(image_gradient_data, footprint=disc)
            
            # save resulting gradient image
            logger.info('Saving resulting gradient image as {}...'.format(image_viscous_name))
            image_viscous = image_like(image_viscous_data, image_gradient)
            save(image_viscous, image_viscous_name)
            
            # skip other morphologies
            continue
        
        
        # create gradient images flattened histogram
        bins = hist_flatened(image_gradient_data, args.sections)
        logger.debug('{} bins created'.format(len(bins) - 1))
        
        # check if the number of bins is consistent
        if args.sections != len(bins) - 1:
            raise Exception('Inconsistency between the number of requested and created bins ({} to {})'.format(args.sections, len(bins) - 1))
        
        # prepare result file
        image_viscous_data = image_gradient_data
        
        # transform the gradient images topography (Note: the content of one bin is: bins[slice - 1] <= content < bins[slice] 
        logger.info('Applying the viscous morphological operations {} times...'.format(args.sections))
        for slice in range(1, args.sections + 1):
            
            # build output file name and check for its existence, if in sections mode
            if 'sections' == args.type:
                # build output file name
                image_viscous_name = args.folder + '/' + image.split('/')[-1][:-4] + '_viscous_{}_sec_{}_ds_{}_sl_{}'.format(args.type, args.sections, args.dsize, slice)
                image_viscous_name += image.split('/')[-1][-4:]
            
                # check if output file exists
                if not args.force:
                    if os.path.exists(image_viscous_name):
                        logger.warning('The output file {} already exists. Skipping this slice.'.format(image_viscous_name))
                        continue
                
                # prepare result file
                image_viscous_data = image_gradient_data

            
            # create masks to extract the affected voxels (i.e. the current slice of the topographic image representation)
            mask_greater = (image_gradient_data >= bins[slice]) # all voxels with are over the current slice
            mask_lower = (image_gradient_data < bins[slice - 1]) # all voxels which are under the current slice
            mask_equal = scipy.invert(mask_greater | mask_lower) # all voxels in the current slice
            if 'mercury' == args.type:
                dsize = int((args.dsize / float(args.sections)) * (slice))
                disc = iterate_structure(generate_binary_structure(3, 1), dsize).astype(scipy.int_)
                mask_equal_or_greater = mask_equal | mask_greater
                image_threshold_data = image_gradient_data * mask_equal_or_greater
            elif 'oil' == args.type:
                dsize = int((args.dsize / float(args.sections)) * (args.sections - slice + 1))
                disc = iterate_structure(generate_binary_structure(3, 1), dsize).astype(scipy.int_)
                image_threshold_data = image_gradient_data.copy()
                mask_equal_or_lower = mask_equal | mask_lower
                # set all voxels over the current slice to the max of all voxels in the current slice
                image_threshold_data[mask_greater] = image_threshold_data[mask_equal_or_lower].max()
            elif 'sections' == args.type:
                dsize = args.dsize
                disc = iterate_structure(generate_binary_structure(3, 1), args.dsize).astype(scipy.int_)
                image_threshold_data = image_gradient_data.copy()
                # set all voxels under the current slice to zero
                image_threshold_data[mask_lower] = 0
                # set all voxels over the current slice to the max of all voxels in the current slice
                image_threshold_data[mask_greater] = image_threshold_data[mask_equal].max()

            logger.debug('{} of {} voxels belong to this level.'.format(len(mask_equal.nonzero()[0]), scipy.prod(image_threshold_data.shape)))            

            # apply the closing with the appropriate disc size
            logger.debug('Applying a disk of {} to all values >= {} and < {}...'.format(dsize, bins[slice - 1],  bins[slice]))
            image_closed_data = grey_closing(image_threshold_data, footprint=disc)
            
            # add result of this slice to the general results
            image_viscous_data = scipy.maximum(image_viscous_data, image_closed_data)
            
            # save created output file, if in sections mode
            if 'sections' == args.type:
                # save resulting gradient image
                logger.info('Saving resulting gradient image as {}...'.format(image_viscous_name))
                image_viscous = image_like(image_viscous_data, image_gradient)
                save(image_viscous, image_viscous_name)
            
            
        # save created output file, if not in sections mode
        if 'sections' != args.type:
            # save resulting gradient image
            logger.info('Saving resulting gradient image as {}...'.format(image_viscous_name))
            image_viscous = image_like(image_viscous_data, image_gradient)
            save(image_viscous, image_viscous_name)
            
    logger.info('Successfully terminated.')
      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The folder to store the results in.')
    parser.add_argument('sections', type=int, help='The number of sections to split the image into.')
    parser.add_argument('dsize', type=int, help='The size of the biggest disc to apply. Note that this value is for each section divided through the section no. and rounded down to the next full integer.')
    parser.add_argument('images', nargs='+', help='One or more gradient images.')
    parser.add_argument('-t', '--type', '--viscous-type', dest='type', default='oil', choices=['oil', 'mercury', 'plain', 'sections'], help='Select the type of the morphological operation. oil behaves more liquid and less viscous in the higher intensity values, mercury in the lower and plain executes a single closing with a disk of the size of the supplied level parameter on the whole range and sections leads to an output image for each section. In the plain case the sections parameter is ignored.')
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
    