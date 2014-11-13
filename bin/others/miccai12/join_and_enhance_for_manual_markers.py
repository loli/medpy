#!/usr/bin/python

"""Joins a number of 3D manual markers into a 4D marker volume, enhancing the data on the way."""

# build-in modules
import argparse
import logging
import re

# third-party modules
import scipy.ndimage

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.core.exceptions import ArgumentError
import os
import itertools


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.3, 2012-06-15"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
    Takes a number of 3D volumes with manual markers inside (!) the RV wall, enhances the
    markers to FG and BG markers for inner resp. outer RV wall and saves them as proper
    4D volumes.
    
    Note that the supplied volumes have to follow a special naming convention.
    Additionally requires the original 4D image as example.
                
    Images in 4D can not me visualized very well for the creation of manual markers. This
    script and its counterpart allow to de-construct a 4D volume in various ways and to
    afterwards combine the created marker volumes easily. Just select one of the following
    modi, create markers for the resulting volumes and then join the markers together.
    
    This script supports the combination of all manual marker volumes that follow the naming
    convention. See the counterpart of this script, "Split for manual markers", for some more
    remarks on this subject.
                
    Some remarks on the manual markers:
    The supplied marker file has to contain one marker (with any index other than 0). If
    additionally markers are present, these are all joined together into a single one.
    Additionally the marker has to form a closed (!) circle.
    An exception are markers with an index equal to or higher than 10, these are removed.
    
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
    inner_data = scipy.zeros(original_data.shape, scipy.uint8)
    outer_data = scipy.zeros(original_data.shape, scipy.uint8)
    del original_data
    
    # First step: Constructing all marker images
    logger.info('Constructing marker information...')
    basename_old = False
    # iterate over marker images
    for marker_image in args.input:
        # extract information from filename and prepare slicer object
        basename, slice_dimension, slice_number = re.match(r'.*m(.*)_d([0-9])_s([0-9]{4}).*', marker_image).groups()
        slice_dimension = int(slice_dimension)
        slice_number = int(slice_number)
        # check basenames
        if basename_old and not basename_old == basename:
            logger.warning('The marker seem to come from different sources. Encountered basenames {} and {}. Continuing anyway.'.fromat(basename, basename_old))
        basename_old = basename
        # prepare slicer
        slicer = [slice(None)] * inner_data.ndim
        slicer[slice_dimension] = slice_number
        # load marker image and prepare (deleting markers with indices > 10 and mergin all others)
        marker_data, _ = load(marker_image)
        marker_data[marker_data >= 10] = 0
        # create markers from sparse marker data
        marker_data_inner, marker_data_outer = __create_markers(marker_data.astype(scipy.bool_), slice_dimension, args.di, args.do)
        # add to resulting final marker images
        inner_data[slicer] += marker_data_inner
        outer_data[slicer] += marker_data_outer
    
    # check if any marker present
    if 0 == len(inner_data.nonzero()[0]):
        raise ArgumentError('No markers for the inner wall could be created.')
    if 0 == len(outer_data.nonzero()[0]):
        raise ArgumentError('No markers for the outer wall could be created.')
    
    # Second step: Thin out marker information by emptying every second slice
    if args.thinning:
        logger.info('Thinning out every second slice...')
        inner_data = __thin_out_markers(inner_data)
        outer_data = __thin_out_markers(outer_data)
    
    # Third step: Enhance marker information by propagating it over time
    logger.info('Enhancing marker information...')
    inner_data = __enhance_markers(inner_data, args.efg, args.ebg)
    outer_data = __enhance_markers(outer_data, args.di, args.do)
    
    # saving
    inner_name = args.output.format('i')
    save(inner_data, inner_name, original_header, args.force)
    
    outer_name = args.output.format('o')
    save(outer_data, outer_name, original_header, args.force)
        
    logger.info("Successfully terminated.")

def __thin_out_markers(marker_data):
    """
    Thins out marker data by removing every second slide.
    """
    # constants
    xdim = 1
    ydim = 2
    tdim = 3
    
    # parameters
    view = (xdim, ydim, tdim)
    arr = marker_data
    odd = True
    counter = 0
    
    # function
    def fun(_arr, odd):
        """
        Returns the original array if odd = True, otherwise an empty copy of it.
        Also returns the inverse of odd.
        """
        if odd:
            return _arr, not odd
        else:
            return scipy.zeros_like(_arr), not odd
    
    # create list of iterations
    iterations = [[None] if dim in view else list(range(arr.shape[dim])) for dim in range(arr.ndim)]
     
    # iterate, create slicer, execute function and collect results
    for indices in itertools.product(*iterations):
        slicer = [slice(None) if idx is None else slice(idx, idx + 1) for idx in indices]
        if not 0 == len(scipy.nonzero(arr[slicer])[0]) and odd:
            counter += 1
        results, odd = fun(scipy.squeeze(arr[slicer]), odd)
        arr[slicer] = results.reshape(arr[slicer].shape)
        
    logger = Logger.getInstance()
    logger.debug('Kept {} slices after thinning.'.format(counter))
        
    return arr
    
def __enhance_markers(marker_data, efg, ebg):
    """
    Takes an marker image (incl. fg and bg markers) and enhance the encoded
    information by propagating the markers through time.
    
    This function assumes a 4D volume with markers in the ED phase, which corresponds to
    the first phase (time-slice).
    """
    # constants
    contour_dimension = 2
    time_dimension = 3
    erosions_per_step_fg = efg # all take a 5 here as sufficient, all except no. 3 take also a 3
    erosions_per_step_bg = ebg # all take a 2 here as sufficient, all except no. 3 also take a 1
    
    # prepare slicer
    slicer = [slice(None)] * marker_data.ndim
    
    # iterate over spatial dimension
    for slice_id in range(marker_data.shape[contour_dimension]): 
        slicer[contour_dimension] = slice(slice_id, slice_id+1)
    
        # extract first time slice
        slicer[time_dimension] = slice(0, 1)
        phase_prototype = scipy.squeeze(marker_data[slicer]).copy() # IMPORTANT TO COPY!
        
        # skip round if empty
        if 0 == len(phase_prototype.nonzero()[0]) : continue
        
        # copy prototype (incl. background) to last slice
        slicer[time_dimension] = slice(-1, None)
        phase_last = scipy.squeeze(marker_data[slicer])
        phase_last += phase_prototype
        
        # split into fg and bg prototype
        phase_prototype_fg = phase_prototype == 1
        phase_prototype_bg = phase_prototype == 2
        
        # iterate over time slices from both sides at once
        for time_id in range(1, marker_data.shape[time_dimension] / 2): # means skipping middle phase in odd phase numbers
            # erode prototypes
            phase_prototype_fg = scipy.ndimage.binary_erosion(phase_prototype_fg, iterations=erosions_per_step_fg)
            phase_prototype_bg = scipy.ndimage.binary_erosion(phase_prototype_bg, iterations=erosions_per_step_bg)
            # extract from the front and add prototype
            slicer[time_dimension] = slice(time_id, time_id + 1)
            phase = scipy.squeeze(marker_data[slicer])
            phase[phase_prototype_fg] = 1
            phase[phase_prototype_bg] = 2
            # extract from the end and add prototype
            slicer[time_dimension] = slice(marker_data.shape[time_dimension] - time_id - 1, marker_data.shape[time_dimension] - time_id)
            phase = scipy.squeeze(marker_data[slicer])
            phase[phase_prototype_fg] = 1
            phase[phase_prototype_bg] = 2
             
    return marker_data
    
     
    
def __create_markers(marker_data, marker_dim, di, do):
    """
    Takes an image with markers inside the RV wall and returns two images with the inner
    repectively outer BG and FG markers.
    """ 
    # constants
    contour_dimension = 2
    time_dimension = 3
    distance_inner = di # within the images 01-05 takes values down to 5, standard is 9 to leave some space
    distance_outer = do # within the images 01-05 takes values down to 6, standard is 10 to leave some space
    
    # prepare output volumes
    inner_data = scipy.zeros(marker_data.shape, scipy.uint8)
    outer_data = scipy.zeros(marker_data.shape, scipy.uint8)
    
    # prepare slicer
    slicer = [slice(None)] * marker_data.ndim
    
    # iterate over contour dimension and process each subvolume slice separately
    if marker_dim == contour_dimension: iter_dimension = time_dimension
    else: iter_dimension = contour_dimension
    for slice_id in range(marker_data.shape[iter_dimension]):
        slicer[contour_dimension] = slice(slice_id, slice_id+1)
        # extract subvolume
        marker_subvolume = scipy.squeeze(marker_data[slicer])
        # skip step if no marker data present
        if 0 == len(marker_subvolume.nonzero()[0]): continue
        
        # check if the marker forms a closed circle
        marker_data_filled = scipy.ndimage.binary_fill_holes(marker_subvolume)
        if (marker_subvolume == marker_data_filled).all():
            raise ArgumentError('The supplied marker does not form a closed structure!')
        
        # COMPUTE MARKERS FOR INNER WALL
        inner_data_subvolume = scipy.squeeze(inner_data[slicer])
        marker_data_dilated = scipy.ndimage.binary_dilation(marker_subvolume, iterations = distance_inner) # dilate by distance_inner
        marker_data_dilated_filled = scipy.ndimage.binary_fill_holes(marker_data_dilated) # fill hole
        # fill hole of original and take inverse as inner bg marker (but erode first once for security)
        inner_data_subvolume[scipy.ndimage.binary_erosion(~scipy.ndimage.binary_fill_holes(marker_subvolume))] = 2
        # if the dilation was to large to keep any markers, use less
        c = 0
        while 0 == len(scipy.logical_xor(marker_data_dilated, marker_data_dilated_filled).nonzero()[0]):
            c += 1
            marker_data_dilated = scipy.ndimage.binary_dilation(marker_subvolume, iterations = distance_inner - c)
            marker_data_dilated_filled = scipy.ndimage.binary_fill_holes(marker_data_dilated) # fill hole
        # take hole as inner fg marker
        inner_data_subvolume[scipy.logical_xor(marker_data_dilated, marker_data_dilated_filled)] = 1
        
        # COMPUTE MARKERS FOR OUTER WALL
        outer_data_subvolume = scipy.squeeze(outer_data[slicer])
        marker_data_dilated = scipy.ndimage.binary_dilation(marker_subvolume, iterations = distance_outer) # dilate by distance_outer
        marker_data_dilated_filled = scipy.ndimage.binary_fill_holes(marker_data_dilated) # fill hole
        # take inverse as outer bg marker
        outer_data_subvolume[~marker_data_dilated_filled] = 2
        # fill hole of original and take as outer fg marker (but erode first twice for security)
        outer_data_subvolume[scipy.ndimage.binary_erosion(scipy.ndimage.binary_fill_holes(marker_subvolume), iterations=2)] = 1
        
    return inner_data, outer_data
    
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
    parser.add_argument('--di', dest='di', default=5, type=int, help='In which distance to the manual markers to place the inner wall background markers.')
    parser.add_argument('--do', dest='do', default=6, type=int, help='In which distance to the manual markers to place the outer wall background markers.')
    parser.add_argument('--efg', dest='efg', default=5, type=int, help='The foreground markers are eroded by this value before being propagated to the next slide.')
    parser.add_argument('--ebg', dest='ebg', default=2, type=int, help='The background markers are eroded by this value before being propagated to the next slide.')
    parser.add_argument('-t', dest='thinning', action='store_true', help='Thin out markers by removing every second slice.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 
    
