#!/usr/bin/env python

"""Fill the wholes in the contour files. Creates two output files for each input file."""

# build-in modules
import argparse
import logging
import os

# third-party modules
from scipy.ndimage.morphology import binary_fill_holes
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save

# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Fill the wholes in the contour files. Creates two output  files for each input file.
                  """
                  
# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    inner_contour_index = 10
    outer_contour_index = 11
    contour_dimension = 0
    time_dimension = 3
    
    # load original example volume
    original_data, original_header = load(args.input)
    
    # prepare output volumes
    inner_data = scipy.zeros(original_data.shape, scipy.bool_)
    outer_data = scipy.zeros(original_data.shape, scipy.bool_)
    
    # prepare slicer
    slicer = [slice(None)] * original_data.ndim
    
    # iterate over contour dimension, extract contours, fill holes and append to result volumes
    for slice_id in range(original_data.shape[contour_dimension]):
        for time_id in range(original_data.shape[time_dimension]):
            slicer[contour_dimension] = slice(slice_id, slice_id+1)
            slicer[time_dimension] = slice(time_id, time_id+1)
            # process inner contour
            inner_data_volume = original_data[slicer].copy()
            if not 0 == len(inner_data_volume.nonzero()[0]):
                inner_data_volume[inner_data_volume != inner_contour_index] = False
                inner_data_volume = scipy.squeeze(inner_data_volume.astype(scipy.bool_))
                #inner_data_volume = binary_closing(inner_data_volume, iterations=2)
                voxel_before = len(inner_data_volume.nonzero()[0])
                inner_data_volume = binary_fill_holes(inner_data_volume)
                voxel_after = len(inner_data_volume.nonzero()[0])
                if voxel_before >= voxel_after: logger.warning('Hole of inner contour in slice space={}, time={} has not been filled.'.format(slice_id, time_id))
                tmp = scipy.squeeze(inner_data[slicer])
                tmp += inner_data_volume
            # process outer contour
            outer_data_volume = original_data[slicer].copy()
            if not 0 == len(outer_data_volume.nonzero()[0]):
                outer_data_volume[outer_data_volume != outer_contour_index] = False
                outer_data_volume = scipy.squeeze(outer_data_volume.astype(scipy.bool_))
                #outer_data_volume = binary_closing(outer_data_volume, iterations=2)
                voxel_before = len(outer_data_volume.nonzero()[0])
                outer_data_volume = binary_fill_holes(outer_data_volume)
                voxel_after = len(outer_data_volume.nonzero()[0])
                if voxel_before >= voxel_after: logger.warning('Hole of outer contour in slice space={}, time={} has not been filled.'.format(slice_id, time_id))
                tmp = scipy.squeeze(outer_data[slicer])
                tmp += outer_data_volume
    
    # prepare output file name
    basename = '.'.join(os.path.basename(args.input).split('.')[:-1])
    suffix = os.path.basename(args.input).split('.')[-1]
    output_inner = '{}/{}_i.{}'.format(args.output, basename, suffix)
    output_outer = '{}/{}_o.{}'.format(args.output, basename, suffix)
    
    # save resulting volumes
    save(inner_data, output_inner, original_header, args.force)
    save(outer_data, output_outer, original_header, args.force)
          
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target folder.')
    parser.add_argument('-p', dest='paintc', action='store_true', help='Paint original contours into the volumes.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 