"""
@package medpy.features.utilities
Utilities for feature handling.
Currently only for features from the @see medpy.features.intensity package.

@author Oskar Maier
@version r0.1.1
@since 2013-08-24
@status Release
"""

# build-in module

# third-party modules
import numpy

# own modules
def normalize(vector, cutoffp = (0, 100), model = False):
    """
    Returns a feature-wise normalized version of the supplied vector. Normalization is
    achieved to [0,1] over the complete vector using shifting and scaling.
    
    When cut-off percentile (cutoffp) values other than (0, 100) are supplied, the values
    lying before or behind the supplied percentiles are cut-off i.e. shifted to fit the
    range. 
    
    When model is set to True, an additional model describing the normalization is
    returned, that can at a later point be passed to the normalized_with_model function
    to normalize other feature vectors accordingly to the one passed.
    
    The vector is expected to have the form samples*features i.e.
        s1    s2    s3    [...]
    f1
    f2
    [...]
    
    Therefore a supplied vector
        s1    s2    s3
    f1   1.5    1    2
    f2    -1    0    1
    
    . would result in the returned vector
        s1    s2    s3
    f1 0.50  0.00  1.00
    f2 0.00  0.50  1.00
    
    @param vector a vector of feature vectors
    @type vector sequence
    
    @return the normalized version of the input vector
    @rtype ndarray
    """
    vector = numpy.array(vector, dtype=numpy.float)
    
    # add a singleton dimension if required
    if 1 == vector.ndim:
        vector = vector[:, None]
    
    # compute lower and upper range border of each row using the supplied percentiles
    minp, maxp = numpy.percentile(vector, cutoffp, 0)
    
    # shift outliers to fit range
    for i in xrange(vector.shape[1]):
        vector[:,i][vector[:,i] < minp[i]] = minp[i]
        vector[:,i][vector[:,i] > maxp[i]] = maxp[i]
    
    # normalize
    minv = vector.min(0)
    vector -= minv
    maxv = vector.max(0)
    vector /= maxv
    
    if not model:
        return vector
    else:
        return vector, (minp, maxp, minv, maxv)
    
def normalize_with_model(vector, model):
    """
    Normalize as with @see normalize(), but not based on the data of the passed feature
    vector, but rather on a learned model created with @see normalize(). Thus formerly
    unseen query data can be normalized according to the training data.
    """
    vector = numpy.array(vector, dtype=numpy.float)
    
    # unpack model
    minp, maxp, minv, maxv = model
    
    # add a singleton dimension if required
    if 1 == vector.ndim:
        vector = vector[:, None]
    
    # shift outliers to fit range
    for i in xrange(vector.shape[1]):
        vector[:,i][vector[:,i] < minp[i]] = minp[i]
        vector[:,i][vector[:,i] > maxp[i]] = maxp[i]
        
    # normalize
    vector -= minv
    vector /= maxv
    
    return vector        

def append(*vectors):
    """
    Takes an arbitrary number of vectors containing features and append them
    (horizontally).
    
    E.g. taking a 100 and a 200 sample vector with 7 features each, a 300x7
    vector is returned.
    
    The vectors are expected to have the form samples*features i.e.
        s1    s2    s3    [...]
    f1
    f2
    [...]
    
    @param *vectors a number of vectors with the same number and type of features
    @type *vectors sequences
    
    @return the appended vectors
    @rtype ndarray
    """
    # check supplied arguments
    if len(vectors) < 2:
        return vectors[0]
    
    # process supplied arguments
    vectors = list(vectors)
    for i in xrange(len(vectors)):
        vectors[i] = numpy.asarray(vectors[i])
        if vectors[i].ndim == 1:
            vectors[i] = numpy.asarray([vectors[i]]).T

    return numpy.squeeze(numpy.concatenate(vectors, 0))
    
def join(*vectors):
    """
    Takes an arbitrary number of aligned vectors of the same length and combines
    them into a single vector (vertically).
    
    E.g. taking two 100-sample feature vectors of once 5 and once 7 features, a 100x12
    feature vector is created and returned. 
    
    The feature vectors are expected to have the form samples*features i.e.
        s1    s2    s3    [...]
    f1
    f2
    [...]
    
    @param *vectors a number of vectors with the same number of samples
    @type *vectors sequences
    
    @return the combined vector
    @rtype ndarray
    """
    # check supplied arguments
    if len(vectors) < 2:
        return vectors[0]

    # process supplied arguments
    vectors = list(vectors)
    for i in range(len(vectors)):
        vectors[i] = numpy.array(vectors[i], copy=False)
        if vectors[i].ndim == 1:
            vectors[i] = numpy.array([vectors[i]], copy=False).T
    
    # treat single-value cases special (no squeezing)
    if 1 == len(vectors[0]):
        return numpy.concatenate(vectors, 1)
    
    return numpy.squeeze(numpy.concatenate(vectors, 1))
