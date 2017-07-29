"""
Unittest for medpy.metric.histogram

@author Pradeep Reddy Raamana
"""

import unittest
import numpy as np
from pytest import raises, warns, set_trace

from medpy.metric import histogram

metric_list_medpy_histogram = [
    'kullback_leibler', 'manhattan', 'minowski', 'euclidean',
    'correlate', 'fidelity_based', 'quadratic_forms',
    'cosine', 'cosine_1', 'cosine_2', 'cosine_alt',
    'noelle_2', 'noelle_4', 'noelle_5' ]

unknown_medpy_histogram = ['histogram_intersection', ]

semi_metric_list_medpy_histogram = [
    'jensen_shannon', 'chi_square',
    'chebyshev', 'chebyshev_neg',
    'histogram_intersection_1',
    'relative_deviation', 'relative_bin_deviation',
    'noelle_1', 'noelle_3',
    'correlate_1']

all_func_medpy_histogram = metric_list_medpy_histogram + semi_metric_list_medpy_histogram + unknown_medpy_histogram

arbitrary_length = np.random.randint(1000)
num_bins = 100

def make_random_histogram(length = arbitrary_length):
    "Returns a sequence of histogram density values that sum to 1.0"

    hist, bin_edges = np.histogram(np.random.random(arbitrary_length),
                                   bins = num_bins, density=True)
    return hist

def test_indiscernibility_metric():

    h1 = make_random_histogram()

    for method_str in metric_list_medpy_histogram:
        method = getattr(histogram, method_str)
        assert np.allclose(method(h1, h1), 0.0, atol= np.finfo(float).eps)

def test_symmetry_metric():

    h1 = make_random_histogram()
    h2 = make_random_histogram()

    for method_str in metric_list_medpy_histogram:
        method = getattr(histogram, method_str)
        assert np.allclose(method(h1, h2), method(h2, h1), atol= np.finfo(float).eps)

def test_nonnegativity_metric():

    h1 = make_random_histogram()
    h2 = make_random_histogram()

    for method_str in metric_list_medpy_histogram:
        method = getattr(histogram, method_str)
        assert method(h1,h2) >= 0.0

def test_triangle_inequality_metric():

    h1 = make_random_histogram()
    h2 = make_random_histogram()
    h3 = make_random_histogram()

    for method_str in metric_list_medpy_histogram:
        method = getattr(histogram, method_str)
        d12 = method(h1, h2)
        d23 = method(h2, h3)
        d13 = method(h1, h3)
        assert d12 <= d13 + d23


test_indiscernibility_metric()