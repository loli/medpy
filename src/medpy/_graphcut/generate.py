"""
@package medpy.graphcut.generate
Generates output files from graphs that are processable by graph-cut algorithms.

All functions in this module are highly depend on the actual implementation of the
graph-cut algorithm they are intended to be used for. They require a minimal version
number and it can not be ensured, that they will work with other versions.

See the package description for a list of the supported graph-cut implementations.

Functions:
    - def bk_mfmc_generate(graph): Generate a C++ file for Boyov and Kolmogorovs
                                   max-flow/min-cut algorithm.

@author Oskar Maier
@version d0.1.0
@since 2012-01-18
@status Development
"""

# build-in modules
import os.path

# third-party modules

# own modules
import medpy
from ..core.Logger import Logger
from ..core.exceptions import SubprocessError


#####
# BK_MFMC: Boyov and Kolmogorovs (1) C++ max-flow/min-cut implementation (a)
#####

# constants
# relative position of the algorithm from the medpy package
__BK_MFMC_GRAPH_LIB = '/cpp/maxflow/graph.h'
__BK_MFMC_GRAPH_FILE = '/cpp/maxflow/graph.cpp'
__BK_MFMC_MAXFLOW_FILE = '/cpp/maxflow/maxflow.cpp'   

# symbols to be used to mark source or sink affiliation 
__BK_MFMC_SOURCE_MARKER = 1
__BK_MFMC_SINK_MARKER = 0

# preformted header and footer of the C++ file to generate with placeholders
__BK_MFMC_HEADER = """
#include <stdio.h>
#include "{}"

int main()
{{
    typedef Graph<double,double,double> GraphType;
    GraphType *g = new GraphType(/*estimated # of nodes*/ {}, /*estimated # of edges*/ {}); 
"""

__BK_MFMC_FOOTER = """
    int flow = g -> maxflow();

    printf("flow=%d\\n", flow);
    int i;
    for(i= 0; i < {}; i++) {{
        if (g->what_segment(i) == GraphType::SOURCE)
            printf("%d={}\\n", i + 1); /* adjust id systems by adding a 1 */
        else
            printf("%d={}\\n", i + 1); /* adjust id systems by adding a 1 */
    }}
    delete g;

    return 0;
}}
"""

def bk_mfmc_generate(graph):
    """
    Generate a C++ file executing the Boyov and Kolmogorovs max-flow/min-cut algorithm
    over the supplied graph.
    
    @param graphs: The graph representing the problem. 
    @type graphs: medpy.graphcut.Graph
    @return: A compile-ready, pre-formated version of the problem to be compiled/executed
             either using the methods provided by the @link: cut module or manually.
    @rtype: str
    
    @raise SubprocessError: When the algorithm library can not be accessed.
    """
    # prepare logger
    logger = Logger.getInstance()
    
    logger.info('Checking conditions for BK_MFMC source file creation...')
    
    # get the algorithms library
    library = __bk_mfmc_get_library()
    
    # format header and footer
    header = __BK_MFMC_HEADER.format(library['graph_lib'], len(graph.get_tweights()), len(graph.get_nweights()))
    footer = __BK_MFMC_FOOTER.format(len(graph.get_nodes()), __BK_MFMC_SOURCE_MARKER, __BK_MFMC_SINK_MARKER)
    
    logger.info('Generating BK_MFMC C++ source file...')
    
    # generate cpp file with the graph encoded
    # Note: The min-cut/max-flow algorithm required node ids to start from 0, while the
    # regions ids and therefore node ids returned by the graph object start from one.
    # The ids written to the file are therefore decremented by 1. This is taken into
    # account in the way the result is printed (i.e. increment of 1, see the __FOOTER)
    # !TODO: Since now this ignores directed graphs
    source_file = header
    source_file += '\tg -> add_node({});\n\n'.format(len(graph.get_nodes()))
    for node, weight in graph.get_tweights().iteritems():
        source_file += '\tg -> add_tweights({}, {}, {});\n'.format(node - 1, weight[0], weight[1])
    source_file += '\n'
    for edge, weight in graph.get_nweights().iteritems():
        source_file += '\tg -> add_edge({}, {}, {}, {});\n'.format(edge[0] - 1, edge[1] - 1, weight, weight)
    source_file += '\n'
    source_file += footer
    
    return source_file

def __bk_mfmc_get_library():
    """
    Return the location of the required algorithm files as dict after ensuring their existence.
    
    @raise SubprocessError: When the algorithm library can not be accessed.
    """
    library = {}
    
    # access the algorithms location
    try:
        library['graph_lib'] = medpy.__path__[0] + __BK_MFMC_GRAPH_LIB
        library['graph_file'] = medpy.__path__[0] + __BK_MFMC_GRAPH_FILE
        library['maxflow_file'] = medpy.__path__[0] + __BK_MFMC_MAXFLOW_FILE
    except Exception as e:
        raise SubprocessError('The path to the algorithm could not be accessed, reason: {}.'.format(e.message))
    
    # test if the algorithm files exist
    if not (os.path.exists(library['graph_lib']) or
            os.path.exists(library['graph_file']) or 
            os.path.exists(library['maxflow_file'])):
        raise SubprocessError('At least one of the required algorithm files does not seem to exists ({}, {}, {}).'.format(library['graph_lib'], library['graph_file'], library['maxflow_file']))
    
    return library
    
