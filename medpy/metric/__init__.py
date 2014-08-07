"""
@package medpy.metric
Metric measures.

Provides a number of metric measures that e.g. can be used for testing and/or evaluation
purposes on two binary masks (i.e. measuring their similarity) or distance between
histograms.

Modules:
    - surface: Holds a class to compute and extract surface similarities as used in (1).
    - volume: Holds a class to compute and extract volume similarities as used in (1).
    - histogram: Holds a number of real or near histogram distance metrics.
    - image: Metrics computed directly on the image intensities.
    - binary: Metrics to compare binary objects in images.

(1) The MICCAI 2997 Grand Challenge: Heimann T. et al. / "Comparison and Evaluation of
Methods for Liver Segmentation From CT Datasets" / IEEE Transactions on Medical Imaging,
Vol.28, No.8, August 2009
"""

# determines the modules that should be imported when "from metric import *" is used
__all__ = []

# if __all__ is not set, only the following, explicit import statements are executed
from binary import dc, hd, asd, assd, precision, recall, ravd, obj_tpr, obj_fpr, obj_asd, obj_assd
from surface import Surface
from volume import Volume
from histogram import *
from image import mutual_information