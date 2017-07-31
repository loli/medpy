"""
Unittest for medpy.metric.histogram

@author Pradeep Reddy Raamana
"""

import unittest
import numpy as np
from pytest import raises, warns, set_trace

from medpy.metric import histogram

metric_list = [
    'kullback_leibler', 'manhattan', 'minowski', 'euclidean',
    'cosine_1',
    'noelle_2', 'noelle_4', 'noelle_5' ]

unknown_prop_list = ['histogram_intersection']
still_under_dev = ['quadratic_forms']
similarity_func = ['correlate', 'cosine', 'cosine_2', 'cosine_alt', 'fidelity_based']

semi_metric_list = [
    'jensen_shannon', 'chi_square',
    'chebyshev', 'chebyshev_neg',
    'histogram_intersection_1',
    'relative_deviation', 'relative_bin_deviation',
    'noelle_1', 'noelle_3',
    'correlate_1']

all_func_medpy_histogram = metric_list + semi_metric_list + similarity_func + unknown_prop_list + still_under_dev

# need to figure out a way to set up tests over a fixed range
# arbitrary_length = np.random.randint(100, 1000)
# num_bins = np.random.randint(20, 200) # 100

arbitrary_length = np.random.randint(100, 1000)
num_bins = 20

def within_tolerance(x, y):
    "Function to indicate acceptable level of tolerance in numerical differences"

    return np.allclose(x, y, rtol=1e-3, atol=np.finfo(float).eps)

def make_random_histogram(length = arbitrary_length):
    "Returns a sequence of histogram density values that sum to 1.0"

    hist, bin_edges = np.histogram(np.random.random(arbitrary_length),
                                   bins = num_bins, density=True)

    if len(hist) < 2:
        raise ValueError('Invalid histogram')

    return hist

def test_indiscernibility_metric():

    h1 = make_random_histogram()

    for method_str in metric_list:
        method = getattr(histogram, method_str)
        is_indiscernible = within_tolerance(method(h1, h1), 0.0)
        assert is_indiscernible

def test_symmetry_metric():

    h1 = make_random_histogram()
    h2 = make_random_histogram()

    for method_str in metric_list:
        method = getattr(histogram, method_str)
        if method_str is 'kullback_leibler':
            # for KL div : h1 can only contain zero values where h2 also contains zero values and vice-versa
            h2[h1 == 0] = 0
            h1[h2 == 0] = 0

        d12 = method(h1, h2)
        d21 = method(h2, h1)
        if np.isnan(d12) or np.isnan(d21):
            print method_str
            print h1
            print h2
        assert within_tolerance(d12, d21)

def test_nonnegativity_metric():

    h1 = make_random_histogram()
    h2 = make_random_histogram()

    for method_str in metric_list:
        method = getattr(histogram, method_str)
        assert method(h1,h2) >= 0.0

def test_triangle_inequality_metric():

    h1 = make_random_histogram()
    h2 = make_random_histogram()
    h3 = make_random_histogram()

    for method_str in metric_list:
        method = getattr(histogram, method_str)
        if method_str is 'kullback_leibler':
            # for KL div : h1 can only contain zero values where h2 also contains zero values and vice-versa
            zeros_loc = np.logical_or(  h1 == 0, h2 == 0)
            zeros_loc = np.logical_or(zeros_loc, h3 == 0)
            h1[zeros_loc] = 0
            h2[zeros_loc] = 0
            h3[zeros_loc] = 0

        d12 = method(h1, h2)
        d23 = method(h2, h3)
        d13 = method(h1, h3)
        assert d12 <= d13 + d23

test_symmetry_metric()
test_indiscernibility_metric()