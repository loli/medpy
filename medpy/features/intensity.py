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
@version r0.3.3
@since 2013-08-24
@status Release
"""

# build-in module

# third-party modules
import numpy
from scipy.ndimage.filters import gaussian_filter, gaussian_gradient_magnitude,\
    median_filter
from scipy.interpolate.interpolate import interp1d
from scipy.ndimage.morphology import distance_transform_edt
from scipy.ndimage._ni_support import _get_output

# own modules
from medpy.features import utilities
from medpy.core.exceptions import ArgumentError
from medpy.features.utilities import join
from medpy.filter.image import sum_filter

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
            centerdistance_xdminus1(image, 2)
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
    spacing is taken into account, i.e. the indices are not array indices, but millimeter
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
    
def shifted_mean_gauss(image, offset = None, sigma = 5, voxelspacing = None, mask = slice(None)):
    """
    !TODO: Write description: mean gauss over area at point offset of current voxel
    """
    return __extract_feature(__extract_shifted_mean_gauss, image, mask, offset = offset, sigma = sigma, voxelspacing = voxelspacing)
    
def mask_distance(image, voxelspacing = None, mask = slice(None)):
    """
    Computes the distance of each point under the mask to the mask border taking the
    voxel-spacing into account.
    
    Note that this feature is independent of the actual image content, but depends
    solely the mask image. Therefore always a one-dimensional feature is returned,
    even if a multi-spectral image has been supplied.
    
    If no mask has been supplied, the distances to the image borders are returned. 
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the distances
    @type ndarray    
    """
    if type(image) == tuple or type(image) == list:
        image = image[0]
        
    return __extract_mask_distance(image, mask = mask, voxelspacing = voxelspacing)
    
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
    @param sigma Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Note that the voxel spacing of the image is taken into account, the given values are treated as mm.
    @type sigma scalar or sequence of scalars
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the images intensities
    @type ndarray
    """
    return __extract_feature(__extract_local_mean_gauss, image, mask, sigma = sigma, voxelspacing = voxelspacing)

def guassian_gradient_magnitude(image, sigma = 5, voxelspacing = None, mask = slice(None)):
    """
    Computes the gradient magnitude (edge-detection) of the supplied image using gaussian
    derivates and returns the intensity values.
    
    Optionally a binary mask can be supplied to select the voxels for which the feature
    should be extracted.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param sigma Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Note that the voxel spacing of the image is taken into account, the given values are treated as mm.
    @type sigma scalar or sequence of scalars
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the images intensities
    @type ndarray
    """
    return __extract_feature(__extract_guassian_gradient_magnitude, image, mask, sigma = sigma, voxelspacing = voxelspacing)

def median(image, size = 5, voxelspacing = None, mask = slice(None)):
    """
    Computes the multi-dimensional median filter and returns the resulting values per
    voxel.
    
    Optionally a binary mask can be supplied to select the voxels for which the feature
    should be extracted.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param size Size of the structuring element. Can be given given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Note that the voxel spacing of the image is taken into account, the given values are treated as mm.
    @type size scalar or sequence of scalars
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the images intensities
    @type ndarray
    """
    return __extract_feature(__extract_median, image, mask, size = size, voxelspacing = voxelspacing)

def local_histogram(image, bins=19, rang="image", cutoffp=(0.0, 100.0), size=None, footprint=None, output=None, mode="ignore", origin=0, mask=slice(None)):
    """
    Computes multi-dimensional histograms over a region around each voxel.
    
    Supply an image and (optionally) a mask and get the local histogram of local
    neighbourhoods around each voxel. These neighbourhoods are cubic with a sidelength of
    size in voxels or, when a shape instead of an integer is passed to size, of this
    shape.
    
    If not argument is passed to output, the returned array will be of dtype float.
    
    Voxels along the image border are treated as defined by mode. The possible values are
    the same as for scipy.ndimage filter without the ''constant'' mode. Instead "ignore"
    is the default and additional mode, which sets that the area outside of the image are
    ignored when computing the histogram.
    
    When a mask is supplied, the local histogram is extracted only for the voxels where
    the mask is True. But voxels from outside the mask can be incorporated in the
    compuation of the histograms.
    
    The range of the histograms can be set via the rang argument. The 'image' keyword can
    be supplied, to use the same range for all local histograms, extracted from the images
    max and min intensity values. Alternatively, an own range can be supplied in the form
    of a tuple of two numbers. Values outside the range of the histogram are ignored.
    
    Setting a proper range is important, as all voxels that lie outside of the range are
    ignored i.e. do not contribute to the histograms as if they would not exists. Some
    of the local histograms can therefore be constructed from less than the expected
    number of voxels.
    
    Taking the histogram range from the whole image is sensitive to outliers. Supplying
    percentile values to the cutoffp argument, these can be filtered out when computing
    the range. This keyword is ignored if rang is not set to 'image'.
    
    Setting the rang to None causes local ranges to be used i.e. the ranges of the
    histograms are computed only over the local area covered by them and are hence
    not comparable. This behaviour should normally not be taken.
    
    The local histograms are normalized by dividing them through the number of elements
    in the bins.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param bins the number of histogram bins
    @type bins integer
    @param rang the range of the histograms, can be supplied manually, set to 'image' or
                set to None to use local ranges
    @type rang string | tuple of numbers | None
    @param cutoffp the cut-off percentiles to exclude outliers, only processed if rang is
                   set to 'image'
    @type cutoffp tuple of scalars | 'image'
    @param size See footprint, below
    @type size scalar | tuple
    @param footprint  Either ``size`` or ``footprint`` must be defined. ``size`` gives the shape that is taken from the input array, at every element position, to define the input to the filter function. ``footprint`` is a boolean array that specifies (implicitly) a shape, but also which of the elements within this shape will get passed to the filter function. Thus ``size=(n,m)`` is equivalent to ``footprint=np.ones((n,m))``. We adjust ``size`` to the number of dimensions of the input array, so that, if the input array is shape (10,10,10), and ``size`` is 2, then the actual size used is (2,2,2).
    @type footprint ndarray
    @param output  The ``output`` parameter passes an array in which to store the filter output.
    @type output ndarray | dtype
    @param mode The ``mode`` parameter determines how the array borders are handled. Default is 'ignore'
    @type mode 'reflect' | 'ignore' | 'nearest' | 'mirror' | 'wrap'
    @param origin The ``origin`` parameter controls the placement of the filter. Default 0.
    @type origin scalar
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the bin values of the local histograms for each voxel
    @rtype ndarray
    """    
    return __extract_feature(__extract_local_histogram, image, mask, bins=bins, rang=rang, cutoffp=cutoffp, size=size, footprint=footprint, output=output, mode=mode, origin=origin)


def hemispheric_difference(image, sigma_active = 7, sigma_reference = 7, cut_plane = 0, voxelspacing = None, mask = slice(None)):
    """
    Computes the hemispheric intensity difference between the brain hemispheres of an brain image.
    
    Cuts the image along the middle of the supplied cut-plane. This results in two
    images, each containing one of the brains hemispheres.
    
    For each of these two, the following steps are applied:
    1. One image is marked as active image
    2. The other hemisphere image is marked as reference image
    3. The reference image is fliped along the cut_plane
    4. A gaussian smoothing is applied to the active image with the supplied sigma
    5. A gaussian smoothing is applied to the reference image with the supplied sigma
    6. The reference image is substracted from the active image, resulting in the
       difference image for the active hemisphere
    
    Finally, the two resulting difference images are stitched back together, forming a
    hemispheric difference image of the same size as the original.
    
    Note that the supplied gaussian kernel sizes (sigmas) are sensitive to the images
    voxel spacing.
    
    Note: if the number of slices along the cut-plane is odd, the central slice is
    interpolated from the two hemisphere difference images when stitching them back
    together.
    
    @param image a single image or a list/tuple of images (for multi-spectral case)
    @type image ndarray | list of ndarrays | tuple of ndarrays
    @param sigma_active Standard deviation for Gaussian kernel of the active image. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Note that the voxel spacing of the image is taken into account, the given values are treated as mm.
    @type sigma_active scalar or sequence of scalars
    @param sigma_reference Standard deviation for Gaussian kernel of the reference image. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Note that the voxel spacing of the image is taken into account, the given values are treated as mm.
    @type sigma_reference scalar or sequence of scalars
    @param cut_plane The axes along which to cut. This is usually the coronal plane.
    @type cut_plane int
    @param voxelspacing the side-length of each voxel
    @type voxelspacing sequence of floats    
    @param mask a binary mask for the image
    @type mask ndarray
    
    @return the bin values of the local histograms for each voxel
    @rtype ndarray
    
    @raise ArgumentError If the supplied cut-plane dimension is invalid.
    """   
    return __extract_feature(__extract_hemispheric_difference, image, mask, sigma_active = sigma_active, sigma_reference = sigma_reference, cut_plane = cut_plane, voxelspacing = voxelspacing)


def __extract_hemispheric_difference(image, mask = slice(None), sigma_active = 7, sigma_reference = 7, cut_plane = 0, voxelspacing = None):
    """
    Internal, single-image version of @see hemispheric_difference
    """
    # constants
    INTERPOLATION_RANGE = int(10) # how many neighbouring values to take into account when interpolating the medial longitudinal fissure slice
    
    # check arguments
    if cut_plane >= image.ndim:
        raise ArgumentError('The suppliedc cut-plane ({}) is invalid, the image has only {} dimensions.'.format(cut_plane, image.ndim))
    
    # set voxel spacing
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim
    
    # compute the (presumed) location of the medial longitudinal fissure, treating also the special of an odd number of slices, in which case a cut into two equal halves is not possible
    medial_longitudinal_fissure = int(image.shape[cut_plane] / 2)
    medial_longitudinal_fissure_excluded = image.shape[cut_plane] % 2
    
    # split the head into a dexter and sinister half along the saggital plane
    # this is assumed to be consistent with a cut of the brain along the medial longitudinal fissure, thus separating it into its hemispheres
    slicer = [slice(None)] * image.ndim
    slicer[cut_plane] = slice(None, medial_longitudinal_fissure)
    left_hemisphere = image[slicer]

    slicer[cut_plane] = slice(medial_longitudinal_fissure + medial_longitudinal_fissure_excluded, None)
    right_hemisphere = image[slicer]
    
    # flip right hemisphere image along cut plane
    slicer[cut_plane] = slice(None, None, -1)
    right_hemisphere = right_hemisphere[slicer]

    # substract once left from right and once right from left hemisphere, including smoothing steps
    right_hemisphere_difference = __substract_hemispheres(right_hemisphere, left_hemisphere, sigma_active, sigma_reference, voxelspacing)
    left_hemisphere_difference = __substract_hemispheres(left_hemisphere, right_hemisphere, sigma_active, sigma_reference, voxelspacing)
    
    # re-flip right hemisphere image to original orientation
    right_hemisphere_difference = right_hemisphere_difference[slicer]
    
    # estimate the medial longitudinal fissure if required
    if 1 == medial_longitudinal_fissure_excluded:
        left_slicer = [slice(None)] * image.ndim
        right_slicer = [slice(None)] * image.ndim
        left_slicer[cut_plane] = slice(-1 * INTERPOLATION_RANGE, None)
        right_slicer[cut_plane] = slice(None, INTERPOLATION_RANGE)
        interp_data_left = left_hemisphere_difference[left_slicer]
        interp_data_right = right_hemisphere_difference[right_slicer]
        interp_indices_left = range(-1 * interp_data_left.shape[cut_plane], 0)
        interp_indices_right = range(1, interp_data_right.shape[cut_plane] + 1)
        interp_data = numpy.concatenate((left_hemisphere_difference[left_slicer], right_hemisphere_difference[right_slicer]), cut_plane)
        interp_indices = numpy.concatenate((interp_indices_left, interp_indices_right), 0)
        medial_longitudinal_fissure_estimated = interp1d(interp_indices, interp_data, kind='cubic', axis=cut_plane)(0)
        # add singleton dimension
        slicer[cut_plane] = numpy.newaxis
        medial_longitudinal_fissure_estimated = medial_longitudinal_fissure_estimated[slicer]

    # stich images back together
    if 1 == medial_longitudinal_fissure_excluded:
        hemisphere_difference = numpy.concatenate((left_hemisphere_difference, medial_longitudinal_fissure_estimated, right_hemisphere_difference), cut_plane)
    else:
        hemisphere_difference = numpy.concatenate((left_hemisphere_difference, right_hemisphere_difference), cut_plane)

    # extract intensities and return
    return __extract_intensities(hemisphere_difference, mask)

def __extract_local_histogram(image, mask=slice(None), bins=19, rang="image", cutoffp=(0.0, 100.0), size=None, footprint=None, output=None, mode="ignore", origin=0):
    """
    Internal, single-image version of @see local_histogram.
    
    Note:
        Values outside of the histograms range are not considered.
    Note:
        Mode constant is not available, instead a mode "ignore" is provided.
    Note:
        Default dtype of returned values is float.
    """
    if "constant" == mode:
        raise RuntimeError('boundary mode not supported')
    elif "ignore" == mode:
        mode = "constant"
    if 'image' == rang:
        rang = tuple(numpy.percentile(image[mask], cutoffp))
    elif not 2 == len(rang):
        raise RuntimeError('the rang must contain exactly two elements or the string "image"')
        
    _, bin_edges = numpy.histogram([], bins=bins, range=rang)
    output, _ = _get_output(numpy.float if None == output else output, image, shape = [bins] + list(image.shape))

    # threshold the image into the histogram bins represented by the output images first dimension, treat last bin separately, since upper border is inclusive
    for i in range(bins - 1):
        output[i] = (image >= bin_edges[i]) & (image < bin_edges[i + 1])
    output[-1] = (image >= bin_edges[-2]) & (image <= bin_edges[-1])

    # apply the sum filter to each dimension, then normalize by dividing through the sum of elements in the bins of each histogram
    for i in range(bins):
        output[i] = sum_filter(output[i], size=size, footprint=footprint, output=None, mode=mode, cval=0.0, origin=origin)
    divident = numpy.sum(output, 0)
    divident[0 == divident] = 1
    output /= divident
    
    # Notes on modes:
    # mode=constant with a cval outside histogram range for the histogram equals a mode=constant with a cval = 0 for the sum_filter
    # mode=constant with a cval inside  histogram range for the histogram has no equal for the sum_filter (and does not make much sense)
    # mode=X for the histogram equals mode=X for the sum_filter

    # treat as multi-spectral image which intensities to extracted
    return __extract_feature(__extract_intensities, [h for h in output], mask)
    
def __extract_median(image, mask = slice(None), size = 1, voxelspacing = None):
    """
    Internal, single-image version of @see median
    """
    # set voxel spacing
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim
        
    # determine structure element size in voxel units
    size = __create_structure_array(size, voxelspacing)
        
    return __extract_intensities(median_filter(image, size), mask)
    
def __extract_guassian_gradient_magnitude(image, mask = slice(None), sigma = 1, voxelspacing = None):
    """
    Internal, single-image version of @see guassian_gradient_magnitude
    """
    # set voxel spacing
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim
        
    # determine gaussian kernel size in voxel units
    sigma = __create_structure_array(sigma, voxelspacing)
        
    return __extract_intensities(gaussian_gradient_magnitude(image, sigma), mask)
    
def __extract_shifted_mean_gauss(image, mask = slice(None), offset = None, sigma = 1, voxelspacing = None):
    """
    Internal, single-image version of @see shifted_mean_gauss
    """    
    # set voxel spacing
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim
    # set offset
    if offset is None:
        offset = [0] * image.ndim
    
    # determine gaussian kernel size in voxel units
    sigma = __create_structure_array(sigma, voxelspacing)
    
    # compute smoothed version of image
    smoothed = gaussian_filter(image, sigma)
    
    shifted = numpy.zeros_like(smoothed)
    in_slicer = []
    out_slicer = []
    for o in offset:
        in_slicer.append(slice(o, None))
        out_slicer.append(slice(None, -1 * o))
    shifted[out_slicer] = smoothed[in_slicer]
    
    return __extract_intensities(shifted, mask)
    
def __extract_mask_distance(image, mask = slice(None), voxelspacing = None):
    """
    Internal, single-image version of @see mask_distance
    """
    if isinstance(mask, slice):
        mask = numpy.ones(image.shape, numpy.bool)
    
    distance_map = distance_transform_edt(mask, sampling=voxelspacing)
    
    return __extract_intensities(distance_map, mask)
    
def __extract_local_mean_gauss(image, mask = slice(None), sigma = 1, voxelspacing = None):
    """
    Internal, single-image version of @see local_mean_gauss
    """
    # set voxel spacing
    if voxelspacing is None:
        voxelspacing = [1.] * image.ndim
        
    # determine gaussian kernel size in voxel units
    sigma = __create_structure_array(sigma, voxelspacing)
        
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

def __substract_hemispheres(active, reference, active_sigma, reference_sigma, voxel_spacing):
    """
    Helper function for @see __extract_hemispheric_difference.
    Smoothes both images and then substracts the reference from the active image.
    """
    active_kernel = __create_structure_array(active_sigma, voxel_spacing)
    active_smoothed = gaussian_filter(active, sigma = active_kernel)

    reference_kernel = __create_structure_array(reference_sigma, voxel_spacing)
    reference_smoothed = gaussian_filter(reference, sigma = reference_kernel)

    return active_smoothed - reference_smoothed

def __create_structure_array(structure_array, voxelspacing):
    """
    Convenient function to take a structure array (single number valid for all dimensions
    or a sequence with a distinct number for each dimension) assumed to be in mm and
    returns a structure array (a sequence) adapted to the image space using the supplied
    voxel spacing.
    """
    try:
        structure_array = [s / float(vs) for s, vs in zip(structure_array, voxelspacing)]
    except TypeError:
        structure_array = [structure_array / float(vs) for vs in voxelspacing]
    
    return structure_array    

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
