"""
@package medpy.features.intensity
Functions to extracts voxel-wise intensity based features from images.

Feature representation:
Features can be one or more dimensional and are kept in the following structures:
           s1    s2    s3    [...]
    f1.1
    f1.2
    f2.1
    f3.1
    f3.2
    [...]
, where each column sX denotes a single sample (voxel) and each row a features element
e.g. f1 is constitutes a 2-dimensional features and occupies therefore two rows, while
f2 is a single element features with a single row. Entries of this array are of type
float.
These feature representation forms are processable by the scikit-learn machine learning
methods.

Multi-spectral images:
This package was originally designed for MR images and is therefore suited to handle
multi-spectral data such as RGB and MR images. Each feature extraction function can be
supplied with list/tuple of images instead of an image. in which case they are considered
co-registered and the feature is extracted from all of them independently.

@author Oskar Maier
@version r0.1.1
@since 2013-08-24
@status Release
"""

# build-in module
import itertools

# third-party modules
import numpy
from scipy.ndimage.filters import gaussian_filter

# own modules
from medpy.features import utilities
from medpy.core.exceptions import ArgumentError
from medpy.features.utilities import join
from medpy.filter.houghtransform import __pad_image

# constants

def intensities(image, mask = slice(None)):
    """
    Takes a simple or multi-spectral image and returns its voxel-wise intensities.
    A multi-spectral image must be supplied as a list or tuple of its spectra.
    
    Optionally a binary mask can be supplied to select the voxels for which the feature
    should be extracted.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the images intensities
    @type ndarray
    """
    return __extract_feature(__extract_intensities, image, mask)

def centerdistance(image, voxelspacing = None, mask = slice(None)):
    """
    Takes a simple or multi-spectral image and returns its voxel-wise center distance in
    mm. A multi-spectral image must be supplied as a list or tuple of its spectra.
    
    Optionally a binary mask can be supplied to select the voxels for which the feature
    should be extracted.
    
    The center distance is the exact euclidean distance in mm of each voxels center to
    the central point of the overal image volume.
    
    Note that this feature is independent of the actual image content, but depends
    solely on its shape. Therefore always a one-dimensional feature is returned, even if
    a multi-spectral image has been supplied. 

    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the distance of each voxel to the images center
    @type ndarray
    """
    if type(image) == tuple or type(image) == list:
        image = image[0]
        
    return __extract_feature(__extract_centerdistance, image, mask, voxelspacing = voxelspacing)

def centerdistance_xdminus1(image, dim, voxelspacing = None, mask = slice(None)):
    """
    Implementation of @see centerdistance that allows to compute sub-volume wise
    centerdistances.
    
    The same notes as for @see centerdistance apply.
    
    Example:
        Considering a 3D medical image we want to compute the axial slice-wise
        centerdistances instead of the ones over the complete image volume. Assuming that
        the third image dimension corresponds to the axial axes of the image, we call
            centerdistance_xdminus1(image, 3)
        Note that the centerdistance of each slice is the same.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param dim the dimension or dimensions along which to cut the image into sub-volumes
    @type dim int | sequence of ints
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the distance of each voxel to the images center
    @type ndarray
    
    @raises ArgumentError if a invalid dim index of number of dim indices were supplied    
    """
    # pre-process arguments
    if type(image) == tuple or type(image) == list:
        image = image[0]
    
    if type(dim) is int:
        dims = [dim]
    else:
        dims = list(dim)
        
    # check arguments
    if len(dims) >= image.ndim - 1:
        raise ArgumentError('Applying a sub-volume extraction of depth {} on a image of dimensionality {} would lead to invalid images of dimensionality <= 1.'.format(len(dims), image.ndim))
    for dim in dims:
        if dim >= image.ndim:
            raise ArgumentError('Invalid dimension index {} supplied for image(s) of shape {}.'.format(dim, image.shape))
    
    # extract desired sub-volume
    slicer = [slice(None)] * image.ndim
    for dim in dims: slicer[dim] = slice(1)
    subvolume = numpy.squeeze(image[slicer])
    
    # compute centerdistance for sub-volume and reshape to original sub-volume shape (note that normalization and mask are not passed on in this step)
    o = centerdistance(subvolume, voxelspacing).reshape(subvolume.shape)
    
    # re-establish original shape by copying the resulting array multiple times
    for dim in sorted(dims):
        o = numpy.asarray([o] * image.shape[dim])
        o = numpy.rollaxis(o, 0, dim + 1)
        
    # extract intensities / centerdistance values, applying normalization and mask in this step
    return intensities(o, mask)

def indices(image, voxelspacing = None, mask = slice(None)):
    """
    Takes an image and returns the voxels ndim-indices as voxel-wise feature. The voxel
    spcaing is taken into account, i.e. the indices are not array indices, but millimeter
    indices.
    
    This is a multi-element feature where each element corresponds to one of the images
    axes, e.g. x, y, z, ...
    
    Note that this feature is independent of the actual image content, but depends
    solely on its shape. Therefore always a one-dimensional feature is returned, even if
    a multi-spectral image has been supplied. 
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray

    @return each voxel ndim-index
    @type ndarray
    """
    if type(image) == tuple or type(image) == list:
        image = image[0]
        
    if not type(mask) is slice:
        mask = numpy.array(mask, copy=False, dtype=numpy.bool)
        
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim

    return join(*map(lambda (a, vs): a[mask].ravel() * vs, zip(numpy.indices(image.shape), voxelspacing)))
    
    
    
def local_mean_gauss(image, sigma = 5, voxelspacing = None, mask = slice(None)):
    """
    Takes a simple or multi-spectral image and returns the approximate mean over a small
    region around each voxel. A multi-spectral image must be supplied as a list or tuple
    of its spectra.
    
    Optionally a binary mask can be supplied to select the voxels for which the feature
    should be extracted.
    
    For this feature a Gaussian smoothing filter is applied to the image / each spectrum
    and then the resulting intensity values returned.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param sigma Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes.
    @type sigma scalar or sequence of scalars
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the images intensities
    @type ndarray
    """
    return __extract_feature(__extract_local_mean_gauss, image, mask, sigma = sigma, voxelspacing = voxelspacing)



def local_histogram(image, size = 11, bins = 19, rang = None, cutoffp = (0, 100), cval = 0, mask = slice(None)):
    """
    Supply an image and (optionally) a mask and get the local histogram of local
    neighbourhoods around each voxel. These neighbourhoods are cubic with a sidelength of
    size in voxels or, when a shape instead of an integer is passed to size, of this
    shape.
    
    Voxels along the image border are treated as being filled with cval. 
    
    When a mask is supplied, the local histogram is extracted only for the voxels where
    the mask is True. But voxels from outside the mask can be incorporated in the
    compuation of the histograms.
    
    The range of the histograms can be set via the rang argument. When set to None, local
    histograms ranges are used, which makes them more pronounced, but less compareable.
    Alternatively the 'image' keyword can be supplied, to use the same range for all
    local histograms, extracted from the images max and min intensity values. Finally, an
    own range can be supplied in the form of a tuple.
    
    Setting a proper range is important, as all voxels that lie outside of the range are
    ignored i.e. do not contribute to the histograms as if they would not exists. Some
    of the local histograms can therefore be constructed from less than the expected
    number of voxels.
    
    Taking the histogram range from the whole image is sensitive to outliers. Supplying
    percentile values to the cutoffp argument, these can be filtered out when computing
    the range. This keyword is ignored if rang is not set to 'image'.
    
    The local histograms are normalized by dividing them through the number of bins.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param size either the local cube areas sidelength or a shape of the area
    @type int | tuple of ints
    @param bins the number of histogram bins
    @type bins integer
    @param rang the range of the histograms, can be supplied manually, set to 'image' or
                set to None to use local ranges
    @type rang string | tuple of numbers | None
    @param cutoffp the cut-off percentiles to exclude outliers, only processed if rang is
                   set to 'image'
    @type cutoffp tuple of numbers
    @param cval constant value to padd the image with
    @type cval number
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the bin values of the local histograms for each voxel
    @rtype ndarray
    """
    return __extract_feature(__extract_local_histogram, image, mask, size = size, bins = bins, rang = rang, cutoffp = cutoffp, cval = cval)


def __extract_local_histogram(image, mask = slice(None), size = 11, bins = 19, rang = None, cutoffp = (0, 100), cval = 0):
    """
    Internal, single-image version of @see localhistogram
    """
    # create a cube with sidlength size or the desired structure
    if isinstance(size, int):
        structure = numpy.ones([size] * image.ndim, dtype=numpy.bool)
    else:
        structure = numpy.ones(size, dtype=numpy.bool)
        
    # prepare iterators over image dimensions
    its = [xrange(x) for x in image.shape]
    
    # extract images intensity range if requested
    if 'image' == rang:
        rang = tuple(numpy.percentile(image[mask], cutoffp))
        
    # pad image with 0 values
    image = __pad_image(image, structure, cval)

    # iterate over all voxels in the image and collect histograms from the surrounding area covered by structure
    out = []
    if isinstance(mask, slice): # iterate without mask (slightly faster)
        for idx in itertools.product(*its):
            slicer = [slice(pos, pos + stride) for pos, stride in zip(idx, structure.shape)]
            h, _ = numpy.histogram(image[slicer], bins, range=rang)
            out.append(h)
    else: # iterate with checking the mask 
        for idx in itertools.product(*its):
            slicer = [slice(pos, pos + stride) for pos, stride in zip(idx, structure.shape)]
            if mask[idx]:
                h, _ = numpy.histogram(image[slicer], bins, range=rang)
                out.append(h)
                
    # assemble and normalize
    out = (numpy.asarray(out, dtype=numpy.float).T / numpy.sum(out, 1)).T
                
    return out
    
def __extract_local_mean_gauss(image, mask = slice(None), sigma = 1, voxelspacing = None):
    """
    Internal, single-image version of @see local_mean_gauss
    """
    # set voxel spacing
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim
        
    # determine gaussian kernel size in voxel units
    try:
        sigma = [s / float(vs) for s, vs in zip(sigma, voxelspacing)]
    except TypeError:
        sigma = [sigma / float(vs) for vs in voxelspacing]
        
    return __extract_intensities(gaussian_filter(image, sigma), mask)


def __extract_centerdistance(image, mask = slice(None), voxelspacing = None):
    """
    Internal, single-image version of @see centerdistance
    """
    image = numpy.array(image, copy=False)
    
    if None == voxelspacing:
        voxelspacing = [1.] * image.ndim
        
    # get image center and an array holding the images indices
    centers = map(lambda x: (x - 1) / 2., image.shape)
    indices = numpy.indices(image.shape, dtype=numpy.float)
    
    # shift to center of image and correct spacing to real world coordinates
    for dim_indices, c, vs in zip(indices, centers, voxelspacing):
        dim_indices -= c
        dim_indices *= vs
        
    # compute euclidean distance to image center
    return numpy.sqrt(numpy.sum(numpy.square(indices), 0))[mask].ravel()
    

def __extract_intensities(image, mask = slice(None)):
    """
    Internal, single-image version of @see intensities
    """
    return numpy.array(image, copy=True)[mask].ravel()


def __extract_feature(fun, image, mask = slice(None), **kwargs):
    """
    Convenient function to cope with multi-spectral images and feature normalization.
    
    @param fun the feature extraction function to call
    @param image the single or multi-spectral image
    @param mask the binary mask to select the voxels for which to extract the feature
    @param kwargs additional keyword arguments to be passed to the feature extraction function 
    """
    if not type(mask) is slice:
        mask = numpy.array(mask, copy=False, dtype=numpy.bool)
    
    if type(image) == tuple or type(image) == list:
        return utilities.join(*[fun(i, mask, **kwargs) for i in image])
    else:
        return fun(image, mask, **kwargs)
    