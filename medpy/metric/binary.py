"""
@package medpy.metric.binary
Provides a number of binary image distance measures.

@author Oskar Maier
@version d0.1.0
@since 2014-03-13
@status Development
"""

# build-in modules

# third-party modules
import numpy
from scipy.ndimage import _ni_support
from scipy.ndimage.morphology import distance_transform_edt, binary_erosion

# own modules

# code
def dc(input1, input2):
    pass

def precision(input1, input2):
    pass

def recall(input1, input2):
    pass

def fscore(input1, input2, beta=1):
    pass

def hd(input1, input2, voxelspacing=None):
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
        
    Returns
    -------
    hd: float
        The symmetric Hausdorff Distance between the object(s) in `input1` and the
        object(s) in `input2`. The distance unit is the same as for the spacing of 
        elements along each dimension, which is usually given in mm.
        
    See also
    --------
    assd
    asd
    
    Notes
    -----
    This is a real metric.
    """
    hd1 = __surface_distances(input1, input2, voxelspacing).max()
    hd2 = __surface_distances(input2, input1, voxelspacing).max()
    hd = max(hd1, hd2)
    return hd

def assd(input1, input2, voxelspacing=None):
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
        
    Returns
    -------
    assd: float
        The average symmetric surface distance between the object(s) in `input1` and the
        object(s) in `input2`. The distance unit is the same as for the spacing of 
        elements along each dimension, which is usually given in mm.
        
    See also
    --------
    asd
    hd
    
    Notes
    -----
    This is a real metric, obtained by calling and averaging
    >>>> asd(input1, input2)
    and
    >>>> asd(input2, input1)
    """
    assd = ( asd(input1, input2, voxelspacing) + asd(input2, input1, voxelspacing) ) / 2.
    return assd

def asd(input1, input2, voxelspacing=None):
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
    
    Returns
    -------
    asd: float
        The average surface distance between the object(s) in `input1` and the
        object(s) in `input2`. The distance unit is the same as for the spacing
        of elements along each dimension, which is usually given in mm.
        
    See also
    --------
    assd
    hd
    
    
    Notes
    -----
    This is not a real metric, as it is directed. See `assd` for a real metric of this.
    
    The method is implemented making use of distance images and simple binary morphology
    to achieve high computational speed.
    
    Examples
    --------
    """
    sds = __surface_distances(input1, input2, voxelspacing)
    asd = sds.mean()
    return asd
    
def __surface_distances(input1, input2, voxelspacing=None):
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
            
    # extract only 1-pixel border line of objects
    input1_border = input1 - binary_erosion(input1, iterations=1)
    
    # compute average surface distance        
    # Note: scipys distance transform is calculated only inside the borders of the
    #       foreground objects, therefore the input has to be reversed
    dt = distance_transform_edt(~input2, sampling=voxelspacing)
    sds = dt[input1_border]
    
    return sds    