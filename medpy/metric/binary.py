"""
@package medpy.metric.binary
Provides a number of binary image distance measures.

@author Oskar Maier
@version r0.1.0
@since 2014-03-13
@status Release
"""

# build-in modules

# third-party modules
import numpy
from scipy.ndimage import _ni_support
from scipy.ndimage.morphology import distance_transform_edt, binary_erosion,\
    generate_binary_structure

# own modules

# code
def dc(input1, input2):
    """
    Dice coefficient
    
    Computes the Dice coefficient (also known as Sorensen index) between the binary
    objects in two images.
    
    The metric is defined as
    
    .. math::
        
        DC = \frac{2|A\capB|}{|A|+|B|}
        
    , where A is the first and B the second set of samples (here binary objects).
    
    Parameters
    ----------
    input1: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    
    Returns
    -------
    dc: float
        The Dice coefficient between the object(s) in `input1` and the
        object(s) in `input2`. It ranges from 0 (no overlap) to 1 (perfect overlap).
        
    Notes
    -----
    This is a real metric.
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
    
    intersection = numpy.count_nonzero(input1 & input2)
    
    size_i1 = numpy.count_nonzero(input1)
    size_i2 = numpy.count_nonzero(input2)
    
    try:
        dc = 2. * intersection / float(size_i1 + size_i2)
    except ZeroDivisionError:
        dc = 0.0
    
    return dc


def precision(input1, input2):
    """
    Precison.
    In case of evaluation, pass the ground truth as second and the classification results
    as first argument.
    
    Parameters
    ----------
    input1: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    
    Returns
    -------
    precision: float
        The precision between two binary datasets, here mostly binary objects in images,
        which is defined as the fraction of retrieved instances that are relevant. The
        precision is not symmetric.
    
    See also
    --------
    :func:`recall`
    
    Note
    ----
    Not symmetric. The inverse of the precision is :func:`recall`.
    High precision means that an algorithm returned substantially more relevant results than irrelevant.
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
        
    tp = numpy.count_nonzero(input1 & input2)
    fp = numpy.count_nonzero(input1 & ~input2)
    
    try:
        precision = tp / float(tp + fp)
    except ZeroDivisionError:
        precision = 0.0
    
    return precision

def recall(input1, input2):
    """
    Recall.
    In case of evaluation, pass the ground truth as second and the classification results
    as first argument.
    
    Parameters
    ----------
    input1: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    
    Returns
    -------
    recall: float
        The recall between two binary datasets, here mostly binary objects in images,
        which is defined as tthe fraction of relevant instances that are retrieved. The
        recall is not symmetric.
    
    while recall (also known as sensitivity) is the fraction of relevant instances that are retrieved.
    In simple terms, high precision means that an algorithm returned substantially more relevant results than irrelevant, while high recall means that an algorithm returned most of the relevant results.
    
    See also
    --------
    :func:`precision`
    
    Note
    ----
    Not symmetric. The inverse of the recall is :func:`precision`.
    High recall means that an algorithm returned most of the relevant results.
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
        
    tp = numpy.count_nonzero(input1 & input2)
    fn = numpy.count_nonzero(~input1 & input2)

    try:
        recall = tp / float(tp + fn)
    except ZeroDivisionError:
        recall = 0.0
    
    return recall

def hd(input1, input2, voxelspacing=None, connectivity=1):
    """
    Hausdorff Distance.
    
    Computes the (symmetric) Hausdorff Distance (HD) between the binary objects in two
    images. It is defined as the maximum surface distance between the objects.
    
    Parameters
    ----------
    input1: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing: float or int, or sequence of same, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity: int
        The neighbourhood/connectivity considered when determining the surface
        of the binary objects. This value is passed to
        scipy.ndimage.morphology.generate_binary_structure and should usually be > 1.
        Presumably does not influence the result in the case of the Hausdorff distance.
        
    Returns
    -------
    hd: float
        The symmetric Hausdorff Distance between the object(s) in `input1` and the
        object(s) in `input2`. The distance unit is the same as for the spacing of 
        elements along each dimension, which is usually given in mm.
        
    See also
    --------
    :func:`assd`
    :func:`asd`
    
    Notes
    -----
    This is a real metric.
    """
    hd1 = __surface_distances(input1, input2, voxelspacing, connectivity).max()
    hd2 = __surface_distances(input2, input1, voxelspacing, connectivity).max()
    hd = max(hd1, hd2)
    return hd

def assd(input1, input2, voxelspacing=None, connectivity=1):
    """
    Average symmetric surface distance.
    
    Computes the average symmetric surface distance (ASD) between the binary objects in
    two images.
    
    Parameters
    ----------
    input1: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing: float or int, or sequence of same, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity: int
        The neighbourhood/connectivity considered when determining the surface
        of the binary objects. This value is passed to
        scipy.ndimage.morphology.generate_binary_structure and should usually be > 1.
        The decision on the connectivity is important, as it can influence the results
        strong. If in doubt, leave it as it is.         
        
    Returns
    -------
    assd: float
        The average symmetric surface distance between the object(s) in `input1` and the
        object(s) in `input2`. The distance unit is the same as for the spacing of 
        elements along each dimension, which is usually given in mm.
        
    See also
    --------
    :func:`asd`
    :func:`hd`
    
    Notes
    -----
    This is a real metric, obtained by calling and averaging
    >>>> asd(input1, input2)
    and
    >>>> asd(input2, input1)
    """
    assd = numpy.mean( (asd(input1, input2, voxelspacing, connectivity), asd(input2, input1, voxelspacing, connectivity)) )
    return assd

def asd(input1, input2, voxelspacing=None, connectivity=1):
    """
    Average surface distance metric.
    
    Computes the average surface distance (ASD) between the binary objects in two images.
    
    Parameters
    ----------
    input1: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2: array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing: float or int, or sequence of same, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity: int
        The neighbourhood/connectivity considered when determining the surface
        of the binary objects. This value is passed to
        scipy.ndimage.morphology.generate_binary_structure and should usually be > 1.
        The decision on the connectivity is important, as it can influence the results
        strong. If in doubt, leave it as it is.        
    
    Returns
    -------
    asd: float
        The average surface distance between the object(s) in `input1` and the
        object(s) in `input2`. The distance unit is the same as for the spacing
        of elements along each dimension, which is usually given in mm.
        
    See also
    --------
    :func:`assd`
    :func:`hd`
    
    
    Notes
    -----
    This is not a real metric, as it is directed. See `assd` for a real metric of this.
    
    The method is implemented making use of distance images and simple binary morphology
    to achieve high computational speed.
    
    Examples
    --------
    The `connectivity` determines what pixels/voxels are considered the surface of a
    binary object. Take the following binary image showing a cross
    >>> from scipy.ndimage.morphology import generate_binary_structure
    >>> cross = generate_binary_structure(2, 1)
    array([[0, 1, 0],
           [1, 1, 1],
           [0, 1, 0]])
    With `connectivity` set to `1` a 4-neighbourhood is considered when determining the
    object surface, resulting in
    array([[0, 1, 0],
           [1, 0, 1],
           [0, 1, 0]])
    Changing `connectivity` to `2`, a 8-neighbourhood is considered and we get:
    array([[0, 1, 0],
           [1, 1, 1],
           [0, 1, 0]])
    , as a diagonal connection does no longer qualifies as valid object surface.
    
    This influences the  results `asd` returns. Imagine we want to compute the surface
    distance of our cross to a cube-like object:
    >>>> cube = generate_binary_structure(2, 1)
    array([[1, 1, 1],
           [1, 1, 1],
           [1, 1, 1]])
    , which surface is, independent of the `connectivity` value set, always
    array([[1, 1, 1],
           [1, 0, 1],
           [1, 1, 1]])
           
    Using a `connectivity` of `1` we get
    >>>> asd(cross, cube, connectivity=1)
    0.0
    while a value of `2` returns uns
    >>>> asd(cross, cube, connectivity=2)
    0.20000000000000001
    due to the center of the cross being considered surface as well.
    
    """
    sds = __surface_distances(input1, input2, voxelspacing, connectivity)
    asd = sds.mean()
    return asd
    
def __surface_distances(input1, input2, voxelspacing=None, connectivity=1):
    """
    The distances between the surface voxel of binary objects in input1 and their
    nearest partner surface voxel of a binary object in input2.
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
    if voxelspacing is not None:
        voxelspacing = _ni_support._normalize_sequence(voxelspacing, input1.ndim)
        voxelspacing = numpy.asarray(voxelspacing, dtype=numpy.float64)
        if not voxelspacing.flags.contiguous:
            voxelspacing = voxelspacing.copy()
            
    # binary structure
    footprint = generate_binary_structure(input1.ndim, connectivity)
    
    # test for emptyness
    if 0 == numpy.count_nonzero(input1): 
        raise RuntimeError('The first supplied image does not contain any binary object.')
    if 0 == numpy.count_nonzero(input2): 
        raise RuntimeError('The second supplied image does not contain any binary object.')    
            
    # extract only 1-pixel border line of objects
    input1_border = input1 - binary_erosion(input1, structure=footprint, iterations=1)
    input2_border = input2 - binary_erosion(input2, structure=footprint, iterations=1)
    
    # compute average surface distance        
    # Note: scipys distance transform is calculated only inside the borders of the
    #       foreground objects, therefore the input has to be reversed
    dt = distance_transform_edt(~input2_border, sampling=voxelspacing)
    sds = dt[input1_border]
    
    return sds    