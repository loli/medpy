#include "pythongraph.h"
#include <boost/python.hpp>

// Instantiations: Graph<captype, tcaptype, flowtype>()
// IMPORTANT:
//    flowtype should be 'larger' than tcaptype
//    tcaptype should be 'larger' than captype
typedef Pythongraph<double, double, double> GraphDouble;
typedef Pythongraph<float, float, float> GraphFloat;
typedef Pythongraph<int, int, int> GraphInt;

// Create thin-wrappers for overloading/default arguments
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphDouble_add_node_overload, maxflow, 0, 1)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphDouble_maxflow_overload, maxflow, 0, 2)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphDouble_what_segment_overload, what_segment, 1, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphFloat_add_node_overload, maxflow, 0, 1)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphFloat_maxflow_overload, maxflow, 0, 2)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphFloat_what_segment_overload, what_segment, 1, 2)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphInt_add_node_overload, maxflow, 0, 1)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphInt_maxflow_overload, maxflow, 0, 2)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(GraphInt_what_segment_overload, what_segment, 1, 2)


// Wrapper functions for different scopes
void wrap_scopegraphfloat()
{
	using namespace boost::python;
	scope graphFloat = 
		class_<GraphFloat>("GraphFloat", "Graph template intance with float for flowtype, tcaptype and captype. Takes the number of nodes as first and the number of edges as second parameter. Although it is possible to exceed these values later, it is discourage as it leads to bad memory management. The edges i->j and j->i count here as one single edge.", init<int, int>())
        .def("add_node", &GraphFloat::add_node/*, GraphFloat_add_node_overload()*/) // "Add one or more nodes to the graph and returns the id of the first such created node. The total number of added nodes should never exceed the max node number passed to the initializer. Only nodes added with this function can be referenced in methods such as add_edge and add_tweights."
        .def("add_edge", &GraphFloat::add_edge, "Add an edge from i to j with the capacity cap and reversed capacity rev_cap. Node ids start from 0. Repeated calls lead to the addition of multiple arcs and therefore the allocate memory can be exceeded.")
        .def("sum_edge", &GraphFloat::sum_edge, "Add an edge from i to j with the capacity cap and reversed capacity rev_cap. Node ids start from 0. Repeated calls are summed to already existing edge weights. Requires less memory, but is slightly slower.")
        .def("add_tweights", &GraphFloat::add_tweights, "Add a terminal weight from cap_source to i and from i to cap_sink. Can be called multiple times (add to the existing weights).")
        .def("maxflow", &GraphFloat::maxflow/*, GraphFloat_maxflow_overload()*/, "Compute the min-cut/max-flow of the graph and return the maxflow value.")
        .def("what_segment", &GraphFloat::what_segment/*, GraphFloat_what_segment_overload()*/, "Returns the terminal the node i belongs to after executing the min-cut/max-flow. Returns either GraphFloat::SOURCE or GraphFloat::SINK.")
        .def("reset", &GraphFloat::reset, "Reset the whole graph to the state just after initialization. Save some time against deleting and creating a new one.")
		.def("get_edge", &GraphFloat::get_edge, "Returns the weight of the directed edge i->j between two node. If not yet set, returns 0. If more than one arc, returns the weight of the first encountered.")
        //.def("get_first_arc", &GraphFloat::get_first_arc) // These two cause problems with their return value. Disabled, since barely ever used.
        //.def("get_next_arc", &GraphFloat::get_next_arc)
        .def("get_node_num", &GraphFloat::get_node_num, "Returns the number of nodes already declared with the add_node method.")
        .def("get_arc_num", &GraphFloat::get_arc_num)
        .def("get_arc_ends", &GraphFloat::get_arc_ends)
        .def("get_trcap", &GraphFloat::get_trcap)
        .def("get_rcap", &GraphFloat::get_rcap)
        .def("set_trcap", &GraphFloat::set_trcap)
        .def("set_rcap", &GraphFloat::set_rcap)
        .def("mark_node", &GraphFloat::mark_node)
        .def("remove_from_changed_list", &GraphFloat::remove_from_changed_list)
		;

		enum_<GraphFloat::termtype>("termtype")
		.value("SOURCE", GraphFloat::SOURCE)
		.value("SINK", GraphFloat::SINK)
		;
}

void wrap_scopegraphdouble()
{
	using namespace boost::python;
	scope graphDouble = 
		class_<GraphDouble>("GraphDouble", "Graph template intance with double for flowtype, tcaptype and captype. Takes the number of nodes as first and the number of edges as second parameter. Although it is possible to exceed these values later, it is discourage as it leads to bad memory management. The edges i->j and j->i count here as one single edge.", init<int, int>())
        .def("add_node", &GraphDouble::add_node/*, GraphDouble_add_node_overload()*/) // "Add one or more nodes to the graph and returns the id of the first such created node. The total number of added nodes should never exceed the max node number passed to the initializer. Only nodes added with this function can be referenced in methods such as add_edge and add_tweights."
        .def("add_edge", &GraphDouble::add_edge, "Add an edge from i to j with the capacity cap and reversed capacity rev_cap. Node ids start from 0. Repeated calls lead to the addition of multiple arcs and therefore the allocate memory can be exceeded.")
        .def("sum_edge", &GraphDouble::sum_edge, "Add an edge from i to j with the capacity cap and reversed capacity rev_cap. Node ids start from 0. Repeated calls are summed to already existing edge weights. Requires less memory, but is slightly slower.")
        .def("add_tweights", &GraphDouble::add_tweights, "Add a terminal weight from cap_source to i and from i to cap_sink. Can be called multiple times (add to the existing weights).")
        .def("maxflow", &GraphDouble::maxflow/*, GraphDouble_maxflow_overload()*/, "Compute the min-cut/max-flow of the graph and return the maxflow value.")
        .def("what_segment", &GraphDouble::what_segment/*, GraphDouble_what_segment_overload()*/, "Returns the terminal the node i belongs to after executing the min-cut/max-flow. Returns either GraphDouble::SOURCE or GraphDouble::SINK.")
        .def("reset", &GraphDouble::reset, "Reset the whole graph to the state just after initialization. Save some time against deleting and creating a new one.")
		.def("get_edge", &GraphDouble::get_edge, "Returns the weight of the directed edge i->j between two node. If not yet set, returns 0. If more than one arc, returns the weight of the first encountered.")
        //.def("get_first_arc", &GraphDouble::get_first_arc) // These two cause problems with their return value. Disabled, since barely ever used.
        //.def("get_next_arc", &GraphDouble::get_next_arc)
        .def("get_node_num", &GraphDouble::get_node_num, "Returns the number of nodes already declared with the add_node method.")
        .def("get_arc_num", &GraphDouble::get_arc_num)
        .def("get_arc_ends", &GraphDouble::get_arc_ends)
        .def("get_trcap", &GraphDouble::get_trcap)
        .def("get_rcap", &GraphDouble::get_rcap)
        .def("set_trcap", &GraphDouble::set_trcap)
        .def("set_rcap", &GraphDouble::set_rcap)
        .def("mark_node", &GraphDouble::mark_node)
        .def("remove_from_changed_list", &GraphDouble::remove_from_changed_list)
    	;

	 	enum_<GraphDouble::termtype>("termtype")
		.value("SOURCE", GraphDouble::SOURCE)
		.value("SINK", GraphDouble::SINK)
    	;
}

void wrap_scopegraphint()
{
	using namespace boost::python;
	scope graphInt = 
		class_<GraphInt>("GraphInt", "Graph template intance with int for flowtype, tcaptype and captype. Takes the number of nodes as first and the number of edges as second parameter. Although it is possible to exceed these values later, it is discourage as it leads to bad memory management. The edges i->j and j->i count here as one single edge.", init<int, int>())
		  .def("add_node", &GraphInt::add_node/*, GraphInt_add_node_overload()*/) // "Add one or more nodes to the graph and returns the id of the first such created node. The total number of added nodes should never exceed the max node number passed to the initializer. Only nodes added with this function can be referenced in methods such as add_edge and add_tweights."
	      .def("add_edge", &GraphInt::add_edge, "Add an edge from i to j with the capacity cap and reversed capacity rev_cap. Node ids start from 0. Repeated calls lead to the addition of multiple arcs and therefore the allocate memory can be exceeded.")
	      .def("sum_edge", &GraphInt::sum_edge, "Add an edge from i to j with the capacity cap and reversed capacity rev_cap. Node ids start from 0. Repeated calls are summed to already existing edge weights. Requires less memory, but is slightly slower.")
		  .def("add_tweights", &GraphInt::add_tweights, "Add a terminal weight from cap_source to i and from i to cap_sink. Can be called multiple times (add to the existing weights).")
		  .def("maxflow", &GraphInt::maxflow/*, GraphInt_maxflow_overload()*/, "Compute the min-cut/max-flow of the graph and return the maxflow value.")
		  .def("what_segment", &GraphInt::what_segment/*, GraphInt_what_segment_overload()*/, "Returns the terminal the node i belongs to after executing the min-cut/max-flow. Returns either GraphInt::SOURCE or GraphInt::SINK.")
		  .def("reset", &GraphInt::reset, "Reset the whole graph to the state just after initialization. Save some time against deleting and creating a new one.")
		  .def("get_edge", &GraphInt::get_edge, "Returns the weight of the directed edge i->j between two node. If not yet set, returns 0. If more than one arc, returns the weight of the first encountered.")
		  //.def("get_first_arc", &GraphInt::get_first_arc) // These two cause problems with their return value. Disabled, since barely ever used.
		  //.def("get_next_arc", &GraphInt::get_next_arc)
		  .def("get_node_num", &GraphInt::get_node_num, "Returns the number of nodes already declared with the add_node method.")
		  .def("get_arc_num", &GraphInt::get_arc_num)
		  .def("get_arc_ends", &GraphInt::get_arc_ends)
		  .def("get_trcap", &GraphInt::get_trcap)
		  .def("get_rcap", &GraphInt::get_rcap)
		  .def("set_trcap", &GraphInt::set_trcap)
		  .def("set_rcap", &GraphInt::set_rcap)
		  .def("mark_node", &GraphInt::mark_node)
		  .def("remove_from_changed_list", &GraphInt::remove_from_changed_list)
	 	;

	 	enum_<GraphInt::termtype>("termtype")
		.value("SOURCE", GraphInt::SOURCE)
		.value("SINK", GraphInt::SINK)
	 	;
}


// Wrap classes
BOOST_PYTHON_MODULE(maxflow)
{
	using namespace boost::python;

	scope().attr("__doc__") = "Wrapper for the max-flow/min-cut implementation if 3.01 of Boyov and Kolmogorov. Exposes all public functions and variable except the seldom used get_first_arc() and get_first_next(), which are troublesome. Additionally the constructor does not accept error classes. For a documentation on the methods, best see the original cpp source code, which is well documented.";

	wrap_scopegraphfloat();
	wrap_scopegraphdouble();
	wrap_scopegraphint();
}
