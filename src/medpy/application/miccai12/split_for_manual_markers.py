#!/usr/bin/python

"""Prepares manual-marker ready volumes from a 4D volume."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save, header
from medpy.core.exceptions import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                Prepares 3D volumes from a 4D volumes for the creation of manual markers. Requires the
                original 4D image to be provided. For some settings, the contour marker 4D volume is also
                required.
                
                Images in 4D can not me visualized very well for the creation of manual markers. This
                script and its counterpart allow to de-construct a 4D volume in various ways and to
                afterwards combine the created marker volumes easily. Just select one of the following
                modi, create markers for the resulting volumes and then join the markers together.
                
                This script supports the following extraction modi:
                  I) Extraction of ED volume only (spatial volume)
                  II) Extraction of ES volume only (spatial volume)
                  III) Extraction of all spatial volumes
                  IV) Extraction of all temporal volumes
                  
                All of the files created with these modi can be re-combined using the
                "Join for manual markers" script, which combines the created manual marker volumes again
                into a valid 4D markers volume. See there for some remarks on the required format of the
                manual markers.
                
                Some remarks on the file naming convention:
                The created 3D volumes follow a special naming convention. The from them created manual
                markers should fulfill the same convention, although some pre- or suffixes might be
                added.
                """
                
# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    dimension_spatial = 0
    dimension_temporal = 3
    name_output_data = '{}/{}_d{:01d}_s{:04d}.nii' # basename / slice-dimension / slice-number
    name_output_marker = '{}/m{}_d{:01d}_s{:04d}.nii' # basename / slice-dimension / slice-number
    
    # load input image
    input_data, input_header = load(args.input)
    
    # determine type of extraction and eventuelly load contour file
    if args.paintc or args.type in ['ed', 'es']:
        contour_data, _ = load(args.contour)
    
    # select dimension and set variable parameter
    if args.type in ['ed', 'es', 'spatial']: cut_dimension = dimension_temporal
    else: cut_dimension = dimension_spatial
    basename = '.'.join(os.path.basename(args.input).split('.')[:-1])
    
    # adjust voxel spacing
    voxel_spacing = list(header.get_pixel_spacing(input_header))
    del voxel_spacing[cut_dimension]
    voxel_spacing += [0]
    header.set_pixel_spacing(input_header, voxel_spacing)
    
    # split and save images
    first = True
    slices = input_data.ndim * [slice(None)]
    for idx in range(input_data.shape[cut_dimension]):
        slices[cut_dimension] = slice(idx, idx + 1)
        
        # extract original sub-volume
        data_output = scipy.squeeze(input_data[slices])
        
        # create same-sized empty volume as marker base
        data_marker = scipy.zeros(data_output.shape, scipy.uint8)
        
        # extract also contour sub-volume if required
        if args.paintc:
            data_marker += scipy.squeeze(contour_data[slices])
            
        # check if contour data is empty in ed and es case; if yes, skip this volume
        if args.type in ['ed', 'es'] and 0 == len(scipy.squeeze(contour_data[slices]).nonzero()[0]):
            continue
        
        # check if first volume in case of type = es, then skip
        if 'es' == args.type and first:
            first = False
            continue
        
        # save data and marker sub-volumes
        save(data_output, name_output_data.format(args.output, basename, cut_dimension, idx), input_header, args.force)
        save(data_marker, name_output_marker.format(args.output, basename, cut_dimension, idx), input_header, args.force)
        
        # in case of type = ed, break after first
        if 'ed' == args.type: break
        
    logger.info("Successfully terminated.")
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if args.paintc and None == args.contour:
        raise ArgumentError('If the "-p" switch is set, a contour file must be provide.')
    elif args.type in ['ed', 'es'] and None == args.contour:
        raise ArgumentError('If the type is set to "ed" or "es, a contour file must be provide.')
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target folder.')
    # Note: diastole = widest, systole = narrowest
    parser.add_argument('type', choices=['ed', 'es', 'spatial', 'temporal'], help='The type of volumes to extract. "ed" and "es" implies "spatial".')
    parser.add_argument('--contour', help='Contour volume. Required for "ed" and "es" types or if "-p" switch is set.')
    parser.add_argument('-p', dest='paintc', action='store_true', help='Paint original contours into the volumes.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 
    