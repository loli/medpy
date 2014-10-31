# Copyright (C) 2013 Oskar Maier
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Oskar Maier
# version r0.1.1
# since 2014-03-13
# status Release

# build-in modules

# third-party modules
import numpy
from scipy.ndimage import _ni_support
from scipy.ndimage.morphology import distance_transform_edt, binary_erosion,\
    generate_binary_structure
from scipy.ndimage.measurements import label, find_objects    

# own modules

# code
def dc(input1, input2):
    r"""
    Dice coefficient
    
    Computes the Dice coefficient (also known as Sorensen index) between the binary
    objects in two images.
    
    The metric is defined as
    
    .. math::
        
        DC=\frac{2|A\cap B|}{|A|+|B|}
        
    , where :math:`A` is the first and :math:`B` the second set of samples (here: binary objects).
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    
    Returns
    -------
    dc : float
        The Dice coefficient between the object(s) in ```input1``` and the
        object(s) in ```input2```. It ranges from 0 (no overlap) to 1 (perfect overlap).
        
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

def jc(input1, input2):
    """
    Jaccard coefficient
    
    Computes the Jaccard coefficient between the binary objects in two images.
    
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
    jc: float
        The Jaccard coefficient between the object(s) in `input1` and the
        object(s) in `input2`. It ranges from 0 (no overlap) to 1 (perfect overlap).
    
    Notes
    -----
    This is a real metric.
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
    
    intersection = numpy.count_nonzero(input1 & input2)
    union = numpy.count_nonzero(input1 | input2)
    
    jc = float(intersection) / float(union)
    
    return jc

def precision(input1, input2):
    """
    Precison.
    In case of evaluation, pass the ground truth as second and the classification results
    as first argument.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    
    Returns
    -------
    precision : float
        The precision between two binary datasets, here mostly binary objects in images,
        which is defined as the fraction of retrieved instances that are relevant. The
        precision is not symmetric.
    
    See also
    --------
    :func:`recall`
    
    Notes
    -----
    Not symmetric. The inverse of the precision is :func:`recall`.
    High precision means that an algorithm returned substantially more relevant results than irrelevant.
    
    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Precision_and_recall
    .. [2] http://en.wikipedia.org/wiki/Confusion_matrix#Table_of_confusion
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
    Recall (or sensitivity).
    In case of evaluation, pass the ground truth as second and the classification results
    as first argument.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    
    Returns
    -------
    recall : float
        The recall between two binary datasets, here mostly binary objects in images,
        which is defined as the fraction of relevant instances that are retrieved. The
        recall is not symmetric.
    
    See also
    --------
    :func:`precision`
    
    Notes
    -----
    Not symmetric. The inverse of the recall is :func:`precision`.
    High recall means that an algorithm returned most of the relevant results.
    
    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Precision_and_recall
    .. [2] http://en.wikipedia.org/wiki/Confusion_matrix#Table_of_confusion
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
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing : float or sequence of floats, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity : int
        The neighbourhood/connectivity considered when determining the surface
        of the binary objects. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        Presumably does not influence the result in the case of the Hausdorff distance.
        
    Returns
    -------
    hd : float
        The symmetric Hausdorff Distance between the object(s) in ```input1``` and the
        object(s) in ```input2```. The distance unit is the same as for the spacing of 
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
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing : float or sequence of floats, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity : int
        The neighbourhood/connectivity considered when determining the surface
        of the binary objects. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        The decision on the connectivity is important, as it can influence the results
        strongly. If in doubt, leave it as it is.         
        
    Returns
    -------
    assd : float
        The average symmetric surface distance between the object(s) in ``input1`` and the
        object(s) in ``input2``. The distance unit is the same as for the spacing of 
        elements along each dimension, which is usually given in mm.
        
    See also
    --------
    :func:`asd`
    :func:`hd`
    
    Notes
    -----
    This is a real metric, obtained by calling and averaging
    
    >>> asd(input1, input2)
    
    and
    
    >>> asd(input2, input1)
    
    """
    assd = numpy.mean( (asd(input1, input2, voxelspacing, connectivity), asd(input2, input1, voxelspacing, connectivity)) )
    return assd

def asd(input1, input2, voxelspacing=None, connectivity=1):
    """
    Average surface distance metric.
    
    Computes the average surface distance (ASD) between the binary objects in two images.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing : float or sequence of floats, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity : int
        The neighbourhood/connectivity considered when determining the surface
        of the binary objects. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        The decision on the connectivity is important, as it can influence the results
        strongly. If in doubt, leave it as it is.
    
    Returns
    -------
    asd : float
        The average surface distance between the object(s) in ``input1`` and the
        object(s) in ``input2``. The distance unit is the same as for the spacing
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
    object surface, resulting in the surface
    
    .. code-block:: python
    
        array([[0, 1, 0],
               [1, 0, 1],
               [0, 1, 0]])
           
    Changing `connectivity` to `2`, a 8-neighbourhood is considered and we get:
    
    .. code-block:: python
    
        array([[0, 1, 0],
               [1, 1, 1],
               [0, 1, 0]])
           
    , as a diagonal connection does no longer qualifies as valid object surface.
    
    This influences the  results `asd` returns. Imagine we want to compute the surface
    distance of our cross to a cube-like object:
    
    >>> cube = generate_binary_structure(2, 1)
    array([[1, 1, 1],
           [1, 1, 1],
           [1, 1, 1]])
           
    , which surface is, independent of the `connectivity` value set, always
    
    .. code-block:: python
    
        array([[1, 1, 1],
               [1, 0, 1],
               [1, 1, 1]])
           
    Using a `connectivity` of `1` we get
    
    >>> asd(cross, cube, connectivity=1)
    0.0
    
    while a value of `2` returns us
    
    >>> asd(cross, cube, connectivity=2)
    0.20000000000000001
    
    due to the center of the cross being considered surface as well.
    
    """
    sds = __surface_distances(input1, input2, voxelspacing, connectivity)
    asd = sds.mean()
    return asd

def ravd(input1, input2):
    """
    Relative absolute volume difference.
    
    Compute the relative absolute volume difference between the (joined) binary objects
    in the two images.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
        
    Returns
    -------
    ravd : float
        The relative absolute volume difference between the object(s) in ``input1``
        and the object(s) in ``input2``. This is a percentage value in the range
        :math:`[-1.0, +inf]` for which a :math:`0` denotes an ideal score.
        
    Raises
    ------
    RuntimeError
        If the reference object is empty.
        
    See also
    --------
    :func:`dc`
    :func:`precision`
    :func:`recall`
    
    Notes
    -----
    This is not a real metric, as it is directed. Whatever object is considered as
    reference should be passed first. Negative values denote a smaller and positive
    values a larger volume than the reference.
    
    This implementation does not check, whether the two supplied arrays are of the same
    size.
    
    Examples
    --------
    Considering the following inputs
    
    >>> import numpy
    >>> arr1 = numpy.asarray([[0,1,0],[1,1,1],[0,1,0]])
    >>> arr1
    array([[0, 1, 0],
           [1, 1, 1],
           [0, 1, 0]])
    >>> arr2 = numpy.asarray([[0,1,0],[1,0,1],[0,1,0]])
    >>> arr2
    array([[0, 1, 0],
           [1, 0, 1],
           [0, 1, 0]])
           
    comparing `arr1` to `arr2` we get
    
    >>> ravd(arr1, arr2)
    -0.2
    
    and reversing the inputs the directivness of the metric becomes evident
    
    >>> ravd(arr2, arr1)
    0.25
    
    It is important to keep in mind that a perfect score of `0` does not mean that the
    binary objects fit exactely, as only the volumes are compared:
    
    >>> arr1 = numpy.asarray([1,0,0])
    >>> arr2 = numpy.asarray([0,0,1])
    >>> ravd(arr1, arr2)
    0.0
    
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
        
    vol1 = numpy.count_nonzero(input1)
    vol2 = numpy.count_nonzero(input2)
    
    if 0 == vol1:
        raise RuntimeError('The first supplied array does not contain any binary object.')

    return (vol2 - vol1) / float(vol1)
    
def obj_assd(input1, input2, voxelspacing=None, connectivity=1):
    """
    Average symmetric surface distance.
    
    Computes the average symmetric surface distance (ASSD) between the binary objects in
    two images.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing : float or sequence of floats, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity : int
        The neighbourhood/connectivity considered when determining what accounts
        for a distinct binary object as well as when determining the surface
        of the binary objects. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        The decision on the connectivity is important, as it can influence the results
        strongly. If in doubt, leave it as it is.
        
    Returns
    -------
    assd : float
        The average symmetric surface distance between all mutually existing distinct
        binary object(s) in ``input1`` and ``input2``. The distance unit is the same as for
        the spacing of elements along each dimension, which is usually given in mm.
        
    See also
    --------
    :func:`obj_asd`
    
    Notes
    -----
    This is a real metric, obtained by calling and averaging
    
    >>> obj_asd(input1, input2)
    
    and
    
    >>> obj_asd(input2, input1)
    
    """
    assd = numpy.mean( (obj_asd(input1, input2, voxelspacing, connectivity), obj_asd(input2, input1, voxelspacing, connectivity)) )
    return assd
    
    
def obj_asd(input1, input2, voxelspacing=None, connectivity=1):
    """
    Average surface distance between objects.
    
    First correspondences between distinct binary objects in input2 and input1 are
    established. Then the average surface distance is only computed between corresponding
    objects. Correspondence is defined as unique and at least one voxel overlap.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    voxelspacing : float or sequence of floats, optional
        The voxelspacing in a distance unit i.e. spacing of elements
        along each dimension. If a sequence, must be of length equal to
        the input rank; if a single number, this is used for all axes. If
        not specified, a grid spacing of unity is implied.
    connectivity : int
        The neighbourhood/connectivity considered when determining what accounts
        for a distinct binary object as well as when determining the surface
        of the binary objects. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        The decision on the connectivity is important, as it can influence the results
        strongly. If in doubt, leave it as it is.
        
    Returns
    -------
    asd : float
        The average surface distance between all mutually existing distinct binary
        object(s) in ``input1`` and ``input2``. The distance unit is the same as for the
        spacing of elements along each dimension, which is usually given in mm.
        
    See also
    --------
    :func:`obj_assd`
    :func:`obj_tpr`
    :func:`obj_fpr`
        
    Notes
    -----
    This is not a real metric, as it is directed. See `obj_assd` for a real metric of this.
    
    For the understanding of this metric, both the notions of connectedness and surface
    distance are essential. Please see :func:`obj_tpr` and :func:`obj_fpr` for more
    information on the first and :func:`asd` on the second.
        
    Examples
    --------
    >>> arr1 = numpy.asarray([[1,1,1],[1,1,1],[1,1,1]])
    >>> arr2 = numpy.asarray([[0,1,0],[0,1,0],[0,1,0]])
    >>> arr1
    array([[1, 1, 1],
           [1, 1, 1],
           [1, 1, 1]])
    >>> arr2
    array([[0, 1, 0],
           [0, 1, 0],
           [0, 1, 0]])
    >>> obj_asd(arr1, arr2)
    1.5
    >>> obj_asd(arr2, arr1)
    0.333333333333
    
    With the `voxelspacing` parameter, the distances between the voxels can be set for
    each dimension separately:
    
    >>> obj_asd(arr1, arr2, voxelspacing=(1,2))
    1.5
    >>> obj_asd(arr2, arr1, voxelspacing=(1,2))
    0.333333333333    
    
    More examples depicting the notion of object connectedness:
    
    >>> arr1 = numpy.asarray([[1,0,1],[1,0,0],[0,0,0]])
    >>> arr2 = numpy.asarray([[1,0,1],[1,0,0],[0,0,1]])
    >>> arr1
    array([[1, 0, 1],
           [1, 0, 0],
           [0, 0, 0]])
    >>> arr2
    array([[1, 0, 1],
           [1, 0, 0],
           [0, 0, 1]])
    >>> obj_asd(arr1, arr2)
    0.0
    >>> obj_asd(arr2, arr1)
    0.0
    
    >>> arr1 = numpy.asarray([[1,0,1],[1,0,1],[0,0,1]])
    >>> arr2 = numpy.asarray([[1,0,1],[1,0,0],[0,0,1]])
    >>> arr1
    array([[1, 0, 1],
           [1, 0, 1],
           [0, 0, 1]])
    >>> arr2
    array([[1, 0, 1],
           [1, 0, 0],
           [0, 0, 1]])
    >>> obj_asd(arr1, arr2)
    0.6
    >>> obj_asd(arr2, arr1)
    0.0
    
    Influence of `connectivity` parameter can be seen in the following example, where
    with the (default) connectivity of `1` the first array is considered to contain two
    objects, while with an increase connectivity of `2`, just one large object is
    detected.  
    
    >>> arr1 = numpy.asarray([[1,0,0],[0,1,1],[0,1,1]])
    >>> arr2 = numpy.asarray([[1,0,0],[0,0,0],[0,0,0]])
    >>> arr1
    array([[1, 0, 0],
           [0, 1, 1],
           [0, 1, 1]])
    >>> arr2
    array([[1, 0, 0],
           [0, 0, 0],
           [0, 0, 0]])
    >>> obj_asd(arr1, arr2)
    0.0
    >>> obj_asd(arr1, arr2, connectivity=2)
    1.742955328
    
    Note that the connectivity also influence the notion of what is considered an object
    surface voxels.
    """
    sds = list()
    labelmap1, labelmap2, _a, _b, mapping = __distinct_binary_object_correspondences(input1, input2, connectivity)
    slicers1 = find_objects(labelmap1)
    slicers2 = find_objects(labelmap2)
    for lid2, lid1 in mapping.iteritems():
        window = __combine_windows(slicers1[lid1 - 1], slicers2[lid2 - 1])
        object1 = labelmap1[window] == lid1
        object2 = labelmap2[window] == lid2
        sds.extend(__surface_distances(object1, object2, voxelspacing, connectivity))
    asd = numpy.mean(sds)
    return asd
    
def obj_fpr(input1, input2, connectivity=1):
    """
    The false positive rate of distinct binary object detection.
    
    The false positive rates gives a percentage measure of how many distinct binary
    objects in the second array do not exists in the first array. A partial overlap
    (of minimum one voxel) is here considered sufficient.
    
    In cases where two distinct binary object in the second array overlap with a single
    distinct object in the first array, only one is considered to have been detected
    successfully and the other is added to the count of false positives.
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    connectivity : int
        The neighbourhood/connectivity considered when determining what accounts
        for a distinct binary object. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        The decision on the connectivity is important, as it can influence the results
        strongly. If in doubt, leave it as it is.
        
    Returns
    -------
    tpr : float
        A percentage measure of how many distinct binary objects in ``input2`` have no
        corresponding binary object in ``input2``. It has the range :math:`[0, 1]`, where a :math:`0`
        denotes an ideal score.
        
    Raises
    ------
    RuntimeError
        If the second array is empty.
    
    See also
    --------
    :func:`obj_tpr`
    
    Notes
    -----
    This is not a real metric, as it is directed. Whatever array is considered as
    reference should be passed first. A perfect score of :math:`0` tells that there are no
    distinct binary objects in the second array that do not exists also in the reference
    array, but does not reveal anything about objects in the reference array also
    existing in the second array (use :func:`obj_tpr` for this).
    
    Examples
    --------
    >>> arr1 = numpy.asarray([[1,0,0],[1,0,1],[0,0,1]])
    >>> arr2 = numpy.asarray([[0,0,1],[1,0,1],[0,0,1]])
    >>> arr1
    array([[1, 0, 0],
           [1, 0, 1],
           [0, 0, 1]])
    >>> arr2
    array([[0, 0, 1],
           [1, 0, 1],
           [0, 0, 1]])
    >>> obj_fpr(arr1, arr2)
    0.0
    >>> obj_fpr(arr2, arr1)
    0.0
    
    Example of directedness:
    
    >>> arr1 = numpy.asarray([1,0,1,0,1])
    >>> arr2 = numpy.asarray([1,0,1,0,0])
    >>> obj_fpr(arr1, arr2)
    0.0
    >>> obj_fpr(arr2, arr1)
    0.3333333333333333
    
    Examples of multiple overlap treatment:
    
    >>> arr1 = numpy.asarray([1,0,1,0,1,1,1])
    >>> arr2 = numpy.asarray([1,1,1,0,1,0,1])
    >>> obj_fpr(arr1, arr2)
    0.3333333333333333
    >>> obj_fpr(arr2, arr1)
    0.3333333333333333
    
    >>> arr1 = numpy.asarray([1,0,1,1,1,0,1])
    >>> arr2 = numpy.asarray([1,1,1,0,1,1,1])
    >>> obj_fpr(arr1, arr2)
    0.0
    >>> obj_fpr(arr2, arr1)
    0.3333333333333333
    
    >>> arr1 = numpy.asarray([[1,0,1,0,0],
                              [1,0,0,0,0],
                              [1,0,1,1,1],
                              [0,0,0,0,0],
                              [1,0,1,0,0]])
    >>> arr2 = numpy.asarray([[1,1,1,0,0],
                              [0,0,0,0,0],
                              [1,1,1,0,1],
                              [0,0,0,0,0],
                              [1,1,1,0,0]])
    >>> obj_fpr(arr1, arr2)
    0.0
    >>> obj_fpr(arr2, arr1)
    0.2    
    """
    _, _, _, n_obj_input2, mapping = __distinct_binary_object_correspondences(input1, input2, connectivity)
    return (n_obj_input2 - len(mapping)) / float(n_obj_input2)
    
def obj_tpr(input1, input2, connectivity=1):
    """
    The true positive rate of distinct binary object detection.
    
    The true positive rates gives a percentage measure of how many distinct binary
    objects in the first array also exists in the second array. A partial overlap
    (of minimum one voxel) is here considered sufficient.
    
    In cases where two distinct binary object in the first array overlaps with a single
    distinct object in the second array, only one is considered to have been detected
    successfully.  
    
    Parameters
    ----------
    input1 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    input2 : array_like
        Input data containing objects. Can be any type but will be converted
        into binary: background where 0, object everywhere else.
    connectivity : int
        The neighbourhood/connectivity considered when determining what accounts
        for a distinct binary object. This value is passed to
        `scipy.ndimage.morphology.generate_binary_structure` and should usually be :math:`> 1`.
        The decision on the connectivity is important, as it can influence the results
        strongly. If in doubt, leave it as it is.
        
    Returns
    -------
    tpr : float
        A percentage measure of how many distinct binary objects in ``input1`` also exists
        in ``input2``. It has the range :math:`[0, 1]`, where a :math:`1` denotes an ideal score.
        
    Raises
    ------
    RuntimeError
        If the reference object is empty.
    
    See also
    --------
    :func:`obj_fpr`
    
    Notes
    -----
    This is not a real metric, as it is directed. Whatever array is considered as
    reference should be passed first. A perfect score of :math:`1` tells that all distinct
    binary objects in the reference array also exist in the second array, but does not
    reveal anything about additional binary objects in the second array
    (use :func:`obj_fpr` for this).
    
    Examples
    --------
    >>> arr1 = numpy.asarray([[1,0,0],[1,0,1],[0,0,1]])
    >>> arr2 = numpy.asarray([[0,0,1],[1,0,1],[0,0,1]])
    >>> arr1
    array([[1, 0, 0],
           [1, 0, 1],
           [0, 0, 1]])
    >>> arr2
    array([[0, 0, 1],
           [1, 0, 1],
           [0, 0, 1]])
    >>> obj_tpr(arr1, arr2)
    1.0
    >>> obj_tpr(arr2, arr1)
    1.0
    
    Example of directedness:
    
    >>> arr1 = numpy.asarray([1,0,1,0,1])
    >>> arr2 = numpy.asarray([1,0,1,0,0])
    >>> obj_tpr(arr1, arr2)
    0.6666666666666666
    >>> obj_tpr(arr2, arr1)
    1.0
    
    Examples of multiple overlap treatment:
    
    >>> arr1 = numpy.asarray([1,0,1,0,1,1,1])
    >>> arr2 = numpy.asarray([1,1,1,0,1,0,1])
    >>> obj_tpr(arr1, arr2)
    0.6666666666666666
    >>> obj_tpr(arr2, arr1)
    0.6666666666666666
    
    >>> arr1 = numpy.asarray([1,0,1,1,1,0,1])
    >>> arr2 = numpy.asarray([1,1,1,0,1,1,1])
    >>> obj_tpr(arr1, arr2)
    0.6666666666666666
    >>> obj_tpr(arr2, arr1)
    1.0
    
    >>> arr1 = numpy.asarray([[1,0,1,0,0],
                              [1,0,0,0,0],
                              [1,0,1,1,1],
                              [0,0,0,0,0],
                              [1,0,1,0,0]])
    >>> arr2 = numpy.asarray([[1,1,1,0,0],
                              [0,0,0,0,0],
                              [1,1,1,0,1],
                              [0,0,0,0,0],
                              [1,1,1,0,0]])
    >>> obj_tpr(arr1, arr2)
    0.8
    >>> obj_tpr(arr2, arr1)
    1.0    
    """
    _, _, n_obj_input1, _, mapping = __distinct_binary_object_correspondences(input1, input2, connectivity)
    return len(mapping) / float(n_obj_input1)

def __distinct_binary_object_correspondences(input1, input2, connectivity=1):
    """
    Determines all distinct (where connectivity is defined by the connectivity parameter
    passed to scipy's `generate_binary_structure`) binary objects in both of the input
    parameters and returns a 1to1 mapping from the labelled objects in input2 to the
    corresponding (whereas a one-voxel overlap suffices for correspondence) objects in
    input1.
    
    All stems from the problem, that the relationship is non-surjective many-to-many.
    
    @return (labelmap1, labelmap2, n_lables1, n_labels2, labelmapping2to1)
    """
    input1 = numpy.atleast_1d(input1.astype(numpy.bool))
    input2 = numpy.atleast_1d(input2.astype(numpy.bool))
    
    # binary structure
    footprint = generate_binary_structure(input1.ndim, connectivity)
    
    # label distinct binary objects
    labelmap1, n_obj_input1 = label(input1, footprint)
    labelmap2, n_obj_input2 = label(input2, footprint)
    
    # find all overlaps from labelmap2 to labelmap1; collect one-to-one relationships and store all one-two-many for later processing
    slicers = find_objects(labelmap2) # get windows of labelled objects
    mapping = dict() # mappings from labels in labelmap2 to corresponding object labels in labelmap1
    used_labels = set() # set to collect all already used labels from labelmap2
    one_to_many = list() # list to collect all one-to-many mappings
    for l1id, slicer in enumerate(slicers): # iterate over object in labelmap2 and their windows
        l1id += 1 # labelled objects have ids sarting from 1
        bobj = (l1id) == labelmap2[slicer] # find binary object corresponding to the label1 id in the segmentation
        l2ids = numpy.unique(labelmap1[slicer][bobj]) # extract all unique object identifiers at the corresponding positions in the reference (i.e. the mapping)
        l2ids = l2ids[0 != l2ids] # remove background identifiers (=0)
        if 1 == len(l2ids): # one-to-one mapping: if target label not already used, add to final list of object-to-object mappings and mark target label as used
            l2id = l2ids[0]
            if not l2id in used_labels:
                mapping[l1id] = l2id
                used_labels.add(l2id)
        elif 1 < len(l2ids): # one-to-many mapping: store relationship for later processing
            one_to_many.append((l1id, set(l2ids)))
            
    # process one-to-many mappings, always choosing the one with the least labelmap2 correspondences first
    while True:
        one_to_many = [(l1id, l2ids - used_labels) for l1id, l2ids in one_to_many] # remove already used ids from all sets
        one_to_many = filter(lambda x: x[1], one_to_many) # remove empty sets
        one_to_many = sorted(one_to_many, key=lambda x: len(x[1])) # sort by set length
        if 0 == len(one_to_many):
            break
        l2id = one_to_many[0][1].pop() # select an arbitrary target label id from the shortest set
        mapping[one_to_many[0][0]] = l2id # add to one-to-one mappings 
        used_labels.add(l2id) # mark target label as used
        one_to_many = one_to_many[1:] # delete the processed set from all sets
    
    return labelmap1, labelmap2, n_obj_input1, n_obj_input2, mapping
    
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
    
    # test for emptiness
    if 0 == numpy.count_nonzero(input1): 
        raise RuntimeError('The first supplied array does not contain any binary object.')
    if 0 == numpy.count_nonzero(input2): 
        raise RuntimeError('The second supplied array does not contain any binary object.')    
            
    # extract only 1-pixel border line of objects
    input1_border = input1 - binary_erosion(input1, structure=footprint, iterations=1)
    input2_border = input2 - binary_erosion(input2, structure=footprint, iterations=1)
    
    # compute average surface distance        
    # Note: scipys distance transform is calculated only inside the borders of the
    #       foreground objects, therefore the input has to be reversed
    dt = distance_transform_edt(~input2_border, sampling=voxelspacing)
    sds = dt[input1_border]
    
    return sds

def __combine_windows(w1, w2):
    """
    Joins two windows (defined by tuple of slices) such that their maximum
    combined extend is covered by the new returned window.
    """
    res = []
    for s1, s2 in zip(w1, w2):
        res.append(slice(min(s1.start, s2.start), max(s1.stop, s2.stop)))
    return tuple(res)
