#!/usr/bin/python

"""Print information about an image volume."""

# build-in modules
import argparse
import logging

# third-party modules

# path changes

# own modules
from medpy.io import load
from medpy.core import Logger


# information
__author__ = "Oskar Maier"
__version__ = "r0.2.0, 2012-05-24"
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
    input_data, input_header = load(args.input)
    
    # print information about the image
    printInfo(input_data, input_header)
    
    logger.info('Successfully terminated.')
        
def printInfo(data, header):
    # print image information
    print '\nInformations obtained from image header:'
    print 'header type={}'.format(type(header))
    
    print '\nInformations obtained from image array:'
    print 'datatype={},dimensions={},shape={}'.format(data.dtype, data.ndim, data.shape)
    print 'first and last element: {} / {}'.format(data.flatten()[0], data.flatten()[-1])
        
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
