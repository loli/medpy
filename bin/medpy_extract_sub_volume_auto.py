#!/usr/bin/python

"""Automatically extracts sub-volumes from a medical image."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import os

# third-party modules
import numpy
from nibabel.loadsave import load, save
from nibabel.spatialimages import ImageFileError

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.utilities.nibabel import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-05-17"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Takes a medical image of arbitrary dimensions and splits it into a
                  number of sub-volumes along the supplied dimensions. The maximum size
                  of each such created volume can be supplied.
                  
                  Note to take into account the input images orientation when supplying the cut dimension.
                  Note that the image offsets are not preserved.
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
    
    for image_name in args.images:
        
        # load input image
        logger.info('Loading {}...'.format(image_name))
        try: image = load(image_name)
        except ImageFileError as e:
            logger.critical('The input image does not exist or its file type is unknown.')
            raise ArgumentError('The input image does not exist or its file type is unknown.', e)
        
        # reduce the image dimensions (nibabel Analyze always assumes 4)
        image_data = numpy.squeeze(image.get_data())
        
        # check if supplied cut dimension is inside the input images dimensions
        if args.dimension < 0 or args.dimension >= image_data.ndim:
            logger.critical('The supplied cut-dimensions {} is invalid. The input image has only {} dimensions.'.format(args.dimension, image_data.ndim))
            raise ArgumentError('The supplied cut-dimensions {} is invalid. The input image has only {} dimensions.'.format(args.dimension, image_data.ndim))
        
        # determine cut lines
        no_sub_volumes = image_data.shape[args.dimension] / args.maxsize + 1 # int-division is desired
        slices_per_volume = image_data.shape[args.dimension] / no_sub_volumes # int-division is desired
        
        # construct names of output images
        chunks = image_name.split('/')[-1].split('.')
        image_suffix = chunks[-1]
        output_base_name = ''.join(chunks[:-1])
        
        # construct processing dict for each sub-volume
        processing_array = []
        for i in range(no_sub_volumes):
            processing_array.append(
                {'path': '{}/{}_sv{}.{}'.format(args.output, output_base_name, i+1, image_suffix),
                 'cut': (i * slices_per_volume, (i + 1) * slices_per_volume)})
            if no_sub_volumes - 1 == i: # last volume has to have increased cut end
                processing_array[i]['cut'] = (processing_array[i]['cut'][0], image_data.shape[args.dimension])

        # construct base indexing list
        index = [slice(None) for _ in range(image_data.ndim)]
        
        # execute extraction of the sub-volumes
        logger.info('Extracting sub-volumes...')
        for dic in processing_array:
            # check if output images exists
            if not args.force:
                if os.path.exists(dic['path']):
                    logger.warning('The output file {} already exists. Skipping this volume.'.format(dic['path']))
                    continue
            
            # extracting sub-volume
            index[args.dimension] = slice(dic['cut'][0], dic['cut'][1])
            volume = image_data[index]
            
            logger.debug('Extracted volume is of shape {}.'.format(volume.shape))
            
            # saving sub-volume
            logger.info('Saving cut {} as {}...'.format(dic['cut'], dic['path']))
            save(image_like(volume, image), dic['path'])
        
    logger.info('Successfully terminated.')

    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('output', help='The location where to store the sub-volumes. They will be of the same file-type as the input image.')
    parser.add_argument('dimension', type=int, help='The dimension in which direction to split (starting from 0:x).')
    parser.add_argument('maxsize', type=int, help='The produced volumes will always be smaller than this size (in terms of slices in the cut-dimension).')
    parser.add_argument('images', nargs='+', help='A number of medical image of arbitrary dimensions.')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()    