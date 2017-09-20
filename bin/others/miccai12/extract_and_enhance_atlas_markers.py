#!/usr/bin/env python

"""Extracts FG and BG markers from an atlas image and enhances them."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
from scipy.spatial.distance import cdist

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.core.exceptions import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-08-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
    Extracts FG and BG markers from an atlas image and enhances them.
    
    Uses the supplied threshold to determine which parts of the atlas should be treated
    as fore- and which as background. Then copies the ED phase to the last (which is
    again ED) and propagates the ED phase markers towards the ES phase.
    """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    temporal_dimension = 3
    
    # check parameters
    if args.bg_threshold > 0.5: logger.warning('The supplied BG threshold is rather high. This might corrupt the results.')
    if args.fg_threshold < 0.5: logger.warning('The supplied FG threshold is rather low. This might corrupt the results.')
    
    # check if output file already exists
    if not args.force and os.path.exists(args.output):
        raise ArgumentError('The supplied output file {} already exists.'.format(args.output))
    
    # loading atlas image
    atlas_data, atlas_header = load(args.atlas)
    
    # prepare neutral slice object
    slicer = [slice(None) for _ in range(atlas_data.ndim)]
    
    logger.info('Extracting ED and ES phase volumes...')
    
    # extract ED 3D volume
    slicer[temporal_dimension] = slice(0,1) # first is ed phase
    ed_data_fg = scipy.squeeze(atlas_data[slicer])
    
    # extract ES 3D volume
    es_data_fg = None
    for slidx in range(1, atlas_data.shape[temporal_dimension]):
        slicer[temporal_dimension] = slice(slidx, slidx + 1)
        if scipy.any(atlas_data[slicer]):
            es_data_fg = scipy.squeeze(atlas_data[slicer]) # first after ed phase is es phase
            es_slidx = slidx # conserve for later usage
            continue
        
    if None == es_data_fg:
        raise AttributeError('Could not find any data in the ES phase of the atlas image.')
        
    logger.debug('Extracted ed volume {} and es volume {}.'.format(ed_data_fg.shape, es_data_fg.shape))
    
    # split into FG and BG volumes and convert to bool type
    logger.info('Splitting into FG and BG binary volumes representing the markers...')
    ed_data_bg = ed_data_fg.copy()
    es_data_bg = es_data_fg.copy()
    ed_data_fg[ed_data_fg <= args.fg_threshold] = 0
    es_data_fg[es_data_fg <= args.fg_threshold] = 0
    ed_data_bg[ed_data_bg <= args.bg_threshold] = 0
    es_data_bg[es_data_bg <= args.bg_threshold] = 0
    ed_data_fg = ed_data_fg.astype(scipy.bool_)
    es_data_fg = es_data_fg.astype(scipy.bool_)
    ed_data_bg = ~ed_data_bg.astype(scipy.bool_)
    es_data_bg = ~es_data_bg.astype(scipy.bool_)
    
    # see if any is empty
    if not scipy.any(es_data_fg):
        raise AttributeError('No foreground marker data for es phase.')
    elif not scipy.any(es_data_bg):
        raise AttributeError('No background marker data for es phase.')
    elif not scipy.any(ed_data_fg):
        raise AttributeError('No foreground marker data for ed phase.')
    elif not scipy.any(ed_data_bg):
        raise AttributeError('No background marker data for ed phase.')
    
    marker_data = scipy.zeros(atlas_data.shape, scipy.uint8)
    
    # enhance the markers by interpolating between binary foreground objects of ED and ES phase
    logger.info('Enhancing the markers from ED-first to ES phase...')
    slicer[temporal_dimension] = slice(0, es_slidx + 1) # first half
    marker_data[slicer] = interpolateBetweenBinaryObjects(ed_data_fg, es_data_fg, es_slidx - 1)
    logger.info('Enhancing the markers from ES to ED-second phase...')
    slicer[temporal_dimension] = slice(es_slidx + 1, None) # second half
    marker_data[slicer] = interpolateBetweenBinaryObjects(es_data_fg, ed_data_fg, marker_data.shape[temporal_dimension] - es_slidx - 3)
    
    # setting the background markers
    logger.info('Setting bg markers...')
    slicer[temporal_dimension] = slice(0,1) # first ed phase
    marker_data[slicer][ed_data_bg] = 2
    slicer[temporal_dimension] = slice(-1, None) # second ed phase
    marker_data[slicer][ed_data_bg] = 2
    slicer[temporal_dimension] = slice(es_slidx, es_slidx + 1) # es phase
    marker_data[slicer][es_data_bg] = 2
        
    save(marker_data, args.output, atlas_header, args.force)
        
    logger.info("Successfully terminated.")

def interpolateBetweenBinaryObjects(obj1, obj2, slices):
    """
    Takes two binary objects and puts slices slices in-between them, each of which
    contains a smooth binary transition between the objects.
    """
    # constants
    temporal_dimension = 3
    # flip second returned binary objects along temporal axis
    slicer = [slice(None) for _ in range(obj1.ndim + 1)]
    slicer[temporal_dimension] = slice(None, None, -1)
    # logical-and combination
    ret = __interpolateBetweenBinaryObjects(obj1, obj2, slices) | __interpolateBetweenBinaryObjects(obj2, obj1, slices)[slicer]
    # control step: see if last volume corresponds to obj2
    slicer[temporal_dimension] = slice(-1, None)
    if not scipy.all(scipy.squeeze(ret[slicer]) == obj2.astype(scipy.bool_)):
        raise Exception('Last created object does not correspond to obj2. Difference of {} voxels.'.format(len(scipy.nonzero(scipy.squeeze(ret[slicer]) & obj2.astype(scipy.bool_))[0])))
    
    return ret

def __interpolateBetweenBinaryObjects(obj1, obj2, slices):
    """
    Takes two binary objects and puts slices slices in-between them, each of which
    contains a smooth binary transition between the objects.
    @note private inner function
    """
    if not obj1.shape == obj2.shape:
        raise AttributeError('The two supplied objects have to be of the same shape, not {} and {}.'.format(obj1.shape, obj2.shape))
    
    # constant
    offset = 0.5 # must be a value smaller than the minimal distance possible
    temporal_dimension = 3
    
    # get all voxel position
    obj1_voxel = scipy.nonzero(obj1)
    obj2_voxel = scipy.nonzero(obj2)
    
    # get smallest pairwise distances between all object voxels
    distances = cdist(scipy.transpose(obj1_voxel),
                      scipy.transpose(obj2_voxel))
    
    # keep for each True voxel of obj1 only the smallest distance to a True voxel in obj2 
    min_distances = distances.min(1)
    
    # test if all seems to work
    if len(min_distances) != len(obj1_voxel[0]):
        raise Exception('Invalid number of minimal distances received.')
    
    # replace True voxels in obj1 with their respective distances to the True voxels in obj2
    thr_obj = obj1.copy()
    thr_obj = thr_obj.astype(scipy.float_)
    thr_obj[obj1_voxel] = min_distances
    thr_obj[obj1_voxel] += offset # previous steps distances include zeros, therefore this is required
    
    # compute the step size for each slice that is added
    maximum = min_distances.max()
    step = maximum / float(slices + 1)
    threshold = maximum
    
    # control step: see if thr_obj really corresponds to obj1
    if not scipy.all(thr_obj.astype(scipy.bool_) == obj1.astype(scipy.bool_)):
        raise Exception('First created object does not correspond to obj1.')
    
    # assemble return volume
    return_volume = [thr_obj.astype(scipy.bool_)] # corresponds to obj1
    for _ in range(slices):
        threshold -= step
        # remove all value higher than the threshold
        thr_obj[thr_obj > threshold] = 0
        # add binary volume to list /makes a copy)
        return_volume.append(thr_obj.astype(scipy.bool_)) 
    
    # add last slice (corresponds to es obj2 slice)
    thr_obj[thr_obj > offset] = 0
    return_volume.append(thr_obj.astype(scipy.bool_)) 
    
    # return binary scipy array
    return scipy.rollaxis(scipy.asarray(return_volume, dtype=scipy.bool_), 0, temporal_dimension + 1)
    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('atlas', help='The atlas volume.')
    parser.add_argument('output', help='Target volume. Contains foreground (=1) and background (=2) markers.')
    parser.add_argument('fg_threshold', type=float, help='All atlas values greater than this will be considered FG markers.')
    parser.add_argument('bg_threshold', type=float, help='All atlas values less or equal than this will be considered BG markers.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 
    