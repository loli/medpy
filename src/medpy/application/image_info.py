#!/usr/bin/python

"""Print information about an image volume."""

# build-in modules
import argparse
import logging

# third-party modules
import numpy
from nibabel.loadsave import load

# path changes

# own modules
from medpy.core import Logger


# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-05-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Prints information about an image volume to the command line.
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
    
    # load input image
    logger.info('Loading image {} using NiBabel...'.format(args.input))
    input_image = load(args.input)
    
    # extract image data
    input_data = numpy.squeeze(input_image.get_data())
    
    # print image information
    print 'Image processed: {}'.format(args.input)
    
    header = input_image.get_header()
    print '\nInformations obtained from image header:' # analyze general if not marked differently
    print 'dtype={}'.format(header.get_data_dtype())
    print 'shape={}'.format(header.get_data_shape())
    print 'zooms={}'.format(header.get_zooms())
    print 'data offset={}'.format(header.get_data_offset())
    try:
        print 'nslices={},slice duration={}'.format(header.get_n_slices(), header.get_slice_duration())
        print 'slice times={}'.format(header.get_slice_times())
        slts = header.get_slice_times()
        slts = slts[1:] - slts[:-1]
        print 'Regular slice times={}'.format(numpy.allclose(slts, len(slts) * [slts[0]]))
    except:
        print 'nslices and slice duration not defined in header'
    print 'qfrom={}'.format(header.get_qform())
    print 'sform={}'.format(header.get_sform())
    
    print '\nInformations obtained after conversion to scipy array:'
    print 'datatype={},dimensions={},shape={}'.format(input_data.dtype, input_data.ndim, input_data.shape)
    print 'image type={}'.format(type(input_image))
    print 'header type={}'.format(type(header))
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('input', help='The image to analyse.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
