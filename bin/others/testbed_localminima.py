# DEVELOPMENT PUT ON HOLD
# This file constitutes the first and only try to implement reduction of the weight map for the watershed to k regional minima

import numpy
import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology
import scipy
from scipy.ndimage import measurements

def main():
    k = 5000
    a = scipy.asarray([[1,2,5,4],
                       [1,2,5,4],
                       [2,5,3,3],
                       [6,5,3,3]])
    a = scipy.random.randint(0, 100000, (100,100,50))
    
    minimas, labels = extracts_minima_areas(a)
    while len(minimas) > k:
        print(len(minimas))
        minimas = minimas[:-k]
        for minima in minimas:
            idx = minima[1]
            sl = minima[2]
            mask = labels[sl] == idx
            a[sl][mask] = max(a[sl].max(), a[sl][mask][0] + 1)
        minimas, labels = extracts_minima_areas(a)
    print(len(minimas))
    
def extracts_minima_areas(arr):
    neighborhood = morphology.generate_binary_structure(len(arr.shape),2)
    local_min = (filters.minimum_filter(arr, footprint=neighborhood)==arr)
    labels = measurements.label(local_min)[0]
    objects = measurements.find_objects(labels)
    areas_and_indices_and_bounding_boxes = []
    for idx, sl in enumerate(objects):
        areas_and_indices_and_bounding_boxes.append((len(arr[sl][labels[sl] == idx + 1]), idx + 1, sl)) # first area, then index, then bounding box
    return sorted(areas_and_indices_and_bounding_boxes), labels

def local_minima(fits, window=15):
    """
    Find the local minima within fits, and return them and their indices.

    Returns a list of indices at which the minima were found, and a list of the
    minima, sorted in order of increasing minimum.  The keyword argument window
    determines how close two local minima are allowed to be to one another.  If
    two local minima are found closer together than that, then the lowest of
    them is taken as the real minimum.  window=1 will return all local minima.

    """
    from scipy.ndimage.filters import minimum_filter as min_filter

    minfits = min_filter(fits, size=window, mode="wrap")

    minima = []
    for i in range(len(fits)):
        if fits[i] == minfits[i]:
            minima.append(fits[i])

    minima.sort()

    good_indices = [ fits.index(fit) for fit in minima ]
    good_fits = [ fit for fit in minima ]

    return(good_indices, good_fits)

def local_minima_fixed(fits, window=15):
    from scipy.ndimage.filters import minimum_filter as min_filter
    minfits = min_filter(fits, size=window, mode="wrap")
    minima_and_indices = []
    for i, (fit, minfit) in enumerate(zip(fits, minfits)):
        if fit == minfit:
            minima_and_indices.append([fit, i])
    minima_and_indices.sort()
    good_fits, good_indices = list(zip(*minima_and_indices))
    return good_indices, good_fits

def local_minima_fancy(fits, window=15):
    from scipy.ndimage import minimum_filter
    fits = numpy.asarray(fits)
    minfits = minimum_filter(fits, size=window, mode="wrap")
    minima_mask = fits == minfits
    good_indices = numpy.arange(len(fits))[minima_mask]
    good_fits = fits[minima_mask]
    order = good_fits.argsort()
    return good_indices[order], good_fits[order]

def detect_local_minima(arr):
    # http://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710
    """
    Takes an array and detects the troughs using the local maximum filter.
    Returns a boolean mask of the troughs (i.e. 1 when
    the pixel's value is the neighborhood maximum, 0 otherwise)
    """
    # define an connected neighborhood
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#generate_binary_structure
    neighborhood = morphology.generate_binary_structure(len(arr.shape),2)
    # apply the local minimum filter; all locations of minimum value 
    # in their neighborhood are set to 1
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters.html#minimum_filter
    local_min = (filters.minimum_filter(arr, footprint=neighborhood)==arr)
    print(local_min)
    # local_min is a mask that contains the peaks we are 
    # looking for, but also the background.
    # In order to isolate the peaks we must remove the background from the mask.
    # 
    # we create the mask of the background
    background = (arr==0)
    # 
    # a little technicality: we must erode the background in order to 
    # successfully subtract it from local_min, otherwise a line will 
    # appear along the background border (artifact of the local minimum filter)
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#binary_erosion
    eroded_background = morphology.binary_erosion(
        background, structure=neighborhood, border_value=1)
    # 
    # we obtain the final mask, containing only peaks, 
    # by removing the background from the local_min mask
    detected_minima = local_min - eroded_background
    return (detected_minima > 0)

if __name__ == "__main__":
    main()