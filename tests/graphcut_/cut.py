"""
Unittest for the medpy.graphcut 's graph cut algorithm approach.
Essentially executes the whole pipeline from a supplied label image, foreground markers
and background markers over graph construction, cut execution until the final
re-labelling of the original label image.
One test if performed with the region bases, and one with the voxel based term.
The test is conducted with an artificial boundary term.

@author Oskar Maier
@version r0.1.2
@since 2011-01-29
@status Release
"""

# build-in modules
import unittest

# third-party modules
import numpy

# own modules
from medpy import filter
from medpy.graphcut import Graph, GraphDouble, graph_from_labels, graph_from_voxels
from medpy.graphcut.energy_voxel import boundary_difference_linear


# code
class TestCut(unittest.TestCase):
    """Executes the complete pipeline of the graph cut algorithm, checking the results."""

    # data for voxel based test
    __voriginal_image = [
        [[1, 0, 1, 2, 3], [1, 0, 1, 4, 3], [0, 1, 1, 6, 4]],
        [[1, 0, 1, 2, 3], [1, 0, 1, 4, 3], [0, 1, 1, 6, 4]],
    ]

    __vfg_markers = [
        [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 0]],
        [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 0]],
    ]

    __vbg_markers = [
        [[0, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
        [[0, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
    ]
    __vexpected = [
        [[1, 1, 1, 0, 0], [1, 1, 1, 0, 0], [1, 1, 1, 0, 0]],
        [[1, 1, 1, 0, 0], [1, 1, 1, 0, 0], [1, 1, 1, 0, 0]],
    ]
    __vmaxflow = 3

    # data for region based test
    __label_image = [
        [1, 2, 3, 3, 10],
        [1, 4, 3, 8, 10],
        [5, 5, 6, 7, 10],
        [6, 6, 6, 9, 10],
    ]
    __fg_marker = [[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    __bg_marker = [[0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1]]
    __result = [[1, 1, 1, 1, 0], [1, 1, 1, 0, 0], [1, 1, 1, 1, 0], [1, 1, 1, 1, 0]]
    __maxflow = 16

    def test_voxel_based(self):
        """Executes the complete pipeline of the graph cut algorithm."""
        # create the graph from the image
        original_image = numpy.asarray(self.__voriginal_image)
        graph = graph_from_voxels(
            numpy.asarray(self.__vfg_markers),
            numpy.asarray(self.__vbg_markers),
            boundary_term=boundary_difference_linear,
            boundary_term_args=(original_image, False),
        )

        # execute min-cut / executing BK_MFMC
        try:
            maxflow = graph.maxflow()
        except Exception as e:
            self.fail(
                "An error was thrown during the external executions: {}".format(
                    e.message
                )
            )

        # reshape results to form a valid mask
        result = numpy.zeros(original_image.size, dtype=numpy.bool_)
        for idx in range(len(result)):
            result[idx] = 0 if graph.termtype.SINK == graph.what_segment(idx) else 1
        result = result.reshape(original_image.shape)

        # check results for validity
        self.assertTrue(
            (result == numpy.asarray(self.__vexpected)).all(),
            "Resulting voxel-based cut is different than expected.",
        )
        self.assertEqual(
            maxflow,
            self.__vmaxflow,
            "The resulting maxflow {} differs from the expected one {}.".format(
                maxflow, self.__vmaxflow
            ),
        )

    def test_region_based(self):
        """Executes the complete pipeline of the graph cut algorithm."""
        return  # deactivated as errorneous

        # create the graph from the image
        label_image = self.__label_image
        graph = graph_from_labels(
            label_image,
            self.__fg_marker,
            self.__bg_marker,
            boundary_term=self.__boundary_term,
        )

        # alter the graph, removing some edges that are undesired
        nweights = graph.get_nweights()
        for edge in self.__get_bad_edges():
            if edge in nweights:
                del nweights[edge]
            else:
                del nweights[(edge[1], edge[0])]

        # create new graph from old graph to check the setting methods of the Graph object
        graph_new = Graph()
        graph_new.set_nodes(graph.get_node_count())
        graph_new.set_source_nodes(graph.get_source_nodes())
        graph_new.set_sink_nodes(graph.get_sink_nodes())
        graph_new.set_nweights(nweights)

        if graph_new.inconsistent():
            self.fail(
                "The newly generated graph is inconsistent. Reasons: {}".format(
                    "\n".join(graph_new.inconsistent())
                )
            )

        # build graph cut graph from graph
        gcgraph = GraphDouble(len(graph_new.get_nodes()), len(graph_new.get_nweights()))
        gcgraph.add_node(len(graph_new.get_nodes()))
        for node, weight in list(graph_new.get_tweights().items()):
            gcgraph.add_tweights(int(node - 1), weight[0], weight[1])
        for edge, weight in list(graph_new.get_nweights().items()):
            gcgraph.add_edge(int(edge[0] - 1), int(edge[1] - 1), weight[0], weight[1])

        # execute min-cut / executing BK_MFMC
        try:
            maxflow = gcgraph.maxflow()
        except Exception as e:
            self.fail(
                "An error was thrown during the external executions: {}".format(
                    e.message
                )
            )

        # apply results to the label image
        label_image = filter.relabel_map(
            label_image,
            gcgraph.what_segment,
            lambda fun, rid: 0 if gcgraph.termtype.SINK == fun(int(rid) - 1) else 1,
        )

        # check results for validity
        self.assertEqual(
            maxflow,
            self.__maxflow,
            "The resulting maxflow {} differs from the expected one {}.".format(
                maxflow, self.__maxflow
            ),
        )
        self.assertSequenceEqual(
            label_image.tolist(),
            self.__result,
            "The resulting cut is wrong. Expected\n {}\n got\n{}".format(
                numpy.asarray(self.__result, dtype=numpy.bool_), label_image
            ),
        )

    @staticmethod
    def __boundary_term(graph, label_image, boundary_term_args):
        "The boundary term function used for this tests."
        dic = TestCut.__get_mapping()
        for key, value in list(dic.items()):
            dic[key] = (value, value)
        return dic

    @staticmethod
    def __get_mapping():
        "Returns a dict holding the edge to weight mappings."
        mapping = {}
        mapping[(1, 2)] = 5
        mapping[(1, 4)] = 7
        mapping[(1, 5)] = 11
        mapping[(2, 3)] = 6
        mapping[(2, 4)] = 4
        mapping[(3, 4)] = 9
        mapping[(3, 6)] = 1  # edge that has to be removed later
        mapping[(3, 8)] = 2
        mapping[(3, 10)] = 6
        mapping[(4, 5)] = 3
        mapping[(5, 6)] = 8
        mapping[(6, 7)] = 5
        mapping[(6, 9)] = 3
        mapping[(7, 8)] = 3
        mapping[(7, 9)] = 7
        mapping[(7, 10)] = 1  # edge that has to be removed later
        mapping[(8, 10)] = 8
        mapping[(9, 10)] = 5

        return mapping

    def __get_bad_edges(self):
        "Returns the edges that should not be in the graph and have to be removed."
        return ((3, 6), (7, 10))


if __name__ == "__main__":
    unittest.main()
