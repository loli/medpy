#!/usr/bin/python

"""Executes opening and closing morphological operations over the input image using selective slicing."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy.ndimage.morphology

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
import itertools
import os


# information
__author__ = "Oskar Maier"
__version__ = "r2.0, 2011-12-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Executes opening and closing morphological operations over the input image using selective slicing.
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

    # check if output image already exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists. Exiting.'.format(args.output))
            exit(-1)

    # load input image
    image_smoothed_data, image_header = load(args.input)
        
    # apply additional hole closing step
    logger.info('Closing holes...')
    def fun_holes(arr):
        return scipy.ndimage.morphology.binary_fill_holes(arr)
    xd_iterator(image_smoothed_data, (1, 2), fun_holes)
        
    # perform opening resp. closing
    # in 3D case: size 1 = 6-connectedness, 2 = 12-connectedness, 3 = 18-connectedness, etc.
    if 'erosion' == args.type:
        logger.info('Applying erosion...')
        def fun(arr):
            if 0 == args.iterations: return arr
            footprint = scipy.ndimage.morphology.generate_binary_structure(arr.ndim, args.size)
            return scipy.ndimage.morphology.binary_erosion(arr, footprint, iterations=args.iterations)
    elif 'dilation' == args.type:
        logger.info('Applying dilation...')
        def fun(arr):
            if 0 == args.iterations: return arr
            footprint = scipy.ndimage.morphology.generate_binary_structure(arr.ndim, args.size)
            return scipy.ndimage.morphology.binary_dilation(arr, footprint, iterations=args.iterations)
    elif 'opening' == args.type:
        logger.info('Applying opening...')
        def fun(arr):
            if 0 == args.iterations: return arr
            footprint = scipy.ndimage.morphology.generate_binary_structure(arr.ndim, args.size)
            return scipy.ndimage.morphology.binary_opening(arr, footprint, iterations=args.iterations)
    else: # closing
        logger.info('Applying closing...')
        def fun(arr):
            if 0 == args.iterations: return arr
            footprint = scipy.ndimage.morphology.generate_binary_structure(arr.ndim, args.size)
            return scipy.ndimage.morphology.binary_closing(arr, footprint, iterations=args.iterations)

    # iterate over slices and apply selected operation
    xd_iterator(image_smoothed_data, (1, 2), fun)

    # save resulting mas
    save(image_smoothed_data, args.output, image_header, args.force)
            
    logger.info('Successfully terminated.')
      
def xd_iterator(arr, view, fun):
    """
    Iterates over arr, slicing it into views over the dimensions provided in view and
    passes the extracted subvolumes to fun.
    Fun has to return an array of the same shape as it receives. This return array is
    then used to update the original array arr in-place.
    
    Example:
        Assuming an array of shape arr.shape = (100, 200, 300), we want to iterate over
        all 2D slices of the first two dimensions, i.e. iterate over the 3rd dimension
        and getting 300 slices of shape (100, 200) passed to the function fun. So we
        have to provide in view the dimensions over which we do not want to iterate, i.e.
        in this case view = [0,1].
    """
    # check parameters
    for dim in view:
        if dim >= arr.ndim or 0 > dim or not type(dim) == int: raise AttributeError('Invalid dimension {} in view. Must be int between 0 and {}.'.format(dim, arr.ndim - 1))
    if len(view) >= arr.ndim:
        raise AttributeError('The view should contain less entries than the array dimensionality.')
    
    # create list of iterations
    iterations = [[None] if dim in view else list(range(arr.shape[dim])) for dim in range(arr.ndim)]
     
    # iterate, create slicer, execute function and collect results
    for indices in itertools.product(*iterations):
        slicer = [slice(None) if idx is None else slice(idx, idx + 1) for idx in indices]
        arr[slicer] = fun(scipy.squeeze(arr[slicer])).reshape(arr[slicer].shape)      
      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='Source volume.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-t', '--type', dest='type', choices=['erosion', 'dilation', 'opening', 'closing'], default='erosion', help='The type of the morphological operation.')
    parser.add_argument('-i', '--iterations', dest='iterations', default=0, type=int, help='The number of iteration to execute. Supply a value of 1 or higher to restrict the effect of the morphological operation. Otherwise it is applied until saturation.')
    parser.add_argument('-s', '--size', dest='size', default=3, type=int, help='Size of the closing element (>=1). The higher this value, the bigger the wholes that get closed (closing) resp. unconnected elements that are removed (opening). In the 3D case, 1 equals a 6-connectedness, 2 a 12-connectedness, 3 a 18-connectedness, etc.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()            
    