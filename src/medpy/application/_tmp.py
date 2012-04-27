#!/usr/bin/python

import argparse
import sys
import os

import scipy
from nibabel.loadsave import load, save

from medpy.utilities import image_like

__description__ = """
                  Helper script for fast conversions.
                  """

def main():
    args = getArguments(getParser())

    # test if output image exists
    #if not args.force:
    #    if os.path.exists(args.output):
    #        print 'The output image {} already exists. Breaking.'.format(args.output)
    #        sys.exit(-1)
     
    
    for input in args.input:
        # load image
        #print 'Loading image {}...'.format(args.input)
        input_image = load(input)
        input_data = scipy.squeeze(input_image.get_data())
        
        # perform operation
        # point out files where image is smaller than X
        mask_size = len(input_data.nonzero()[0])
        if mask_size < 100:
            print '{} has only {} voxels!'.format(input, mask_size)
        
        # save resulting 3D volume
        #print 'Saving image as {}...'.format(args.output)
        #output_image = image_like(output_data, input_image)
        #save(output_image, args.output)
        
    print "Successfully terminated."



def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', nargs='+', help='Input image.')
    #parser.add_argument('output', help='Output image (\w suffix).')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        