"""
@package medpy.io.header
Provides functionality to access the image headers.
    
The supplied methods hide more complex usage of a number of third party modules.

@author Oskar Maier
@version r0.1.1
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
    
    raise AttributeError('The provided header {} is of unknown type or does not support queries for pixel spacing.'.format(type(hdr)))

def set_pixel_spacing(hdr, spacing):
    """
    Sets the pixels spacing in an image header.
    
    @param hdr and image header as returned by @link io.load.load()
    @type object
    @param spacing the desired pixel spacing
    @type spacing sequence
    """
    exception = False
    try:
        return __set_pixel_spacing_nibabel(hdr, spacing)
    except AttributeError as e:
        if not exception: exception = e
    except Exception: pass
    try:
        return __set_pixel_spacing_pydicom(hdr, spacing)
    except AttributeError as e:
        if not exception: exception = e
    except Exception: pass
    try:
        return __set_pixel_spacing_itk(hdr, spacing)
    except AttributeError as e:
        if not exception: exception = e
    except Exception: pass
        
    if exception: raise exception
    
    raise AttributeError('The provided header {} is of unknown type or does not support setting of pixel spacing.'.format(type(hdr)))    

def __get_pixel_spacing_itk(hdr):
    return tuple([hdr.GetSpacing().GetElement(x) for x in range(hdr.GetSpacing().GetVectorDimension())])
    
def __get_pixel_spacing_nibabel(hdr):
    return hdr.get_header().get_zooms()

def __get_pixel_spacing_pydicom(hdr):
    if "SpacingBetweenSlices" in hdr:
        return tuple(hdr.PixelSpacing + [hdr.SpacingBetweenSlices])
    else:
        return tuple(hdr.PixelSpacing)
    
def __set_pixel_spacing_itk(hdr, spacing):
    """
    Set the spacing value of the ITK header to spacing.
    
    @param hdr a valid ITK image
    @param spacing a sequence of numbers
    """
    if not hdr.GetSpacing().GetVectorDimension() == len(spacing):
        raise AttributeError('Vector dimensions of header ({}) and supplied spacing sequence ({}) differ.'.format(hdr.GetSpacing().GetVectorDimension(), len(spacing)))
    for i in range(hdr.GetSpacing().GetVectorDimension()):
        hdr.GetSpacing().SetElement(i, float(spacing[i]))
                            
def __set_pixel_spacing_nibabel(hdr, spacing):
    """
    Set the spacing value of the Nibabel header to spacing.
    
    @param hdr a valid NiBabel image
    @param spacing a sequence of numbers
    """
    if not len(hdr.get_header().get_zooms()) == len(spacing):
        raise AttributeError('Vector dimensions of header ({}) and supplied spacing sequence ({}) differ.'.format(len(hdr.get_header().get_zooms()), len(spacing)))
    hdr.get_header().set_zooms([float(x) for x in spacing])    
    
def __set_pixel_spacing_pydicom(hdr, spacing):
    """
    Set the spacing value of the PyDicom header to spacing.
    
    @param hdr a valid PyDicom image
    @param spacing a sequence of numbers
    """
    if not len(spacing) <= 3:
        raise AttributeError('PyDicom supports a maximum dimensionality of 3, the supplied spacing sequence contains {} elements.'.format(len(spacing)))
    
    if len(spacing) >= 2:
        if "PixelSpacing" in hdr:
            hdr.PixelSpacing = [float(x) for x in spacing[0:2]]
    if len(spacing) >= 3:
        if "SpacingBetweenSlices" in hdr:
            hdr.SpacingBetweenSlices = float(spacing[2])
    
def __update_header_from_array_nibabel(hdr, arr):
    """
    Update an original nibabel header with the data extracted from a scipy.ndarray.
    """
    hdr.get_header().set_data_shape(arr.shape)
    hdr.get_header().set_data_dtype(arr.dtype)

def __is_header_pydicom(hdr):
    """
    Returns true is the supplied object is a valid pydicom image, otherwise False.
    """
    import dicom
    return (type(hdr) == dicom.dataset.FileDataset)

def __is_header_nibabel(hdr):
    """
    Returns true is the supplied object is a valid nibabel image holding a header attribute, otherwise False.
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
