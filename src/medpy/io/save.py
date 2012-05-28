"""
@package medpy.io.save
Provides functionality connected with image saving.
    
The supplied methods hide more complex usage of a number of third party modules.

@author Oskar Maier
@version d0.1.0
@since 2012-05-28
@status Development
"""

# build-in modules
import os

# third-party modules

# own modules
from imageheader import ImageHeader # why does from ..io not work
from ..core import Logger
from ..core import ImageTypeError, DependencyError,\
    ImageSavingError

def save(arr, filename, hdr = False, force = True):
    """
    Tries to save the supplied image data array as filename. If a header object (ImageHeader) is
    supplied, it it used to obtain meta information about the image.
    
    The order of the meta-data priority, i.e. which information are used to save the
    image, are as follows:
        highest: the image data in the array (shape, dtype and dimensions)
        highest: data extracted from ImageHeader
        lowest: the original header eventually carried with the ImageHeader object
                (these objects can carry additional meta information, that can not be
                stored in the array or in the ImageHeader object) 
    
    @param arr the image data
    @type arr scipy.ndarray
    @param filename where to save the image, path and filename including the image suffix
    @type filename string
    @param hdr the image header
    @type hdr ImageHeader
    @param force set to True to overwrite already exiting image silently
    @type force bool
    """
    ###############################
    # responsibility dictionaries #
    ###############################
    # These dictionaries determine which third-party module is responsible to save which
    # image type. For extending the loaders functionality, just create the required
    # private loader functions (__save_<name>) and register them here.
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
    
    type_to_function = {'nifti': __save_nibabel, # mapping from type string to responsible loader function
                        'analyze': __save_nibabel,
                        'dicom': __save_pydicom,
                        'meta': __save_itk,
                        'png': __save_itk}
    
    save_fallback_order = {__save_nibabel, __save_pydicom, __save_itk} # list and order of loader function to use in case of fallback to brute-force
    
    ########
    # code #
    ########
    logger = Logger.getInstance()
    logger.info('Saving image as {}...'.format(filename))
    
    # Check image file existence
    if not force and os.path.exists(filename):
        raise ImageSavingError('The target file {} already exists.'.format(filename))
    
    # create minimal header if not supplied
    if not hdr: hdr = ImageHeader()
    
    # Try normal saving
    try:
        # determine image type by ending
        image_type = suffix_to_type[filename.split('.')[-1]]
        # determine responsible function
        saver = type_to_function[image_type]
        # load the image
        return saver(arr, hdr, filename)
    except KeyError:
        err = ImageTypeError('The ending {} of {} could not be associated with any known image type. Supported types are: {}'.format(filename.split('.')[-1], filename, type_to_string.values()))
    except ImportError as e:
        err = DependencyError('Saving images of type {} requires a third-party module that could not be encountered. Reason: {}.'.format(type_to_string[image_type], e))
    except Exception as e:
        err = ImageSavingError('Failed to save image {} as type {}. Reason signaled by third-party module: {}'.format(filename, type_to_string[image_type], e))
        
    # Try brute force
    logger.debug('Normal saving failed. Entering brute force mode.')
    for saver in save_fallback_order:
        try:
            return saver(arr, hdr, filename)
        except Exception as e:
            logger.debug('Module {} signaled error: {}.'.format(saver, e))
    
    raise err    

def __save_pydicom(arr, hdr, filename):
    raise NotImplementedError()

def __save_itk(arr, hdr, filename):
    raise NotImplementedError()
    
def __save_nibabel(arr, hdr, filename):
    """
    Image saver using the third-party module nibabel.
    @param arr the image data
    @param hdr the image header with met-information
    @param filename the target location
    """
    import nibabel # cupla de nibabel!
    from ..utilities.nibabel import image_like

    logger = Logger.getInstance()
    logger.debug('Saving image as {} with NiBabel...'.format(filename))
    
    # if original image object was provided with hdr, try to use it for creating the image object
    if hdr.get_original_header() and nibabel.spatialimages.SpatialImage == type(hdr.get_original_header()):
        image = hdr.get_original_header()
        __update_header_from_imageheader_nibabel(image.get_header(), hdr)
        __update_header_from_array_nibabel(image.get_header(), arr)
        image = image_like(arr, hdr.get_original_header())
    # if not, create new image object
    else:
        image = __create_image_nibabel(arr)
        __update_header_from_imageheader_nibabel(image.get_header(), hdr)
        
    # save image
    nibabel.save(image, filename)

def __create_image_nibabel(arr):
    """
    Creates a nibabel image object of a desired type from an array.
    """
    import nibabel
    return nibabel.spatialimages.SpatialImage(arr, None)

def __update_header_from_array_nibabel(hdr, arr):
    """
    Update an original nibabel header with the data extracted from a scipy.ndarray.
    """
    hdr.set_data_shape(arr.shape)
    hdr.set_data_dtype(arr.dtype)
    
def __update_header_from_imageheader_nibabel(hdr, ihdr):
    """
    Update an original nibabel header with the data extracted from a ImageHeader.
    """
    hdr.set_zooms(ihdr.get_slice_spacing())
