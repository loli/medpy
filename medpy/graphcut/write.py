"""
@package medpy.graphcut.write
Functions to persist a graph in various file formats.

Functions:
    - def bk_mfmc_parse(output): Parse the output of Boyov and Kolmogorovs max-flow/min-cut algorithm.

@author Oskar Maier
@version d0.1.0
@since 2012-02-06
@status Release
"""

# build-in module

# third-party modules

# own modules

# code
def graph_to_dimacs(g, f):
    """
    Persists the supplied graph in valid dimacs format into the file. 
    @param g A graph object to persist.
    @type g Graph
    @param f A file-like object.
    @type f file
    """
    # write comments
    f.write('c Created by medpy\n')
    f.write('c Oskar Maier, oskar.maier@googlemail.com\n')
    f.write('c\n')
    
    # write problem
    f.write('c problem line\n')
    f.write('p max {} {}\n'.format(g.get_node_count() + 2, len(g.get_edges()))) # +2 as terminal nodes also count in dimacs format # no-nodes / no-edges
    
    # denote source and sink
    f.write('c source descriptor\n')
    f.write('n 1 s\n')
    f.write('c sink descriptor\n')
    f.write('n 2 t\n')
    
    # write terminal arcs (t-weights)
    f.write('c terminal arcs (t-weights)\n')
    for node, weight in g.get_tweights().iteritems():
        # Note: the nodes ids of the graph start from 1, but 1 and 2 are reserved for source and sink respectively, therefore add 2
        if not 0 == weight[0]: # 0 weights are implicit
            f.write('a 1 {} {}\n'.format(node + 2, weight[0]))
        if not 0 == weight[1]: # 0 weights are implicit
            f.write('a {} 2 {}\n'.format(node + 2, weight[1]))
    
    # write inter-node arcs (n-weights)
    f.write('c inter-node arcs (n-weights)\n')
    for edge, weight in g.get_nweights().iteritems():
        if not 0 == weight[0]: # 0 weights are implicit
            f.write('a {} {} {}\n'.format(edge[0] + 2, edge[1] + 2, weight[0]))
        # reversed weights have to follow directly in the next line
        if not 0 == weight[1]: # 0 weights are implicit
            f.write('a {} {} {}\n'.format(edge[1] + 2, edge[0] + 2, weight[1]))
            
    # end comment
    f.write('c end-of-file')
    