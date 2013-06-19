"""
@package medpy.filter.otsu
Implementation of the Otsu's method to fin the optimal threshold separating an image into
fore- and background.
    
See http://en.wikipedia.org/wiki/Otsu%27s_method and
http://www.labbookpages.co.uk/software/imgProc/otsuThreshold.html for more
information on the subject.

@author Oskar Maier
@version d0.1.1
@since 2013-06-19
@status Release
"""

# build-in modules
import math

# third-party modules
import scipy

# own modules

# public methods
def otsu (img, bins=64):
    """
    Implementation of the Otsu's method to fin the optimal threshold separating an image into
    fore- and background.
    
    This rather expensive method iterates over a number of thresholds to separate the
    images histogram into two parts with a minimal intra-class variance.
    
    An increase in the number of bins increases the algorithms specificity at the cost of
    slowing it down.
    
    @param img the image for which to determine the threshold
    @type img numpy.ndarray
    @param bins an integer determining the number of histogram bins
    @type bins int
    
    @return the otsu threshold
    @rtype number
    """
    # cast bins parameter to int
    bins = int(bins)
    
    # cast img parameter to scipy arrax
    img = scipy.asarray(img)
    
    # check supplied parameters
    if bins <= 1:
        raise AttributeError('At least a number two bins have to be provided.')
    
    # determine initial threshold and threshold step-length
    steplength = (img.max() - img.min()) / float(bins)
    initial_threshold = img.min() + steplength
    
    # initialize best value variables
    best_bcv = 0
    best_threshold = initial_threshold
    
    # iterate over the thresholds and find highest between class variance
    for threshold in scipy.arange(initial_threshold, img.max(), steplength):
        mask_fg = (img >= threshold)
        mask_bg = (img < threshold)
        
        wfg = scipy.count_nonzero(mask_fg)
        wbg = scipy.count_nonzero(mask_bg)
        
        if 0 == wfg or 0 == wbg: continue
        
        mfg = img[mask_fg].mean()
        mbg = img[mask_bg].mean()
        
        bcv = wfg * wbg * math.pow(mbg - mfg, 2)
        
        if bcv > best_bcv:
            best_bcv = bcv
            best_threshold = threshold
        
    return best_threshold
