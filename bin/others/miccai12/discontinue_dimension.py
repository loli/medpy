#!/usr/bin/python

"""Cuts all regions ties along one dimension on a region image."""

# build-in modules
import itertools
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.filter.label import relabel
import os


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-06-26"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Cuts all regions ties along one dimension on a region image.
                  The output label image will have region ids starting from 1.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # check if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists. Exiting.'.format(args.output))
            exit(-1)    

    # load input image
    input_data, input_header = load(args.input)
    
    logger.debug('Old number of regions={}.'.format(len(scipy.unique(input_data))))
    
    # cut and relabel along the required dimension
    logger.info('Cutting and relabeling...')
    dimensions = list(range(input_data.ndim))
    del dimensions[args.dimension]
    __split_along(input_data, dimensions)
    
    logger.debug('New number of regions={}.'.format(len(scipy.unique(input_data))))
    
    # save result contour volume
    save(input_data, args.output, input_header, args.force)

    logger.info("Successfully terminated.")


def __split_along(arr, view):
    """
    Split a region image's regions along one dimension.
    """
    
    def fun(arr, start):
        arr = relabel(arr, start)
        return arr, arr.max() + 1
    
    start = 1
    
    # create list of iterations
    iterations = [[None] if dim in view else list(range(arr.shape[dim])) for dim in range(arr.ndim)]
     
    # iterate, create slicer, execute function and collect results
    for indices in itertools.product(*iterations):
        slicer = [slice(None) if idx is None else slice(idx, idx + 1) for idx in indices]
        ret, start = fun(scipy.squeeze(arr[slicer]), start)
        arr[slicer] = ret.reshape(arr[slicer].shape)    
    
    return arr


def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('dimension', type=int, help='The dimension along which to cut (starting from 0).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 