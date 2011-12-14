#!/usr/bin/python

"""A standard watershed image filter implemented with scipy."""

# build-in modules

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "a0.1, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = "Watershed image filter."

# code
class Watershed(object):
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