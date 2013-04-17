"""
@package medpy.metric
Metric measures.

Provides a number of metric measures that e.g. can be used for testing and/or evaluation
purposes on two binary masks (i.e. measuring their similarity) or distance between
histograms.

Modules:
    - Surface: Holds a class to compute and extract surface similarities as used in (1).
    - Volume: Holds a class to compute and extract volume similarities as used in (1).
    - Histogram: Holds a number of real or near histogram distance metrics.

(1) The MICCAI 2997 Grand Challenge: Heimann T. et al. / "Comparison and Evaluation of
Methods for Liver Segmentation From CT Datasets" / IEEE Transactions on Medical Imaging,
Vol.28, No.8, August 2009
"""

# determines the modules that should be imported when "from metric import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from surface import Surface
from volume import Volume
from histogram import *