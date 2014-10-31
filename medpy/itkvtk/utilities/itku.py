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
# version r0.5.1
# since 2011-11-25
# status Release

# build-in modules

# third-party modules
import scipy
import itk

# path changes

# own modules
from ...core import ImageLoadingError, DependencyError, ImageTypeError, Logger

# code
def getInformation(image): # tested
    """
    Returns an information string about a ITK image in a compressed way.
    
    Parameters
    ----------
    image : itk.Image
        An ITK image as used by WrapITK.
        
    Returns
    -------
    information : string
        Pretty-formatted string with image metadata.
        
    Notes
    -----
    Performs UpdateOutputInformation() on the image, therefore triggering pipeline processing if necessary
    Only works on 3D images.
    """
    # refresh information
    image.UpdateOutputInformation()
    
    # request information and format string
    s = 'itkImageData info:\n'
    s += '\tscalar-type: {}\n'.format(str(itk.template(image)[1][0]))
    rs = image.GetLargestPossibleRegion().GetSize()
    s += '\tdimensions: {}\n'.format([rs.GetElement(x) for x in range(rs.GetSizeDimension())])
    sp = image.GetSpacing()
    s += '\tspacing: {}\n'.format([sp.GetElement(x) for x in range(rs.GetSizeDimension())])
    o = image.GetOrigin()
    s += '\torigin: {}\n'.format([o.GetElement(x) for x in range(rs.GetSizeDimension())]) 
    s += '\tdata dim.: {}'.format(str(itk.template(image)[1][1])) # alternative impl. for when GetImageDimension() fails 
    
    return s

def getInformationWithScalarRange(image): # tested
    """
    Behaves like `getInformation` but also computes the intensity range, which is computationally expensive.
          
    Parameters
    ----------
    image : itk.Image
        An ITK image as used by WrapITK.
        
    Returns
    -------
    information : string
        Pretty-formatted string with image metadata and intensity range.
        
    Notes
    -----
    Performs UpdateOutputInformation() on the image, therefore triggering pipeline processing if necessary
    """
    s = getInformation(image)
    
    # refresh data
    image.Update()
    
    # initiate max/min intensity value computer
    calc = itk.MinimumMaximumImageCalculator[getImageType(image)].New()
    calc.SetImage(image)
    calc.Compute()
    
    s += '\n'
    s += '\tscalar-range: (' + str(calc.GetMinimum()) + ', ' + str(calc.GetMaximum()) + ')\n'
    
    return s

def saveImageMetaIO(image, file_name): # tested
    """
    Saves the image data into a file as MetaIO format.
    
    Parameters
    ----------
    image : itk.Image
        An ITK image as used by WrapITK.
    file_name : string
        Path and file name (without suffix) where to save the image.
    
    Notes
    -----
    A write operation will trigger the image pipeline to be processed.
    """
    saveImage(image, file_name + '.mhd')
    
def saveImage(image, file_name): # tested
    """
    Saves the image data into a file in the format specified by the file name suffix.
    
    Parameters
    ----------
    image : itk.Image
        An ITK image as used by WrapITK.
    file_name : string
        Path and file name (with suffix) where to save the image.
    
    Notes
    -----
    A write operation will trigger the image pipeline to be processed.
    """
    # retrieve image type
    image_type = getImageType(image)
    
    writer = itk.ImageFileWriter[image_type].New()
    writer.SetInput(image)
    writer.SetFileName(file_name)
    writer.Write()
    
def getImageFromArray(arr, image_type = False):
    """
    Returns an itk Image created from the supplied numpy ndarray.
    If the ``image_type`` is supported, will be automatically transformed to that type,
    otherwise the most suitable is selected.
    
    Parameters
    ----------
    arr : array_like
        The image as numpy array.
    image_type : itk.Image (template)
        An itk image type.
    
    Returns
    -------
    itk_image : itk.Image (instance)
        An instance of itk.Image holding the array's data.
    
    Notes
    -----
    Always use this instead of directly the itk.PyBuffer, as that object transposes the image axes.
    """
    # The itk_py_converter transposes the image dimensions. This has to be countered.
    arr = scipy.transpose(arr)

    # determine image type if not supplied
    if not image_type:
        image_type = getImageTypeFromArray(arr)

    # convert
    itk_py_converter = itk.PyBuffer[image_type]
    return itk_py_converter.GetImageFromArray(arr)
    
def getArrayFromImage(image):
    """
    Returns a numpy ndarray created from the supplied itk image.
    
    Parameters
    ----------
    image : itk.Image (instance)
        An instance of itk.Image holding the array's data.
        
    Returns
    -------
    arr : ndarray
        The image as numpy array.
    
    Notes
    -----
    Always use this instead of directly the itk.PyBuffer, as that object transposes the image axes.
    """
    #convert
    itk_py_converter = itk.PyBuffer[getImageType(image)]
    arr = itk_py_converter.GetArrayFromImage(image)
    
    ############
    # !BUG: WarpITK is a very critical itk wrapper. Everything returned / created by it
    # seems to exist only inside the scope of the current function (at least for 
    # ImageFileReader's image and PyBuffers's scipy array. The returned objects have
    # therefore to be copied once, to survive outside the current scope.
    ############
    arr = arr.copy()
    
    # The itk_py_converter transposes the image dimensions. This has to be countered.
    return scipy.squeeze(scipy.transpose(arr))
    
def getImageType(image): # tested
    """
    Returns the image type of the supplied image as itk.Image template.
    
    Parameters
    ----------
    image : itk.Image (instance)
        An instance of itk.Image.
    
    Returns
    -------
    image_type : itk.Image (template)
        An itk image type.
    """
    try:
        return itk.Image[itk.template(image)[1][0],
                         itk.template(image)[1][1]]
    except IndexError as _:
        raise NotImplementedError, 'The python wrappers of ITK define no template class for this data type.'
    
def getImageTypeFromArray(arr): # tested
    """
    Returns the image type of the supplied array as itk.Image template.
    
    Parameters
    ----------
    arr : array_like
        The image as numpy array.
    
    Returns
    -------
    image_type : itk.Image (template)
        An itk image type.
    
    Raises
    ------
    DependencyError
        If the itk wrapper do not support the target image type
    ImageTypeError
        If the array dtype is unsupported
    """
    # mapping from scipy to the possible itk types, in order from most to least suitable
    # ! this assumes char=8bit, short=16bit and long=32bit (minimal values)
    scipy_to_itk_types = {scipy.bool_: [itk.SS, itk.UC, itk.US, itk.SS, itk.UL, itk.SL],
                          scipy.uint8: [itk.UC, itk.US, itk.SS, itk.UL, itk.SL],
                          scipy.uint16: [itk.US, itk.UL, itk.SL],
                          scipy.uint32: [itk.UL],
                          scipy.uint64: [],
                          scipy.int8: [itk.SC, itk.SS, itk.SL],
                          scipy.int16: [itk.SS, itk.SL],
                          scipy.int32: [itk.SL],
                          scipy.int64: [],
                          scipy.float32: [itk.F, itk.D],
                          scipy.float64: [itk.D],
                          scipy.float128: []}
    
    if arr.ndim <= 1:
        raise DependencyError('Itk does not support images with less than 2 dimensions.')
    
    # chek for unknown array data type
    if not arr.dtype.type in scipy_to_itk_types:
        raise ImageTypeError('The array dtype {} could not be mapped to any itk image type.'.format(arr.dtype))
    
    # check if any valid conversion exists
    if 0 == len(scipy_to_itk_types[arr.dtype.type]):
        raise ImageTypeError('No valid itk type for the pixel data dtype {}.'.format(arr.dtype))
    
    # iterate and try out candidate templates
    ex = None
    for itk_type in scipy_to_itk_types[arr.dtype.type]:
        try:                
            return itk.Image[itk_type, arr.ndim]
        except Exception as e: # pass raised exception, as a list of ordered possible itk pixel types is processed and some of them might not be compiled with the current itk wrapper module
            ex = e
            pass
    # if none fitted, examine error and eventually translate, otherwise rethrow
    if type(ex) == KeyError:
        raise DependencyError('The itk python wrappers were compiled without support the combination of {} dimensions and at least one of the following pixel data types (which are compatible with dtype {}): {}.'.format(arr.ndim, arr.dtype, scipy_to_itk_types[arr.dtype.type]))
    else:
        raise

    
def getImageTypeFromFile(image): # tested
    """
    Inconvenient but necessary implementation to load image with ITK whose component type
    and number of dimensions are unknown.
    
    Holds functionalities to determine the voxel data type and dimensions of an unknown
    image.
    
    Parameters
    ----------
    image : string
        Path to an image.
    
    Returns
    -------
    image_type : itk.Image (template) or False
        Either the correct image type (itk.Image template) associated with the image file or False if loading failed.
    
    Raises
    ------
    ImageLoadingError
        If the header of the supplied image could be recognized but is on an unsupported type
    """
    logger = Logger.getInstance()
    
    # list of component type strings (as returned by ImageIOBase.GetComponentTypeAsString() to itk component types
    string_to_component = {'char': itk.SC,
                           'unsigned_char': itk.UC,
                           'short': itk.SS,
                           'unsigned_short': itk.US,
                           'int': itk.SI,
                           'unsigned_int': itk.UI,
                           'long': itk.SL,
                           'unsigned_long': itk.UL,
                           'float': itk.F,
                           'double': itk.D}

    # List of all current itk image loaders
    image_loaders = [itk.GE4ImageIO,
                     itk.BMPImageIO,
                     itk.NiftiImageIO,
                     itk.PNGImageIO,
                     itk.BioRadImageIO,
                     itk.LSMImageIO,
                     itk.NrrdImageIO,
                     itk.SiemensVisionImageIO,
                     itk.IPLCommonImageIO,
                     itk.JPEGImageIO,
                     itk.GEAdwImageIO,
                     itk.AnalyzeImageIO,
                     itk.Brains2MaskImageIO,
                     itk.TIFFImageIO,
                     itk.VTKImageIO,
                     itk.GDCMImageIO,
                     itk.GE5ImageIO,
                     itk.GiplImageIO,
                     itk.MetaImageIO,
                     itk.StimulateImageIO,
                     itk.DICOMImageIO2]
    
    # try to find an image loader who feels responsible for the image
    # Note: All used methods are based on the common parent class ImageIOBase
    for loader_class in image_loaders:
        loader = loader_class.New()
        if loader.CanReadFile(image):
            
            # load image header
            loader.SetFileName(image)
            loader.ReadImageInformation()
            
            # request information about the image
            pixel_type = loader.GetPixelTypeAsString(loader.GetPixelType())
            component_type = loader.GetComponentTypeAsString(loader.GetComponentType())
            dimensions = loader.GetNumberOfDimensions()
            components = loader.GetNumberOfComponents()
            if not 'scalar' == pixel_type and not 1 == components:
                logger.error('Can only open scalar image with one component. Found type {} with {} components.'.format(pixel_type, components))
                raise ImageLoadingError('Can only open scalar image with one component. Found type {} with {} components.'.format(pixel_type, components))
            
            # return image type object
            logger.debug('Determined image type as {} with pixel type {} and {} dimensions.'.format(loader, component_type, dimensions))
            return itk.Image[string_to_component[component_type], dimensions]
        
    # no suitable loader found
    return False
