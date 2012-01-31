"""
Unittest for the medpy.graphcut.energy methods.

@author Oskar Maier
@version d0.1.0
@since 2011-01-30
@status Development
"""

# build-in modules
import unittest

# third-party modules

# own modules
from medpy.graphcut import points_to_slices, slices_to_points, boundary_stawiaski, \
                           boundary_medium_intensity, intersection, inflate_rectangle

# code
class TestEnergy(unittest.TestCase):
    
    def test_intersection(self):
        """
        Test the @link medpy.graphcut.energy.intersection() function.
        """
        # 2d case
        rect1 = ([1,1], [4,3])
        rect2 = ([2,2], [5,4])
        expected = ([2,2], [4,3])
        inters = intersection(rect1, rect2)
        self.assertEqual(len(expected), len(inters), 'Result is of unexpected length.')
        for pe, pr in zip(expected, inters):
            self.assertEqual(len(pe), len(pr), 'Point of unexpected dimension.')
            for ve, vr in zip(pe, pr):
                self.assertEqual(ve, vr, 'Unexpected value.')
        # 3d case
        rect1 = ([1,1,3], [4,3,6])
        rect2 = ([2,2,2], [5,4,4])
        expected = ([2,2,3], [4,3,4])
        inters = intersection(rect1, rect2)
        self.assertEqual(len(expected), len(inters), 'Result is of unexpected length.')
        for pe, pr in zip(expected, inters):
            self.assertEqual(len(pe), len(pr), 'Point of unexpected dimension.')
            for ve, vr in zip(pe, pr):
                self.assertEqual(ve, vr, 'Unexpected value.')
        # 3d case \wo intersection
        rect1 = ([1,1,5], [4,3,6])
        rect2 = ([2,2,2], [5,4,4])
        self.assertFalse(intersection(rect1, rect2), 'Intersection falsely detected.')
        # check if reversed result is the same
        rect1 = ([1,1,3], [4,3,6])
        rect2 = ([2,2,2], [5,4,4])
        expected = intersection(rect1, rect2)
        inters = intersection(rect2, rect1)
        self.assertEqual(len(expected), len(inters), 'Result is of unexpected length.')
        for pe, pr in zip(expected, inters):
            self.assertEqual(len(pe), len(pr), 'Point of unexpected dimension.')
            for ve, vr in zip(pe, pr):
                self.assertEqual(ve, vr, 'Unexpected value.')
    
    def test_inflate_rectangle(self):
        """
        Test the @link medpy.graphcut.energy.inflate_rectangle() function.
        """
        p1 = [0,1,2]
        p2 = [3,4,5]
        p3 = [0,1]
        # standard case with 3 dimensions and inflation of 2
        rect = inflate_rectangle((p1, p2), 2)
        for i in range(3):
            self.assertEqual(rect[0][i], max(p1[i] - 2, 0), 'Lower left corner value invalid.')
            self.assertEqual(rect[1][i], p2[i] + 2, 'Upper right corner value invalid.')
        # unequal corner dimensions
        rect = inflate_rectangle((p1, p3), 2) # should silently be ignored
        rect = inflate_rectangle((p3, p1), 2) # should silently be ignored
        # invalid parameters
        rect = inflate_rectangle((p1, p2), False) # should result into no increasement and be ignored
        self.assertRaises(TypeError, inflate_rectangle , (p1, p2), None)
        self.assertRaises(TypeError, inflate_rectangle , (p1, False), 2)
        self.assertRaises(TypeError, inflate_rectangle , (False), 2)
    
    def test_slices_to_points(self):
        """
        Test the @link medpy.graphcut.energy.test_slices_to_points() function.
        """
        sl1 = slice(1,2)
        sl2 = slice(3,4)
        sl3 = slice(5,6)
        sl4 = slice(7,8,2)
        # standard case with 3 dimensions
        sl_list = [sl1, sl2, sl3]
        rect = slices_to_points(sl_list)
        for i in range(3):
            self.assertEqual(rect[0][i], sl_list[i].start, 'Lower left corner value invalid.')
            self.assertEqual(rect[1][i], sl_list[i].stop, 'Upper right corner value invalid.')
        # passing empty list
        rect = slices_to_points([])
        # passing list with invalid elements
        self.assertRaises(AttributeError, slices_to_points , [sl1, sl2, sl3, None])
        # passing slice with step parameter set (should get ignored)
        sl_list = [sl1, sl4]
        rect = slices_to_points(sl_list)
        for i in range(2):
            self.assertEqual(rect[0][i], sl_list[i].start, 'Lower left corner value invalid.')
            self.assertEqual(rect[1][i], sl_list[i].stop, 'Upper right corner value invalid.')
    
    def test_points_to_slices(self):
        """
        Test the @link medpy.graphcut.energy.points_to_slices() function.
        """
        p1 = (0,1,2,3,4,5,6,7)
        p2 = (8,9,10,11,12,13,14,15)
        p3 = (8,7,6)
        # standard case with 8 dimensions
        slices = points_to_slices((p1, p2))
        for i in range(8):
            self.assertEqual(slices[i].start, p1[i], 'Start took unexpected value.')
            self.assertEqual(slices[i].stop, p2[i], 'Stop took unexpected value.')
        # unequal dimensions in lower left corner
        slices = points_to_slices((p3, p2))
        self.assertEqual(len(slices), 3, 'Silent shortening of slices failed.')
        # unequal dimensions in upper right corner
        slices = points_to_slices((p2, p3))
        self.assertEqual(len(slices), 3, 'Silent shortening of slices failed.')
        # lower left and upper right corner exchanged (no exception should be thrown or error signaled)
        slices = points_to_slices((p2, p1))
        # too many points
        slices = points_to_slices((p1, p2, p3))
        # too few points
        self.assertRaises(TypeError, points_to_slices, (p1))
        # invalid parameter
        self.assertRaises(TypeError, points_to_slices, None)
        
        
if __name__ == '__main__':
    unittest.main()    
        