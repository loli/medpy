"""
=====================================
Metric measures (:mod:`medpy.metric`)
=====================================
.. currentmodule:: medpy.metric

This package provides a number of metric measures that e.g. can be used for testing
and/or evaluation purposes on two binary masks (i.e. measuring their similarity) or
distance between histograms.

Binary metrics (:mod:`medpy.metric.binary`)
===========================================
Metrics to compare binary objects and classification results.

Compare two binary objects
**************************

.. module:: medpy.metric.binary

.. autosummary::
    :toctree: generated/

    dc
    jc
    hd
    asd
    assd
    precision
    recall
    sensitivity
    specificity
    true_positive_rate
    true_negative_rate
    positive_predictive_value
    ravd

Compare two sets of binary objects
**********************************

.. autosummary::
    :toctree: generated/

    obj_tpr
    obj_fpr
    obj_asd
    obj_assd

Compare to sequences of binary objects
**************************************

.. autosummary::
    :toctree: generated/

    volume_correlation
    volume_change_correlation

Image metrics (:mod:`medpy.metric.image`)
=========================================
Some more image metrics (e.g. `~medpy.filter.image.sls` and `~medpy.filter.image.ssd`)
can be found in :mod:`medpy.filter.image`.

.. module:: medpy.metric.image
.. autosummary::
    :toctree: generated/

    mutual_information

Histogram metrics (:mod:`medpy.metric.histogram`)
=================================================

.. module:: medpy.metric.histogram
.. autosummary::
    :toctree: generated/

    chebyshev
    chebyshev_neg
    chi_square
    correlate
    correlate_1
    cosine
    cosine_1
    cosine_2
    cosine_alt
    euclidean
    fidelity_based
    histogram_intersection
    histogram_intersection_1
    jensen_shannon
    kullback_leibler
    manhattan
    minowski
    noelle_1
    noelle_2
    noelle_3
    noelle_4
    noelle_5
    quadratic_forms
    relative_bin_deviation
    relative_deviation

"""

# Copyright (C) 2013 Oskar Maier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .binary import asd as asd
from .binary import assd as assd
from .binary import dc as dc
from .binary import hd as hd
from .binary import hd95 as hd95
from .binary import jc as jc
from .binary import obj_asd as obj_asd
from .binary import obj_assd as obj_assd
from .binary import obj_fpr as obj_fpr
from .binary import obj_tpr as obj_tpr
from .binary import positive_predictive_value as positive_predictive_value
from .binary import precision as precision
from .binary import ravd as ravd
from .binary import recall as recall
from .binary import sensitivity as sensitivity
from .binary import specificity as specificity
from .binary import true_negative_rate as true_negative_rate
from .binary import true_positive_rate as true_positive_rate
from .binary import volume_change_correlation as volume_change_correlation
from .binary import volume_correlation as volume_correlation
from .histogram import chebyshev as chebyshev
from .histogram import chebyshev_neg as chebyshev_neg
from .histogram import chi_square as chi_square
from .histogram import correlate as correlate
from .histogram import correlate_1 as correlate_1
from .histogram import cosine as cosine
from .histogram import cosine_1 as cosine_1
from .histogram import cosine_2 as cosine_2
from .histogram import cosine_alt as cosine_alt
from .histogram import euclidean as euclidean
from .histogram import fidelity_based as fidelity_based
from .histogram import histogram_intersection as histogram_intersection
from .histogram import histogram_intersection_1 as histogram_intersection_1
from .histogram import jensen_shannon as jensen_shannon
from .histogram import kullback_leibler as kullback_leibler
from .histogram import manhattan as manhattan
from .histogram import minowski as minowski
from .histogram import noelle_1 as noelle_1
from .histogram import noelle_2 as noelle_2
from .histogram import noelle_3 as noelle_3
from .histogram import noelle_4 as noelle_4
from .histogram import noelle_5 as noelle_5
from .histogram import quadratic_forms as quadratic_forms
from .histogram import relative_bin_deviation as relative_bin_deviation
from .histogram import relative_deviation as relative_deviation
from .image import mutual_information

__all__ = [
    "asd",
    "assd",
    "dc",
    "hd",
    "jc",
    "positive_predictive_value",
    "precision",
    "ravd",
    "recall",
    "sensitivity",
    "specificity",
    "true_negative_rate",
    "true_positive_rate",
    "hd95",
    "obj_asd",
    "obj_assd",
    "obj_fpr",
    "obj_tpr",
    "volume_change_correlation",
    "volume_correlation",
    "chebyshev",
    "chebyshev_neg",
    "chi_square",
    "correlate",
    "correlate_1",
    "cosine",
    "cosine_1",
    "cosine_2",
    "cosine_alt",
    "euclidean",
    "fidelity_based",
    "histogram_intersection",
    "histogram_intersection_1",
    "jensen_shannon",
    "kullback_leibler",
    "manhattan",
    "minowski",
    "noelle_1",
    "noelle_2",
    "noelle_3",
    "noelle_4",
    "noelle_5",
    "quadratic_forms",
    "relative_bin_deviation",
    "relative_deviation",
    "mutual_information",
]
