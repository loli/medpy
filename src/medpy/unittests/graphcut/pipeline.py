"""
Unittest for the medpy.graphcut s BK_MFMC algorithm approach.

@author Oskar Maier
@version d0.1.0
@since 2011-01-29
@status Development
"""

# build-in modules
import unittest

# third-party modules

# own modules
from medpy.graphcut import graph_from_labels, bk_mfmc_generate, bk_mfmc_cut, bk_mfmc_parse, Graph

# code
class TestBkMfmc(unittest.TestCase):
    """Executes the complete pipeline of the BK_MFMC algorithm, checking the results."""

    __label_image = [[ 1,  2,  3,  3, 10],
                     [ 1,  4,  3,  8, 10],
                     [ 5,  5,  6,  7, 10],
                     [ 6,  6,  6,  9, 10]]
    __fg_marker = [[1, 0, 0, 0, 0],
                 [1, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0]]
    __bg_marker = [[0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 1]]
    
    def test_bk_mfmc(self):
        """Executes the complete pipeline of the BK_MFMC algorithm."""
        # create the graph from the image
        label_image = self.__label_image
        graph = graph_from_labels(label_image,
                                  self.__fg_marker,
                                  self.__bg_marker,
                                  boundary_term=self.__boundary_term)
        
        # alter the graph, removing some edges that are undesired
        nweights = graph.get_nweights()
        for edge in self.__get_bad_edges():
            if edge in nweights: del nweights[edge]
            else: del nweights[(edge[1], edge[0])]
        
        graph_new = Graph()
        graph_new.set_nodes(graph.get_nodes())
        graph_new.set_source_nodes(graph.get_source_nodes())
        graph_new.set_sink_nodes(graph.get_sink_nodes())
        graph_new.set_nweights(nweights)
        
        if graph_new.inconsistent():
            self.fail('The newly generated graph is inconsistent. Reasons: {}'.format('\n'.join(graph_new.inconsistent())))
        
        # perparing and executing BK_MFMC
        source_file = bk_mfmc_generate(graph_new)
        try:
            output = bk_mfmc_cut(source_file)
        except Exception as e:
            self.fail('An error was thrown during the external executions: {}'.format(e.message))
            
        # parsing the results
        results = bk_mfmc_parse(output)
        
        # set expected results
        maxflow = 16
        mapping = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1, 10: 0}
        
        # check results for validity
        self.assertEqual(results[0], maxflow, 'The resulting maxflow {} differes from the expected one {}.'.format(results[0], maxflow))
        self.assertSequenceEqual(results[1], mapping, 'The resulting mapping is wrong.', dict)
        
            
    def __boundary_term(self, label_image, r1_bb, r2_bb, r1_id, r2_id, boundary_term_args):
        "The boundary term function used for this tests."
        tpl1 = (r1_id, r2_id)
        tpl2 = (r2_id, r1_id)
        
        mapping = self.__get_mapping()
    
        if tpl1 in mapping: return mapping[tpl1]
        else: return mapping[tpl2]
        
    def __get_mapping(self):
        "Returns a dict holding the edge to weight mappings."
        mapping = {}
        mapping[(1, 2)] = 5
        mapping[(1, 4)] = 7
        mapping[(1, 5)] = 11
        mapping[(2, 3)] = 6
        mapping[(2, 4)] = 4
        mapping[(3, 4)] = 9
        mapping[(3, 6)] = 1 # edge that has to be removed later
        mapping[(3, 8)] = 2
        mapping[(3, 10)] = 6
        mapping[(4, 5)] = 3
        mapping[(5, 6)] = 8
        mapping[(6, 7)] = 5
        mapping[(6, 9)] = 3
        mapping[(7, 8)] = 3
        mapping[(7, 9)] = 7
        mapping[(7, 10)] = 1 # edge that has to be removed later
        mapping[(8, 10)] = 8
        mapping[(9, 10)] = 5
        
        return mapping
    
    def __get_bad_edges(self):
        "Returns the edges that should not be in the graph and have to be removed."
        return ((3, 6), (7, 10))
    
if __name__ == '__main__':
    unittest.main()     