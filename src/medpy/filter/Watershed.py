#!/usr/bin/python

"""A standard watershed image filter implemented with scipy."""

# build-in modules

# third-party modules
from scipy.ndimage.filters import generic_gradient_magnitude, sobel
from scipy.ndimage.measurements import watershed_ift

# path changes

# own modules
from medpy.filter.MinimaExtraction import local_minima

# information
__author__ = "Oskar Maier"
__version__ = "e0.1, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Experimental"
__description__ = "Watershed image filter."

# code
class Watershed(object):
    
    def __init__(self, ):
        # 1 (a): cast to gradient image, but for CT/MRI to many details, requires filtering/
        #        smoothing. Therefore:
        #   (b): Use a Perona-Malik anisotropic diffusion filter (i.e. an image filter that
        #        preserves the edges in the image without blurring them, which is a very
        #        important attribute).
        #        An example would be: itk.GradientMagnitudeAnisotropicDiffusionImageFilter
        #        \w 10 times, conductance = 1.0
        #   (c): An alternative (according to Gert) would be Value-and-Criterion Filters,
        #        faster, edge-preserving, but probably not that good as watershed input
        
        # 2 extract seed points (in normal watershed the local minima)
        # local minima serve as foreground markers
        # could be extracted by iterating a mask over the image, selecting all voxels
        # whose neighbours have only higher values (!problem with valleys of equally low
        # voels!) 
        
        # 3 apply watershed
    
        # to gradient
        gradient_image = generic_gradient_magnitude(input, sobel) # alternative to sobel is preqitt
        # extracting local minima
        minima_image = local_minima(gradient_image)
        # watershed
        watershed_image = watershed_ift(gradient_image, minima_image)
    