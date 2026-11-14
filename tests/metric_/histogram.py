"""
Unit and Hypothesis Tests for histogram metrics

"""

import numpy as np
from hypothesis import assume, given
from hypothesis import settings as hyp_settings
from hypothesis import strategies

from medpy.metric import histogram

metric_list = ["manhattan", "minowski", "euclidean", "noelle_2", "noelle_4", "noelle_5"]
metric_list_to_doublecheck = ["cosine_1"]

unknown_property = ["histogram_intersection"]
still_under_dev = ["quadratic_forms"]
similarity_funcs = ["correlate", "cosine", "cosine_2", "cosine_alt", "fidelity_based"]
semi_metric_list = [
    "kullback_leibler",
    "jensen_shannon",
    "chi_square",
    "chebyshev",
    "chebyshev_neg",
    "histogram_intersection_1",
    "relative_deviation",
    "relative_bin_deviation",
    "noelle_1",
    "noelle_3",
    "correlate_1",
]

default_feature_dim = 1000
default_num_bins = 20

range_feature_dim = [10, 10000]
range_num_bins = [5, 200]


def within_tolerance(x, y):
    "Function to indicate acceptable level of tolerance in numerical differences"

    # as the np.allcose function is not symmetric,
    # this ensurers second arg is larger
    if x < y:
        smaller = x
        larger = y
    else:
        smaller = y
        larger = x

    # atol=np.finfo(float).eps is super strict, choosing 1e-3
    # rtol=1e-2 approx. matches two decimal points
    return bool(np.allclose(smaller, larger, rtol=1e-2, atol=1e-3))


def make_random_histogram(length=default_feature_dim, num_bins=default_num_bins):
    "Returns a sequence of histogram density values that sum to 1.0"

    hist, bin_edges = np.histogram(
        np.random.random(length), bins=num_bins, density=True
    )

    # to ensure they sum to 1.0
    hist = hist / sum(hist)

    if len(hist) < 2:
        raise ValueError("Invalid histogram")

    return hist


# Increasing the number of examples to try
@hyp_settings(max_examples=1000)  # , verbosity=Verbosity.verbose)
@given(
    strategies.sampled_from(metric_list),
    strategies.integers(range_feature_dim[0], range_feature_dim[1]),
    strategies.integers(range_num_bins[0], range_num_bins[1]),
)
def test_math_properties_metric(method_str, feat_dim, num_bins):
    """Trying to test the four properties on the same set of histograms"""

    # checking for bad examples
    assume(not num_bins > feat_dim)

    h1 = make_random_histogram(feat_dim, num_bins)
    h2 = make_random_histogram(feat_dim, num_bins)
    h3 = make_random_histogram(feat_dim, num_bins)

    method = getattr(histogram, method_str)

    check_indiscernibility(method, h1)
    check_symmetry(method, h1, h2)
    check_nonnegativity(method, h1, h2)
    check_triangle_inequality(method, h1, h2, h3)


def check_indiscernibility(method, hist):
    """a must be unique, and a is identical to a if and only if dist(a,a)=0"""

    assert within_tolerance(method(hist, hist), 0.0)


def check_symmetry(method, h1, h2):
    """symmetry test"""

    d12 = method(h1, h2)
    d21 = method(h2, h1)

    assert within_tolerance(d12, d21)


def check_nonnegativity(method, h1, h2):
    """distance between two samples must be >= 0.0"""

    assert method(h1, h2) >= 0.0


def check_triangle_inequality(method, h1, h2, h3):
    """Classic test for a metric: dist(a,b) < dist(a,b) + dist(a,c)"""

    d12 = method(h1, h2)
    d23 = method(h2, h3)
    d13 = method(h1, h3)
    assert d12 <= d13 + d23
