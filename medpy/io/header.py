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
# version r0.1.3
# since 2012-06-01
# status Release

# build-in modules

# third-party modules
import numpy

# own modules
from ..core import Logger

# !TODO: Turn into an own class, with sub-classes for each 3rd party type (see _header.py).

# code
def get_pixel_spacing(hdr):
    r"""
    Extracts the pixels spacing from an image header.
    
    Parameters
    ----------
    hdr : object
        An image header as returned by `load`.
    
    Returns
    -------
    pixel_spacing : tuple of floats
        The image's pixel spacing.
        
    Raises
    ------
    AttributeError
        If the header is of an unknown type or does not support the reading of the pixel spacing.
    """
    try:
        if __is_header_nibabel(hdr):
            return __get_pixel_spacing_nibabel(hdr)
        elif __is_header_pydicom(hdr):
            return __get_pixel_spacing_pydicom(hdr)
        elif __is_header_itk(hdr):
            return __get_pixel_spacing_itk(hdr)
        else:
            raise Exception()
    except Exception:
        raise AttributeError('The provided header {} is of unknown type or does not support queries for pixel spacing.'.format(type(hdr)))

def get_offset(hdr):
    r"""
    Extracts the image offset from an image header.
    
    Parameters
    ----------
    hdr : object
        An image header as returned by `load`.
    
    Returns
    -------
    offset : tuple of floats
        The image's offset.
    
    Raises
    ------
    AttributeError
        If the header is of an unknown type or does not support the reading of the offset.
    
    Notes
    -----
    Usually it can be assumed that the offset is measured from the center point of
    the first pixel, but this does not hold true for ITK versions < 3.16 and even for
    later it can not be assured, as some compile flags change the behaviour.
    
    The Analyze format does not specify a header field for the offset, thus zeros
    are returned in this case.
    """
    try:
        if __is_header_nibabel(hdr):
            return __get_offset_nibabel(hdr)
        elif __is_header_pydicom(hdr):
            return __get_offset_pydicom(hdr)
        elif __is_header_itk(hdr):
            return __get_offset_itk(hdr)
        else:
            raise Exception()
    except Exception:
        raise AttributeError('The provided header {} is of unknown type or does not support queries for offsets.'.format(type(hdr)))        

def set_pixel_spacing(hdr, spacing):
    r"""
    Sets the pixels spacing in an image header.
    
    Parameters
    ----------
    hdr : object
        An image header as returned by `load`.
    pixel_spacing : tuple of floats
        The desired pixel spacing.
        
    Raises
    ------
    AttributeError
        If the header is of an unknown type or does not support the setting of the pixel spacing.
    """
    try:
        if __is_header_nibabel(hdr):
            __set_pixel_spacing_nibabel(hdr, spacing)    
        elif __is_header_pydicom(hdr):
            __set_pixel_spacing_pydicom(hdr, spacing)
        elif __is_header_itk(hdr):
            __set_pixel_spacing_itk(hdr, spacing)
        else:
            raise Exception()
    except AttributeError as e:
        raise e
    except Exception:
        raise AttributeError('The provided header {} is of unknown type or does not support setting of pixel spacing.'.format(type(hdr)))

def set_offset(hdr, offset):
    r"""
    Sets the offset in the image header.
    
    Parameters
    ----------
    hdr : object
        An image header as returned by `load`.
    offset : tuple of floats
        The desired offset.
        
    Raises
    ------
    AttributeError
        If the header is of an unknown type or does not support the setting of the offset.
        
    Notes
    -----
    The offset is usually based on the center of the first voxel.
    See also `get_offset` for more details.
    """
    try:
        if __is_header_nibabel(hdr):
            __set_offset_nibabel(hdr, offset)
        elif __is_header_pydicom(hdr):
            __set_offset_pydicom(hdr, offset)
        elif __is_header_itk(hdr):
            __set_offset_itk(hdr, offset)
        else:
            raise Exception()
    except AttributeError as e:
        raise e
    except Exception:
        raise AttributeError('The provided header {} is of unknown type or does not support setting of offsets.'.format(type(hdr)))    

def copy_meta_data(hdr_to, hdr_from):
    r"""
    Copy image meta data (voxel spacing and offset) from one header to another.
    
    Parameters
    ----------
    hdr_to : object
        An image header as returned by `load`.
    hdr_from : object
        An image header as returned by `load`.
        
    Raises
    ------
    AttributeError
        If one of the headers does not support the reading respectively writing of metadata.
    """
    logger = Logger.getInstance()
    try:
        set_pixel_spacing(hdr_to, get_pixel_spacing(hdr_from))
    except AttributeError as e:
        logger.warning('The voxel spacing could not be set correctly. Signaled error: {}'.format(e))
    try:
        set_offset(hdr_to, get_offset(hdr_from))
    except AttributeError as e:
        logger.warning('The image offset could not be set correctly. Signaled error: {}'.format(e))


def __get_pixel_spacing_itk(hdr):
    return tuple([hdr.GetSpacing().GetElement(x) for x in range(hdr.GetSpacing().GetVectorDimension())])
    
def __get_pixel_spacing_nibabel(hdr):
    dimensionality = sum(0 if 1 == x else 1 for x in hdr.shape) # required for Analyze format, which always assumes for dimensions, even if less present
    return hdr.get_header().get_zooms()[0:dimensionality]

def __get_pixel_spacing_pydicom(hdr):
    """
    @note The SpacingBetweenSlices gives the distance between the slice centers, while
          SliceThickness gives the actual SliceThickness. This means that
          SpacingBetweenSlices must contain a value as least as high as SliceThickness if
          no overlap between the slices exists. We choose to simply query the
          SliceThickness, as this value determines the thickness of the voxels.
          But we flag a warning, if there might be a gap or overlap.
    """
    # 1. Check if PixelSpacing element is present
    if "PixelSpacing" in hdr:
        spacing = [x for x in hdr.PixelSpacing] # has to be copy, otherwise the value of the field is changed when spacing gets manipulated
    else:
        logger = Logger.getInstance()
        logger.warning('No pixel spacing defined in DICOM header, assuming isotropic spacing.')
        spacing = [1] * 2
        
    # Skip here if the number of frames is present and 1 or below, we ignore other values in this case
    if "NumberOfFrames" in hdr and hdr.NumberOfFrames <= 1: # 2d case
        return tuple(map(float, spacing))
        
    # 2. Check if SliceThickness element is present
    if "SliceThickness" in hdr:
        if "SpacingBetweenSlices" in hdr and hdr.SliceThickness != hdr.SpacingBetweenSlices:
            logger = Logger.getInstance()
            logger.debug('The DICOM headers SliceThickness tag does not correspond with the SpacingBetweenSlices tag. There might be gaps or overlaps between the slices.')
        spacing += [hdr.SliceThickness]
    elif "SpacingBetweenSlices" in hdr:
        logger = Logger.getInstance()
        logger.debug('No SliceThickness defined in DICOM header, falling back to SpacingBetweenSlices.')
        spacing += [hdr.SpacingBetweenSlices]
    elif "NumberOfFrames" in hdr and hdr.NumberOfFrames > 1: # 3d case \wo a given SliceThickness
        logger = Logger.getInstance()
        logger.debug('No SliceThickness defined in DICOM header, assuming isotropic spacing.')
        spacing += [1]
        
    return tuple(map(float, spacing))
    
def __get_offset_nibabel(hdr):
    """
    @note Only Nifit has full support for image offsets. The two Analyze versions SPM2
          and SPM99 can also define offsets, but the definition is rather unclear.
          Instead zero sequences are returned in these cases, which is the standard
          behaviour.
    """ 
    import nibabel
    if type(hdr) == nibabel.nifti1.Nifti1Image or type(hdr) == nibabel.nifti1.Nifti1Pair: # The nifti image format supports offsets
        hdr_real = hdr.get_header()
        offset = [float(hdr_real['qoffset_x']), float(hdr_real['qoffset_y']), float(hdr_real['qoffset_z']), float(hdr_real['toffset'])][0:len(hdr.shape)]
        # multiply with sign of diagonal of voxel-to-world affine to account for axis directions
        axis_directions = numpy.sign(numpy.diagonal(hdr.get_affine())) 
        offset_corrected = numpy.multiply(offset, axis_directions[0:len(offset)])
        return tuple(offset_corrected)
    else: # An Analyze or other image format
        dimensionality = sum(0 if 1 == x else 1 for x in hdr.shape) # required for Analyze format, which always assumes four dimensions, even if less present
        return tuple([0 for _ in range(len(hdr.shape))][0:dimensionality])

def __get_offset_pydicom(hdr):
    if "NumberOfFrames" in hdr and hdr.NumberOfFrames > 1: # 3D case
        if "ImagePositionPatient" in hdr:
            return tuple(map(float, hdr.ImagePositionPatient))
        else:
            logger = Logger.getInstance()
            logger.warning('No offset defined in DICOM header, assuming none exists.')
            return tuple([0] * 3)
    else: # 2D case
        if "ImagePositionPatient" in hdr:
            return tuple(map(float, hdr.ImagePositionPatient)[:2])
        else:
            logger = Logger.getInstance()
            logger.warning('No offset defined in DICOM header, assuming none exists.')
            return tuple([0] * 2)

def __get_offset_itk(hdr):
    origin = hdr.GetOrigin()
    return tuple([origin.GetElement(i) for i in range(origin.Size())])
    
    
def __set_offset_nibabel(hdr, offset):
    """
    @note Only works for Nifti images, not for Analyze or other formats.
    """
    import nibabel
    if type(hdr) == nibabel.nifti1.Nifti1Image or type(hdr) == nibabel.nifti1.Nifti1Pair: # The nifti image format supports offsets
        # check if the offset is of the expected length
        if not len(hdr.shape) == len(offset):
            raise AttributeError('Vector dimensions of header ({}) and supplied offset sequence ({}) differ.'.format(len(hdr.shape), len(offset)))
        # check if the offset is too long
        if not len(offset) <= 4:
            raise AttributeError('Nifti supports a maximum offset of 4 elements (x, y, z and t), got {}. Note that Nifit naturally does not support images of more than 4 dimensions, although it can handle them.'.format(len(offset)))
        # set offset in header
        mapping = ['qoffset_x', 'qoffset_y', 'qoffset_z', 'toffset']
        hdr_real = hdr.get_header()
        for i in range(len(offset)):
            hdr_real[mapping[i]] = offset[i]
    else:
        raise Exception() # always caught and dismissed
    
def __set_offset_pydicom(hdr, offset):
    if not len(hdr.pixel_array.shape) == len(offset):
        raise AttributeError('Vector dimensions of header ({}) and supplied offset sequence ({}) differ.'.format(len(hdr.pixel_array.shape), len(offset)))
    hdr.ImagePositionPatient = map(float, offset)
    
def __set_offset_itk(hdr, offset):
    origin = hdr.GetOrigin()
    if not origin.Size() == len(offset):
        raise AttributeError('Vector dimensions of header ({}) and supplied offset sequence ({}) differ.'.format(origin.Size(), len(offset)))
    for i, o in enumerate(offset):
        origin.SetElement(i, o)
    
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
    
    @note The SpacingBetweenSlices gives the distance between the slice centers, while
          SliceThickness gives the actual SliceThickness. This means that
          SpacingBetweenSlices must contain a value as least as high as SliceThickness if
          no overlap between the slices exists. We choose to set both to the same value
          when setting the pixel spacing, assuming neither overlap nor unrecorded image
          space between the slice, which seems to be the normal behaviour. 
    
    @param hdr a valid PyDicom image
    @param spacing a sequence of numbers
    """
    if not len(spacing) <= 3:
        raise AttributeError('PyDicom supports a maximum dimensionality of 3, the supplied spacing sequence contains {} elements.'.format(len(spacing)))
    
    if len(spacing) >= 2:
        hdr.PixelSpacing = [float(x) for x in spacing[0:2]]
    if len(spacing) >= 3:
        hdr.SliceThickness = float(spacing[2])
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
    # try to convert pointer from smart pointer to normal pointer
    try:
        hdr = hdr.GetPointer()
    except Exception:
        pass
    # see if itk header type
    for cl in itk.Image.__template__.itervalues():
        if cl in type(hdr).__bases__: return True
    return False
