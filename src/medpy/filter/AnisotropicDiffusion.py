#!/usr/bin/python

"""Performs Anisotropic diffusion on an image."""

# build-in modules

# third-party modules
import numpy
#import scipy.ndimage as ndimage

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "e0.1, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Experimental"
__description__ = "Anisotropic diffusion image filter."

# code
class AnisotropicDiffusion(object):
    # by: Zachary Pincus
    # Anisotropic Diffusion, as per Perona and Malik's paper (see section V).
    
    def __init__(self):
        pass
    
    @staticmethod
    def _exp(self, image_gradient, scale):
        return numpy.exp(-(numpy.absolute(image_gradient)/scale)**2)
    
    @staticmethod
    def _inv(self, image_gradient, scale):
        return 1 / (1 + (numpy.absolute(image_gradient)/scale)**2)
    
    def anisotropic_diffusion(self, image, num_iters=10, scale=10, step_size=0.2, conduction_function=AnisotropicDiffusion._inv):
        # 'step_size' is Perona and Malik's lambda parameter; scale is their 'K' parameter.
        # The 'conduction_function' is the function 'g' in the original formulation;
        # if this function simply returns a constant, the result is Gaussian blurring.
        if step_size > 0.25:
            raise ValueError('step_size parameter must be <= 0.25 for numerical stability.')
        image = image.copy()
        # simplistic boundary conditions -- no diffusion at the boundary
        central = image[1:-1, 1:-1]
        n = image[:-2, 1:-1]
        s = image[2:, 1:-1]
        e = image[1:-1, :-2]
        w = image[1:-1, 2:]
        directions = [s,e,w]
        for i in range(num_iters):
            di = n - central
            accumulator = conduction_function(di, scale)*di
            for direction in directions:
                di = direction - central
                accumulator += conduction_function(di, scale)*di
            accumulator *= step_size
            central += accumulator
        return image
