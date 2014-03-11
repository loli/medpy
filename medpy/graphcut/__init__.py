"""
@package medpy.graphcut
Functionalities to use graph-cut (max-flow/min-cut) algorithms.

Provides functionalities to efficiently construct graphs from various sources using
arbitrary energy functions (boundary and regional terms). The graph can then be saved in
the Dimacs graph standard and/or processed (i.e. cut) using 3rd party graph-cut
algorithms.

Supported graph-cut algorithms with tested version number:\n
    - \b BK_MFMC: Boykov and Kolmogorovs (1) max-flow/min-cut C++ implementation (a) [v3.01]

Modules:
    - graph: The basic Graph object.
    - write: Functions to persist a graph in various file formats like Dimacs (b).
    - maxflow: C++ wrapper around the max-flow/min-cut implementation of (1)
    - generate: Provides functions to generate graphs efficiently from nD label-images.
    - energy_label: Run-time optimized energy functions for the graph generation. Label/Superpixel based.
    - energy_voxel: Run-time optimized energy functions for the graph generation. Voxel based.
    

@note This package makes use of @link: medpy.core.Logger to generate progress and debug
      messages.

(a) http://vision.csd.uwo.ca/code/ [last seen: 01/2012]
(b) http://lpsolve.sourceforge.net/5.5/DIMACS_maxf.htm

(1) Boykov Y., Kolmogorov V. / "An Experimental Comparison of Min-Cut/Max-Flow
Algorithms for Energy Minimization in Vision" / In IEEE Transactions on PAMI, Vol. 26,
No. 9, pp. 1124-1137, Sept. 2004

@author Oskar Maier
"""

# determines the modules that should be imported when "from graphcut import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from graph import Graph, GCGraph
from maxflow import GraphDouble, GraphFloat, GraphInt # this always triggers an error in Eclipse, but is right
from write import graph_to_dimacs
from generate import graph_from_labels, graph_from_voxels
import energy_label
import energy_voxel
