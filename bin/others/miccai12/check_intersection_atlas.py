#!/usr/bin/python

"""Checks whether and how much an atlas for a given threshold and a massive 4D contour volume intersect."""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load
from argparse import ArgumentError
from scipy.ndimage.morphology import binary_erosion


# information
__author__ = "Oskar Maier"
__version__ = "r0.2.1, 2012-08-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
    Takes an atlas image and a threshold and checks in how far the atlas voxels
    below/above the threshold intersect with a supplied binary 4D volume.
    
    Creates an extensive statistic of the intersections as three CSV files. 
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
    spatial_dimension = 0
    
    # load volumes
    atlas_data, _ = load(args.atlas)
    contour_data, _ = load(args.contour)
    
    # check volumes
    if atlas_data.shape != contour_data.shape:
        raise ArgumentError('The shapes of the two supplied volumes do not match.')
    
    # truncate atlas data and convert to binary images
    if not args.lower: atlas_data[atlas_data <= args.threshold] = 0
    else: # bg case
        mask = atlas_data <= args.threshold
        atlas_data[mask] = 1
        atlas_data[~mask] = 0
    atlas_data = atlas_data.astype(scipy.bool_)
    contour_data = contour_data.astype(scipy.bool_)
        
    # split ED 3D volume from 4D volumes
    slicer = [slice(None) for _ in range(atlas_data.ndim)]
    slicer[temporal_dimension] = slice(0, 1)
    atlas_data_ed = scipy.squeeze(atlas_data[slicer])
    contour_data_ed = scipy.squeeze(contour_data[slicer])
    
    # determine ES volume position and extract
    contour_data_es = None
    for slid in range(1, contour_data.shape[temporal_dimension]):
        slicer[temporal_dimension] = slice(slid, slid + 1)
        if contour_data[slicer].any():
            atlas_data_es = scipy.squeeze(atlas_data[slicer])
            contour_data_es = scipy.squeeze(contour_data[slicer])
            break
        
    if None == contour_data_es:
        print("[ERROR] No ED phase detected in contour {}. Exiting.".format(args.atlas))
        exit(-1)
        
    # erode mask created from atlas if requested
    if not 0 == args.erosion:
        logger.info('Eroding by factor {}...'.format(args.erosion))
        
        slicer = [slice(None) for _ in range(atlas_data_ed.ndim)]
        for slid in range(1, atlas_data_ed.shape[spatial_dimension]):
            slicer[spatial_dimension] = slice(slid, slid + 1)
            atlas_data_ed[slicer] = binary_erosion(atlas_data_ed[slicer], iterations=args.erosion, border_value=1)
            atlas_data_es[slicer] = binary_erosion(atlas_data_es[slicer], iterations=args.erosion, border_value=1)
        
    # determine slice-wise statistical parameters for ED and ES phase
    ed_slice_statistics = []
    es_slice_statistics = []
    slicer = [slice(None) for _ in range(atlas_data_ed.ndim)]
    for slid in range(1, atlas_data_ed.shape[spatial_dimension]):
        slicer[spatial_dimension] = slice(slid, slid + 1)
        if not args.lower: # fg case
            if contour_data_ed[slicer].any():
                ed_slice_statistics.append(collect_data_fg(atlas_data_ed[slicer], contour_data_ed[slicer]))
            if contour_data_es[slicer].any():
                es_slice_statistics.append(collect_data_fg(atlas_data_es[slicer], contour_data_es[slicer]))
        else: # bg case
            if contour_data_ed[slicer].any():
                ed_slice_statistics.append(collect_data_bg(atlas_data_ed[slicer], contour_data_ed[slicer]))
            if contour_data_es[slicer].any():
                es_slice_statistics.append(collect_data_bg(atlas_data_es[slicer], contour_data_es[slicer]))
    
    # compute additional statistics
    #ed_statistics = [(mean(l), sum(l)) for l in zip(*ed_slice_statistics)] # 3 entries for the three values; each tuple of 0:mean, 1:total
    #es_statistics = [(mean(l), sum(l)) for l in zip(*es_slice_statistics)] # 3 entries for the three values; each tuple of 0:mean, 1:total
    total_list = list(ed_slice_statistics)
    total_list.extend(es_slice_statistics)
    #total_statistics = [(mean(l), sum(l)) for l in zip(*total_list)] # 3 entries for the three values; each tuple of 0:mean, 1:total
        
    # save results in csv file
    with open(args.output, 'w') as f:
        f.write('threshold;{}e{}\n'.format(args.threshold, args.erosion))
        write_results(f, 'ED slices', ed_slice_statistics)
        write_results(f, 'ES slices', es_slice_statistics)
    
def write_results(f, title, sliceswise):
    """
    Write the standard csv file.
    """
    f.write('{}\n'.format(title))
    f.write('"sliceno (from basal down)";"rightly classified (%)";"wrongly classified (%)";"undefined (%)"\n')
    for slid, entry in enumerate(sliceswise): f.write('{};{};{};{}\n'.format(slid, *entry))

def mean(col):
    """Compute the mean value of a collection."""
    return sum(col)/float(len(col))
    
def collect_data_fg(mask, contour):
    """
    Collects statistical data to evaluate how well the mask voxels fit to the contour.
    """
    total_contour_size = len(contour.nonzero()[0])
    total_mask_size = len(mask.nonzero()[0])
    intersection = len((mask & contour).nonzero()[0])
    mask_out_of_contour = total_mask_size - intersection
    contour_out_of_mask = total_contour_size - intersection
    
    return (intersection / float(total_contour_size), # intersection as percentage of total contour size (range 0-1), i.e. rightly classified FG
            mask_out_of_contour / float(total_contour_size),  # wrongly classified fg as percentage of total contour size (range 0-1)
            contour_out_of_mask / float(total_contour_size)) # area left for the gc to assign as percentage of total contour size (range 0-1)
    
def collect_data_bg(mask, contour):
    """
    Collects statistical data to evaluate how well the mask voxels fit to the contour.
    """
    total_contour_size = len(contour.nonzero()[0])
    intersection = len((mask & contour).nonzero()[0])
    hole_size = len((~mask).nonzero()[0])
    contour_out_of_mask = total_contour_size - intersection
    hole_not_covered_by_contour = hole_size - contour_out_of_mask
    
    return (contour_out_of_mask / float(total_contour_size), # fg contour rightly not classified as bg
            intersection / float(total_contour_size), # intersection as percentage of total contour size (range 0-1)), i.e. FG wrongly classified as BG
            hole_not_covered_by_contour / float(total_contour_size)) # area left for the gc to assign as percentage of total contour size (range 0-?)    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('atlas', help='Atlas volume.')
    parser.add_argument('contour', help='Contour volume.')
    parser.add_argument('threshold', type=float, help='Threshold value.')
    parser.add_argument('output', help='Output CSV file, where to store the slice-wise results.')
    parser.add_argument('-e', dest='erosion', type=int, default=0, help='Erode bg resp. fg mask by this value before processing.')
    parser.add_argument('-l', dest='lower', action='store_true', help='Lower, i.e. use all voxels lower or equal than the threshold rather than higher than (which is the normal behaviour).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Override existing output files without prompting.')
    return parser

if __name__ == "__main__":
    main()     
