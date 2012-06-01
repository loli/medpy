"""
@package medpy.itkvtk.filter.watershed
Gradient filters.

Provides a watershed filter using itk.

Functions:
    - def watershed(arr): Performs a watershedding over an image.

@author Oskar Maier
@version r0.1.0
@since 2012-06-01
@status Release
"""
# third-party modules
import scipy
import itk

# own modules
from ...core.logger import Logger
from ..utilities import itku

# code
def watershed(arr, pixel_spacing = False, threshold = 0, level = 0):
    """
    Performs a watershedding / a watershed segmentation over an image using a filter
    provided by itk.
    The pixel type of the resulting image will be unsigned long.
    
    If no pixel spacing has been supplied, values of 1 are assumed. This can lead to 
    poor results, so best extract the pixel spacing from the image header using
    @link io.header.get_pixel_spacing() and supply the return value.
    
    For more information on the threshold and level parameter, see
    http://www.itk.org/Doxygen/html/classitk_1_1WatershedImageFilter.html .
    
    @param arr the original input array
    @type arr scipy.ndarray
    @param pixel_spacing the pixel spacing
    @type sequence
    @param threshold the threshold passed to itkWatershedImageFilter
    @type threshold float
    @param level the level passed to itkWatershedImageFilter
    @type level float
    
    @return the gradient magnitutde map (of type unsigned long)
    @rtype arr scipy.ndarray
    """
    logger = Logger.getInstance()
    
    # convert array to an itk image (note: output image type is the same as input image type)
    input_image_type = itku.getImageTypeFromArray(arr)
    image_input = itku.getImageFromArray(arr, input_image_type)
    
    # set pixel spacing if supplied
    if pixel_spacing: image_input.SetSpacing([float(sp) for sp in pixel_spacing])
    
    logger.debug(itku.getInformation(image_input))
    
    # execute the watershed
    image_watershed = itk.WatershedImageFilter[input_image_type].New()
    image_watershed.SetInput(image_input)
    image_watershed.SetThreshold(threshold)
    image_watershed.SetLevel(level)
    image_watershed.Update()
                
    logger.debug(itku.getInformation(image_watershed.GetOutput()))
    
    # convert to scipy array and cast to uint32 (we now, that it suffices, as the original image type i itk.UL)
    arr = itku.getArrayFromImage(image_watershed.GetOutput())
    return arr.astype(scipy.uint32)
