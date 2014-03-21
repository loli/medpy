"""
@package medpy.graphcut.graph
Basic graph classes.

Classes:
    - class Graph: a class representing a graph; flexible Python implementation
    - class GCGraph: a class representing a graph; directly based on the graph cut C++
                     implementation graph maxflow.GraphDouble
    
@author Oskar Maier
@version r0.1.2
@since 2012-02-06
@status Release
"""

# build-in module

# third-party modules

# own modules
from maxflow import GraphDouble, GraphFloat

# code
class Graph(object):
    """
    Represents a graph suitable for further processing with the graphcut package.
    
    The graph contains nodes, edges (directed) between the nodes (n-edges), edges
    between two terminals (called source and sink) and the nodes (t-edges), and a
    weight for each edge. 
    
    @note the node-ids used by the graph are assumed to start with 1 and be
    continuous. This is not actually checked, except when calling the
    inconsistent() method, so be careful.
    
    Methods:
        - set_nodes() -- Set the nodes.
        - set_source_nodes() -- Set the source nodes.
        - set_sink_nodes() -- Set the sink nodes.
        - set_nweights() -- Set the inter-node weights.
        - add_tweights() -- Add some terminal-to-node weights.
        - get_node_count() -- Return the number of nodes
        - get_nodes() -- Return all nodes.
        - get_source_nodes() -- Return all nodes connected to the source.
        - get_sink_nodes() -- Return all nodes connected to the sink.
        - get_edges() -- Return all edges.
        - get_nweights() -- Return all inter-node weights.
        - get_tweights() -- Return all terminal-node weights.
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
        self.__nodes = int(nodes)
        
    def set_source_nodes(self, source_nodes):
        """
        Set the source nodes and compute their t-weights.
        
        @warning It does not get checked if one of the supplied source-nodes already has
        a weight assigned (e.g. by passing it to set_sink_nodes()). This can
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
        a weight assigned (e.g. by passing it to set_source_nodes()). This can
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
        @param nweights a dictionary with (node-id, node-id) tuples as keys and
                         (weight-a-to-b, weight-b-to-a) as values.
        @type nweights dict
        """
        self.__nweights = nweights
            
    def add_tweights(self, tweights):
        """
        Adds t-weights to the current collection of t-weights, overwriting already
        existing ones.
        @note the weights for nodes directly connected to either the source or the sink
        are best set using set_source_nodes() or set_sink_nodes() to ensure
        consistency of their maximum values.
        
        @param tweights a dictionary with node_ids as keys and (weight-to-source, weight-to-sink) tuples as values.
        @type tweights dict
        """
        self.__tweights.update(tweights)    
        
    def get_node_count(self):
        """
        @return the number of nodes (excluding sink and source).
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
        for node in self.__snodes:
            if not node <= self.__nodes: messages.append("Node {} in s-nodes but not in nodes.".format(node))
        for node in self.__tnodes:
            if not node <= self.__nodes: messages.append("Node {} in t-nodes but not in nodes.".format(node))
        for e in self.__nweights.iterkeys():
            if not e[0] <= self.__nodes: messages.append("Node {} in edge {} but not in nodes.".format(e[0], e))
            if not e[1] <= self.__nodes: messages.append("Node {} in edge {} but not in nodes.".format(e[1], e))
            if (e[1], e[0]) in self.__nweights.iterkeys(): messages.append("The reversed edges of {} is also in the n-weights.".format(e))
                
            
        if 0 == len(messages): return False
        else: return messages
        
class GCGraph:
    """
    A graph representation that works directly with the maxflow.GraphDouble graph as
    base. It is therefore less flexible as graph.Graph, but leads to lower memory
    requirements.
    
    The graph contains nodes, edges (directed) between the nodes (n-edges), edges
    between two terminals (called source and sink) and the nodes (t-edges), and a
    weight for each edge. 
    
    @note the node-ids used by the graph are assumed to start with 0 and be
    continuous. This is not actually checked, so be careful.
    
    @note This wrapper tries to catch the most usual exception that can occur in the
    underlying C++ implementation and to convert them into catchable and meaningful
    error messages.
    
    Methods:
        - set_source_nodes() -- Set multiple source nodes.
        - set_sink_nodes() -- Set multiple sink nodes.
        - set_nweight() -- Set a single n-weight / edge-weight.
        - set_nweights() -- Set multiple inter-node weights.
        - set_tweight() -- Set a single t-weight / terminal-weight.
        - set_tweights() -- Set multiple terminal-to-node weights.
        - get_graph() -- Return the C++ graph.
        - get_nodes() -- Return all nodes.
        - get_node_count() -- Return the number of nodes.
        - get_edge_count() -- Return the number of edges.
    """
    # @var __INT_16_BIT The maximum value of signed int 16bit.
    __INT_16_BIT = 32767
    # @var __UINT_16_BIT: The maximum value of unsigned int 16bit.
    __UINT_16_BIT = 65535
    # @var MAX The maximum value a terminal weight can take.
    MAX = __UINT_16_BIT
    
    def __init__(self, nodes, edges):
        """
        @param nodes the number of nodes in the graph
        @type nodes int
        @param edges the number of edges in the graph
        @type edges int
        """
        self.__graph = GraphDouble(nodes, edges)
        self.__graph.add_node(nodes)
        self.__nodes = nodes
        self.__edges = edges
        
    def set_source_nodes(self, source_nodes):
        """
        Set multiple source nodes and compute their t-weights.
        
        @warning It does not get checked if one of the supplied source-nodes already has
        a weight assigned (e.g. by passing it to set_sink_nodes()). This can
        occur when the foreground- and background-markers cover the same region. In this
        case the order of setting the terminal nodes can affect the graph and therefore
        the graph-cut result.
        
        @param source_nodes a sequence of integers
        @type source_nodes sequence
        
        @raise ValueError if a passed node id does not refer to any node of the graph
                          (i.e. it is either higher than the initially set number of
                          nodes or lower than zero).
        """
        if max(source_nodes) >= self.__nodes or min(source_nodes) < 0:
            raise ValueError('Invalid node id of {} or {}. Valid values are 0 to {}.'.format(max(source_nodes), min(source_nodes), self.__nodes - 1))
        # set the source-to-node weights (t-weights)
        for snode in source_nodes:
            self.__graph.add_tweights(int(snode), self.MAX, 0) # (weight-to-source, weight-to-sink)
            
    def set_sink_nodes(self, sink_nodes):
        """
        Set multiple sink nodes and compute their t-weights.
        
        @warning It does not get checked if one of the supplied sink-nodes already has
        a weight assigned (e.g. by passing it to set_source_nodes()). This can
        occur when the foreground- and background-markers cover the same region. In this
        case the order of setting the terminal nodes can affect the graph and therefore
        the graph-cut result.
        
        @param sink_nodes a sequence of integers
        @type sink_nodes sequence
        
        @raise ValueError if a passed node id does not refer to any node of the graph
                          (i.e. it is either higher than the initially set number of
                          nodes or lower than zero).
        """
        if max(sink_nodes) >= self.__nodes or min(sink_nodes) < 0:
            raise ValueError('Invalid node id of {} or {}. Valid values are 0 to {}.'.format(max(sink_nodes), min(sink_nodes), self.__nodes - 1))
        # set the node-to-sink weights (t-weights)
        for snode in sink_nodes:
            self.__graph.add_tweights(int(snode), 0, self.MAX) # (weight-to-source, weight-to-sink)
            
    def set_nweight(self, node_from, node_to, weight_there, weight_back):
        """
        Set a single n-weight / edge-weight.
        @param node_from node-id from the first node of the edge
        @param node_to node-id from the second node of the edge
        @param weight_there weight from first to second node (>0) 
        @param weight_back weight from second to first node (>0)
        
        @note The object does not check if the number of supplied edges in total exceeds
              the number passed to the init-method. If this is the case, the underlying
              C++ implementation will double the memory, which is very unefficient.
               
        @note The underlying C++ implementation allows zero weights, but these are highly
              undesirable for inter-node weights and therefore raise an error.
              
        @raise ValueError if a passed node id does not refer to any node of the graph
                          (i.e. it is either higher than the initially set number of
                          nodes or lower than zero).
        @raise ValueError if the two node-ids of the edge are the same (graph cut does
                          not allow self-edges).
        @raise ValueError if one of the passed weights is <= 0.
        """
        if node_from >= self.__nodes or node_from < 0:
            raise ValueError('Invalid node id (node_from) of {}. Valid values are 0 to {}.'.format(node_from, self.__nodes - 1))
        elif node_to >= self.__nodes or node_to < 0:
            raise ValueError('Invalid node id (node_to) of {}. Valid values are 0 to {}.'.format(node_to, self.__nodes - 1))
        elif node_from == node_to:
            raise ValueError('The node_from ({}) can not be equal to the node_to ({}) (self-connections are forbidden in graph cuts).'.format(node_from, node_to))
        elif weight_there <= 0 or weight_back <= 0:
            raise ValueError('Negative or zero weights are not allowed.')
        self.__graph.sum_edge(int(node_from), int(node_to), float(weight_there), float(weight_back))
            
    def set_nweights(self, nweights):
        """
        Set multiple n-weights / edge-weights.
        @param nweights a dictionary with (node-id, node-id) tuples as keys and
                        (weight-a-to-b, weight-b-to-a) as values.
        @type nweights dict
        
        @note The object does not check if the number of supplied edges in total exceeds
              the number passed to the init-method. If this is the case, the underlying
              C++ implementation will double the memory, which is very inefficient.
              
        @note see set_nweight() for raised errors.
        """
        for edge, weight in nweights.iteritems():
            self.set_nweight(edge[0], edge[1], weight[0], weight[1])
            
    def set_tweight(self, node, weight_source, weight_sink):
        """
        Set a single n-weight / edge-weight.
        @param node the node which t-weights to set
        @param weight_source weight from the source to the node
        @param weight_sink weight from the node to the sink
        
        @note The object does not check if the number of supplied edges in total exceeds
              the number passed to the init-method. If this is the case, the underlying
              C++ implementation will double the memory, which is very inefficient.
              
        @note Terminal weights can be zero or negative.
              
        @raise ValueError if a passed node id does not refer to any node of the graph
                          (i.e. it is either higher than the initially set number of
                          nodes or lower than zero).
        """
        if node >= self.__nodes or node < 0:
            raise ValueError('Invalid node id of {}. Valid values are 0 to {}.'.format(node, self.__nodes - 1))
        self.__graph.add_tweights(int(node), float(weight_source), float(weight_sink)) # (weight-to-source, weight-to-sink)
            
    def set_tweights(self, tweights):
        """
        Set multiple t-weights to the current collection of t-weights, overwriting
        already existing ones.
        
        @warning since this method overrides already existing t-weights, it is strongly
        recommended to run set_source_nodes() and set_sink_nodes() after the
        last call to this method.
        
        @note the weights for nodes directly connected to either the source or the sink
        are best set using set_source_nodes() or set_sink_nodes() to ensure
        consistency of their maximum values.
        
        @param tweights a dictionary with node_ids as keys and (weight-to-source, weight-to-sink) tuples as values.
        @type tweights dict
        
        @raise ValueError if a passed node id does not refer to any node of the graph
                          (i.e. it is either higher than the initially set number of
                          nodes or lower than zero).
        """        
        for node, weight in tweights.iteritems():
            self.set_tweight(node, weight[0], weight[1]) # (weight-to-source, weight-to-sink)
            
    def set_tweights_all(self, tweights):
        """
        Set all t-weights at once.
        
        @warning since this method overrides already existing t-weights, it is strongly
        recommended to run set_source_nodes() and set_sink_nodes() after the
        last call to this method.
        
        @note the weights for nodes directly connected to either the source or the sink
        are best set using set_source_nodes() or set_sink_nodes() to ensure
        consistency of their maximum values.
        
        @param tweights an iterable, e.g. a list or an array, containing a pair of
                        numeric values for each of the graphs nodes 
        @type tweights iterable
        """
        for node, (twsource, twsink) in enumerate(tweights):
            self.set_tweight(node, twsource, twsink) # source = FG, sink = BG
        
    def get_graph(self):
        """
        @return the underlying maxflow.GraphDouble C++ implementation of the graph.
        @rtype maxflow.GraphDouble
        """
        return self.__graph
        
    def get_node_count(self):
        """
        @return the number of nodes (excluding sink and source).
        @rtype int
        """
        return self.__nodes
        
    def get_nodes(self):
        """
        @return all nodes as an ordered list (starting from 0).
        @rtype list
        """
        return range(0, self.__nodes)
    
    def get_edge_count(self):
        """
        @return the number of edges
        @rtype int
        """
        return self.__edges
