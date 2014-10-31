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
# version r0.1.0
# since 2012-06-01
# status Release

# build-in modules

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
    filter provided by ITK. The pixel type of the resulting image will be float.
    
    If no pixel spacing has been supplied, values of 1 are assumed. This can lead to 
    poor results, so best extract the pixel spacing from the image header using
    `~medpy.io.header.get_pixel_spacing` and supply the return value.
    
    Parameters
    ----------
    arr : array_like
        The input image.
    pixel_spacing : tuple of floats
        The pixel spacing of ``arr``.
    
    Returns
    -------
    gradient_magnitude : ndarray
        The gradient magnitude map (of type float).
    
    Notes
    -----
    The buggy implementation of WrapITK requires the input data to be cast to
    float32. This should be kept in mind when using this method, as it can result in the
    loss of precision.
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


def watershed(arr, pixel_spacing = False, threshold = 0, level = 0):
    """
    Performs a watershedding / a watershed segmentation over an image using a filter
    provided by ITK. The pixel type of the resulting image will be unsigned long.
    
    If no pixel spacing has been supplied, values of 1 are assumed. This can lead to 
    poor results, so best extract the pixel spacing from the image header using
    `~medpy.io.header.get_pixel_spacing` and supply the return value.
    
    For more information on the threshold and level parameter, see [1]_.
    
    Parameters
    ----------
    arr : array_like
        The input image.
    pixel_spacing : tuple of floats
        The pixel spacing of ``arr``.
    threshold : float
        The threshold passed to itkWatershedImageFilter.
    level : float
        The level passed to itkWatershedImageFilter.
        
    Returns
    -------
    gradient_magnitude : ndarray
        The watershed region image (of type unsigned long).
        
    References
    ----------
    .. [1] http://www.itk.org/Doxygen/html/classitk_1_1WatershedImageFilter.html
        
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
