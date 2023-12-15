import numpy as np

from medpy.filter import anisotropic_diffusion

# Purpose of these tests is to ensure the filter code does not crash
# Depending on Python versions


def test_anisotropic_diffusion_powerof2_single_channel():
    arr = np.random.uniform(size=(64, 64))
    filtered = anisotropic_diffusion(arr)
    assert filtered.shape == arr.shape


def test_anisotropic_diffusion_powerof2_three_channels():
    # Purpose of this test is to ensure the filter code does not crash
    # Depending on Python versions
    arr = np.random.uniform(size=(64, 64, 3))
    filtered = anisotropic_diffusion(arr)
    assert filtered.shape == arr.shape


def test_anisotropic_diffusion_single_channel():
    # Purpose of this test is to ensure the filter code does not crash
    # Depending on Python versions
    arr = np.random.uniform(size=(60, 31))
    filtered = anisotropic_diffusion(arr)
    assert filtered.shape == arr.shape


def test_anisotropic_diffusion_three_channels():
    # Purpose of this test is to ensure the filter code does not crash
    # Depending on Python versions
    arr = np.random.uniform(size=(60, 31, 3))
    filtered = anisotropic_diffusion(arr)
    assert filtered.shape == arr.shape


def test_anisotropic_diffusion_voxel_spacing_array():
    # Purpose of this test is to ensure the filter code does not crash
    # Depending on Python versions
    arr = np.random.uniform(size=(60, 31, 3))
    filtered = anisotropic_diffusion(arr, voxelspacing=np.array([1, 1, 1.0]))
    assert filtered.shape == arr.shape
