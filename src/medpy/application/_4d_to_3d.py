#!/usr/bin/python

import argparse
import logging

import scipy
from nibabel.loadsave import load, save

from medpy.core import Logger
from medpy.utilities import image_like
import os

__description__ = """
                  Splits a 4D volume into a number of 3D volumes.
                  Takes every offset slice, starting from the first, of the input 4D
                  volume and combines them into a 3D volume. Then repeatets the process
                  starting from the second slice, etc.
                  All in all a number of offset 3D volumes will be created.
                  """

def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)    
    
    # load 4d image
    image_4d = load(args.input)
    data_4d = scipy.squeeze(image_4d.get_data())
    
    # determine number of 3D volumes to create
    # Note: the dimension with the highest number of slices is assumed to be the target split dimension
    slices_idx = args.dimension
    slices = data_4d.shape[args.dimension]
    if not 0 == slices % args.offset:
        logger.warning('The offset is not a divider of the slices ({} / {}).'.format(slices, args.offset))
        exit(1)
    volumes = slices / args.offset
    
    logger.debug('Separating {} slices into {} 3D volumes of thickness {}.'.format(slices, volumes, args.offset))
        
    # prepare parameters
    volume_shape = list(data_4d.shape)
    volume_shape[slices_idx] = volumes
    
        
    # iterate over 4D image and create 3D sub volumes
    for idx in range(args.offset):
        volume_data = scipy.zeros(volume_shape, dtype=data_4d.dtype)
        if idx + 1 < 10: volume_name = '{}0{}.nii'.format(args.output, idx + 1)
        else: volume_name = '{}{}.nii'.format(args.output, idx + 1)
        
        # test if output image exists
        if not args.force:
            if os.path.exists(volume_name):
                logger.warning('The output image {} already exists. Skipping this volume.'.format(volume_name))
                continue
        
        # collect the slices
        for sl in range(volumes):
            idx_from = [slice(None), slice(None), slice(None)]
            idx_from[slices_idx] = slice(idx + sl * args.offset, idx + sl * args.offset + 1)
            idx_to = [slice(None), slice(None), slice(None)]
            idx_to[slices_idx] = slice(sl, sl+1)
            #print 'Slice {} to {}.'.format(idx_from, idx_to)
            volume_data[idx_to] = data_4d[idx_from]
        
        # save resulting 3D volume
        logger.info('Saving volume no. {} as {}...'.format(idx + 1, volume_name))
        volume_image = image_like(volume_data, image_4d)
        save(volume_image, volume_name)
    
    print "Successfully terminated."



def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='The input 4D volume.')
    parser.add_argument('dimension', type=int, help='The dimension in which to cut (starting from 0).')
    parser.add_argument('offset', type=int, help='The offset between the slices.')
    parser.add_argument('output', help='Target location and name of the created volumes image (\wo suffix).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        