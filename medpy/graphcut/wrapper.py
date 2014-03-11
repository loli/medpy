"""
@package medpy.graphcut.wrapper
Wrappers for executing graph cuts and other convenience functions.

Functions:
    - 
    
@author Oskar Maier
@version r0.1.0
@since 2012-06-25
@status Release
"""

# build-in module
import multiprocessing
import itertools
import math

# third-party modules
import scipy

# own modules
from energy_label import boundary_stawiaski
from generate import graph_from_labels
from ..core.exceptions import ArgumentError
from ..core.logger import Logger
from medpy.filter.label import relabel, relabel_map

# code
def split_marker(marker, fg_id = 1, bg_id = 2):
    """
    Splits an integer marker image into two binary image containing the foreground and
    background markers respectively.
    All encountered 1's are hereby treated as foreground, all 2's as background, all 0's
    as neutral marker and all others are ignored.
    This behaviour can be changed by supplying the fg_id and/or bg_id parameters.
    
    @param marker the marker image
    @type marker scipy.ndimage (dtype=scipy.int?)
    @param fg_id the id that should be treated as foreground
    @type fg_id int
    @param bg_id the id that should be treated as background
    @type bg_id int
    
    @return fgmarkers, bgmarkers
    @rtype scipy.ndimage (dtype=scipy.bool_), scipy.ndimage (dtype=scipy.bool_)
    """
    img_marker = scipy.asarray(marker)
    
    img_fgmarker = scipy.zeros(img_marker.shape, scipy.bool_)
    img_fgmarker[img_marker == fg_id] = True
    
    img_bgmarker = scipy.zeros(img_marker.shape, scipy.bool_)
    img_bgmarker[img_marker == bg_id] = True
    
    return img_fgmarker, img_bgmarker

def graphcut_split(graphcut_function, regions, gradient, foreground, background, minimal_edge_length = 100, overlap = 10, processes = None):
    """
    Executes a graph cut by splitting the original volume into a number of sub-volumes of
    a minimal edge length. These are then processed in subprocesses.
    
    This can be significantly faster than the traditional graph cuts, but should be
    used with, as it can lead to different results. To minimize this effect, the overlap
    parameter allows control over how much the respective sub-volumes should overlap.
    
    @param graphcut_function the graph cut to use (e.g. @link graphcut_stawiaski())
    @type graphcut_function function
    
    @param regions the regions image
    @type regions scipy.ndarray (dtype=scipy.int?)
    @param gradient the gradient image
    @type gradient scipy.ndarray (dtype=scipy.float?)
    @param foreground the foreground markers
    @type foreground scipy.ndarray (dtype=scipy.bool_)
    @param background the background markers
    @type background scipy.ndarray (dtype=scipy.bool_)
    
    @param minimal_edge_length the minimal edge length of the sub-volumes
    @type minimal_edge_length int
    @param overlap the overlap (in voxels) between the generated sub-volumes
    @type overlap int
    
    @param processes the number of processes to run simultaneously, if not supplied, will
                     be the same as the number of processors
    @type processes int
    """
    # initialize logger
    logger = Logger.getInstance()
    
    # ensure that input images are scipy arrays
    img_region = scipy.asarray(regions)
    img_gradient = scipy.asarray(gradient)
    img_fg = scipy.asarray(foreground, dtype=scipy.bool_)
    img_bg = scipy.asarray(background, dtype=scipy.bool_)
    
    # ensure correctness of supplied images
    if not (img_region.shape == img_gradient.shape == img_fg.shape == img_bg.shape): raise ArgumentError('All supplied images must be of the same shape.')    
    
    # check and eventually enhance input parameters
    if minimal_edge_length < 10: raise ArgumentError('A minimal edge length smaller than 10 is not supported.')
    if overlap < 0: raise ArgumentError('A negative overlap is not supported.')
    if overlap >= minimal_edge_length: raise ArgumentError('The overlap is not allowed to exceed the minimal edge length.')
    
    # compute how to split the volumes into sub-volumes i.e. determine step-size for each image dimension
    shape = list(img_region.shape)
    steps = map(lambda x: x / int(minimal_edge_length), shape) # we want integer division
    steps = [1 if 0 == x else x for x in steps] # replace zeros by ones
    stepsizes = [math.ceil(x / float(y)) for x, y in zip(shape, steps)]
    logger.debug('Using a minimal edge length of {}, a sub-volume size of {} was determined from the shape {}, which means {} sub-volumes.'.format(minimal_edge_length, stepsizes, shape, reduce(lambda x, y: x*y, steps)))
    
    # control step-sizes to definitely cover the whole image
    covered_shape = [x * y for x, y in zip(steps, stepsizes)]
    for c, o in zip(covered_shape, shape):
        if c < o: raise Exception("The computed sub-volumes do not cover the complete image!")
            
    # iterate over the steps and extract subvolumes according to the stepsizes
    slicer_steps = [range(0, int(step * stepsize), int(stepsize)) for step, stepsize in zip(steps, stepsizes)]
    slicers = [[slice(_from, _from + _offset + overlap) for _from, _offset in zip(slicer_step, stepsizes)] for slicer_step in itertools.product(*slicer_steps)]
    subvolumes_input = [(img_region[slicer],
                         img_gradient[slicer],
                         img_fg[slicer],
                         img_bg[slicer]) for slicer in slicers]
    
    # execute the graph cuts and collect results
    subvolumes_output = graphcut_subprocesses(graphcut_function, subvolumes_input, processes)
    
    # put back data together
    img_result = scipy.zeros(img_region.shape, dtype=scipy.bool_)
    for slicer, subvolume in zip(slicers, subvolumes_output):
        sslicer_antioverlap = [slice(None)] * img_result.ndim
        
        # treat overlap area using logical-and (&)
        for dim in range(img_result.ndim):
            if 0 == slicer[dim].start: continue
            sslicer_antioverlap[dim] = slice(overlap, None)
            sslicer_overlap = [slice(None)] * img_result.ndim
            sslicer_overlap[dim] = slice(0, overlap)
            img_result[slicer][sslicer_overlap] = scipy.logical_and(img_result[slicer][sslicer_overlap], subvolume[sslicer_overlap])
            
        # treat remainder through assignment
        img_result[slicer][sslicer_antioverlap] = subvolume[sslicer_antioverlap]
    
    return img_result.astype(scipy.bool_)
    

def graphcut_subprocesses(graphcut_function, graphcut_arguments, processes = None):
    """
    Executes multiple graph cuts in parallel.
    This can result in a significant speed-up.
    
    @param graphcut_function the graph cut to use (e.g. @link graphcut_stawiaski())
    @type graphcut_function function
    @param graphcut_arguments list of arguments to pass to the respective subprocesses 
    @type graphcut_arguments sequence
    @param processes the number of processes to run simultaneously, if not supplied, will
                     be the same as the number of processors
    @type processes int
    
    @return list of all results, of same length as the supplied graphcut_arguments list
    @rtype sequence
    """
    # initialize logger
    logger = Logger.getInstance()
    
    # check and eventually enhance input parameters
    if not processes: processes = multiprocessing.cpu_count()
    if not int == type(processes) or processes <= 0: raise ArgumentError('The number processes can not be zero or negative.')
    
    logger.debug('Executing graph cuts in {} subprocesses.'.format(multiprocessing.cpu_count()))
    
    # creates subprocess pool and execute
    pool = multiprocessing.Pool(processes)
    results = pool.map(graphcut_function, graphcut_arguments)
    
    return results


def graphcut_stawiaski(regions, gradient = False, foreground = False, background = False):
    """
    Executes a Stawiaski label graph cut.
    
    @param regions the regions image
    @type regions scipy.ndarray (dtype=scipy.int?)
    @param gradient the gradient image
    @type gradient scipy.ndarray (dtype=scipy.float?)
    @param foreground the foreground markers
    @type foreground scipy.ndarray (dtype=scipy.bool_)
    @param background the background markers
    @type background scipy.ndarray (dtype=scipy.bool_)
    
    @return the cut image as binary array
    @rtype scipy.ndarray (dtype=scipy.bool_)
    
    @raise ArgumentError when the supplied data is erroneous
    """
    # initialize logger
    logger = Logger.getInstance()
    
    # unpack images if required
    # !TODO: This is an ugly hack, especially since it can be seen inside the function definition
    # How to overcome this, since I can not use a wrapper function as the whole thing must be pickable
    if not gradient and not foreground and not background: 
        regions, gradient, foreground, background = regions
    
    # ensure that input images are scipy arrays
    img_region = scipy.asarray(regions)
    img_gradient = scipy.asarray(gradient)
    img_fg = scipy.asarray(foreground, dtype=scipy.bool_)
    img_bg = scipy.asarray(background, dtype=scipy.bool_)
    
    # ensure correctness of supplied images
    if not (img_region.shape == img_gradient.shape == img_fg.shape == img_bg.shape): raise ArgumentError('All supplied images must be of the same shape.')

    # recompute the label ids to start from id = 1
    img_region = relabel(img_region)
    
    # generate graph
    gcgraph = graph_from_labels(img_region, img_fg, img_bg, boundary_term = boundary_stawiaski, boundary_term_args = (img_gradient))
    
    # execute min-cut
    maxflow = gcgraph.maxflow() # executes the cut and returns the maxflow value
    
    logger.debug('Graph-cut terminated successfully with maxflow of {}.'.format(maxflow))
    
    # apply results to the region image
    mapping = [0] # no regions with id 1 exists in mapping, entry used as padding
    mapping.extend(map(lambda x: 0 if gcgraph.termtype.SINK == gcgraph.what_segment(int(x) - 1) else 1,
                       scipy.unique(img_region)))
    img_results = relabel_map(img_region, mapping)
    
    return img_results.astype(scipy.bool_)
