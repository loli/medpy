"""
@package medpy.features
Functionality to extract features from images and present/manipulate them.

Packages:
    - histogram: Functions to create and manipulate (fuzzy) histograms.
    - intensity: Functions to extracts voxel-wise intensity based features from (medical) images.
    - utilities: Utilities for feature handling. Currently only for features from the @see medpy.features.intensity package.
"""

# determines the modules that should be imported when "from metric import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from histogram import fuzzy_histogram, triangular_membership, trapezoid_membership, \
                      gaussian_membership, sigmoidal_difference_membership
from intensity import centerdistance, centerdistance_xdminus1, guassian_gradient_magnitude, \
                      hemispheric_difference, indices, intensities, local_histogram, local_mean_gauss, \
                      median, shifted_mean_gauss, mask_distance
from utilities import append, join, normalize, normalize_with_model