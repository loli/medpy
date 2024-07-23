"""
Unittest for medpy.features.histogram.

@author Oskar Maier
@version r0.1.0
@since 2024-07-23
@status Release
"""

import numpy as np

from medpy.metric import asd, assd, obj_asd, obj_assd

result_min = np.asarray([1, 0]).astype(bool)
reference_min = np.asarray([0, 1]).astype(bool)
result_sym = np.asarray(
    [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0]]
).astype(bool)
reference_sym = np.asarray(
    [[1, 1, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]]
).astype(bool)


def test_asd_identity():
    assert asd(result_min, result_min) == 0


def test_assd_identity():
    assert assd(result_min, result_min) == 0


def test_obj_asd_identity():
    assert obj_asd(result_min, result_min) == 0


def test_obj_assd_identity():
    assert obj_assd(result_min, result_min) == 0


def test_asd_distance():
    assert asd(result_min, reference_min) == 1.0


def test_assd_distance():
    assert assd(result_min, reference_min) == 1.0


def test_asd_voxelspacing():
    assert asd(result_min, reference_min, voxelspacing=[2]) == 2.0


def test_assd_voxelspacing():
    assert assd(result_min, reference_min, voxelspacing=[2]) == 2.0


def test_asd_is_not_symetric():
    asd_1 = asd(result_sym, reference_sym)
    asd_2 = asd(reference_sym, result_sym)
    assert asd_1 != asd_2


def test_assd_is_symetric():
    assd_1 = assd(result_sym, reference_sym)
    assd_2 = assd(reference_sym, result_sym)
    assert assd_1 == assd_2


def test_obj_asd_is_not_symetric():
    asd_1 = obj_asd(result_sym, reference_sym)
    asd_2 = obj_asd(reference_sym, result_sym)
    assert asd_1 != asd_2


def test_obj_assd_is_symetric():
    assd_1 = obj_assd(result_sym, reference_sym)
    assd_2 = obj_assd(reference_sym, result_sym)
    assert assd_1 == assd_2
