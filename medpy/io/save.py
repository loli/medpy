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
# since 2012-05-28
# status Release

# build-in modules
import os

# third-party modules
import scipy

# own modules
from ..core import Logger
from ..core import ImageTypeError, DependencyError,\
    ImageSavingError
from .header import __update_header_from_array_nibabel,\
    __is_header_itk, __is_header_nibabel, copy_meta_data

# !TODO: Change to not work with the Exceptions anymore, as these hides bugs!

# code
def save(arr, filename, hdr = False, force = True):
    r"""
    Save the image ``arr`` as filename using information encoded in ``hdr``. The target image
    format is determined by the ``filename`` suffix. If the ``force`` parameter is set to true,
    an already existing image is overwritten silently. Otherwise an error is thrown.
    
    The header (``hdr``) object is the one returned by `~medpy.io.load.load` and is only used
    if the source and target image formats are the same.
    
    Generally this function does not guarantee, that metadata other than the image shape
    and pixel data type are kept.
    
    
    The supported file formats depend on the installed third party modules. This method
    includes support for the NiBabel package and for ITK python wrappers created with
    WrapITK. Note that for the later it is import how it has been compiled.
    
    NiBabel enables support for:
    
        - NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
        - Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
        - and some others (http://nipy.sourceforge.net/nibabel/)
        
    WrapITK enables support for:
    
        - NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
        - Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
        - Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)
        - Itk/Vtk MetaImage (.mhd, .mha/.raw)
        - Nrrd - Nearly Raw Raster Data (.nhdr, .nrrd)
        - and many others (http://www.cmake.org/Wiki/ITK/File_Formats)
        
    Generally we advise to use the nibabel third party tool, which is implemented in pure
    python and whose support for Nifti (.nii) and Analyze 7.5 (.hdr/.img) is excellent
    and comprehensive.
        
    For informations about which image formats, dimensionalities and pixel data types
    your current configuration supports, see :mod:`test.io.loadsave` . There you can
    find an automated test method.
                
    Some known restrictions are explicit, independent of the third party modules or how
    they were compiled:
    
        - DICOM does not support images of 4 or more dimensions (Danger: ITK actually
          saves the image without signaling an error. But the dimensionality is reduced
          to 3 dimensions).
        - DICOM does not support pixel data of uint32/64 and float32/64/128.
        - ITK does not support images with less than 2 dimensions.
        - ITK does not support pixel data of uint64, int64 and float128.
        - JPEG, PIC are unstable in the sense, that differences between the saved and the
          loaded data can occure.
        - GIPL images are always loaded as 3D, even if they have been saved as 2D images.
        - PNG images are always loaded as 2D, even if they have been saved as 3D images.
    
    Further information:
    
        - http://nipy.sourceforge.net/nibabel/ : The NiBabel python module
        - http://www.cmake.org/Wiki/ITK/File_Formats : Supported file formats and data types by ITK
        - http://code.google.com/p/pydicom/ : The PyDicom python module
    
    Parameters
    ----------
    arr : array_like
        The image data.
    filename : string
        Where to save the image; path and filename including the image suffix.
    hdr : object
        The image header containing the metadata.
    force : bool
        Set to True to overwrite already exiting image silently.
    
    Raises
    ------
    ImageTypeError
        If attempting to save as an unsupported image type.
    DependencyError
        If an required third party module is not existent or has been
        compiled without support for the target image format
    ImageSavingError
        If the image could not be saved due to various reasons
    """
    ###############################
    # responsibility dictionaries #
    ###############################
    # These dictionaries determine which third-party module is responsible to save which
    # image type. For extending the loaders functionality, just create the required
    # private loader functions (__save_<name>) and register them here.
    suffix_to_type = {'nii': 'nifti', # mapping from file suffix to type string
                      'nii.gz': 'nifti',
                      'hdr': 'analyze',
                      'img': 'analyze',
                      'img.gz': 'analyze',
                      'dcm': 'dicom',
                      'dicom': 'dicom',
                      'mhd': 'meta',
                      'mha': 'meta',
                      'nrrd': 'nrrd',
                      'nhdr': 'nrrd',
                      'png': 'png',
                      'bmp': 'bmp',
                      'tif': 'tif',
                      'tiff': 'tif',
                      'jpg': 'jpg',
                      'jpeg': 'jpg'}
    
    type_to_string = {'nifti': 'NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)', # mapping from type string to description string
                      'analyze': 'Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)',
                      'dicom': 'Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)',
                      'meta': 'Itk/Vtk MetaImage (.mhd, .mha/.raw)',
                      'nrrd': 'Nrrd - Nearly Raw Raster Data (.nhdr, .nrrd)',
                      'png': 'Portable Network Graphics (.png)',
                      'bmp': 'Bitmap Image File (.bmp)',
                      'tif': 'Tagged Image File Format (.tif,.tiff)',
                      'jpg': 'Joint Photographic Experts Group (.jpg, .jpeg)'}
    
    type_to_function = {'nifti': __save_nibabel, # mapping from type string to responsible loader function
                        'analyze': __save_nibabel,
                        'dicom': __save_itk,
                        'meta': __save_itk,
                        'nrrd': __save_itk,
                        'png': __save_itk,
                        'bmp': __save_itk,
                        'tif': __save_itk,
                        'jpg': __save_itk}
    
    save_fallback_order = [__save_nibabel, __save_itk] # list and order of loader function to use in case of fallback to brute-force
    
    ########
    # code #
    ########
    logger = Logger.getInstance()
    logger.info('Saving image as {}...'.format(filename))
    
    # Check image file existence
    if not force and os.path.exists(filename):
        raise ImageSavingError('The target file {} already exists.'.format(filename))
    
    # Try normal saving
    try:
        # determine two suffixes (the second one of the compound of the two last elements)
        suffix = filename.split('.')[-1].lower()
        if not suffix in suffix_to_type:
            suffix = '.'.join(map(lambda x: x.lower(), filename.split('.')[-2:]))
            if not suffix in suffix_to_type: # otherwise throw an Exception that will be caught later on
                raise KeyError()
        # determine image type by ending
        image_type = suffix_to_type[suffix]
        # determine responsible function
        saver = type_to_function[image_type]
        try:
            # load the image
            return saver(arr, hdr, filename)
        except ImportError as e:
            raise DependencyError('Saving images of type {} requires a third-party module that could not be encountered. Reason: {}.'.format(type_to_string[image_type], e))
        except Exception as e:
            raise ImageSavingError('Failed to save image {} as type {}. Reason signaled by third-party module: {}'.format(filename, type_to_string[image_type], e))
    except KeyError:
        raise ImageTypeError('The ending {} of {} could not be associated with any known image type. Supported types are: {}'.format(filename.split('.')[-1], filename, type_to_string.values()))
        
    # Try brute force
    logger.debug('Normal saving failed. Entering brute force mode.')
    for saver in save_fallback_order:
        try:
            return saver(arr, hdr, filename)
        except Exception as e:
            logger.debug('Module {} signaled error: {}.'.format(saver, e))
    
    raise err

def __save_itk(arr, hdr, filename):
    """
    Image saver using the third-party module itk.
    @param arr the image data
    @param hdr the image header with met-information
    @param filename the target location
    """
    import itk
    from medpy.itkvtk.utilities import itku

    logger = Logger.getInstance()
    logger.debug('Saving image as {} with Itk...'.format(filename))

    # determine image type from array
    image_type = itku.getImageTypeFromArray(arr)

    # convert array to itk image
    try:
        img = itku.getImageFromArray(arr)
    except KeyError:
        raise DependencyError('The itk python PyBuffer transition object was compiled without support for image of type {}.'.format(image_type))

    # if original image object was provided with hdr, try to use it for creating the image object
    if __is_header_itk(hdr):
        # save original image shape / largest possible region
        shape = []
        for i in range(img.GetLargestPossibleRegion().GetImageDimension()):
            shape.append(img.GetLargestPossibleRegion().GetSize().GetElement(i))

        # copy meta data
        try:
            img.CopyInformation(hdr.GetPointer())
            # reset largest possible region / shape to original value
            for i in range(len(shape)):
                img.GetLargestPossibleRegion().GetSize().SetElement(i, shape[i])
        except RuntimeError as e: # raised when the meta data information could not be copied (e.g. when the two images ndims differ)
            logger.debug('The meta-information could not be copied form the old header. CopyInformation signaled: {}.'.format(e))
            pass
        
    elif hdr: # otherwise copy meta-data information as far as possible
        copy_meta_data(img, hdr)
    
    # save the image
    writer = itk.ImageFileWriter[image_type].New()
    writer.SetFileName(filename)
    writer.SetInput(img.GetPointer())
    writer.Update()
    
def __save_nibabel(arr, hdr, filename):
    """
    Image saver using the third-party module nibabel.
    @param arr the image data
    @param hdr the image header with met-information
    @param filename the target location
    """
    import nibabel
    from ..utilities import nibabelu

    logger = Logger.getInstance()
    logger.debug('Saving image as {} with NiBabel...'.format(filename))
    
    # convert type bool to int8
    if scipy.bool_ == arr.dtype:
        arr = arr.astype(scipy.uint8)
    
    # if original image object was provided with hdr, try to use it for creating the image object
    if hdr and __is_header_nibabel(hdr):        
        __update_header_from_array_nibabel(hdr, arr)
        image = nibabelu.image_like(arr, hdr)
    # if not, create new image object and copy meta data as far as possible
    else:
        image = nibabelu.image_new(arr, filename)
        if hdr: copy_meta_data(image, hdr)
        
    # save image
    nibabel.save(image, filename)
