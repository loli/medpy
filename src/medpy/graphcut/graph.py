"""
@package medpy.graphcut.graph
A basic graph class.

Classes:
    - class Graph: a class for holding graphs

@author Oskar Maier
@version d0.1.0
@since 2012-02-06
@status Development
"""

# build-in module

# third-party modules

# own modules


# code
class Graph(object):
    """
    Represents a graph suitable for further processing with the graphcut package.
    
    The graph contains nodes, edges (directed) between the nodes (n-edges), edges
    between two terminals (called source and sink) and the nodes (t-edges), and a
    weight for each edge. 
    
    @note the node-ids used by the graph are assumed to start with 1 and be
    continuous. This is not actually checked, except when calling the
    @link inconsistent() method, so be careful.
    
    Methods:
        - set_nodes(nodes) -- Set the nodes.
        - set_source_nodes(source_nodes) -- Set the source nodes.
        - set_sink_nodes(sink_nodes) -- Set the sink nodes.
        - set_nweights(nweights) -- Set the inter-node weights-
        - add_tweights(nweights) -- Add some terminal-to-node weights.
        - get_node_count() -- Return the number of nodes
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
    MAX = __UINT_16_BIT
    
    def __init__(self):
        self.__nodes = 0
        self.__snodes = []
        self.__tnodes = []
        self.__nweights = {}
        self.__tweights = {}
        
    def set_nodes(self, nodes):
        """
        Set the number of graph nodes (starting from node-id = 1),
        excluding sink and source.
        
        @param nodes number of nodes
        @type nodes int
        """
        self.__nodes = nodes
        
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
        Sets all n-weights.
        @param nweights a dictionary with (region-a-id, region-b-id) tuples as keys and
                         (weight-a-to-b, weight-b-to-a) as values.
        @type nweights dict
        """
        self.__nweights = nweights
            
    def add_tweights(self, tweights):
        """
        Adds t-weights to the current collection of t-weights, overwriting already
        existing ones.
        @note the weights for nodes directly connected to either the source or the sink
        are best set using @link set_source_nodes() or @link set_sink_nodes() to ensure
        consistency of their maximum values.
        
        @param tweights a dictionary with node_ids as keys and (weight-to-source, weight-to-sink) tuples as values.
        @type tweights dict
        """
        self.__tweights.update(tweights) 
        
    def get_node_count(self):
        """
        @return the numnber of nodes (excluding sink and source).
        @rtype int
        """
        return self.__nodes
        
    def get_nodes(self):
        """
        @return all nodes as an ordered list.
        @rtype list
        """
        return range(1, self.__nodes + 1)
    
    def get_source_nodes(self):
        """
        @return all nodes that are connected with the source as an unordered list (excluding sink and source).
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
        @return all n-weights (inter-node weights) as {edge-tuple: (weight, weight_reverersed)...} dict.
        @rtype dict
        """
        return self.__nweights
        
    def get_tweights(self):
        """
        @note returns only the t-weights that have been set so far. For nodes with unset
        t-weight, no entry is returned.
        @return all t-weights (terminal-node weights) as {node_id: (weight-source-node, weight-node-sink), ...} dict.
        @rtype dict
        """
        return self.__tweights
    
    def inconsistent(self):
        """
        Perform some consistency tests on the graph represented by this object.
        @note this check is very time intensive and should not be executed on huge
        graphs, except for debugging purposes.
        @return False if consistent, else a list of inconsistency messages.
        """
        messages = []
        for node in self.__tweights.iterkeys():
            if not node <= self.__nodes: messages.append("Node {} in t-weights but not in nodes.".format(node))
        for node in self.__snodes.iterkeys():
            if not node <= self.__nodes: messages.append("Node {} in s-nodes but not in nodes.".format(node))
        for node in self.__tnodes.iterkeys():
            if not node <= self.__nodes: messages.append("Node {} in t-nodes but not in nodes.".format(node))
        for e in self.__nweights.iterkeys():
            if not e[0] <= self.__nodes: messages.append("Node {} in edge {} but not in nodes.".format(e[0], e))
            if not e[1] <= self.__nodes: messages.append("Node {} in edge {} but not in nodes.".format(e[1], e))
            if (e[1], e[0]) in self.__nweights.iterkeys(): messages.append("The reversed edges of {} is also in the n-weights.".format(e))
                
            
        if 0 == len(messages): return False
        else: return messages