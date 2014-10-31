/* pythongraph.h */
/**
	Extention of the Graph class that is shipped with the min-cut/max-flow algorithm by
	Yuri Boykov and Vladimir Kolmogorov. Simply wraps the constructor in a version not
	taking an exception class pointer to avoid problems with the boost:python wrapper.

	Author: Oskar Maier
*/

#ifndef __PYTHON_GRAPH_H__
#define __PYTHON_GRAPH_H__

#include "graph.h"

template <typename captype, typename tcaptype, typename flowtype>
class Pythongraph : public Graph<captype, tcaptype, flowtype>
{
public:
	Pythongraph(int node_num_max, int edge_num_max) : Graph<captype, tcaptype, flowtype>(node_num_max, edge_num_max, NULL) {};
	flowtype maxflow() { Graph<captype, tcaptype, flowtype>::maxflow(); };
	typename Graph<captype, tcaptype, flowtype>::termtype what_segment(int i) { Graph<captype, tcaptype, flowtype>::what_segment(i); };
};
#endif

