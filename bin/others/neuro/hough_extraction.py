#!/usr/bin/python

"""
Extracts round structures from an intensity image.

Copyright (C) 2013 Oskar Maier

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.filter.houghtransform import template_sphere, ght, template_ellipsoid
from medpy.core import Logger
from medpy.io import load, save


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2013-07-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Extracts round structures from an intensity image.
                  
                  Uses the the general hough transform with a circle template and applies
                  it to each 2D slice separately. Iteratively increases the circles radius
                  until no bigger object can be found anymore. Returns the last steps
                  results as an object probability image resp. hough image.
                  
                  Copyright (C) 2013 Oskar Maier
                  This program comes with ABSOLUTELY NO WARRANTY; This is free software,
                  and you are welcome to redistribute it under certain conditions; see
                  the LICENSE file or <http://www.gnu.org/licenses/> for details.   
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # constants
    result_percentage = 0.1
    minimal_fill = 1/2.
    initial_radius = 5
    
    # loading input image
    img, hdr = load(args.input)

    # Note:
    # DW, T2 tra, flair: 3rd to iterate over
    # T1, T2 sag: ? to iterate over

    # normalize input image
    img -= img.min() # move to contain only positive values
    img /= img.max() # normalize to values between 0 and 1
    
    if args.intermediate:
        intermediates = []
        bestcircles = []
    
    # run iteratively with increasing circle radius
    r = initial_radius
    condition = True
    while (condition):
        logger.debug('Executing for radius {}...'.format(r))
        
        # prepare sphere
        sphere = template_sphere(r, img.ndim - 1)
        #sphere = template_ellipsoid((r*2, r*2, 2))
    
        # compute threshold for stopping condition
        threshold = scipy.count_nonzero(sphere) * minimal_fill
        
        # execute slice-wise general hough transform
        hough_image = __slicewise_ght(img, sphere, args.dim)
        #hough_image = ght(img, sphere)
        
        # count number of area that excedd the threshold
        hits = scipy.count_nonzero(hough_image > threshold)
        logger.debug('...got {} hits.'.format(hits))
        
        # update trackers and increment
        condition = hits > 0
        r += 1
        
        if args.intermediate:
            intermediates.append(hough_image / float(scipy.count_nonzero(sphere))) # normalize
            bestcircles.append(hough_image > threshold)
            
    # saving the best percent of the last iteration as result segmentation
    hough_image[hough_image < hough_image.max() - result_percentage * hough_image.max()] = 0
    save(hough_image, args.output, hdr, args.force)
    
    if args.intermediate:
        logger.info('Saving intermediate images:')
        logger.info('(1) {} holds the hough transform images of each iteration step'.format(args.output + '_intermediate.nii.gz'))
        intermediate_images = scipy.zeros(list(hough_image.shape) + [len(intermediates)], hough_image.dtype)
        for i in range(intermediate_images.shape[-1]):
            intermediate_images[...,i] = intermediates[i]
        save(intermediate_images, args.output + '_intermediate.nii.gz', hdr, args.force)
        logger.info('(2) {} holds the centers of each turn best circles.'.format(args.output + '_bestcircles.nii.gz'))
        bestcircles_images = scipy.zeros(list(hough_image.shape) + [len(bestcircles)], hough_image.dtype)
        for i in range(bestcircles_images.shape[-1]):
            bestcircles_images[...,i] = bestcircles[i]
        save(bestcircles_images, args.output + '_bestcircles.nii.gz', hdr, args.force)
    
    
def __slicewise_ght(img, template, dim):
    "Executes the hough transform slice-wise over an image."
    # add a singleton dimension to the template (required, as slicing with "slice" object
    # does not remove singleton dimensions)
    template = template[[scipy.newaxis if x == dim else slice(None) for x in range(img.ndim)]]
    
    # prepare slicer
    slicer = [slice(None)] * img.ndim

    # run for first slice to get result data type
    slicer[dim] = slice(0, 1)
    hough_slice = ght(img[slicer], template)
    o = scipy.zeros(img.shape, hough_slice.dtype)
    o[slicer] = hough_slice
    
    # run for remaining dimensions
    for x in range(1, img.shape[dim]):
        slicer[dim] = slice(x, x + 1)
        o[slicer] = ght(img[slicer], template)    
    
    return o
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='the hemisphere difference image')
    parser.add_argument('dim', type=int, help='the dimension over which to iterate starting from 0')
    parser.add_argument('output', help='the lesion location as probability map')
    parser.add_argument('-i', '--intermediate', dest='intermediate', action='store_true', help='create some intermediate files to visualize the process')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', '--force', dest='force', action='store_true', help='overwrite existing files')
    return parser
    
if __name__ == "__main__":
    main()        
