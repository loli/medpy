"""
Unittest for the medpy.graphcut.graph classes.

!TODO:
- Implement the test_Graph() test for the Graph class. Follow the line along test_GCGraph.

@author Oskar Maier
@version d0.2.1
@since 2011-01-19
@status Development
"""

# build-in modules
import unittest

# own modules
from medpy.graphcut import GCGraph

# third-party modules


# code
class TestGraph(unittest.TestCase):
    def test_Graph(self):
        """Test the @link medpy.graphcut.graph.Graph implementation."""
        pass

    def test_GCGraph(self):
        """Test the @link medpy.graphcut.graph.GCGraph implementation."""
        # set test parmeters
        nodes = 10
        edges = 20

        # construct graph
        graph = GCGraph(nodes, edges)  # nodes edges

        # SETTER TESTS
        # set_source_nodes should accept a sequence and raise an error if an invalid node id was passed
        graph.set_source_nodes(list(range(0, nodes)))
        self.assertRaises(ValueError, graph.set_source_nodes, [-1])
        self.assertRaises(ValueError, graph.set_source_nodes, [nodes])
        # set_sink_nodes should accept a sequence and raise an error if an invalid node id was passed
        graph.set_sink_nodes(list(range(0, nodes)))
        self.assertRaises(ValueError, graph.set_sink_nodes, [-1])
        self.assertRaises(ValueError, graph.set_sink_nodes, [nodes])
        # set_nweight should accept integers resp. floats and raise an error if an invalid node id was passed or the weight is zero or negative
        graph.set_nweight(0, nodes - 1, 1, 2)
        graph.set_nweight(nodes - 1, 0, 0.5, 1.5)
        self.assertRaises(ValueError, graph.set_nweight, -1, 0, 1, 1)
        self.assertRaises(ValueError, graph.set_nweight, 0, nodes, 1, 1)
        self.assertRaises(ValueError, graph.set_nweight, 0, 0, 1, 1)
        self.assertRaises(ValueError, graph.set_nweight, 0, nodes - 1, 0, 0)
        self.assertRaises(ValueError, graph.set_nweight, 0, nodes - 1, -1, -2)
        self.assertRaises(ValueError, graph.set_nweight, 0, nodes - 1, -0.5, -1.5)
        # set_nweights works as set_nweight but takes a dictionary as argument
        graph.set_nweights({(0, nodes - 1): (1, 2)})
        graph.set_nweights({(nodes - 1, 0): (0.5, 1.5)})
        self.assertRaises(ValueError, graph.set_nweights, {(-1, 0): (1, 1)})
        self.assertRaises(ValueError, graph.set_nweights, {(0, nodes): (1, 1)})
        self.assertRaises(ValueError, graph.set_nweights, {(0, 0): (1, 1)})
        self.assertRaises(ValueError, graph.set_nweights, {(0, nodes - 1): (0, 0)})
        self.assertRaises(ValueError, graph.set_nweights, {(0, nodes - 1): (-1, -2)})
        self.assertRaises(
            ValueError, graph.set_nweights, {(0, nodes - 1): (-0.5, -1.5)}
        )
        # set_tweight should accept integers resp. floats and raise an error if an invalid node id was passed or the weight is zero or negative
        graph.set_tweight(0, 1, 2)
        graph.set_tweight(nodes - 1, 0.5, 1.5)
        graph.set_tweight(0, -1, -2)
        graph.set_tweight(0, 0, 0)
        self.assertRaises(ValueError, graph.set_tweight, -1, 1, 1)
        self.assertRaises(ValueError, graph.set_tweight, nodes, 1, 1)
        # set_tweights works as set_tweight but takes a dictionary as argument
        graph.set_tweights({0: (1, 2)})
        graph.set_tweights({nodes - 1: (0.5, 1.5)})
        graph.set_tweights({0: (-1, -2)})
        graph.set_tweights({0: (0, 0)})
        self.assertRaises(ValueError, graph.set_tweights, {-1: (1, 1)})
        self.assertRaises(ValueError, graph.set_tweights, {nodes: (1, 1)})

        # SOME MINOR GETTERS
        self.assertEqual(graph.get_node_count(), nodes)
        self.assertEqual(graph.get_edge_count(), edges)
        self.assertSequenceEqual(graph.get_nodes(), list(range(0, nodes)))


if __name__ == "__main__":
    unittest.main()
