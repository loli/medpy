"""
@package medpy.graphcut.graph
Create and modify graphs from nD label-images to be used in graph-cut algorithms.

Classes:
    - class Graph: a class for holding graphs

Functions:
    - def graph_from_labels(label_image,
                            fg_markers,
                            bg_markers,
                            regional_term = False,
                            boundary_term = False,
                            directed = False,
                            extract_marker_features = False,
                            regional_term_args = False,
                            boundary_term_args = False,
                            extract_marker_features_args = False): Creates a Graph object from a nD label image
    - def relabel(label_image, start = 1): relabels a label image to be consecutive

@author Oskar Maier
@version d0.1.0
@since 2012-01-18
@status Development
"""

# build-in module
import inspect

# third-party modules
import scipy
from scipy.ndimage.measurements import find_objects

# own modules
from ..core import Logger
from ..core import FunctionError
from medpy.graphcut.energy import boundary_stawiaski2


# code
class Graph(object):
    """
    Represents a graph suitable for further processing with the graphcut package.
    
    The graph contains nodes, edges (directed) between the nodes (n-edges), edges
    between two terminals (called source and sink) and the edges (t-edges) and a
    weight for each edge. 
    
    Methods:
        - set_nodes(nodes) -- Set the nodes.
        - set_source_nodes(source_nodes) -- Set the source nodes.
        - set_sink_nodes(sink_nodes) -- Set the sink nodes.
        - set_nweights(nweights) -- Set the inter-node weights-
        - add_tweights(nweights) -- Add some terminal-to-node weights.
        - get_nodes() -- Return all nodes.
        - get_source_nodes() -- Return all nodes connected to the source.
        - get_sink_nodes() -- Return all nodes connected to the sink.
        - get_edges() -- Return all edges.
        - get_nweights() -- Return all inter-node weights.
        - get_tweights() -- Return all terminal-node weights.
        - get_tweights2() -- Unsave version of get_tweights()
        - inconsistent() -- Whether the contained graph is consistent or not.
    """
    
    # @var __INT_16_BIT The maximum value of signed int 16bit.
    __INT_16_BIT = 32767
    # @var __UINT_16_BIT: The maximum value of unsigned int 16bit.
    __UINT_16_BIT = 65535
    # @var MAX The maximum value a weight can take.
    MAX = __UINT_16_BIT ### 
    
    def __init__(self):
        self.__nodes = []
        self.__snodes = []
        self.__tnodes = []
        self.__nweights = {}
        self.__tweights = {}
        
    def set_nodes(self, nodes):
        """
        Set the graphs nodes.
        
        @param nodes a sequence of integers
        @type nodes sequence
        """
        self.__nodes = list(nodes)
        
    def set_source_nodes(self, source_nodes):
        """
        Set the source nodes and compute their t-weights.
        
        @warning It does not get checked if one of the supplied source-nodes already has
        a weight assigned (e.g. by passing it to @link set_sink_nodes()). This can
        occur when the foreground- and background-markers cover the same region. In this
        case the order of setting the terminal nodes can affect the graph and therefore
        the graph-cut result.
        
        @param source_nodes a sequence of integers
        @type source_nodes sequence
        """
        self.__snodes = list(source_nodes)
        
        # set the source-to-node weights (t-weights)
        for snode in self.__snodes:
            self.__tweights[snode] = (self.MAX, 0) # (weight-to-source, weight-to-sink)
            
    def set_sink_nodes(self, sink_nodes):
        """
        Set the sink nodes and compute their t-weights.
        
        @warning It does not get checked if one of the supplied sink-nodes already has
        a weight assigned (e.g. by passing it to @link set_source_nodes()). This can
        occur when the foreground- and background-markers cover the same region. In this
        case the order of setting the terminal nodes can affect the graph and therefore
        the graph-cut result.
        
        @param sink_nodes a sequence of integers
        @type sink_nodes sequence
        """
        self.__tnodes = list(sink_nodes)
        
        # set the source-to-node weights (t-weights)
        for tnode in self.__tnodes:
            self.__tweights[tnode] = (0, self.MAX) # (weight-to-source, weight-to-sink)
            
    def set_nweights(self, nweights):
        """
        Sets all nweights.
        @param nweights a dictionary with (region-a-id, region-b-id) tuples as keys and
                         (weight-a-to-b, weight-b-to-a) as values.
        @type nweights dict
        """
        self.__nweights = nweights
            
    def add_tweights(self, tweights):
        """
        Adds tweights to the current collection of tweights, overwriting already existing ones.
        
        @param tweights a dictionary with node_ids as keys and (weight-to-soource, weight-to-sink) tuples as values.
        @type tweights dict
        """
        self.__tweights.update(tweights) 
        
    def get_nodes(self):
        """
        @return all nodes as an unordered list.
        @rtype list
        """
        return self.__nodes
    
    def get_source_nodes(self):
        """
        @return all nodes that are connected with the source as an unordered list.
        @rtype list
        """
        return self.__snodes
    
    def get_sink_nodes(self):
        """
        @return all nodes that are connected with the source as an unordered list.
        @rtype list
        """
        return self.__tnodes
    
    def get_edges(self):
        """
        @return all edges as ordered list of tuples (i.e. [(node_id1, node_id2), (..), ...].
        @rtype list
        """
        return self.__nweights.keys()
        
    def get_nweights(self):
        """
        @return all n-weights (inter-node weights) as {edge-tuple: weight, ...} dict.
        @rtype dict
        """
        return self.__nweights
        
    def get_tweights(self):
        """
        @return all t-weights (terminal-node weights) as {node_id: weight, ...} dict.
        @rtype dict
        """
        # prepare __tweights that are not set yet
        for node in self.__nodes:
            if not node in self.__tweights:
                self.__tweights[node] = (0, 0) # (weight-to-source, weight-to-sink)

        return self.__tweights
    
    def get_tweights2(self):
        """
        Version of @link get_tweights() that does not check if all tweights has
        been set and is therefore slightly faster. Use with caution!
        @return all t-weights (terminal-node weights) as {node_id: weight, ...} dict.
        @rtype dict
        """
        return self.__tweights
    
    def inconsistent(self):
        """
        Perform some consistency tests on the graph represented by this object.
        @note this check is very time intenisve and should not be executed on huge
        graphs.
        @return False if consistent, else a list of inconsistency messages.
        """
        #!TODO: Imprive the execution time of this step
        self.get_tweights() # to trigger computation of remaining tweights
        
        messages = []
        for node in self.__nodes:
            if not node in self.__tweights: messages.append("Node {} not in tweights.".format(node))
        for node in self.__tweights:
            if not node in self.__nodes: messages.append("Node {} in tweights but not in nodes.".format(node))
        for node in self.__snodes:
            if not node in self.__nodes: messages.append("Node {} in snodes but not in nodes.".format(node))
        for node in self.__tnodes:
            if not node in self.__nodes: messages.append("Node {} in tnodes but not in nodes.".format(node))
        for e in self.__nweights:
            if not e[0] in self.__nodes: messages.append("Node {} in edge {} but not in nodes.".format(e[0], e))
            if not e[1] in self.__nodes: messages.append("Node {} in edge {} but not in nodes.".format(e[1], e))
            
        if 0 == len(messages): return False
        else: return messages


def graph_from_labels(label_image,
                      fg_markers,
                      bg_markers,
                      regional_term = False,
                      boundary_term = False,
                      directed = False,
                      extract_marker_features = False,
                      regional_term_args = False,
                      boundary_term_args = False,
                      extract_marker_features_args = False):
    """
    Create a @link Graph object from a nD label image.
    
    The graph created consists of nodes, edges and weights (two type: n-weight, which are
    inter-node weights, and t-weights, which are terminat-to-node weights).
    
    For every region in the supplied label image a node is generated with the region-id
    as node-id. Using ndim*2-connectedness (e.g. 3*2=6 for 3D) the neighbours of each region
    are determined and a edge created for each such pair of neighbours. The provides 
    boundary_term function is used to compute the weights for all inter-node (i.e. inter
    region) weights (n-weights). For the terminal-to-node weights (t-weights) two
    approaches are taken: all regions that are touched by the supplied foreground mask
    (fg_markers) the weight from the source is set to a maximum (@link Graph.MAX) and
    the weight to the sink to 0. For the background mask (bg_markers) vice-versa. All
    nodes that are not contained in these receive a weight calculated with the provided
    regional_term function.
    
    @param label_image The label image as an array containing uint values. @note: The
                        region labels have to start from 1 and be continuous
                        (@link relabel()).
    @type label_image numpy.ndarray 
    @param fg_markers The foreground markers as binary array.
    @type fg_markers ndarray
    @param bg_markers The background markers as binary array.
    @type bg_markers ndarray
    @param regional_term This can be either
                         False - all t-weights are set to 0, except for the nodes that are
                         directly connected to the source or sink.
                         , or a function - 
                         The supplied function is used to compute the t_edges. It has to
                         have the following signature
                         source_weight, sink_weight = fun(label_image, region_bb, region_id, fg_featurs, bg_features, regional_term_args),
                         where source_weight is the weight from the source to the node
                         of the supplied region; sink_weight the weight from the node to
                         the sink; fg_features the output of the extract_marker_features
                         function over the foreground regions if supplied, otherwise
                         False; bg_features the same for the background regions; region_bb
                         the bounding box of the current region as a list of slice-objects;
                         region_id the id og the regions; label_image the label image; and
                         regional_term_args eventual additional parameters passed via the
                         regional_term_args argument.
    @type regional_term function
    @param boundary_term This can be either
                         False - 
                         In which case the weight of all n_edges i.e. between all nodes
                         that are not source or sink, are set to 0.
                         , or a function -
                         In which case it is used to compute the edges weights. The
                         supplied function has to have the following signature
                         weight = fun(label_image, r1_bb, r2_bb, r1_id, r2_id, boundary_term_args),
                         where r1_bb and r2_bb are the bounding boxes around the regions
                         defined by a list of slice-objects, r1_id and r2_id the
                         respective regions ids and boundary_term_args eventual additional
                         parameters passed via the boundary_term_args argument.
                         It is called for any two neighbouring regions. If the directed
                         parameter is set to True, it is also called for the computation
                         of the reversed weight.
    @type boundary_term function
    @param directed Set this to True, if the n_edges should be directed i.e. have
                    different weights for both directions.
    @type directed bool
    @param extract_marker_features A function that has to follow the signature
                                   features = fun(label_image, bbs_of_marked_regions, is_foreground, extract_marker_features_args)
                                   and is called once with all regions that are marked
                                   by the foreground markers and once with all regions
                                   that are marked as background. The return values are
                                   passed to the regional_term function.
    @type extract_marker_features function
    @param regional_term_args Use this to pass some additional parameters to the
                              regional_term function.
    @param boundary_term_args Use this to pass some additional parameters to the
                              boundary_term function.
    @param extract_marker_features_args Use this to pass some additional parameters to
                                        the extract_marker_features function.
    
    @return the created graph
    @rtype graph.Graph
    
    @raise AttributeError If an argument is maleformed.
    @raise FunctionError If one of the supplied functions returns unexpected results.
    """
    # prepare logger
    logger = Logger.getInstance()
    
    # prepare result graph
    graph = Graph()
    
    logger.info('Performing attribute tests...')
    
    # check, set and convert all supplied parameters
    label_image = scipy.asarray(label_image) #!TODO: uint as dtype might here be better -> how to detmerine the range that is needed?
    fg_markers = scipy.asarray(fg_markers, dtype=scipy.bool_)
    bg_markers = scipy.asarray(bg_markers, dtype=scipy.bool_)
    
    # check supplied labels image
    if not 1 == min(label_image.flat):
        raise AttributeError('The supplied label image does either not contain any regions or they are not labeled consecutively starting from 1.')
    
    # set dummy functions if not supplied
    if not regional_term: regional_term = __regional_term
    if not boundary_term: boundary_term = __boundary_term
    
    # check supplied functions and their signature
    if not hasattr(regional_term, '__call__') or not 6 <= len(inspect.getargspec(regional_term)[0]):
        raise AttributeError('regional_term has to be a callable object which takes six or more parameters.')
    if not hasattr(boundary_term, '__call__') or not 6 <= len(inspect.getargspec(boundary_term)[0]):
        raise AttributeError('boundary_term has to be a callable object which takes six or more parameters.')
    if extract_marker_features:
        if not hasattr(extract_marker_features, '__call__') or not 4 <= len(inspect.getargspec(extract_marker_features)[0]):
            raise AttributeError('extract_marker_features has to be a callable object which takes four or more parameters.')

    logger.info('Collecting nodes...')

    # collect all labels i.e.
    # collect all nodes Vr of the graph
    graph.set_nodes(scipy.unique(label_image))
    
    # collect all regions that are under the foreground resp. background markers i.e.
    # collect all nodes that are connected to the source resp. sink
    graph.set_source_nodes(scipy.unique(label_image[fg_markers]))
    graph.set_sink_nodes(scipy.unique(label_image[bg_markers]))
    
    logger.debug('#nodes={}, #hardwired-nodes source/sink={}/{}'.format(len(graph.get_nodes()),
                                                                        len(graph.get_source_nodes()),
                                                                        len(graph.get_sink_nodes())))
    
    logger.info('Computing edges...')
    
    # determine for each region the neighbouring regions i.e.
    # determine for each node the neighbouring nodes i.e.
    # determine and collect all edges Er of the graph
    Er = __compute_edges(label_image)
    logger.debug('...{} edges found.'.format(len(Er)))
    
    logger.info('Extracting the regions bounding boxes...')
    
    # extract the bounding boxes
    bounding_boxes = find_objects(label_image)
    
    # extract features from the foreground and background regions, if requested
    if extract_marker_features:
        logger.info('Extracting terminal features...')
        
        fg_regions = []
        for r in graph.get_source_nodes():
            fg_regions.append(bounding_boxes[r - 1]) # bounding boxes indexed from 0
        fg_features = extract_marker_features(label_image, fg_regions, True, extract_marker_features_args)
        
        bg_regions = []
        for r in graph.get_sink_nodes():
            bg_regions.append(bounding_boxes[r - 1]) # bounding boxes indexed from 0
        bg_features = extract_marker_features(label_image, bg_regions, False, extract_marker_features_args)
    else:
        fg_features = False
        bg_features = False
        
    # compute the weights of all edges from the source and to the sink i.e.
    # compute the weights of the t_edges Wt
    logger.info('Computing terminal edge weights...')
    Wt = {}
    for r in set(graph.get_nodes()) - set(graph.get_source_nodes()) - set(graph.get_sink_nodes()):
        Wt[r] = regional_term(label_image,
                              bounding_boxes[r - 1], # bounding boxes indexed from 0
                              r,
                              fg_features,
                              bg_features,
                              regional_term_args)
    graph.add_tweights(Wt)
        
    
    # compute the weights of the edges between the neighbouring nodes i.e.
    # compute the weights of the n_edges Wr
    logger.info('Computing inter-node edge weights...')
    
    Wr = boundary_stawiaski2(label_image, boundary_term_args)
    
#    # iterate over edges and execute boundary_term for all to compute the weights
#    Wr = {}
#    for e in Er:
#        Wr[e] = boundary_term(label_image,
#                              bounding_boxes[e[0] - 1], # bounding boxes indexed from 0
#                              bounding_boxes[e[1] - 1],
#                              e[0],
#                              e[1],
#                              boundary_term_args)
#        if Wr[e] <= 0:
#            raise FunctionError("The boundary_term function has to be strictly positive, but returned for the edge {} a value of {}.".format(e, Wr[e]))
#        if directed:
#            Wr[(e[1], e[0])] = boundary_term(label_image,
#                                             bounding_boxes[e[0] - 1], # bounding boxes indexed from 0
#                                             bounding_boxes[e[1] - 1],
#                                             e[0],
#                                             e[1],
#                                             boundary_term_args)
#            if Wr[(e[1], e[0])] <= 0:
#                raise FunctionError("The boundary_term function has to be strictly positive, but returned for the edge {} a value of {}.".format((e[1], e[0]), Wr[(e[1], e[0])]))
#    
    print "adding weights"
    graph.set_nweights(Wr)
    

    return graph

def __regional_term(d1, d2, d3, d4, d5, d6):
    """Fake regional_term function with the appropriate signature."""
    return (0, 0)

def __boundary_term(d1, d2, d3, d4, d5, d6):
    """Fake regional_term function with the appropriate signature."""
    # TODO: A >0 value is required to make the boundary_term function strictly positive
    # But how to make this most elegant? And ensure that it survives the conversion to C++?
    return scipy.finfo(float).tiny
    

def __compute_edges(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    Note The returned set contains neither duplicates, nor self-references
    (i.e. (id_1, id_1)), nor reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    
    @param label_image An image with labeled regions (nD).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    # compute the neighbours
    Er = __compute_edges_nd(label_image)
    
    # remove reversed neighbours and self-references
    for edge in list(Er):
        if (edge[1], edge[0]) in Er:
            Er.remove(edge)
    return Er
    
    
def __compute_edges_nd(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    @see __compute_edges_nd2 alternative implementation (slighty slower)
    @see __compute_edges_3d faster implementation for three dimensions only
    
    @param label_image An image with labeled regions (nD).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    Er = set()
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        Er = Er.union(set(zip(label_image[slices_x].flat,
                              label_image[slices_y].flat)))
    return Er

def __compute_edges_nd2(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    @see __compute_edges_nd alternative implementation (slightly faster)
    @see __compute_edges_3d faster implementation for three dimensions only
    
    @param label_image An image with labeled regions (nD).
    @param return A set with tuples denoting the edge neighbourhood.
    """    
    # prepare iterators
    labels = label_image.flat
    nb_pointers = []
    for dim in range(label_image.ndim):
        slices_base = []
        slices_add = []
        for di in range(label_image.ndim):
            slices_base.append(slice(1 if di == dim else None, None))
            slices_add.append(slice(-1 if di == dim else None, None))
        nb_pointers.append(scipy.concatenate((label_image[slices_base],
                                              label_image[slices_add]), dim).flat)
    
    # iterate and search neighbours
    Er = set()
    for label, nbs in zip(labels, zip(*nb_pointers)):
        for nb in nbs: Er.add((label, nb))
    return Er
    

def __compute_edges3d_1d(label_image):
    """
    Used by @link __compute_edges_3d.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    
    @param label_image An image with labeled regions (1D).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    Er = set()
    for l in zip(label_image[:-1],
                 label_image[1:]): #label/next element
                Er.add((l[0], l[1]))
    return Er

def __compute_edges3d_2d(label_image):
    """
    Used by @link __compute_edges_3d.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    Note that this function leaves out the maximal x,y columns, which have to be
    separately processed with the 1D version.
    
    @param label_image An image with labeled regions (2D).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    Er = set()
    for x in range(0, label_image.shape[0] - 1):
            for l in zip(label_image[x,:-1],
                         label_image[x+1,:-1],
                         label_image[x,1:]): #label/right/bottom (tetris triangle shape)
                for n in l[1:]: Er.add((l[0], n))
    return Er

def __compute_edges3d_3d(label_image):
    """
    Used by @link __compute_edges_3d.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    Note that this function leaves out the maximal x,y and z planes, which have to be
    separately processed with the 2D version.
    
    @param label_image An image with labeled regions (3D).
    @param return A set with tuples denoting the edge neighbourhood.
    """ 
    Er = set()
    for x in range(0, label_image.shape[0] - 1):
        for y in range(0, label_image.shape[1] - 1):
            for l in zip(label_image[x,y,:-1],
                         label_image[x+1,y,:-1],
                         label_image[x,y+1,:-1],
                         label_image[x,y,1:]): #label/right/bottom/deep of a half star-volume
                for n in l[1:]: Er.add((l[0], n))
    return Er

def __compute_edges_3d(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    @see __compute_edges_nd for n-dimensional input arrays
    @see __compute_edges_nd2 for n-dimnsional input arrays (alternative implementation)
    
    @param label_image An image with labeled regions.
    @param return A set with tuples denoting the edge neighbourhood.
    """        
    # compute edges for all except the far planes of all three dimensions
    Er = __compute_edges3d_3d(label_image)
    # compute edges for all except the far columns of each plane
    Er = Er.union(__compute_edges3d_2d(label_image[-1]))
    Er = Er.union(__compute_edges3d_2d(label_image[:,-1]))
    Er = Er.union(__compute_edges3d_2d(label_image[:,:,-1]))
    # compute edges for the far columns
    Er = Er.union(__compute_edges3d_1d(label_image[-1,-1]))
    Er = Er.union(__compute_edges3d_1d(label_image[-1,:,-1]))
    Er = Er.union(__compute_edges3d_1d(label_image[:,-1,-1]))
    
    return Er

def relabel(label_image, start = 1):
    """ 
    Relabel the regions of a label image.
    Re-processes the labels to make them consecutively and starting from start.
    
    @param label_image a label image
    @type label_image sequence
    @param start the id of the first label to assign
    @type start int
    @return The relabeled image.
    @rtype numpy.ndarray
    """
    label_image = scipy.asarray(label_image)
    mapping = {}
    rav = label_image.ravel()
    for i in range(len(rav)):
        if not rav[i] in mapping:
            mapping[rav[i]] = start
            start += 1
        rav[i] = mapping[rav[i]]
    return rav.reshape(label_image.shape)
