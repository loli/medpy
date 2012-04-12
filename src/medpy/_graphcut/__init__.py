"""
@package medpy.graphcut
Functionalities to use graph-cut (max-flow/min-cut) algorithms.

Provides methods to build graphs from label-image using arbitrary energy functions
(boundary and regional terms), format these graphs to be processed by a number of
graph-cut implementations, executing these and parsing the results.

Supported graph-cut algorithms with tested version number:\n
    - \b BK_MFMC: Boykov and Kolmogorovs (1) max-flow/min-cut C++ implementation (a) [v3.01]

Modules:
    - graph: Create and modify graphs from nD label-images to be used in graph-cut algorithms.
    - generate: Generates output files from graphs that are processable by graph-cut algorithms.
    - cut: Prepares, compiles and executed graph-cut implementations.
    - parse: Parses the output returned by graph-cut implementations.
    - energy: Run-time optimized energy functions for graph-cut.
    

@note This package makes use of @link: medpy.core.Logger to generate progress and debug
      messages.

(a) http://vision.csd.uwo.ca/code/ [last seen: 01/2012]

(1) Boykov Y., Kolmogorov V. / "An Experimental Comparison of Min-Cut/Max-Flow
Algorithms for Energy Minimization in Vision" / In IEEE Transactions on PAMI, Vol. 26,
No. 9, pp. 1124-1137, Sept. 2004
"""

# determines the modules that should be imported when "from graphcut import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from graph import graph_from_labels, relabel, Graph
from generate import bk_mfmc_generate
from cut import bk_mfmc_cut
from parse import bk_mfmc_parse, apply_mapping
from energy import boundary_stawiaski, intersection, points_to_slices, slices_to_points, boundary_medium_intensity, inflate_rectangle