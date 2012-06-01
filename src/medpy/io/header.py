"""
@package medpy.io.header
Provides functionality to access the image headers.
    
The supplied methods hide more complex usage of a number of third party modules.

@author Oskar Maier
@version r0.1.0
@since 2012-06-01
@status Release
"""

# build-in modules

# third-party modules

# own modules

# code
def get_pixel_spacing(hdr):
    """
    Extracts the pixels spacing from an image header.
    
    @param hdr and image header as returned by @link io.load.load()
    @type object
    
    @return the image's pixel spacing
    @rtype tuple
    """
    try:
        return __get_pixel_spacing_nibabel(hdr)
    except Exception: pass
    try:
        return __get_pixel_spacing_pydicom(hdr)
    except Exception: pass
    try:
        return __get_pixel_spacing_itk(hdr)
    except Exception: pass
    
    raise AttributeError('The provided header is of unknown type {}.'.format(type(hdr)))

def __get_pixel_spacing_itk(hdr):
    return tuple([hdr.GetSpacing().GetElement(x) for x in range(hdr.GetSpacing().GetVectorDimension())])
    
def __get_pixel_spacing_nibabel(hdr):
    return hdr.get_header().get_zooms()

def __get_pixel_spacing_pydicom(hdr):
    if "SpacingBetweenSlices" in hdr:
        return tuple(hdr.PixelSpacing + [hdr.SpacingBetweenSlices])
    else:
        return tuple(hdr.PixelSpacing)
    
    
def __update_header_from_array_nibabel(hdr, arr):
    """
    Update an original nibabel header with the data extracted from a scipy.ndarray.
    """
    hdr.get_header().set_data_shape(arr.shape)
    hdr.get_header().set_data_dtype(arr.dtype)

def __is_header_pydicom(hdr):
    """
    """
    import dicom
    return (type(hdr) == dicom.dataset.FileDataset)

def __is_header_nibabel(hdr):
    """
    Returns true is the supplied object is a valid itk image, otherwise False.
    """
    try:
        hdr.get_header()
        return True
    except Exception:
        return False

def __is_header_itk(hdr):
    """
    Returns true is the supplied object is a valid itk image, otherwise False.
    """
    import itk
    for cl in itk.Image.__template__.itervalues():
        if cl in type(hdr).__bases__: return True
    return False 