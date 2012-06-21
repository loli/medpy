#!/usr/bin/python

"""Execute a graph cut on a region image based on some foreground and background markers."""

# build-in modules
from argparse import RawTextHelpFormatter
import argparse
import logging
import os

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import ArgumentError, Logger
from medpy.io import load, save
from medpy import graphcut
from medpy import filter
import math
import itertools



# information
__author__ = "Oskar Maier"
__version__ = "r0.3.4, 2012-03-16"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  !Modified version of original GC label, as splits the volumes into
                  more handy sizes before processing them. Also uses multiple subprocesses.
                  
                  Perform a binary graph cut using Boykov's max-flow/min-cut algorithm.
                  
                  This implementation does only compute a boundary term and does not use
                  any regional term. The desired boundary term can be selected via the
                  --boundary argument. Depending on the selected term, an additional
                  image has to be supplied as badditional.
                  
                  In the case of the stawiaski boundary term, this is the gradient image.
                  In the case of the difference of means, it is the original image.
                  
                  Furthermore the algorithm requires the region map of the original
                  image, a binary image with foreground markers and a binary
                  image with background markers.
                  
                  Additionally a filename for the created binary mask marking foreground
                  and background has to be supplied.
                  
                  Note that the input images must be of the same dimensionality,
                  otherwise an exception is thrown.
                  Note to take into account the input images orientation.
                  Note that the quality of the resulting segmentations depends also on
                  the quality of the supplied markers.
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
        
    # check if output image exists
    if not args.force:
        if os.path.exists(args.output):
            logger.warning('The output image {} already exists. Exiting.'.format(args.output))
            exit(-1)
            
    # constants
    # the minimal edge length of a subvolume-cube ! has to be of type int!
    minimal_edge_length = 100
    overlap = 20
    if overlap >= minimal_edge_length: logger.warning('The overlap should not exceed the minimal edge length.')

    # load input images
    region_image_data, reference_header = load(args.region)
    markers_image_data, _ = load(args.markers)
    gradient_image_data, _ = load(args.gradient)
    
    # split marker image into fg and bg images
    logger.info('Extracting foreground and background markers...')
    bgmarkers_image_data = scipy.zeros(markers_image_data.shape, scipy.bool_)
    bgmarkers_image_data[markers_image_data == 2] = True
    markers_image_data[markers_image_data != 1] = 0
    fgmarkers_image_data = markers_image_data.astype(scipy.bool_)
       
    # check if all images dimensions are the same
    if not (gradient_image_data.shape == region_image_data.shape == fgmarkers_image_data.shape == bgmarkers_image_data.shape):
        logger.critical('Not all of the supplied images are of the same shape.')
        raise ArgumentError('Not all of the supplied images are of the same shape.')
    
    # compute how to split the volumes into subvolumes i.e. determine stepsize for each image dimension
    shape = list(region_image_data.shape)
    steps = map(lambda x: x / int(minimal_edge_length), shape) # we want integer division
    steps = [1 if 0 == x else x for x in steps] # replace zeros by ones
    stepsizes = [math.ceil(x / float(y)) for x, y in zip(shape, steps)]
    logger.debug('Using a minimal edge length of {}, a subcube-size of {} was determined from the shape {}, which means {} subcubes.'.format(minimal_edge_length, stepsizes, shape, reduce(lambda x, y: x*y, steps)))
    
    # controll stepsizes to definitely cover the whole image
    covered_shape = [x * y for x, y in zip(steps, stepsizes)]
    for c, o in zip(covered_shape, shape):
        if c < o: raise Exception("The computed subvolume cubes do not cover the complete image!")
            
    # iterate over the steps and extract subvolumes according to the stepsizes
    slicer_steps = [range(0, int(step * stepsize), int(stepsize)) for step, stepsize in zip(steps, stepsizes)]
    slicers = [[slice(_from, _from + _offset + overlap) for _from, _offset in zip(slicer_step, stepsizes)] for slicer_step in itertools.product(*slicer_steps)]
    subvolumes = [(region_image_data[slicer],
                   gradient_image_data[slicer],
                   fgmarkers_image_data[slicer],
                   bgmarkers_image_data[slicer]) for slicer in slicers]
    subvolumes = __gc_pool(subvolumes)
    
    
    # put data together
    output_volume = scipy.zeros(region_image_data.shape, dtype=scipy.bool_)
    for slicer, subvolume in zip(slicers, subvolumes):
        sslicer_antioverlap = [slice(None)] * output_volume.ndim
        
        # treat overlap area using logical and (&)
        for dim in range(output_volume.ndim):
            if 0 == slicer[dim].start: continue
            sslicer_antioverlap[dim] = slice(overlap, None)
            sslicer_overlap = [slice(None)] * output_volume.ndim
            sslicer_overlap[dim] = slice(0, overlap)
            output_volume[slicer][sslicer_overlap] = scipy.logical_and(output_volume[slicer][sslicer_overlap], subvolume[sslicer_overlap])
            
        # treat remainder through assignment
        output_volume[slicer][sslicer_antioverlap] = subvolume[sslicer_antioverlap]
    
    # save resulting mask
    save(output_volume, args.output, reference_header, args.force)

    logger.info('Successfully terminated.')

def __gc_pool(arguments, processes = None):
    "Executes multiple GC's in parallel"
    from multiprocessing import Pool, cpu_count
    logger = Logger.getInstance()
    logger.debug('Executing GC in {} subprocesses...'.format(cpu_count()))
    
    pool = Pool(processes)
    region_image_chunks = pool.map(__gc_volume, arguments)
    return region_image_chunks

def __gc_volume(images):
    "Executes a stawiaski graph cut over a volume."
    img_region, img_gradient, img_fg, img_bg = images
    
    logger = Logger.getInstance()
    
    # recompute the label ids to start from id = 1
    logger.info('Relabel input image...')
    img_region = filter.relabel(img_region)
    
    # generate graph
    logger.info('Preparing graph...')
    gcgraph = graphcut.graph_from_labels(img_region,
                                         img_fg,
                                         img_bg,
                                         boundary_term = graphcut.energy_label.boundary_stawiaski,
                                         boundary_term_args = (img_gradient)) # second is directedness of graph , 0)
    
    # execute min-cut
    logger.info('Executing min-cut...')
    maxflow = gcgraph.maxflow()
    logger.debug('Maxflow is {}'.format(maxflow))
    
    # apply results to the region image
    logger.info('Applying results...')
    mapping = [0] # no regions with id 1 exists in mapping, entry used as padding
    mapping.extend(map(lambda x: 0 if gcgraph.termtype.SINK == gcgraph.what_segment(int(x) - 1) else 1,
                       scipy.unique(img_region)))
    img_region = filter.relabel_map(img_region, mapping)
    
    return img_region
    

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('gradient', help='The gradient magnitude image of the image to segment.')
    parser.add_argument('region', help='The region image of the image to segment.')
    parser.add_argument('markers', help='Binary image containing the foreground (=1) and background (=2) markers.')
    parser.add_argument('output', help='The output image containing the segmentation.')
    parser.add_argument('-f', dest='force', action='store_true', help='Set this flag to silently override files that exist.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    

if __name__ == "__main__":
    main()