#!/usr/bin/python

"""Joins a number of 3D manual markers into a 4D marker volume."""

# build-in modules
import argparse
import logging
import re

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.core.exceptions import ArgumentError
from medpy.filter import relabel_non_zero


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                Prepares one or more 4D from a number of 3D manual marker volumes. The supplied volumes
                have to follow a special naming convention. Additionally requires the original 4D image.
                
                Images in 4D can not me visualized very well for the creation of manual markers. This
                script and its counterpart allow to de-construct a 4D volume in various ways and to
                afterwards combine the created marker volumes easily. Just select one of the following
                modi, create markers for the resulting volumes and then join the markers together.
                
                This script supports the combination of all manual marker volumes that follow the naming
                convention. See the counterpart of this script, "Split for manual markers", for some more
                remarks on this subject.
                
                Some remarks on the manual markers:
                The supplied marker file has to contain two or more markers, which all must have indices
                between 1 and 9 (higher are ignored). If two markers could be found, the one with the
                lowest index is treated as foreground (FG) and the other one as background (BG).
                Upon the existence of more markers, all but the lone with the highest index are treated
                as FG of an distinct object. For each of these objects a 4D marker volume is created,
                whereas the associated marker index is treated as FG and all others joined together into
                the BG marker.
                In the resulting files the index 1 will always represent the FG and the index 2 the BG.
                """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load original example volume
    original_data, original_header = load(args.original)
    
    # prepare execution
    result_data = scipy.zeros(original_data.shape, scipy.uint8)
    del original_data
    
    # First step: Combine all marker images
    basename_old = False
    # iterate over marker images
    for marker_image in args.input:
        # extract information from filename and prepare slicr object
        basename, slice_dimension, slice_number = re.match(r'.*m(.*)_d([0-9])_s([0-9]{4}).*', marker_image).groups()
        slice_dimension = int(slice_dimension)
        slice_number = int(slice_number)
        # check basenames
        if basename_old and not basename_old == basename:
            logger.warning('The marker seem to come from different sources. Encountered basenames {} and {}. Continuing anyway.'.format(basename, basename_old))
        basename_old = basename
        # prepare slicer
        slicer = [slice(None)] * result_data.ndim
        slicer[slice_dimension] = slice_number
        # load marker image
        marker_data, _ = load(marker_image)
        # add to marker image ONLY where this is zero!
        result_data_subvolume = result_data[slicer]
        mask_array = result_data_subvolume == 0
        result_data_subvolume[mask_array] = marker_data[mask_array]
        if not 0 == len(marker_data[~mask_array].nonzero()[0]):
            logger.warning('The mask volume {} showed some intersection with previous mask volumes. Up to {} marker voxels might be lost.'.format(marker_image, len(marker_data[~mask_array].nonzero()[0])))
        
    # Second step: Normalize and determine type of markers
    result_data[result_data >= 10] = 0 # remove markers with indices higher than 10
    #result_data = relabel_non_zero(result_data) # relabel starting from 1, 0's are kept where encountered
    marker_count = len(scipy.unique(result_data))
    
    if 3 > marker_count: # less than two markers
        raise ArgumentError('A minimum of two markers must be contained in the conjunction of all markers files (excluding the neutral markers of index 0).')
    
    # assuming here that 1 == inner marker, 2 = border marker and 3 = background marker
    inner_name = args.output.format('i')
    inner_data = scipy.zeros_like(result_data)
    inner_data[result_data == 1] = 1
    inner_data[result_data == 2] = 2
    inner_data[result_data == 3] = 2
    save(inner_data, inner_name, original_header, args.force)
    
    outer_name = args.output.format('o')
    outer_data = scipy.zeros_like(result_data)
    outer_data[result_data == 1] = 1
    outer_data[result_data == 2] = 1
    outer_data[result_data == 3] = 2
    save(outer_data, outer_name, original_header, args.force)    
    
#    for marker in scipy.unique(result_data)[1:-1]: # first is neutral marker (0) and last overall background marker
#        output = args.output.format(marker)
#        _data = scipy.zeros_like(result_data)
#        _data += 2 # set all as BG markers
#        _data[result_data == marker] = 1
#        _data[result_data == 0] = 0
#        save(_data, output, original_header, args.force)
        
    logger.info("Successfully terminated.")
    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if not '{}' in args.output:
        raise ArgumentError(args.output, 'The output argument string must contain the sequence "{}".')
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('original', help='Original volume.')
    parser.add_argument('output', help='Target volume(s). Has to include the sequence "{}" in the place where the marker number should be placed.')
    parser.add_argument('input', nargs='+', help='The manual marker volumes to combine.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 
    