#!/usr/bin/python

"""Executes gradient magnitude filter over images."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy
import itk

# path changes

# own modules
from medpy.io import load, save
from medpy.core import Logger
from medpy.itkvtk.utilities import itku


# information
__author__ = "Oskar Maier"
__version__ = "r0.3.0, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Creates a height map of the input images using the gradient magnitude
                  filter.
                  The pixel type of the resulting image will be float.
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
        
    # loading image
    data_input, header_input = load(args.input)
    data_input = data_input.astype(scipy.float32)
    
    # load image as float using ITK
    image_type = itk.Image[itk.F, 4] # causes Eclipse PyDev to complain -> ignore error warning
    reader = itk.ImageFileReader[image_type].New()
    reader.SetFileName(args.input)
    reader.Update()
    
    # compare
    print reader.GetOutput().GetPixel([0,0,0,0]), reader.GetOutput().GetPixel([0,0,0,4])
    print data_input[0,0,0,0], data_input[0,0,0,4], data_input.dtype
    
    # to array
    it = itku.getImageType(reader.GetOutput())
    itk_py_converter_in = itk.PyBuffer[it]
    data_i1 = itk_py_converter_in.GetArrayFromImage(reader.GetOutput())
    #data_i1 = scipy.swapaxes(data_i1, 0, 1)
    #data_i1 = scipy.swapaxes(data_i1, 1, 2)
    #data_i1 = scipy.swapaxes(data_i1, 2, 3)
    #data_i1 = scipy.swapaxes(data_i1, 0, 2)
    
    __compare(data_i1, data_input)
    
    # convert to itk image
    #######
    # BUG/MISSING IMPLEMENTATION: WrapITK does not wrap all templates for the
    # itk.GradientMagnitudeImageFilter. Only from same type to same type is
    # supported, what is kind of senseless, as the output should always be float for
    # exact results. Thus we have to treat the input image as a float image to apply the
    # filter. This might lead to the loss of some precision, but it should not be in any
    # relevant margin.
    ####### 
    input_image_type = itk.Image[itk.F, data_input.ndim]
    itk_py_converter_in = itk.PyBuffer[input_image_type]
    image_input = itk_py_converter_in.GetImageFromArray(data_input)

    logger.debug(itku.getInformation(image_input))
    
    # output image type is float
    output_image_type = itk.Image[itk.F, data_input.ndim]
        
    # execute the gradient map filter
    logger.info('Applying gradient map filter...')
    image_gradient = itk.GradientMagnitudeImageFilter[input_image_type, output_image_type].New()
    image_gradient.SetInput(image_input)
    image_gradient.Update()
        
    logger.debug(itku.getInformation(image_gradient.GetOutput()))
    
    # convert to scipy array
    itk_py_converter_out = itk.PyBuffer[output_image_type]
    data_output = itk_py_converter_out.GetArrayFromImage(image_gradient.GetOutput())
    
    # save image
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
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser

def __compare(i1, i2):
    # compare image data
    print i1.flatten()[0], i1.flatten()[-1], 'vs.', i2.flatten()[0], i2.flatten()[-1]   
    
    if not i1.dtype == i2.dtype: print 'Dtype differs: {} to {}'.format(i1.dtype, i2.dtype)
    if not i1.shape == i2.shape:
        print 'Shape differs: {} to {}'.format(i1.shape, i2.shape)
        print 'The voxel content of images of different shape can not be compared. Exiting.'
        return   
    
    voxel_total = reduce(lambda x, y: x*y, i1.shape)
    voxel_difference = len((i1 != i2).nonzero()[0])
    if not 0 == voxel_difference:
        print 'Voxel differ: {} of {} total voxels'.format(voxel_difference, voxel_total)
        print 'Max difference: {}'.format(scipy.absolute(i1 - i2).max())
    else: print 'Both the same.'
    
if __name__ == "__main__":
    main()        