#!/usr/bin/python

"""Executes a discrete fast Fourier transformation over an image."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy.fftpack
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.utilities.nibabelu import image_like

import numpy
import math
import scipy.ndimage.interpolation as ndii



# information
__author__ = "Oskar Maier"
__version__ = "d0.1, 2012-02-02"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Executes a discrete fast Fourier transformation over an image. The
                  result will be two images, one containing the real part suffixed
                  '_real' and a second containing the imaginary part suffixed '_imag'. 
                  """

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # iterate over input images
    for image in args.images:
        
        # build output image name
        image_real_name = image.split('/')[-1][:-4] + '_real' + image.split('/')[-1][-4:]
        image_imag_name = image.split('/')[-1][:-4] + '_imag' + image.split('/')[-1][-4:]
        
        # check if output images exists
        if not args.force:
            if os.path.exists(image_real_name):
                logger.warning('The output image {} already exists. Skipping this step.'.format(image_real_name))
                continue
            elif os.path.exists(image_imag_name):
                logger.warning('The output image {} already exists. Skipping this step.'.format(image_imag_name))
                continue
        
        # load image using nibabel
        logger.info('Loading image {} using NiBabel...'.format(image))
        image_original = load(image)
        
        # get and prepare image data
        image_original_data = scipy.squeeze(image_original.get_data())
        
        # apply the discrete fast Fourier transformation
        logger.info('Executing the discrete fast Fourier transformation...')
        image_fft_data = scipy.fftpack.fftn(image_original_data)
        
        # transform to logarithmic scale
        logger.info('To logarithmic space...')
        image_real_data = image_fft_data.real
        print(image_real_data.min(), image_real_data.max())
        image_real_data = image_real_data + abs(image_real_data.min())
        constant = 65535./(math.log(1 + image_real_data.max())) # scale by 0.0001, log and then scale to fir uint16
        myfunc = lambda x: constant * math.log(1 + x * 0.0001)
        new_func = numpy.vectorize(myfunc)
        logger.info('Apply...')
        image_real_data = new_func(image_real_data)
        print(image_real_data.min(), image_real_data.max())
        image_imag_data = image_fft_data.imag
        
        # save resulting images
        logger.info('Saving resulting images real part as {} in the same format as input image, only with data-type float32...'.format(image_real_name))
        image_real = image_like(image_real_data, image_original)
        image_real.get_header().set_data_dtype(scipy.uint16)
        save(image_real, image_real_name)
        logger.info('Saving resulting images real part as {} in the same format as input image, only with data-type float32...'.format(image_imag_name))
        image_imag = image_like(image_imag_data, image_original)
        image_imag.get_header().set_data_dtype(scipy.float32)
        save(image_imag, image_imag_name)
    
    logger.info('Successfully terminated.')
    
def logpolar(image, angles=None, radii=None):
    """Return log-polar transformed image and log base."""
    shape = image.shape
    center = shape[0] / 2, shape[1] / 2
    if angles is None:
        angles = shape[0]
    if radii is None:
        radii = shape[1]
    theta = numpy.empty((angles, radii), dtype=numpy.float64)
    theta.T[:] = -numpy.linspace(0, numpy.pi, angles, endpoint=False)
    #d = radii
    d = numpy.hypot(shape[0]-center[0], shape[1]-center[1])
    log_base = 10.0 ** (math.log10(d) / (radii))
    radius = numpy.empty_like(theta)
    radius[:] = numpy.power(log_base, numpy.arange(radii,
                                                   dtype=numpy.float64)) - 1.0
    x = radius * numpy.sin(theta) + center[0]
    y = radius * numpy.cos(theta) + center[1]
    output = numpy.empty_like(x)
    ndii.map_coordinates(image, [x, y], output=output)
    return output, log_base
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('images', nargs='+', help='One or more input images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
