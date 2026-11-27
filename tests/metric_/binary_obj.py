"""
Unittest for the object-wise metrics in medpy.metric.binary.
"""

import numpy as np

from medpy.metric import asd, obj_asd, obj_fpr, obj_tpr

# reference holds three objects, result detects two of them and adds none
result = np.asarray([1, 0, 1, 0, 0]).astype(bool)
reference = np.asarray([1, 0, 1, 0, 1]).astype(bool)

# one object each: a 3x3 square and its middle column
square = np.ones((3, 3), dtype=bool)
column = np.asarray([[0, 1, 0], [0, 1, 0], [0, 1, 0]]).astype(bool)


def test_obj_tpr_is_fraction_of_reference_objects_detected():
    assert np.isclose(obj_tpr(result, reference), 2 / 3)
    assert obj_tpr(reference, result) == 1.0


def test_obj_fpr_is_fraction_of_result_objects_not_in_reference():
    assert obj_fpr(result, reference) == 0.0
    assert np.isclose(obj_fpr(reference, result), 1 / 3)


def test_obj_asd_matches_asd_for_single_objects():
    assert np.isclose(obj_asd(square, column), asd(square, column))
    assert np.isclose(obj_asd(column, square), asd(column, square))
