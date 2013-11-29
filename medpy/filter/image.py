"""
@package medpy.filter.image
Filters for multi-dimensional images.

These filter rely heavily on and are modeled after the scipy.ndimage package.

@author Oskar Maier
@version d0.1.0
@since 2013-11-29
@status Development
"""

# build-in module

# third-party modules
import numpy
from scipy.ndimage.filters import convolve
from scipy.ndimage._ni_support import _normalize_sequence, _get_output

# own modules

# code
def average_filter(input, size=None, footprint=None, output=None, mode="reflect", cval=0.0, origin=0):
    """
    Calculates a multi-dimensional average filter.

    Parameters
    ----------
    input : array-like
        input array to filter
    size : scalar or tuple, optional
        See footprint, below
    footprint : array, optional
        Either `size` or `footprint` must be defined. `size` gives
        the shape that is taken from the input array, at every element
        position, to define the input to the filter function.
        `footprint` is a boolean array that specifies (implicitly) a
        shape, but also which of the elements within this shape will get
        passed to the filter function. Thus ``size=(n,m)`` is equivalent
        to ``footprint=np.ones((n,m))``. We adjust `size` to the number
        of dimensions of the input array, so that, if the input array is
        shape (10,10,10), and `size` is 2, then the actual size used is
        (2,2,2).
    output : array, optional
        The ``output`` parameter passes an array in which to store the
        filter output.
    mode : {'reflect','constant','nearest','mirror', 'wrap'}, optional
        The ``mode`` parameter determines how the array borders are
        handled, where ``cval`` is the value when mode is equal to
        'constant'. Default is 'reflect'
    cval : scalar, optional
        Value to fill past edges of input if ``mode`` is 'constant'. Default
        is 0.0
    origin : scalar, optional
        The ``origin`` parameter controls the placement of the filter.
        Default 0

    Returns
    -------
    average_filter : ndarray
        Returned array of same shape as `input`.

    Notes
    -----
    Convenience implementation employing convolve.

    See Also
    --------
    convolve : Convolve an image with a kernel.
    """
    if footprint is None:
            if size is None:
                raise RuntimeError("no footprint or filter size provided")
            sizes = _normalize_sequence(size, input.ndim)
            footprint = numpy.ones(sizes, dtype=bool)
    else:
            footprint = numpy.asarray(footprint, dtype=bool)
    
    filter_size = numpy.where(footprint, 1, 0).sum()
    
    output, return_value = _get_output(output, input)
    convolve(input, footprint, output, mode, cval, origin)
    output /= float(filter_size)
    return return_value


def sum_filter(input, size=None, footprint=None, output=None, mode="reflect", cval=0.0, origin=0):
    """
    Calculates a multi-dimensional sum filter.

    Parameters
    ----------
    input : array-like
        input array to filter
    size : scalar or tuple, optional
        See footprint, below
    footprint : array, optional
        Either `size` or `footprint` must be defined. `size` gives
        the shape that is taken from the input array, at every element
        position, to define the input to the filter function.
        `footprint` is a boolean array that specifies (implicitly) a
        shape, but also which of the elements within this shape will get
        passed to the filter function. Thus ``size=(n,m)`` is equivalent
        to ``footprint=np.ones((n,m))``. We adjust `size` to the number
        of dimensions of the input array, so that, if the input array is
        shape (10,10,10), and `size` is 2, then the actual size used is
        (2,2,2).
    output : array, optional
        The ``output`` parameter passes an array in which to store the
        filter output.
    mode : {'reflect','constant','nearest','mirror', 'wrap'}, optional
        The ``mode`` parameter determines how the array borders are
        handled, where ``cval`` is the value when mode is equal to
        'constant'. Default is 'reflect'
    cval : scalar, optional
        Value to fill past edges of input if ``mode`` is 'constant'. Default
        is 0.0
    origin : scalar, optional
        The ``origin`` parameter controls the placement of the filter.
        Default 0

    Returns
    -------
    sum_filter : ndarray
        Returned array of same shape as `input`.

    Notes
    -----
    Convenience implementation employing convolve.

    See Also
    --------
    convolve : Convolve an image with a kernel.
    """
    if footprint is None:
            if size is None:
                raise RuntimeError("no footprint or filter size provided")
            size = _normalize_sequence(size, input.ndim)
            footprint = numpy.ones(size, dtype=bool)
    else:
            footprint = numpy.asarray(footprint, dtype=bool)
            
    return convolve(input, footprint, output, mode, cval, origin)
