#!/usr/bin/python

"""Executes the watershed algorithm over images."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import itk

# path changes

# own modules
from medpy.io import load, save
from medpy.core import Logger, ArgumentError
from medpy.itkvtk.utilities import itku


# information
__author__ = "Oskar Maier"
__version__ = "r0.5.0, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Applies the watershed segmentation to a number of images with a range
                  of parameters.
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_watershed_[parameters]'
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
    
    # check if output image exists (will also be performed before saving, but as the watershed might be very time intensity, a initial check can save frustration)
    if not args.force:
        if os.path.exists(args.output):
            raise ArgumentError('The output image {} already exists.'.format(args.output))
    
    # loading image
    data_input, header_input = load(args.input)
    
    # convert to itk image
    input_image_type = itku.getImageTypeFromArray(data_input)
    itk_py_converter_in = itk.PyBuffer[input_image_type]
    image_input = itk_py_converter_in.GetImageFromArray(data_input)

    logger.debug(itku.getInformation(image_input))
    
    # apply the watershed
    logger.info('Watershedding with settings: thr={} / level={}...'.format(args.threshold, args.level))
    image_watershed = itk.WatershedImageFilter[input_image_type].New()
    image_watershed.SetInput(image_input)
    image_watershed.SetThreshold(args.threshold)
    image_watershed.SetLevel(args.level)
                
    logger.debug(itku.getInformation(image_watershed.GetOutput()))
    
    # convert itk image to scipy array
    output_image_type = itku.getImageType(image_watershed.GetOutput())
    itk_py_converter_out = itk.PyBuffer[output_image_type]
    data_output = itk_py_converter_out.GetArrayFromImage(image_watershed.GetOutput())
    
    print data_output.dtype, data_output.shape
                
    # save file
    save(data_output, args.output, header_input, args.force)
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('level', type=float, help='The level parameter of the ITK watershed filter.')
    parser.add_argument('threshold', type=float, help='The threshold parameter of the ITK watershed filter.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
