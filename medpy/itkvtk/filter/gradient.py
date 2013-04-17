"""
@package medpy.itkvtk.filter.gradient
Gradient filters.

Provides a gradient magnitude filter using itk.

Functions:
    - def gradient_magnitude(arr): Performs a gradient magnitude filter on the image data.

@author Oskar Maier
@version r0.1.0
@since 2012-06-01
@status Release
"""
# third-party modules
import itk
import scipy

# own modules
from ...core.logger import Logger
from ..utilities import itku

# code
def gradient_magnitude(arr, pixel_spacing = False):
    """
    Creates a height map of the input images using the gradient magnitude
    filter provided by ITK.
    The pixel type of the resulting image will be float.
    
    If no pixel spacing has been supplied, values of 1 are assumed. This can lead to 
    poor results, so best extract the pixel spacing from the image header using
    @link io.header.get_pixel_spacing() and supply the return value.
    
    @note: The buggy implementation of WrapITK requires the input data to be cast to
    float32. This should be kept in mind when using this method, as it can result in the
    loss of precision.
    
    @param arr the original input array
    @type arr scipy.ndarray
    @param pixel_spacing the pixel spacing
    @type sequence
    
    @return the gradient magnitutde map (of type float)
    @rtype arr scipy.ndarray
    """
    logger = Logger.getInstance()
    
    #######
    # BUG/MISSING IMPLEMENTATION: WrapITK does not wrap all templates for the
    # itk.GradientMagnitudeImageFilter. Only from same type to same type is
    # supported, what is kind of senseless, as the output should always be float for
    # exact results. Thus we have to treat the input image as a float image to apply the
    # filter. This might lead to the loss of some precision, but it should not be in any
    # relevant margin.
    #######
    if not scipy.float32 == arr.dtype:
        logger.warning('Loading array data as an itk image of type float32. This might result in some loss of precision.'.format(scipy.float_))
        
    # convert array to an itk image (note: output image type is the same as input image type)
    image_type = itk.Image[itk.F, arr.ndim]
    image_input = itku.getImageFromArray(arr.astype(scipy.float32), image_type)
    
    # set pixel spacing if supplied
    if pixel_spacing: image_input.SetSpacing([float(sp) for sp in pixel_spacing])
    
    logger.debug(itku.getInformation(image_input))
    
    # execute the gradient map filter
    image_gradient = itk.GradientMagnitudeImageFilter[image_type, image_type].New()
    image_gradient.SetInput(image_input)
    image_gradient.Update()
        
    logger.debug(itku.getInformation(image_gradient.GetOutput()))
    
    # convert to scipy array and return
    return itku.getArrayFromImage(image_gradient.GetOutput())  
