"""
@package medpy.io.load
Provides functionality connected with image loading.
    
The supplied methods hide more complex usage of a number of third party modules.

@author Oskar Maier
@version d0.1.0
@since 2012-05-28
@status Development
"""

# build-in modules
import os

# third-party modules
import scipy

# own modules
from ..core import Logger
from ..core import ImageTypeError, DependencyError,\
    ImageLoadingError

# code
def load(image):
    """
    Tries to load the image found under the supplied path and returns a scipy ndarray
    with its data. Additionally a image specific header object object is returned that
    can be used to save the image with @link io.save_like , keeping the relevant
    meta-data. This works only reliable, when the type in which the image is saved is the
    same as its original type.
    
    Internally first tries to figure out the image type and the associated loader to use.
    If this fails due to some reason, a brute-force approach is chosen. In some cases a
    third party module might be able to load an image for which it is not registered as
    responsible.
    
    @param image the image to load
    @type image string
    
    @return (image_data, image_header) tuple
    @rtype (scipy.ndarray, *)
    
    @raise ImageLoadingError if the image could not be loaded.
    @raise ImageTypeError if the image type is unknown.
    @raise DependencyError if a required third-party module is missing.
    """
    ###############################
    # responsibility dictionaries #
    ###############################
    # These dictionaries determine which third-party module is responsible to load which
    # image type. For extending the loaders functionality, just create the required
    # private loader functions (__load_<name>) and register them here.
    suffix_to_type = {'nii': 'nifti', # mapping from file suffix to type string
                      'gz': 'nifti',
                      'hdr': 'analyze',
                      'img': 'analyze',
                      'dcm': 'dicom',
                      'mhd': 'meta',
                      'png': 'png'}
    
    type_to_string = {'nifti': 'NifTi - Neuroimaging Informatics Technology Initiative (.nii)', # mapping from type string to description string
                      'analyze': 'Analyze (plain, SPM99, SPM2) (.hdr/.img)',
                      'dicom': 'Dicom - Digital Imaging and Communications in Medicine (.dcm)',
                      'meta': 'Itk/Vtk MetaImage (.mhd/.raw)',
                      'png': 'Portable Network Graphics (.png)'}
    
    type_to_function = {'nifti': __load_nibabel, # mapping from type string to responsible loader function
                        'analyze': __load_nibabel,
                        'dicom': __load_pydicom,
                        'meta': __load_itk,
                        'png': __load_itk}
    
    load_fallback_order = {__load_nibabel, __load_pydicom, __load_itk} # list and order of loader function to use in case of fallback to brute-force
    
    
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
        # determine image type by ending
        image_type = suffix_to_type[image.split('.')[-1]]
        # determine responsible function
        loader = type_to_function[image_type]
        # load the image
        return loader(image)
    except KeyError:
        err = ImageTypeError('The ending {} of {} could not be associated with any known image type. Supported types are: {}'.format(image.split('.')[-1], image, type_to_string.values()))
    except ImportError as e:
        err = DependencyError('Loading images of type {} requires a third-party module that could not be encountered. Reason: {}.'.format(type_to_string[image_type], e))
    except Exception as e:
        raise
        err = ImageLoadingError('Failes to load image {} as {}. Reason signaled by third-party module: {}'.format(image, type_to_string[image_type], e))
        
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
    
    img = dicom.ReadFile(image)
    arr = img.PixelArray
    
    return arr, img

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
    itk_py_converter = itk.PyBuffer[image_type]
    arr = itk_py_converter.GetArrayFromImage(img)
    
    ############
    # !BUG: WarpITK is a very critical itk wrapper. Everything returned / created by it
    # seems to exist only inside the scope of the current function (at least for 
    # ImageFileReader's image and PyBuffers's scipy array. The returned objects have
    # therefore to be copied once, to survive outside the current scope.
    ############
    ############
    # !BUG: WrapITK returns a itk.SS,3 image as pointer, while a itk.US, 4 image is
    # returned as intelligent pointer - what is this?
    ############
    arr = arr.copy()
    try:
        img_copy = img.New()
        img_copy.Graft(img)
    except Exception:
        img_copy = img.GetPointer().New()
        img_copy.Graft(img.GetPointer())

    return arr, img_copy
