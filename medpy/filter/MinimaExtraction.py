#!/usr/bin/python

"""A function to extract the local minima from an array."""

# build-in modules

# third-party modules
import numpy
import scipy.ndimage

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "d0.1, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = "Function to extract the local minima from an array."

# code
def local_minima(ar, min_distance = 4):
    """
    Returns all local minima from an array.
    @param ar: The original array
    @param min_distance: The minimal distance between the minimas. If it is less, only the lower minima is returned.
    @return: (array of indices, array of values) of the local minima found.
    """
    # @TODO: Write a unittest for this.
    fits = numpy.asarray(ar)
    minfits = scipy.ndimage.minimum_filter(fits, size=min_distance) # default mode is reflect
    minima_mask = fits == minfits
    good_indices = numpy.transpose(minima_mask.nonzero())
    good_fits = fits[minima_mask]
    order = good_fits.argsort()
    return good_indices[order], good_fits[order]