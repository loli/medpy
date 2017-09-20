"""
@package medpy.application.miccai12.core
Some helper functions developed for the MICCAI'12 challenge, that could also be used
otherwise.

Functions:
    - def xd_iterator(arr, view, fun): Iterate over a subview of the array

@author Oskar Maier
@version d0.1.0
@since 2012-06-21
@status Development
"""

# build-in module
import itertools
import multiprocessing

# third-party modules
import scipy

# own modules

# code
def xd_iterator_pool(arr, view, fun, processes = None):
    """
    Same as xd_iterator, but distributes the execution over 'processes' subprocesses.
    """
    # check parameters
    for dim in view:
        if dim >= arr.ndim or 0 > dim or not type(dim) == int: raise AttributeError('Invalid dimension {} in view. Must be int between 0 and {}.'.format(dim, arr.ndim - 1))
    if len(view) >= arr.ndim:
        raise AttributeError('The view should contain less entries than the array dimensionality.')
    
    # prepare worker pool    
    worker_pool = multiprocessing.Pool(processes)
    
    # create list of iterations
    iterations = [[None] if dim in view else list(range(arr.shape[dim])) for dim in range(arr.ndim)]
    
    # prepare views on array (subvolumes)
    slicers = [[slice(None) if idx is None else slice(idx, idx + 1) for idx in indices] for indices in itertools.product(*iterations)]
    reference_shape = arr[slicers[0]].shape
    subvolumes = [scipy.squeeze(arr[slicer]) for slicer in slicers]
        
    # excecute subprocesses
    result_subvolumes = worker_pool.map(fun, subvolumes)
    
    for slicer, result_subvolume in zip(slicers, result_subvolumes):
        arr[slicer] = result_subvolume.reshape(reference_shape)

def xd_iterator_add(arr, view, fun, add):
    """
    Same as xd_iterator, but expects an additional argument which is passed to each call
    of fun and expected to be returned as second return value.
    """
    # check parameters
    for dim in view:
        if dim >= arr.ndim or 0 > dim or not type(dim) == int: raise AttributeError('Invalid dimension {} in view. Must be int between 0 and {}.'.format(dim, arr.ndim - 1))
    if len(view) >= arr.ndim:
        raise AttributeError('The view should contain less entries than the array dimensionality.')
    
    # create list of iterations
    iterations = [[None] if dim in view else list(range(arr.shape[dim])) for dim in range(arr.ndim)]
     
    # iterate, create slicer, execute function and collect results
    for indices in itertools.product(*iterations):
        slicer = [slice(None) if idx is None else slice(idx, idx + 1) for idx in indices]
        _tmp, add = fun(scipy.squeeze(arr[slicer]), add)
        arr[slicer] = _tmp.reshape(arr[slicer].shape)
        
def xd_iterator(arr, view, fun):
    """
    Iterates over arr, slicing it into views over the dimensions provided in view and
    passes the extracted subvolumes to fun.
    Fun has to return an array of the same shape as it receives. This return array is
    then used to update the original array arr in-place.
    
    Example:
        Assuming an array of shape arr.shape = (100, 200, 300), we want to iterate over
        all 2D slices of the first two dimensions, i.e. iterate over the 3rd dimension
        and getting 300 slices of shape (100, 200) passed to the function fun. So we
        have to provide in view the dimensions over which we do not want to iterate, i.e.
        in this case view = [0,1].
    """
    # check parameters
    for dim in view:
        if dim >= arr.ndim or 0 > dim or not type(dim) == int: raise AttributeError('Invalid dimension {} in view. Must be int between 0 and {}.'.format(dim, arr.ndim - 1))
    if len(view) >= arr.ndim:
        raise AttributeError('The view should contain less entries than the array dimensionality.')
    
    # create list of iterations
    iterations = [[None] if dim in view else list(range(arr.shape[dim])) for dim in range(arr.ndim)]
     
    # iterate, create slicer, execute function and collect results
    for indices in itertools.product(*iterations):
        slicer = [slice(None) if idx is None else slice(idx, idx + 1) for idx in indices]
        arr[slicer] = fun(scipy.squeeze(arr[slicer])).reshape(arr[slicer].shape)

    