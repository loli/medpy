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
# version r0.2.1
# since 2012-05-28
# status Release

# build-in modules
import os

# third-party modules
import scipy

# own modules
from . import header
from ..core import Logger
from ..core import ImageTypeError, DependencyError,\
    ImageLoadingError

# !TODO: Change to not work with the Exceptions anymore, as these hides bugs!

# code
def load(image):
    r"""
    Loads the ``image`` and returns a ndarray with the image's pixel content as well as
    an image format specific header object.
    
    The type of the returned header object depends on the third party module used to load
    the image. It can, with restrictions, be used to extract additional meta-information
    about the image (e.g. using the methods in :mod:`medpy.io.header`). Additionally it serves
    as meta-data container that can be passes to `~medpy.io.save.save` when the altered
    image is saved to the hard drive again. Note that the transfer of meta-data is only
    possible, and even then not guaranteed, when the source and target image formats are
    the same.
    
    The supported file formats depend on the installed third party modules. This method
    includes support for the NiBabel package and for ITK python wrappers created with
    WrapITK. Note that for the later it is import how it has been compiled.
    
    NiBabel enables support for:
    
        - NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
        - Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
        - and some others (http://nipy.sourceforge.net/nibabel/)
        
    PyDicom:
    
        - Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)
        
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
    your current configuration supports, see :mod:`tests.io.loadsave`. There you can
    find an automated test method.    
    
    Further information:
    
        - http://nipy.sourceforge.net/nibabel/ : The NiBabel python module
        - http://www.cmake.org/Wiki/ITK/File_Formats : Supported file formats and data types by ITK
        - http://code.google.com/p/pydicom/ : The PyDicom python module
    
    
    Internally first tries to figure out the image type and the associated loader to use.
    If this fails due to some reason, a brute-force approach is chosen. In some cases a
    third party module might be able to load an image for which it is not registered as
    responsible.
    
    Parameters
    ----------
    image : string
        Path to the image to load.
    
    Returns
    -------
    image_data : ndarray
        The image data as numpy array.
    image_header : object
        The image metadata as header object to be processed with the methods in :mod:`medpy.io.header`.
    
    Raises
    ------
    ImageLoadingError
        If the image could not be loaded due to some reason.
    ImageTypeError
        If the image type is not supported.
    DependencyError
        If a required third-party module is missing or has been
        compiled without the required support
    """
    ###############################
    # responsibility dictionaries #
    ###############################
    # These dictionaries determine which third-party module is responsible to load which
    # image type. For extending the loaders functionality, just create the required
    # private loader functions (__load_<name>) and register them here.
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
    
    type_to_function = {'nifti': __load_nibabel, # mapping from type string to responsible loader function
                        'analyze': __load_nibabel,
                        'dicom': __load_pydicom,
                        'meta': __load_itk,
                        'nrrd': __load_itk,
                        'png': __load_itk,
                        'bmp': __load_itk,
                        'tif': __load_itk,
                        'jpg': __load_itk}
    
    load_fallback_order = [__load_nibabel, __load_pydicom, __load_itk] # list and order of loader function to use in case of fallback to brute-force
    
    ########
    # code #
    ########
    logger = Logger.getInstance()
    logger.info('Loading image {}...'.format(image))
    
    # Check image file existence
    if not os.path.exists(image):
        raise ImageLoadingError('The supplied image {} does not exist.'.format(image))
    
    # Try normal loading
    try:
        # determine two suffixes (the second one of the compound of the two last elements)
        suffix = image.split('.')[-1].lower()
        if not suffix in suffix_to_type:
            suffix = '.'.join(map(lambda x: x.lower(), image.split('.')[-2:]))
            if not suffix in suffix_to_type: # otherwise throw an Exception that will be caught later on
                raise KeyError()
        # determine image type by ending
        image_type = suffix_to_type[suffix]
        # determine responsible function
        loader = type_to_function[image_type]
        try:
            # load the image
            return loader(image)
        except ImportError as e:
            err = DependencyError('Loading images of type {} requires a third-party module that could not be encountered. Reason: {}.'.format(type_to_string[image_type], e))
        except Exception as e:
            err = ImageLoadingError('Failes to load image {} as {}. Reason signaled by third-party module: {}'.format(image, type_to_string[image_type], e))
    except KeyError:
        err = ImageTypeError('The ending {} of {} could not be associated with any known image type. Supported types are: {}'.format(image.split('.')[-1], image, type_to_string.values()))

    # Try brute force
    logger.debug('Normal loading failed. Entering brute force mode.')
    
    for loader in load_fallback_order:
        try:
            return loader(image)
        except Exception as e:
            logger.debug('Module {} signaled error: {}.'.format(loader, e))
    
    raise err
    
def __load_nibabel(image):
    """
    Image loader using the third-party module nibabel.
    @param image the image to load
    @return A tuple of 1. a scipy array with the image data, 2. a ImageHeader object with additional information
    """
    import nibabel
    
    logger = Logger.getInstance()
    logger.debug('Loading image {} with NiBabel...'.format(image))
    
    img = nibabel.load(image)
    arr = scipy.squeeze(img.get_data())

    return arr, img

def __load_pydicom(image):
    """
    Image loader using the third-party module pydicom.
    @param image the image to load
    @return A tuple of 1. a scipy array with the image data, 2. a ImageHeader object with additional information
    """
    import dicom
    
    logger = Logger.getInstance()
    logger.debug('Loading image {} with PyDicom...'.format(image))
    
    try:
        img = dicom.read_file(image)
    except dicom.filereader.InvalidDicomError as e:
        logger.debug('Module pydicom signaled error: {}. Attempting to force loading nevertheless'.format(e))
        img = dicom.read_file(image, force=True)
    arr = img.pixel_array
    
    # Dicom images are difficult and require special treatment:
    # (1) Usually, when saved as DICOM image, row and solumn direction as exchanged as
    #     compared to other image modailites.
    # (2) Furthermore PyDicom loads DICOM images with the 3rd dimension (Frames/Slices)
    #     in the first numpy ndarray position.
    # Thus, to ensure consistency between the loaded data independent of the 3rd party
    # tool or image format used, we have to
    # (a) transpose the data array, which counters both, point (1) and point (2) in one go
    # (b) flip the first and second (column and row) element of the pixel spacing
    # Note: Strangely the offset i.e. PatientPosition does not have do be flipped... why?  
    pixel_spacing = scipy.asarray(header.get_pixel_spacing(img))
    tmp = float(pixel_spacing[1])
    pixel_spacing[1] = pixel_spacing[0]
    pixel_spacing[0] = tmp
    header.set_pixel_spacing(img, pixel_spacing)
    
    return scipy.transpose(arr), img

def __load_itk(image):
    """
    Image loader using the third-party module itk.
    @param image the image to load
    @return A tuple of 1. a scipy array with the image data, 2. a ImageHeader object with additional information
    """
    import itk
    from ..itkvtk.utilities import itku
    
    logger = Logger.getInstance()
    logger.debug('Loading image {} with ITK...'.format(image))
    
    # determine the image type
    image_type = itku.getImageTypeFromFile(image)
    
    if not image_type:
        raise ImageLoadingError('This image can not be loaded with ITK.')
    
    # load image
    reader = itk.ImageFileReader[image_type].New()
    reader.SetFileName(image)
    reader.Update()
    img = reader.GetOutput()
    
    # convert to scipy
    arr = itku.getArrayFromImage(img)
    
    ############
    # !BUG: WrapITK returns a itk.SS,3 image as pointer, while a itk.US, 4 image is
    # returned as intelligent pointer - what is this?
    ############
    try:
        img_copy = img.New()
        img_copy.Graft(img)
    except Exception:
        img_copy = img.GetPointer().New()
        img_copy.Graft(img.GetPointer())

    return arr, img_copy
