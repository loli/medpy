"""
Unittest for the medpy.graphcut.parse methods.

@author Oskar Maier
@version d0.1.0
@since 2011-01-26
@status Development
"""

# build-in modules
import unittest

# third-party modules
import scipy

# own modules
from medpy.graphcut import bk_mfmc_parse, apply_mapping
from medpy.core.exceptions import ArgumentError

# code
class TestParse(unittest.TestCase):

    __label_image = [[0, 1, 2, 2, 9],
                     [0, 3, 2, 7, 9],
                     [4, 4, 5, 6, 9],
                     [5, 5, 5, 8, 9]]
    __mask = [[0, 0, 1, 1, 1],
              [0, 0, 1, 1, 1],
              [0, 0, 1, 1, 1],
              [1, 1, 1, 1, 1]]
    
    def test_apply_mapping(self):
        """
        Test the application of the results to the original label image using
        @link medpy.graphcut.parse.apply_mapping().
        """
        mapping = {0: 0,
                   1: 0,
                   2: 1,
                   3: 0,
                   4: 0,
                   5: 1,
                   6: 1,
                   7: 1,
                   8: 1,
                   9: 1}
        mask = apply_mapping(self.__label_image, mapping)
        li = scipy.asarray(self.__label_image)
        for el in zip(mask.flat, li.flat):
            self.assertEqual(el[0], mapping[el[1]], 'The mapping has not been performed right.')
        
        
    
    def test_bk_mfmc(self):
        """
        Runs the test for the @link medpy.graphcut.parse.bk_mfmc_parse() function, parsing
        some more complicated and maleformed strings.
        """
        str1 = 'flow=348234\n#com\n\t#com\n #com\n\t\n \n2=4\n 3=5\n  4=6  \n\t5=7\t\n\n'
        str2 = 'flow=-5'
        str3 = ''
        str4 = 'flow=5\na=b'
        str5 = 'flow=5\n1==2'
        
        # test results
        res1 = bk_mfmc_parse(str1)
        self.assertEqual(res1[0], 348234)
        self.assertEqual(len(res1[1]), 4)
        self.assertEqual(res1[1][2], 4)
        self.assertEqual(res1[1][3], 5)
        self.assertEqual(res1[1][4], 6)
        self.assertEqual(res1[1][5], 7)
        
        res2 = bk_mfmc_parse(str2)
        self.assertEqual(res2[0], -5)
        self.assertEqual(len(res2[1]), 0)
        
        self.assertRaises(ArgumentError, bk_mfmc_parse, str3)
        
        self.assertRaises(ArgumentError, bk_mfmc_parse, str4)
        
        self.assertRaises(ArgumentError, bk_mfmc_parse, str5)
        
if __name__ == '__main__':
    unittest.main()