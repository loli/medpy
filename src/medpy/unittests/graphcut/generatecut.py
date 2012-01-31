"""
Unittest for the medpy.graphcut.generate and medpy.graphcut.cut methods.

@author Oskar Maier
@version d0.1.0
@since 2011-01-26
@status Development
"""

# build-in modules
import unittest

# third-party modules

# own modules
from medpy.graphcut import graph_from_labels, bk_mfmc_generate, bk_mfmc_cut

# code
class TestGenerateCut(unittest.TestCase):

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
        """
        Runs the test for the @link medpy.graphcut.generate.bk_mfmc_generate() and the
        @link: medpy.graphcut.cut.bk_mfmc_cut() function, which mainly assures that all
        of the external calls are applicable.
        """
        label_image = self.__label_image
        graph = graph_from_labels(label_image,
                                  self.__fg_marker,
                                  self.__bg_marker,
                                  boundary_term=self.__boundary_term)
        source_file = bk_mfmc_generate(graph)
        try:
            bk_mfmc_cut(source_file)
        except Exception as e:
            self.fail('An error was thrown during the external executions: {}'.format(e.message))
            
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
