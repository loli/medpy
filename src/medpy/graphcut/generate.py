"""
@package medpy.graphcut.generate
Provides functionality to generate graphs efficiently from nD label-images and image voxels.

Functions:
    - def graph_from_labels(label_image,
                      fg_markers,
                      bg_markers,
                      regional_term = False,
                      boundary_term = False,
                      regional_term_args = False,
                      boundary_term_args = False): Creates a Graph object from a nD label image.
    - def graph_from_voxels(fg_markers,
                      bg_markers,
                      regional_term = False,
                      boundary_term = False,
                      regional_term_args = False,
                      boundary_term_args = False): Creates a Graph object from the voxels of an image.
@author Oskar Maier
@version r0.2.0
@since 2012-01-18
@status Release
"""

# build-in modules
import inspect

# third-party modules
import scipy
from scipy.ndimage.measurements import find_objects

# own modules
from ..core.Logger import Logger
from ..graphcut import Graph, GCGraph

def graph_from_voxels(fg_markers,
                      bg_markers,
                      regional_term = False,
                      boundary_term = False,
                      regional_term_args = False,
                      boundary_term_args = False):
    """
    Create a graphcut.graph.Graph object for all voxels of an image with a ndim * 2
    neighbourhood.
    
    Every voxel of the image is regarded as a node. They are connected to their immediate
    neighbours via arcs. If to voxels are neighbours is determined using
    ndim*2-connectedness (e.g. 3*2=6 for 3D). In the next step the arcs weights
    (n-weights) are computed using the supplied boundary_term function.
    
    Implicitly the graph holds two additional nodes: the source and the sink, so called
    terminal nodes. These are connected with all other nodes through arcs of an initial
    weight (t-weight) of zero.
    All voxels that are under the foreground markers are considered to be tightly bound
    to the source: The t-weight of the arc from source to these nodes is set to a maximum
    value. The same goes for the background markers: The covered voxels receive a maximum
    (graphcut.graph.Graph.MAX) t-weight for their arc towards the sink.
    
    @note If a voxel is marked as both, foreground and background, the background marker
    is given higher priority.
     
    @note all arcs whose weight is not explicitly set are assumed to carry a weight of
    zero.
    
    @param fg_markers The foreground markers as binary array of the same shape as the original image.
    @type fg_markers ndarray
    @param bg_markers The background markers as binary array of the same shape as the original image.
    @type bg_markers ndarray
    @param regional_term This can be either
                         False - all t-weights are set to 0, except for the nodes that are
                         directly connected to the source or sink.
                         , or a function - 
                         The supplied function is used to compute the t_edges. It has to
                         have the following signature
                         regional_term(regional_term_args),
                         and is supposed to return a dictionary with flattened voxel ids
                         as keys and a tuple (source_t_weight, sink_t_weight) as values.
                         The returned dictionary does only need to contain entries for
                         nodes where one of the t-weights is not zero. Additional
                         parameters can be passed via the regional_term_args argument.
    @type regional_term function
    @param boundary_term This can be either
                         False - 
                         In which case the weight of all n_edges i.e. between all nodes
                         that are not source or sink, are set to 0.
                         , or a function -
                         In which case it is used to compute the edges weights. The
                         supplied function has to have the following signature
                         fun(boundary_term_args), and is supposed to return
                         a dictionary with the graphs edges as keys and their n-weights
                         as values. These weights are tuples of numbers assigning the
                         weights in both directions of the edge. Additional parameters
                         can be passed via the boundary_term_args argument.
    @type boundary_term function
    @param regional_term_args Use this to pass some additional parameters to the
                              regional_term function.
    @param boundary_term_args Use this to pass some additional parameters to the
                              boundary_term function.
    
    @return the created graph
    @rtype graphcut.graph.Graph
    
    @raise AttributeError If an argument is maleformed.
    @raise FunctionError If one of the supplied functions returns unexpected results.
    """
    # prepare logger
    logger = Logger.getInstance()
    
    # prepare result graph
    print "Assuming {} nodes and {} edges for image of shape {}".format(fg_markers.size, __voxel_4conectedness(fg_markers.shape), fg_markers.shape) 
    graph = GCGraph(fg_markers.size, __voxel_4conectedness(fg_markers.shape))
    
    logger.info('Performing attribute tests...')
    
    # check, set and convert all supplied parameters
    fg_markers = scipy.asarray(fg_markers, dtype=scipy.bool_)
    bg_markers = scipy.asarray(bg_markers, dtype=scipy.bool_)
    
    # set dummy functions if not supplied
    if not regional_term: regional_term = __regional_term_voxel
    if not boundary_term: boundary_term = __boundary_term_voxel
    
    # check supplied functions and their signature
    if not hasattr(regional_term, '__call__') or not 1 == len(inspect.getargspec(regional_term)[0]):
        raise AttributeError('regional_term has to be a callable object which takes one parameter.')
    if not hasattr(boundary_term, '__call__') or not 2 == len(inspect.getargspec(boundary_term)[0]):
        raise AttributeError('boundary_term has to be a callable object which takes two parameters.')

    # collect all voxels i.e.
    # collect all nodes Vr of the graph
    #graph.set_nodes(fg_markers.size)
    
    logger.debug('#nodes={}, #hardwired-nodes source/sink={}/{}'.format(fg_markers.size,
                                                                        len(fg_markers.ravel().nonzero()[0]),
                                                                        len(bg_markers.ravel().nonzero()[0])))
    
    # compute the weights of all edges from the source and to the sink i.e.
    # compute the weights of the t_edges Wt
    logger.info('Computing terminal edge weights...')
    Wt = regional_term(regional_term_args)
    graph.set_tweights(Wt)

    # compute the weights of the edges between the neighbouring nodes i.e.
    # compute the weights of the n_edges Wr
    logger.info('Computing and adding inter-node edge weights...')
    boundary_term(graph, boundary_term_args)
    #graph.set_nweights(Wr)
    
    # collect all voxels that are under the foreground resp. background markers i.e.
    # collect all nodes that are connected to the source resp. sink
    logger.info('Setting terminal weights for the markers...')
    graph.set_source_nodes(fg_markers.ravel().nonzero()[0])
    graph.set_sink_nodes(bg_markers.ravel().nonzero()[0])    
    
    return graph.get_graph()

def graph_from_labels(label_image,
                      fg_markers,
                      bg_markers,
                      regional_term = False,
                      boundary_term = False,
                      regional_term_args = False,
                      boundary_term_args = False):
    """
    Create a graphcut.graph.Graph object from a nD label image.
    
    Every region of the label image is regarded as a node. They are connected to their
    immediate neighbours by arcs. If to regions are neighbours is determined using
    ndim*2-connectedness (e.g. 3*2=6 for 3D).
    In the next step the arcs weights (n-weights) are computed using the supplied
    boundary_term function.
    
    Implicitly the graph holds two additional nodes: the source and the sink, so called
    terminal nodes. These are connected with all other nodes through arcs of an initial
    weight (t-weight) of zero.
    All regions that are under the foreground markers are considered to be tightly bound
    to the source: The t-weight of the arc from source to these nodes is set to a maximum 
    value. The same goes for the background markers: The covered regions receive a
    maximum (graphcut.graph.Graph.MAX) t-weight for their arc towards the sink.
    
    @note If a region is marked as both, foreground and background, the background marker
    is given higher priority.
     
    @note all arcs whose weight is not explicitly set are assumed to carry a weight of
    zero.
    
    @param label_image The label image as an array containing uint values. Note that the
                       region labels have to start from 1 and be continuous (filter.label.relabel()).
    @type label_image numpy.ndarray 
    @param fg_markers The foreground markers as binary array of the same shape as the label image.
    @type fg_markers ndarray
    @param bg_markers The background markers as binary array of the same shape as the label image.
    @type bg_markers ndarray
    @param regional_term This can be either
                         False - all t-weights are set to 0, except for the nodes that are
                         directly connected to the source or sink.
                         , or a function - 
                         The supplied function is used to compute the t_edges. It has to
                         have the following signature
                         regional_term(label_image, regions, bounding_boxes, regional_term_args),
                         and is supposed to return a dictionary with region-ids as keys
                         and a tuple (source_t_weight, sink_t_weight) as values. The
                         returned dictionary does only need to contain entries for nodes
                         where one of the t-weights is not zero. Additional parameters
                         can be passed via the regional_term_args argument.
    @type regional_term function
    @param boundary_term This can be either
                         False - 
                         In which case the weight of all n_edges i.e. between all nodes
                         that are not source or sink, are set to 0.
                         , or a function -
                         In which case it is used to compute the edges weights. The
                         supplied function has to have the following signature
                         fun(label_image, boundary_term_args), and is supposed to return
                         a dictionary with the graphs edges as keys and their n-weights
                         as values. These weights are tuples of numbers assigning the
                         weights in both directions of the edge. Additional parameters
                         can be passed via the boundary_term_args argument.
    @type boundary_term function
    @param regional_term_args Use this to pass some additional parameters to the
                              regional_term function.
    @param boundary_term_args Use this to pass some additional parameters to the
                              boundary_term function.
    
    @return the created graph
    @rtype graphcut.graph.Graph
    
    @raise AttributeError If an argument is maleformed.
    @raise FunctionError If one of the supplied functions returns unexpected results.
    """
    # prepare logger
    logger = Logger.getInstance()
    
    # prepare result graph
    graph = Graph()
    
    logger.info('Performing attribute tests...')
    
    # check, set and convert all supplied parameters
    label_image = scipy.asarray(label_image)
    fg_markers = scipy.asarray(fg_markers, dtype=scipy.bool_)
    bg_markers = scipy.asarray(bg_markers, dtype=scipy.bool_)
    
    # check supplied labels image
    if not 1 == min(label_image.flat):
        raise AttributeError('The supplied label image does either not contain any regions or they are not labeled consecutively starting from 1.')
    
    # set dummy functions if not supplied
    if not regional_term: regional_term = __regional_term_label
    if not boundary_term: boundary_term = __boundary_term_label
    
    # check supplied functions and their signature
    if not hasattr(regional_term, '__call__') or not 4 == len(inspect.getargspec(regional_term)[0]):
        raise AttributeError('regional_term has to be a callable object which takes four parameters.')
    if not hasattr(boundary_term, '__call__') or not 2 == len(inspect.getargspec(boundary_term)[0]):
        raise AttributeError('bounda__voxel_4conectednessry_term has to be a callable object which takes two parameters.')

    logger.info('Collecting nodes...')

    # collect all labels i.e.
    # collect all nodes Vr of the graph
    graph.set_nodes(len(scipy.unique(label_image)))
    
    # collect all regions that are under the foreground resp. background markers i.e.
    # collect all nodes that are connected to the source resp. sink
    graph.set_source_nodes(scipy.unique(label_image[fg_markers]))
    graph.set_sink_nodes(scipy.unique(label_image[bg_markers]))
    
    logger.debug('#nodes={}, #hardwired-nodes source/sink={}/{}'.format(len(graph.get_nodes()),
                                                                        len(graph.get_source_nodes()),
                                                                        len(graph.get_sink_nodes())))
    
    logger.info('Extracting the regions bounding boxes...')
    
    # extract the bounding boxes
    bounding_boxes = find_objects(label_image)
        
    # compute the weights of all edges from the source and to the sink i.e.
    # compute the weights of the t_edges Wt
    logger.info('Computing terminal edge weights...')
    regions = set(graph.get_nodes()) - set(graph.get_source_nodes()) - set(graph.get_sink_nodes())
    Wt = regional_term(label_image, regions, bounding_boxes, regional_term_args) # bounding boxes indexed from 0
    graph.add_tweights(Wt)

    # compute the weights of the edges between the neighbouring nodes i.e.
    # compute the weights of the n_edges Wr
    logger.info('Computing inter-node edge weights...')
    Wr = boundary_term(label_image, boundary_term_args)
    graph.set_nweights(Wr)
    
    return graph

def __regional_term_voxel(regional_term_args):
    """Fake regional_term function with the appropriate signature."""
    return {}

def __regional_term_label(label_image, regions, bounding_boxes, regional_term_args):
    """Fake regional_term function with the appropriate signature."""
    return {}

def __boundary_term_voxel(boundary_term_args):
    """Fake regional_term function with the appropriate signature."""
    # supplying no boundary term contradicts the whole graph cut idea.
    return {}

def __boundary_term_label(label_image, boundary_term_args):
    """Fake regional_term function with the appropriate signature."""
    # supplying no boundary term contradicts the whole graph cut idea.
    return {}
    
def __voxel_4conectedness(shape):
    """
    Returns the number of edges for the supplied image shape assuming 4-connectedness.
    
    The name of the function has historical reasons. Essentially it returns the number
    of edges assuming 4-connectedness only for 2D. For 3D it assumes 6-connectedness,
    etc.
    
    @param shape the shape of the image
    @type shape sequence
    @return the number of edges
    @rtype int
    """
    shape = list(shape)
    while 1 in shape: shape.remove(1) # empty resp. 1-sized dimensions have to be removed (equal to scipy.squeeze on the array)
    return int(round(sum([(dim - 1)/float(dim) for dim in shape]) * scipy.prod(shape)))