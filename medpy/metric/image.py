"""
@package medpy.metric.image
Provides a number of image distance and similarity measures.

@author Oskar Maier
@version r0.1.0
@since 2013-07-09
@status Release
"""

# build-in modules

# third-party modules
import numpy

# own modules
from medpy.core import ArgumentError

# code
def mutual_information(i1, i2, bins=256):
    """
    Computes the mutual information (MI) (a measure of entropy) between two images.

    MI is not real metric, but a symmetric and nonnegative similarity measures that
    takes high values for similar images. Negative values are also possible.
    
    Intuitively, mutual information measures the information that X and Y share: it
    measures how much knowing one of these variables reduces uncertainty about the other.
    
    The Entropy is defined as:
    \f[
        H(X) = - \sum_i p(g_i) * ln(p(g_i)
    \f]
    with \f$p(g_i)\f$ being the intensity probability of the images grey value \f$g_i\f$.
    
    Assuming two image R and T, the mutual information is then computed by comparing the
    images entropy values (i.e. a measure how well-structured the common histogram is).
    The distance metric is then calculated as follows:
    \f[
        MI(R,T) = H(R) + H(T) - H(R,T) = H(R) - H(R|T) = H(T) - H(T|R)
    \f]
    
    A maximization of the mutual information is equal to a minimization of the joint
    entropy.
    
    Note
    ----
    @see medpy.filter.ssd() for another image metric.
    
    @param i1 the first image
    @type i1 array-like sequence
    @param i2 the second image
    @type i2 array-like sequence
    @param bins the number of histogram bins (squared for the joined histogram)
    @type bins int
    
    @return the mutual information distance value
    @rtype float
    """
    # pre-process function arguments
    i1 = numpy.asarray(i1)
    i2 = numpy.asarray(i2)
    
    # validate function arguments
    if not i1.shape == i2.shape:
        raise ArgumentError('the two supplied array-like sequences i1 and i2 must be of the same shape')
    
    # compute i1 and i2 histogram range
    i1_range = __range(i1, bins)
    i2_range = __range(i2, bins)
    
    # compute joined and separated normed histograms
    i1i2_hist, _, _ = numpy.histogram2d(i1.flatten(), i2.flatten(), bins=bins, range=[i1_range, i2_range]) # Note: histogram2d does not flatten array on its own
    i1_hist, _ = numpy.histogram(i1, bins=bins, range=i1_range)
    i2_hist, _ = numpy.histogram(i2, bins=bins, range=i2_range)
    
    # compute joined and separated entropy
    i1i2_entropy = __entropy(i1i2_hist)
    i1_entropy = __entropy(i1_hist)
    i2_entropy = __entropy(i2_hist)
    
    # compute and return the mutual information distance
    return i1_entropy + i2_entropy - i1i2_entropy

def __range(a, bins):
    '''Compute the histogram range of the values in the array a according to
    scipy.stats.histogram.'''
    a = numpy.asarray(a)
    a_max = a.max()
    a_min = a.min()
    s = 0.5 * (a_max - a_min) / float(bins - 1)
    return (a_min - s, a_max + s)
 
def __entropy(data):
    '''Compute entropy of the flattened data set (e.g. a density distribution).'''
    # normalize and convert to float
    data = data/float(numpy.sum(data))
    # for each grey-value g with a probability p(g) = 0, the entropy is defined as 0, therefore we remove these values and also flatten the histogram
    data = data[numpy.nonzero(data)]
    # compute entropy
    return -1. * numpy.sum(data * numpy.log2(data))
    