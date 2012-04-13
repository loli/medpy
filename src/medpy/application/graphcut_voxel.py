#!/usr/bin/python

"""Execute a graph cut on a voxel image based on some foreground and background markers."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import os

# third-party modules
import scipy
import numpy
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError 

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabel import image_like
from medpy import graphcut



# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-03-23"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Perform a binary graph cut using Boykov's max-flow/min-cut algorithm.
                  
                  This implementation does only compute a boundary term and does not use
                  any regional term. The desired boundary term can be selected via the
                  --boundary argument. Depending on the selected term, an additional
                  image has to be supplied as badditional.
                  
                  In the case of the difference of means, it is the original image.
                  
                  Furthermore the algorithm requires a binary image with foreground
                  markers and a binary image with background markers.
                  
                  Additionally a filename for the created binary mask marking foreground
                  and background has to be supplied.
                  
                  Note that the input images must be of the same dimensionality,
                  otherwise an exception is thrown.
                  Note to take into account the input images orientation.
                  Note that the quality of the resulting segmentations depends also on
                  the quality of the supplied markers.
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
        
    # check if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists. Exiting.'.format(args.output))
            exit(1)
            
    # select boundary term
    if args.boundary == 'means':
        boundary_term = graphcut.boundary_difference_of_means_voxel
        boundary_term = graphcut.energy_voxel.boundary_difference_of_means2
        logger.info('Selected boundary term: difference of means')

    # load input images
    logger.info('Loading foreground markers {}...'.format(args.foreground))
    try: 
        fgmarkers_image_data = numpy.squeeze(load(args.foreground).get_data()).astype(scipy.bool_)
    except ImageFileError as e:
        logger.critical('The foreground marker image does not exist or its file type is unknown.')
        raise ArgumentError('The foreground marker image does not exist or its file type is unknown.', e)
    
    logger.info('Loading background markers {}...'.format(args.background))
    try:
        bgmarkers_image = load(args.background) # keep loaded image as prototype for saving the result
        bgmarkers_image_data = numpy.squeeze(bgmarkers_image.get_data()).astype(scipy.bool_)
    except ImageFileError as e:
        logger.critical('The background marker image does not exist or its file type is unknown.')
        raise ArgumentError('The background marker image does not exist or its file type is unknown.', e)
       
    logger.info('Loading additional image for the boundary term {}...'.format(args.badditional))
    try: 
        badditional_image_data = numpy.squeeze(load(args.badditional).get_data())
    except ImageFileError as e:
        logger.critical('The badditional image does not exist or its file type is unknown.')
        raise ArgumentError('The badditional image does not exist or its file type is unknown.', e)
       
    # check if all images dimensions are the same
    if not (badditional_image_data.shape == fgmarkers_image_data.shape == bgmarkers_image_data.shape):
        logger.critical('Not all of the supplied images are of the same shape.')
        raise ArgumentError('Not all of the supplied images are of the same shape.')

    # generate graph
    logger.info('Preparing BK_MFMC C++ graph...')
    gcgraph = graphcut.graph_from_voxels(fgmarkers_image_data,
                                         bgmarkers_image_data,
                                         boundary_term = boundary_term,
                                         boundary_term_args = badditional_image_data)
    
    # execute min-cut
    logger.info('Executing min-cut...')
    maxflow = gcgraph.maxflow()
    logger.debug('Maxflow is {}'.format(maxflow))
    
    # reshape results to form a valid mask
    logger.info('Applying results...')
    result_image_data = scipy.zeros(bgmarkers_image_data.size, dtype=scipy.bool_)
    for idx in range(len(result_image_data)):
        result_image_data[idx] = 0 if gcgraph.termtype.SINK == gcgraph.what_segment(idx) else 1
    result_image_data = result_image_data.reshape(bgmarkers_image_data.shape)
    
    # save resulting mask as int8            
    logger.info('Saving resulting segmentation...')
    bgmarkers_image.get_header().set_data_dtype(scipy.int8)
    save(image_like(result_image_data, bgmarkers_image), args.output)

    logger.info('Successfully terminated.')

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('badditional', help='The additional image required by the boundary term. See there for details.')
    parser.add_argument('foreground', help='Binary image containing the foreground markers.')
    parser.add_argument('background', help='Binary image containing the background markers.')
    parser.add_argument('output', help='The output image containing the segmentation.')
    parser.add_argument('--boundary', default='means', help='The boundary term to use. Note that difference of means (means) requires the original image.', choices=['means'])
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    

if __name__ == "__main__":
    main()